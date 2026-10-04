"""The run auditor, and the finalize gate that makes it the price of "completed".

The 47-check instrument that found most of the August 2026 campaign's defects
lived in a session scratchpad; customers ran the pipeline without the thing
that catches what the pipeline misses. `run-audit.py` productizes it, and
`finalize --status completed` now refuses without a fresh CLEAN verdict.

Every plant here reproduces a failure class observed on a real run at least
once. A guard that has never been watched failing proves nothing. Stdlib only.
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

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / "scripts" / "run-audit.py"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cm = _load("cf_cm_runaudit", "checkpoint-manager.py")

BODY = """# ignored title

The recurring line is the one nobody budgets, and the number that proves it is
already in every invoice a director signs. This piece walks the three published
breakdowns and what they leave out of the per-terabyte rate.

<!-- VISUAL: id=visual-01 | file=assets/x-chart-01.png | placement=after-paragraph-1 -->

Retrieval is billed per request and per gigabyte, and the recurring line keeps
recurring whether or not it made the plan. Ask what a full restore costs.
"""


class RunFixture(unittest.TestCase):
    """A synthetic run that passes cleanly — each test then breaks one thing."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        home = Path(self._tmp.name)
        self._orig = cm._common.marketing_home
        cm._common.marketing_home = lambda: home
        self.home = home
        self.run = cm.init_run("AuditBrand", "audit fixture topic", "blog",
                               {"word_count": 65})
        self.run_id = self.run["run_id"]
        self.run_dir = home / "auditbrand" / "runs" / self.run_id
        self._populate()

    def tearDown(self):
        cm._common.marketing_home = self._orig
        self._tmp.cleanup()

    def _save(self, phase, content, ext):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="",
                                         suffix=f".{ext}", delete=False) as fh:
            fh.write(content)
            tmp = fh.name
        cm.save_phase("AuditBrand", self.run_id, phase, Path(tmp).read_text(
            encoding="utf-8"), ext)
        os.unlink(tmp)

    def _populate(self):
        for ph, ext, content in [
            ("0.5", "txt", "A Title"),
            ("1", "md", "# research"), ("2", "md", "# factcheck"),
            ("3", "md", "# draft"), ("3.5", "md", "# visuals"),
            ("4", "md", "# validation"), ("5", "md", "# structured"),
            ("6", "md", "# seo"), ("6.5", "md", BODY),
        ]:
            self._save(ph, content, ext)
        asset = self.home / "auditbrand" / "assets" / "x-chart-01.png"
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
        self._save("3.5", json.dumps({"visuals": [
            {"id": "visual-01", "type": "chart", "status": "generated",
             "file_path": str(asset), "approved_by_user": False}]}), "json")
        self._save("7", json.dumps({
            "overall_score": 8.1, "decision": "APPROVED",
            "publication_status": "CLEAR",
            "fix_ledger": {"unresolved_blocking": [], "regressed": [],
                           "checks": []}}), "json")
        self._save("8", json.dumps({"status": "success",
                                    "publication_status": "CLEAR"}), "json")

    def audit(self, *extra):
        proc = subprocess.run(
            [sys.executable, str(AUDIT), "--run-dir", str(self.run_dir), *extra],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        return proc.returncode, json.loads(proc.stdout)

    def manifest(self):
        return json.loads((self.run_dir / "run.json").read_text(encoding="utf-8"))

    def write_manifest(self, m):
        (self.run_dir / "run.json").write_text(json.dumps(m), encoding="utf-8")

    def save_review(self, **fields):
        """Replace the fixture's phase-7 review with a variant of it."""
        review = {"overall_score": 8.1, "decision": "APPROVED",
                  "publication_status": "CLEAR",
                  "fix_ledger": {"unresolved_blocking": [], "regressed": [],
                                 "checks": []}}
        review.update(fields)
        self._save("7", json.dumps(review), "json")

    def write_profile(self, industry):
        path = self.home / "auditbrand" / "Brand-Guidelines" / "AuditBrand-brand-profile.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"brand_name": "AuditBrand", "industry": industry}),
                        encoding="utf-8")

    def set_loops(self, counts):
        m = self.manifest()
        m["loop_counts"] = dict(counts)
        m["total_loops"] = sum(counts.values())
        self.write_manifest(m)

    @staticmethod
    def row(out, name_part):
        rows = [c for c in out["checks"] if name_part in c["name"]]
        assert rows, f"no audit row mentions {name_part!r}: {[c['name'] for c in out['checks']]}"
        return rows[0]

    @staticmethod
    def fail_names(out):
        return [c["name"] for c in out["checks"] if c["result"] == "FAIL"]


