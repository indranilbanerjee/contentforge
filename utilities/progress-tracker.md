# Utility: Progress Tracker

**Purpose:** Real-time dashboard for monitoring batch content processing with live updates every 30 seconds.

---

## Responsibilities

1. **Track Pipeline States** — Monitor each active pipeline's current phase
2. **Calculate ETAs** — Dynamic time-remaining estimates based on progress
3. **Display Dashboard** — ASCII-formatted real-time status view
4. **Log Milestones** — Record phase completions, quality scores, errors
5. **Performance Metrics** — Track throughput, average time per piece, quality trends

---

## Dashboard Format

### Full Dashboard (Live Display)
```
╔═════════════════════════════════════════════════════════════════╗
║ ContentForge Batch Processing Dashboard                        ║
║ Batch ID: Batch_2026-02-17_14-30-15                            ║
║ Started: 2:30 PM | Elapsed: 42 minutes                         ║
╠═════════════════════════════════════════════════════════════════╣
║ Summary                                                         ║
║ Total: 12 pieces | Running: 3 | Completed: 7 | Failed: 0       ║
║ Queue: 2 pending | Estimated Completion: 18 minutes            ║
║ Average Quality Score: 8.9 / 10 (from 7 completed)             ║
╠═════════════════════════════════════════════════════════════════╣
║ Active Pipelines (Running Now)                                 ║
║ ┌─────────────────────────────────────────────────────────────┐ ║
║ │ REQ-010 | Article Remote Work | Phase 6.5 → | Est: 8min    │ ║
║ │ Progress: ████████████████░░░░  (Phase 6.5/9 = 72%)        │ ║
║ │ Status: Humanizing content (removing AI patterns)           │ ║
║ └─────────────────────────────────────────────────────────────┘ ║
║ ┌─────────────────────────────────────────────────────────────┐ ║
║ │ REQ-011 | Blog SEO Trends    | Phase 4  →  | Est: 14min    │ ║
║ │ Progress: ██████████░░░░░░░░  (Phase 4/9 = 44%)            │ ║
║ │ Status: Scientific validation (checking for hallucinations) │ ║
║ └─────────────────────────────────────────────────────────────┘ ║
║ ┌─────────────────────────────────────────────────────────────┐ ║
║ │ REQ-012 | Whitepaper AI      | Phase 2  →  | Est: 28min    │ ║
║ │ Progress: ████░░░░░░░░░░░░░░  (Phase 2/9 = 22%)            │ ║
║ │ Status: Fact-checking sources (12/20 URLs verified)         │ ║
║ └─────────────────────────────────────────────────────────────┘ ║
╠═════════════════════════════════════════════════════════════════╣
║ Completed (Latest 5)                                            ║
║ ✓ REQ-009 | Blog Marketing Tips    | Done 3m ago | Score: 9.1 ║
║ ✓ REQ-008 | Article Data Privacy   | Done 8m ago | Score: 8.7 ║
║ ✓ REQ-007 | FAQ Product Launch     | Done 12m ago | Score: 8.5║
║ ✓ REQ-006 | Article Customer Story | Done 18m ago | Score: 9.3║
║ ✓ REQ-005 | Blog Content Calendar  | Done 22m ago | Score: 8.8║
╠═════════════════════════════════════════════════════════════════╣
║ Queue (Next 2)                                                  ║
║ ⏸ REQ-013 | Article AI Ethics      | Priority 2 | Est: 24min  ║
║ ⏸ REQ-014 | Blog Email Strategy    | Priority 3 | Est: 19min  ║
╠═════════════════════════════════════════════════════════════════╣
║ Performance Stats                                               ║
║ Throughput: 0.17 pieces/min (10.2 pieces/hour with concurrency)║
║ Avg Time per Piece: 23.4 minutes                               ║
║ Speedup vs Sequential: 4.2x faster                             ║
╚═════════════════════════════════════════════════════════════════╝

Last updated: 3:12 PM (auto-refresh every 30s)
Press Ctrl+C to stop monitoring (batch will continue in background)
```

---

## Data Structure

