# Utility: Batch Queue Manager

**Purpose:** Build, sort, and manage the execution queue for batch content processing.

---

## Responsibilities

1. **Load Requirements** — Read from Google Sheets or CSV
2. **Validate Entries** — Check required fields, brand existence, content type support
3. **Priority Sorting** — Order queue by priority, then estimated time
4. **Time Estimation** — Calculate per-piece and total batch completion times
5. **Concurrency Planning** — Determine which pieces start immediately vs. wait in queue

---

## Input Format

### Google Sheets (Recommended)
**Required Columns:**
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| requirement_id | string | Unique identifier | REQ-001 |
| content_type | enum | article, blog, whitepaper, faq, research_paper | article |
| title | string | Content topic/title | "AI in Healthcare 2026" |
| target_audience | string | Who this is for | "Healthcare CIOs" |
| brand | string | Brand profile name (must exist) | "AcmeMed" |
| word_count | integer | Target word count | 2000 |
| priority | integer | 1-5 (1=highest) | 1 |
| status | enum | pending, in_progress, completed, failed, review_required | pending |

**Optional Columns:**
- `deadline` (ISO date): For priority tie-breaking
- `notes` (string): Special instructions
- `assigned_to` (string): Team member (agency use)

### CSV Alternative
```csv
requirement_id,content_type,title,target_audience,brand,word_count,priority,status
REQ-001,article,AI in Healthcare 2026,Healthcare CIOs,AcmeMed,2000,1,pending
REQ-002,blog,10 Remote Team Tips,HR Managers,TechCorp,1500,3,pending
REQ-003,whitepaper,Future of SEO,Marketing Directors,AgencyCo,4000,2,pending
```

---

## Validation Rules

### Required Field Checks
```python
required_fields = [
    'requirement_id',
    'content_type',
    'title',
    'target_audience',
    'brand',
    'word_count',
    'priority',
    'status'
]

for field in required_fields:
    if not row[field] or row[field].strip() == '':
        validation_errors.append(f"{row['requirement_id']}: Missing {field}")
```

### Content Type Validation
```python
valid_content_types = ['article', 'blog', 'whitepaper', 'faq', 'research_paper']

if row['content_type'] not in valid_content_types:
    validation_errors.append(
        f"{row['requirement_id']}: Invalid content_type '{row['content_type']}'. "
        f"Must be one of: {', '.join(valid_content_types)}"
    )
```

### Brand Profile Validation
```python
# Check if brand profile exists in Google Drive
brand_profile_path = f"ContentForge/{row['brand']}-profile-cache.json"

if not drive_file_exists(brand_profile_path):
    validation_errors.append(
        f"{row['requirement_id']}: Brand '{row['brand']}' profile not found. "
        f"Run /brand-setup {row['brand']} first."
    )
```

### Word Count Validation
```python
word_count_ranges = {
    'article': (1500, 2000),
    'blog': (800, 1500),
    'whitepaper': (2500, 5000),
    'faq': (600, 1200),
    'research_paper': (4000, 8000)
}

min_wc, max_wc = word_count_ranges[row['content_type']]

if not (min_wc <= row['word_count'] <= max_wc):
    validation_errors.append(
        f"{row['requirement_id']}: Word count {row['word_count']} out of range "
        f"for {row['content_type']} ({min_wc}-{max_wc})"
    )
```

### Priority Validation
```python
if not (1 <= row['priority'] <= 5):
    validation_errors.append(
        f"{row['requirement_id']}: Priority must be 1-5, got {row['priority']}"
    )
```

### Status Filter
```python
# Only process rows with status='pending'
if row['status'] != 'pending':
    skipped.append(
        f"{row['requirement_id']}: Skipped (status={row['status']})"
    )
```

---

## Time Estimation Logic

### Base Processing Times (minutes)
```python
base_times = {
    'article': {
        'min': 22,
        'max': 28,
        'typical': 25
    },
    'blog': {
        'min': 15,
        'max': 22,
        'typical': 18
    },
    'whitepaper': {
        'min': 30,
        'max': 45,
        'typical': 35
    },
    'faq': {
        'min': 12,
        'max': 18,
        'typical': 15
    },
    'research_paper': {
        'min': 45,
        'max': 75,
        'typical': 60
    }
}
```

