"""Authorship preservation, significance markers (42/43), entity development.

Three capabilities mined from a public anti-detector skill and rebuilt as
quality tooling rather than evasion tooling. What these tests pin, above all,
is the direction of each feature:

  * patterns 42/43 DELETE filler, and the catalog must not simultaneously
    recommend the filler elsewhere (it did — that regression is pinned here);
  * entity development is fixed by DEVELOPING specifics, never by deleting
    them, and stays silent on pieces too short to measure;
  * authorship preservation may only ever UNDERSTATE human involvement, and
    an author's own sentences are exempt from the pattern catalog entirely.

Nothing here targets a detector, and no test asserts a "human enough" score.
"""
from __future__ import annotations

import importlib.util
import json
import re
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


tm = _load("tm_markers", "text-metrics.py")
auth = _load("authorship_mod", "authorship.py")
sheet = _load("review_sheet_mod", "build_review_sheet.py")

CATALOG = json.loads((REPO / "config" / "humanization-patterns.json").read_text(encoding="utf-8"))
HUMANIZER = (REPO / "agents" / "06.5-humanizer.md").read_text(encoding="utf-8")
REVIEWER = (REPO / "agents" / "07-reviewer.md").read_text(encoding="utf-8")
OUTPUT_MGR = (REPO / "agents" / "08-output-manager.md").read_text(encoding="utf-8")
DRAFTER = (REPO / "agents" / "03-content-drafter.md").read_text(encoding="utf-8")
ORCHESTRATOR = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")

# A long piece that introduces a fresh named specific in nearly every sentence
# and never returns to one: the shape the entity proxy exists to catch.
CHURN = "# Report\n\n## Findings\n\n" + " ".join(
    f"The {n} team logged a shift that quarter and staff there noted the change soon afterwards. "
    f"Analysts called the pattern broadly consistent with the prior period across that whole region. "
    f"Nobody involved disputed the summary that was circulated to the group later that same month. "
    for n in ("Fraunhofer", "Siemens", "Duisburg", "Stuttgart", "Hoffmann", "Weber",
              "Leipzig", "Kessler", "Hannover", "Baumann", "Dortmund", "Vogel",
              "Essen", "Bremen", "Aachen", "Kiel", "Rostock", "Ulm", "Trier", "Jena"))

AUTHOR_SOURCE = """ok so the thing that killed us was the 14 day estimate. we quoted it for two years and nobody checked.
i found out in march when the bavaria client missed their launch window.
turns out fraunhofer revised it twice and we never noticed, its 31 days now not 14.
we lost about 40k in rework on that one account alone.
"""

DRAFT_PRESERVED = """# Why our review estimates were wrong

ok so the thing that killed us was the 14 day estimate. we quoted it for two years and nobody checked.

The figure came from a 2019 Fraunhofer benchmark nobody on the team had revisited.

i found out in march when the bavaria client missed their launch window.

Kessler Partners audited the same Bavaria cohort in 2024 and landed at 30 days.

turns out fraunhofer revised it twice and we never noticed, its 31 days now not 14.

we lost about 40k in rework on that one account alone.
"""

DRAFT_LAUNDERED = """# Why our review estimates were wrong

The critical issue was the 14-day estimate. We quoted it for two years, and nobody verified it.

The figure came from a 2019 Fraunhofer benchmark nobody on the team had revisited.

I discovered this in March, when the Bavaria client missed their launch window.

turns out fraunhofer revised it twice and we never noticed, its 31 days now not 14.
"""


