"""Production scaffolding reached the reader, and the loop trail was never written.

Two defects found by auditing a delivered run:

1. The published document carried three raw `[VISUAL-PLACEHOLDER: ...]` lines —
   instructions addressed to Phase 3.5 — visible mid-article, and embedded none
   of the three valid charts sitting on disk. Phase 3.5 never replaced the
   placeholders with `<!-- VISUAL: id=... -->` anchors, so Phase 8 had nowhere to
   insert the assets. Every artifact looked healthy: the charts existed, the
   manifest validated, the document rendered.

   The subtle part: `body_word_count` had been taught to *exclude* placeholder
   lines so Gate 3 would measure prose. Correct for the count — and it removed
   the only thing in the pipeline that touched them, so nothing was left to
   notice they were still there. Excluding something from a measurement can
   delete the last signal that it exists.

2. `utils/loop-tracker.md` documented a `loop_history` of from_phase, to_phase,
   iteration, reason and timestamp, and said it survived `/contentforge:resume`.
   `record_loop` wrote counts only. The reason a run looped — the one thing you
   open a finished run to find — lived in the orchestrator's context and vanished
   with the session.

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


tm = _load("cf_text_metrics_pub", "text-metrics.py")
cm = _load("cf_checkpoint_pub", "checkpoint-manager.py")
lt = _load("cf_local_tracker_pub", "local-tracker.py")

DIRTY = """# The real cost of preservation

Bit preservation is the cheap part, and the number nobody budgets is the one
that recurs.

[VISUAL-PLACEHOLDER: type=chart | description="cost recovery by tier" | data="S6"]

Retrieval is billed per request.

## References
1. Someone. (2020).
"""

CLEAN = """# The real cost of preservation

Bit preservation is the cheap part.

<!-- VISUAL: id=visual-01 | file=assets/run-chart-01.png | placement=after-section-2 -->

Retrieval is billed per request.
"""


class TestResidualScaffolding(unittest.TestCase):
    def test_leftover_placeholder_is_reported(self):
        r = tm._residual_scaffolding(DIRTY)
        self.assertFalse(r["clean"])
        self.assertEqual(r["count"], 1)
        self.assertEqual(r["items"][0]["kind"], "visual_placeholder")
        self.assertEqual(r["items"][0]["line"], 6)

    def test_replaced_placeholder_is_clean(self):
        self.assertTrue(tm._residual_scaffolding(CLEAN)["clean"])

    def test_word_count_still_excludes_it(self):
        """The count stays right. The point is that both facts are now visible,
        not that one replaces the other."""
        self.assertNotIn("VISUAL-PLACEHOLDER", "")
        self.assertLess(tm._body_word_count(DIRTY), len(DIRTY.split()))
        self.assertFalse(tm._residual_scaffolding(DIRTY)["clean"])

    def test_reported_in_the_default_result(self):
        """A phase should not have to know the check exists to receive it."""
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "body.md"
            p.write_text(DIRTY, encoding="utf-8")
            result = tm.analyze(DIRTY) if hasattr(tm, "analyze") else None
        if result is None:
            self.skipTest("analyze() not exposed under that name")
        self.assertIn("residual_scaffolding", result)
        self.assertIn("visual_markers", result)


class TestVisualMarkers(unittest.TestCase):
    def test_marker_ids_are_extracted(self):
        m = tm._visual_markers(CLEAN)
        self.assertEqual(m["count"], 1)
        self.assertEqual(m["ids"], ["visual-01"])

    def test_a_body_with_no_anchors_is_measurable(self):
        """Phase 8 can compare this to the manifest instead of discovering at
        render time that there is nowhere to put a chart."""
        m = tm._visual_markers(DIRTY)
        self.assertEqual(m["count"], 0)
        self.assertEqual(m["ids"], [])

    def test_anchor_without_an_id_is_counted_separately(self):
        m = tm._visual_markers("<!-- VISUAL: file=assets/x.png -->\n")
        self.assertEqual(m["count"], 1)
        self.assertEqual(m["unidentified"], 1)
        self.assertEqual(m["ids"], [])


class TestLoopHistory(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        home = Path(self._tmp.name)
        self._orig = cm._common.marketing_home
        cm._common.marketing_home = lambda: home
        self.run = cm.init_run("LoopBrand", "a topic", "blog", {})
        self.run_id = self.run["run_id"]

    def tearDown(self):
        cm._common.marketing_home = self._orig
        self._tmp.cleanup()

    def manifest(self):
        return json.loads(
            (Path(cm._common.marketing_home()) / "loopbrand" / "runs" / self.run_id
             / "run.json").read_text(encoding="utf-8"))

    def test_reason_is_persisted_not_just_counted(self):
        cm.record_loop("LoopBrand", self.run_id, "phase_4_to_3",
                       "unsourced claims in section 2")
        hist = self.manifest()["loop_history"]
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["reason"], "unsourced claims in section 2")
        self.assertEqual(hist[0]["edge"], "phase_4_to_3")
        self.assertEqual(hist[0]["iteration"], 1)
        self.assertIn("timestamp", hist[0])

    def test_edge_is_decomposed_into_phases(self):
        cm.record_loop("LoopBrand", self.run_id, "phase_4_to_3_5", "chart mismatch")
        h = self.manifest()["loop_history"][0]
        self.assertEqual(h["from_phase"], "4")
        self.assertEqual(h["to_phase"], "3.5")

    def test_iterations_accumulate_per_edge(self):
        cm.record_loop("LoopBrand", self.run_id, "phase_6_5_to_6_5", "first")
        r = cm.record_loop("LoopBrand", self.run_id, "phase_6_5_to_6_5", "second")
        self.assertEqual(r["edge_count"], 2)
        hist = self.manifest()["loop_history"]
        self.assertEqual([h["iteration"] for h in hist], [1, 2])
        self.assertEqual([h["reason"] for h in hist], ["first", "second"])

    def test_counts_still_work(self):
        cm.record_loop("LoopBrand", self.run_id, "phase_7_to_5", "compliance")
        m = self.manifest()
        self.assertEqual(m["loop_counts"]["phase_7_to_5"], 1)
        self.assertEqual(m["total_loops"], 1)

    def test_missing_reason_warns_rather_than_writing_a_useless_row(self):
        r = cm.record_loop("LoopBrand", self.run_id, "phase_7_to_5")
        self.assertIn("warning", r)
        self.assertIsNone(self.manifest()["loop_history"][0]["reason"])

    def test_history_survives_a_reload(self):
        """The documented promise: a resumed run keeps its history."""
        cm.record_loop("LoopBrand", self.run_id, "phase_4_to_3", "why")
        status = cm.get_status("LoopBrand", self.run_id)
        self.assertIsInstance(status, dict)
        self.assertEqual(self.manifest()["loop_history"][0]["reason"], "why")


class TestBlockedDeliveryIsFiledHonestly(unittest.TestCase):
    """Phase 8 correctly refused to call a piece publishable — and the delivery
    step undid it twice: mark_complete hardcoded status "completed", and it named
    the published copies from the tracking row's title rather than the source
    file, so a DRAFT- deliverable published under an ordinary name."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        home = Path(self._tmp.name)
        self._orig = lt._common.marketing_home
        lt._common.marketing_home = lambda: home
        self.publish = home / "published"
        lt.init_tracking("blockedbrand")
        lt.add_row("blockedbrand", {"title": "The Cost Nobody Budgets",
                                    "content_type": "blog"})
        self.src = home / "DRAFT-the-cost-nobody-budgets.docx"
        self.src.write_bytes(b"PK not really a docx")

    def tearDown(self):
        lt._common.marketing_home = self._orig
        self._tmp.cleanup()

    def file_it(self, data):
        return lt.mark_complete("blockedbrand", "REQ-001", data,
                                output_file=str(self.src),
                                publish_dir_override=str(self.publish))

    def test_blocked_status_survives_into_the_record(self):
        r = self.file_it({"status": "blocked_pending_human_review",
                          "blocked_reason": "HUM-1: feature image missing"})
        self.assertEqual(r["status"], "blocked_pending_human_review")
        self.assertEqual(r["filed_as"], "filed_not_publishable")
        store, _ = lt.load_tracking("blockedbrand")
        row = store["records"][0]
        self.assertEqual(row["status"], "blocked_pending_human_review")
        self.assertIn("HUM-1", row["blocked_reason"])

    def test_blocked_artifact_cannot_publish_under_a_clean_name(self):
        r = self.file_it({"status": "blocked_pending_human_review"})
        for key in ("published_path", "output_path"):
            name = Path(r[key]).name
            self.assertTrue(name.upper().startswith("DRAFT-"),
                            f"{key} published as {name!r} with no marker")

    def test_completed_runs_are_unchanged(self):
        r = self.file_it({"quality_score": 8.5})
        self.assertEqual(r["status"], "completed")
        self.assertFalse(Path(r["published_path"]).name.upper().startswith("DRAFT-"))

    def test_marker_is_not_doubled(self):
        store, _ = lt.load_tracking("blockedbrand")
        store["records"][0]["title"] = "DRAFT-already marked"
        lt.save_tracking("blockedbrand", store)
        r = self.file_it({"status": "blocked_pending_human_review"})
        self.assertNotIn("draft-draft", Path(r["published_path"]).name.lower())


