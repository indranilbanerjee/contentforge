---
description: Resume a ContentForge pipeline run that was interrupted partway through
argument-hint: "[run-id] (omit to pick the latest in-progress run for the active brand)"
---

# Resume Interrupted Pipeline

Pick up a `/contentforge:create-content` run that stopped before Phase 8 finished — instead of restarting from scratch, load the saved Phase N outputs and continue from Phase N+1.

## Trigger

User runs `/contentforge:resume` (with optional `run-id` argument). Also surface this command in any error message when a pipeline run terminates abnormally.

## What this fixes

ContentForge's 10-phase pipeline runs 20-60 minutes end to end. If the underlying agent session terminates partway through (context-window exhaustion, network blip, user cancels, machine sleeps), the in-memory Phase 1-N outputs disappear. As of v3.12.3 every phase writes its output to `~/.claude-marketing/{brand}/runs/{run_id}/` via `scripts/checkpoint-manager.py`, so a fresh session can reload those artifacts and skip the phases that already completed.

## Process

### Step 0: Cross-session checkpoint download (v3.12.10+, Cowork only)

Before listing local runs, check if we're in Cowork+Drive mode — if so, the user might be resuming from a DIFFERENT Cowork session (different sandbox), and the local FS has no record of the run. Pull the run's checkpoint state from Drive first.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/drive-sync-state.py --action read-config
```

If `configured: false` OR `environment != "cowork-sandbox"`, skip to Step 1 (local-mode flow).

If `configured: true` AND a Drive MCP is available:

1. Use the Drive MCP to list contents of `{drive_root_folder_name}/_runs/`
2. For each `<run_id>` subfolder, check if it has phase artifacts (`phase-*.md`, `_manifest.json`, `_sync-pending.json`)
3. Identify in-progress runs (manifest exists but `phase_artifacts` doesn't include `phase 8` — i.e., output-manager hasn't completed)
4. For each in-progress run that doesn't yet exist locally at `~/.claude-marketing/{brand}/runs/{run_id}/`:
   - Use the Drive MCP to download every file from `{drive_root}/_runs/{run_id}/` into the local sandbox path
   - This restores the run's full checkpoint history so Step 2 below can load artifacts normally
5. Tell the user: "Pulled {N} run(s) from Drive for resume eligibility: {run_id list}"

Then proceed to Step 1.

### Step 1: Pick the run to resume

If the user supplied a `run-id`, use it directly. Otherwise list the in-progress runs for the active brand and either auto-pick the most recent or ask the user to choose if there's ambiguity.

```bash
# Auto-pick the most recent in-progress run for the active brand
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}"

# Or with an explicit run id
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}" --run-id "{run_id}"

# List all runs (use when the user wants to choose among several)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py list --brand "{active_brand}"
```

The `resume` action returns the status of the selected run, including `completed_phases`, `remaining_phases`, `next_phase`, and the absolute paths of every saved artifact.

If there are no in-progress runs, say so and offer to start a fresh `/contentforge:create-content`. Do NOT silently start a new run.

### Step 2: Reload the saved artifacts

For each completed phase, load the saved file from `phase_artifacts` and put its contents back into context:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py load \
    --brand "{active_brand}" --run-id "{run_id}" --phase 1
# ... repeat for every phase in completed_phases
```

Use the loaded content as the **input** to the next phase that has NOT been checkpointed — do not re-execute earlier phases.

### Step 3: Continue the pipeline from `next_phase`

Hand control to the agent that owns `next_phase` (see `agents/0X-*.md`) and feed it the loaded prior-phase artifacts. After that agent finishes, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py save \
    --brand "{active_brand}" --run-id "{run_id}" \
    --phase {phase_id} --content-file {tmp_output_path} --extension {md|json}
```

Then move to the next remaining phase. Continue until the pipeline finishes Phase 8, at which point:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py finalize \
    --brand "{active_brand}" --run-id "{run_id}" --status completed
```

### Step 4: Surface the resumption summary

Before continuing, tell the user what's being skipped vs re-run:

```
🔁 Resuming run {run_id}
   Topic: {topic}
   Type:  {content_type}
   Brand: {brand}

   ✅ Already completed (skipping): Phase 1 (Research), Phase 2 (Fact Check), Phase 3 (Content Draft)
   ➡️  Resuming from: Phase 3.5 (Visual Assets)
   📋 Remaining: 3.5 → 4 → 5 → 6 → 6.5 → 7 → 8

   Estimated remaining time: ~{minutes} min (based on plugin-tracker benchmarks for {content_type})
```

## Edge cases

- **The user resumes mid-loop.** If a phase failed its quality gate and triggered a loop back to an earlier phase, the checkpoint reflects whatever was last saved. The user should re-run that phase's quality gate after resuming.
- **The user resumes a run that's now ancient.** If `last_updated` is more than 7 days old, warn the user before resuming — sources may have moved, search results have drifted, claims may have been superseded. Offer to start fresh instead.
- **Multiple in-progress runs.** If there are several in-progress runs for the brand, list them with `list` and ask the user which one to resume rather than guessing.
- **No checkpoint manager script.** Older sessions may have been started before v3.12.3. In that case, `checkpoint-manager.py list` returns an empty `runs` array — tell the user no resumable runs exist and offer to start a new pipeline.

## Related

- [`commands/create-content.md`](create-content.md) — the main pipeline this command resumes.
- [`scripts/checkpoint-manager.py`](../scripts/checkpoint-manager.py) — the storage layer.
- [`commands/output-folder.md`](output-folder.md) — open the user-visible `~/Documents/ContentForge/` directory to find finished outputs.
