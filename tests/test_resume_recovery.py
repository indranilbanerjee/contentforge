"""Defects in the crash-recovery path, found by crashing a real run.

A self-orchestrated 10-phase run had its agent hit a session usage limit
mid-Phase 7. `phase-7-review.json` was already complete on disk — 45KB,
overall_score 8.3, decision APPROVED — but the checkpoint had not been recorded.

`resume` reported `next_phase: 7`.

Following that literally would have discarded a finished review and re-run the
reviewer. The cause: `get_status` derived `next_phase` from
`manifest["completed_phases"]` alone and never looked at the run directory. So
the crash window this recovery path exists for — between "artifact written" and
"checkpoint recorded" — was the one window it could not see.

Also pinned here: checkpointing was not byte-stable on Windows (universal-newline
read + os.linesep write turned 45,087 bytes into 45,551 and changed the sha256,
breaking a provenance hash recorded in phase-8-output.json), and the Gate 8
appendix count in the contract disagreed with the config it says wins.

Stdlib only.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = _load("cf_checkpoint_manager", "checkpoint-manager.py")


class TestResumeSeesOrphanedArtifacts(unittest.TestCase):
    """The manifest is not the only source of truth about what happened."""

    def _run(self, tmp, completed, files):
        rd = Path(tmp) / "b" / "runs" / "r1"
        rd.mkdir(parents=True)
        (rd / "run.json").write_text(json.dumps({
            "run_id": "r1", "brand": "b", "topic": "t", "content_type": "blog",
            "meta": {}, "status": "in_progress", "completed_phases": completed,
            "phase_artifacts": {}, "loop_counts": {}, "total_loops": 0,
            "pending_rework": None, "phase_order": cm.PHASE_ORDER,
        }), encoding="utf-8")
        for f in files:
            (rd / f).write_text("artifact body", encoding="utf-8")
        return rd

    def test_artifact_without_checkpoint_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            orig = cm._run_dir
            rd = self._run(tmp, ["0.5", "1", "2"], ["phase-3-draft.md"])
            cm._run_dir = lambda b, r: rd
            try:
                st = cm.get_status("b", "r1")
            finally:
                cm._run_dir = orig
            phases = [o["phase"] for o in st["orphaned_artifacts"]]
            self.assertIn("3", phases,
                          "a written-but-uncheckpointed artifact must be surfaced")
            self.assertIsNotNone(st["reconciliation_note"])
            self.assertIn("does NOT account for them", st["reconciliation_note"])

    def test_a_clean_run_reports_no_orphans(self):
        with tempfile.TemporaryDirectory() as tmp:
            orig = cm._run_dir
            rd = self._run(tmp, ["0.5", "1"], [])
            cm._run_dir = lambda b, r: rd
            try:
                st = cm.get_status("b", "r1")
            finally:
                cm._run_dir = orig
            self.assertEqual(st["orphaned_artifacts"], [])
            self.assertIsNone(st["reconciliation_note"],
                              "no note when there is nothing to reconcile")

    def test_next_phase_is_still_reported_unchanged(self):
        """The reconciliation is additive. next_phase keeps its old meaning so
        nothing downstream changes behaviour silently; the note is what tells a
        caller the number is incomplete."""
        with tempfile.TemporaryDirectory() as tmp:
            orig = cm._run_dir
            rd = self._run(tmp, ["0.5", "1", "2"], ["phase-3-draft.md"])
            cm._run_dir = lambda b, r: rd
            try:
                st = cm.get_status("b", "r1")
            finally:
                cm._run_dir = orig
            self.assertEqual(st["next_phase"], "3")


class TestCheckpointingIsByteStable(unittest.TestCase):
    """A re-save must not change the file. Gate failures re-save the looped
    phase, so churn here breaks any hash-based provenance — and it did: a
    source_sha256 recorded in phase-8-output.json did not match sha256sum."""

    def test_crlf_content_survives_a_save_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            rd = Path(tmp) / "b" / "runs" / "r1"
            rd.mkdir(parents=True)
            (rd / "run.json").write_text(json.dumps({
                "run_id": "r1", "brand": "b", "topic": "t", "content_type": "blog",
                "meta": {}, "status": "in_progress", "completed_phases": [],
                "phase_artifacts": {}, "loop_counts": {}, "total_loops": 0,
                "pending_rework": None, "phase_order": cm.PHASE_ORDER,
            }), encoding="utf-8")
            content = "line one\r\nline two\r\nline three\r\n"
            orig = cm._run_dir
            cm._run_dir = lambda b, r: rd
            try:
                cm.save_phase("b", "r1", "3", content, "md")
            finally:
                cm._run_dir = orig
            written = (rd / "phase-3-draft.md").read_bytes()
            self.assertEqual(written, content.encode("utf-8"),
                             "save must not translate newlines — a re-save that "
                             "changes bytes invalidates every recorded hash")


class TestGate8AgreesWithItsConfig(unittest.TestCase):
    """SKILL.md states that where the doc and the config disagree, the config
    wins. The Gate 8 row asked for A/B/C while the config required 4 — so a
    Phase 8 emitting three appendices passed the doc and failed the config."""

    def test_contract_matches_configured_appendix_count(self):
        cfg = json.loads((REPO / "config" / "scoring-thresholds.json").read_text(encoding="utf-8"))
        def find(o):
            if isinstance(o, dict):
                if "appendices_present" in o:
                    return o["appendices_present"]
                for v in o.values():
                    r = find(v)
                    if r is not None:
                        return r
            return None
        required = find(cfg)
        self.assertEqual(required, 4, "config changed; update the contract too")
        skill = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Appendices A/B/C present", skill,
                         "the contract must not ask for fewer appendices than the config")
        self.assertIn("Internal Link Map", skill,
                      "name the fourth appendix the config requires")


class TestSilentSubagentHasARecoveryRule(unittest.TestCase):
    def test_contract_says_audit_the_disk_before_re_running(self):
        skill = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("If a subagent returns nothing", skill)
        self.assertIn("orphaned_artifacts", skill,
                      "the resume rule must reference the field that reports them")


if __name__ == "__main__":
    unittest.main()
