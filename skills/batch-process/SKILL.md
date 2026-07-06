---
name: batch-process
description: Process multiple content pieces through a prioritized, checkpointed queue with progress tracking and per-piece quality gates
argument-hint: "[sheet-url or topic-list]"
effort: max
---

# Batch Content Processing

Process multiple content requirements through the ContentForge pipeline as a **sequential, checkpointed queue** with priority-based scheduling and event-driven progress tracking. Each piece runs the full 10-phase pipeline (plus Step 0.5) with all 10 quality gates — batch mode changes the intake, not the standards.

## When to Use

Use `/contentforge:batch-process` when:
- You have 2+ content pieces to produce
- You want hands-off production of a whole queue (each piece needs a pre-set title — batch runs are non-interactive)
- You need priority scheduling (urgent pieces first)
- You want per-piece progress visibility and resumability
- You're running agency-scale production (10-50+ pieces)

## What This Command Does

1. **Intake Multiple Requirements** — Read from the brand's tracking backend: local JSON (default), Google Sheets, Airtable, or a CSV file
2. **Build Execution Queue** — Validate rows and sort by priority
3. **Sequential Orchestration** — Run one full ContentForge pipeline per piece, in queue order; every phase of every piece is checkpointed, so an interrupted batch resumes where it stopped
4. **Progress Tracking** — Status table redrawn after each piece/phase event (piece started, gate passed, piece finished)
5. **Error Handling** — Automatic retry for transient failures (resuming from checkpoints), human escalation for persistent issues
6. **Completion Report** — Summary of all pieces: APPROVED, review_required, failed, with quality scores and output locations

## Required Inputs

**Tracking backend** (per brand, via `tracking.backend` in the brand profile — `local` is the default):
- **Local JSON** — requirements managed by `scripts/local-tracker.py`
- **Google Sheets** — sheet with columns: `Requirement ID`, `Content Type`, `Title`, `Target Audience`, `Brand`, `Word Count Target`, `Priority` (1-5), `Status`
- **Airtable** — base with the same fields

**CSV** (alternative intake):
```csv
requirement_id,content_type,title,target_audience,brand,word_count,priority,status
REQ-001,article,AI in Healthcare,Healthcare CIOs,acmemed,2000,1,pending
REQ-002,blog,10 Tips for Remote Teams,HR Managers,techcorp,1500,3,pending
```

**Note:** the `title` column doubles as the `--title` bypass — batch pieces skip interactive title curation and use it verbatim.

## How to Use

### Basic Usage
```
/contentforge:batch-process
```
**Prompt:** "Where are your content requirements? (local queue / Google Sheet URL / Airtable / CSV)"

### With Direct Sheet URL
```
/contentforge:batch-process https://docs.google.com/spreadsheets/d/ABC123/edit
```

### With CSV Upload
```
/contentforge:batch-process batch-requirements.csv
```

## What Happens

