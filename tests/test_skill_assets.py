"""Guards for the claude.ai .skill release assets (v4.1.0).

The packaging contract: config/skill-assets.json names every skill shipped as
a standalone claude.ai upload plus the repo files its prose references.
scripts/build-skill-assets.py refuses to package a skill whose SKILL.md
references ${CLAUDE_PLUGIN_ROOT} or an undeclared repo path — these tests
prove the manifest is live, the scan actually rejects (plant-checked), and
the built zip has the shape claude.ai accepts (one top-level dir, exactly
one SKILL.md, under the file cap, deterministic bytes).
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO / "config" / "skill-assets.json"


def _load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_skill_assets", REPO / "scripts" / "build-skill-assets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestManifestIntegrity(unittest.TestCase):
    """config/skill-assets.json must describe real, shippable skills."""

    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_parses_with_cap_and_skills(self):
        self.assertIsInstance(self.manifest["claude_ai_upload_cap_files"], int)
        self.assertGreater(len(self.manifest["skills"]), 0)

    def test_every_listed_skill_exists_with_skill_md(self):
        for name in self.manifest["skills"]:
            self.assertTrue((REPO / "skills" / name / "SKILL.md").exists(),
                            f"manifest lists '{name}' but skills/{name}/SKILL.md is missing")

    def test_every_declared_extra_file_exists(self):
        for name, spec in self.manifest["skills"].items():
            for extra in spec.get("extra_files", []):
                self.assertTrue((REPO / extra).exists(),
                                f"{name} declares extra file '{extra}' which does not exist")

    def test_pipeline_skill_is_not_listed(self):
        # The 10-phase pipeline needs subagent dispatch — it can never ship as
        # a standalone claude.ai upload. Guard against optimistic additions.
        self.assertNotIn("contentforge", self.manifest["skills"],
                         "the pipeline skill cannot be a standalone .skill asset")


class TestPortabilityScan(unittest.TestCase):
    """The scan must pass every manifest skill and reject planted violations."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_builder()
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_all_manifest_skills_scan_clean(self):
        problems = []
        for name, spec in self.manifest["skills"].items():
            problems.extend(self.mod.scan_portability(name, spec.get("extra_files", [])))
        self.assertEqual(problems, [], "manifest skills must be portable")

    def test_scan_rejects_plugin_root_reference(self):
        # Plant: a skill whose SKILL.md needs the plugin root must be refused.
        tmp = Path(tempfile.mkdtemp())
        try:
            planted = tmp / "skills" / "planted"
            planted.mkdir(parents=True)
            (planted / "SKILL.md").write_text(
                "Run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py` first.\n",
                encoding="utf-8")
            old_repo = self.mod.REPO
            self.mod.REPO = tmp
            try:
                problems = self.mod.scan_portability("planted", [])
            finally:
                self.mod.REPO = old_repo
            self.assertTrue(any("CLAUDE_PLUGIN_ROOT" in p for p in problems),
                            f"plant not caught: {problems}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_scan_rejects_undeclared_repo_reference(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            planted = tmp / "skills" / "planted"
            planted.mkdir(parents=True)
            (planted / "SKILL.md").write_text(
                "Read config/does-not-exist.json for the numeric specs.\n",
                encoding="utf-8")
            old_repo = self.mod.REPO
            self.mod.REPO = tmp
            try:
                problems = self.mod.scan_portability("planted", [])
            finally:
                self.mod.REPO = old_repo
            self.assertTrue(any("does-not-exist.json" in p for p in problems),
                            f"plant not caught: {problems}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_scan_reports_missing_declared_extra(self):
        name = next(iter(self.manifest["skills"]))
        problems = self.mod.scan_portability(name, ["config/ghost-file.json"])
        self.assertTrue(any("ghost-file.json" in p for p in problems),
                        "a declared-but-missing extra file must be a violation")


class TestBuiltAssetShape(unittest.TestCase):
    """A built .skill must match what claude.ai's uploader accepts."""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_builder()
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.tmp = Path(tempfile.mkdtemp())
        cls.mod.DIST = cls.tmp
        cls.skill = "cf-brief"
        spec = cls.manifest["skills"][cls.skill]
        cap = cls.manifest["claude_ai_upload_cap_files"]
        cls.out = cls.mod.build_skill(cls.skill, spec["extra_files"], cap)
        cls.names = zipfile.ZipFile(cls.out).namelist()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_single_top_level_directory(self):
        tops = {n.split("/", 1)[0] for n in self.names}
        self.assertEqual(tops, {self.skill})

    def test_exactly_one_skill_md(self):
        md = [n for n in self.names if n.endswith("/SKILL.md")]
        self.assertEqual(md, [f"{self.skill}/SKILL.md"])

    def test_extra_files_land_at_repo_relative_paths(self):
        for extra in self.manifest["skills"][self.skill]["extra_files"]:
            self.assertIn(f"{self.skill}/{extra}", self.names,
                          f"extra file '{extra}' missing from bundle")

    def test_under_the_upload_cap(self):
        self.assertLessEqual(len(self.names),
                             self.manifest["claude_ai_upload_cap_files"])

    def test_rebuild_is_byte_identical(self):
        first = self.out.read_bytes()
        spec = self.manifest["skills"][self.skill]
        again = self.mod.build_skill(
            self.skill, spec["extra_files"],
            self.manifest["claude_ai_upload_cap_files"])
        self.assertEqual(first, again.read_bytes(),
                         "builds must be deterministic for release provenance")


if __name__ == "__main__":
    unittest.main()
