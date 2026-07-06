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

Storage layout (artifact contract — the doc layer depends on these names):

    <marketing-home>/{brand-slug}/runs/{run_id}/
        run.json                       — manifest (status, phases, meta,
                                         loop_counts, pending_rework)
        phase-0.5-title.txt            — confirmed title
        phase-1-research.md            — research outline + sources
        phase-2-factcheck.md           — verified claim ledger
        phase-3-draft.md               — first draft
        phase-3.5-visuals.md           — visual assets draft
        phase-3.5-visual-manifest.json — visual asset manifest (save with
                                         --phase 3.5 --extension json)
        phase-4-validation.md          — hallucination / validation report
        phase-5-structured.md          — proofread draft
        phase-6-seo.md                 — SEO-optimised draft
        phase-6-structure-manifest.json— answer-first structure manifest
                                         (save with --phase 6 --extension json)
        phase-6.5-humanized.md         — humanized draft
        phase-7-review.json            — quality scorecard
        phase-8-output.json            — output-manager result

Usage:
    python checkpoint-manager.py init --brand Acme --topic "AI in Pharma" \
        --content-type whitepaper --keyword "ai in pharma" \
        --audience "pharma execs" --word-count 2500 --tone authoritative
        -> { "run_id": "20260703-114215-ai-in-pharma", "path": "..." }

    python checkpoint-manager.py save --brand Acme --run-id RID --phase 3 \
        --content-file /tmp/draft.md --extension md
        -> stores Phase 3 draft, updates run.json

    python checkpoint-manager.py save --brand Acme --run-id RID --phase 7 \
        --content-file review.json --extension json \
        --pending-rework '{"target_phase": "5", "feedback": "fix flow in section 2"}'
        -> records that the pipeline must loop back to phase 5

    python checkpoint-manager.py loop --brand Acme --run-id RID --edge phase_7_to_5
        -> increments run.json loop_counts["phase_7_to_5"] and total_loops

    python checkpoint-manager.py status --brand Acme --run-id RID
    python checkpoint-manager.py list --brand Acme
    python checkpoint-manager.py resume --brand Acme [--run-id RID]
    python checkpoint-manager.py finalize --brand Acme --run-id RID
    python checkpoint-manager.py discard --brand Acme --run-id RID

Design choices:
    • One file per phase output, named by the canonical artifact contract.
    • run.json is the canonical state — every save updates it atomically.
    • If pending_rework is set, resume/status report its target_phase as the
      next phase. Saving that phase (without a new --pending-rework) clears it.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

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

# Canonical artifact filename suffix per phase (artifact contract).
PHASE_SUFFIX = {
    "0.5": "title",
    "1": "research",
    "2": "factcheck",
    "3": "draft",
    "3.5": "visuals",
    "4": "validation",
    "5": "structured",
    "6": "seo",
    "6.5": "humanized",
    "7": "review",
    "8": "output",
}

# Companion JSON manifests for phases whose primary artifact is markdown.
MANIFEST_NAMES = {
    "3.5": ("phase-3.5-visual-manifest.json", "3.5-manifest"),
    "6": ("phase-6-structure-manifest.json", "6-manifest"),
}


def _slug(text: str, maxlen: int = 40) -> str:
    s = re.sub(r"[^\w\s-]", "", (text or "").lower())
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen] or "untitled"


def _runs_dir(brand: str) -> Path:
    return _common.brand_dir(brand) / "runs"


def _run_dir(brand: str, run_id: str) -> Path:
    return _runs_dir(brand) / run_id


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_manifest(brand: str, run_id: str) -> dict | None:
    f = _run_dir(brand, run_id) / "run.json"
    if not f.exists():
        return None
    data = _common.load_json_safe(f)
    if isinstance(data, dict) and data.get("corrupt"):
        return None
    return data


def _save_manifest(brand: str, run_id: str, manifest: dict) -> None:
    _common.atomic_write_json(_run_dir(brand, run_id) / "run.json", manifest)


def _artifact_name(phase: str, extension: str) -> tuple:
    """Return (filename, artifact_key) for a phase + extension.

    Phases 3.5 and 6 store a companion JSON manifest alongside their markdown
    primary artifact; a json save for those phases targets the manifest slot
    and does NOT mark the phase complete."""
    ext = extension.lstrip(".")
    if phase in MANIFEST_NAMES and ext == "json":
        return MANIFEST_NAMES[phase]
    return f"phase-{phase}-{PHASE_SUFFIX[phase]}.{ext}", phase


