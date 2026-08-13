"""Tier-2 structural tells: measured, advisory, and honest about what they see.

StoryScope (arXiv 2604.03136) showed AI text stays detectable on STRUCTURE
after a perfect surface pass. These tests pin the structural scan's behavior
in both directions (an AI-shaped fixture fires, a human-shaped one does not),
pin the advisory-never-a-gate rule, and pin the pipeline wiring: the humanizer
emits the review sheet, the reviewer guarantees it exists in every lane, and
the sheet states plainly that it has no relationship to any watermark.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tm = _load("text_metrics", "text-metrics.py")

_AI_PARA = ("Businesses today face many challenges in the modern landscape. It is "
            "important to remember that success typically requires careful planning and "
            "can often depend on many factors. Organizations may generally benefit from "
            "adopting best practices that can usually improve outcomes for teams.")
AI_FIXTURE = "# The Guide\n\n" + "".join(
    f"## {h}\n\n{_AI_PARA}\n\n{_AI_PARA}\n\nUltimately, this matters because planning "
    "is essential. In conclusion, the key takeaway is that preparation typically wins.\n\n"
    for h in ("Understanding The Basics", "Building The Foundation",
              "Growing The Business", "Scaling The Operation", "Measuring The Results"))

HUMAN_FIXTURE = """# What 14 months of failed cold email taught us

## The $4,300 mistake nobody warns you about

I spent Q3 2025 sending 11,000 cold emails through a client's ESP for Acme Robotics. Open rate: 61%. Meetings booked: 4.

Four.

Our deliverability consultant, Priya Sharma, put it bluntly: "You optimized the wrong funnel stage." She was right, and the fix took one afternoon of rewriting.

## Why the 61% open rate was a trap that took us months to see

Opens measure subject lines. Meetings measure the offer. According to HubSpot's 2026 State of Sales report, reply-to-meeting conversion sits near 9% for B2B SaaS — we were at 2.1%.

The gap came from one paragraph in our template, the one bragging about features. I killed it and replaced it with a single case number: "We cut Vertex Manufacturing's quote-turnaround from 6 days to 11 hours." Replies tripled in two weeks, from 38 to 117.

## What I'd tell anyone starting this in 2026

Skip the sequence tooling debates entirely. Spend the first week interviewing five customers about why they actually bought — record the calls and quote them verbatim.

The tools don't book the meetings. The specifics do, and I have fourteen months of expensive proof of exactly that.
"""


class TestStructureScanFiresOnAIShape(unittest.TestCase):
    def setUp(self):
        self.result = tm.structure_scan(AI_FIXTURE)

    def test_overall_attention(self):
        self.assertEqual(self.result["overall"], "ATTENTION")

    def test_the_transferable_storyscope_tells_all_fire(self):
        f = self.result["findings"]
        for key in ("moralizing", "section_symmetry", "parallel_headings",
                    "specificity", "stance"):
            self.assertEqual(f[key]["band"], "ATTENTION",
                             f"{key} did not fire on the AI-shaped fixture")

    def test_moralizing_carries_spans_for_the_review_sheet(self):
        spans = self.result["findings"]["moralizing"]["spans"]
        self.assertTrue(spans, "moralizing finding has no spans — the sheet "
                               "cannot show the editor where to work")
        self.assertIn("phrase", spans[0])


class TestStructureScanStaysQuietOnHumanShape(unittest.TestCase):
    def test_human_fixture_reads_ok_on_the_core_tells(self):
        f = tm.structure_scan(HUMAN_FIXTURE)["findings"]
        for key in ("moralizing", "section_symmetry", "parallel_headings",
                    "specificity", "stance"):
            self.assertEqual(f[key]["band"], "OK",
                             f"{key} false-fired on the human-shaped fixture")


class TestAdvisoryNeverAGate(unittest.TestCase):
    def test_structural_thresholds_live_in_the_script_not_the_gate_config(self):
        cfg = json.loads((REPO / "config" / "scoring-thresholds.json").read_text(encoding="utf-8"))
        flat = json.dumps(cfg).lower()
        for needle in ("structure_scan", "moralizing", "specificity_per_1000",
                       "parallel_heading"):
            self.assertNotIn(needle, flat,
                             f"'{needle}' found in scoring-thresholds.json — the "
                             "structural tier must never become a scored gate")

    def test_scan_output_states_the_advisory_contract(self):
        note = tm.structure_scan(AI_FIXTURE)["advisory_note"]
        self.assertIn("advisory only", note)
        self.assertIn("no relationship to any statistical watermark", note)


class TestReviewSheet(unittest.TestCase):
    def test_sheet_builds_escapes_and_carries_both_tiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = Path(tmp) / "draft.md"
            hostile = AI_FIXTURE + "\n\nAlso <script>alert(1)</script> appears here.\n"
            draft.write_text(hostile, encoding="utf-8")
            out = Path(tmp) / "sheet.html"
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "build_review_sheet.py"),
                 "--draft", str(draft), "--out", str(out), "--title", "probe <x>"],
                capture_output=True, text=True, timeout=120)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = json.loads(proc.stdout)
            self.assertEqual(summary["tier2_overall"], "ATTENTION")
            self.assertGreater(summary["tier1_flagged_spans"], 0)
            html = out.read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
            self.assertIn("never a publish gate", html)
            self.assertIn("no relationship to any statistical watermark", html)
            self.assertIn("<mark", html)


class TestPipelineWiring(unittest.TestCase):
    def test_humanizer_runs_the_structural_scan_and_emits_the_sheet(self):
        text = (REPO / "agents" / "06.5-humanizer.md").read_text(encoding="utf-8")
        self.assertIn("--structure-scan", text)
        self.assertIn("build_review_sheet.py", text)
        self.assertIn("phase-6.5-review-sheet.html", text)
        self.assertIn("never invent content to satisfy a metric", text.lower())

    def test_reviewer_guarantees_the_sheet_in_every_lane(self):
        text = (REPO / "agents" / "07-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("Structural tells (advisory)", text)
        self.assertIn("the sheet must exist in every lane", text)

    def test_completion_card_surfaces_the_structural_line(self):
        text = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Structural tells (advisory)", text)

    def test_reference_doc_teaches_the_structural_tier(self):
        text = (REPO / "references" / "ai-detection-signals.md").read_text(encoding="utf-8")
        self.assertIn("2604.03136", text)
        self.assertIn("orthogonal to surface prose artifacts", text)


if __name__ == "__main__":
    unittest.main()
