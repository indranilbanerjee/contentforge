#!/usr/bin/env python3
"""
pipeline-tracker.py
===================
Pipeline performance tracker for ContentForge content pipeline.

Records wall-clock timing for each phase, supports feedback loops
(multiple iterations per phase), and estimates token usage.

Usage:
    python pipeline-tracker.py --action init --brand "Acme" --content-type article --topic "AI Trends"
    python pipeline-tracker.py --action phase-start --brand "Acme" --phase 1
    python pipeline-tracker.py --action phase-end --brand "Acme" --phase 1 --content-words 1200
    python pipeline-tracker.py --action get-report --brand "Acme"

Storage: ~/.claude-marketing/{brand}/pipeline-run.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────

PHASE_NAMES = {
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

AGENT_INSTRUCTION_TOKENS = {
    "1": 3200, "2": 2400, "3": 3800, "3.5": 2600,
    "4": 2200, "5": 2800, "6": 3000, "6.5": 2200,
    "7": 2800, "8": 3400,
}

PHASE_BENCHMARKS = {
    "article": {"1": 300, "2": 180, "3": 420, "3.5": 120, "4": 180, "5": 180, "6": 180, "6.5": 90, "7": 180, "8": 120},
    "blog": {"1": 240, "2": 120, "3": 300, "3.5": 90, "4": 120, "5": 120, "6": 120, "6.5": 60, "7": 120, "8": 90},
    "whitepaper": {"1": 360, "2": 240, "3": 540, "3.5": 180, "4": 240, "5": 240, "6": 240, "6.5": 120, "7": 240, "8": 180},
    "faq": {"1": 180, "2": 120, "3": 240, "3.5": 60, "4": 120, "5": 120, "6": 120, "6.5": 60, "7": 120, "8": 60},
    "research_paper": {"1": 420, "2": 300, "3": 600, "3.5": 180, "4": 300, "5": 240, "6": 240, "6.5": 120, "7": 300, "8": 180},
}

TOKENS_PER_WORD = 1.33
BRAND_PROFILE_TOKENS = 3000
OVERHEAD_MULTIPLIER = 1.8

BASE_DIR = Path.home() / ".claude-marketing"


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


def get_run_file(brand):
    """Return the path to the pipeline-run.json file for a brand."""
    return BASE_DIR / brand / "pipeline-run.json"


def read_run(brand):
    """Read the pipeline-run.json for a brand. Returns (data, error)."""
    run_file = get_run_file(brand)
    if not run_file.exists():
        return None, f"No active pipeline run for brand '{brand}'. Run --action init first."
    try:
        with open(run_file, "r", encoding="utf-8") as f:
            return json.load(f), None
    except (json.JSONDecodeError, OSError) as e:
        return None, f"Error reading pipeline run file: {e}"


def write_run(brand, data):
    """Write the pipeline-run.json for a brand."""
    run_file = get_run_file(brand)
    with open(run_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def now_iso():
    """Return current UTC timestamp in ISO8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Operations ──────────────────────────────────────────────────────

def init_pipeline(brand, content_type, topic):
    """Create a fresh pipeline-run.json for a new content run."""
    brand_dir = BASE_DIR / brand
    brand_dir.mkdir(parents=True, exist_ok=True)

    run_data = {
        "brand": brand,
        "content_type": content_type,
        "topic": topic,
        "pipeline_start": now_iso(),
        "pipeline_end": None,
        "phases": {},
    }

    write_run(brand, run_data)

    return {
        "status": "initialized",
        "brand": brand,
        "run_file": str(get_run_file(brand)),
    }


def phase_start(brand, phase):
    """Record the start of a pipeline phase."""
    data, err = read_run(brand)
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

    write_run(brand, data)

    return {
        "status": "phase_started",
        "phase": phase,
        "name": phase_name,
        "iteration": len(data["phases"][phase]["runs"]),
    }


def phase_end(brand, phase, content_words=None):
    """Record the end of a pipeline phase."""
    data, err = read_run(brand)
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

    write_run(brand, data)

    phase_name = PHASE_NAMES.get(phase, f"Phase {phase}")

    return {
        "status": "phase_ended",
        "phase": phase,
        "name": phase_name,
        "duration_seconds": int(duration),
        "iteration": target_idx + 1,
    }


def get_report(brand):
    """Generate the full timing and token estimation report."""
    data, err = read_run(brand)
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

    # Sort phases in pipeline order
    phase_order = ["1", "2", "3", "3.5", "4", "5", "6", "6.5", "7", "8"]
    active_phases = [p for p in phase_order if p in data["phases"]]

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
    parser.add_argument("--phase", help="Phase number (e.g., 1, 2, 3, 3.5, 4, 5, 6, 6.5, 7, 8)")
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
            result = init_pipeline(args.brand, args.content_type, args.topic)

    elif args.action == "phase-start":
        if not args.phase:
            result = {"error": "Provide --phase for phase-start"}
        else:
            result = phase_start(args.brand, args.phase)

    elif args.action == "phase-end":
        if not args.phase:
            result = {"error": "Provide --phase for phase-end"}
        else:
            result = phase_end(args.brand, args.phase, args.content_words)

    elif args.action == "get-report":
        result = get_report(args.brand)

    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
