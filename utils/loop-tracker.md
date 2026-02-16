# Loop Tracker — ContentForge Utility

## Purpose
Track feedback loops to prevent infinite iterations and enforce max loop limits.

## Loop Limits (from scoring-thresholds.json)

```json
"feedback_loop_limits": {
  "phase_4_to_3": 2,    // Scientific validation → Drafter
  "phase_6_to_5": 1,    // SEO optimization → Structurer
  "phase_7_to_any": 2,  // Reviewer → Any phase
  "max_total_loops": 5  // Total loops across all phases
}
```

## Loop Tracking State

**Maintained in execution context:**

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