### Pipeline State Tracking
```python
pipeline_state = {
    'requirement_id': 'REQ-010',
    'title': 'Article Remote Work',
    'content_type': 'article',
    'brand': 'TechCorp',
    'status': 'in_progress',
    'current_phase': 6.5,  # Can be 1, 2, 3, 4, 5, 6, 6.5, 7, 8
    'phase_details': 'Humanizing content (removing AI patterns)',
    'start_time': '2026-02-17T14:30:15',
    'estimated_completion_time': '2026-02-17T14:38:15',  # 8 min from now
    'elapsed_time_minutes': 14,
    'estimated_remaining_minutes': 8,
    'progress_percentage': 72,  # Phase 6.5/9 * 100
    'quality_score': None,  # Filled after Phase 7
    'loops_used': 1,  # Feedback loops so far
    'errors': []
}
```

### Batch State Tracking
```python
batch_state = {
    'batch_id': 'Batch_2026-02-17_14-30-15',
    'start_time': '2026-02-17T14:30:15',
    'source': 'https://docs.google.com/spreadsheets/d/ABC123',
    'total_pieces': 12,
    'active_pipelines': [pipeline_state_1, pipeline_state_2, pipeline_state_3],
    'completed': [completed_1, completed_2, ...],  # 7 pieces
    'failed': [],
    'queue': [queued_1, queued_2],  # 2 pieces
    'validation_errors': [],
    'average_quality_score': 8.9,
    'total_elapsed_minutes': 42,
    'estimated_remaining_minutes': 18,
    'estimated_completion_time': '2026-02-17T15:12:15'
}
```

---

## Phase Progress Calculation

### Phase Weights (for % completion)
```python
phase_weights = {
    1: 0.15,  # Research: 15% of total time
    2: 0.12,  # Fact-checking: 12%
    3: 0.18,  # Drafting: 18% (heaviest)
    4: 0.08,  # Scientific validation: 8%
    5: 0.10,  # Structuring & proofreading: 10%
    6: 0.12,  # SEO/GEO optimization: 12%
    6.5: 0.08,  # Humanizer: 8%
    7: 0.10,  # Reviewer: 10%
    8: 0.07   # Output manager: 7%
}

def calculate_progress_percentage(current_phase):
    """Calculate how much of the pipeline is complete."""
    completed_weight = sum([
        phase_weights[p] for p in phase_weights.keys()
        if p < current_phase
    ])
    return round(completed_weight * 100)

# Example:
# If current_phase = 6.5:
# Completed phases: 1, 2, 3, 4, 5, 6
# Weight: 0.15 + 0.12 + 0.18 + 0.08 + 0.10 + 0.12 = 0.75 = 75%
```

### Visual Progress Bar
```python
def render_progress_bar(percentage, width=20):
    """Render ASCII progress bar."""
    filled = int(width * (percentage / 100))
    empty = width - filled
    return f"{'█' * filled}{'░' * empty}  ({percentage}%)"

# Example:
# 72% → "██████████████░░░░░░  (72%)"
```

---

## ETA Calculation

### Dynamic Time Estimation
```python
def calculate_eta(pipeline_state, phase_times):
    """Calculate estimated time remaining for a pipeline."""

    current_phase = pipeline_state['current_phase']
    elapsed = pipeline_state['elapsed_time_minutes']

    # Remaining phases
    remaining_phases = [p for p in phase_times.keys() if p > current_phase]

    # Estimated time for remaining phases
    estimated_remaining = sum([phase_times[p] for p in remaining_phases])

    # Adjust based on actual elapsed time vs. expected
    expected_elapsed = sum([phase_times[p] for p in phase_times.keys() if p < current_phase])

    if expected_elapsed > 0:
        pace_multiplier = elapsed / expected_elapsed
        estimated_remaining *= pace_multiplier

    return round(estimated_remaining)

# Example:
# Article, Phase 6.5 complete
# Expected elapsed for Phases 1-6: 18 min
# Actual elapsed: 14 min (faster than expected!)
# Pace multiplier: 14/18 = 0.78 (22% faster)
# Remaining phases (7, 8): expected 4 min
# Adjusted: 4 * 0.78 = 3.1 min → "Est: 3min"
```

