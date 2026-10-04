"""The one-page HTML scorecard: `scripts/scorecard-html.py`.

A finished run's verdict is spread across a dozen files; the scorecard is the one
page a writer, an editor or a client opens. The page is only worth opening if it
cannot flatter, so these tests hold it to three promises:

  1. Every number is read from the run's own files and config -- never invented
     (the approve line and dimension minimums are RESOLVED, by the same code the
     run auditor uses, for the review's industry).
  2. A stale or missing audit is shown as such. A CLEAN verdict about an earlier
     version of the run is never presented as the current one.
  3. It is a safe local file: self-contained, every run-derived string escaped,
     light and dark, readable at phone width.

Every guard below is paired with a plant: a body the guard must reject, so a
scanner that cannot fail is caught here and not in front of a client.
Stdlib only.
"""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "scorecard-html.py"
AUDIT = REPO / "scripts" / "run-audit.py"
SCORING = json.loads((REPO / "config" / "scoring-thresholds.json").read_text(encoding="utf-8"))

REAL_RUN = (Path.home() / ".claude-marketing" / "e2e-preservation" / "runs"
            / "20260816-131632-link-rot-in-2026-why-organizational-web-")
REAL_BRAND = REAL_RUN.parent.parent


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = _load("cf_cm_scorecard_test", "checkpoint-manager.py")
tm = _load("cf_tm_scorecard_test", "text-metrics.py")
common = cm._common

RUN_ID = "20260901-101500-scorecard-fixture-topic"
BODY = (
    "# Fixture title\n\n"
    "The recurring line is the one nobody budgets, and the number that proves it is "
    "already in every invoice a director signs. This piece walks the three published "
    "breakdowns and what they leave out of the per-terabyte rate.\n\n"
    "Retrieval is billed per request and per gigabyte, and the recurring line keeps "
    "recurring whether or not it made the plan. Ask what a full restore costs before "
    "the contract is signed, not after the first quarter's invoice arrives.\n"
)
BODY_WORDS = tm._body_word_count(BODY)

DIMS = {"content_quality": 8.4, "citation_integrity": 7.9, "brand_compliance": 9.1,
        "seo_performance": 7.2, "readability": 8.6}          # composite 8.255 -> 8.3
REVIEW = {
    "run_id": RUN_ID, "lane": "full", "brand": "Fixture Brand", "industry": "saas",
    "overall_score": 8.3, "grade": "B+", "decision": "APPROVED",
    "loop_target_phase": None, "minimum_pass_score_applied": 7.0,
    "weights_applied": {"content_quality": 30, "citation_integrity": 25,
                        "brand_compliance": 20, "seo_performance": 15, "readability": 10},
    "dimensions": dict(DIMS),
    "critical_violations": {"hallucinations": 0, "prohibited_claims": 0,
                            "missing_disclaimers": 0},
    "publication_status": "CLEAR",
    "fix_ledger": {"unresolved_blocking": [], "regressed": [], "checks": []},
}
REPORT = ("### 8. AI-TELL SCAN (advisory)\n\n"
          "- **Advisory rating: LOW.** Nothing adverse.\n"
          "**Remaining-AI-signal score: 0.08** (gate 0.3)\n"
          "- **structure_scan overall: OK.**\n")


