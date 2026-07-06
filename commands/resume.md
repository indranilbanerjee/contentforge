---
description: Resume a ContentForge pipeline run that was interrupted partway through
argument-hint: "[run-id] (omit to pick the latest in-progress run for the active brand)"
---

# Resume Interrupted Pipeline

Pick up a `/contentforge:create-content` run that stopped before Phase 8 finished — instead of restarting from scratch, load the run manifest and continue from the next phase (or the pending rework target).

## Trigger

User runs `/contentforge:resume` (with optional `run-id` argument). Also surface this command in any error message when a pipeline run terminates abnormally.

## What this fixes

ContentForge's 10-phase pipeline is long-running. If the underlying agent session terminates partway through (context-window exhaustion, network blip, user cancels, machine sleeps), the in-memory Phase 1-N outputs disappear. Every phase that passes its quality gate writes its output to `~/.claude-marketing/{brand-slug}/runs/{run_id}/` via `scripts/checkpoint-manager.py`, so a fresh session can reload those artifacts and skip the phases that already completed.

## Process

### Step 0: Cross-session checkpoint download (Cowork only)

Before listing local runs, check if we're in Cowork+Drive mode — if so, the user might be resuming from a DIFFERENT Cowork session (different sandbox), and the local FS has no record of the run. Pull the run's checkpoint state from Drive first.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/drive-sync-state.py --action read-config
```

If `configured: false` OR `environment != "cowork-sandbox"`, skip to Step 1 (local-mode flow).

If `configured: true` AND a Drive MCP is available:

1. Use the Drive MCP to list contents of `{drive_root_folder_name}/_runs/`
2. For each `<run_id>` subfolder, check if it has phase artifacts (`phase-*.md`, `_manifest.json`, `_sync-pending.json`)
3. Identify in-progress runs (manifest exists but `phase_artifacts` doesn't include `phase 8` — i.e., output-manager hasn't completed)
4. For each in-progress run that doesn't yet exist locally at `~/.claude-marketing/{brand-slug}/runs/{run_id}/`:
   - Use the Drive MCP to download every file from `{drive_root}/_runs/{run_id}/` into the local sandbox path
   - This restores the run's full checkpoint history so Step 2 below can load artifacts normally
5. Tell the user: "Pulled {N} run(s) from Drive for resume eligibility: {run_id list}"

Then proceed to Step 1.

### Step 1: Pick the run to resume

If the user supplied a `run-id`, use it directly. Otherwise list the in-progress runs for the active brand and either auto-pick the most recent or ask the user to choose if there's ambiguity.

```bash
# Auto-pick the most recent in-progress run for the active brand
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}"

# Or with an explicit run id
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py resume --brand "{active_brand}" --run-id "{run_id}"

# List all runs (use when the user wants to choose among several)
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py list --brand "{active_brand}"
```

The `resume` action returns the status of the selected run, including `completed_phases`, `remaining_phases`, `next_phase`, `pending_rework` (if a reviewer-ordered loop was interrupted), the run `meta` (keyword, audience, word-count target, tone), and the absolute paths of every saved artifact.

If there are no in-progress runs, say so and offer to start a fresh `/contentforge:create-content`. Do NOT silently start a new run.

### Step 2: Reload the manifest — then only what the next phase needs

1. **Reload `run.json`** and reconstruct the original-requirements block from it: topic, content type, brand, plus the `meta` fields (**keyword, audience, word-count target, tone**). These are required by downstream phases (Phase 6 needs the keyword; Phase 3 needs the word-count target) — do not proceed without them.
2. **Determine the resumption target:**
   - If `pending_rework` is present, the next step is the **rework target phase** with the stored reviewer feedback — NOT the next un-checkpointed phase. Honor the recorded loop counts (max 2 per edge, 5 total still apply).
   - Otherwise, the next step is `next_phase`.
3. **Load only the artifacts the target phase contractually reads**, per the Pipeline Contract table in [skills/contentforge/SKILL.md](../skills/contentforge/SKILL.md). Pass all other completed-phase artifacts **by path only** — do not reload their contents into context.

```bash
# Example: resuming at Phase 4 — load only its contracted inputs
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py load \
    --brand "{active_brand}" --run-id "{run_id}" --phase 3
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py load \
    --brand "{active_brand}" --run-id "{run_id}" --phase 2
```

Do not re-execute earlier phases, and do not reload every artifact "just in case" — that recreates the context exhaustion that killed the original run.

### Step 3: Continue the pipeline from the resumption target

Re-enter the contentforge skill's **Required Per-Phase Workflow** at the target phase: invoke the phase's qualified subagent (see the Pipeline Contract table for `subagent_type`, inputs, and gate), passing artifact paths + the ≤10-line summary + brand-profile path + requirements block. After the orchestrator verifies the gate:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py save \
    --brand "{active_brand}" --run-id "{run_id}" \
    --phase {phase_id} --content-file {tmp_output_path} --extension {md|json|txt}
```

Then move to the next remaining phase. Continue until the pipeline finishes Phase 8 (Gate 8: .docx generated + Appendices A/B/C present + delivery location verified), at which point:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py finalize \
    --brand "{active_brand}" --run-id "{run_id}" --status completed
```

### Step 4: Surface the resumption summary

Before continuing, tell the user what's being skipped vs re-run:

```
🔁 Resuming run {run_id}
   Topic:   {topic}
   Type:    {content_type}
   Brand:   {brand}
   Keyword: {meta.keyword} | Audience: {meta.audience} | Target: {meta.word_count_target} words

   ✅ Already completed (skipping): Phase 1 (Research), Phase 2 (Fact Check), Phase 3 (Content Draft)
   ➡️  Resuming from: Phase 3.5 (Visual Assets)
   📋 Remaining: 3.5 → 4 → 5 → 6 → 6.5 → 7 → 8
```

If resuming into a `pending_rework`, say so explicitly: "Resuming reviewer-ordered rework of Phase {X} (loop {n}/2): {stored feedback summary}".

## Edge cases

- **The user resumes mid-loop.** If Phase 7 ordered rework before the interruption, `run.json` carries `pending_rework` — resume at the rework target with the stored feedback, then return to Phase 7 for re-review. Loop limits recorded in `run.json` still apply.
- **The user resumes a run that's now ancient.** If `last_updated` is more than 7 days old, warn the user before resuming — sources may have moved, search results have drifted, claims may have been superseded. Offer to start fresh instead.
- **Multiple in-progress runs.** If there are several in-progress runs for the brand, list them with `list` and ask the user which one to resume rather than guessing.
- **Old runs without meta.** Runs checkpointed before meta support have no keyword/audience/tone in `run.json` — ask the user to re-supply them before continuing, and record them going forward.
- **No checkpoint manager state.** If `checkpoint-manager.py list` returns an empty `runs` array, tell the user no resumable runs exist and offer to start a new pipeline.

## Related

- [`commands/create-content.md`](create-content.md) — the wrapper for the pipeline this command resumes.
- [`skills/contentforge/SKILL.md`](../skills/contentforge/SKILL.md) — the Execution Protocol and Pipeline Contract table this command re-enters.
- [`scripts/checkpoint-manager.py`](../scripts/checkpoint-manager.py) — the storage layer.
- [`commands/output-folder.md`](output-folder.md) — open the user-visible `~/Documents/ContentForge/` directory. Finished `.docx` files are dual-copy saved: run directory + `~/Documents/ContentForge/{Brand}/`.