### Batch-Level ETA
```python
def calculate_batch_eta(batch_state):
    """Calculate when entire batch will complete."""

    # Time remaining for active pipelines
    active_max_time = max([p['estimated_remaining_minutes'] for p in batch_state['active_pipelines']])

    # Time for queued pieces (will start as actives finish)
    queue_time = sum([p['estimated_time'] for p in batch_state['queue']]) / len(batch_state['active_pipelines'])

    total_remaining = active_max_time + queue_time

    completion_time = datetime.now() + timedelta(minutes=total_remaining)

    return total_remaining, completion_time
```

---

## Update Frequency

### Real-Time Updates
- **Phase Changes**: Immediate update when pipeline moves to next phase
- **Quality Scores**: Immediate update when Phase 7 completes
- **Completions**: Immediate when Phase 8 finishes
- **Errors**: Immediate when pipeline encounters error

### Dashboard Refresh
- **Every 30 seconds**: Re-render full dashboard with updated ETAs
- **Every 2 minutes**: Recalculate batch-level ETA (accounts for pace changes)

### Logging
```python
# Log all events to batch-progress-log.txt
def log_event(batch_id, event_type, details):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(f'{batch_id}-progress.log', 'a') as f:
        f.write(f"[{timestamp}] {event_type}: {details}\n")

# Example events:
# [2026-02-17 14:30:15] BATCH_START: 12 pieces, Priority range 1-3
# [2026-02-17 14:32:40] PHASE_COMPLETE: REQ-001 completed Phase 1 (Research)
# [2026-02-17 14:45:20] QUALITY_SCORE: REQ-005 scored 8.8/10
# [2026-02-17 14:46:00] PIPELINE_COMPLETE: REQ-005 finished in 24min
# [2026-02-17 14:46:05] PIPELINE_START: REQ-008 started (from queue)
```

---

## Status Messages by Phase

### Detailed Phase Status
```python
phase_status_messages = {
    1: "Researching topic (SERP analysis, source mining)",
    2: "Fact-checking sources ({verified}/{total} URLs verified)",
    3: "Drafting content ({current_words}/{target_words} words)",
    4: "Scientific validation (checking for hallucinations)",
    5: "Structuring & proofreading (grammar, readability)",
    6: "SEO/GEO optimization (keyword density: {kw_density}%)",
    6.5: "Humanizing content (removing AI patterns)",
    7: "Reviewing quality (scoring 5 dimensions)",
    8: "Generating output (.docx file, uploading to Drive)"
}

def get_phase_status(pipeline_state):
    """Get human-readable status message for current phase."""
    phase = pipeline_state['current_phase']
    message = phase_status_messages[phase]

    # Fill in dynamic placeholders
    if phase == 2 and 'urls_verified' in pipeline_state:
        message = message.format(
            verified=pipeline_state['urls_verified'],
            total=pipeline_state['total_urls']
        )
    elif phase == 3 and 'current_word_count' in pipeline_state:
        message = message.format(
            current_words=pipeline_state['current_word_count'],
            target_words=pipeline_state['target_word_count']
        )
    elif phase == 6 and 'keyword_density' in pipeline_state:
        message = message.format(
            kw_density=round(pipeline_state['keyword_density'], 2)
        )

    return message
```

---

## Performance Metrics

### Throughput Calculation
```python
def calculate_throughput(batch_state):
    """Calculate pieces per minute and per hour."""
    completed_count = len(batch_state['completed'])
    elapsed_minutes = batch_state['total_elapsed_minutes']

    if elapsed_minutes == 0:
        return 0, 0

    pieces_per_minute = completed_count / elapsed_minutes
    pieces_per_hour = pieces_per_minute * 60

    return round(pieces_per_minute, 2), round(pieces_per_hour, 1)

# Example:
# 7 pieces completed in 42 minutes
# = 0.17 pieces/min
# = 10.2 pieces/hour (with 5 concurrent)
```

### Average Time per Piece
```python
def calculate_avg_time(batch_state):
    """Average completion time across finished pieces."""
    completed = batch_state['completed']

    if not completed:
        return 0

    total_time = sum([p['elapsed_time_minutes'] for p in completed])
    avg = total_time / len(completed)

    return round(avg, 1)
```

