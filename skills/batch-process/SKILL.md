---
name: batch-process
description: Process multiple content pieces in parallel with queue management, priority scheduling, and progress tracking
skill_type: command
---

# Batch Content Processing

Process multiple content requirements simultaneously through the ContentForge pipeline with intelligent queue management, priority-based scheduling, and real-time progress tracking.

## When to Use

Use `/batch-process` when:
- You have 2+ content pieces to produce
- You want to maximize throughput with parallel execution
- You need priority scheduling (urgent pieces first)
- You want real-time progress visibility
- You're running agency-scale production (10-50+ pieces)

## What This Command Does

1. **Intake Multiple Requirements** — Read from Google Sheets or CSV with multiple rows
2. **Build Execution Queue** — Create prioritized queue with estimated completion times
3. **Parallel Orchestration** — Launch multiple ContentForge pipelines simultaneously (max 5 concurrent)
4. **Progress Tracking** — Real-time dashboard showing status of each piece (phase completion, quality scores, ETA)
5. **Error Handling** — Automatic retry for transient failures, human escalation for persistent issues
6. **Completion Report** — Summary of all pieces (successes, failures, quality scores, total time)

## Required Inputs

**Google Sheets** (Recommended):
- Sheet with columns: `Requirement ID`, `Content Type`, `Title/Topic`, `Target Audience`, `Brand`, `Word Count Target`, `Priority` (1-5), `Status`
- Each row = one content piece
- Example sheet: [ContentForge Batch Template](https://docs.google.com/spreadsheets/d/your-template)

**CSV** (Alternative):
```csv
requirement_id,content_type,title,target_audience,brand,word_count,priority,status
REQ-001,article,AI in Healthcare 2026,Healthcare CIOs,AcmeMed,2000,1,pending
REQ-002,blog,10 Tips for Remote Teams,HR Managers,TechCorp,1500,3,pending
```

## How to Use

### Basic Usage
```
/batch-process
```
**Prompt:** "Which Google Sheet contains your content requirements?"

### With Direct Sheet URL
```
/batch-process https://docs.google.com/spreadsheets/d/ABC123/edit
```

### With CSV Upload
```
/batch-process batch-requirements.csv
```

## What Happens

### Step 1: Queue Building (1-2 minutes)
- Load all requirements from source
- Validate each row (required fields, brand exists, content type supported)
- Calculate estimated time per piece based on content type and word count
- Sort by priority (1=highest, 5=lowest)
- Display queue summary: Total pieces, estimated total time, concurrent execution plan

### Step 2: Parallel Execution (20-30 min per piece, up to 5 concurrent)
- Launch up to 5 ContentForge pipelines simultaneously
- Each pipeline runs full 9-phase process independently
- Progress tracker updates in real-time
- When one completes, next in queue starts automatically

### Step 3: Progress Dashboard (Live Updates)
```
╔═════════════════════════════════════════════════════════════════╗
║ ContentForge Batch Processing Dashboard                        ║
║ Total: 12 pieces | Running: 5 | Completed: 4 | Failed: 0       ║
║ Estimated Completion: 45 minutes                                ║
╠═════════════════════════════════════════════════════════════════╣
║ REQ-001 | AI in Healthcare    | Phase 7  ✓ | Score: 9.2 | 2min ║
║ REQ-002 | Remote Teams Blog   | Phase 4  → | Est: 18min         ║
║ REQ-003 | SEO Whitepaper      | Phase 2  → | Est: 42min         ║
║ REQ-004 | FAQ Product Launch  | Completed ✓ | Score: 8.8        ║
║ REQ-005 | Case Study Acme     | Phase 6.5→ | Est: 8min          ║
╚═════════════════════════════════════════════════════════════════╝
```

### Step 4: Completion Report
- Total pieces processed: X
- Successful completions: Y (Z%)
- Human review required: N pieces (scores <5.0)
- Average quality score: 8.7/10
- Total processing time: HH:MM
- Output locations: [Google Drive folder link]

## Priority Scheduling

**Priority Levels:**
- **1 (Urgent)**: Processed first, deadline-driven (e.g., press release for tomorrow)
- **2 (High)**: Campaign-critical content
- **3 (Normal)**: Standard blog posts, articles
- **4 (Low)**: Evergreen content, no deadline
- **5 (Backlog)**: Nice-to-have, filler content

## Concurrency Limits

- **Max 5 concurrent pipelines** (prevents resource exhaustion, API rate limits)
- Each pipeline is fully independent (no shared state)
- If piece fails, it's retried once; if fails again, marked for human review

## Error Handling

### Transient Failures (Auto-Retry)
- API rate limits → wait 60s, retry
- Network timeouts → retry immediately
- Source URL temporarily unavailable → retry with alternate sources

### Persistent Failures (Human Escalation)
- Brand profile not found
- Requirement validation fails (missing required fields)
- Quality score <3.0 after max loops (2 attempts)
- Two consecutive pipeline failures

## Requirements

### MCP Integrations
- ✅ **Google Sheets** — Requirement intake
- ✅ **Google Drive** — Output storage

### Brand Profiles
- All brands referenced in requirements must have existing profiles
- Use `/brand-setup` to create missing brands before batch processing

## Output Structure

All outputs organized in Google Drive:
```
ContentForge Output/
└── Batch_2026-02-17_14-30/
    ├── REQ-001_AI-in-Healthcare_v1.0.docx
    ├── REQ-002_Remote-Teams-Blog_v1.0.docx
    ├── REQ-003_SEO-Whitepaper_v1.0.docx
    ├── batch-summary-report.txt
    └── failed-requirements.csv (if any)
```

## Performance Metrics

**Typical Batch Run (12 pieces):**
- Sequential (v1.0): ~240-360 minutes (4-6 hours)
- Parallel (v2.0): ~60-90 minutes (1-1.5 hours)
- **Speedup: 4-5x faster**

## Troubleshooting

### "Queue is empty"
- Check Google Sheet has rows with `status=pending`
- Ensure Sheet URL is correct and accessible

### "Max concurrency reached"
- Wait for one pipeline to complete
- Current limit is 5 concurrent (can't be increased)

### "Brand profile not found"
- Run `/brand-setup [brand-name]` for missing brands
- Update requirements sheet with correct brand names

### "Multiple pieces stuck in Phase X"
- Likely API rate limit across all pipelines
- System will auto-throttle and continue
- Check API quotas (web_search, Drive API)

## Example Workflow

**Scenario:** Agency needs 15 blog posts for 3 clients by end of week

1. **Prepare Requirements Sheet**
   - 15 rows in Google Sheet
   - Columns: ID, type=blog, title, audience, brand, word_count=1200, priority=2

2. **Run Batch Processing**
   ```
   /batch-process https://docs.google.com/spreadsheets/d/ABC123/edit
   ```

3. **Monitor Progress**
   - Dashboard shows 5 running, 0 completed
   - Estimated completion: 90 minutes

4. **Review Outputs**
   - 14/15 completed successfully (scores 8.5-9.5)
   - 1/15 requires human review (score 4.8, citation issues)

5. **Quality Check**
   - Spot-check 3 random pieces
   - Fix the one flagged for review

6. **Deliver to Clients**
   - All 15 pieces delivered in 2 hours vs. 6 hours sequential

## Integration with Other Skills

- **Before Batch**: `/brand-setup` for new brands
- **During Batch**: Progress tracker auto-updates
- **After Batch**: Use outputs directly or run `/content-refresh` for updates

## Limitations (v2.0)

- Max 5 concurrent pipelines (more can overwhelm APIs)
- All pieces must use existing brand profiles (no on-the-fly creation)
- Google Sheets or CSV only (no Notion, Airtable yet — coming in v2.1)

## Agent Used

- **Batch Orchestrator Agent** (new in v2.0) — see `agents/09-batch-orchestrator.md`

## Related Skills

- `/brand-setup` — Create brand profiles
- `/content-refresh` — Update existing content
- `/generate-variants` — A/B test variations

---

**Version:** 2.0.0
**Agent:** Batch Orchestrator
**Utilities:** batch-queue-manager.md, progress-tracker.md
