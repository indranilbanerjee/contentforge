"""End-to-end checkpoint-manager.py lifecycle tests (subprocess, tmp HOME).

Covers: init (meta fields incl. --meta JSON, non-ASCII topic under a cp1252
console), save (artifact contract filenames, manifest slots), loop counters,
pending_rework set/clear + resume targeting, load, finalize, exit codes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPT = TESTS_DIR.parent / "scripts" / "checkpoint-manager.py"


def run_cp(env, *args):
    """Run checkpoint-manager.py; return (returncode, parsed_json)."""
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, env=env,
    )
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except json.JSONDecodeError:
        payload = {"_unparseable_stdout": out, "_stderr": proc.stderr.decode("utf-8", errors="replace")}
    return proc.returncode, payload


class TestCheckpointRoundtrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.home = Path(cls._tmp.name)
        cls.env = os.environ.copy()
        cls.env["CLAUDE_MARKETING_HOME"] = str(cls.home)
        # Simulate a Windows cp1252 console — the utf8 guard must override it.
        cls.env["PYTHONIOENCODING"] = "cp1252"

        rc, payload = run_cp(
            cls.env, "init",
            "--brand", "Acme Corp",
            "--topic", "AI in Pharma — テスト",   # non-ASCII on purpose
            "--content-type", "article",
            "--keyword", "ai in pharma",
            "--word-count", "2500",
            "--meta", json.dumps({"audience": "pharma execs", "tone": "authoritative"}),
        )
        cls.init_rc = rc
        cls.init_payload = payload
        cls.run_id = payload.get("run_id", "")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_01_init_survives_cp1252_console_with_non_ascii_topic(self):
        self.assertEqual(self.init_rc, 0, self.init_payload)
        self.assertTrue(self.run_id)

    def test_02_init_meta_merges_flags_and_meta_json(self):
        meta = self.init_payload["manifest"]["meta"]
        self.assertEqual(meta["keyword"], "ai in pharma")
        self.assertEqual(meta["word_count"], 2500)
        self.assertEqual(meta["audience"], "pharma execs")
        self.assertEqual(meta["tone"], "authoritative")

    def test_03_run_dir_uses_brand_slug(self):
        run_dir = self.home / "acme-corp" / "runs" / self.run_id
        self.assertTrue(run_dir.is_dir(), f"expected {run_dir}")
        self.assertTrue((run_dir / "run.json").exists())

    def test_10_save_title_artifact_contract(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "0.5", "--content", "My Confirmed Title", "--extension", "txt")
        self.assertEqual(rc, 0, p)
        self.assertTrue(p["artifact"].endswith("phase-0.5-title.txt"), p["artifact"])
        self.assertIn("0.5", p["completed_phases"])

    def test_11_save_draft_via_content_file(self):
        draft = self.home / "draft.md"
        draft.write_text("# Draft\n\nBody — with em dash.", encoding="utf-8")
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "3", "--content-file", str(draft), "--extension", "md")
        self.assertEqual(rc, 0, p)
        self.assertTrue(p["artifact"].endswith("phase-3-draft.md"))

    def test_12_json_on_phase_3_5_targets_manifest_slot(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "3.5", "--content", '{"assets": []}', "--extension", "json")
        self.assertEqual(rc, 0, p)
        self.assertTrue(p["artifact"].endswith("phase-3.5-visual-manifest.json"))
        self.assertEqual(p["artifact_key"], "3.5-manifest")
        self.assertNotIn("3.5", p["completed_phases"],
                         "manifest save must not mark the phase complete")

    def test_13_md_on_phase_3_5_is_primary(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "3.5", "--content", "visual draft", "--extension", "md")
        self.assertEqual(rc, 0, p)
        self.assertTrue(p["artifact"].endswith("phase-3.5-visuals.md"))
        self.assertIn("3.5", p["completed_phases"])

    def test_20_loop_counters(self):
        rc, p1 = run_cp(self.env, "loop", "--brand", "Acme Corp", "--run-id", self.run_id,
                        "--edge", "phase_7_to_5")
        self.assertEqual(rc, 0, p1)
        rc, p2 = run_cp(self.env, "loop", "--brand", "Acme Corp", "--run-id", self.run_id,
                        "--edge", "phase_7_to_5")
        self.assertEqual(p2["edge_count"], 2)
        self.assertEqual(p2["total_loops"], 2)
        rc, p3 = run_cp(self.env, "loop", "--brand", "Acme Corp", "--run-id", self.run_id,
                        "--edge", "phase_4_to_3")
        self.assertEqual(p3["total_loops"], 3)
        self.assertEqual(p3["loop_counts"]["phase_7_to_5"], 2)

    def test_30_pending_rework_sets_next_phase(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "7", "--content", '{"score": 6.4}', "--extension", "json",
                       "--pending-rework", json.dumps({"target_phase": "5", "feedback": "tighten section 2"}))
        self.assertEqual(rc, 0, p)
        self.assertEqual(p["pending_rework"]["target_phase"], "5")

        rc, s = run_cp(self.env, "status", "--brand", "Acme Corp", "--run-id", self.run_id)
        self.assertEqual(s["next_phase"], "5")
        self.assertEqual(s["pending_rework"]["feedback"], "tighten section 2")

        rc, r = run_cp(self.env, "resume", "--brand", "Acme Corp")
        self.assertEqual(r["resume_run"]["next_phase"], "5")
        self.assertEqual(r["resume_run"]["meta"]["keyword"], "ai in pharma")
        self.assertEqual(r["resume_run"]["loop_counts"]["phase_7_to_5"], 2)

    def test_31_saving_target_phase_clears_pending_rework(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "5", "--content", "reworked structure", "--extension", "md")
        self.assertEqual(rc, 0, p)
        self.assertIsNone(p["pending_rework"])
        rc, s = run_cp(self.env, "status", "--brand", "Acme Corp", "--run-id", self.run_id)
        self.assertIsNone(s["pending_rework"])
        self.assertNotEqual(s["next_phase"], "5")

    def test_40_load_returns_content(self):
        rc, p = run_cp(self.env, "load", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "3")
        self.assertEqual(rc, 0, p)
        self.assertIn("Body — with em dash.", p["content"])

    def test_50_finalize_and_list(self):
        rc, p = run_cp(self.env, "finalize", "--brand", "Acme Corp", "--run-id", self.run_id)
        self.assertEqual(rc, 0, p)
        rc, listed = run_cp(self.env, "list", "--brand", "Acme Corp")
        self.assertEqual(listed["runs"][0]["status"], "completed")

    def test_60_missing_run_exits_1(self):
        rc, p = run_cp(self.env, "status", "--brand", "Acme Corp", "--run-id", "nope-000")
        self.assertEqual(rc, 1)
        self.assertIn("error", p)

    def test_61_bad_pending_rework_json_exits_1(self):
        rc, p = run_cp(self.env, "save", "--brand", "Acme Corp", "--run-id", self.run_id,
                       "--phase", "6", "--content", "x", "--pending-rework", "{not json")
        self.assertEqual(rc, 1)
        self.assertIn("error", p)


if __name__ == "__main__":
    unittest.main()
