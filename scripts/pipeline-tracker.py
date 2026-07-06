#!/usr/bin/env python3
"""
pipeline-tracker.py
===================
Pipeline performance tracker for ContentForge content pipeline.

Records wall-clock timing for each phase, supports feedback loops
(multiple iterations per phase), and estimates token usage.

Usage:
    python pipeline-tracker.py --action init --brand "Acme" --run-id RID --content-type article --topic "AI Trends"
    python pipeline-tracker.py --action phase-start --brand "Acme" --run-id RID --phase 1
    python pipeline-tracker.py --action phase-end --brand "Acme" --run-id RID --phase 1 --content-words 1200
    python pipeline-tracker.py --action get-report --brand "Acme" --run-id RID

Storage:
    with --run-id:    <brand-dir>/runs/{run_id}/pipeline-run.json
                      (per-run — parallel batch pipelines don't clobber each other)
    without --run-id: <brand-dir>/pipeline-run.json (legacy single-run path)
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

# ── Constants ───────────────────────────────────────────────────────

PHASE_NAMES = {
    "0.5": "Title Curation",
    "1": "Research",
    "2": "Fact Checking",
    "3": "Content Drafting",
    "3.5": "Visual Asset Annotation",
    "4": "Scientific Validation",
    "5": "Structuring & Proofreading",
    "6": "SEO/GEO Optimization",
    "6.5": "Humanizer",
    "7": "Review",
    "8": "Output & Delivery",
}

PHASE_ORDER = ["0.5", "1", "2", "3", "3.5", "4", "5", "6", "6.5", "7", "8"]

AGENT_INSTRUCTION_TOKENS = {
    "0.5": 1200, "1": 3200, "2": 2400, "3": 3800, "3.5": 2600,
    "4": 2200, "5": 2800, "6": 3000, "6.5": 2200,
    "7": 2800, "8": 3400,
}

PHASE_BENCHMARKS = {
    "article": {"0.5": 60, "1": 300, "2": 180, "3": 420, "3.5": 120, "4": 180, "5": 180, "6": 180, "6.5": 90, "7": 180, "8": 120},
    "blog": {"0.5": 60, "1": 240, "2": 120, "3": 300, "3.5": 90, "4": 120, "5": 120, "6": 120, "6.5": 60, "7": 120, "8": 90},
    "whitepaper": {"0.5": 90, "1": 360, "2": 240, "3": 540, "3.5": 180, "4": 240, "5": 240, "6": 240, "6.5": 120, "7": 240, "8": 180},
    "faq": {"0.5": 60, "1": 180, "2": 120, "3": 240, "3.5": 60, "4": 120, "5": 120, "6": 120, "6.5": 60, "7": 120, "8": 60},
    "research_paper": {"0.5": 90, "1": 420, "2": 300, "3": 600, "3.5": 180, "4": 300, "5": 240, "6": 240, "6.5": 120, "7": 300, "8": 180},
}

TOKENS_PER_WORD = 1.33
BRAND_PROFILE_TOKENS = 3000
OVERHEAD_MULTIPLIER = 1.8


# ── Helpers ─────────────────────────────────────────────────────────

def format_time(seconds):
    """Format seconds into human-readable 'Xm Ys' format."""
    if seconds is None:
        return "N/A"
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    if minutes > 0:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def get_run_file(brand, run_id=None):
    """Path to the pipeline-run.json for a brand (and optionally a run)."""
    bd = _common.brand_dir(brand)
    if run_id:
        return bd / "runs" / run_id / "pipeline-run.json"
    return bd / "pipeline-run.json"


def read_run(brand, run_id=None):
    """Read the pipeline-run.json. Returns (data, error)."""
    run_file = get_run_file(brand, run_id)
    if not run_file.exists():
        return None, (f"No active pipeline run for brand '{brand}'"
                      + (f" run '{run_id}'" if run_id else "")
                      + ". Run --action init first.")
    data = _common.load_json_safe(run_file)
    if isinstance(data, dict) and "error" in data:
        return None, f"Error reading pipeline run file: {data['error']}"
    return data, None


def write_run(brand, data, run_id=None):
    """Atomically write the pipeline-run.json."""
    _common.atomic_write_json(get_run_file(brand, run_id), data)


def now_iso():
    """Return current UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Operations ──────────────────────────────────────────────────────