### Adjustments
```python
def estimate_time(row, brand_cache_status):
    """Calculate estimated processing time for a single piece."""

    base = base_times[row['content_type']]['typical']

    # Adjustment 1: Brand cache
    if brand_cache_status[row['brand']] == 'cold':
        base *= 1.20  # +20% for first-time brand use
    elif brand_cache_status[row['brand']] == 'warm':
        base *= 0.90  # -10% for cached brand

    # Adjustment 2: Word count deviation
    typical_word_count = {
        'article': 1750,
        'blog': 1200,
        'whitepaper': 3500,
        'faq': 900,
        'research_paper': 6000
    }

    wc_ratio = row['word_count'] / typical_word_count[row['content_type']]
    base *= wc_ratio

    # Adjustment 3: High-citation types
    if row['content_type'] in ['whitepaper', 'research_paper']:
        base *= 1.10  # +10% for heavy citation work

    return round(base)
```

### Batch Total Time
```python
def estimate_batch_time(queue, concurrency=5):
    """Calculate total batch completion time with parallel execution."""

    if len(queue) <= concurrency:
        # All pieces can run in parallel
        return max([piece['estimated_time'] for piece in queue])
    else:
        # First wave: longest N pieces (N=concurrency)
        first_wave = sorted(queue, key=lambda x: x['estimated_time'], reverse=True)[:concurrency]
        longest_first_wave = max([p['estimated_time'] for p in first_wave])

        # Remaining pieces
        remaining = queue[concurrency:]
        total_remaining_time = sum([p['estimated_time'] for p in remaining])
        avg_remaining_time = total_remaining_time / concurrency

        return round(longest_first_wave + avg_remaining_time)
```

---

## Priority Sorting Algorithm

### Step 1: Group by Priority
```python
priority_groups = {1: [], 2: [], 3: [], 4: [], 5: []}

for piece in validated_queue:
    priority_groups[piece['priority']].append(piece)
```

### Step 2: Sort Within Priority by Estimated Time (Descending)
```python
# Longest pieces first within each priority group
# Rationale: Start long-running pieces early for better parallelization

for priority in priority_groups:
    priority_groups[priority].sort(
        key=lambda x: x['estimated_time'],
        reverse=True  # Descending: longest first
    )
```

### Step 3: Flatten to Final Queue
```python
final_queue = []

for priority in [1, 2, 3, 4, 5]:  # Process priorities in order
    final_queue.extend(priority_groups[priority])
```

### Example Queue After Sorting

**Input (unsorted):**
| ID | Priority | Type | Est. Time |
|----|----------|------|-----------|
| REQ-001 | 2 | article | 25min |
| REQ-002 | 1 | whitepaper | 35min |
| REQ-003 | 3 | blog | 18min |
| REQ-004 | 1 | article | 22min |
| REQ-005 | 2 | blog | 20min |

**Output (sorted):**
| Position | ID | Priority | Type | Est. Time | Reason |
|----------|----|----|------|-----------|--------|
| 1 | REQ-002 | 1 | whitepaper | 35min | Priority 1, longest |
| 2 | REQ-004 | 1 | article | 22min | Priority 1, shorter |
| 3 | REQ-001 | 2 | article | 25min | Priority 2, longer |
| 4 | REQ-005 | 2 | blog | 20min | Priority 2, shorter |
| 5 | REQ-003 | 3 | blog | 18min | Priority 3 |

---

## Concurrency Planning

### Determine Initial Wave
```python
def plan_execution_waves(queue, concurrency=5):
    """Divide queue into waves for parallel execution."""

    waves = []

    for i in range(0, len(queue), concurrency):
        wave = queue[i:i+concurrency]
        waves.append(wave)

    return waves

# Example:
# 12 pieces, concurrency=5
# Wave 1: REQ-002, REQ-004, REQ-001, REQ-005, REQ-003 (5 pieces)
# Wave 2: REQ-006, REQ-007, REQ-008, REQ-009, REQ-010 (5 pieces)
# Wave 3: REQ-011, REQ-012 (2 pieces)
```