class TestCleanRun(RunFixture):
    def test_clean_run_is_clean(self):
        code, out = self.audit()
        fails = [c for c in out["checks"] if c["result"] == "FAIL"]
        self.assertEqual(code, 0, fails)
        self.assertEqual(out["verdict"], "CLEAN")

    def test_result_is_written_into_the_run(self):
        self.audit()
        rec = json.loads((self.run_dir / "run-audit.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(rec["verdict"], "CLEAN")

    def test_na_is_reported_not_silently_passed(self):
        """This fixture has no source draft and no fix ledger — those checks
        must appear as N/A rows, not vanish."""
        _, out = self.audit()
        na = {c["name"] for c in out["checks"] if c["result"] == "N/A"}
        self.assertTrue(any("authorship" in n for n in na), na)
        self.assertTrue(any("ledger" in n for n in na), na)

    def test_strict_mode_fails_on_na(self):
        code, out = self.audit("--strict")
        self.assertEqual(code, 1)
        self.assertEqual(out["verdict"], "VIOLATIONS")


class TestPlants(RunFixture):
    """Each plant is a failure class observed on a real run."""

    def test_completed_phase_with_missing_artifact(self):
        (self.run_dir / "phase-4-validation.md").unlink()
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("missing artifacts", str(out["checks"]))

    def test_scaffolding_in_the_delivered_body(self):
        body = (self.run_dir / "phase-6.5-humanized.md")
        with open(body, "a", encoding="utf-8", newline="") as fh:
            fh.write('\n[VISUAL-PLACEHOLDER: type=chart | description="x"]\n')
        code, out = self.audit()
        self.assertEqual(code, 1)
        fails = [c["name"] for c in out["checks"] if c["result"] == "FAIL"]
        self.assertTrue(any("scaffolding" in n for n in fails), fails)

    def test_generated_asset_with_no_anchor(self):
        body = self.run_dir / "phase-6.5-humanized.md"
        text = body.read_text(encoding="utf-8").replace(
            "<!-- VISUAL: id=visual-01 | file=assets/x-chart-01.png | placement=after-paragraph-1 -->", "")
        with open(body, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("visual-01", str(out["checks"]))

    def test_manifest_path_pointing_at_a_missing_file(self):
        (self.home / "auditbrand" / "assets" / "x-chart-01.png").unlink()
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("ghost", str(out["checks"]))

    def test_approved_decision_with_failing_score(self):
        self._save("7", json.dumps({"overall_score": 5.9,
                                    "decision": "APPROVED"}), "json")
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("backed by its own score", str(out["checks"]))

    def test_completed_status_hiding_a_blocked_publication(self):
        (self.run_dir / "phase-4-fixes.json").write_text(json.dumps({
            "schema": "contentforge.fix-ledger/1", "run_id": self.run_id,
            "emitted_by": "phase-4", "items": [{
                "id": "HUM-1", "severity": "MODERATE", "blocking": True,
                "class": "requires_human", "rationale": "supply feature image",
                "status": "human_pending", "applied_at_phase": None,
                "applied_to": None, "note": None}]}), encoding="utf-8")
        m = self.manifest()
        m["status"] = "completed"
        self.write_manifest(m)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("not hiding a blocked publication", str(out["checks"]))

    def test_loop_arithmetic_drift(self):
        m = self.manifest()
        m["loop_counts"] = {"phase_5_to_5": 2}
        m["total_loops"] = 1
        self.write_manifest(m)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("sum of loop_counts", str(out["checks"]))

    def test_pre_328_run_without_loop_history_is_na_not_fail(self):
        m = self.manifest()
        m["loop_counts"] = {"phase_5_to_5": 1}
        m["total_loops"] = 1
        m.pop("loop_history", None)
        self.write_manifest(m)
        _, out = self.audit()
        rows = [c for c in out["checks"] if "loop history" in c["name"]]
        self.assertTrue(rows and rows[0]["result"] == "N/A", rows)


class TestFinalizeGate(RunFixture):
    def test_completed_without_audit_is_refused(self):
        r = cm.finalize_run("AuditBrand", self.run_id, "completed")
        self.assertIn("error", r)
        self.assertIn("no run-audit.json", r["error"])
        self.assertNotEqual(self.manifest().get("status"), "completed")

    def test_completed_with_clean_audit_passes(self):
        self.audit()
        r = cm.finalize_run("AuditBrand", self.run_id, "completed")
        self.assertEqual(r.get("status"), "completed", r)
        self.assertEqual(self.manifest().get("audit_verdict"), "CLEAN")

    def test_completed_with_violations_is_refused(self):
        (self.run_dir / "phase-4-validation.md").unlink()
        self.audit()
        r = cm.finalize_run("AuditBrand", self.run_id, "completed")
        self.assertIn("error", r)
        self.assertIn("VIOLATIONS", r["error"])

    def test_skip_audit_finalizes_but_stamps_the_skip(self):
        r = cm.finalize_run("AuditBrand", self.run_id, "completed",
                            skip_audit=True)
        self.assertEqual(r.get("status"), "completed")
        self.assertIn("warning", r)
        self.assertTrue(self.manifest().get("audit_skipped"))

    def test_blocked_needs_no_audit(self):
        r = cm.finalize_run("AuditBrand", self.run_id, "blocked")
        self.assertEqual(r.get("status"), "blocked")


ra = _load("cf_ra_policy", "run-audit.py")
CONFIG = json.loads((REPO / "config" / "scoring-thresholds.json").read_text(encoding="utf-8"))
GRAPH = json.loads((REPO / "config" / "pipeline-graph.json").read_text(encoding="utf-8"))

DIMS_8 = {"content_quality": 8.0, "citation_integrity": 8.0, "brand_compliance": 8.0,
          "seo_performance": 8.0, "readability": 8.0}
DEFAULT_WEIGHTS = {"content_quality": 30, "citation_integrity": 25, "brand_compliance": 20,
                   "seo_performance": 15, "readability": 10}
PHARMA_WEIGHTS = {"content_quality": 25, "citation_integrity": 35, "brand_compliance": 25,
                  "seo_performance": 10, "readability": 5}


class TestApproveLineFromConfig(RunFixture):
    """The approve line is resolved from config for the review's industry — the
    script no longer carries a number in its head. Every test below is a plant
    (or its passing twin) for one of the new section-E checks."""

    APPROVED_ROW = "backed by its own score"

    def test_pharma_review_at_7_4_approved_fails(self):
        self.save_review(overall_score=7.4, industry="pharma")
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn(self.APPROVED_ROW, " ".join(self.fail_names(out)))
        self.assertIn("8.0", self.row(out, self.APPROVED_ROW)["detail"])

    def test_default_industry_review_at_7_4_passes(self):
        self.save_review(overall_score=7.4, industry="technology",
                         minimum_pass_score_applied=7.0)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, self.APPROVED_ROW)["result"], "PASS")

    def test_pharma_review_at_8_4_passes_with_the_right_line_recorded(self):
        self.save_review(overall_score=8.4, industry="pharma",
                         minimum_pass_score_applied=8.0)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "approve line its industry")["result"], "PASS")

    def test_recorded_approve_line_that_disagrees_with_config_fails(self):
        self.save_review(overall_score=8.4, industry="pharma",
                         minimum_pass_score_applied=7.0)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("approve line its industry", " ".join(self.fail_names(out)))

    def test_recorded_approve_line_on_a_default_industry_must_be_the_default(self):
        self.save_review(overall_score=8.4, industry="technology",
                         minimum_pass_score_applied=8.0)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("approve line its industry", " ".join(self.fail_names(out)))

    def test_missing_applied_line_is_reported_na_never_silently_passed(self):
        code, out = self.audit()   # the fixture's legacy review records none
        self.assertEqual(self.row(out, "approve line applied")["result"], "N/A")
        self.assertEqual(self.row(out, "review industry")["result"], "N/A")

    def test_industry_name_is_normalised_like_the_config_keys(self):
        for spelling in ("Pharma", "PHARMA ", "pharma"):
            with self.subTest(spelling=spelling):
                self.save_review(overall_score=7.4, industry=spelling)
                code, out = self.audit()
                self.assertEqual(code, 1, spelling)

    def test_brand_profile_industry_binds_when_the_review_omits_it(self):
        self.write_profile("Pharma")
        self.save_review(overall_score=7.4)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn(self.APPROVED_ROW, " ".join(self.fail_names(out)))

    def test_review_cannot_record_a_laxer_industry_than_the_brand_profile(self):
        self.write_profile("Pharma")
        self.save_review(overall_score=8.4, industry="technology",
                         minimum_pass_score_applied=7.0)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("not laxer", " ".join(self.fail_names(out)))

    def test_review_matching_the_brand_profile_passes_the_cross_check(self):
        self.write_profile("Pharma")
        self.save_review(overall_score=8.4, industry="pharma",
                         minimum_pass_score_applied=8.0)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "not laxer")["result"], "PASS")

    def test_industry_without_an_override_resolves_to_the_default_line(self):
        self.save_review(overall_score=7.2, industry="an industry nobody configured",
                         minimum_pass_score_applied=7.0)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))

    # -- dimension minimums (the reviewer-edit's observable consequence) ------
    def test_pharma_dimension_minimum_override_binds(self):
        dims = dict(DIMS_8, content_quality=9.0, brand_compliance=9.0,
                    seo_performance=9.0, readability=9.0)   # citation stays 8.0 < 8.5
        self.save_review(overall_score=8.7, industry="pharma",
                         minimum_pass_score_applied=8.0, dimensions=dims)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("dimension at or above its minimum", " ".join(self.fail_names(out)))
        self.assertIn("citation_integrity", self.row(out, "dimension at or above")["detail"])

    def test_the_same_dimensions_pass_under_the_default_industry(self):
        dims = dict(DIMS_8, content_quality=9.0, brand_compliance=9.0,
                    seo_performance=9.0, readability=9.0)
        self.save_review(overall_score=8.8, industry="technology",
                         minimum_pass_score_applied=7.0, dimensions=dims)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "dimension at or above")["result"], "PASS")

    def test_approved_with_a_default_minimum_missed_fails(self):
        self.save_review(overall_score=7.6, industry="technology",
                         minimum_pass_score_applied=7.0,
                         dimensions=dict(DIMS_8, readability=5.5))
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("readability", self.row(out, "dimension at or above")["detail"])

    def test_non_numeric_dimension_is_skipped_not_failed(self):
        dims = dict(DIMS_8, brand_compliance="SKIPPED", seo_performance=None)
        self.save_review(overall_score=8.0, industry="technology", dimensions=dims,
                         minimum_pass_score_applied=7.0)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))

    # -- weights + composite (what makes "recomputed from config" true) ------
    def test_review_that_applied_default_weights_to_a_pharma_piece_fails(self):
        self.save_review(overall_score=8.0, industry="pharma",
                         minimum_pass_score_applied=8.0, dimensions=DIMS_8,
                         weights_applied=DEFAULT_WEIGHTS)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("weights match the configured", " ".join(self.fail_names(out)))

    def test_pharma_weights_recorded_correctly_pass(self):
        # citation 9.0 >= pharma's 8.5, brand 8.0 >= 8.0; composite under pharma
        # weights = 0.25*8 + 0.35*9 + 0.25*8 + 0.10*8 + 0.05*8 = 8.35
        dims = dict(DIMS_8, citation_integrity=9.0)
        self.save_review(overall_score=8.4, industry="pharma",
                         minimum_pass_score_applied=8.0, dimensions=dims,
                         weights_applied=PHARMA_WEIGHTS)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "weights match the configured")["result"], "PASS")
        self.assertEqual(self.row(out, "matches the weighted dimension scores")["result"], "PASS")

    def test_weights_recorded_as_fractions_are_understood(self):
        self.save_review(overall_score=8.0, industry="technology",
                         minimum_pass_score_applied=7.0, dimensions=DIMS_8,
                         weights_applied={k: v / 100 for k, v in DEFAULT_WEIGHTS.items()})
        code, out = self.audit()
        self.assertEqual(self.row(out, "weights match the configured")["result"], "PASS")

    def test_composite_that_does_not_follow_from_its_own_dimensions_fails(self):
        dims = {k: 6.0 for k in DIMS_8}
        self.save_review(overall_score=8.5, industry="technology",
                         minimum_pass_score_applied=7.0, dimensions=dims)
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("matches the weighted dimension scores", " ".join(self.fail_names(out)))

    def test_composite_inside_rounding_tolerance_passes(self):
        dims = {"content_quality": 8.3, "citation_integrity": 7.9, "brand_compliance": 8.1,
                "seo_performance": 7.4, "readability": 8.8}
        # the exact weighted composite, reported the way a reviewer would: one decimal
        exact = sum(dims[k] * CONFIG["default"]["dimension_weights"][k] for k in dims)
        self.save_review(overall_score=round(exact, 1), industry="technology",
                         minimum_pass_score_applied=7.0, dimensions=dims,
                         weights_applied=DEFAULT_WEIGHTS)
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "matches the weighted dimension scores")["result"], "PASS")

    def test_express_lane_review_is_not_recomputed(self):
        self.save_review(overall_score=8.5, industry="technology", lane="express",
                         dimensions={k: 6.0 for k in DIMS_8}, minimum_pass_score_applied=7.0)
        _, out = self.audit()
        self.assertEqual(self.row(out, "weights and composite")["result"], "N/A")

    # -- the resolver, in isolation ------------------------------------------
    def test_content_type_layer_applies_and_industry_layer_wins(self):
        scoring = {
            "default": {"minimum_pass_score": 7.0,
                        "dimension_weights": {"a": 0.5, "b": 0.5},
                        "quality_gates": {"phase_7_review": {"min_a": 6.0, "min_b": 7.0}}},
            "content_type_overrides": {
                "whitepaper": {"minimum_pass_score": 7.5,
                               "quality_gates": {"phase_7_review": {"min_a": 6.5}}}},
            "industry_overrides": {
                "pharma": {"minimum_pass_score": 8.0,
                           "dimension_weights": {"a": 0.2, "b": 0.8},
                           "quality_gates": {"phase_7_review": {"min_b": 8.5}}}},
        }
        base = ra.resolve_policy(scoring)
        self.assertEqual(base["minimum_pass_score"], 7.0)
        wp = ra.resolve_policy(scoring, None, "Whitepaper")
        self.assertEqual((wp["minimum_pass_score"], wp["minimums"]["min_a"]), (7.5, 6.5))
        both = ra.resolve_policy(scoring, "Pharma", "whitepaper")
        self.assertEqual(both["minimum_pass_score"], 8.0)            # industry wins
        self.assertEqual(both["minimums"], {"min_a": 6.5, "min_b": 8.5})  # layers merge
        self.assertEqual(both["weights"], {"a": 0.2, "b": 0.8})
        self.assertEqual(ra.resolve_policy(scoring, "unknown")["minimum_pass_score"], 7.0)

    def test_shipped_config_resolves_the_documented_industry_lines(self):
        got = {k: ra.resolve_policy(CONFIG, k)["minimum_pass_score"]
               for k in ("pharma", "bfsi", "healthcare", "legal", "real_estate", "technology")}
        self.assertEqual(got, {"pharma": 8.0, "bfsi": 7.5, "healthcare": 8.0, "legal": 8.0,
                               "real_estate": 7.0, "technology": 7.0})

    def test_the_auditor_no_longer_hardcodes_the_approve_line(self):
        src = AUDIT.read_text(encoding="utf-8")
        self.assertNotRegex(src, r"score >= \d", "run-audit.py carries a literal approve line again")


