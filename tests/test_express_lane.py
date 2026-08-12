"""The express lane may drop ceremony, never verification.

Express exists so users with their own research get speed — but the lane's
whole legitimacy rests on three invariants: fact-check (Gate 2) and
validation (Gate 4) and review (Gate 7) run in EVERY lane, the reviewer
treats chosen skips as choices rather than defects, and hard fails are
lane-independent. These tests pin those invariants into the orchestrator and
reviewer contracts so no future edit can quietly produce a gate-less lane.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ORCHESTRATOR = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(
    encoding="utf-8", errors="replace")
REVIEWER = (REPO / "agents" / "07-reviewer.md").read_text(
    encoding="utf-8", errors="replace")


def express_section() -> str:
    m = re.search(r"## Express Lane.*?(?=\n## )", ORCHESTRATOR, re.S)
    return m.group(0) if m else ""


class TestExpressLaneContract(unittest.TestCase):
    def test_express_lane_is_documented(self):
        self.assertTrue(express_section(), "orchestrator has no Express Lane section")

    def test_thesis_gates_are_in_the_express_phase_set(self):
        sec = express_section()
        for agent in ("contentforge:fact-checker",
                      "contentforge:scientific-validator",
                      "contentforge:reviewer"):
            self.assertIn(agent, sec,
                          f"express lane no longer dispatches {agent} — a lane "
                          "without its verification gates is not a lane, it is a bypass")
        for phrase in ("UNCHANGED — Gate 2 in full", "UNCHANGED — Gate 4 in full"):
            self.assertIn(phrase, sec,
                          "the verification gates must be marked unchanged in express")

    def test_no_gateless_phase_promise(self):
        self.assertIn("no gate-less phase in any lane", express_section())

    def test_lane_is_recorded_in_run_json(self):
        sec = express_section()
        self.assertIn('"mode": "express"', sec)
        self.assertIn("skipped_phases", sec)

    def test_skipped_phases_are_readdable_by_flag(self):
        sec = express_section()
        for flag in ("--with-visuals", "--with-structure", "--with-seo",
                     "--with-humanizer"):
            self.assertIn(flag, sec, f"{flag} missing — skips must be re-addable")

    def test_reviewer_has_the_express_contract(self):
        self.assertIn("## EXPRESS RUNS", REVIEWER)
        self.assertIn('"mode": "express"', REVIEWER)
        # The probe finding that motivated this: missing-report caps must not
        # fire on chosen skips, or every express run halts.
        self.assertIn("does NOT apply", REVIEWER)
        self.assertIn("Hard fails are lane-independent", REVIEWER)

    def test_reviewer_still_caps_missing_verification_artifacts(self):
        """Express relaxes caps ONLY for skipped polish phases — a missing
        Phase 2/4 artifact stays a defect in every lane."""
        m = re.search(r"## EXPRESS RUNS.*?(?=\n## |\Z)", REVIEWER, re.S)
        self.assertIsNotNone(m)
        self.assertIn("that IS a defect", m.group(0))


if __name__ == "__main__":
    unittest.main()