### Dynamic Wave Management
- As pieces in Wave 1 complete, start pieces from Wave 2
- Maintain exactly 5 active pipelines at all times (until queue exhausted)
- No pre-defined waves — continuous queue consumption

---

## Output: Queue Summary

### Console Display
```
╔═══════════════════════════════════════════════════════════════╗
║ Batch Queue Summary                                           ║
╠═══════════════════════════════════════════════════════════════╣
║ Source: Google Sheets - ContentRequirements                   ║
║ Total Rows: 15                                                ║
║ Valid: 12 | Skipped: 2 | Validation Errors: 1                 ║
╠═══════════════════════════════════════════════════════════════╣
║ Queue Breakdown:                                              ║
║   Priority 1: 3 pieces (Est: 82 min total)                    ║
║   Priority 2: 5 pieces (Est: 122 min total)                   ║
║   Priority 3: 4 pieces (Est: 68 min total)                    ║
╠═══════════════════════════════════════════════════════════════╣
║ Execution Plan:                                               ║
║   Max Concurrency: 5 pipelines                                ║
║   First Wave: REQ-002, REQ-004, REQ-001, REQ-005, REQ-003     ║
║   Estimated Total Time: 68 minutes (~1.1 hours)               ║
║   vs. Sequential: 272 minutes (~4.5 hours)                    ║
║   Speedup: 4.0x faster                                        ║
╠═══════════════════════════════════════════════════════════════╣
║ Validation Issues:                                            ║
║   ⚠ REQ-013: Brand 'NewStartup' profile not found             ║
║      Action: Run /brand-setup NewStartup, then retry          ║
╠═══════════════════════════════════════════════════════════════╣
║ Skipped (non-pending status):                                ║
║   ℹ REQ-014: Already completed (status=completed)             ║
║   ℹ REQ-015: Currently running (status=in_progress)           ║
╚═══════════════════════════════════════════════════════════════╝

Ready to start batch processing? (yes/no)
```

---

## Error Handling

### Missing Brand Profile
```python
# Save failed requirements for user to fix
failed_requirements = []

for error in validation_errors:
    if 'Brand' in error and 'not found' in error:
        req_id = error.split(':')[0]
        failed_requirements.append({
            'requirement_id': req_id,
            'error': error,
            'action_required': 'Create brand profile with /brand-setup'
        })

# Export to CSV
save_csv('failed-requirements.csv', failed_requirements)
```

### Invalid Data
```python
# Log validation errors, don't halt batch
# User can fix and resubmit invalid rows later

with open('batch-validation-log.txt', 'w') as f:
    f.write("Batch Validation Report\n")
    f.write(f"Timestamp: {datetime.now()}\n\n")
    f.write(f"Total Rows: {total_rows}\n")
    f.write(f"Valid: {valid_count}\n")
    f.write(f"Invalid: {len(validation_errors)}\n\n")

    f.write("Errors:\n")
    for error in validation_errors:
        f.write(f"  - {error}\n")
```

---

## Integration with Batch Orchestrator

**Batch Orchestrator calls this utility:**
1. **Queue Building Phase**
   ```python
   queue = batch_queue_manager.build_queue(source_url)
   # Returns: validated, sorted queue with time estimates
   ```

2. **Execution Planning**
   ```python
   waves = batch_queue_manager.plan_waves(queue, concurrency=5)
   total_time = batch_queue_manager.estimate_batch_time(queue)
   ```

3. **Error Reporting**
   ```python
   if queue.validation_errors:
       save_failed_requirements_csv(queue.validation_errors)
       alert_user("1 requirement failed validation. See failed-requirements.csv")
   ```

---

## Performance Targets

- **Validation Speed**: <5 seconds for 100 rows
- **Sorting Speed**: <1 second for 100 rows
- **Queue Build Total**: <10 seconds for typical batch (20-30 rows)

---

## Version History

- **v2.0.0**: Initial implementation with priority sorting and time estimation
- Future: Add deadline-based priority overrides, team assignment routing

---

**This utility is the foundation of efficient batch processing** — proper sorting and time estimation are critical for maximizing throughput.
