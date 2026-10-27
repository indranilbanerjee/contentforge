"""checkpoint-manager refuses what must never be recorded: a path as an extension, and a loop past its cap.

Found in 4.5.12 by two independent audits of the installed script:
  * `save --extension ../../../../../../ext-escape.md` exited 0 and wrote the artifact six levels up, in the user's home folder,
    and run.json then listed the escaped path as the phase artifact. The prose already promised md, json or txt.
  * `loop` recorded the 3rd traversal of an edge and the 8th loop of a run without a word; only run-audit, at the very end,
    called it a violation. The cap is now enforced where the loop is recorded, with the same rule run-audit applies
    (the smaller cap governs), so a refused loop is exactly one the audit would have failed.
Everything runs in a temp HOME and workspace.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
SCRIPT = SCRIPTS / "checkpoint-manager.py"
CONFIG = SCRIPTS.parent / "config"


def run_cp(env, *args):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, env=env, timeout=120)
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except json.JSONDecodeError:
        payload = {"_unparseable": out, "_stderr": proc.stderr.decode("utf-8", errors="replace")}
    return proc.returncode, payload, proc.stderr.decode("utf-8", errors="replace")


def audit_module():
    spec = importlib.util.spec_from_file_location("_cf_run_audit_for_test", SCRIPTS / "run-audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)
        self.env = {**os.environ, "CLAUDE_MARKETING_HOME": str(self.home / "ws"), "HOME": str(self.home),
                    "USERPROFILE": str(self.home), "PYTHONUTF8": "1"}
        for name in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "CLAUDE_PLUGIN_DATA_DIR"):
            self.env.pop(name, None)
        rc, payload, _ = run_cp(self.env, "init", "--brand", "Acme", "--topic", "Guards", "--content-type", "article")
        self.assertEqual(rc, 0, payload)
        self.run_id = payload["run_id"]

    def cp(self, *args):
        return run_cp(self.env, *args, "--brand", "Acme", "--run-id", self.run_id) if args[0] != "init" else run_cp(self.env, *args)

    def files_named(self, name):
        return [p for p in self.home.rglob(name) if p.is_file()]


class TestExtensionIsNotAPath(RunCase):

    def test_a_traversal_extension_is_refused_at_the_command_line_and_writes_nothing(self):
        rc, payload, err = self.cp("save", "--phase", "4", "--content", "ESCAPED", "--extension", "../../../../../../ext-escape.md")
        self.assertEqual(rc, 2, (payload, err))
        self.assertIn("invalid choice", err)
        self.assertEqual(self.files_named("ext-escape.md"), [])
        self.assertEqual(self.files_named("*ext-escape*"), [])

    def test_a_shallower_traversal_does_not_leave_a_file_in_the_run_folder_either(self):
        rc, payload, err = self.cp("save", "--phase", "4", "--content", "X", "--extension", "../../x")
        self.assertEqual(rc, 2, (payload, err))
        self.assertEqual([p for p in self.home.rglob("x") if p.is_file()], [])

    def test_the_python_function_refuses_too_and_run_json_is_untouched(self):
        sys.path.insert(0, str(SCRIPTS))
        os.environ["CLAUDE_MARKETING_HOME"] = str(self.home / "ws")
        try:
            spec = importlib.util.spec_from_file_location("_cf_checkpoint_for_test", SCRIPT)
            cm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cm)
            before = (cm._run_dir("Acme", self.run_id) / "run.json").read_bytes()
            got = cm.save_phase("Acme", self.run_id, "4", "ESCAPED", "../../../escape.md")
            self.assertIn("error", got, got)
            self.assertEqual((cm._run_dir("Acme", self.run_id) / "run.json").read_bytes(), before)
            self.assertEqual(self.files_named("escape.md"), [])
        finally:
            os.environ.pop("CLAUDE_MARKETING_HOME", None)

    def test_md_json_and_txt_still_save(self):
        for phase, ext in (("1", "md"), ("1", "txt"), ("3.5", "json"), ("4", "json")):
            with self.subTest(phase=phase, extension=ext):
                rc, payload, err = self.cp("save", "--phase", phase, "--content", "{}" if ext == "json" else "text", "--extension", ext)
                self.assertEqual(rc, 0, (payload, err))
                self.assertTrue(Path(payload["artifact"]).name.endswith("." + ext) or payload["artifact"].endswith(".json"))


class TestLoopsStopAtTheCap(RunCase):

    def caps(self):
        audit = audit_module()
        graph = audit._json(audit.CONFIG_DIR / "pipeline-graph.json")
        scoring = audit._json(audit.CONFIG_DIR / "scoring-thresholds.json")
        return audit, audit.loop_caps(graph, scoring)

    def test_the_cap_the_tests_rely_on_is_what_config_says(self):
        _, caps = self.caps()
        self.assertEqual(caps["per_edge"], 2)
        self.assertEqual(caps["total"], 5)

    def test_the_third_loop_on_one_edge_is_refused_not_recorded_and_says_what_to_do(self):
        for n in (1, 2):
            rc, payload, _ = self.cp("loop", "--edge", "phase_7_to_5", "--reason", f"round {n}")
            self.assertEqual(rc, 0, payload)
        rc, payload, _ = self.cp("loop", "--edge", "phase_7_to_5", "--reason", "round 3")
        self.assertEqual(rc, 1, payload)
        self.assertIn("loop cap reached", payload["error"])
        self.assertIn("phase_7_to_5", payload["error"])
        self.assertIn("NOT recorded", payload["error"])
        self.assertIn("human reviewer", payload["recovery"])
        self.assertIn("--status blocked", payload["recovery"])
        rc, status, _ = self.cp("status")
        self.assertEqual(status["loop_counts"], {"phase_7_to_5": 2})
        self.assertEqual(status["total_loops"], 2)

    def test_the_sixth_loop_of_a_run_is_refused_even_across_edges(self):
        # five loops over edges that each stay inside their own caps reach the per-run cap of 5
        for edge in ("phase_4_to_3", "phase_4_to_3", "phase_6_to_5", "phase_7_to_5", "phase_7_to_3"):
            rc, payload, _ = self.cp("loop", "--edge", edge, "--reason", "r")
            self.assertEqual(rc, 0, (edge, payload))
        rc, payload, _ = self.cp("loop", "--edge", "phase_5_to_3", "--reason", "one too many")
        self.assertEqual(rc, 1, payload)
        self.assertIn("per-run cap 5", payload["error"])
        rc, after, _ = self.cp("status")
        self.assertEqual(after["total_loops"], 5)

    def test_an_edge_inside_its_caps_is_still_recorded(self):
        rc, payload, _ = self.cp("loop", "--edge", "phase_4_to_3", "--reason", "gate fail")
        self.assertEqual(rc, 0, payload)
        self.assertEqual(payload["edge_count"], 1)

    def test_a_first_loop_on_a_fresh_run_breaks_no_cap(self):
        sys.path.insert(0, str(SCRIPTS))
        spec = importlib.util.spec_from_file_location("_cf_checkpoint_for_test2", SCRIPT)
        cm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cm)
        self.assertEqual(cm._loop_cap_violations({}, "phase_7_to_5"), [])
        self.assertTrue(cm._loop_cap_violations({"phase_7_to_5": 2}, "phase_7_to_5"))


if __name__ == "__main__":
    unittest.main()
