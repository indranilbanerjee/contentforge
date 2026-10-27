"""`finalize --status completed` re-derives the audit; a record written by hand does not stand in for it.

Found in 4.5.12: finalize read run-audit.json's `verdict` and `fingerprint` and never re-derived either. A body with real
production scaffolding audits as VIOLATIONS, but a file written by hand with `{"verdict": "CLEAN", "fingerprint": <the fresh
fingerprint>}` finalized the same run as completed (and a re-audit of the completed run then reported VIOLATIONS). The README says
"the pipeline says it finished" and "the artifacts prove it finished" can never drift apart silently; that is only true when
finalize does its own audit. The record proves the audit step ran on these bytes; it is not the evidence.
Runs in a temp HOME and workspace.
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
CHECKPOINT = SCRIPTS / "checkpoint-manager.py"
AUDIT = SCRIPTS / "run-audit.py"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402

SCAFFOLDED = "A short article about invoices.\n\n[VISUAL-PLACEHOLDER: chart of monthly invoices]\n\nThe end.\n"
CLEAN = "A short article about invoices.\n\nThey are paid on time.\n\nThe end.\n"


def run(script, *args, env):
    proc = subprocess.run([sys.executable, str(script), *args], capture_output=True, env=env, timeout=240)
    out = proc.stdout.decode("utf-8", "replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except ValueError:
        payload = {"_unparseable": out}
    return proc.returncode, payload


class TestFinalizeRederives(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.env = {**os.environ, "HOME": str(root), "USERPROFILE": str(root), "CLAUDE_MARKETING_HOME": str(root / "ws"),
                    "PYTHONUTF8": "1"}
        for name in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA"):
            self.env.pop(name, None)
        rc, payload = run(CHECKPOINT, "init", "--brand", "Acme", "--topic", "Invoices", "--content-type", "article", env=self.env)
        self.assertEqual(rc, 0, payload)
        self.run_id = payload["run_id"]
        self.run_dir = next((root / "ws").rglob(self.run_id))

    def save_body(self, text):
        rc, payload = run(CHECKPOINT, "save", "--brand", "Acme", "--run-id", self.run_id, "--phase", "6.5", "--content", text,
                          "--extension", "md", env=self.env)
        self.assertEqual(rc, 0, payload)

    def audit(self):
        return run(AUDIT, "--brand", "Acme", "--run-id", self.run_id, env=self.env)

    def finalize(self):
        return run(CHECKPOINT, "finalize", "--brand", "Acme", "--run-id", self.run_id, env=self.env)

    def test_a_real_audit_of_a_scaffolded_body_blocks_finalize(self):
        self.save_body(SCAFFOLDED)
        rc, report = self.audit()
        self.assertEqual(report["verdict"], "VIOLATIONS", report)
        rc, got = self.finalize()
        self.assertEqual(rc, 1, got)
        self.assertIn("VIOLATIONS", got["error"])

    def test_a_hand_written_clean_record_with_a_fresh_fingerprint_does_not_finalize_a_failing_run(self):
        self.save_body(SCAFFOLDED)
        rc, real = self.audit()
        self.assertEqual(real["verdict"], "VIOLATIONS", real)
        forged = {"verdict": "CLEAN", "fingerprint": _common.run_artifact_fingerprint(self.run_dir), "checks": []}
        (self.run_dir / "run-audit.json").write_text(json.dumps(forged), encoding="utf-8")
        rc, got = self.finalize()
        self.assertEqual(rc, 1, got)
        self.assertIn("fresh audit", got["error"])
        self.assertTrue(got["failing_checks"], got)
        manifest = json.loads((self.run_dir / "run.json").read_text(encoding="utf-8"))
        self.assertNotEqual(manifest["status"], "completed")

    def test_an_honest_clean_audit_still_finalizes(self):
        self.save_body(CLEAN)
        rc, report = self.audit()
        self.assertEqual(report["verdict"], "CLEAN", report)
        rc, got = self.finalize()
        self.assertEqual((rc, got.get("status")), (0, "completed"), got)

    def test_a_clean_run_edited_after_the_audit_is_still_refused(self):
        self.save_body(CLEAN)
        self.audit()
        self.save_body(CLEAN + "\nOne more line.\n")
        rc, got = self.finalize()
        self.assertEqual(rc, 1, got)
        self.assertIn("changed after it was audited", got["error"])


if __name__ == "__main__":
    unittest.main()
