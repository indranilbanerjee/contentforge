"""pipeline-tracker.py tests — per-run storage, 0.5 phase, exit codes."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPT = TESTS_DIR.parent / "scripts" / "pipeline-tracker.py"


def run_pt(env, *args):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, env=env)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except json.JSONDecodeError:
        payload = {"_unparseable_stdout": out}
    return proc.returncode, payload


class TestPipelineTracker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.home = Path(cls._tmp.name)
        cls.env = os.environ.copy()
        cls.env["CLAUDE_MARKETING_HOME"] = str(cls.home)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_two_run_ids_do_not_clobber(self):
        rc, a = run_pt(self.env, "--action", "init", "--brand", "acme",
                       "--run-id", "run-A", "--content-type", "article", "--topic", "Topic A")
        self.assertEqual(rc, 0, a)
        rc, b = run_pt(self.env, "--action", "init", "--brand", "acme",
                       "--run-id", "run-B", "--content-type", "blog", "--topic", "Topic B")
        self.assertEqual(rc, 0, b)

        self.assertTrue((self.home / "acme" / "runs" / "run-A" / "pipeline-run.json").exists())
        self.assertTrue((self.home / "acme" / "runs" / "run-B" / "pipeline-run.json").exists())

        run_pt(self.env, "--action", "phase-start", "--brand", "acme", "--run-id", "run-A", "--phase", "1")
        run_pt(self.env, "--action", "phase-end", "--brand", "acme", "--run-id", "run-A",
               "--phase", "1", "--content-words", "900")
        run_pt(self.env, "--action", "phase-start", "--brand", "acme", "--run-id", "run-B", "--phase", "2")
        run_pt(self.env, "--action", "phase-end", "--brand", "acme", "--run-id", "run-B", "--phase", "2")

        rc, rep_a = run_pt(self.env, "--action", "get-report", "--brand", "acme", "--run-id", "run-A")
        rc, rep_b = run_pt(self.env, "--action", "get-report", "--brand", "acme", "--run-id", "run-B")
        self.assertEqual([p["phase"] for p in rep_a["phases"]], ["1"])
        self.assertEqual([p["phase"] for p in rep_b["phases"]], ["2"])
        self.assertEqual(rep_a["topic"], "Topic A")
        self.assertEqual(rep_b["topic"], "Topic B")

    def test_phase_0_5_is_named_title_curation(self):
        run_pt(self.env, "--action", "init", "--brand", "acme",
               "--run-id", "run-C", "--content-type", "article", "--topic", "Topic C")
        rc, started = run_pt(self.env, "--action", "phase-start", "--brand", "acme",
                             "--run-id", "run-C", "--phase", "0.5")
        self.assertEqual(rc, 0, started)
        self.assertEqual(started["name"], "Title Curation")
        rc, ended = run_pt(self.env, "--action", "phase-end", "--brand", "acme",
                           "--run-id", "run-C", "--phase", "0.5")
        self.assertEqual(rc, 0, ended)
        self.assertGreaterEqual(ended["duration_seconds"], 0)
        rc, rep = run_pt(self.env, "--action", "get-report", "--brand", "acme", "--run-id", "run-C")
        self.assertEqual(rep["phases"][0]["phase"], "0.5")
        self.assertIsNotNone(rep["phases"][0]["benchmark_seconds"])

    def test_legacy_path_without_run_id(self):
        rc, p = run_pt(self.env, "--action", "init", "--brand", "legacybrand",
                       "--content-type", "faq", "--topic", "Legacy")
        self.assertEqual(rc, 0, p)
        self.assertTrue((self.home / "legacybrand" / "pipeline-run.json").exists())

    def test_phase_end_without_start_exits_1(self):
        run_pt(self.env, "--action", "init", "--brand", "acme",
               "--run-id", "run-D", "--content-type", "article", "--topic", "D")
        rc, p = run_pt(self.env, "--action", "phase-end", "--brand", "acme",
                       "--run-id", "run-D", "--phase", "4")
        self.assertEqual(rc, 1)
        self.assertIn("error", p)

    def test_missing_run_exits_1(self):
        rc, p = run_pt(self.env, "--action", "get-report", "--brand", "acme", "--run-id", "ghost")
        self.assertEqual(rc, 1)
        self.assertIn("error", p)


if __name__ == "__main__":
    unittest.main()