class TestLoopBudgets(RunFixture):
    """The audit is the only place a blown loop budget can be caught:
    checkpoint-manager records a loop and never refuses one."""

    def test_a_run_exactly_at_its_budget_passes(self):
        self.set_loops({"phase_1_to_1": 2, "phase_3_to_3": 2, "phase_5_to_5": 1})
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.assertEqual(self.row(out, "per-run budget")["result"], "PASS")

    def test_total_over_the_per_run_budget_fails(self):
        self.set_loops({"phase_1_to_1": 2, "phase_3_to_3": 2, "phase_5_to_5": 2})
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("per-run budget", " ".join(self.fail_names(out)))
        self.assertIn("6 loops", self.row(out, "per-run budget")["detail"])

    def test_one_edge_over_the_generic_edge_cap_fails(self):
        self.set_loops({"phase_3_to_3": 3})
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("phase_3_to_3: 3 loops, cap 2", self.row(out, "every loop edge")["detail"])

    def test_named_cap_smaller_than_the_generic_cap_governs(self):
        # phase_4_to_3_5 is capped at 1 by config although per_edge is 2.
        self.set_loops({"phase_4_to_3_5": 2})
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("phase_4_to_3_5: 2 loops, cap 1", self.row(out, "every loop edge")["detail"])
        self.set_loops({"phase_6_to_5": 2})
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("phase_6_to_5", self.row(out, "every loop edge")["detail"])

    def test_phase_7_cap_bounds_the_sum_of_its_edges(self):
        self.set_loops({"phase_7_to_5": 1, "phase_7_to_6": 2})   # each <= 2, sum 3 > 2
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("phase_7_to_any", self.row(out, "every loop edge")["detail"])
        self.set_loops({"phase_7_to_5": 1, "phase_7_to_6": 1})
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))

    def test_validation_loops_bound_the_sum_of_phase_4_edges(self):
        self.set_loops({"phase_4_to_3": 2})
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))
        self.set_loops({"phase_4_to_3": 2, "phase_4_to_3_5": 1})
        code, out = self.audit()
        self.assertEqual(code, 1)
        self.assertIn("max_validation_loops", self.row(out, "every loop edge")["detail"])

    def test_phase_6_5_edges_are_not_mistaken_for_phase_6_edges(self):
        self.set_loops({"phase_6_5_to_6_5": 2})   # prefix trap: 'phase_6_5_to_' != 'phase_6_to_'
        code, out = self.audit()
        self.assertEqual(code, 0, self.fail_names(out))

    def test_smaller_cap_rule_on_synthetic_config(self):
        graph = {"loop_budgets": {"per_edge": 2, "total_per_run": 5}}
        scoring = {"default": {
            "feedback_loop_limits": {"_precedence": "prose", "phase_4_to_3": 3,
                                     "phase_6_to_5": 1, "phase_7_to_any": 2,
                                     "max_total_loops": 3},
            "quality_gates": {"phase_4_validation": {"max_validation_loops": 9},
                              "phase_6_seo": {"max_seo_loops": 9}}}}
        caps = ra.loop_caps(graph, scoring)
        self.assertEqual(caps["total"], 3, "per-run: smaller of total_per_run and max_total_loops")
        # named cap LARGER than per_edge: per_edge (2) is the smaller, so it governs
        total_v, edge_v = ra.loop_violations({"phase_4_to_3": 3}, caps)
        self.assertTrue(edge_v and "cap 2" in edge_v[0], edge_v)
        # named cap SMALLER than per_edge: the named cap governs
        _, edge_v = ra.loop_violations({"phase_6_to_5": 2}, caps)
        self.assertTrue(edge_v and "cap 1" in edge_v[0], edge_v)
        self.assertFalse(ra.loop_violations({"phase_6_to_5": 1}, caps)[1])
        # '_precedence' is prose, never a cap
        self.assertNotIn("_precedence", caps["named"])

    def test_config_states_the_precedence_rule_once(self):
        note = CONFIG["default"]["feedback_loop_limits"]["_precedence"]
        self.assertIn("SMALLER cap governs", note)
        self.assertEqual(json.dumps(CONFIG).count("SMALLER cap governs"), 1)