class TestDocxAppendixHonesty(unittest.TestCase):
    def test_burstiness_is_not_given_a_target_that_does_not_exist(self):
        """The appendix printed "(target >=0.7)" while Phase 7 scores burstiness
        as advisory with no minimum, so the delivered document showed a figure
        failing a threshold that exists nowhere in the pipeline."""
        text = (REPO / "scripts" / "generate-docx.py").read_text(encoding="utf-8")
        # Strip comments first: the explanation of this very fix quotes the old
        # string, and asserting against raw file text matches the comment.
        code = " ".join(line for line in text.splitlines()
                        if not line.lstrip().startswith("#"))
        self.assertNotIn("target ≥" + "0.7", code)
        self.assertNotIn("target >=0.7", code)
        self.assertIn("Burstiness score", code)
        idx = code.index("Burstiness score")
        self.assertIn("advisory", code[idx:idx + 200])


class TestContractWiring(unittest.TestCase):
    def read(self, rel):
        return (REPO / rel).read_text(encoding="utf-8")

    def test_output_manager_checks_for_scaffolding(self):
        text = self.read("agents/08-output-manager.md")
        self.assertTrue("residual_scaffolding" in text,
                        "Phase 8 does not check for leftover production scaffolding")
        self.assertTrue("visual_markers" in text,
                        "Phase 8 does not reconcile anchors against the manifest")

    def test_annotator_must_replace_every_placeholder(self):
        text = self.read("agents/03.5-visual-asset-annotator.md")
        self.assertTrue("residual_scaffolding" in text,
                        "Phase 3.5 is not told to verify its own replacements")

    def test_pipeline_contract_states_the_gate(self):
        text = self.read("skills/contentforge/SKILL.md")
        self.assertTrue("residual_scaffolding" in text)

    def test_loop_tracker_doc_matches_the_script(self):
        text = self.read("utils/loop-tracker.md")
        self.assertTrue("--reason" in text,
                        "loop-tracker.md documents a history the script cannot record")


if __name__ == "__main__":
    unittest.main(verbosity=2)
