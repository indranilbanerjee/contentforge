#!/usr/bin/env python3
"""
run-audit.py
============
Re-derives every claim a finished run makes from the artifacts on disk, using
the plugin's own scripts — so "the pipeline says it finished" and "the artifacts
prove it finished" can never drift apart silently.

Why this exists
---------------
This instrument found most of the thirty-eight defects of the August 2026
self-run campaign — but it lived in a session scratchpad, so customers ran the
pipeline without the thing that catches what the pipeline misses. Every failure
class it checks for was observed in a real run at least once: phases recorded
complete without their artifact, an artifact on disk the manifest never heard
of, a delivered body carrying production scaffolding, a valid chart with no
anchor to embed at, corrections silently lost or silently undone, an APPROVED
review beside an unpublishable piece with nothing saying so, a DRAFT deliverable
published under a clean filename.

The auditor holds two disciplines learned the hard way:

1. **It re-derives; it never trusts.** Scores are recomputed from config, gate
   fields are compared against fresh script output, statuses are checked against
   the files they describe. An agent's report is a claim; the artifact is the
   evidence.
2. **A missing input downgrades a check to reported-N/A, never to silent-pass.**
   "Not checked" and "checked and fine" are different results, and conflating
   them is how every hollow gate in the campaign was born.

Usage:
    python run-audit.py --brand <slug> --run-id <run_id> [--strict] [--out FILE]
    python run-audit.py --run-dir <path>                 [--strict] [--out FILE]

Writes ``run-audit.json`` into the run directory by default (``--out`` to
override). ``checkpoint-manager.py finalize --status completed`` refuses unless
that record exists with a clean verdict — the audit is the price of the word
"completed".

``--strict`` also fails on N/A checks, for CI-style use.

Exit codes: 0 clean · 1 violations (or, with --strict, N/A) · 2 usage/IO error.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

SCRIPTS = pathlib.Path(__file__).resolve().parent

PHASE_ORDER = ["0.5", "1", "2", "3", "3.5", "4", "5", "6", "6.5", "7", "8"]


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path: pathlib.Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def _json(path: pathlib.Path):
    try:
        return json.loads(_read(path))
    except (OSError, json.JSONDecodeError):
        return None


class Audit:
    def __init__(self):
        self.checks = []

    def check(self, section, name, ok, detail=""):
        self.checks.append({"section": section, "name": name,
                            "result": "PASS" if ok else "FAIL",
                            "detail": detail or None})

    def na(self, section, name, reason):
        self.checks.append({"section": section, "name": name,
                            "result": "N/A", "detail": reason})

    def summary(self, strict=False):
        p = sum(1 for c in self.checks if c["result"] == "PASS")
        f = sum(1 for c in self.checks if c["result"] == "FAIL")
        n = sum(1 for c in self.checks if c["result"] == "N/A")
        verdict = "CLEAN" if f == 0 and (not strict or n == 0) else "VIOLATIONS"
        return {"pass": p, "fail": f, "na": n, "verdict": verdict}


def audit_run(run_dir: pathlib.Path, strict: bool = False) -> dict:
    a = Audit()

    # ---------------------------------------------------------- A. manifest
    manifest = _json(run_dir / "run.json")
    a.check("A manifest", "run.json parses", manifest is not None)
    if manifest is None:
        return {"run_dir": str(run_dir), "checks": a.checks,
                **a.summary(strict)}

    completed = [str(x) for x in manifest.get("completed_phases", [])]
    artifacts = manifest.get("phase_artifacts", {})
    a.check("A manifest", "completed phases are known phases",
            set(completed) <= set(PHASE_ORDER),
            f"unknown: {sorted(set(completed) - set(PHASE_ORDER))}")

    missing = [ph for ph in completed
               if not (run_dir / artifacts.get(ph, f"__absent__{ph}")).is_file()]
    a.check("A manifest", "every completed phase has its artifact on disk",
            not missing, f"missing artifacts for phases: {missing}")

    # The invisible-crash window: artifacts present for phases the manifest
    # does not record. Not an error by itself — it is the reconciliation signal
    # resume exists for — but a run FINALIZED with orphans is lying about scope.
    cm = _load("cf_cm_audit", "checkpoint-manager.py")
    orphaned = []
    for ph in PHASE_ORDER:
        if ph in completed:
            continue
        for ext in ("md", "json", "txt"):
            fname, key = cm._artifact_name(ph, ext)
            if key == ph and (run_dir / fname).is_file():
                orphaned.append({"phase": ph, "artifact": fname})
                break
    if manifest.get("status") in ("completed", "blocked"):
        a.check("A manifest", "no orphaned artifacts in a finalized run",
                not orphaned, str(orphaned))
    elif orphaned:
        a.na("A manifest", "orphaned artifacts present (run not finalized)",
             f"reconcile via resume: {orphaned}")

    lc = manifest.get("loop_counts", {})
    a.check("A manifest", "total_loops equals the sum of loop_counts",
            manifest.get("total_loops", 0) == sum(lc.values()),
            f"total_loops={manifest.get('total_loops')} sum={sum(lc.values())}")
    if "loop_history" in manifest:
        hist = manifest["loop_history"]
        a.check("A manifest", "loop history arithmetic matches the counts",
                len(hist) == sum(lc.values()),
                f"history rows={len(hist)} vs count sum={sum(lc.values())}")
    elif lc:
        # Runs created before loop_history existed (pre-3.28) cannot carry it;
        # absence of the KEY dates the run, absence of ROWS would be the defect.
        a.na("A manifest", "loop history",
             "pre-3.28 run: loop_counts exist but the manifest has no "
             "loop_history key — the reasons for these loops were never "
             "persisted and cannot be recovered")

    # ------------------------------------------------------------- B. body
    body_name = artifacts.get("6.5", "phase-6.5-humanized.md")
    body_path = run_dir / body_name
    body = _read(body_path) if body_path.is_file() else None
    if body is None:
        a.na("B body", "body measurements", f"{body_name} absent")
    else:
        tm = _load("cf_tm_audit", "text-metrics.py")
        scaff = tm._residual_scaffolding(body)
        a.check("B body", "no production scaffolding in the delivered body",
                scaff["clean"], f"{scaff['count']} item(s), first at line "
                f"{scaff['items'][0]['line'] if scaff['items'] else '?'}")

        target = (manifest.get("meta") or {}).get("word_count")
        if target:
            wc = tm._body_word_count(body)
            lo, hi = int(target * 0.9), int(target * 1.1)
            a.check("B body", f"body word count inside the gate ({lo}-{hi})",
                    lo <= wc <= hi, f"{wc} words")
        else:
            a.na("B body", "word count gate", "no word_count in run meta")

        mani = _json(run_dir / "phase-3.5-visual-manifest.json")
        if mani:
            vis = mani if isinstance(mani, list) else mani.get("visuals", [])
            generated = [v for v in vis if v.get("status") == "generated"]
            anchors = set(tm._visual_markers(body)["ids"])
            unanchored = [v.get("id") for v in generated
                          if v.get("placement") != "feature-image"
                          and v.get("id") not in anchors]
            a.check("B body", "every generated inline asset has a body anchor",
                    not unanchored, f"no anchor for: {unanchored}")
            ghosts = [v.get("id") for v in vis
                      if v.get("file_path")
                      and not pathlib.Path(v["file_path"]).is_file()]
            a.check("B body", "no manifest path points at a missing file",
                    not ghosts, f"ghost files: {ghosts}")
        else:
            a.na("B body", "visual anchors", "no visual manifest")

    # -------------------------------------------------------- C. authorship
    src = run_dir / "source-draft.md"
    if src.is_file() and body is not None:
        au = _load("cf_au_audit", "authorship.py")
        rec = au.classify(_read(src), body)
        v = rec["violations"]
        a.check("C authorship", "zero author sentences rewritten",
                v["author_sentences_rewritten"] == 0, str(v))
        a.check("C authorship", "zero author sentences dropped",
                v["author_sentences_dropped"] == 0, str(v))
        stored = _json(run_dir / "phase-6.5-authorship.json")
        if stored is not None:
            a.check("C authorship",
                    "stored authorship record matches a fresh measurement",
                    stored.get("author_word_share") == rec["author_word_share"],
                    f"stored {stored.get('author_word_share')} vs fresh "
                    f"{rec['author_word_share']} — the stored record predates "
                    f"a body change")
    elif src.is_file():
        a.na("C authorship", "authorship", "source draft present but no body")
    else:
        a.na("C authorship", "authorship", "no source draft in this run")

    # -------------------------------------------------------- D. fix ledger
    ledger_path = run_dir / "phase-4-fixes.json"
    ledger_verify = None
    if ledger_path.is_file() and body is not None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "fix-ledger.py"), "verify",
             "--run-dir", str(run_dir), "--target", body_name],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            ledger_verify = json.loads(proc.stdout)
        except json.JSONDecodeError:
            ledger_verify = None
        a.check("D ledger", "fix-ledger verify produced a readable result",
                ledger_verify is not None, proc.stdout[:200])
        if ledger_verify:
            a.check("D ledger", "no correction was undone downstream",
                    ledger_verify.get("regressed") == [],
                    f"regressed: {ledger_verify.get('regressed')}")
    elif ledger_path.is_file():
        a.na("D ledger", "ledger verification", "ledger present but no body")
    else:
        a.na("D ledger", "fix ledger", "no phase-4-fixes.json (pre-3.27 run, "
             "or Phase 4 carried no corrections)")

    # ------------------------------------------------------------ E. review
    review = _json(run_dir / "phase-7-review.json")
    if review:
        score = review.get("overall_score")
        decision = review.get("decision", "")
        if isinstance(score, (int, float)) and "APPROVED" in str(decision):
            a.check("E review", "APPROVED decision is backed by its own score",
                    score >= 7.0, f"decision {decision} at score {score}")
        pub = review.get("publication_status")
        if ledger_verify and pub:
            a.check("E review",
                    "review publication_status agrees with the ledger",
                    pub == ledger_verify.get("publication_status"),
                    f"review says {pub}, ledger verify says "
                    f"{ledger_verify.get('publication_status')}")
        elif ledger_verify and not pub:
            a.check("E review", "review records a publication_status",
                    False, "a run with a fix ledger needs the review to say "
                           "whether the piece is publishable")
    else:
        a.na("E review", "review checks", "no phase-7-review.json")

    # ------------------------------------------------------ F. deliverable
    out8 = _json(run_dir / "phase-8-output.json")
    docx = [p for p in run_dir.glob("*.docx")
            if "pre-remediation" not in p.name.lower()]
    if out8:
        pub8 = out8.get("publication_status")
        if ledger_verify and pub8:
            a.check("F deliverable", "phase-8 status agrees with the ledger",
                    pub8 == ledger_verify.get("publication_status"),
                    f"phase-8 says {pub8}, ledger says "
                    f"{ledger_verify.get('publication_status')}")
        if pub8 == "BLOCKED" and docx:
            a.check("F deliverable", "blocked deliverable is marked DRAFT",
                    all(d.name.upper().startswith("DRAFT-") for d in docx),
                    f"{[d.name for d in docx]}")
        if docx:
            bad = []
            for d in docx:
                try:
                    with zipfile.ZipFile(d) as z:
                        if z.testzip() is not None or \
                                "word/document.xml" not in z.namelist():
                            bad.append(d.name)
                except zipfile.BadZipFile:
                    bad.append(d.name)
            a.check("F deliverable", "every .docx is valid OOXML",
                    not bad, f"invalid: {bad}")
    else:
        a.na("F deliverable", "deliverable checks", "no phase-8-output.json")

    # ----------------------------------------------------- G. status honesty
    status = manifest.get("status")
    if status == "completed":
        problems = []
        if ledger_verify and ledger_verify.get("publication_status") == "BLOCKED":
            problems.append("fix ledger holds unresolved blocking corrections")
        if review and review.get("publication_status") == "BLOCKED":
            problems.append("review says BLOCKED")
        a.check("G honesty", "'completed' is not hiding a blocked publication",
                not problems, "; ".join(problems))
    elif status and str(status).startswith("blocked"):
        a.check("G honesty", "'blocked' names at least one open blocker",
                bool(ledger_verify and ledger_verify.get("unresolved_blocking"))
                or bool(review and review.get("publication_status") == "BLOCKED"),
                "status is blocked but no artifact records an open blocker")

    return {"run_dir": str(run_dir), "run_id": manifest.get("run_id"),
            "status": status, "checks": a.checks, **a.summary(strict)}


def main():
    ap = argparse.ArgumentParser(
        description="Re-derive every gate of a run from its artifacts.")
    ap.add_argument("--brand")
    ap.add_argument("--run-id")
    ap.add_argument("--run-dir")
    ap.add_argument("--strict", action="store_true",
                    help="N/A checks also fail the verdict")
    ap.add_argument("--out", default=None,
                    help="result path (default: <run-dir>/run-audit.json)")
    args = ap.parse_args()

    if args.run_dir:
        run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    elif args.brand and args.run_id:
        run_dir = (_common.brand_dir(args.brand) / "runs" / args.run_id).resolve()
    else:
        print(json.dumps({"error": "need --run-dir, or --brand and --run-id"}))
        sys.exit(2)

    if not run_dir.is_dir():
        print(json.dumps({"error": f"no run directory at {run_dir}"}))
        sys.exit(2)

    result = audit_run(run_dir, strict=args.strict)
    out = pathlib.Path(args.out).expanduser() if args.out \
        else run_dir / "run-audit.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    result["written_to"] = str(out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["verdict"] == "CLEAN" else 1)


if __name__ == "__main__":
    main()
