"""Every file name a model supplies stays inside the run directory it belongs to.

Found in 4.5.12 by an audit of the installed scripts:
  * `fix-ledger.py apply --target ../outside.md` exited 0 and rewrote a file outside the run (`--target` and `--source-draft`
    were joined as `run_dir / name`, and an absolute path was accepted on purpose). `verify`, `resolve` and `validate` read
    the same way;
  * `run-audit.py` took the body's file name from run.json and read `run_dir / name`; with checkpoint-manager's old
    `--extension` hole, a poisoned artifact name reached fix-ledger through the audit;
  * `drive-sync-state.py --file ../../../x.md` stored the traversal name for the agent to upload;
  * `fix-ledger apply --dry-run` reported `file_changed: true` although nothing was written.
Each fix has a test on the whole chain below. Everything runs in a temp HOME and workspace.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
LEDGER = SCRIPTS / "fix-ledger.py"
AUDIT = SCRIPTS / "run-audit.py"
CHECKPOINT = SCRIPTS / "checkpoint-manager.py"
DRIVE = SCRIPTS / "drive-sync-state.py"


def run(script, *args, env=None):
    proc = subprocess.run([sys.executable, str(script), *args], capture_output=True, env=env, timeout=180)
    out = proc.stdout.decode("utf-8", "replace").strip()
    try:
        payload = json.loads(out) if out else {}
    except ValueError:
        payload = {"_unparseable": out}
    return proc.returncode, payload, proc.stderr.decode("utf-8", "replace")


def ledger(find="1997", replace="1998"):
    return {"schema": "contentforge.fix-ledger/1", "run_id": "t", "emitted_by": "phase-4",
            "items": [{"id": "T1", "severity": "MINOR", "blocking": True, "class": "text_replace", "rationale": "year",
                       "status": "pending", "applied_at_phase": None, "applied_to": None, "note": None,
                       "find": find, "replace": replace}]}


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.run_dir = self.root / "run"
        self.run_dir.mkdir()
        self.outside = self.root / "outside.md"
        self.outside.write_text("The café opened in 1997 outside.\n", encoding="utf-8")
        self.outside_before = self.outside.read_bytes()
        (self.run_dir / "body.md").write_text("The café opened in 1997 inside.\n", encoding="utf-8")
        (self.run_dir / "phase-4-fixes.json").write_text(json.dumps(ledger()), encoding="utf-8")
        self.env = {**os.environ, "HOME": str(self.root), "USERPROFILE": str(self.root),
                    "CLAUDE_MARKETING_HOME": str(self.root / "ws"), "PYTHONUTF8": "1"}
        for name in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA"):
            self.env.pop(name, None)

    def ledger_cmd(self, command, *args):
        return run(LEDGER, command, "--run-dir", str(self.run_dir), *args, env=self.env)


class TestFixLedgerStaysInTheRun(Case):

    def test_a_target_with_dotdot_is_refused_and_the_outside_file_is_untouched(self):
        before = self.outside_before
        for command in ("apply", "verify", "resolve", "validate"):
            extra = ("--id", "T1", "--already-satisfied") if command == "resolve" else ()
            with self.subTest(command=command):
                rc, payload, err = self.ledger_cmd(command, "--target", "../outside.md", *extra)
                self.assertEqual(rc, 2, (payload, err))
        self.assertEqual(self.outside.read_bytes(), before)

    def test_an_absolute_target_is_refused(self):
        rc, payload, err = self.ledger_cmd("apply", "--target", str(self.outside))
        self.assertEqual(rc, 2, (payload, err))
        self.assertEqual(self.outside.read_bytes(), self.outside_before)

    def test_a_source_draft_outside_the_run_is_refused(self):
        rc, payload, err = self.ledger_cmd("apply", "--target", "body.md", "--source-draft", "../outside.md")
        self.assertEqual(rc, 2, (payload, err))
        self.assertIn("1997", (self.run_dir / "body.md").read_text(encoding="utf-8"))

    def test_a_plain_file_name_still_applies(self):
        rc, payload, err = self.ledger_cmd("apply", "--target", "body.md", "--phase", "5")
        self.assertEqual(rc, 0, (payload, err))
        self.assertIn("1998", (self.run_dir / "body.md").read_text(encoding="utf-8"))

    def test_a_dry_run_says_would_change_and_does_not_claim_a_change(self):
        rc, payload, err = self.ledger_cmd("apply", "--target", "body.md", "--dry-run")
        self.assertEqual(rc, 0, (payload, err))
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["file_changed"], payload)
        self.assertTrue(payload["would_change"], payload)
        self.assertIn("1997", (self.run_dir / "body.md").read_text(encoding="utf-8"))

    def test_a_real_run_reports_file_changed(self):
        rc, payload, _ = self.ledger_cmd("apply", "--target", "body.md")
        self.assertEqual(rc, 0, payload)
        self.assertTrue(payload["file_changed"])
        self.assertTrue(payload["would_change"])


class TestDriveSyncNames(Case):

    def drive(self, *args):
        rc, payload, err = run(DRIVE, *args, env=self.env)
        return rc, payload, err

    def test_a_traversal_file_name_is_refused_and_nothing_is_stored(self):
        rc, payload, err = run(CHECKPOINT, "init", "--brand", "Acme", "--topic", "Sync", "--content-type", "article", env=self.env)
        self.assertEqual(rc, 0, payload)
        run_id = payload["run_id"]
        for bad in ("../../../x.md", "..\\x.md", "/etc/x.md", "a/b.md"):
            with self.subTest(file=bad):
                rc, payload, err = self.drive("--action", "add-pending-upload", "--brand", "Acme", "--run-id", run_id, "--file", bad)
                self.assertEqual(rc, 2, (payload, err))
        rc, listed, _ = self.drive("--action", "list-pending-uploads", "--brand", "Acme", "--run-id", run_id)
        self.assertEqual(listed.get("pending", []), [])
        rc, payload, err = self.drive("--action", "add-pending-upload", "--brand", "Acme", "--run-id", run_id, "--file", "phase-3-draft.md")
        self.assertEqual(rc, 0, (payload, err))


class TestThePoisonedArtifactChain(Case):
    """checkpoint-manager (save) -> run.json -> run-audit -> fix-ledger verify, with a name that points outside the run."""

    def make_run(self):
        rc, payload, _ = run(CHECKPOINT, "init", "--brand", "Acme", "--topic", "Chain", "--content-type", "article", env=self.env)
        self.assertEqual(rc, 0, payload)
        self.run_id = payload["run_id"]
        run_path = Path(payload["path"]) if "path" in payload else None
        if run_path is None:
            for found in (self.root / "ws").rglob(self.run_id):
                run_path = found
        return run_path

    def test_save_refuses_the_traversal_extension_so_the_chain_cannot_start_there(self):
        self.make_run()
        rc, payload, err = run(CHECKPOINT, "save", "--brand", "Acme", "--run-id", self.run_id, "--phase", "6.5",
                               "--content", "BODY", "--extension", "../../../../outside-from-extension.md", env=self.env)
        self.assertEqual(rc, 2, (payload, err))
        self.assertEqual(list(self.root.rglob("outside-from-extension*")), [])

    def test_a_hand_poisoned_run_json_is_flagged_by_the_audit_and_the_outside_file_is_not_read(self):
        run_path = self.make_run()
        secret = self.root / "secret-outside.md"
        secret.write_text("DO-NOT-READ-ME [TODO: scaffolding marker]\n", encoding="utf-8")
        manifest = json.loads((run_path / "run.json").read_text(encoding="utf-8"))
        manifest["phase_artifacts"]["6.5"] = "../../../../../secret-outside.md"
        (run_path / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
        (run_path / "phase-4-fixes.json").write_text(json.dumps(ledger()), encoding="utf-8")
        rc, report, err = run(AUDIT, "--brand", "Acme", "--run-id", self.run_id, env=self.env)
        self.assertNotEqual(rc, 0, report)
        names = {c["name"]: c["result"] for c in report.get("checks", [])}
        self.assertEqual(names.get("phase artifact names stay inside the run"), "FAIL", names)
        self.assertNotIn("DO-NOT-READ-ME", json.dumps(report))
        self.assertEqual(report["verdict"], "VIOLATIONS")
        rc, payload, err = run(LEDGER, "verify", "--run-dir", str(run_path), "--target", "../../../../../secret-outside.md", env=self.env)
        self.assertEqual(rc, 2, (payload, err))


if __name__ == "__main__":
    unittest.main()