class TestSignificanceMarkers(unittest.TestCase):
    """Pattern 42 — the labelling sentence, deleted rather than reworded."""

    def test_catalog_defines_42_and_43_as_detector_signal_patterns(self):
        bucket = CATALOG["signs_of_ai_writing_catalog"]["detector_signal_patterns"]
        self.assertIn("42_significance_markers", bucket)
        self.assertIn("43_soft_adverb_feeling_tags", bucket)

    def test_42_is_weighted_high_signal(self):
        high = CATALOG["ai_signal_scoring"]["weights"]["high_signal_x2"]
        self.assertIn("42_significance_markers", high)

    def test_fix_strategy_is_deletion_not_rewording(self):
        p42 = CATALOG["signs_of_ai_writing_catalog"]["detector_signal_patterns"]["42_significance_markers"]
        fix = p42["fix_strategy"].lower()
        self.assertIn("delete", fix)
        self.assertIn("do not reword", fix)

    def test_scan_flags_the_marker_sentence_with_the_phrase(self):
        text = ("Approvals slipped from 14 days to 31 in the Bavaria cohort last year. "
                "Here's the thing, that is what really matters here. "
                "Reviewers confirmed the figure against payroll records from 2024.")
        scan = tm.ai_tell_scan(text)
        hits = [f for f in scan["flagged_sentences"] if f["tell"] == "significance_marker"]
        self.assertEqual(len(hits), 1, "the labelling sentence must be flagged")
        self.assertEqual(hits[0]["phrase"], "here's the thing")

    def test_curly_apostrophe_does_not_evade_the_scan(self):
        scan = tm.ai_tell_scan("The backlog doubled in Bavaria. Here’s the thing, it matters.")
        self.assertEqual(scan["significance_marker_count"], 1)

    def test_clean_prose_scores_zero_markers(self):
        text = ("Approvals slipped from 14 days to 31 in the Bavaria cohort. "
                "Reviewers confirmed the figure against payroll records from 2024.")
        self.assertEqual(tm.ai_tell_scan(text)["significance_marker_count"], 0)

    def test_literal_uses_of_marker_words_are_not_flagged(self):
        """Precision guard. 'that's the part' and 'the thing is' have ordinary
        literal senses; the phrase list is scoped so those survive. A scan that
        cries wolf on plain prose gets ignored, which costs more than it saves."""
        legitimate = [
            "Section 4 covers reviewer staffing. That's the part of the regulation that changed in June.",
            "The instrument arrived damaged. The thing is broken beyond any economical repair.",
        ]
        for text in legitimate:
            with self.subTest(text=text[:45]):
                self.assertEqual(tm.ai_tell_scan(text)["significance_marker_count"], 0,
                                 "literal prose must not be flagged as a significance marker")

    def test_marker_senses_still_fire(self):
        for text, phrase in (
            ("The median rose to 31 days. Here's the thing, that is the part that matters.", "here's the thing"),
            ("Approvals slipped badly. The thing is, nobody checked the benchmark for years.", "the thing is,"),
        ):
            with self.subTest(phrase=phrase):
                scan = tm.ai_tell_scan(text)
                self.assertEqual(scan["significance_marker_count"], 1)


class TestSoftAdverbTags(unittest.TestCase):
    """Pattern 43 — clusters are the tell; one earned use is not."""

    def test_cluster_sentence_is_counted(self):
        scan = tm.ai_tell_scan("It was genuinely a quietly remarkable shift for the whole team.")
        self.assertEqual(scan["soft_adverb_cluster_sentences"], 1)

    def test_single_legitimate_use_in_a_short_piece_does_not_force_high(self):
        """The floor that keeps arithmetic from manufacturing a tell: one
        'actually' in 200 words normalizes to ~5 per 1000, over the threshold,
        yet is plainly not a pattern."""
        text = ("We spent the first week interviewing five customers about why they actually "
                "bought the product, and recorded every call. " + "The team reviewed each "
                "transcript against the 2024 pipeline data before rewriting the offer. " * 12)
        scan = tm.ai_tell_scan(text)
        self.assertLess(scan["per_1000_words"]["soft_adverb_tags"], 4.0 * 3,
                        "sanity: fixture should carry exactly one soft adverb")
        self.assertNotEqual(scan["advisory_rating"], "HIGH",
                            "a single earned soft adverb must not drive the scan to HIGH")


