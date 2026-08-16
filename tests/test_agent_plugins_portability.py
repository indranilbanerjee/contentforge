"""Agent Plugins 1.0 portability: the standard the plugin must now travel in.

OpenAI's Agent Plugins 1.0 (announced 2026-08-06, adopted by ChatGPT, Codex,
Cursor, GitHub Copilot, VS Code, Kiro) packages skills in a root-manifest
directory and defines `${PLUGIN_ROOT}` / `${PLUGIN_DATA}` — not the `CLAUDE_*`
names every command line here historically used. Before these tests, a
compliant non-Claude host resolved no data directory at all, and the pipeline's
execution model was undefined anywhere without subagent dispatch.

Also pins the Phase 3.5 embedding-contract reconciliation: Phase 3.5 said three
times that "Phase 8 embeds only approved images", Phase 8 says approval gates AI
imagery only — and a real run resolved the contradiction by embedding nothing.

Stdlib only.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestRootManifest(unittest.TestCase):
    """The Agent Plugins 1.0 root plugin.json — closed schema, version-synced."""

    def setUp(self):
        self.manifest = json.loads((REPO / "plugin.json").read_text(encoding="utf-8"))

    def test_exists_with_schema_and_name(self):
        self.assertEqual(self.manifest["$schema"],
                         "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(self.manifest["name"], "contentforge")

    def test_version_matches_claude_manifest(self):
        """Two manifests, one version. The release ritual bumps both or the
        directories serve different plugins under the same name."""
        claude = json.loads((REPO / ".claude-plugin" / "plugin.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(self.manifest["version"], claude["version"])

    def test_closed_schema_respected(self):
        """The spec forbids hooks/agents/commands/mcpServers at the top level —
        clients reject unknown fields, so extras break installs everywhere."""
        allowed = {"$schema", "name", "version", "description", "author", "extensions"}
        self.assertLessEqual(set(self.manifest.keys()), allowed,
                             f"unexpected top-level fields: "
                             f"{set(self.manifest.keys()) - allowed}")

    def test_name_rules(self):
        import re
        self.assertRegex(self.manifest["name"], r"^[a-z0-9][a-z0-9.-]{0,62}[a-z0-9]$")
        self.assertNotRegex(self.manifest["name"], r"[.-]{2}")

    def test_skills_are_first_level_skill_md_dirs(self):
        """AP1.0 skills/: first-level subdirectories each holding SKILL.md."""
        for d in (REPO / "skills").iterdir():
            if d.is_dir():
                self.assertTrue((d / "SKILL.md").is_file(),
                                f"skills/{d.name}/ has no SKILL.md")


class TestPluginDataFallback(unittest.TestCase):
    """A host that sets only the standard PLUGIN_DATA must still resolve."""

    def setUp(self):
        self._saved = {k: os.environ.pop(k, None)
                       for k in ("CLAUDE_MARKETING_HOME", "CLAUDE_PLUGIN_DATA",
                                 "PLUGIN_DATA")}
        self.common = _load("cf_common_portability", "_common.py")

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_plugin_data_alone_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["PLUGIN_DATA"] = tmp
            self.assertEqual(self.common.marketing_home(), Path(tmp))

    def test_claude_name_wins_when_both_set(self):
        """Precedence must not flip for existing Claude installs."""
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            os.environ["CLAUDE_PLUGIN_DATA"] = a
            os.environ["PLUGIN_DATA"] = b
            self.assertEqual(self.common.marketing_home(), Path(a))

    def test_no_env_falls_back_to_home(self):
        self.assertEqual(self.common.marketing_home(),
                         Path.home() / ".claude-marketing")


class TestPortableExecutionLane(unittest.TestCase):
    """Without this section, the pipeline's execution model is undefined on
    every platform lacking subagent dispatch — including the two the plugins
    are most used on outside Claude Code."""

    def setUp(self):
        self.skill = (REPO / "skills" / "contentforge" / "SKILL.md")\
            .read_text(encoding="utf-8")

    def test_lane_exists(self):
        self.assertIn("Portable execution lane", self.skill)

    def test_lane_keeps_the_gates(self):
        idx = self.skill.index("Portable execution lane")
        lane = self.skill[idx:idx + 3000]
        self.assertIn("Same artifacts, same names, same gates", lane)
        self.assertIn("agents/{NN}-{name}.md", lane)

    def test_lane_names_the_standard_env_vars(self):
        idx = self.skill.index("Portable execution lane")
        lane = self.skill[idx:idx + 3000]
        self.assertIn("${PLUGIN_ROOT}", lane)
        self.assertIn("${PLUGIN_DATA}", lane)


class TestEmbeddingContractReconciled(unittest.TestCase):
    """Phase 3.5 and Phase 8 must state the same embedding rule."""

    def test_no_unqualified_embeds_only_approved(self):
        text = (REPO / "agents" / "03.5-visual-asset-annotator.md")\
            .read_text(encoding="utf-8")
        self.assertNotIn("Phase 8 embeds only approved images", text,
                         "the unqualified wording that made a run embed zero "
                         "of its four valid deterministic figures is back")

    def test_deterministic_assets_exempt_stated_in_3_5(self):
        text = (REPO / "agents" / "03.5-visual-asset-annotator.md")\
            .read_text(encoding="utf-8")
        self.assertIn("NOT gated on this flag", text)

    def test_labeled_diagrams_routed_off_the_ai_path(self):
        text = (REPO / "agents" / "03.5-visual-asset-annotator.md")\
            .read_text(encoding="utf-8")
        self.assertIn("must NOT go to the AI path", text)

    def test_feature_image_placement_value_defined(self):
        text = (REPO / "agents" / "03.5-visual-asset-annotator.md")\
            .read_text(encoding="utf-8")
        self.assertIn("`feature-image`", text)

    def test_reviewer_has_re_review_mode(self):
        text = (REPO / "agents" / "07-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("RE-REVIEW MODE", text)
        self.assertIn("No loop budget is consumed", text)

    def test_comparative_scoring_needs_history(self):
        text = (REPO / "agents" / "07-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("at least 5 prior pieces", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
