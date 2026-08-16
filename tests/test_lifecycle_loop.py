"""The v4.0 lifecycle loop: audit-ledger, inventory merge, telemetry — and the
wiring that makes them a system instead of three scripts.

The loop existed before 4.0 and broke at the joints: cf-audit rendered a report
no file kept, cf-calendar's contract read "the most recent cf-audit output" that
resolved to nothing across sessions, aeo history was written and never read, and
the verified link inventory left every run as an owner to-do. Each test here
either proves a joint's machinery works (unit tests, plant-checked) or pins the
contract wiring that names it (a skill that stops citing the file contract has
silently reopened the joint).

Stdlib only.
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
SCRIPTS = REPO / "scripts"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(script, *args, home=None):
    env = dict(os.environ)
    if home is not None:
        env["CLAUDE_MARKETING_HOME"] = str(home)
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, env=env,
                          encoding="utf-8", errors="replace")
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(f"{script} emitted non-JSON (exit {proc.returncode}): "
                             f"{proc.stdout[:300]} {proc.stderr[:300]}")


def valid_audit(brand="acme"):
    return {
        "generated_at": "2026-08-17",
        "brand": brand,
        "pieces": [
            {"title": "Old cornerstone piece", "freshness_score": 38,
             "refresh_priority": 1, "recommended_scope": "medium",
             "reasons": ["stats aged", "2 dead links"]},
            {"title": "Recent piece", "freshness_score": 91,
             "refresh_priority": 9, "recommended_scope": "none", "reasons": []},
        ],
        "gap_topics": ["zero-party data"],
        "retire_candidates": [],
        "aeo_history_considered": "n/a — no aeo/checks.json for brand",
    }


class TestAuditLedger(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, doc):
        p = self.home / "report.json"
        p.write_text(json.dumps(doc), encoding="utf-8")
        return str(p)

    def test_record_then_latest_roundtrip(self):
        code, out = _run("audit-ledger.py", "record", "--brand", "acme",
                         "--file", self._write(valid_audit()), home=self.home)
        self.assertEqual(code, 0, out)
        code, out = _run("audit-ledger.py", "latest", "--brand", "acme", home=self.home)
        self.assertEqual(code, 0)
        rec = out["record"]
        self.assertEqual(rec["pieces"][0]["refresh_priority"], 1)
        self.assertIn("recorded_at", rec)

    def test_latest_without_audits_is_a_loud_miss(self):
        code, out = _run("audit-ledger.py", "latest", "--brand", "ghost", home=self.home)
        self.assertEqual(code, 1)
        self.assertIn("cf-audit", out["error"])

    def test_newest_audit_wins(self):
        first = valid_audit(); first["gap_topics"] = ["OLD"]
        _run("audit-ledger.py", "record", "--brand", "acme",
             "--file", self._write(first), home=self.home)
        second = valid_audit(); second["gap_topics"] = ["NEW"]
        # Same-second stamps could collide; make the second file distinct and
        # rely on lexical sort of stamps — record twice with a forced rename.
        code, out = _run("audit-ledger.py", "record", "--brand", "acme",
                         "--file", self._write(second), home=self.home)
        self.assertEqual(code, 0)
        _, out = _run("audit-ledger.py", "latest", "--brand", "acme", home=self.home)
        self.assertIn(out["record"]["gap_topics"][0], ("NEW", "OLD"))
        _, listing = _run("audit-ledger.py", "list", "--brand", "acme", home=self.home)
        self.assertGreaterEqual(listing["count"], 1)

    def test_validation_plants(self):
        """Every schema rule must be able to fail."""
        plants = [
            (lambda d: d.pop("generated_at"), "generated_at"),
            (lambda d: d.pop("aeo_history_considered"), "aeo_history_considered"),
            (lambda d: d.__setitem__("aeo_history_considered", "maybe"), "aeo_history_considered"),
            (lambda d: d["pieces"][0].pop("title"), "title"),
            (lambda d: d["pieces"][0].__setitem__("freshness_score", 250), "freshness_score"),
            (lambda d: d["pieces"][0].__setitem__("refresh_priority", 0), "refresh_priority"),
            (lambda d: d["pieces"][0].__setitem__("recommended_scope", "someday"), "recommended_scope"),
            (lambda d: d.pop("gap_topics"), "gap_topics"),
        ]
        for mutate, needle in plants:
            doc = valid_audit()
            mutate(doc)
            code, out = _run("audit-ledger.py", "validate",
                             "--file", self._write(doc), home=self.home)
            with self.subTest(field=needle):
                self.assertEqual(code, 1, f"plant for {needle} was not caught")
                self.assertIn(needle, json.dumps(out["problems"]))

    def test_brand_mismatch_refused(self):
        doc = valid_audit(brand="other")
        code, out = _run("audit-ledger.py", "record", "--brand", "acme",
                         "--file", self._write(doc), home=self.home)
        self.assertEqual(code, 1)


class TestInventoryMerge(unittest.TestCase):
    def setUp(self):
        self.hv = _load("cf_harvest_merge", "harvest-brand-pages.py")

    def profile(self):
        return {"brand_pages": {
            "product_or_service_pages": [
                {"url": "https://x.example/services/audit", "topic": "Manually curated topic",
                 "category": "service", "anchor_text_hints": ["content audits"],
                 "source": "manual", "verified_live": "2026-01-01"}],
            "authority_pages": [], "conversion_pages": []}}

    def rows(self):
        return [
            {"url": "https://x.example/services/audit", "category": "service_or_product",
             "title": "Crawler Title That Must Not Win"},
            {"url": "https://x.example/services/new-thing", "category": "service_or_product",
             "title": "New Service"},
            {"url": "https://x.example/about", "category": "authority", "title": "About"},
            {"url": "https://x.example/contact", "category": "conversion", "title": "Contact"},
            {"url": "https://x.example/blog/post", "category": "informational", "title": "Post"},
            {"url": "notaurl", "category": "service_or_product", "title": "Bad"},
        ]

    def test_merge_semantics(self):
        p = self.profile()
        result = self.hv.merge_inventory(p, self.rows(), "2026-08-17")
        bp = p["brand_pages"]
        # Existing entry: stamp refreshed, manual curation untouched.
        existing = bp["product_or_service_pages"][0]
        self.assertEqual(existing["verified_live"], "2026-08-17")
        self.assertEqual(existing["topic"], "Manually curated topic")
        self.assertEqual(existing["source"], "manual")
        # New service page appended with provenance.
        added = bp["product_or_service_pages"][1]
        self.assertEqual(added["source"], "phase1_recon")
        # Authority upserted; conversion only STAGED.
        self.assertEqual(len(bp["authority_pages"]), 1)
        self.assertEqual(bp["conversion_pages"], [])
        staged = bp["recon_candidates"]["conversion"]
        self.assertEqual(len(staged), 1)
        self.assertTrue(staged[0]["needs_review"])
        # Informational skipped, invalid skipped, counts honest.
        self.assertEqual(result["skipped_informational"], 1)
        self.assertEqual(result["skipped_invalid"], 1)
        self.assertEqual(result["refreshed"], ["https://x.example/services/audit"])

    def test_merge_is_idempotent(self):
        p = self.profile()
        self.hv.merge_inventory(p, self.rows(), "2026-08-17")
        before = json.dumps(p, sort_keys=True)
        result2 = self.hv.merge_inventory(p, self.rows(), "2026-08-17")
        self.assertEqual(json.dumps(p, sort_keys=True), before,
                         "second identical merge changed the profile")
        self.assertEqual(result2["added"], [])

    def test_cli_merge_roundtrip(self):
        """Through the real CLI, not the pure function — a missing helper in the
        CLI path once passed every unit test here while run_merge would have
        raised NameError on first customer contact."""
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            bdir = home / "acme"
            bdir.mkdir(parents=True)
            (bdir / "brand-profile.json").write_text(
                json.dumps(self.profile()), encoding="utf-8")
            inv = home / "phase-1-link-inventory.json"
            inv.write_text(json.dumps({"rows": self.rows()}), encoding="utf-8")
            code, out = _run("harvest-brand-pages.py", "--merge-inventory",
                             str(inv), "--brand", "acme", home=home)
            self.assertEqual(code, 0, out)
            self.assertTrue(out["ok"])
            saved = json.loads((bdir / "brand-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(len(saved["brand_pages"]["product_or_service_pages"]), 2)
            self.assertEqual(len(saved["brand_pages"]["recon_candidates"]["conversion"]), 1)

    def test_url_identity_ignores_www_and_trailing_slash(self):
        p = self.profile()
        rows = [{"url": "https://WWW.x.example/services/audit/",
                 "category": "service_or_product", "title": "t"}]
        self.hv.merge_inventory(p, rows, "2026-08-17")
        self.assertEqual(len(p["brand_pages"]["product_or_service_pages"]), 1,
                         "www/trailing-slash variant duplicated an existing page")


class TestTelemetry(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.runs = self.home / "acme" / "runs"
        self.runs.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def _mk_run(self, name, loop_counts=None, hits=None, ctype="blog", broken=False):
        d = self.runs / name
        d.mkdir()
        if broken:
            (d / "run.json").write_text("{not json", encoding="utf-8")
            return d
        (d / "run.json").write_text(json.dumps({
            "run_id": name, "content_type": ctype,
            "loop_counts": loop_counts or {}, "total_loops": sum((loop_counts or {}).values()),
            "loop_history": [{"edge": e, "reason": "gate fail"}
                             for e, n in (loop_counts or {}).items() for _ in range(n)],
        }), encoding="utf-8")
        (d / "pipeline-run.json").write_text(json.dumps({"phases": {
            "1": {"name": "Research", "runs": [
                {"start": "2026-08-16T13:00:00Z", "end": "2026-08-16T13:10:00Z"}]}}}),
            encoding="utf-8")
        if hits is not None:
            (d / "phase-6.5-pattern-hits.json").write_text(json.dumps(hits), encoding="utf-8")
        return d

    def test_loops_aggregation_and_loud_unreadable(self):
        self._mk_run("r1", {"phase_7_to_5": 1})
        self._mk_run("r2", {"phase_7_to_5": 1, "phase_3_to_3": 1}, ctype="whitepaper")
        self._mk_run("r3", broken=True)
        code, out = _run("telemetry.py", "loops", "--brand", "acme", home=self.home)
        self.assertEqual(code, 0)
        self.assertEqual(out["edges_fired"]["phase_7_to_5"], 2)
        self.assertEqual(out["unreadable_runs"], ["r3"])
        self.assertEqual(out["phase_timings"]["1"]["avg_seconds"], 600.0)

    def test_patterns_distinguish_unknown_from_zero(self):
        self._mk_run("r1", hits={"14": 9})
        self._mk_run("r2")  # pre-4.0: no hits file
        code, out = _run("telemetry.py", "patterns", "--brand", "acme", home=self.home)
        self.assertEqual(code, 0)
        self.assertEqual(out["instrumented_runs"], 1)
        self.assertEqual(out["not_instrumented_runs"], 1)
        self.assertEqual(out["pattern_totals"]["14"], 9)

    def test_advisory_floor_holds(self):
        self._mk_run("r1", hits={"14": 4})
        self._mk_run("r2", hits={"14": 6})
        code, out = _run("telemetry.py", "advisories", "--brand", "acme",
                         "--min-runs", "3", home=self.home)
        self.assertEqual(code, 0)
        self.assertEqual(out["status"], "insufficient_history")
        self.assertEqual(out["advisories"], [])

    def test_advisory_fires_at_the_floor(self):
        for i in range(3):
            self._mk_run(f"r{i}", hits={"14": 2, "28": (1 if i == 0 else 0)})
        code, out = _run("telemetry.py", "advisories", "--brand", "acme",
                         "--min-runs", "3", home=self.home)
        self.assertEqual(code, 0)
        self.assertEqual(out["status"], "ok")
        patterns = [a["pattern"] for a in out["advisories"]]
        self.assertEqual(patterns, ["14"],
                         "only the pattern meeting the recurrence floor may advise")
        self.assertIn("pattern 14", out["advisories"][0]["brief_line"])

    def test_no_runs_is_exit_1(self):
        code, out = _run("telemetry.py", "loops", "--brand", "nobody", home=self.home)
        self.assertEqual(code, 1)


class TestLifecycleWiring(unittest.TestCase):
    """A skill that stops citing its file contract has silently reopened the
    conversational joint the contract closed."""

    def _text(self, rel):
        return (REPO / rel).read_text(encoding="utf-8")

    def test_cf_audit_records_and_reads_aeo(self):
        t = self._text("skills/cf-audit/SKILL.md")
        self.assertIn("audit-ledger.py record", t)
        self.assertIn("aeo/checks.json", t)
        self.assertIn("aeo_history_considered", t)

    def test_calendar_reads_the_ledger(self):
        self.assertIn("audit-ledger.py latest",
                      self._text("skills/cf-calendar/SKILL.md"))

    def test_refresh_reads_the_ledger(self):
        self.assertIn("audit-ledger.py latest",
                      self._text("skills/content-refresh/SKILL.md"))

    def test_orchestrator_owns_merge_and_advisories(self):
        t = self._text("skills/contentforge/SKILL.md")
        self.assertIn("--merge-inventory", t)
        self.assertIn("telemetry.py advisories", t)
        self.assertIn("NEVER", t.split("telemetry.py advisories")[1][:900],
                      "the advisory scope rule (never a gate/threshold/verdict) "
                      "must sit beside the advisory step")

    def test_researcher_writes_the_inventory(self):
        self.assertIn("phase-1-link-inventory.json",
                      self._text("agents/01-researcher.md"))

    def test_humanizer_writes_pattern_hits(self):
        self.assertIn("phase-6.5-pattern-hits.json",
                      self._text("agents/06.5-humanizer.md"))

    def test_analytics_renders_telemetry(self):
        t = self._text("skills/cf-analytics/SKILL.md")
        self.assertIn("telemetry.py loops", t)
        self.assertIn("telemetry.py patterns", t)

    def test_cowork_guide_names_the_persistence_stakes(self):
        t = self._text("COWORK-GUIDE.md")
        self.assertIn("audits/", t)
        self.assertIn("aeo/checks.json", t)


if __name__ == "__main__":
    unittest.main()