class Fixture(unittest.TestCase):
    """A synthetic finished run that the real auditor passes, then a real audit."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.run_dir = self.home / "fixturebrand" / "runs" / RUN_ID
        self.run_dir.mkdir(parents=True)
        self.build()
        self.audit()

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixture construction -------------------------------------------------
    def w(self, name, text):
        with open(self.run_dir / name, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)

    def wj(self, name, doc):
        self.w(name, json.dumps(doc, indent=2))

    def build(self, review=None, manifest=None):
        phases = {"0.5": ("phase-0.5-title.txt", "A Plain Fixture Title"),
                  "1": ("phase-1-research.md", "# research"),
                  "2": ("phase-2-factcheck.md", "# factcheck"),
                  "3": ("phase-3-draft.md", "# draft"),
                  "4": ("phase-4-validation.md", "# validation"),
                  "5": ("phase-5-structured.md", "# structured"),
                  "6": ("phase-6-seo.md", "# seo"),
                  "6.5": ("phase-6.5-humanized.md", BODY)}
        for _, (fname, text) in phases.items():
            self.w(fname, text)
        self.w("phase-6.5-report.md", REPORT)
        rv = dict(REVIEW)
        rv.update(review or {})
        self.wj("phase-7-review.json", rv)
        self.wj("phase-8-output.json", {"status": "success", "publication_status": "CLEAR"})
        arts = {k: v[0] for k, v in phases.items()}
        arts["7"] = "phase-7-review.json"
        arts["8"] = "phase-8-output.json"
        run = {"run_id": RUN_ID, "brand": "fixturebrand", "topic": "A fixture topic",
               "content_type": "blog", "meta": {"word_count": BODY_WORDS},
               "status": "completed", "completed_phases": list(arts),
               "phase_artifacts": arts, "loop_counts": {}, "total_loops": 0}
        run.update(manifest or {})
        self.wj("run.json", run)

    def audit(self):
        proc = subprocess.run([sys.executable, str(AUDIT), "--run-dir", str(self.run_dir)],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
        self.assertIn(proc.returncode, (0, 1), proc.stdout[:300] + proc.stderr[:300])
        return json.loads(proc.stdout)

    def audit_record(self):
        return json.loads((self.run_dir / "run-audit.json").read_text(encoding="utf-8"))

    def write_audit_record(self, rec):
        (self.run_dir / "run-audit.json").write_text(json.dumps(rec), encoding="utf-8")

    # -- running the script under test ----------------------------------------
    def card(self, *extra, run_dir=None, expect=0):
        rd = run_dir if run_dir is not None else self.run_dir
        proc = subprocess.run([sys.executable, str(SCRIPT), "--run-dir", str(rd), *extra],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
        self.assertEqual(proc.returncode, expect, proc.stdout[:400] + proc.stderr[:400])
        out = json.loads(proc.stdout)
        page = ""
        if expect == 0:
            page = Path(out["path"]).read_text(encoding="utf-8")
        return out, page

    @staticmethod
    def block(page, dimension):
        m = re.search(rf'data-dimension="{dimension}".*?</li>', page, re.S)
        assert m, f"no row for {dimension}"
        return m.group(0)


# ----------------------------------------------------------- scanners + plants

EXTERNAL_ATTR_RE = re.compile(
    r'''(?ix)\b(?:src|href|action|poster|data|srcset)\s*=\s*["']?\s*(?:https?:)?//''')
EXTERNAL_OTHER_RE = re.compile(
    r'''(?ix)@import | url\(\s*["']?\s*(?:https?:)?// |
         <\s*(?:script|link|iframe|object|embed|img|video|audio|source)\b''')


def external_refs(page):
    return EXTERNAL_ATTR_RE.findall(page) + EXTERNAL_OTHER_RE.findall(page)


def has_dark_tokens(page):
    """prefers-color-scheme dark block that REDEFINES the colour tokens on :root."""
    m = re.search(r"@media\s*\(\s*prefers-color-scheme\s*:\s*dark\s*\)\s*\{(.*?)\n\}", page, re.S)
    if not m:
        return False
    block = m.group(1)
    return ":root" in block and all(t in block for t in ("--bg:", "--ink:", "--surface:"))


def mobile_ready(page):
    if not re.search(r'<meta name="viewport" content="width=device-width', page):
        return False
    widths = [int(n) for n in re.findall(r"(?<![-\w])width\s*:\s*(\d+)px", page)]
    return all(w <= 400 for w in widths)


class TestScannerPlants(unittest.TestCase):
    """The scanners must be able to fail; otherwise the checks below prove nothing."""

    def test_external_scanner_fires(self):
        for bad in ('<img src="https://x.test/a.png">',
                    '<a href="//cdn.test/x">x</a>',
                    '<link rel="stylesheet" href="https://fonts.test/css">',
                    '<script src="https://x.test/a.js"></script>',
                    "<style>@import url(https://fonts.test/a.css);</style>",
                    "<style>body{background:url(https://x.test/a.png)}</style>",
                    "<script>alert(1)</script>"):
            self.assertTrue(external_refs(bad), bad)
        self.assertFalse(external_refs("<p>see https://example.test in the text</p>"))

    def test_dark_scanner_fires(self):
        self.assertFalse(has_dark_tokens(":root{--bg:#fff;--ink:#000;--surface:#fff}"))
        self.assertFalse(has_dark_tokens(
            "@media (prefers-color-scheme: dark){\n:root{--bg:#000}\n}"))   # incomplete
        self.assertTrue(has_dark_tokens(
            "@media (prefers-color-scheme: dark){\n:root{--bg:#000;--ink:#fff;--surface:#111}\n}"))

    def test_mobile_scanner_fires(self):
        self.assertFalse(mobile_ready("<style>.a{width:800px}</style>"))
        self.assertFalse(mobile_ready('<meta name="x"><style>.a{width:100%}</style>'))
        self.assertTrue(mobile_ready(
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<style>.a{max-width:46rem;width:100%}</style>"))


# ------------------------------------------------------------------ rendering

class TestRender(Fixture):
    def test_result_contract_and_default_path(self):
        out, page = self.card()
        self.assertEqual(Path(out["path"]), self.run_dir / "scorecard.html")
        self.assertEqual(out["bytes"], (self.run_dir / "scorecard.html").stat().st_size)
        self.assertEqual(out["verdict_shown"], "CLEAN")
        self.assertIs(out["stale_audit"], False)
        self.assertEqual(out["audit_state"], "fresh")
        self.assertEqual(out["decision"], "APPROVED")
        self.assertEqual(out["overall_score"], 8.3)
        self.assertTrue(page.startswith("<!doctype html>"))

    def test_out_flag_is_honored(self):
        target = self.home / "elsewhere" / "card.html"
        out, _ = self.card("--out", str(target))
        self.assertEqual(Path(out["path"]), target.resolve())
        self.assertTrue(target.is_file())
        self.assertFalse((self.run_dir / "scorecard.html").exists())

    def test_numbers_equal_the_review_json(self):
        _, page = self.card()
        review = json.loads((self.run_dir / "phase-7-review.json").read_text(encoding="utf-8"))
        self.assertIn(f'<span class="big">{review["overall_score"]:.1f}</span>', page)
        self.assertIn(f'approve line {SCORING["default"]["minimum_pass_score"]:.1f}', page)
        mins = SCORING["default"]["quality_gates"]["phase_7_review"]
        for key, score in review["dimensions"].items():
            row = self.block(page, key)
            self.assertIn(f'<span class="dim-score">{score:.1f}</span>', row, key)
            self.assertIn(f'Weight {review["weights_applied"][key]}%', row, key)
            self.assertIn(f'Minimum {mins["min_" + key]:.1f}', row, key)
            self.assertIn("Meets minimum", row, key)

    def test_below_minimum_dimension_is_marked_not_hidden(self):
        self.build(review={"dimensions": dict(DIMS, readability=5.1), "overall_score": 7.8,
                           "decision": "LOOP", "loop_target_phase": "5"})
        _, page = self.card()
        self.assertIn("Below minimum", self.block(page, "readability"))
        self.assertIn("LOOP TO PHASE 5", page)
        self.assertIn('class="card hero t-warn"', page)

    def test_approve_line_and_minimums_follow_the_industry_config(self):
        pharma = SCORING["industry_overrides"]["pharma"]
        w = {k: round(v * 100) for k, v in pharma["dimension_weights"].items()}
        self.build(review={"industry": "pharma", "minimum_pass_score_applied": 8.0,
                           "weights_applied": w, "overall_score": 8.3,
                           "dimensions": dict(DIMS)})
        out, page = self.card()
        self.assertIn(f'approve line {pharma["minimum_pass_score"]:.1f}', page)
        self.assertIn(f'Minimum {pharma["quality_gates"]["phase_7_review"]["min_citation_integrity"]:.1f}',
                      self.block(page, "citation_integrity"))
        # citation integrity 7.9 is below pharma's raised 8.5: an APPROVED decision must say so
        self.assertIn("Below minimum", self.block(page, "citation_integrity"))
        self.assertIn("APPROVED but these dimensions are below their minimum", page)
        self.assertIn("config override for pharma", page)

    def test_plant_approved_below_the_resolved_line_is_flagged(self):
        self.build(review={"industry": "pharma", "overall_score": 7.5,
                           "minimum_pass_score_applied": 8.0})
        _, page = self.card()
        self.assertIn("APPROVED but the score 7.5 is below the approve line 8.0", page)
        self.assertIn('class="card hero t-bad"', page)

    def test_reviewer_recording_a_laxer_line_is_flagged(self):
        self.build(review={"industry": "pharma", "minimum_pass_score_applied": 7.0})
        _, page = self.card()
        self.assertIn("The reviewer recorded an approve line of 7.0; config resolves 8.0", page)

    def test_express_lane_unscored_dimension_is_not_invented(self):
        dims = {k: v for k, v in DIMS.items() if k != "seo_performance"}
        dims["brand_compliance"] = "SKIPPED"
        self.build(review={"lane": "express", "dimensions": dims,
                           "weights_applied": {"content_quality": 35, "citation_integrity": 30,
                                               "brand_compliance": 23, "readability": 12}})
        _, page = self.card()
        self.assertIn("Not scored (SKIPPED)", self.block(page, "brand_compliance"))
        self.assertNotIn('data-dimension="seo_performance"', page)
        self.assertIn("express lane renormalizes", page)

    def test_word_count_is_measured_against_the_gate_band(self):
        _, page = self.card()
        self.assertIn(f"{BODY_WORDS:,}", page)
        self.assertIn("inside", page)
        self.build(manifest={"meta": {"word_count": BODY_WORDS * 3}})
        _, page = self.card()
        self.assertIn("OUTSIDE", page)

    def test_humanizer_scan_is_read_from_the_report(self):
        _, page = self.card()
        self.assertIn('<span class="k">AI-tell scan</span><span class="v">LOW</span>', page)
        self.assertIn('<span class="v">0.08</span>', page)
        self.assertIn('<span class="k">Structural tells</span><span class="v">OK</span>', page)
        self.w("phase-6.5-report.md", "Advisory rating: **HIGH**. Flagged lines follow.")
        _, page = self.card()
        self.assertIn('<span class="k">AI-tell scan</span><span class="v">HIGH</span>', page)

    def test_missing_or_unfilled_scan_is_not_recorded_never_guessed(self):
        (self.run_dir / "phase-6.5-report.md").unlink()
        _, page = self.card()
        self.assertIn('<span class="k">AI-tell scan</span><span class="v">not recorded</span>', page)
        # the agent template's unfilled line must not read as a LOW rating
        self.w("phase-6.5-report.md", "Advisory rating: LOW/MODERATE/HIGH (from text-metrics)")
        _, page = self.card()
        self.assertIn('<span class="k">AI-tell scan</span><span class="v">not recorded</span>', page)

    def test_blocked_publication_lists_the_open_corrections(self):
        self.build(review={"publication_status": "BLOCKED"})
        self.wj("phase-7-fix-ledger.json", {
            "ok": True, "total": 3, "survived": 1, "unresolved_blocking": ["REQ-9", "MAJ-2"],
            "regressed": ["MIN-4"], "publication_status": "BLOCKED", "checks": []})
        _, page = self.card()
        self.assertIn('data-publication="BLOCKED"', page)
        for fid in ("REQ-9", "MAJ-2", "MIN-4"):
            self.assertIn(fid, page)
        self.assertIn("2 unresolved blocking, 1 undone downstream", page)

    def test_review_and_phase8_disagreement_is_surfaced(self):
        self.wj("phase-8-output.json", {"status": "success", "publication_status": "BLOCKED"})
        _, page = self.card()
        self.assertIn("The review says CLEAR but Phase 8 says BLOCKED", page)

    def test_title_comes_from_phase_05_and_survives_bom_and_unicode(self):
        self.w("phase-0.5-title.txt", "﻿Café – 日本語: a title")
        _, page = self.card()
        self.assertIn("<h1>Café – 日本語: a title</h1>", page)
        self.assertNotIn("﻿", page)
        self.assertIn("Topic: A fixture topic", page)

    def test_footer_names_contentforge_and_the_run(self):
        _, page = self.card()
        foot = page.split("<footer>")[1]
        self.assertIn("Generated by ContentForge", foot)
        self.assertIn(RUN_ID, foot)
        self.assertIn("nothing here has been shared", foot)

    def test_header_carries_brand_type_industry_lane(self):
        _, page = self.card()
        for chip in ("Fixture Brand", "Blog", "saas", "full"):
            self.assertIn(f"<b>{chip}</b>", page)


# ------------------------------------------------------------ audit freshness

class TestAuditFreshness(Fixture):
    def test_fresh_clean_audit_is_shown_as_current(self):
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["stale_audit"]), ("CLEAN", False))
        self.assertIn('data-audit-state="fresh"', page)
        self.assertIn("Audit CLEAN", page)
        self.assertRegex(page, r"\d+ passed &middot; 0 failed")

    def test_missing_audit_is_said_loudly(self):
        (self.run_dir / "run-audit.json").unlink()
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["audit_state"], out["stale_audit"]),
                         ("NOT_AUDITED", "missing", True))
        self.assertIn("NOT AUDITED", page)
        self.assertNotIn("Audit CLEAN", page)
        self.assertNotIn("CLEAN", page)

    def test_plant_a_byte_change_after_the_audit_makes_it_stale(self):
        with open(self.run_dir / "phase-3-draft.md", "ab") as fh:
            fh.write(b"\nA late edit nobody audited.\n")
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["audit_state"], out["stale_audit"]),
                         ("STALE", "stale", True))
        self.assertIn("AUDIT IS STALE", page)
        self.assertIn("phase-3-draft.md changed", page)
        self.assertIn('data-verdict="STALE"', page)
        self.assertNotIn("Audit CLEAN", page)
        self.assertNotIn("CLEAN", page, "a stale CLEAN must never read as the current verdict")

    def test_a_one_byte_change_in_the_review_is_enough(self):
        text = (self.run_dir / "phase-7-review.json").read_text(encoding="utf-8")
        self.w("phase-7-review.json", text.replace("8.3", "8.4", 1))
        out, page = self.card()
        self.assertTrue(out["stale_audit"])
        self.assertIn("phase-7-review.json changed", page)

    def test_an_added_and_a_removed_artifact_are_both_stale(self):
        self.w("phase-3.5-visuals.md", "# a phase that appeared after the audit")
        out, page = self.card()
        self.assertEqual(out["audit_state"], "stale")
        self.assertIn("phase-3.5-visuals.md was added", page)
        (self.run_dir / "phase-3.5-visuals.md").unlink()
        (self.run_dir / "phase-6-seo.md").unlink()
        _, page = self.card()
        self.assertIn("phase-6-seo.md was removed", page)

    def test_touching_mtimes_without_changing_bytes_stays_fresh(self):
        p = self.run_dir / "phase-1-research.md"
        p.write_bytes(p.read_bytes())          # rewrite identical bytes, new mtime
        out, _ = self.card()
        self.assertFalse(out["stale_audit"])

    def test_audit_without_a_fingerprint_cannot_be_shown_current(self):
        rec = self.audit_record()
        rec.pop("fingerprint")
        self.write_audit_record(rec)
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["audit_state"], out["stale_audit"]),
                         ("UNVERIFIED", "unfingerprinted", True))
        self.assertIn("CANNOT BE SHOWN TO BE CURRENT", page)
        self.assertNotIn("CLEAN", page)

    def test_unreadable_audit_record(self):
        (self.run_dir / "run-audit.json").write_text("{not json", encoding="utf-8")
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["stale_audit"]), ("UNREADABLE", True))
        self.assertIn("AUDIT RECORD UNREADABLE", page)

    def test_a_fresh_violations_audit_lists_the_failing_checks(self):
        # the real auditor fails an APPROVED decision that sits below config's line
        self.build(review={"overall_score": 6.4, "dimensions": dict(DIMS, readability=6.1)})
        rec = self.audit()
        self.assertEqual(rec["verdict"], "VIOLATIONS")
        out, page = self.card()
        self.assertEqual((out["verdict_shown"], out["stale_audit"]), ("VIOLATIONS", False))
        self.assertIn("APPROVED decision is backed by its own score", page)
        self.assertIn("Audit VIOLATIONS", page)

    def test_na_checks_are_labelled_not_checked(self):
        _, page = self.card()
        self.assertIn("not applicable: not checked, not passed", page)

    def test_a_skipped_audit_is_on_the_page(self):
        self.build(manifest={"audit_skipped": True})
        self.audit()
        _, page = self.card()
        self.assertIn("finalized with the audit skipped", page)

    def test_building_the_scorecard_never_makes_the_audit_stale(self):
        before = self.audit_record()["fingerprint"]
        self.card()
        self.card()
        self.assertEqual(common.fingerprint_drift(before, common.run_artifact_fingerprint(self.run_dir)), [])
        out, _ = self.card()
        self.assertFalse(out["stale_audit"])

    def test_finalize_still_accepts_the_run_after_the_scorecard_exists(self):
        self.build(manifest={"status": "in_progress"})
        self.audit()
        self.card()
        orig = common.marketing_home
        common.marketing_home = lambda: self.home
        try:
            res = cm.finalize_run("fixturebrand", RUN_ID, "completed")
        finally:
            common.marketing_home = orig
        self.assertNotIn("error", res, res)


# ------------------------------------------------------- self-contained + safe

class TestSelfContainedAndSafe(Fixture):
    HOSTILE = '<script>alert(1)</script><img src=x onerror=alert(2)>"><a href="http://evil.test/x">'

    def test_page_has_no_external_references(self):
        _, page = self.card()
        self.assertEqual(external_refs(page), [])
        self.assertNotRegex(page, r"(?i)\b(?:src|href)\s*=")
        self.assertNotIn("<script", page.lower())

    def test_plant_hostile_run_text_is_escaped_everywhere_it_surfaces(self):
        h = self.HOSTILE
        self.w("phase-0.5-title.txt", h)
        self.build(review={"brand": h, "industry": h,
                           "fix_ledger": {"unresolved_blocking": [h], "regressed": []}},
                   manifest={"topic": h, "content_type": h})
        self.wj("phase-7-fix-ledger.json", {"total": 1, "survived": 0,
                                            "unresolved_blocking": [h], "regressed": []})
        self.w("phase-0.5-title.txt", h)
        rec = self.audit()
        # plant the hostile string into an audit check detail as well
        rec["checks"].append({"section": h, "name": h, "result": "FAIL", "detail": h})
        rec["verdict"] = "VIOLATIONS"
        self.write_audit_record(rec)
        _, page = self.card()
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script", page.lower())
        self.assertNotIn("<img", page.lower())
        self.assertEqual(external_refs(page), [])
        self.assertNotRegex(page, r"(?i)\b(?:src|href)\s*=\s*[\"']?http")
        self.assertNotIn('"><a', page)
        # the title appears in <title> and <h1>, both escaped
        self.assertGreaterEqual(page.count("&lt;script&gt;"), 3)

    def test_plant_script_in_the_title_alone(self):
        self.w("phase-0.5-title.txt", "<script>alert('x')</script>")
        _, page = self.card()
        self.assertNotIn("<script", page.lower())
        self.assertIn("&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", page)

    def test_light_and_dark_tokens_are_present(self):
        _, page = self.card()
        self.assertTrue(has_dark_tokens(page))
        self.assertIn('<meta name="color-scheme" content="light dark">', page)
        # light tokens are defined on :root outside the dark block, with an explicit body background
        self.assertRegex(page, r":root\{\s*--bg:#")
        self.assertIn("background:var(--bg)", page)

    def test_readable_at_phone_width(self):
        _, page = self.card()
        self.assertTrue(mobile_ready(page))
        self.assertIn("overflow-wrap:anywhere", page)
        self.assertNotIn("<table", page)

    def test_status_never_relies_on_colour_alone(self):
        self.build(review={"dimensions": dict(DIMS, readability=5.1), "decision": "LOOP",
                           "loop_target_phase": "5", "overall_score": 7.8})
        _, page = self.card()
        self.assertIn("Below minimum", page)
        self.assertIn("Meets minimum", page)


# --------------------------------------------------------------- unusable input

class TestUnusableInput(unittest.TestCase):
    def run_card(self, run_dir, *extra):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--run-dir", str(run_dir), *extra],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        return proc.returncode, json.loads(proc.stdout)

    def test_missing_directory_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.run_card(Path(tmp) / "nope")
        self.assertEqual(code, 2)
        self.assertIn("no run directory", out["error"])

    def test_no_run_json_exits_2_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.run_card(tmp)
            self.assertEqual(code, 2)
            self.assertIn("run.json", out["error"])
            self.assertFalse((Path(tmp) / "scorecard.html").exists())

    def test_corrupt_run_json_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "run.json").write_text("{broken", encoding="utf-8")
            code, out = self.run_card(tmp)
        self.assertEqual(code, 2)

    def test_run_without_a_review_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "run.json").write_text(json.dumps({"run_id": RUN_ID}), encoding="utf-8")
            code, out = self.run_card(tmp)
            self.assertEqual(code, 2)
            self.assertIn("phase-7-review.json", out["error"])
            self.assertFalse((Path(tmp) / "scorecard.html").exists())

    def test_corrupt_review_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "run.json").write_text(json.dumps({"run_id": RUN_ID}), encoding="utf-8")
            (Path(tmp) / "phase-7-review.json").write_text("[1, 2", encoding="utf-8")
            code, _ = self.run_card(tmp)
        self.assertEqual(code, 2)


# ---------------------------------------------------------------- wiring

class TestWiring(unittest.TestCase):
    SKILL = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")

    def test_skill_builds_the_scorecard_after_finalize(self):
        self.assertIn("scorecard-html.py", self.SKILL)
        after_finalize = self.SKILL.split("checkpoint-manager.py finalize", 1)[1]
        self.assertIn("scorecard-html.py", after_finalize)

    def test_publishing_is_an_offer_never_automatic_and_never_called_shared(self):
        seg = self.SKILL.split("scorecard-html.py", 1)[1][:1800].lower()
        self.assertIn("offer", seg)
        self.assertIn("explicit", seg)
        self.assertIn("private", seg)
        self.assertIn("never say", seg)
        self.assertIn("local path", seg)

    def test_the_always_on_description_did_not_grow_with_this_feature(self):
        desc = re.search(r'^description:\s*(.+)$', self.SKILL, re.M).group(1)
        self.assertNotIn("scorecard-html", desc)
        self.assertNotIn("HTML scorecard", desc)


# ----------------------------------------------------------------- the real run

@unittest.skipUnless((REAL_RUN / "run.json").is_file(), "the preserved real run is not on this machine")
class TestRealRun(unittest.TestCase):
    """A genuinely finished run, copied (never written into)."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        brand = Path(cls._tmp.name) / REAL_BRAND.name
        cls.run_dir = brand / "runs" / REAL_RUN.name
        shutil.copytree(REAL_RUN, cls.run_dir)
        if (REAL_BRAND / "brand-profile.json").is_file():
            shutil.copy2(REAL_BRAND / "brand-profile.json", brand / "brand-profile.json")
        cls.before = common.run_artifact_fingerprint(REAL_RUN)
        proc = subprocess.run([sys.executable, str(SCRIPT), "--run-dir", str(cls.run_dir)],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        cls.code = proc.returncode
        cls.out = json.loads(proc.stdout)
        cls.page = Path(cls.out["path"]).read_text(encoding="utf-8")
        cls.review = json.loads((cls.run_dir / "phase-7-review.json").read_text(encoding="utf-8"))
        cls.audit = json.loads((cls.run_dir / "run-audit.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_renders(self):
        self.assertEqual(self.code, 0, self.out)
        self.assertGreater(self.out["bytes"], 5000)

    def test_numbers_equal_the_real_review_json(self):
        self.assertIn(f'<span class="big">{self.review["overall_score"]:.1f}</span>', self.page)
        self.assertIn(self.review["decision"], self.page)
        for key, score in self.review["dimensions"].items():
            row = Fixture.block(self.page, key)
            self.assertIn(f'<span class="dim-score">{score:.1f}</span>', row, key)
            self.assertIn(f'Weight {self.review["weights_applied"][key]}%', row, key)

    def test_verdict_shown_matches_the_audit_when_it_is_still_fresh(self):
        drift = common.fingerprint_drift(self.audit["fingerprint"], common.run_artifact_fingerprint(self.run_dir))
        if drift:
            self.assertEqual(self.out["verdict_shown"], "STALE")
        else:
            self.assertEqual(self.out["verdict_shown"], self.audit["verdict"])
            self.assertFalse(self.out["stale_audit"])

    def test_the_page_is_self_contained(self):
        self.assertEqual(external_refs(self.page), [])
        self.assertTrue(has_dark_tokens(self.page))
        self.assertTrue(mobile_ready(self.page))

    def test_the_original_run_was_not_written_into(self):
        self.assertFalse((REAL_RUN / "scorecard.html").exists())
        self.assertEqual(common.fingerprint_drift(self.before, common.run_artifact_fingerprint(REAL_RUN)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