class TestFinalizeFreshness(RunFixture):
    """`finalize --status completed` refuses when the run changed after it was
    audited. Both directions: stale refused, fresh and merely-touched allowed."""

    def finalize(self):
        return cm.finalize_run("AuditBrand", self.run_id, "completed")

    def test_audit_records_a_fingerprint_of_what_it_read(self):
        _, out = self.audit()
        fp = out["fingerprint"]
        self.assertEqual(fp["algorithm"], "sha256")
        self.assertIn("phase-6.5-humanized.md", fp["files"])
        self.assertIn("run.json", fp["files"])
        self.assertNotIn("run-audit.json", fp["files"])
        self.assertTrue(out["audited_at"].endswith("Z"))

    def test_fresh_audit_finalizes(self):
        self.audit()
        self.assertEqual(self.finalize().get("status"), "completed")

    def test_edit_after_the_audit_is_refused(self):
        self.audit()
        with open(self.run_dir / "phase-6.5-humanized.md", "a", encoding="utf-8", newline="") as fh:
            fh.write("\nOne more sentence the audit never saw.\n")
        r = self.finalize()
        self.assertIn("error", r)
        self.assertIn("changed after it was audited", r["error"])
        self.assertIn("phase-6.5-humanized.md changed", r["changed_since_audit"])
        self.assertNotEqual(self.manifest().get("status"), "completed")

    def test_artifact_added_after_the_audit_is_refused(self):
        self.audit()
        (self.run_dir / "phase-7-review-pre-remediation.json").write_text("{}", encoding="utf-8")
        r = self.finalize()
        self.assertIn("error", r)
        self.assertIn("phase-7-review-pre-remediation.json was added", r["changed_since_audit"])

    def test_artifact_removed_after_the_audit_is_refused(self):
        self.audit()
        (self.run_dir / "phase-6-seo.md").unlink()
        r = self.finalize()
        self.assertIn("error", r)
        self.assertIn("phase-6-seo.md was removed", r["changed_since_audit"])

    def test_delivered_docx_replaced_after_the_audit_is_refused(self):
        import zipfile
        docx = self.run_dir / "Piece.docx"
        with zipfile.ZipFile(docx, "w") as z:
            z.writestr("word/document.xml", "<w/>")
        self.audit()
        with zipfile.ZipFile(docx, "w") as z:
            z.writestr("word/document.xml", "<w>different</w>")
        r = self.finalize()
        self.assertIn("Piece.docx changed", r.get("changed_since_audit", []))

    def test_a_checkpoint_saved_after_the_audit_is_refused(self):
        self.audit()
        self._save("6", "# seo, reworked after the audit", "md")
        r = self.finalize()
        self.assertIn("error", r)

    def test_re_auditing_after_a_change_makes_it_finalizable_again(self):
        self.audit()
        with open(self.run_dir / "phase-6.5-humanized.md", "a", encoding="utf-8", newline="") as fh:
            fh.write("\nAnother sentence.\n")
        self.assertIn("error", self.finalize())
        self.audit()
        self.assertEqual(self.finalize().get("status"), "completed")

    def test_mtime_alone_does_not_invalidate_the_audit(self):
        """Hashes, not mtimes: a sync or copy rewrites timestamps, not bytes."""
        self.audit()
        for p in self.run_dir.iterdir():
            if p.name != "run-audit.json":
                os.utime(p, (4_000_000_000, 4_000_000_000))
        self.assertEqual(self.finalize().get("status"), "completed")

    def test_sync_bookkeeping_and_the_audit_file_are_not_part_of_the_fingerprint(self):
        self.audit()
        (self.run_dir / "_sync-pending.json").write_text('{"pending": []}', encoding="utf-8")
        self.assertEqual(self.finalize().get("status"), "completed")

    def test_an_audit_without_a_fingerprint_cannot_prove_freshness(self):
        (self.run_dir / "run-audit.json").write_text(
            json.dumps({"verdict": "CLEAN", "checks": []}), encoding="utf-8")
        r = self.finalize()
        self.assertIn("error", r)
        self.assertIn("no artifact fingerprint", r["error"])

    def test_skip_audit_and_blocked_are_unaffected(self):
        self.audit()
        with open(self.run_dir / "phase-6.5-humanized.md", "a", encoding="utf-8", newline="") as fh:
            fh.write("\nedited\n")
        self.assertEqual(cm.finalize_run("AuditBrand", self.run_id, "blocked").get("status"),
                         "blocked")
        r = cm.finalize_run("AuditBrand", self.run_id, "completed", skip_audit=True)
        self.assertEqual(r.get("status"), "completed")
        self.assertTrue(self.manifest().get("audit_skipped"))

    def test_fingerprint_drift_helper_names_every_kind_of_change(self):
        common = cm._common
        a = {"files": {"x": "1", "y": "2", "z": "3"}}
        b = {"files": {"x": "1", "y": "9", "w": "4"}}
        self.assertEqual(common.fingerprint_drift(a, b),
                         ["y changed", "w was added", "z was removed"])
        self.assertEqual(common.fingerprint_drift(a, a), [])