class TestCatalogDoesNotRecommendWhatItRemoves(unittest.TestCase):
    """The regression this whole pass started from: ContentForge told the
    drafter to write 'Here's the thing' in the conversational voice profile
    and the blog template, while the humanizer was meant to strip it. A
    catalog that plants its own tells cannot remove them."""

    TEMPLATE_FILES = [
        REPO / "templates" / "content-types" / "blog-structure.md",
        REPO / "templates" / "content-types" / "whitepaper-structure.md",
        REPO / "templates" / "content-types" / "article-structure.md",
    ]
    # The catalog's own ban list and lexicon legitimately quote these phrases;
    # advice lives in the writing-guidance sections, so those are what we scan.
    ADVICE_SECTIONS = ("personality_profiles", "sentence_structure_patterns",
                       "humanization_techniques", "ai_telltale_phrases")
    BANNED_ADVICE = ("here's the thing", "here's where it gets interesting",
                     "here's why this matters", "but wait, there's more",
                     "ever wondered", "bottom line:")

    def test_writing_guidance_sections_never_recommend_a_marker(self):
        offenders = []
        for section in self.ADVICE_SECTIONS:
            blob = json.dumps(CATALOG.get(section, {}), ensure_ascii=False)
            for line in re.split(r'","|",\s*"', blob):
                low = line.lower()
                forbids = any(w in low for w in (
                    "never", "avoid", "do not", "don't", "pattern 42", "pattern 28",
                    "banned", "strip", "delete", "humanizer", "not sentence variety"))
                if any(b in low for b in self.BANNED_ADVICE) and not forbids:
                    offenders.append(f"{section}: {line.strip()[:100]}")
        self.assertEqual(offenders, [],
                         "these entries recommend a phrase the humanizer removes:\n" +
                         "\n".join(offenders))

    def test_content_type_templates_never_recommend_a_marker(self):
        offenders = []
        for path in self.TEMPLATE_FILES:
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                low = line.lower()
                forbids = any(w in low for w in (
                    "never", "not ", "avoid", "do not", "don't", "pattern 42",
                    "banned", "strip", "delete", "humanizer"))
                if any(b in low for b in self.BANNED_ADVICE) and not forbids:
                    offenders.append(f"{path.name}:{i}: {line.strip()[:90]}")
        self.assertEqual(offenders, [],
                         "these template lines recommend a phrase the humanizer removes:\n" +
                         "\n".join(offenders))

    def test_conversational_voice_profile_points_at_pattern_42(self):
        techniques = json.dumps(CATALOG["personality_profiles"]["conversational"]["techniques"],
                                ensure_ascii=False).lower()
        self.assertIn("pattern 42", techniques,
                      "the conversational profile must name the pattern it used to violate")


class TestEntityDevelopment(unittest.TestCase):
    """Fixed by developing specifics, never by deleting them."""

    def test_churn_fires_on_a_long_undeveloped_piece(self):
        f = tm.structure_scan(CHURN)["findings"]["entity_development"]
        self.assertTrue(f["measurable"])
        self.assertEqual(f["band"], "ATTENTION")
        self.assertLessEqual(f["mentions_per_entity"], 1.25)

    def test_short_piece_is_not_banded(self):
        """A 200-word piece names things once for lack of room. Banding that
        would punish brevity and contradict the specificity finding."""
        short = ("# Note\n\n## Result\n\nThe Fraunhofer report put Bavaria at 31 days in 2024, "
                 "and Kessler Partners agreed within a day. " * 3)
        f = tm.structure_scan(short)["findings"]["entity_development"]
        self.assertFalse(f["measurable"])
        self.assertEqual(f["band"], "OK")

    def test_meaning_forbids_fixing_by_deletion(self):
        f = tm.structure_scan(CHURN)["findings"]["entity_development"]
        meaning = f["meaning"].lower()
        self.assertIn("never by deleting", meaning)
        self.assertIn("forbidden", meaning)

    def test_thresholds_live_in_script_never_in_scored_config(self):
        """Same rule as the rest of the structural tier: an advisory proxy's
        thresholds must not leak into a file the quality gates read."""
        self.assertIn("mentions_per_entity", tm._BANDS)
        scored = (REPO / "config" / "scoring-thresholds.json").read_text(encoding="utf-8")
        self.assertNotIn("mentions_per_entity", scored)
        self.assertNotIn("entity_development", scored)

    def test_humanizer_teaches_the_develop_not_delete_fix(self):
        self.assertIn("Fix by developing, never by deleting", HUMANIZER)


