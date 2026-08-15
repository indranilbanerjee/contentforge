# Loop Tracker — ContentForge Utility

> REFERENCE DOC — pseudocode/algorithm guidance for agents; not an executable module.

## Purpose
Track feedback loops to prevent infinite iterations and enforce max loop limits.

## Loop Limits (from scoring-thresholds.json — single source of truth; keep in sync)

```json
"feedback_loop_limits": {
  "phase_4_to_3_5": 1,  // Scientific validation → Visual assets
  "phase_4_to_3": 2,    // Scientific validation → Drafter
  "phase_6_to_5": 1,    // SEO optimization → Structurer
  "phase_7_to_any": 2,  // Reviewer → Any phase
  "max_total_loops": 5  // Total loops across all phases
}
```

**Persistence:** loop counts persist in the pipeline run's `run.json` under `loop_counts`, and each traversal appends an entry to `loop_history` — both written by the checkpoint-manager `loop` subcommand, so a run resumed with `/contentforge:resume` keeps its history.

Record the reason, always:

```bash
python scripts/checkpoint-manager.py loop --brand {brand} --run-id {run_id} \
  --edge phase_4_to_3 --reason "unsourced claims in section 2"
```

`--reason` is optional and the command warns when it is omitted. That warning is the point: this file documented a `loop_history` carrying `reason` and `timestamp` and claimed it survived a resume, while `record_loop` wrote counts only — so the one thing you open a finished run to find out, *why it looped*, lived in the orchestrator's context and vanished with the session. A count tells you a loop happened; it never tells you what was wrong.

## Loop Tracking State

**Persisted in `run.json`:**

```json
{
  "loop_history": [
    {
      "from_phase": 4,
      "to_phase": 3,
      "iteration": 1,
      "reason": "Unsourced claims detected",
      "timestamp": "2026-02-16T18:15:00Z"
    },
    {
      "from_phase": 7,
      "to_phase": 5,
      "iteration": 1,
      "reason": "Brand compliance failure",
      "timestamp": "2026-02-16T18:22:00Z"
    }
  ],
  "loop_counts": {
    "4_to_3": 1,
    "6_to_5": 0,
    "7_to_any": 1,
    "total": 2
  }
}
```

## Decision Logic

```python
def should_loop(from_phase, to_phase, reason):
    """
    Determine if loop is allowed or should escalate to human
    """
    loop_key = f"{from_phase}_to_{to_phase}"

    # Check phase-specific limit
    if loop_counts[loop_key] >= limits[loop_key]:
        return "ESCALATE_TO_HUMAN", f"Max loops exceeded for {loop_key}"

    # Check total loop limit
    if loop_counts["total"] >= limits["max_total_loops"]:
        return "ESCALATE_TO_HUMAN", "Max total loops exceeded"

    # Loop is allowed
    loop_counts[loop_key] += 1
    loop_counts["total"] += 1
    log_loop(from_phase, to_phase, reason)

    return "LOOP_ALLOWED", f"Looping to Phase {to_phase} (iteration {loop_counts[loop_key]})"
```

## Usage

**Phase 4 (Scientific Validator):**
```python
if hallucinations_detected:
    can_loop, message = should_loop(from_phase=4, to_phase=3, reason="Hallucinations")
    if can_loop == "LOOP_ALLOWED":
        return_to_phase_3_with_feedback()
    else:
        flag_for_human_review(message)
```

**Phase 7 (Reviewer):**
```python
if overall_score < 7.0 and overall_score >= 5.0:
    weakest_phase = identify_weakest_dimension()
    can_loop, message = should_loop(from_phase=7, to_phase=weakest_phase, reason="Score below threshold")
    if can_loop == "LOOP_ALLOWED":
        return_to_phase_with_specific_feedback()
    else:
        flag_for_human_review(message)
```

## Benefits
- Prevents infinite loops
- Tracks loop patterns for optimization
- Automatic escalation to human when stuck
- Clear audit trail of all iterations
