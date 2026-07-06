"""text-metrics.py tests — burstiness ordering, FK sanity, keyword placement,
structured-element counting."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

spec = importlib.util.spec_from_file_location("cf_text_metrics", SCRIPTS_DIR / "text-metrics.py")
tm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tm)


UNIFORM = " ".join(["The quick brown fox jumps over one lazy dog today."] * 10)

VARIED = (
    "Short one. "
    "This considerably longer sentence rambles across many additional words to inflate its length dramatically for testing purposes. "
    "Tiny. "
    "Here is another moderately sized sentence with a dozen or so words in it. "
    "No. "
    "The final sentence of this fixture is also quite long because burstiness rewards a wide spread of sentence lengths across the passage."
)

KEYWORD_DOC = """---
title: ignored frontmatter title
---
# AI in Healthcare: The 2026 Guide

AI in healthcare is the use of machine learning to improve patient outcomes.
Hospitals adopt it for triage, imaging, and operations planning.

## How does AI in healthcare work?

Models ingest clinical data. They flag anomalies for clinicians.

## Benefits for hospital operators

- Faster triage
- Fewer errors

## Conclusion

Adopting ai in healthcare early compounds the advantage.
"""

STRUCTURE_DOC = """# Structured Answer-First Piece

**Burstiness**: a measure of sentence-length variation across a passage.

## What is keyword clustering?

Keyword clustering is the practice of grouping queries by SERP overlap.

## How do you deploy it?

1. Gather queries
2. Cluster them
3. Map to pages

## Checklist

- item one
- item two

Additional prose paragraph here.

- another list starts
- with two items

| Col A | Col B |
|-------|-------|
| 1     | 2     |
"""


class TestBurstiness(unittest.TestCase):
    def test_uniform_lower_than_varied(self):
        uniform = tm.analyze(UNIFORM)
        varied = tm.analyze(VARIED)
        self.assertLess(uniform["burstiness"], varied["burstiness"])
        self.assertAlmostEqual(uniform["burstiness"], 0.0, places=3)
        self.assertGreater(varied["burstiness"], 0.3)

    def test_burstiness_capped_at_1(self):
        result = tm.analyze("A. " + "w " * 400 + ".")
        self.assertLessEqual(result["burstiness"], 1.0)


class TestFleschKincaid(unittest.TestCase):
    def test_simple_prose_scores_low(self):
        simple = tm.analyze("The cat sat on the mat. The dog ran to the park. We like to eat food.")
        self.assertLess(simple["fk_grade"], 6.0)

    def test_complex_prose_scores_higher(self):
        complex_doc = tm.analyze(
            "Organizational transformation initiatives necessitate comprehensive stakeholder "
            "alignment throughout implementation, particularly when interdependent technological "
            "infrastructure modernization considerations complicate prioritization frameworks."
        )
        simple = tm.analyze("The cat sat on the mat. The dog ran fast.")
        self.assertGreater(complex_doc["fk_grade"], simple["fk_grade"])

    def test_counts_present(self):
        r = tm.analyze(UNIFORM)
        self.assertEqual(r["sentence_count"], 10)
        self.assertGreaterEqual(r["word_count"], 90)


class TestKeywordPlacements(unittest.TestCase):
    def test_placements(self):
        r = tm.analyze(KEYWORD_DOC, keyword="AI in Healthcare")
        p = r["keyword_placements"]
        self.assertTrue(p["in_title"])
        self.assertTrue(p["in_first_100_words"])
        self.assertEqual(p["h2_count_with_keyword"], 1)
        self.assertTrue(p["in_conclusion"])
        self.assertGreaterEqual(r["keyword_count"], 3)
        self.assertGreater(r["keyword_density_pct"], 0)

    def test_absent_keyword(self):
        r = tm.analyze(KEYWORD_DOC, keyword="quantum basket weaving")
        self.assertEqual(r["keyword_count"], 0)
        self.assertFalse(r["keyword_placements"]["in_title"])
        self.assertFalse(r["keyword_placements"]["in_conclusion"])


class TestStructuredElements(unittest.TestCase):
    def test_counts(self):
        s = tm.analyze(STRUCTURE_DOC)["structured_elements"]
        self.assertEqual(s["qa_headers"], 2)          # two "?" H2s
        self.assertEqual(s["numbered_lists"], 1)
        self.assertEqual(s["bullet_lists"], 2)
        self.assertEqual(s["tables"], 1)
        self.assertGreaterEqual(s["definition_patterns"], 2)  # bold-term + "is the practice of"

    def test_qa_headers_in_keyword_doc(self):
        s = tm.analyze(KEYWORD_DOC)["structured_elements"]
        self.assertEqual(s["qa_headers"], 1)


if __name__ == "__main__":
    unittest.main()