def init_run(brand: str, topic: str, content_type: str | None,
             meta: dict | None = None) -> dict:
    now = datetime.now(timezone.utc)
    run_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{_slug(topic)}"
    run_dir = _run_dir(brand, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_id": run_id,
        "brand": brand,
        "topic": topic,
        "content_type": content_type,
        "meta": meta or {},
        "status": "in_progress",
        "started_at": _now_iso(),
        "last_updated": _now_iso(),
        "completed_phases": [],
        "phase_artifacts": {},  # artifact key -> relative filename
        "loop_counts": {},
        "total_loops": 0,
        "pending_rework": None,
        "phase_labels": PHASE_LABELS,
        "phase_order": PHASE_ORDER,
    }
    _save_manifest(brand, run_id, manifest)
    return {"run_id": run_id, "path": str(run_dir), "manifest": manifest}


def save_phase(brand: str, run_id: str, phase: str, content: str,
               extension: str, pending_rework: dict | None = None) -> dict:
    if phase not in PHASE_LABELS:
        return {"error": f"unknown phase {phase!r}; expected one of {PHASE_ORDER}"}
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}

    filename, artifact_key = _artifact_name(phase, extension)
    out = _run_dir(brand, run_id) / filename
    out.write_text(content, encoding="utf-8")

    is_primary = artifact_key == phase
    if is_primary and phase not in manifest["completed_phases"]:
        manifest["completed_phases"].append(phase)
        manifest["completed_phases"].sort(
            key=lambda p: PHASE_ORDER.index(p) if p in PHASE_ORDER else 99)
    manifest.setdefault("phase_artifacts", {})[artifact_key] = filename

    # Rework bookkeeping: a new --pending-rework wins; otherwise saving the
    # rework target phase clears the pending flag.
    if pending_rework is not None:
        manifest["pending_rework"] = pending_rework
    elif (is_primary and manifest.get("pending_rework")
          and manifest["pending_rework"].get("target_phase") == phase):
        manifest["pending_rework"] = None

    manifest["last_updated"] = _now_iso()
    _save_manifest(brand, run_id, manifest)

    # v3.12.10: if Cowork+Drive is configured, mark this artifact as needing
    # upload to Drive. The agent (output-manager / orchestrator) consumes
    # _sync-pending.json after each phase and uploads via the Drive MCP.
    drive_sync_hint = _maybe_mark_pending(brand, run_id, [filename, "run.json"])

    return {
        "status": "saved",
        "run_id": run_id,
        "phase": phase,
        "phase_label": PHASE_LABELS[phase],
        "artifact": str(out),
        "artifact_key": artifact_key,
        "completed_phases": manifest["completed_phases"],
        "pending_rework": manifest.get("pending_rework"),
        "drive_sync_hint": drive_sync_hint,
    }


def record_loop(brand: str, run_id: str, edge: str) -> dict:
    """Increment the loop counter for a feedback edge (e.g. phase_7_to_5)."""
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    counts = manifest.setdefault("loop_counts", {})
    counts[edge] = counts.get(edge, 0) + 1
    manifest["total_loops"] = sum(counts.values())
    manifest["last_updated"] = _now_iso()
    _save_manifest(brand, run_id, manifest)
    return {
        "status": "loop_recorded",
        "run_id": run_id,
        "edge": edge,
        "edge_count": counts[edge],
        "loop_counts": counts,
        "total_loops": manifest["total_loops"],
    }


def _maybe_mark_pending(brand: str, run_id: str, files: list) -> dict:
    """If a Cowork+Drive config exists, append these files to the run's
    _sync-pending.json so the agent knows to upload them. Returns a small
    hint dict the caller can surface. If Cowork is not configured, returns
    {"cowork_drive_configured": false} and does nothing."""
    cowork_config = _common.marketing_home() / "_cowork-config.json"
    if not cowork_config.exists():
        return {"cowork_drive_configured": False}
    cfg = _common.load_json_safe(cowork_config)
    if "error" in cfg:
        return {"cowork_drive_configured": False,
                "error": "cowork-config.json present but unreadable"}
    if cfg.get("environment") != "cowork-sandbox":
        # local-mode user — sync not needed
        return {"cowork_drive_configured": False,
                "reason": "config exists but environment is not cowork-sandbox"}

    pending_path = _run_dir(brand, run_id) / "_sync-pending.json"
    try:
        if pending_path.exists():
            data = _common.load_json_safe(pending_path)
            if "error" in data:
                data = {"pending": [], "uploaded": []}
            data.setdefault("pending", [])
            data.setdefault("uploaded", [])
        else:
            data = {"pending": [], "uploaded": []}
        for f in files:
            if f not in data["pending"] and f not in {u["file"] for u in data["uploaded"]}:
                data["pending"].append(f)
        data["last_updated"] = _now_iso()
        _common.atomic_write_json(pending_path, data)
        return {
            "cowork_drive_configured": True,
            "files_marked_pending": files,
            "total_pending_after": len(data["pending"]),
            "drive_root": cfg.get("drive_root_folder_name"),
            "note": "Agent: read _sync-pending.json and upload listed files via the Drive MCP tool. Use drive-sync-state.py --action mark-uploaded after each successful upload.",
        }
    except OSError as e:
        return {"cowork_drive_configured": True,
                "error": f"failed to write _sync-pending.json: {e}"}


