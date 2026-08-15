"""Phase 4's corrections had nowhere to go, so the pipeline lost them.

Found by auditing a real completed run. Phase 4 passed while holding 8
carry-forward corrections with exact find/replace strings. One was applied.
Seven were silently dropped, and Phase 6.5 later reworded one of the flagged
sentences into a *wider* claim than the one Phase 4 objected to. Phase 7 caught
six of the seven by hand-grepping the finished article, missed the seventh, and
invented a `mandatory_before_publish` field that appears nowhere in the plugin —
so Phase 8 rendered and delivered the document with none of it resolved.

No agent misbehaved. The contract lost the corrections in three independent
places:

  1. Phase 4's only documented destination for a fix list was "FEEDBACK FOR
     PHASE 3 — when looping back". On a PASS there was no destination at all.
  2. Phase 5's input list described the validation report as one where fixes
     were "already applied" — presupposing the work.
  3. Phase 5's Critical Rule forbade changing "facts, statistics, or citations",
     which is exactly what a reference URL, a citation date and a claim-scope
     tightening are. The corrections were unappliable by contract.

These tests pin the ledger that replaces that hole, and the contract wording, so
the dead end cannot be re-introduced. Stdlib only.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "fix-ledger.py"


def item(fid, find=None, replace=None, *, blocking=True, cls="text_replace",
         severity="MINOR", status="pending", rationale="because"):
    rec = {"id": fid, "severity": severity, "blocking": blocking, "class": cls,
           "rationale": rationale, "status": status, "applied_at_phase": None,
           "applied_to": None, "note": None}
    if cls == "text_replace":
        rec["find"] = find
        rec["replace"] = replace
    return rec


class LedgerHarness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.run_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, body, items, source=None, newline="\n"):
        with open(self.run_dir / "body.md", "w", encoding="utf-8", newline="") as fh:
            fh.write(body if newline == "\n" else body.replace("\n", newline))
        if source is not None:
            (self.run_dir / "src.md").write_text(source, encoding="utf-8")
        ledger = {"schema": "contentforge.fix-ledger/1", "run_id": "t",
                  "emitted_by": "phase-4", "items": items}
        (self.run_dir / "phase-4-fixes.json").write_text(
            json.dumps(ledger, indent=2), encoding="utf-8")

    def run_cmd(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args,
                               "--run-dir", str(self.run_dir)],
                              capture_output=True, text=True, encoding="utf-8")
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.fail(f"non-JSON output (exit {proc.returncode}):\n"
                      f"{proc.stdout}\n{proc.stderr}")
        return proc.returncode, payload

    def body(self):
        with open(self.run_dir / "body.md", "r", encoding="utf-8", newline="") as fh:
            return fh.read()

    def ledger(self):
        return json.loads((self.run_dir / "phase-4-fixes.json").read_text(encoding="utf-8"))


class TestApply(LedgerHarness):
    def test_single_occurrence_applies_verbatim(self):
        self.write("It never shows up in a rate.\n",
                   [item("MIN-5", "never shows up", "does not show up")])
        code, out = self.run_cmd("apply", "--target", "body.md", "--phase", "5")
        self.assertEqual(code, 0, out)
        self.assertIn("does not show up", self.body())
        self.assertEqual(self.ledger()["items"][0]["status"], "applied")
        self.assertEqual(self.ledger()["items"][0]["applied_at_phase"], "5")

    def test_missing_target_string_is_loud_not_a_noop(self):
        """The defect: three fixes were written at Phase 4 against text that
        later phases rewrote. A script that shrugged at a missing match would
        report success having done nothing."""
        self.write("The text moved on.\n",
                   [item("MIN-2", "no study reports a similar time", "...")])
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 1, out)
        self.assertEqual(out["results"][0]["outcome"], "not_found")
        self.assertEqual(out["blocking_failures"], 1)

    def test_ambiguous_match_refuses_to_guess(self):
        self.write("cost line. cost line.\n", [item("X", "cost line", "price line")])
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["results"][0]["outcome"], "ambiguous")
        self.assertEqual(out["results"][0]["occurrences"], 2)
        self.assertIn("cost line. cost line.", self.body())

    def test_author_sentences_are_protected_by_measurement(self):
        """A correction that would rewrite or drop the author's own words is
        reverted. The guard is the authorship record, not the fix's good
        intentions."""
        self.write("that migration ate four months of one persons time.\nAI prose here.\n",
                   [item("BAD", "that migration ate four months of one persons time.",
                         "The migration took four months.")],
                   source="that migration ate four months of one persons time.\n")
        code, out = self.run_cmd("apply", "--target", "body.md",
                                 "--source-draft", "src.md")
        self.assertEqual(code, 1, out)
        self.assertEqual(out["authorship_guard"], "active")
        self.assertEqual(out["results"][0]["outcome"], "author_protected")
        self.assertIn("one persons time", self.body())

    def test_guard_state_is_reported_never_assumed(self):
        self.write("plain text\n", [item("A", "plain", "simple")])
        _, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(out["authorship_guard"], "not_applicable")

    def test_dry_run_touches_nothing(self):
        self.write("never shows up\n", [item("A", "never shows up", "does not show up")])
        before = self.body()
        code, out = self.run_cmd("apply", "--target", "body.md", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(self.body(), before)
        self.assertEqual(self.ledger()["items"][0]["status"], "pending")

    def test_line_endings_elsewhere_are_untouched(self):
        """A checkpoint sha256 recorded elsewhere in the run must survive an edit
        that only changes one phrase."""
        self.write("alpha\nnever shows up\nbeta\n",
                   [item("A", "never shows up", "does not show up")],
                   newline="\r\n")
        code, _ = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 0)
        raw = self.body()
        self.assertIn("alpha\r\n", raw)
        self.assertIn("beta\r\n", raw)
        self.assertNotIn("alpha\n\r", raw)


class TestVerify(LedgerHarness):
    def test_appending_fix_is_not_mistaken_for_regression(self):
        """MIN-6's replacement contains its own find string. A naive
        'find must be absent' rule reports a correctly applied fix as regressed."""
        self.write("About 37% falls after Year 1.\n",
                   [item("MIN-6", "About 37% falls after Year 1.",
                         "About 37% falls after Year 1 - our arithmetic.")])
        self.run_cmd("apply", "--target", "body.md")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["checks"][0]["state"], "survived")

    def test_later_phase_undoing_a_fix_is_caught(self):
        """Phase 6.5 rewrote a flagged sentence and widened the claim. Applying a
        fix is not the end of its life."""
        self.write("and under-priced by the market selling it.\n",
                   [item("MIN-4", "and under-priced by the market selling it.",
                         "and, on their own disclosure, under-priced by the service.")])
        self.run_cmd("apply", "--target", "body.md")
        with open(self.run_dir / "body.md", "w", encoding="utf-8", newline="") as fh:
            fh.write("and the vendors selling it under-price it.\n")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 3, out)
        self.assertEqual(out["regressed"], ["MIN-4"])
        self.assertEqual(out["publication_status"], "BLOCKED")

    def test_unresolved_blocking_item_blocks_publication(self):
        self.write("body\n", [item("A", "absent string", "x")])
        self.run_cmd("apply", "--target", "body.md")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["publication_status"], "BLOCKED")
        self.assertEqual(out["unresolved_blocking"], ["A"])

    def test_non_blocking_item_does_not_block(self):
        self.write("body\n", [item("A", "absent", "x", blocking=False)])
        self.run_cmd("apply", "--target", "body.md")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["publication_status"], "CLEAR")

    def test_human_item_blocks_until_marked_done(self):
        """A feature image and an unrendered chart cannot be auto-applied. They
        are still mandatory before publication."""
        self.write("body\n", [item("IMG", cls="requires_human",
                                   rationale="supply a 1200x630 feature image")])
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["checks"][0]["state"], "human_pending")

        led = self.ledger()
        led["items"][0]["status"] = "human_done"
        (self.run_dir / "phase-4-fixes.json").write_text(json.dumps(led), encoding="utf-8")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["publication_status"], "CLEAR")

    def test_deletion_is_expressible_and_verified_by_absence(self):
        """Phase 4's contract says a CRITICAL hallucination MUST be removed. A
        ledger that cannot express a deletion cannot carry its most severe class
        of correction — found by a validator agent working the real contract."""
        self.write("Keep this. Fabricated sentence here. Keep that.\n",
                   [item("CRIT", "Fabricated sentence here. ", "",
                         severity="CRITICAL")])
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertNotIn("Fabricated", self.body())
        self.assertIn("Keep this. Keep that.", self.body())

        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["checks"][0]["state"], "survived")

    def test_a_reinstated_deletion_is_caught_as_regression(self):
        self.write("Keep this. Fabricated sentence here.\n",
                   [item("CRIT", "Fabricated sentence here.", "", severity="CRITICAL")])
        self.run_cmd("apply", "--target", "body.md")
        with open(self.run_dir / "body.md", "w", encoding="utf-8", newline="") as fh:
            fh.write("Keep this. Fabricated sentence here.\n")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 3, out)
        self.assertEqual(out["regressed"], ["CRIT"])

    def test_declined_is_a_recorded_decision_not_a_silent_drop(self):
        self.write("body\n", [item("A", "absent", "x", status="declined")])
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["checks"][0]["state"], "declined")


class TestResolve(LedgerHarness):
    """A `not_found` correction still has to be made, and the documented remedy
    used to leave `replace` pointing at wording nobody wrote — so `verify`
    reported the hand-fixed item as `regressed`, and Phase 8 escalates that to a
    downstream-sabotage finding. On a real run it would have falsely accused
    five of eleven corrections."""

    def setUp(self):
        super().setUp()
        self.write("The literature prints prices without saying the share.\n",
                   [item("MIN-3", "the current literature publishes prices "
                                  "without saying the share",
                         "Published prices do not say the share.")])
        self.run_cmd("apply", "--target", "body.md")

    def hand_correct(self):
        with open(self.run_dir / "body.md", "w", encoding="utf-8", newline="") as fh:
            fh.write("Published prices do not say the share.\n")

    def test_hand_correction_verifies_instead_of_reporting_sabotage(self):
        self.hand_correct()
        code, out = self.run_cmd("resolve", "--target", "body.md", "--id", "MIN-3",
                                 "--replaced-with",
                                 "Published prices do not say the share.",
                                 "--note", "find string had drifted")
        self.assertEqual(code, 0, out)
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["regressed"], [])
        self.assertEqual(out["checks"][0]["state"], "survived")

    def test_phase_4_wording_is_preserved_not_lost(self):
        self.hand_correct()
        self.run_cmd("resolve", "--target", "body.md", "--id", "MIN-3",
                     "--replaced-with", "Published prices do not say the share.")
        led = self.ledger()["items"][0]
        self.assertIn("current literature", led["original_replace"] + led["find"])
        self.assertEqual(led["status"], "applied")

    def test_cannot_declare_a_correction_done_without_doing_it(self):
        code, out = self.run_cmd("resolve", "--target", "body.md", "--id", "MIN-3",
                                 "--replaced-with", "text nobody ever wrote")
        self.assertEqual(code, 1)
        self.assertEqual(self.ledger()["items"][0]["status"], "not_found")

    def test_zero_byte_case_is_not_called_applied(self):
        """An earlier phase had already made the correction in other words.
        Calling that 'applied' claims a substitution nobody performed."""
        code, out = self.run_cmd("resolve", "--target", "body.md", "--id", "MIN-3",
                                 "--already-satisfied",
                                 "--note", "body already carries the narrower claim")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.ledger()["items"][0]["status"], "already_satisfied")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["checks"][0]["state"], "already_satisfied")

    def test_already_satisfied_requires_an_explanation(self):
        code, _ = self.run_cmd("resolve", "--target", "body.md", "--id", "MIN-3",
                               "--already-satisfied")
        self.assertEqual(code, 2)

    def test_unknown_id_is_rejected(self):
        code, _ = self.run_cmd("resolve", "--target", "body.md", "--id", "NOPE",
                               "--replaced-with", "x")
        self.assertEqual(code, 2)


class TestEncodingSafeOutput(LedgerHarness):
    def test_out_file_is_utf8_regardless_of_console(self):
        """A reviewer copied this payload from stdout on Windows and silently got
        'Â§' for '§' and a mangled em dash, then recorded the copy as verbatim.
        The file is the safe channel."""
        note = "per §7 — the author's own wording, left alone"
        self.write("a claim in the body\n",
                   [dict(item("A", "x", "y", status="declined"), note=note)])
        out_path = self.run_dir / "verify.json"
        self.run_cmd("verify", "--target", "body.md", "--out", str(out_path))
        raw = out_path.read_bytes().decode("utf-8")   # fails outright if not UTF-8
        self.assertIn(note, raw)
        self.assertNotIn("Â§", raw)
        self.assertNotIn("â€", raw)


class TestMultiPairIds(LedgerHarness):
    def test_two_substitutions_from_one_report_item(self):
        """Phase 4's MOD-2 carried two find/replace pairs under one id, while ids
        must stay unique. `source_id` keeps the tie back to the report."""
        self.write("He is right that it holds. His 40% lands inside.\n",
                   [dict(item("MOD-2a", "He is right that it holds.", "It holds."),
                         source_id="MOD-2"),
                    dict(item("MOD-2b", "His 40% lands inside.", "That 40% lands inside."),
                         source_id="MOD-2")])
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 0, out)
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual({c["id"] for c in out["checks"]}, {"MOD-2a", "MOD-2b"})


class TestValidateProvesSomething(LedgerHarness):
    """Gate 4 cited `validate` as evidence the ledger was sound. It only checked
    JSON structure and never opened the draft, so a ledger whose every find
    string matched nothing passed with exit 0. The gate's evidence was not
    evidence."""

    def test_structure_only_run_says_it_proved_nothing(self):
        self.write("real body text\n",
                   [item("GHOST", "a string that is nowhere in the draft", "x")])
        code, out = self.run_cmd("validate")
        self.assertEqual(code, 0)
        self.assertIn("warning", out)
        self.assertIn("did NOT confirm", out["warning"])
        self.assertIsNone(out["target_checked"])

    def test_unlandable_ledger_fails_against_the_draft(self):
        self.write("real body text\n",
                   [item("GHOST", "a string that is nowhere in the draft", "x")])
        code, out = self.run_cmd("validate", "--target", "body.md")
        self.assertEqual(code, 1, out)
        self.assertEqual(out["unmatched"], ["GHOST"])
        self.assertFalse(out["ok"])

    def test_ambiguous_find_is_reported_before_apply(self):
        self.write("cost line. cost line.\n", [item("X", "cost line", "price line")])
        code, out = self.run_cmd("validate", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["ambiguous"][0]["id"], "X")

    def test_landable_ledger_passes(self):
        self.write("It never shows up in a rate.\n",
                   [item("A", "never shows up", "does not show up")])
        code, out = self.run_cmd("validate", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["find_strings_resolvable"], 1)


class TestLineEndingTolerance(LedgerHarness):
    """Artifacts are CRLF and the script reads with newline="" to stay
    byte-stable, so a find string an agent composed with LF matched nothing —
    a silent not_found for a reason unrelated to the text."""

    def test_lf_find_matches_a_crlf_body(self):
        self.write("First line here.\nSecond line follows.\nThird ends it.\n",
                   [item("LF", "Second line follows.\nThird ends it.",
                         "Second line ends it.")],
                   newline="\r\n")
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertIn("Second line ends it.", self.body())

    def test_the_files_own_line_endings_survive(self):
        self.write("First line here.\nSecond line follows.\nThird ends it.\n",
                   [item("LF", "Second line follows.\nThird ends it.",
                         "Second line ends it.")],
                   newline="\r\n")
        self.run_cmd("apply", "--target", "body.md")
        raw = self.body()
        self.assertIn("First line here.\r\n", raw)
        self.assertEqual(raw.count("\r\n"), raw.count("\n"))

    def test_a_genuinely_absent_string_still_fails(self):
        """The tolerance must not turn every miss into a match."""
        self.write("First line here.\n", [item("X", "not in the file at all", "y")],
                   newline="\r\n")
        code, out = self.run_cmd("apply", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["results"][0]["outcome"], "not_found")


class TestReworkClass(LedgerHarness):
    """A section the outline requires and the draft never wrote is a correction
    that is neither a substitution nor a person's job — an earlier phase owns it.
    Forcing it into requires_human makes the pipeline's own work look like a task
    waiting on the user."""

    def test_rework_item_blocks_and_names_its_phase(self):
        self.write("body\n",
                   [dict(item("SEC-1", cls="requires_rework",
                              rationale="outline point 1 has no section"),
                         target_phase="3")])
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 1)
        self.assertEqual(out["checks"][0]["class"], "requires_rework")
        self.assertEqual(out["checks"][0]["state"], "human_pending")

    def test_rework_without_a_target_phase_is_rejected(self):
        self.write("body\n",
                   [item("SEC-1", cls="requires_rework", rationale="missing section")])
        code, out = self.run_cmd("validate")
        self.assertEqual(code, 2)
        self.assertTrue(any("target_phase" in p for p in out["problems"]), out)


class TestSupersededOnLoop(LedgerHarness):
    """On a loop Phase 3 rewrites the draft, so every find string is expected to
    stop matching. Overwriting the ledger wholesale would make a correction Phase
    3 fixed on its own indistinguishable from one that was lost."""

    def test_superseded_items_do_not_block(self):
        self.write("rewritten body\n",
                   [item("OLD", "text from the previous draft", "x",
                         status="superseded")])
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["publication_status"], "CLEAR")

    def test_superseded_is_not_reported_as_applied(self):
        self.write("rewritten body\n",
                   [item("OLD", "gone", "x", status="superseded")])
        _, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(out["checks"][0]["state"], "superseded")


class TestSchema(LedgerHarness):
    def _validate(self, items, schema="contentforge.fix-ledger/1"):
        (self.run_dir / "body.md").write_text("x", encoding="utf-8")
        (self.run_dir / "phase-4-fixes.json").write_text(
            json.dumps({"schema": schema, "run_id": "t", "items": items}), encoding="utf-8")
        return self.run_cmd("validate")

    def test_valid_ledger_passes(self):
        code, out = self._validate([item("A", "a", "b")])
        self.assertEqual(code, 0, out)

    def test_duplicate_ids_rejected(self):
        code, out = self._validate([item("A", "a", "b"), item("A", "c", "d")])
        self.assertEqual(code, 2)
        self.assertTrue(any("duplicate" in p for p in out["problems"]), out)

    def test_fix_that_changes_nothing_rejected(self):
        code, out = self._validate([item("A", "same", "same")])
        self.assertEqual(code, 2)
        self.assertTrue(any("identical" in p for p in out["problems"]), out)

    def test_human_item_needs_an_action(self):
        code, out = self._validate([item("A", cls="requires_human", rationale="")])
        self.assertEqual(code, 2)

    def test_wrong_schema_rejected(self):
        code, _ = self._validate([item("A", "a", "b")], schema="something/else")
        self.assertEqual(code, 2)

    def test_missing_ledger_is_an_error_not_an_empty_pass(self):
        (self.run_dir / "body.md").write_text("x", encoding="utf-8")
        code, out = self.run_cmd("verify", "--target", "body.md")
        self.assertEqual(code, 2)
        self.assertIn("no fix ledger", out["error"])


class TestContractWiring(unittest.TestCase):
    """The script is only half the fix. These pin the contract that routes
    corrections into it, because the original defect was entirely in the prose."""

    def read(self, rel):
        return (REPO / rel).read_text(encoding="utf-8")

    def assertHas(self, text, needle, rel):
        # assertIn would dump the whole 40KB contract into the failure report.
        self.assertTrue(needle in text, f"{rel} does not mention {needle!r}")

    def assertLacks(self, text, needle, rel):
        self.assertTrue(needle not in text, f"{rel} still contains {needle!r}")

    def test_validator_emits_the_ledger(self):
        rel = "agents/04-scientific-validator.md"
        text = self.read(rel)
        self.assertHas(text, "phase-4-fixes.json", rel)
        self.assertHas(text, "fix-ledger.py", rel)

    def test_validator_pass_with_open_fixes_requires_the_ledger(self):
        """A PASS while holding corrections is the exact case that lost them."""
        rel = "agents/04-scientific-validator.md"
        self.assertHas(self.read(rel), "PASS while holding", rel)

    def test_structurer_applies_the_ledger(self):
        rel = "agents/05-structurer-proofreader.md"
        text = self.read(rel)
        self.assertHas(text, "fix-ledger.py", rel)
        self.assertHas(text, "apply", rel)

    def test_structurer_fact_rule_carries_the_ledger_exception(self):
        """Phase 5 was forbidden from making exactly these corrections. Without a
        stated exception the contradiction returns."""
        rel = "agents/05-structurer-proofreader.md"
        text = self.read(rel)
        self.assertHas(text, "Do NOT change facts", rel)
        idx = text.index("Do NOT change facts")
        window = text[idx:idx + 1200].lower()
        self.assertTrue("fix ledger" in window,
                        f"{rel}: the do-not-change-facts rule states no exception for "
                        f"the fix ledger within 1200 chars, so the contradiction that "
                        f"made Phase 4's corrections unappliable is back")

    def test_structurer_input_does_not_presuppose_fixes_applied(self):
        rel = "agents/05-structurer-proofreader.md"
        self.assertLacks(self.read(rel), "any minor fixes applied", rel)

    def test_humanizer_must_not_undo_applied_fixes(self):
        rel = "agents/06.5-humanizer.md"
        self.assertHas(self.read(rel), "fix-ledger.py", rel)

    def test_reviewer_consumes_the_ledger(self):
        rel = "agents/07-reviewer.md"
        text = self.read(rel)
        self.assertHas(text, "fix-ledger.py", rel)
        self.assertHas(text, "phase-4-fixes.json", rel)

    def test_output_manager_blocks_on_unresolved_fixes(self):
        rel = "agents/08-output-manager.md"
        text = self.read(rel)
        self.assertHas(text, "fix-ledger.py", rel)
        self.assertHas(text, "publication_status", rel)

    def test_reviewer_fix_ledger_shape_is_unambiguous(self):
        """Step 0 said 'copy the checks array into fix_ledger' while the schema
        showed fix_ledger as an object. Both cannot hold, and a reviewer had to
        pick one."""
        rel = "agents/07-reviewer.md"
        text = self.read(rel)
        self.assertHas(text, "fix_ledger.checks", rel)

    def test_scorecard_template_shows_publication_status(self):
        """A scorecard rendered exactly to template would have read APPROVED with
        nothing indicating the piece was unpublishable."""
        rel = "templates/quality-scorecard.md"
        text = self.read(rel)
        self.assertHas(text, "Publication status", rel)
        self.assertHas(text, "fix-ledger.py verify", rel)

    def test_reviewer_config_keys_are_addressable(self):
        """`phase_7_review` and `feedback_loop_limits` live under `default.`; the
        contract cited them as top-level, where a literal lookup returns null."""
        rel = "agents/07-reviewer.md"
        text = self.read(rel)
        self.assertHas(text, "default.quality_gates.phase_7_review", rel)
        self.assertHas(text, "default.feedback_loop_limits.max_total_loops", rel)

    def test_pipeline_contract_declares_the_artifact(self):
        rel = "skills/contentforge/SKILL.md"
        text = self.read(rel)
        self.assertHas(text, "phase-4-fixes.json", rel)
        self.assertHas(text, "fix-ledger.py", rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