def init_pipeline(brand, content_type, topic, run_id=None):
    """Create a fresh pipeline-run.json for a new content run."""
    run_data = {
        "brand": brand,
        "run_id": run_id,
        "content_type": content_type,
        "topic": topic,
        "pipeline_start": now_iso(),
        "pipeline_end": None,
        "phases": {},
    }

    write_run(brand, run_data, run_id)

    return {
        "status": "initialized",
        "brand": brand,
        "run_id": run_id,
        "run_file": str(get_run_file(brand, run_id)),
    }


def phase_start(brand, phase, run_id=None):
    """Record the start of a pipeline phase."""
    data, err = read_run(brand, run_id)
    if err:
        return {"error": err}

    phase_name = PHASE_NAMES.get(phase, f"Phase {phase}")

    # Create phase entry if it doesn't exist
    if phase not in data["phases"]:
        data["phases"][phase] = {
            "name": phase_name,
            "runs": [],
        }

    # Append a new run entry
    data["phases"][phase]["runs"].append({
        "start": now_iso(),
        "end": None,
        "content_words": None,
    })

    write_run(brand, data, run_id)

    return {
        "status": "phase_started",
        "phase": phase,
        "name": phase_name,
        "run_id": run_id,
        "iteration": len(data["phases"][phase]["runs"]),
    }


def phase_end(brand, phase, content_words=None, run_id=None):
    """Record the end of a pipeline phase."""
    data, err = read_run(brand, run_id)
    if err:
        return {"error": err}

    if phase not in data["phases"]:
        return {"error": f"Phase {phase} has not been started yet."}

    # Find the last run with end=null
    runs = data["phases"][phase]["runs"]
    target_run = None
    target_idx = None
    for i in range(len(runs) - 1, -1, -1):
        if runs[i]["end"] is None:
            target_run = runs[i]
            target_idx = i
            break

    if target_run is None:
        return {"error": f"No open run found for phase {phase}. Call phase-start first."}

    end_time = now_iso()
    target_run["end"] = end_time

    if content_words is not None:
        target_run["content_words"] = content_words

    # Calculate duration
    start_dt = datetime.fromisoformat(target_run["start"].replace("Z", "+00:00"))
    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    duration = (end_dt - start_dt).total_seconds()

    # If this is phase 8, mark pipeline end
    if phase == "8":
        data["pipeline_end"] = end_time

    write_run(brand, data, run_id)

    phase_name = PHASE_NAMES.get(phase, f"Phase {phase}")

    return {
        "status": "phase_ended",
        "phase": phase,
        "name": phase_name,
        "run_id": run_id,
        "duration_seconds": int(duration),
        "iteration": target_idx + 1,
    }