class TestAuthorshipPreservation(unittest.TestCase):
    """The author's sentences survive, or the pipeline says so."""

    def test_preserved_draft_reports_no_violations(self):
        r = auth.classify(AUTHOR_SOURCE, DRAFT_PRESERVED)
        self.assertEqual(r["violations"]["author_sentences_rewritten"], 0)
        self.assertEqual(r["violations"]["author_sentences_dropped"], 0)
        self.assertEqual(r["counts"]["author_verbatim"], 5)

    def test_paraphrasing_the_author_is_caught_as_a_violation(self):
        r = auth.classify(AUTHOR_SOURCE, DRAFT_LAUNDERED)
        self.assertGreaterEqual(r["violations"]["author_sentences_rewritten"], 2)
        self.assertGreaterEqual(r["violations"]["author_sentences_dropped"], 1)
        rewritten = " ".join(x["text"].lower() for x in r["rewritten"])
        self.assertIn("nobody verified it", rewritten,
                      "the 'improved' version of the author's sentence must be named")

    def test_repeating_one_author_sentence_cannot_inflate_their_share(self):
        """One-to-one matching: echoing the author's line five times does not
        make the piece five times more theirs."""
        padded = DRAFT_PRESERVED + "\n\n" + ("we lost about 40k in rework on that one account alone.\n\n" * 4)
        r = auth.classify(AUTHOR_SOURCE, padded)
        self.assertEqual(r["counts"]["author_verbatim"], 5)

    def test_script_exits_3_on_violations_and_0_when_clean(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            src = td / "source.md"
            src.write_text(AUTHOR_SOURCE, encoding="utf-8")
            for name, body, expected in (("good", DRAFT_PRESERVED, 0),
                                         ("bad", DRAFT_LAUNDERED, 3)):
                d = td / f"{name}.md"
                d.write_text(body, encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, str(SCRIPTS / "authorship.py"),
                     "--source", str(src), "--draft", str(d)],
                    capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(proc.returncode, expected,
                                 f"{name} draft: expected exit {expected}, got {proc.returncode}")

    def test_missing_file_reports_error_not_crash(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "authorship.py"),
             "--source", "no-such-file.md", "--draft", "also-missing.md"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not found", proc.stdout)


class TestAuthoredClaimCannotBeOverstated(unittest.TestCase):
    """The disclosure may only ever understate human authorship."""

    def test_clean_and_substantial_may_claim(self):
        self.assertTrue(auth.classify(AUTHOR_SOURCE, DRAFT_PRESERVED)["may_claim_authored"])

    def test_outstanding_violation_blocks_the_authored_claim(self):
        r = auth.classify(AUTHOR_SOURCE, DRAFT_LAUNDERED)
        self.assertFalse(r["may_claim_authored"],
                         "a piece that rewrote the author's sentences must not claim they wrote it")

    def test_trivial_author_share_blocks_the_authored_claim(self):
        thin = ("# Piece\n\n" + "The 2024 Fraunhofer review put the Bavaria median at 31 days "
                "and Kessler Partners confirmed it independently. " * 40
                + "\n\nwe lost about 40k in rework on that one account alone.\n")
        r = auth.classify(AUTHOR_SOURCE, thin)
        self.assertLess(r["author_word_share"], auth.AUTHORED_WORD_SHARE_FLOOR)
        self.assertFalse(r["may_claim_authored"])

    def test_no_source_draft_means_no_claim(self):
        self.assertFalse(auth.classify("", DRAFT_PRESERVED)["may_claim_authored"])

    def test_output_manager_reads_the_record_and_refuses_to_infer(self):
        self.assertIn("may_claim_authored", OUTPUT_MGR)
        self.assertIn("Never infer authorship from anything but this record", OUTPUT_MGR)

    def test_record_states_it_is_not_a_score_to_optimize(self):
        note = auth.classify(AUTHOR_SOURCE, DRAFT_PRESERVED)["note"].lower()
        self.assertIn("not a score to optimize", note)
        self.assertIn("no relationship to any statistical watermark", note)


class TestAuthorSentencesAreExemptFromTheCatalog(unittest.TestCase):
    """The author wrote 'here's the thing' on purpose. It stays."""

    def test_humanizer_exempts_author_sentences_from_the_43_patterns(self):
        self.assertIn("The 43-pattern catalog does not apply to author sentences", HUMANIZER)
        self.assertIn("here's the thing", HUMANIZER.lower())

    def test_humanizer_forbids_grammar_fixing_the_author(self):
        self.assertIn("Never paraphrase, condense, merge, or grammar-fix", HUMANIZER)

    def test_drafter_carries_author_sentences_verbatim(self):
        self.assertIn("verbatim", DRAFTER)
        self.assertIn("source-draft.md", DRAFTER)

    def test_author_claims_are_not_treated_as_verified_facts(self):
        self.assertIn("Never present their claims as verified", DRAFTER)

    def test_reviewer_blocks_on_authorship_violations(self):
        self.assertIn("phase-6.5-authorship.json", REVIEWER)
        self.assertIn("BLOCKING finding", REVIEWER)

    def test_orchestrator_declares_the_artifact_and_the_intake(self):
        self.assertIn("phase-6.5-authorship.json", ORCHESTRATOR)
        self.assertIn("--source-draft", ORCHESTRATOR)
        self.assertIn("the mess is the signal", ORCHESTRATOR)


class TestNoEvasionSurfaceAnywhere(unittest.TestCase):
    """This work was mined from a detector-evasion skill. None of that came
    with it, and this test exists so none of it arrives later."""

    NEW_FILES = [
        SCRIPTS / "authorship.py",
        SCRIPTS / "text-metrics.py",
        REPO / "references" / "ai-detection-signals.md",
        REPO / "agents" / "06.5-humanizer.md",
    ]
    FORBIDDEN = ("zero-width", "homoglyph", "watermark removal", "remove the watermark",
                 "strip the watermark", "bypass the detector", "evade detection",
                 "pass as human", "discourse fracture")

    def test_no_evasion_technique_is_named_as_a_capability(self):
        offenders = []
        for path in self.NEW_FILES:
            low = path.read_text(encoding="utf-8").lower()
            for term in self.FORBIDDEN:
                if term in low:
                    offenders.append(f"{path.name}: {term}")
        self.assertEqual(offenders, [], f"evasion surface introduced: {offenders}")

    def test_authorship_script_disclaims_being_a_detector_tool(self):
        src = (SCRIPTS / "authorship.py").read_text(encoding="utf-8").lower()
        self.assertIn("not a detector-evasion tool", src)
        self.assertIn("no target ratio", src)


if __name__ == "__main__":
    unittest.main()


class TestAphorismProxyIsCalibrated(unittest.TestCase):
    """Field-test findings, 2026-08-14. Measured against a published human
    essay and a real generated article, the <=9-word aphorism heuristic fired
    at ~13 per 1000 words on both and drove them to a HIGH advisory rating —
    which the reviewer maps to a Readability sub-score of <=5. Good writing was
    being marked down by a proxy that cannot tell a maxim from a short fact."""

    def test_self_contained_maxims_still_flagged(self):
        for s in ("Speed wins the shelf.", "Strong brands design the data to travel.",
                  "The future looks bright.", "Quality matters above all else."):
            with self.subTest(s=s):
                self.assertTrue(tm.is_aphorism_candidate(s))

    def test_context_dependent_sentences_are_not_maxims(self):
        """A sentence pointing at a speaker, a reader, or the sentence before it
        cannot be the self-contained generalization pattern 36 targets."""
        for s in ("That is what you are looking for.",
                  "The next step is to notice them.",
                  "I decided to find out by making it.",
                  "But pick something and get going.",
                  "And that is not all."):
            with self.subTest(s=s):
                self.assertFalse(tm.is_aphorism_candidate(s))

    def test_aphorisms_do_not_drive_the_advisory_rating(self):
        """A signal too imprecise to gate on is too imprecise to headline a
        rating that feeds a reviewer score. Counted and reported, never rating."""
        maxims = "\n\n".join(["Speed wins the shelf. Quality matters above all else."] * 12)
        r = tm.ai_tell_scan(maxims)
        self.assertGreater(r["per_1000_words"]["aphorism_candidates"], 30,
                           "sanity: fixture should be dense with maxims")
        self.assertEqual(r["advisory_rating"], "LOW",
                         "aphorism density alone must not raise the rating")
        self.assertIn("aphorism_candidates", r["per_1000_words"],
                      "the metric must still be reported for the editor")


class TestRobustnessAndPerformance(unittest.TestCase):
    """Found by adversarial load testing, 2026-08-14.

    The original all-pairs matcher was quadratic: 0.47s at 100 sentences,
    11.43s at 500, and its difflib prefilter pruned nothing in exactly the case
    that matters — when the draft really does contain the author's sentences,
    every pair looks promising. A long whitepaper would have hung the phase.
    """

    ADVERSARIAL = {
        "empty": "", "whitespace": "   \n\n\t ", "single_char": "x",
        "no_punctuation": "this never ends",
        "unicode": "# 🎯 Résumé\n\nLe café naïve 日本語 Ελληνικά مرحبا\n",
        "rtl": "# שלום\n\nזהו טקסט עם 31 ו-14.\n",
        "cjk": "# 標題\n\n這是一段中文文字。第二句話。\n",
        "malformed_frontmatter": "---\ntitle: unterminated\n\n# H\n\nBody.\n",
        "unclosed_fence": "# D\n\n```py\nprint(1)\n\nAfter.\n",
        "null_bytes": "# D\x00\n\nText \x00 here.\n",
        "html": "# <script>alert(1)</script>\n\n<img src=x onerror=y>\n",
        "windows_newlines": "# D\r\n\r\nA line.\r\nAnother.\r\n",
        "only_punctuation": "... !!! ??? ---\n",
    }

    def test_scans_never_crash_on_adversarial_input(self):
        for name, text in self.ADVERSARIAL.items():
            with self.subTest(case=name):
                a = tm.ai_tell_scan(text)
                s = tm.structure_scan(text)
                self.assertIn(a["advisory_rating"], ("LOW", "MODERATE", "HIGH"))
                self.assertIn(s["overall"], ("OK", "NOTE", "ATTENTION"))
                for f in s["findings"].values():
                    self.assertIn(f["band"], ("OK", "NOTE", "ATTENTION"))

    def test_authorship_never_crashes_on_adversarial_input(self):
        for name, text in self.ADVERSARIAL.items():
            with self.subTest(case=name):
                r = auth.classify(text, text)
                self.assertEqual(r["violations"]["author_sentences_rewritten"], 0,
                                 "identical text must never report a rewrite")
                auth.classify(text, "")
                auth.classify("", text)

    def test_authorship_is_not_quadratic(self):
        """A 5000-sentence match must stay far under a second. The pre-fix
        implementation took 11.4s at 500 and would have been minutes here."""
        import time
        big = "The Fraunhofer report tracked review delays across Bavaria in 2024. " * 5000
        start = time.time()
        r = auth.classify(big, big)
        elapsed = time.time() - start
        self.assertEqual(r["counts"]["author_verbatim"], 5000)
        self.assertLess(elapsed, 5.0,
                        f"authorship matching took {elapsed:.1f}s on 5000 sentences — "
                        "the quadratic all-pairs behaviour has returned")

    def test_review_sheet_escapes_injected_html(self):
        text = "# <script>alert(1)</script>\n\nBody with <img src=x onerror=y>.\n"
        html = sheet.build_sheet(text, tm.ai_tell_scan(text), tm.structure_scan(text), "t")
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)


