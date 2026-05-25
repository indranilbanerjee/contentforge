#!/usr/bin/env python3
"""
checkpoint-manager.py
=====================
Persists per-phase outputs from a ContentForge pipeline run so an interrupted
run can be resumed instead of restarted from scratch.

Background: the 10-phase pipeline can run 20-60 minutes end to end. When the
underlying agent session terminates partway through (context window exhaustion,
network blip, user cancel), the in-memory Phase 1-N outputs are lost. The team
report from the v3.12.2 beta cycle: "process hote hote bodnho hoye geche"
(process stopped midway). Without checkpoints there is nothing to resume from.

This script writes per-phase artifacts to a deterministic location keyed by a
``run_id`` so the orchestrator (or the user via /contentforge:resume) can pick
up exactly where the pipeline stopped.

Storage layout:

    ~/.claude-marketing/{brand}/runs/{run_id}/
        run.json                    — manifest (status, phases, timestamps)
        phase-0.5-title.json        — title curation output
        phase-1-research.md         — research outline + sources
        phase-2-factcheck.json      — verified claim ledger
        phase-3-draft.md            — first draft
        phase-3.5-visuals.json      — visual asset manifest
        phase-4-validation.json     — hallucination report
        phase-5-structure.md        — proofread draft
        phase-6-seo.md              — SEO-optimised draft (with INTERNAL-LINK markers)
        phase-6.5-humanized.md      — humanized draft
        phase-7-review.json         — quality scorecard
        phase-8-output.json         — output-manager result (paths, c2pa, etc.)

Usage:
    python checkpoint-manager.py init --brand Acme --topic "AI in Pharma" --content-type whitepaper
        -> { "run_id": "20260525-114215-ai-in-pharma", "path": "..." }

    python checkpoint-manager.py save --brand Acme --run-id RID --phase 3 \\
        --content-file /tmp/draft.md --extension md
        -> stores Phase 3 draft, updates run.json status

    python checkpoint-manager.py status --brand Acme --run-id RID
        -> { "run_id": RID, "completed_phases": [...], "next_phase": "..." }

    python checkpoint-manager.py list --brand Acme
        -> [ {run_id, topic, status, last_phase, last_updated}, ... ]

    python checkpoint-manager.py resume --brand Acme
        -> {selected: latest incomplete run} OR --run-id <id> to pick one

    python checkpoint-manager.py finalize --brand Acme --run-id RID
        -> marks status=completed, archives the run

Design choices:
    • One file per phase output, named by phase id so the orchestrator can
      read just the slice it needs to resume.
    • run.json is the canonical state — every save updates it atomically.
    • No external dependencies (stdlib only).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path.home() / ".claude-marketing"

PHASE_ORDER = ["0.5", "1", "2", "3", "3.5", "4", "5", "6", "6.5", "7", "8"]
PHASE_LABELS = {
    "0.5": "Title Curation",
    "1": "Research",
    "2": "Fact Check",
    "3": "Content Draft",
    "3.5": "Visual Assets",
    "4": "Scientific Validation",
    "5": "Structure & Proofread",
    "6": "SEO / GEO",
    "6.5": "Humanizer",
    "7": "Reviewer",
    "8": "Output Manager",
}


def _slug(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^\w\s-]", "", (text or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen] or "untitled"


def _runs_dir(brand: str) -> Path:
    return BASE_DIR / brand / "runs"


def _run_dir(brand: str, run_id: str) -> Path:
    return _runs_dir(brand) / run_id


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_manifest(brand: str, run_id: str) -> dict | None:
    f = _run_dir(brand, run_id) / "run.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def _save_manifest(brand: str, run_id: str, manifest: dict) -> None:
    f = _run_dir(brand, run_id) / "run.json"
    tmp = f.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)  # atomic-ish


def init_run(brand: str, topic: str, content_type: str | None) -> dict:
    now = datetime.now(timezone.utc)
    run_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{_slug(topic)}"
    run_dir = _run_dir(brand, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "brand": brand,
        "topic": topic,
        "content_type": content_type,
        "status": "in_progress",
        "started_at": _now_iso(),
        "last_updated": _now_iso(),
        "completed_phases": [],
        "phase_artifacts": {},  # phase -> relative filename
        "phase_labels": PHASE_LABELS,
        "phase_order": PHASE_ORDER,
    }
    _save_manifest(brand, run_id, manifest)
    return {"run_id": run_id, "path": str(run_dir), "manifest": manifest}


def save_phase(brand: str, run_id: str, phase: str, content: str, extension: str) -> dict:
    if phase not in PHASE_LABELS:
        return {"error": f"unknown phase {phase!r}; expected one of {PHASE_ORDER}"}
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}

    label_slug = _slug(PHASE_LABELS[phase], maxlen=20)
    filename = f"phase-{phase}-{label_slug}.{extension.lstrip('.')}"
    out = _run_dir(brand, run_id) / filename
    out.write_text(content, encoding="utf-8")

    if phase not in manifest["completed_phases"]:
        manifest["completed_phases"].append(phase)
        manifest["completed_phases"].sort(key=lambda p: PHASE_ORDER.index(p))
    manifest["phase_artifacts"][phase] = filename
    manifest["last_updated"] = _now_iso()
    _save_manifest(brand, run_id, manifest)

    return {
        "status": "saved",
        "run_id": run_id,
        "phase": phase,
        "phase_label": PHASE_LABELS[phase],
        "artifact": str(out),
        "completed_phases": manifest["completed_phases"],
    }


def get_status(brand: str, run_id: str) -> dict:
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    done = manifest["completed_phases"]
    remaining = [p for p in PHASE_ORDER if p not in done]
    next_phase = remaining[0] if remaining else None
    return {
        "run_id": run_id,
        "brand": brand,
        "topic": manifest.get("topic"),
        "content_type": manifest.get("content_type"),
        "status": manifest.get("status"),
        "started_at": manifest.get("started_at"),
        "last_updated": manifest.get("last_updated"),
        "completed_phases": done,
        "remaining_phases": remaining,
        "next_phase": next_phase,
        "next_phase_label": PHASE_LABELS.get(next_phase, None),
        "phase_artifacts": {
            p: str(_run_dir(brand, run_id) / fn)
            for p, fn in manifest.get("phase_artifacts", {}).items()
        },
    }


def load_phase(brand: str, run_id: str, phase: str) -> dict:
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    fn = manifest.get("phase_artifacts", {}).get(phase)
    if not fn:
        return {"error": f"phase {phase} has no checkpoint in run {run_id}"}
    artifact = _run_dir(brand, run_id) / fn
    return {
        "phase": phase,
        "phase_label": PHASE_LABELS.get(phase),
        "artifact": str(artifact),
        "content": artifact.read_text(encoding="utf-8") if artifact.exists() else None,
    }


def list_runs(brand: str) -> dict:
    rd = _runs_dir(brand)
    if not rd.exists():
        return {"brand": brand, "runs": []}
    runs = []
    for d in sorted(rd.iterdir(), reverse=True):
        if not d.is_dir():
            continue
        m = _load_manifest(brand, d.name)
        if m is None:
            continue
        last_phase = m["completed_phases"][-1] if m.get("completed_phases") else None
        runs.append({
            "run_id": m["run_id"],
            "topic": m.get("topic"),
            "content_type": m.get("content_type"),
            "status": m.get("status"),
            "last_phase": last_phase,
            "last_phase_label": PHASE_LABELS.get(last_phase) if last_phase else None,
            "last_updated": m.get("last_updated"),
            "completed_phases": m.get("completed_phases", []),
        })
    return {"brand": brand, "runs": runs}


def pick_resumable(brand: str, run_id: str | None) -> dict:
    """Return the run that should be resumed. If run_id is provided, use it;
    otherwise pick the most recent in_progress run."""
    if run_id:
        s = get_status(brand, run_id)
        return {"resume_run": s} if "error" not in s else s
    listed = list_runs(brand)
    candidates = [r for r in listed["runs"] if r["status"] == "in_progress"]
    if not candidates:
        return {"brand": brand, "resume_run": None,
                "message": "No in-progress runs found. Start a new pipeline with /contentforge:create-content."}
    target = candidates[0]  # already sorted newest first
    s = get_status(brand, target["run_id"])
    return {"brand": brand, "resume_run": s}


def finalize_run(brand: str, run_id: str, status: str = "completed") -> dict:
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    manifest["status"] = status
    manifest["finalized_at"] = _now_iso()
    manifest["last_updated"] = _now_iso()
    _save_manifest(brand, run_id, manifest)
    return {"status": status, "run_id": run_id}


def discard_run(brand: str, run_id: str) -> dict:
    rd = _run_dir(brand, run_id)
    if not rd.exists():
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    shutil.rmtree(rd)
    return {"status": "discarded", "run_id": run_id}


def main() -> int:
    parser = argparse.ArgumentParser(description="ContentForge per-phase checkpoint manager")
    sub = parser.add_subparsers(dest="action", required=True)

    p_init = sub.add_parser("init", help="Start a new tracked pipeline run")
    p_init.add_argument("--brand", required=True)
    p_init.add_argument("--topic", required=True)
    p_init.add_argument("--content-type", default=None)

    p_save = sub.add_parser("save", help="Save the output of a phase")
    p_save.add_argument("--brand", required=True)
    p_save.add_argument("--run-id", required=True)
    p_save.add_argument("--phase", required=True, help="Phase id (e.g. 1, 3.5, 6.5, 8)")
    g = p_save.add_mutually_exclusive_group(required=True)
    g.add_argument("--content", help="Phase content (inline)")
    g.add_argument("--content-file", help="Path to file containing phase content")
    p_save.add_argument("--extension", default="md", help="File extension for the saved artifact (md / json / txt)")

    p_status = sub.add_parser("status", help="Show run status, completed and remaining phases")
    p_status.add_argument("--brand", required=True)
    p_status.add_argument("--run-id", required=True)

    p_load = sub.add_parser("load", help="Print the saved content for a phase")
    p_load.add_argument("--brand", required=True)
    p_load.add_argument("--run-id", required=True)
    p_load.add_argument("--phase", required=True)

    p_list = sub.add_parser("list", help="List all runs for a brand")
    p_list.add_argument("--brand", required=True)

    p_resume = sub.add_parser("resume", help="Pick the run that should be resumed (latest in_progress, or --run-id)")
    p_resume.add_argument("--brand", required=True)
    p_resume.add_argument("--run-id", default=None)

    p_fin = sub.add_parser("finalize", help="Mark a run as completed or failed")
    p_fin.add_argument("--brand", required=True)
    p_fin.add_argument("--run-id", required=True)
    p_fin.add_argument("--status", default="completed", choices=["completed", "failed", "abandoned"])

    p_dis = sub.add_parser("discard", help="Delete a run's checkpoint directory")
    p_dis.add_argument("--brand", required=True)
    p_dis.add_argument("--run-id", required=True)

    args = parser.parse_args()

    try:
        if args.action == "init":
            result = init_run(args.brand, args.topic, args.content_type)
        elif args.action == "save":
            content = args.content
            if args.content_file:
                content = Path(args.content_file).expanduser().read_text(encoding="utf-8")
            result = save_phase(args.brand, args.run_id, args.phase, content, args.extension)
        elif args.action == "status":
            result = get_status(args.brand, args.run_id)
        elif args.action == "load":
            result = load_phase(args.brand, args.run_id, args.phase)
        elif args.action == "list":
            result = list_runs(args.brand)
        elif args.action == "resume":
            result = pick_resumable(args.brand, args.run_id)
        elif args.action == "finalize":
            result = finalize_run(args.brand, args.run_id, args.status)
        elif args.action == "discard":
            result = discard_run(args.brand, args.run_id)
        else:
            result = {"error": f"unknown action {args.action!r}"}
    except Exception as exc:  # surface unexpected errors cleanly
        result = {"error": f"{type(exc).__name__}: {exc}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
