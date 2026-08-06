"""--ai-tell-scan: deterministic detector-signal proxies. Advisory only."""
import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("tmetrics", SCRIPTS / "text-metrics.py")
tm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tm)

AI_SOUNDING = """Speed wins the shelf. Moreover, the landscape is shifting fast.
Furthermore, capacity gets you a slot. Leveraging the platform, teams delve into
seamless workflows. Ultimately, execution is everything. The market rewards focus.
"""

GROUNDED = """In June 2024 the agency finalized its clinical-pharmacology guidance
for this drug class (Agency, 2024). Submissions after that date must include
six-month stability data at the proposed storage condition — a census, in effect,
of how each batch actually behaves. Timelines still vary with agency workload;
the 2024 cohort averaged nine months from submission to decision.
"""


class TestTellScan(unittest.TestCase):
    def test_ai_sounding_scores_worse_than_grounded(self):
        ai = tm.ai_tell_scan(AI_SOUNDING)
        human = tm.ai_tell_scan(GROUNDED)
        self.assertGreater(ai["per_1000_words"]["aphorism_candidates"],
                           human["per_1000_words"]["aphorism_candidates"])
        self.assertGreater(ai["per_1000_words"]["banned_lexemes"],
                           human["per_1000_words"]["banned_lexemes"])
        self.assertGreater(ai["connective_openers_pct"], human["connective_openers_pct"])

    def test_ratings_ordered(self):
        self.assertEqual(tm.ai_tell_scan(AI_SOUNDING)["advisory_rating"], "HIGH")
        self.assertEqual(tm.ai_tell_scan(GROUNDED)["advisory_rating"], "LOW")

    def test_aphorism_heuristic(self):
        self.assertTrue(tm.is_aphorism_candidate("Speed wins the shelf."))
        self.assertFalse(tm.is_aphorism_candidate("Revenue rose 14% in Q2 2026."))
        self.assertFalse(tm.is_aphorism_candidate("What does the guidance require?"))

    def test_flagged_sentences_present(self):
        flags = tm.ai_tell_scan(AI_SOUNDING)["flagged_sentences"]
        self.assertTrue(any(f["tell"] == "aphorism_candidate" for f in flags))

    def test_advisory_note_always_present(self):
        self.assertIn("advisory", tm.ai_tell_scan(GROUNDED)["advisory_note"].lower())


if __name__ == "__main__":
    unittest.main()
