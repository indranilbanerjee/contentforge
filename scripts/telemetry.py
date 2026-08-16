#!/usr/bin/env python3
"""telemetry.py — cross-run aggregation of the signals each run already records.

Why this exists (v4.0)
----------------------
Every run directory holds loop history (which gate-fail edges fired, and why),
per-phase timings, and — from 4.0 — the humanizer's per-pattern hit counts.
All of it died with its run. Aggregated across runs, the same data answers two
questions no single run can: "where does the pipeline systematically stumble?"
(a loop edge that fires on a third of runs for one content type is a contract
problem, not a run problem — the signal that drove the August 2026 fix arc,
made continuous) and "what does the humanizer keep fixing for this brand?"
(a pattern recurring across runs belongs in the drafter's brief, so the
pipeline stops re-making a mistake its own quality machinery keeps catching).

Discipline
----------
- Aggregation only; this script never modifies a run.
- Runs without instrumentation are counted as ``not_instrumented``, never as
  zero — absence of measurement is not evidence of absence.
- Advisories carry a recurrence floor: below ``--min-runs`` instrumented
  occurrences, the answer is ``insufficient_history`` and no advisory is
  emitted. A loop that feeds briefs from anecdote launders noise into policy.
- Malformed run manifests are reported in ``unreadable_runs``, never silently
  skipped.
- Advisories inform the Phase 3 brief. They never touch a gate, a threshold,
  or a verdict.

Actions
-------
  loops      --brand <slug> [--window N]      loop-edge + timing aggregation
  patterns   --brand <slug> [--window N]      humanizer pattern hits across runs
  advisories --brand <slug> [--min-runs 3] [--window 10]
                                              drafter-brief advisory lines

Exit codes: 0 ok · 1 no runs found · 2 usage/IO error. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

PATTERN_HITS_FILE = "phase-6.5-pattern-hits.json"


def _load_json(path):
    """_common.load_json_safe never raises AND never returns None — missing or
    corrupt files come back as a dict carrying an 'error' key (payloads produced
    by ContentForge never carry one, per its contract). Normalize to None so
    'unreadable' has one spelling here."""
    doc = _common.load_json_safe(path)
    if isinstance(doc, dict) and "error" in doc:
        return None
    return doc


def _duration_seconds(start, end):
    """Seconds between two ISO-8601 stamps, or None when either is unusable.
    A malformed stamp yields None (unknown), never zero."""
    from datetime import datetime
    try:
        s = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        e = datetime.fromisoformat(str(end).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    dur = (e - s).total_seconds()
    return dur if dur >= 0 else None


def run_dirs(brand: str) -> list:
    """All run directories for a brand, newest first (run ids sort lexically)."""
    root = _common.brand_dir(brand) / "runs"
    if not root.is_dir():
        return []
    return sorted((d for d in root.iterdir() if d.is_dir()), reverse=True)


def _load_runs(brand: str, window: int):
    runs, unreadable = [], []
    for d in run_dirs(brand)[:window]:
        manifest = _load_json(d / "run.json")
        if manifest is None:
            unreadable.append(d.name)
            continue
        runs.append((d, manifest))
    return runs, unreadable


def cmd_loops(args) -> int:
    runs, unreadable = _load_runs(args.brand, args.window)
    if not runs and not unreadable:
        print(json.dumps({"ok": False, "error": f"no runs for brand {args.brand!r}"}))
        return 1
    edges: dict = {}
    by_type: dict = {}
    total_loops = 0
    reasons: dict = {}
    timings: dict = {}
    for d, m in runs:
        ctype = m.get("content_type", "unknown")
        by_type.setdefault(ctype, {"runs": 0, "loops": 0})
        by_type[ctype]["runs"] += 1
        for edge, n in (m.get("loop_counts") or {}).items():
            edges[edge] = edges.get(edge, 0) + n
            by_type[ctype]["loops"] += n
            total_loops += n
        for entry in (m.get("loop_history") or []):
            key = entry.get("reason") or "(no reason recorded)"
            reasons[key] = reasons.get(key, 0) + 1
        tracker = _load_json(d / "pipeline-run.json") or {}
        # pipeline-run.json shape: phases is a dict keyed by phase number, each
        # holding runs: [{start, end, content_words}] with ISO-8601 stamps.
        for phase_no, ph in (tracker.get("phases") or {}).items():
            if not isinstance(ph, dict):
                continue
            for attempt in (ph.get("runs") or []):
                dur = _duration_seconds(attempt.get("start"), attempt.get("end"))
                if dur is not None:
                    timings.setdefault(str(phase_no), []).append(dur)
    timing_summary = {
        ph: {"n": len(v), "avg_seconds": round(sum(v) / len(v), 1),
             "max_seconds": round(max(v), 1)}
        for ph, v in sorted(timings.items()) if v
    }
    print(json.dumps({
        "ok": True, "brand": args.brand, "runs_analyzed": len(runs),
        "unreadable_runs": unreadable,
        "total_loops": total_loops,
        "edges_fired": dict(sorted(edges.items(), key=lambda kv: -kv[1])),
        "by_content_type": by_type,
        "loop_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "phase_timings": timing_summary,
        "reading": ("an edge that fires across many runs of one content type is "
                    "a contract problem, not a run problem — fix the template or "
                    "the gate, not the next run"),
    }, indent=2))
    return 0


def _pattern_rows(brand: str, window: int):
    runs, unreadable = _load_runs(brand, window)
    instrumented, not_instrumented = [], 0
    for d, m in runs:
        hits = _load_json(d / PATTERN_HITS_FILE)
        if hits is None:
            not_instrumented += 1
            continue
        clean = {str(k): v for k, v in hits.items()
                 if isinstance(v, int) and not isinstance(v, bool) and v > 0}
        instrumented.append((d.name, clean))
    return runs, unreadable, instrumented, not_instrumented


def cmd_patterns(args) -> int:
    runs, unreadable, instrumented, not_instrumented = _pattern_rows(args.brand, args.window)
    if not runs and not unreadable:
        print(json.dumps({"ok": False, "error": f"no runs for brand {args.brand!r}"}))
        return 1
    totals: dict = {}
    presence: dict = {}
    for _, clean in instrumented:
        for pid, n in clean.items():
            totals[pid] = totals.get(pid, 0) + n
            presence[pid] = presence.get(pid, 0) + 1
    print(json.dumps({
        "ok": True, "brand": args.brand, "runs_analyzed": len(runs),
        "unreadable_runs": unreadable,
        "instrumented_runs": len(instrumented),
        "not_instrumented_runs": not_instrumented,
        "note": ("not_instrumented runs predate the phase-6.5-pattern-hits.json "
                 "contract (4.0) — they are unknown, not zero"),
        "pattern_totals": dict(sorted(totals.items(), key=lambda kv: -kv[1])),
        "pattern_run_presence": dict(sorted(presence.items(), key=lambda kv: -kv[1])),
    }, indent=2))
    return 0


def cmd_advisories(args) -> int:
    runs, unreadable, instrumented, not_instrumented = _pattern_rows(args.brand, args.window)
    if not runs and not unreadable:
        print(json.dumps({"ok": False, "error": f"no runs for brand {args.brand!r}"}))
        return 1
    if len(instrumented) < args.min_runs:
        print(json.dumps({
            "ok": True, "brand": args.brand,
            "status": "insufficient_history",
            "instrumented_runs": len(instrumented),
            "min_runs": args.min_runs,
            "advisories": [],
            "note": ("no advisory below the recurrence floor — a brief fed from "
                     "fewer runs than the floor is fed from anecdote"),
        }, indent=2))
        return 0
    presence: dict = {}
    totals: dict = {}
    for _, clean in instrumented:
        for pid, n in clean.items():
            presence[pid] = presence.get(pid, 0) + 1
            totals[pid] = totals.get(pid, 0) + n
    advisories = []
    for pid, runs_seen in sorted(presence.items(), key=lambda kv: -kv[1]):
        if runs_seen >= args.min_runs:
            advisories.append({
                "pattern": pid,
                "runs_seen": runs_seen,
                "instrumented_runs": len(instrumented),
                "total_instances": totals[pid],
                "brief_line": (f"Recurring humanizer catch for this brand: pattern "
                               f"{pid} fired in {runs_seen} of the last "
                               f"{len(instrumented)} runs ({totals[pid]} instances) — "
                               f"avoid it at drafting time."),
            })
    print(json.dumps({
        "ok": True, "brand": args.brand, "status": "ok",
        "instrumented_runs": len(instrumented), "min_runs": args.min_runs,
        "advisories": advisories,
        "scope": ("advisories inform the Phase 3 brief only; they never modify "
                  "a gate, a threshold, or a verdict"),
    }, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-run telemetry aggregation (read-only)")
    sub = ap.add_subparsers(dest="action", required=True)
    for name in ("loops", "patterns"):
        p = sub.add_parser(name)
        p.add_argument("--brand", required=True)
        p.add_argument("--window", type=int, default=20)
    p = sub.add_parser("advisories")
    p.add_argument("--brand", required=True)
    p.add_argument("--min-runs", type=int, default=3)
    p.add_argument("--window", type=int, default=10)
    args = ap.parse_args()
    return {"loops": cmd_loops, "patterns": cmd_patterns,
            "advisories": cmd_advisories}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