### Speedup vs. Sequential
```python
def calculate_speedup(batch_state):
    """How much faster is batch vs sequential processing?"""
    avg_time = calculate_avg_time(batch_state)
    total_pieces = batch_state['total_pieces']
    concurrency = len(batch_state['active_pipelines'])

    sequential_time = avg_time * total_pieces
    parallel_time = batch_state['estimated_completion_time'] - batch_state['start_time']

    speedup = sequential_time / parallel_time
    return round(speedup, 1)
```

---

## Dashboard Rendering

### ASCII Art Header
```python
def render_header(batch_state):
    print("╔" + "═" * 65 + "╗")
    print("║ ContentForge Batch Processing Dashboard" + " " * 24 + "║")
    print(f"║ Batch ID: {batch_state['batch_id']:<52} ║")

    start_time = format_time(batch_state['start_time'])
    elapsed = batch_state['total_elapsed_minutes']

    print(f"║ Started: {start_time} | Elapsed: {elapsed} minutes{' ' * (65 - 35 - len(str(elapsed)))}║")
    print("╠" + "═" * 65 + "╣")
```

### Active Pipelines Section
```python
def render_active_pipelines(active_pipelines):
    print("║ Active Pipelines (Running Now)" + " " * 34 + "║")

    for pipeline in active_pipelines:
        req_id = pipeline['requirement_id']
        title = pipeline['title'][:20]  # Truncate long titles
        phase = pipeline['current_phase']
        eta = pipeline['estimated_remaining_minutes']

        print("║ ┌" + "─" * 61 + "┐ ║")
        print(f"║ │ {req_id} | {title:<22} | Phase {phase:<4} → | Est: {eta}min{' ' * (61 - 40 - len(str(eta)))} │ ║")

        # Progress bar
        progress_pct = pipeline['progress_percentage']
        progress_bar = render_progress_bar(progress_pct, width=20)
        print(f"║ │ Progress: {progress_bar:<44} │ ║")

        # Status message
        status = get_phase_status(pipeline)[:55]  # Truncate
        print(f"║ │ Status: {status:<54} │ ║")
        print("║ └" + "─" * 61 + "┘ ║")
```

---

## Error Highlighting

### Failed Pipelines
```python
if batch_state['failed']:
    print("╠" + "═" * 65 + "╣")
    print("║ ❌ Failed Pipelines" + " " * 45 + "║")

    for failed in batch_state['failed']:
        req_id = failed['requirement_id']
        error = failed['error'][:50]  # Truncate error message
        print(f"║ ✗ {req_id} | {error:<50} ║")
        print(f"║   Action: {failed['recovery_action']:<52} ║")
```

---

## Integration with Batch Orchestrator

**Batch Orchestrator uses this utility:**

1. **Initialize Dashboard**
   ```python
   progress_tracker.init_dashboard(batch_id, total_pieces)
   ```

2. **Update Pipeline State**
   ```python
   progress_tracker.update_pipeline(
       req_id='REQ-010',
       current_phase=6.5,
       phase_details='Humanizing content',
       estimated_remaining_minutes=8
   )
   ```

3. **Mark Complete**
   ```python
   progress_tracker.mark_complete(
       req_id='REQ-010',
       quality_score=9.2,
       elapsed_time=24
   )
   ```

4. **Render Dashboard** (every 30s)
   ```python
   progress_tracker.render()
   ```

---

## Export Options

### Progress Snapshot (JSON)
```python
# Save current state to JSON for external monitoring
progress_tracker.export_json(f'{batch_id}-snapshot.json')
```

### CSV Export (for spreadsheets)
```python
# Export completed pieces to CSV
progress_tracker.export_csv(f'{batch_id}-completed.csv')
```

---

## Performance Targets

- **Dashboard Render Time**: <100ms
- **State Update**: <10ms per pipeline
- **Memory Usage**: <50MB for batch of 100 pieces

---

## Version History

- **v2.0.0**: Initial real-time dashboard with 30s refresh
- Future: Web-based dashboard (HTML/CSS), Slack/Teams notifications

---

**The progress tracker turns batch processing from a black box into a transparent, confidence-inspiring experience** — users see exactly what's happening in real-time.