class TestFeatureCard(unittest.TestCase):
    def run_card(self, tmp, **kw):
        args = {"--title": "A Reasonable Title for a Card",
                "--brand-name": "Test Brand", "--primary": "#0B6E4F",
                "--secondary": "#DDA15E", "--out": str(Path(tmp) / "card.png")}
        args.update(kw)
        argv = [sys.executable, str(REPO / "scripts" / "feature_card.py")]
        for k, v in args.items():
            argv += [k, v]
        proc = subprocess.run(argv, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        try:
            return proc.returncode, json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(f"non-JSON (exit {proc.returncode}): "
                      f"{proc.stdout[:200]} {proc.stderr[:200]}")

    def test_renders_exact_og_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self.run_card(tmp)
            self.assertEqual(code, 0, out)
            self.assertEqual(out["size"], [1200, 630])
            self.assertGreater(out["bytes"], 5000)
            self.assertTrue(Path(out["file_path"]).is_file())

    def test_is_honest_about_what_it_is(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out = self.run_card(tmp)
            self.assertEqual(out["kind"], "deterministic_feature_card")
            self.assertFalse(out["ai_generated"])
            self.assertFalse(out["approved_by_user"],
                             "a feature card is the piece's public face; "
                             "approval is the user's, not the renderer's")

    def test_rejects_invented_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self.run_card(tmp, **{"--primary": "green"})
            self.assertEqual(code, 2)

    def test_rejects_unfittable_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _ = self.run_card(tmp, **{"--title": "x" * 200})
            self.assertEqual(code, 2)

    def test_deterministic_within_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, a = self.run_card(tmp, **{"--out": str(Path(tmp) / "a.png")})
            _, b = self.run_card(tmp, **{"--out": str(Path(tmp) / "b.png")})
            self.assertEqual(a["sha256"], b["sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
