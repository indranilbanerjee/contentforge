#!/usr/bin/env python3
"""
fix-ledger.py
=============
Carries Phase 4's required corrections forward as a machine-readable ledger, so
they are applied verbatim, survive the phases that follow, and can block a
publication claim when they do not.

Why this exists
---------------
Phase 4 (Scientific Validator) produces exact find/replace corrections. Before
this script the only documented destination for them was "FEEDBACK FOR PHASE 3
(CONTENT DRAFTER) — when looping back". On a PASS decision there was no
destination at all: the corrections were written into a markdown report that no
later phase was required to act on, while Phase 5's own contract described that
report as one where fixes were already applied and forbade it from changing
"facts, statistics, or citations" — which is precisely what these corrections
are. A validator that passed while holding corrections therefore lost them, and
no gate could see it happen.

Observed in a real run: Phase 4 issued 8 carry-forward corrections, 1 was
applied, 7 were silently dropped, and one of the survivors was later reworded by
Phase 6.5 into a *wider* claim than the one Phase 4 had flagged. The reviewer
caught 6 of the 7 by hand-grepping the final article and missed the seventh,
because a prose list re-derived at the end is not a ledger carried through.

Two failure modes this file is shaped around:

1. **Stale targets.** A correction written at Phase 4 is applied against a body
   that later phases keep editing. Three of the strings above no longer matched
   the text by the time anyone tried. A missing match is therefore reported
   loudly and never treated as "nothing to do" — silence on a not-found blocking
   fix is the bug, not the base case.
2. **Regression.** Applying a fix is not the end of its life. Every phase after
   the one that applied it can undo it, so ``verify`` re-checks survival rather
   than trusting the status recorded at application time.

Author text is protected by measurement, not by care: an application that would
alter the authorship record is reverted and reported. See ``authorship.py``.

Ledger contract — ``<run-dir>/phase-4-fixes.json``::

    {
      "schema": "contentforge.fix-ledger/1",
      "run_id": "...",
      "emitted_by": "phase-4",
      "items": [
        {
          "id": "MIN-4",                  # stable, matches the Phase 4 report
          "severity": "MODERATE",         # CRITICAL | MODERATE | MINOR
          "blocking": true,               # may this be published unresolved?
          "class": "text_replace",        # text_replace | requires_human
                                          #   | requires_rework
          "source_id": "MOD-2",           # optional: the report issue this came
                                          #   from, when one issue needs two swaps
          "find": "...",                  # exact substring (text_replace only)
          "replace": "...",               # exact substring; "" deletes the found text
          "target_phase": "3",            # requires_rework only: who does the work
          "rationale": "...",
          "status": "pending",
          "applied_at_phase": null,
          "applied_to": null,
          "note": null
        }
      ]
    }

Classes: ``text_replace`` (a substitution, including deletion), ``requires_human``
(work no script can do — supply an image), ``requires_rework`` (work an earlier
phase must redo — write a missing section; neither a swap nor a person's job).

Statuses: pending, applied, already_satisfied, not_found, ambiguous,
author_protected, declined, human_pending, human_done, superseded.

Usage::

    python fix-ledger.py validate --run-dir DIR --target phase-3.5-visuals.md
    python fix-ledger.py apply    --run-dir DIR --target phase-5-structured.md \
                                  [--source-draft source-draft.md] [--phase 5]
    python fix-ledger.py resolve  --run-dir DIR --target FILE --id MIN-2 \
                                  --replaced-with "text now in the body"
    python fix-ledger.py verify   --run-dir DIR --target phase-6.5-humanized.md \
                                  [--out phase-7-fix-ledger.json]
    python fix-ledger.py status   --run-dir DIR

``validate`` without ``--target`` checks JSON structure only. That is not evidence
a correction can land: a ledger whose every ``find`` matches nothing is perfectly
well-formed. Pass ``--target``.

Exit codes:
    0  clean
    1  unresolved blocking items (or a blocking item failed to apply)
    2  usage, schema, or IO error
    3  regression — a previously applied fix is no longer present
"""

import argparse
import hashlib
import importlib.util
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

SCHEMA = "contentforge.fix-ledger/1"
LEDGER_NAME = "phase-4-fixes.json"