class TestTheReportMustNotLiveInTheMeasuredFile(unittest.TestCase):
    """Found by a live probe run, not by reasoning.

    Five humanizer probes ran against planted fixtures. Two followed the old
    instruction and appended the Humanization Report to
    `phase-6.5-humanized.md`; two deliberately deviated and flagged the problem
    unprompted. One of the two that complied produced a provenance record with
    104 ai_added sentences and `may_claim_authored: false` -- denying the author
    credit for work they actually did, purely because of where a report was
    written.

    `authorship.py` classifies EVERY sentence in the draft file. Report prose in
    that file is machine-added text by definition, so it dilutes
    `author_word_share`. Real runs landed at 0.253 and 0.250, directly on the
    0.25 floor, which is why this was not a theoretical risk.
    """

    ROOT = Path(__file__).resolve().parent.parent

    def test_appending_a_report_can_flip_the_authorship_verdict(self):
        """The measurement behind the fix. Violations stay clean either way --
        it is the SHARE that moves, which is the subtle part."""
        src = ("we spent two years on this and got it wrong twice.\n"
               "the fix in the end was unglamorous and took a fortnight.\n")
        body = ("# Title\n\nwe spent two years on this and got it wrong twice.\n\n"
                "A researched sentence adds context from the verified ledger here.\n\n"
                "the fix in the end was unglamorous and took a fortnight.\n")
        report = ("\n\n## Humanization Report\n\n"
                  + "The catalog was applied and the marker was deleted rather than reworded. " * 12)

        clean = auth.classify(src, body)
        dirty = auth.classify(src, body + report)

        self.assertTrue(clean["may_claim_authored"])
        self.assertFalse(dirty["may_claim_authored"],
                         "appending a report should dilute the author's share")
        self.assertLess(dirty["author_word_share"], clean["author_word_share"])
        self.assertEqual(clean["violations"], dirty["violations"],
                         "violations must be unaffected — only the share moves, "
                         "which is exactly why this defect was easy to miss")

    def test_humanizer_agent_says_the_draft_file_is_body_only(self):
        text = (self.ROOT / "agents" / "06.5-humanizer.md").read_text(encoding="utf-8")
        self.assertIn("phase-6.5-report.md", text,
                      "the report needs its own path or it lands in the measured file")
        low = text.lower()
        self.assertTrue("body only" in low or "article body and nothing else" in low,
                        "the agent must state that the humanized draft is body-only")

    def test_pipeline_contract_declares_the_separate_report_artifact(self):
        text = (self.ROOT / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("phase-6.5-report.md", text,
                      "Pipeline Contract must declare the report artifact so the "
                      "orchestrator saves it somewhere other than the draft")