def get_report(brand, run_id=None):
    """Generate the full timing and token estimation report."""
    data, err = read_run(brand, run_id)
    if err:
        return {"error": err}

    content_type = data.get("content_type", "")
    benchmarks = PHASE_BENCHMARKS.get(content_type, {})

    # ── Per-phase calculations ──────────────────────────────────────
    phase_reports = []
    total_time = 0
    total_benchmark = 0
    agent_instruction_tokens = 0
    content_tokens = 0

    active_phases = [p for p in PHASE_ORDER if p in data["phases"]]

    for phase_id in active_phases:
        phase_data = data["phases"][phase_id]
        runs = phase_data["runs"]

        # Total duration across all runs
        phase_duration = 0
        max_content_words = 0

        for run in runs:
            if run["start"] and run["end"]:
                start_dt = datetime.fromisoformat(run["start"].replace("Z", "+00:00"))
                end_dt = datetime.fromisoformat(run["end"].replace("Z", "+00:00"))
                phase_duration += (end_dt - start_dt).total_seconds()
            if run.get("content_words") and run["content_words"] > max_content_words:
                max_content_words = run["content_words"]

        phase_duration = int(phase_duration)
        total_time += phase_duration

        # Benchmark comparison
        benchmark = benchmarks.get(phase_id)
        if benchmark is not None:
            total_benchmark += benchmark
            status = "under" if phase_duration <= benchmark else "over"
        else:
            status = "under"

        phase_reports.append({
            "phase": phase_id,
            "name": phase_data["name"],
            "duration_seconds": phase_duration,
            "duration_formatted": format_time(phase_duration),
            "benchmark_seconds": benchmark,
            "benchmark_formatted": format_time(benchmark) if benchmark is not None else "N/A",
            "status": status,
            "iterations": len(runs),
        })

        # Token estimates
        if phase_id in AGENT_INSTRUCTION_TOKENS:
            agent_instruction_tokens += AGENT_INSTRUCTION_TOKENS[phase_id]
        if max_content_words > 0:
            content_tokens += int(max_content_words * TOKENS_PER_WORD)

    # ── Pipeline-level calculations ─────────────────────────────────
    pipeline_status = "under_benchmark" if total_time <= total_benchmark else "over_benchmark"

    # ── Token estimation ────────────────────────────────────────────
    config_tokens = BRAND_PROFILE_TOKENS
    measurable_subtotal = agent_instruction_tokens + content_tokens + config_tokens
    system_overhead = int(measurable_subtotal * (OVERHEAD_MULTIPLIER - 1))
    estimated_total = measurable_subtotal + system_overhead

    return {
        "brand": data["brand"],
        "run_id": data.get("run_id"),
        "content_type": content_type,
        "topic": data.get("topic", ""),
        "total_time_seconds": total_time,
        "total_time_formatted": format_time(total_time),
        "benchmark_seconds": total_benchmark,
        "benchmark_formatted": format_time(total_benchmark),
        "status": pipeline_status,
        "phases": phase_reports,
        "token_estimate": {
            "agent_instructions": agent_instruction_tokens,
            "content": content_tokens,
            "config_and_brand_profile": config_tokens,
            "measurable_subtotal": measurable_subtotal,
            "system_overhead": system_overhead,
            "estimated_total": estimated_total,
            "disclaimer": "Token estimates are approximate. For precise session costs, use /cost.",
        },
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Pipeline Performance Tracker")
    parser.add_argument("--action", required=True,
                        choices=["init", "phase-start", "phase-end", "get-report"])
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--run-id", default=None,
                        help="Checkpoint run id. Stores timing per-run under <brand>/runs/{run_id}/ "
                             "(recommended; required for parallel batch pipelines). "
                             "Omit for the legacy per-brand file.")
    parser.add_argument("--phase", help="Phase number (e.g., 0.5, 1, 2, 3, 3.5, 4, 5, 6, 6.5, 7, 8)")
    parser.add_argument("--content-type",
                        help="Content type for init (article, blog, whitepaper, faq, research_paper)")
    parser.add_argument("--topic", help="Content topic for init")
    parser.add_argument("--content-words", type=int, help="Word count at end of phase")
    args = parser.parse_args()

    # Dispatch
    if args.action == "init":
        if not args.content_type:
            result = {"error": "Provide --content-type for init"}
        elif not args.topic:
            result = {"error": "Provide --topic for init"}
        else:
            result = init_pipeline(args.brand, args.content_type, args.topic, run_id=args.run_id)

    elif args.action == "phase-start":
        if not args.phase:
            result = {"error": "Provide --phase for phase-start"}
        else:
            result = phase_start(args.brand, args.phase, run_id=args.run_id)

    elif args.action == "phase-end":
        if not args.phase:
            result = {"error": "Provide --phase for phase-end"}
        else:
            result = phase_end(args.brand, args.phase, args.content_words, run_id=args.run_id)

    elif args.action == "get-report":
        result = get_report(args.brand, run_id=args.run_id)

    else:
        result = {"error": f"Unknown action: {args.action}"}

    _common.finish(result)


if __name__ == "__main__":
    main()