SEVERITIES = ("CRITICAL", "MODERATE", "MINOR")
CLASSES = ("text_replace", "requires_human", "requires_rework")
STATUSES = ("pending", "applied", "already_satisfied", "not_found", "ambiguous",
            "author_protected", "declined", "human_pending", "human_done",
            "superseded")

# Statuses that mean the correction is settled and needs nothing further.
RESOLVED = ("applied", "already_satisfied", "declined", "human_done",
            "superseded")


_OUT_FILE = None


def _out(payload, code=0):
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if _OUT_FILE:
        # Written as UTF-8 bytes so a consumer reads the file rather than
        # scraping a console. A reviewer once copied this payload out of stdout
        # on Windows and silently got "Â§" for "§" and 'â€"' for an em dash —
        # the console codepage, not the script — then asserted the copy was
        # verbatim. Nothing downstream could have caught it.
        pathlib.Path(_OUT_FILE).write_text(text + "\n", encoding="utf-8")
    sys.stdout.write(text + "\n")
    sys.exit(code)


def _fail(message, code=2):
    _out({"ok": False, "error": message}, code)


def _read(path: pathlib.Path) -> str:
    """Read without newline translation so applying a fix cannot rewrite line
    endings across the whole file. A checkpoint sha256 recorded elsewhere in the
    run must still match a file this script has only edited in one place."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def _write(path: pathlib.Path, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def match_newlines(replacement: str, matched: str) -> str:
    """Give a replacement the line-ending convention of the text it replaces.

    `locate` maps an LF-composed `find` onto a CRLF body and hands back the
    CRLF-form match — but the `replace` string comes from the same LF-composed
    ledger, so substituting it verbatim planted a bare LF in the middle of a
    CRLF file. Mixed endings are exactly the churn the byte-stability work
    exists to prevent: the next universal-newline read/write cycle rewrites the
    file and breaks any recorded sha256."""
    if "\n" not in replacement:
        return replacement
    if "\r\n" in matched:
        return replacement.replace("\r\n", "\n").replace("\n", "\r\n")
    return replacement


def contains(body: str, text: str) -> bool:
    """Substring test that tolerates line-ending differences, like `locate`.

    `verify` and `resolve` compare ledger strings against the body. Once `apply`
    writes replacements in the body's own convention, a literal `in` on the
    LF-form ledger string would report a correctly applied multi-line fix as
    `regressed` — a false accusation manufactured by an encoding detail."""
    if not text:
        return True
    if text in body:
        return True
    return text.replace("\r\n", "\n") in body.replace("\r\n", "\n")


def locate(body: str, find: str):
    """Find `find` in `body`, tolerating line-ending differences.

    Returns (count, actual_substring). Artifacts on Windows are CRLF and this
    script reads with newline="" to stay byte-stable, so a `find` string an agent
    composed with "\\n" matches nothing at all — a silent `not_found` on every
    multi-line correction, for a reason that has nothing to do with the text. The
    literal match is tried first; only if it misses do we retry with newlines
    normalised, and we return the substring as it actually appears so the
    replacement preserves the file's own line endings.
    """
    if not find:
        return 0, find
    n = body.count(find)
    if n:
        return n, find
    flat_body = body.replace("\r\n", "\n")
    flat_find = find.replace("\r\n", "\n")
    n = flat_body.count(flat_find)
    if n != 1:
        return n, find
    start = flat_body.index(flat_find)
    # Map the flat offset back onto the real text: every \r removed before the
    # match shifts the index by one.
    real_start = start
    for _ in range(body.count("\r\n")):
        if body[:real_start].replace("\r\n", "\n") == flat_body[:start]:
            break
        real_start += 1
    actual = body[real_start:real_start + len(flat_find) + flat_find.count("\n")]
    if actual.replace("\r\n", "\n") != flat_find:
        return 0, find
    return 1, actual


def _load_authorship():
    """Load the sibling authorship module, or None when it is unavailable.

    Absence degrades the guard to 'not checked' and is reported as such; it never
    silently downgrades to 'checked and fine'."""
    here = pathlib.Path(__file__).resolve().parent / "authorship.py"
    if not here.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("cf_authorship", here)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _authorship_signature(module, source_text: str, draft_text: str):
    """The part of the authorship record a fix must not disturb."""
    rec = module.classify(source_text, draft_text)
    return {
        "author_verbatim": rec["counts"].get("author_verbatim", 0),
        "rewritten": rec["violations"]["author_sentences_rewritten"],
        "dropped": rec["violations"]["author_sentences_dropped"],
    }


# ---------------------------------------------------------------- ledger io

def ledger_path(run_dir: pathlib.Path) -> pathlib.Path:
    return run_dir / LEDGER_NAME


def load_ledger(run_dir: pathlib.Path) -> dict:
    path = ledger_path(run_dir)
    if not path.is_file():
        _fail(f"no fix ledger at {path}. Phase 4 must emit {LEDGER_NAME} "
              f"whenever it carries corrections forward.")
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as exc:
        _fail(f"{LEDGER_NAME} is not valid JSON: {exc}")


def save_ledger(run_dir: pathlib.Path, ledger: dict) -> None:
    _write(ledger_path(run_dir), json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")


def validate_ledger(ledger: dict) -> list:
    """Structural problems, as a list of human-readable strings."""
    problems = []
    if ledger.get("schema") != SCHEMA:
        problems.append(f"schema must be {SCHEMA!r}, found {ledger.get('schema')!r}")
    items = ledger.get("items")
    if not isinstance(items, list):
        return problems + ["'items' must be a list"]

    seen = set()
    for idx, item in enumerate(items):
        where = f"items[{idx}]"
        if not isinstance(item, dict):
            problems.append(f"{where} is not an object")
            continue
        fid = item.get("id")
        if not fid or not isinstance(fid, str):
            problems.append(f"{where} has no string 'id'")
        elif fid in seen:
            problems.append(f"{where} duplicates id {fid!r}")
        else:
            seen.add(fid)
        # A single Phase 4 issue can carry two find/replace pairs (MOD-2 gave two
        # pronoun fixes under one id). Ids must stay unique because they address
        # one substitution each, so the pair becomes MOD-2a / MOD-2b and
        # `source_id` keeps the tie back to the report the rules require.
        if item.get("source_id") is not None and not isinstance(item["source_id"], str):
            problems.append(f"{where} 'source_id' must be a string when present")
        if item.get("severity") not in SEVERITIES:
            problems.append(f"{where} severity must be one of {SEVERITIES}")
        if not isinstance(item.get("blocking"), bool):
            problems.append(f"{where} 'blocking' must be a boolean")
        cls = item.get("class")
        if cls not in CLASSES:
            problems.append(f"{where} class must be one of {CLASSES}")
        if item.get("status") not in STATUSES:
            problems.append(f"{where} status must be one of {STATUSES}")
        if cls == "text_replace":
            if not isinstance(item.get("find"), str) or not item.get("find"):
                problems.append(f"{where} text_replace needs a non-empty 'find'")
            # An empty 'replace' is a deletion, and deletion has to be expressible:
            # Phase 4's own contract says a CRITICAL hallucination "MUST be removed",
            # and forcing every removal to be re-phrased as a rewrite would make the
            # ledger unable to carry its most severe class of correction.
            if not isinstance(item.get("replace"), str):
                problems.append(f"{where} text_replace needs a string 'replace' "
                                f"(use \"\" to delete the found text)")
            if item.get("find") == item.get("replace"):
                problems.append(f"{where} find and replace are identical — a fix that "
                                f"changes nothing cannot be verified")
        elif cls in ("requires_human", "requires_rework"):
            if not item.get("rationale"):
                problems.append(f"{where} {cls} needs a rationale describing "
                                f"the action required")
            # A missing section is a correction no substitution can make and no
            # person is expected to hand-write either -- an earlier phase owns it.
            if cls == "requires_rework" and not item.get("target_phase"):
                problems.append(f"{where} requires_rework needs a target_phase "
                                f"naming the phase that must do the work")
    return problems


# ------------------------------------------------------------------ apply

def cmd_apply(args):
    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    target = run_dir / args.target if not pathlib.Path(args.target).is_absolute() \
        else pathlib.Path(args.target)
    if not target.is_file():
        _fail(f"target not found: {target}")

    ledger = load_ledger(run_dir)
    problems = validate_ledger(ledger)
    if problems:
        _fail({"ledger_invalid": problems})

    body = _read(target)
    before_sha = _sha256(body)

    auth = _load_authorship() if args.source_draft else None
    source_text = None
    baseline = None
    guard = "not_applicable"
    if args.source_draft:
        src_path = run_dir / args.source_draft if not pathlib.Path(args.source_draft).is_absolute() \
            else pathlib.Path(args.source_draft)
        if not src_path.is_file():
            _fail(f"source draft not found: {src_path}")
        if auth is None:
            guard = "unavailable"
        else:
            source_text = _read(src_path)
            baseline = _authorship_signature(auth, source_text, body)
            guard = "active"

    results = []
    blocking_failures = 0

    for item in ledger["items"]:
        fid = item["id"]
        if item.get("status") in RESOLVED:
            results.append({"id": fid, "outcome": item["status"], "changed": False,
                            "note": "already resolved"})
            continue
        if item["class"] in ("requires_human", "requires_rework"):
            if item.get("status") == "pending":
                item["status"] = "human_pending"
            results.append({"id": fid, "outcome": item["status"], "changed": False,
                            "note": "needs a person; no automatic action"})
            if item["blocking"]:
                blocking_failures += 1
            continue

        find, replace = item["find"], item["replace"]
        occurrences, find = locate(body, find)

        if occurrences == 0:
            # Loud on purpose. A correction whose target has moved is the failure
            # this file exists to surface, not a no-op to pass over.
            item["status"] = "not_found"
            item["note"] = ("find string absent from the target — the text moved "
                            "after this fix was written; re-derive it against the "
                            "current body")
            results.append({"id": fid, "outcome": "not_found", "changed": False,
                            "note": item["note"]})
            if item["blocking"]:
                blocking_failures += 1
            continue

        if occurrences > 1:
            item["status"] = "ambiguous"
            item["note"] = (f"find string occurs {occurrences} times — refusing to "
                            f"guess which one; lengthen the string until unique")
            results.append({"id": fid, "outcome": "ambiguous", "changed": False,
                            "occurrences": occurrences, "note": item["note"]})
            if item["blocking"]:
                blocking_failures += 1
            continue

        candidate = body.replace(find, match_newlines(replace, find), 1)

        if guard == "active":
            after = _authorship_signature(auth, source_text, candidate)
            if (after["rewritten"] > baseline["rewritten"]
                    or after["dropped"] > baseline["dropped"]
                    or after["author_verbatim"] < baseline["author_verbatim"]):
                item["status"] = "author_protected"
                item["note"] = ("applying this fix would alter the author's own "
                                f"sentences (authorship record moved from {baseline} "
                                f"to {after}) — reverted")
                results.append({"id": fid, "outcome": "author_protected",
                                "changed": False, "note": item["note"]})
                if item["blocking"]:
                    blocking_failures += 1
                continue
            baseline = after

        body = candidate
        item["status"] = "applied"
        item["applied_at_phase"] = args.phase
        item["applied_to"] = target.name
        item["note"] = None
        results.append({"id": fid, "outcome": "applied", "changed": True})

    changed = _sha256(body) != before_sha
    if changed and not args.dry_run:
        _write(target, body)
    if not args.dry_run:
        save_ledger(run_dir, ledger)

    payload = {
        "ok": blocking_failures == 0,
        "command": "apply",
        "target": target.name,
        "dry_run": bool(args.dry_run),
        "authorship_guard": guard,
        "file_changed": changed,
        "sha256_before": before_sha,
        "sha256_after": _sha256(body),
        "applied": sum(1 for r in results if r["outcome"] == "applied"),
        "blocking_failures": blocking_failures,
        "results": results,
    }
    if guard == "unavailable":
        payload["warning"] = ("authorship.py could not be loaded — author sentences "
                              "were NOT protected during this apply")
    _out(payload, 0 if blocking_failures == 0 else 1)


# ---------------------------------------------------------------- resolve

def cmd_resolve(args):
    """Close an item the applier could not, without hand-editing the ledger.

    When a fix reports `not_found` the correction still has to be made — the
    text moved, the correction did not stop being required. Doing that by hand
    used to mean editing the JSON, and the documented remedy ("set status to
    applied with a note recording the string you actually replaced") left
    `replace` pointing at wording that is not in the body. `verify` then reports
    the item as `regressed`, which Phase 8 escalates to a downstream-sabotage
    finding. On one real run that would have falsely accused five of eleven
    corrections. The remedy has to update what `verify` actually checks.
    """
    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    target = run_dir / args.target if not pathlib.Path(args.target).is_absolute() \
        else pathlib.Path(args.target)
    if not target.is_file():
        _fail(f"target not found: {target}")

    ledger = load_ledger(run_dir)
    item = next((i for i in ledger["items"] if i.get("id") == args.id), None)
    if item is None:
        _fail(f"no ledger item with id {args.id!r}; ids: "
              f"{[i.get('id') for i in ledger['items']]}")

    body = _read(target)

    if args.already_satisfied:
        # Zero bytes change: an earlier phase had already made the correction in
        # different words. Recording that as "applied" would claim a
        # substitution this script never performed.
        if not args.note:
            _fail("--already-satisfied requires --note explaining what the body "
                  "already says instead")
        item["status"] = "already_satisfied"
        item["note"] = args.note
        item["applied_at_phase"] = args.phase
        item["applied_to"] = target.name
        save_ledger(run_dir, ledger)
        _out({"ok": True, "command": "resolve", "id": args.id,
              "outcome": "already_satisfied", "note": args.note}, 0)

    if not args.replaced_with:
        _fail("resolve needs either --replaced-with '<text now in the body>' or "
              "--already-satisfied --note '<why no change was needed>'")

    if not contains(body, args.replaced_with):
        # Refusing here is the point: without it, resolve becomes a way to
        # declare a correction done without doing it.
        _fail({"id": args.id,
               "error": "the text you say you wrote is not in the target",
               "target": target.name,
               "searched_for": args.replaced_with[:160]}, 1)

    item["original_replace"] = item.get("original_replace") or item.get("replace")
    item["replace"] = args.replaced_with
    item["status"] = "applied"
    item["applied_at_phase"] = args.phase
    item["applied_to"] = target.name
    item["note"] = args.note or ("hand-corrected: the Phase 4 find string no longer "
                                 "matched the body")
    save_ledger(run_dir, ledger)
    _out({"ok": True, "command": "resolve", "id": args.id, "outcome": "applied",
          "replace_now_verifies_against": args.replaced_with[:160],
          "original_replace_preserved": item["original_replace"][:160]}, 0)


# ----------------------------------------------------------------- verify

def cmd_verify(args):
    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    target = run_dir / args.target if not pathlib.Path(args.target).is_absolute() \
        else pathlib.Path(args.target)
    if not target.is_file():
        _fail(f"target not found: {target}")

    ledger = load_ledger(run_dir)
    problems = validate_ledger(ledger)
    if problems:
        _fail({"ledger_invalid": problems})

    body = _read(target)
    checks, unresolved, regressed = [], [], []

    for item in ledger["items"]:
        fid, status, blocking = item["id"], item.get("status"), item["blocking"]

        if item["class"] in ("requires_human", "requires_rework"):
            state = "resolved" if status == "human_done" else "human_pending"
            if state == "human_pending" and blocking:
                unresolved.append(fid)
            checks.append({"id": fid, "class": item["class"], "state": state,
                           "blocking": blocking, "action": item.get("rationale")})
            continue

        if status == "already_satisfied":
            checks.append({"id": fid, "class": "text_replace",
                           "state": "already_satisfied", "blocking": blocking,
                           "detail": item.get("note")})
            continue

        if status == "applied":
            # A deletion (replace == "") is verified by absence: "" is trivially
            # present in any text, so survival for those rests entirely on the
            # staleness test below.
            present = contains(body, item["replace"])
            # An appending fix keeps its own find string as a prefix, so a
            # surviving 'find' only proves regression when it is not part of the
            # replacement text.
            stale = contains(body, item["find"]) and not contains(item["replace"], item["find"])
            if present and not stale:
                state = "survived"
            else:
                state = "regressed"
                regressed.append(fid)
            checks.append({"id": fid, "class": "text_replace", "state": state,
                           "blocking": blocking,
                           "detail": None if state == "survived" else
                           ("replacement text is gone — a later phase rewrote it"
                            if not present else
                            "the original wording is back alongside the fix")})
            continue

        if status in ("declined", "superseded"):
            # `superseded` is the loop case: Phase 3 rewrote the draft, so this
            # correction's find string is expected to stop matching. Keeping the
            # row rather than deleting it is what makes "Phase 3 fixed this
            # itself" distinguishable from "this was lost".
            checks.append({"id": fid, "class": "text_replace", "state": status,
                           "blocking": blocking, "detail": item.get("note")})
            continue

        state = status or "pending"
        if blocking:
            unresolved.append(fid)
        checks.append({"id": fid, "class": "text_replace", "state": state,
                       "blocking": blocking, "detail": item.get("note")})

    if regressed:
        code = 3
    elif unresolved:
        code = 1
    else:
        code = 0

    _out({
        "ok": code == 0,
        "command": "verify",
        "target": target.name,
        "total": len(ledger["items"]),
        "survived": sum(1 for c in checks if c["state"] == "survived"),
        "unresolved_blocking": unresolved,
        "regressed": regressed,
        "publication_status": "CLEAR" if code == 0 else "BLOCKED",
        "checks": checks,
    }, code)


# ----------------------------------------------------------- status / validate

def cmd_status(args):
    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    ledger = load_ledger(run_dir)
    counts = {}
    blocking_open = []
    for item in ledger["items"]:
        counts[item.get("status")] = counts.get(item.get("status"), 0) + 1
        if item["blocking"] and item.get("status") not in RESOLVED:
            blocking_open.append(item["id"])
    _out({
        "ok": not blocking_open,
        "command": "status",
        "run_id": ledger.get("run_id"),
        "total": len(ledger["items"]),
        "by_status": counts,
        "blocking_open": blocking_open,
        "publication_status": "BLOCKED" if blocking_open else "CLEAR",
    }, 0 if not blocking_open else 1)


def cmd_validate(args):
    """Structure, and — when given a target — whether the corrections can land.

    Gate 4 cites this command as evidence that a ledger is sound. Structure alone
    is not that evidence: a ledger whose every `find` string matches nothing in
    the draft is perfectly well-formed and exits 0. Passing `--target` is what
    turns the check into the thing the gate is claiming, so the gate now requires
    it.
    """
    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    ledger = load_ledger(run_dir)
    problems = validate_ledger(ledger)

    payload = {"ok": not problems, "command": "validate", "problems": problems,
               "target_checked": None}
    if problems:
        _out(payload, 2)

    if not args.target:
        payload["warning"] = ("no --target given, so this checked JSON structure "
                              "only and did NOT confirm any correction can be "
                              "applied. Gate 4 requires --target.")
        _out(payload, 0)

    target = run_dir / args.target if not pathlib.Path(args.target).is_absolute() \
        else pathlib.Path(args.target)
    if not target.is_file():
        _fail(f"target not found: {target}")

    body = _read(target)
    unmatched, ambiguous, ok = [], [], 0
    for item in ledger["items"]:
        if item["class"] != "text_replace" or item.get("status") in RESOLVED:
            continue
        count, _actual = locate(body, item["find"])
        if count == 0:
            unmatched.append(item["id"])
        elif count > 1:
            ambiguous.append({"id": item["id"], "occurrences": count})
        else:
            ok += 1

    payload["target_checked"] = target.name
    payload["find_strings_resolvable"] = ok
    payload["unmatched"] = unmatched
    payload["ambiguous"] = ambiguous
    payload["ok"] = not unmatched and not ambiguous
    _out(payload, 0 if payload["ok"] else 1)


def main():
    parser = argparse.ArgumentParser(
        description="Carry Phase 4 corrections forward, apply them verbatim, and "
                    "prove they survived to publication.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--target", default=None,
                   help="draft the corrections apply to. Without it this checks "
                        "JSON structure only and proves nothing about whether any "
                        "correction can land — Gate 4 requires it")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("status")
    p.add_argument("--run-dir", required=True)
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("apply")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--target", required=True,
                   help="body file the corrections apply to, relative to run-dir")
    p.add_argument("--source-draft", default=None,
                   help="author's source draft; enables the authorship guard")
    p.add_argument("--phase", default=None, help="phase label recorded on each fix")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_apply)

    p = sub.add_parser("verify")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--out", default=None,
                   help="also write the payload here as UTF-8; read this file "
                        "rather than copying the console output")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("resolve",
                       help="close an item the applier could not, without hand-editing JSON")
    p.add_argument("--run-dir", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--replaced-with", default=None,
                   help="the text now in the body; verified before the status moves")
    p.add_argument("--already-satisfied", action="store_true",
                   help="an earlier phase already made this correction in other words")
    p.add_argument("--note", default=None)
    p.add_argument("--phase", default=None)
    p.set_defaults(func=cmd_resolve)

    args = parser.parse_args()
    global _OUT_FILE
    _OUT_FILE = getattr(args, "out", None)
    args.func(args)


if __name__ == "__main__":
    main()
