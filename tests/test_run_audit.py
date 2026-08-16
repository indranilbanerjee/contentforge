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