def get_status(brand: str, run_id: str) -> dict:
    manifest = _load_manifest(brand, run_id)
    if manifest is None:
        return {"error": f"no run found: brand={brand} run_id={run_id}"}
    done = manifest["completed_phases"]
    remaining = [p for p in PHASE_ORDER if p not in done]
    pending_rework = manifest.get("pending_rework")
    if pending_rework and pending_rework.get("target_phase"):
        next_phase = pending_rework["target_phase"]
    else:
        next_phase = remaining[0] if remaining else None
    return {
        "run_id": run_id,
        "brand": brand,
        "topic": manifest.get("topic"),
        "content_type": manifest.get("content_type"),
        "meta": manifest.get("meta", {}),
        "status": manifest.get("status"),
        "started_at": manifest.get("started_at"),
        "last_updated": manifest.get("last_updated"),
        "completed_phases": done,
        "remaining_phases": remaining,
        "next_phase": next_phase,
        "next_phase_label": PHASE_LABELS.get(next_phase, None),
        "loop_counts": manifest.get("loop_counts", {}),
        "total_loops": manifest.get("total_loops", 0),
        "pending_rework": pending_rework,
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


def main() -> None:
    parser = argparse.ArgumentParser(description="ContentForge per-phase checkpoint manager")
    sub = parser.add_subparsers(dest="action", required=True)

    p_init = sub.add_parser("init", help="Start a new tracked pipeline run")
    p_init.add_argument("--brand", required=True)
    p_init.add_argument("--topic", required=True)
    p_init.add_argument("--content-type", default=None)
    p_init.add_argument("--keyword", default=None, help="Primary keyword (stored in run.json meta)")
    p_init.add_argument("--audience", default=None, help="Target audience (stored in run.json meta)")
    p_init.add_argument("--word-count", default=None, type=int, help="Target word count (stored in run.json meta)")
    p_init.add_argument("--tone", default=None, help="Requested tone (stored in run.json meta)")
    p_init.add_argument("--meta", default=None,
                        help='JSON object merged into run.json "meta" (keys here win over the '
                             'individual flags), e.g. \'{"keyword": "ai in pharma"}\'')

    p_save = sub.add_parser("save", help="Save the output of a phase")
    p_save.add_argument("--brand", required=True)
    p_save.add_argument("--run-id", required=True)
    p_save.add_argument("--phase", required=True, help="Phase id (e.g. 1, 3.5, 6.5, 8)")
    g = p_save.add_mutually_exclusive_group(required=True)
    g.add_argument("--content", help="Phase content (inline; use --content-file for large content)")
    g.add_argument("--content-file", help="Path to file containing phase content")
    p_save.add_argument("--extension", default="md",
                        help="File extension for the saved artifact (md / json / txt). "
                             "json on phases 3.5 and 6 targets the companion manifest slot.")
    p_save.add_argument("--pending-rework", default=None,
                        help='JSON: {"target_phase": "5", "feedback": "..."} — records that the pipeline must loop back')

    p_loop = sub.add_parser("loop", help="Record a feedback-loop traversal (e.g. phase_7_to_5)")
    p_loop.add_argument("--brand", required=True)
    p_loop.add_argument("--run-id", required=True)
    p_loop.add_argument("--edge", required=True, help="Loop edge id, e.g. phase_7_to_5 / phase_4_to_3")

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
            meta = {k: v for k, v in {
                "keyword": args.keyword,
                "audience": args.audience,
                "word_count": args.word_count,
                "tone": args.tone,
            }.items() if v is not None}
            if args.meta:
                extra = json.loads(args.meta)
                if not isinstance(extra, dict):
                    raise ValueError("--meta must be a JSON object")
                meta.update(extra)
            result = init_run(args.brand, args.topic, args.content_type, meta=meta)
        elif args.action == "save":
            content = args.content
            if args.content_file:
                content = Path(args.content_file).expanduser().read_text(encoding="utf-8")
            pending_rework = None
            if args.pending_rework:
                pending_rework = json.loads(args.pending_rework)
            result = save_phase(args.brand, args.run_id, args.phase, content,
                                args.extension, pending_rework=pending_rework)
        elif args.action == "loop":
            result = record_loop(args.brand, args.run_id, args.edge)
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
    except json.JSONDecodeError as exc:
        result = {"error": f"invalid JSON in --meta / --pending-rework: {exc}"}
    except Exception as exc:  # surface unexpected errors cleanly
        result = {"error": f"{type(exc).__name__}: {exc}"}

    _common.finish(result)


if __name__ == "__main__":
    main()
