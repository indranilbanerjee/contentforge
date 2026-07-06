"""Cross-script path contract: checkpoint-manager.py and drive-sync-state.py
MUST agree on the _sync-pending.json location for the same brand string.

Regression guard: before v3.16 checkpoint-manager keyed the run dir on the RAW
brand name while drive-sync-state slugified it, so for any brand like
"Acme Corp" the Cowork Drive-sync roundtrip (save -> list-pending ->
mark-uploaded) silently broke.
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
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
CHECKPOINT = SCRIPTS_DIR / "checkpoint-manager.py"
SYNC_STATE = SCRIPTS_DIR / "drive-sync-state.py"

BRAND = "Acme Corp"  # deliberately NOT a slug


def run(env, script, *args):
    proc = subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, env=env)
    out = proc.stdout.decode("utf-8", "replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except json.JSONDecodeError:
        payload = {"_unparseable_stdout": out,
                   "_stderr": proc.stderr.decode("utf-8", "replace")}
    return proc.returncode, payload


class TestPendingSyncPathContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.home = Path(cls._tmp.name)
        cls.env = os.environ.copy()
        cls.env["CLAUDE_MARKETING_HOME"] = str(cls.home)
        # Cowork mode ON so checkpoint saves mark files pending.
        (cls.home).mkdir(parents=True, exist_ok=True)
        (cls.home / "_cowork-config.json").write_text(json.dumps({
            "environment": "cowork-sandbox",
            "drive_root_folder_name": "CF-Root",
        }), encoding="utf-8")

        rc, init = run(cls.env, CHECKPOINT, "init", "--brand", BRAND,
                       "--topic", "Sync Contract", "--content-type", "article")
        assert rc == 0, init
        cls.run_id = init["run_id"]

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_1_save_marks_pending_in_cowork_mode(self):
        rc, saved = run(self.env, CHECKPOINT, "save", "--brand", BRAND,
                        "--run-id", self.run_id, "--phase", "1",
                        "--content", "research notes", "--extension", "md")
        self.assertEqual(rc, 0, saved)
        hint = saved["drive_sync_hint"]
        self.assertTrue(hint["cowork_drive_configured"], hint)
        self.assertIn("phase-1-research.md", hint["files_marked_pending"])

    def test_2_drive_sync_state_sees_the_same_pending_file(self):
        rc, listing = run(self.env, SYNC_STATE, "--action", "list-pending-uploads",
                          "--brand", BRAND, "--run-id", self.run_id)
        self.assertEqual(rc, 0, listing)
        self.assertIn("phase-1-research.md", listing["pending"],
                      "drive-sync-state must read the SAME _sync-pending.json "
                      "checkpoint-manager wrote (brand-path contract)")

    def test_3_mark_uploaded_roundtrip(self):
        rc, marked = run(self.env, SYNC_STATE, "--action", "mark-uploaded",
                         "--brand", BRAND, "--run-id", self.run_id,
                         "--file", "phase-1-research.md", "--drive-file-id", "drv123")
        self.assertEqual(rc, 0, marked)
        rc, listing = run(self.env, SYNC_STATE, "--action", "list-pending-uploads",
                          "--brand", BRAND, "--run-id", self.run_id)
        self.assertNotIn("phase-1-research.md", listing["pending"])
        self.assertEqual(listing["uploaded"][0]["file"], "phase-1-research.md")

    def test_4_single_run_directory_exists_under_slug(self):
        slug_runs = self.home / "acme-corp" / "runs" / self.run_id
        raw_runs = self.home / BRAND / "runs" / self.run_id
        self.assertTrue(slug_runs.exists())
        self.assertFalse(raw_runs.exists(),
                         "raw-brand duplicate directory must not be created")

    def test_5_list_runs_needing_sync_uses_same_paths(self):
        rc, needing = run(self.env, SYNC_STATE, "--action", "list-runs-needing-sync",
                          "--brand", BRAND)
        self.assertEqual(rc, 0, needing)
        run_ids = [r["run_id"] for r in needing["runs"]]
        self.assertIn(self.run_id, run_ids)  # run.json still pending upload


if __name__ == "__main__":
    unittest.main()