### Step 1: Queue Building
- Load all requirements from source
- Validate each row (required fields, brand exists, content type supported, word count within the type's canonical range)
- Sort by priority (1=highest, 5=lowest)
- Display queue summary: total pieces, priority mix, execution order

### Step 2: Sequential Execution
- Run one ContentForge pipeline per piece, front-to-back
- Each pipeline runs the full protocol from `skills/contentforge/SKILL.md` — Step 0 init, title bypass, phases 1–8 with orchestrator-verified gates, per-phase checkpoints
- When one piece finishes (or is escalated), the next starts automatically

### Step 3: Progress Table (event-driven)
Redrawn after each piece/phase event — not on a timer:
```
CONTENTFORGE BATCH — 2/5 complete | 1 review_required | 0 failed
─────────────────────────────────────────────────────────────
▶ REQ-003 | SEO Whitepaper       | Phase 4 (Validation)
✓ REQ-001 | AI in Healthcare     | APPROVED 8.4
✓ REQ-004 | FAQ Product Launch   | APPROVED 7.6
⚠ REQ-002 | Remote Teams Blog    | review_required (6.1)
· REQ-005 | Case Study Acme      | queued
```

### Step 4: Completion Report
- Total pieces processed
- APPROVED count (reviewer composite ≥7.0, industry-adjusted, all dimension minimums met)
- review_required count (5.0-6.9 after loop limits, or <5.0)
- Failed count
- Output locations: `~/Documents/ContentForge/{Brand}/` (+ Drive folder if configured)

## Priority Scheduling

**Priority Levels:**
- **1 (Urgent)**: Processed first, deadline-driven (e.g., press release for tomorrow)
- **2 (High)**: Campaign-critical content
- **3 (Normal)**: Standard blog posts, articles
- **4 (Low)**: Evergreen content, no deadline
- **5 (Backlog)**: Nice-to-have, filler content

## Execution Model

- **Sequential, one piece at a time** — no concurrent pipelines. Shared per-brand state, API rate limits, and context limits make in-session parallelism unsafe; resilience comes from per-phase checkpointing instead.
- Each piece is fully independent (own checkpoint run directory, own quality gates)
- If a piece's pipeline fails, it's retried once (resuming from its checkpoints); if it fails again, it's marked for human review and the queue continues

## Error Handling

### Transient Failures (Auto-Retry)
- API rate limits → the inner pipeline backs off and retries
- Network timeouts → retry
- Source URL temporarily unavailable → Gate 2 re-sourcing loop handles it

### Persistent Failures (Human Escalation)
- Brand profile not found
- Requirement validation fails (missing required fields)
- Reviewer score below the approval threshold after loop limits (2 per edge, 5 total)
- Two consecutive pipeline failures on the same piece

**Success criteria are canonical:** a piece is "completed" ONLY if the reviewer decision is APPROVED (composite ≥7.0 per `config/scoring-thresholds.json`). Scores of 5.0-6.9 are `review_required` — never silently marked complete.

## Requirements

### Backends
- **Local JSON** (default) — no integrations required
- **Google Sheets + Drive** — optional, for sheet intake and Drive delivery
- **Airtable** — optional, for base intake and attachments

### Brand Profiles
- All brands referenced in requirements must have existing profiles
- Use `/contentforge:brand-setup` to create missing brands before batch processing

## Output Structure

Local (always):
```
~/Documents/ContentForge/
└── {Brand}/
    ├── REQ-001_AI-in-Healthcare_v1.0.docx
    ├── REQ-002_Remote-Teams-Blog_v1.0.docx
    └── batch-summary-report.txt
```

Google Drive (if configured):
```
ContentForge Output/
└── {batch_id}/
    ├── Completed/ ...
    ├── Review/ ...
    └── failed-requirements.csv (if any)
```

## Resuming an Interrupted Batch

Batch state lives in the tracking backend plus each piece's checkpoint run directory — both on disk. If the session dies:
1. Re-run `/contentforge:batch-process` — rows already `completed`/`review_required`/`failed` are skipped
2. The in-flight piece resumes from its last gate-passed phase via its checkpoints (see `commands/resume.md`)
3. Remaining `pending` rows queue normally

## Troubleshooting

### "Queue is empty"
- Check the backend has rows with `status=pending`
- Ensure the Sheet URL / base ID is correct and accessible

### "Brand profile not found"
- Run `/contentforge:brand-setup` for missing brands
- Update the requirements source with correct brand names

### "A piece is stuck in Phase X"
- Likely an API rate limit; the inner pipeline auto-throttles and continues
- If the session died, re-run the batch — the piece resumes from its checkpoint

## Example Workflow

(SYNTHETIC EXAMPLE — fabricated for illustration; never reuse these numbers.)

**Scenario:** Agency needs 15 blog posts for 3 clients by end of week

1. **Prepare Requirements**
   - 15 rows (local queue or Google Sheet)
   - Columns: ID, type=blog, title, audience, brand, word_count=1200, priority=2

2. **Run Batch Processing**
   ```
   /contentforge:batch-process https://docs.google.com/spreadsheets/d/ABC123/edit
   ```

3. **Monitor Progress**
   - Status table updates as each piece moves through its phases

4. **Review Outputs**
   - 14/15 APPROVED (scores 7.4-9.1)
   - 1/15 review_required (6.2, citation issues) — feedback stored in its `phase-7-review.json`

5. **Quality Check**
   - Spot-check 3 random pieces
   - Fix the one flagged for review

6. **Deliver to Clients**
   - All approved pieces in `~/Documents/ContentForge/{Brand}/`

## Integration with Other Skills

- **Before Batch**: `/contentforge:brand-setup` for new brands
- **During Batch**: status table auto-updates on events
- **After Batch**: use outputs directly or run `/contentforge:content-refresh` for updates

## Limitations

- Sequential execution — one pipeline at a time (throughput comes from checkpointed resume, not concurrency)
- All pieces must use existing brand profiles (no on-the-fly creation)
- Every requirement needs a title (batch runs are non-interactive)
- Backends: local JSON (default), Google Sheets, or Airtable

## Agent Used

- **Batch Orchestrator Agent** — see `agents/09-batch-orchestrator.md`

## Related Skills

- `/contentforge:brand-setup` — Create brand profiles
- `/contentforge:content-refresh` — Update existing content
- `/contentforge:cf-variants` — A/B test variations
