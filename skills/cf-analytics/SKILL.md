---
name: cf-analytics
description: "Render an ASCII analytics dashboard of ContentForge production history — quality score trends, phase-by-phase pipeline timing, brand and content-type comparisons, compliance and citation metrics, outlier detection, and triggered alerts over a 7/30/90-day window. Triggers on \"/contentforge:cf-analytics\", \"are our quality scores improving\", \"which pipeline phase is slowest\", \"show content production stats\", \"compare brands by quality\". Reads tracking records written by Phase 8 to the brand's tracking backend (local JSON, Google Sheets, or Airtable) and alert rules from config/analytics-config.json; needs 10+ tracked pieces for meaningful trends. Analysis only — invokes no agents and never reads or stores content text."
effort: low
argument-hint: "[--period 7|30|90] [--brand <name>] [--type <content-type>] [--focus quality|timing|compliance|citations]"
---

# Content Analytics Dashboard

Track ContentForge production quality, pipeline timing, brand-specific patterns, and compliance trends over configurable time periods with automated insights and alert flags.

## When to Use

Use `/contentforge:cf-analytics` when you need:
- **Quality trend visibility** — Are scores improving or declining over time?
- **Pipeline performance audit** — Which phases are slowest? Where are bottlenecks?
- **Brand comparison** — Which brands consistently score highest/lowest?
- **Content type analysis** — Are articles scoring better than whitepapers?
- **Compliance monitoring** — Citation rates, brand adherence, loop frequency
- **Capacity planning** — Average throughput for estimating batch timelines

**For real-time batch monitoring**, use the Progress Tracker (built into `/contentforge:batch-process`).
**For individual content production**, use [`/contentforge:create-content`](../../commands/create-content.md).

## What This Command Does

Loads historical production data from the brand's configured tracking backend (Google Sheets, Airtable, or local — see `tracking.backend` in the brand profile), calculates aggregate metrics across configurable dimensions, identifies statistical outliers and concerning trends, generates an ASCII dashboard with actionable recommendations, and flags alerts when performance degrades.

**Process Flow:**

1. **Load Data** — Read tracking records from the brand's tracking backend (Google Sheets / Airtable / local JSON)
2. **Filter & Parse** — Apply time period, brand, content type, and metric focus filters
3. **Calculate Aggregates** — Average scores, trends, percentiles, phase timing breakdowns
4. **Detect Outliers** — Flag data points beyond 2.0 standard deviations from mean
5. **Generate Insights** — Identify patterns, correlations, and improvement opportunities
6. **Present Dashboard** — Render ASCII analytics display with charts and recommendations
7. **Alert Check** — Evaluate alert rules and surface any triggered flags

## Required Inputs

**Optional (all have defaults):**
- **Time Period** — `7` | `30` | `90` days (default: `30`)
- **Brand Filter** — Filter to specific brand (default: all brands)
- **Content Type Filter** — `article` | `blog` | `whitepaper` | `faq` | `research_paper` | `video_script` | `case_study` | `newsletter` (default: all types)
- **Metric Focus** — `quality` | `timing` | `compliance` | `citations` (default: `quality`)

## How to Use

### Default Dashboard (Last 30 Days, All Brands)
```
/contentforge:cf-analytics
```

### Specific Time Period
```
/contentforge:cf-analytics --period=90
```

### Brand-Specific Analysis
```
/contentforge:cf-analytics --brand=AcmeMed --period=30
```

### Content Type Focus
```
/contentforge:cf-analytics --type=whitepaper --period=90
```

### Metric-Specific Deep Dive
```
/contentforge:cf-analytics --focus=timing --period=30
```

### Combined Filters
```
/contentforge:cf-analytics --brand=AcmeMed --type=article --focus=quality --period=90
```

## Data Sources

### Data source: the brand's tracking backend

ContentForge's Output Manager (Phase 8) logs every completed piece to the backend configured in the brand profile (`tracking.backend`):

- **`google_sheets`** — rows in the configured Google Sheet (read via `scripts/sheets-tracker.py`)
- **`airtable`** — records in the configured Airtable base (read via `scripts/airtable-tracker.py`)
- **`local`** — `tracking.json` under `~/.claude-marketing/{brand-slug}/tracking/` (read via `scripts/local-tracker.py`)

All three backends share the same record schema:

| Column | Type | Description |
|--------|------|-------------|
| requirement_id | string | Unique content ID (REQ-001) |
| title | string | Content title |
| brand | string | Brand profile used |
| content_type | enum | article, blog, whitepaper, faq, research_paper, video_script, case_study, newsletter |
| word_count | integer | Final word count |
| quality_score | float | Composite score (0-10) |
| content_quality | float | Dimension score (0-10) |
| citation_integrity | float | Dimension score (0-10) |
| brand_compliance | float | Dimension score (0-10) |
| seo_performance | float | Dimension score (0-10) |
| readability | float | Dimension score (0-10) |
| processing_time_min | float | Total pipeline time in minutes |
| phase_1_time | float | Research phase duration |
| phase_2_time | float | Fact-check phase duration |
| phase_3_time | float | Drafting phase duration |
| phase_4_time | float | Validation phase duration |
| phase_5_time | float | Structuring phase duration |
| phase_6_time | float | SEO phase duration |
| phase_6_5_time | float | Humanizer phase duration |
| phase_7_time | float | Reviewer phase duration |
| phase_8_time | float | Output phase duration |
| loops_used | integer | Total feedback loops triggered |
| loop_details | string | Which loops fired (e.g., "P4>P3 x1, P7>P5 x1") |
| citations_count | integer | Number of citations in final output |
| broken_links | integer | Broken links detected (should be 0) |
| completed_at | datetime | Completion timestamp |
| output_url | string | Google Drive link to .docx |

### Default when no cloud backend is configured
The `local` backend is the default: tracking data lives at
```
~/.claude-marketing/{brand-slug}/tracking/tracking.json
```
Switch backends anytime with `/contentforge:cf-switch-backend` (migration is additive and idempotent).

## What Happens

### Step 1: Data Loading (5-10 seconds)

```
Loading analytics data...
Source: <brand's tracking backend, e.g. Airtable base appXXXX / Google Sheet / local tracking.json>
Records found: 147 total
After filters: 42 records (last 30 days, all brands)
Date range: 2026-01-26 to 2026-02-25
```

**Pipeline telemetry (v4.0).** When a brand filter is active, also load the
cross-run telemetry so the dashboard can show where the pipeline itself works
hard for this brand:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.py loops --brand <slug>
python ${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.py patterns --brand <slug>
```

Render two additional panels from the output: **Loop edges fired** (by edge and
content type — an edge firing across many runs of one content type is a contract
problem worth a template fix, and the panel should say so) and **Recurring
humanizer patterns** (per-pattern totals and run-presence; runs the script
reports as `not_instrumented` are shown as "unknown (pre-4.0 run)", never as
zero). Skip both panels silently only when the brand has no runs at all.

### Step 2: Aggregate Calculation

**Quality Metrics:**
- Mean, median, min, max for composite score and each dimension
- Standard deviation for outlier detection
- Trend direction (improving, stable, declining) via linear regression slope
- Percentile distribution (P25, P50, P75, P90)

**Timing Metrics:**
- Average total processing time by content type
- Phase-by-phase timing breakdown (mean per phase)
- Slowest phase identification
- Comparison against benchmarks from `config/analytics-config.json`

**Compliance Metrics:**
- Average citations per piece
- Citation density (citations per 300 words)
- Average loops per piece
- Loop-free completion rate (% of pieces that passed on first review)
- Brand compliance dimension average

**Trend Metrics:**
- Rolling 7-day average quality score
- Week-over-week quality change
- Content volume by week

### Step 3: Outlier Detection

Flag any record where:
- Quality score is >2.0 standard deviations below the mean
- Processing time is >1.5x the benchmark for its content type
- Loops used >3 (suggests requirement or pipeline issues)
- Any dimension score <5.0 (below minimum pass threshold)

### Step 4: Insight Generation

Analyze patterns across the dataset:
- **Correlation Analysis:** Do longer processing times correlate with higher quality?
- **Brand Patterns:** Which brands have the most consistent scores?
- **Type Patterns:** Which content types have the highest loop frequency?
- **Phase Bottlenecks:** Which phase consumes the most time relative to benchmark?
- **Improvement Trajectory:** Is the system getting better over time?

### Step 5: Dashboard Rendering

## Output: Analytics Dashboard

### Full Dashboard (Default View)

**Before rendering, read `references/dashboard-examples.md` (in this skill's directory), section "Full Dashboard (Default View)", for the full synthetic layout** (quality score overview, weekly trend chart, phase timing breakdown, brand performance comparison, content type averages, feedback loop analysis, alerts, recommendations) — reproduce this shape with real computed values. All numbers in the reference are invented.

### Timing-Focused Dashboard (--focus=timing)

**Read `references/dashboard-examples.md` (in this skill's directory), section "Timing-Focused Dashboard (--focus=timing)", for the full synthetic layout** (processing-time distribution, time by content type, phase waterfall, bottleneck analysis, throughput metrics) — reproduce this shape with real computed values.

### Compliance-Focused Dashboard (--focus=compliance)

**Read `references/dashboard-examples.md` (in this skill's directory), section "Compliance-Focused Dashboard (--focus=compliance)", for the full synthetic layout** (citation compliance, brand compliance scores, feedback loop compliance, hallucination report) — reproduce this shape with real computed values.

## Alert Rules

Alerts are configured in `config/analytics-config.json` and trigger when:

| Alert | Condition | Severity |
|-------|-----------|----------|
| Quality Decline | 3 consecutive pieces from same brand score <7.0 | High |
| Phase Slowdown | Any phase averages >1.5x its benchmark time | Medium |
| Citation Drop | Citation density drops below content-type minimum | Medium |
| Loop Spike | Average loops/piece exceeds 2.0 for any content type | High |
| Score Floor | Any piece scores below 5.0 composite | Critical |
| Volume Gap | Fewer than 10 data points in analysis window | Info |

## Configuration

Analytics behavior is controlled by `config/analytics-config.json`:
- Quality thresholds (excellent, good, acceptable, needs_review)
- Timing benchmarks per content type
- Alert rule conditions
- Trend analysis parameters (window, min data points, outlier threshold)
- Dashboard defaults (time period, charts to display)
- Score component weights

See [`config/analytics-config.json`](../../config/analytics-config.json) for full configuration.

## Data Privacy

- Analytics operates on **aggregate metrics only** — no content text is stored or displayed
- Tracking data includes scores, timing, and metadata — never the content body
- All data stays within your configured tracking backend — no external transmission

## Limitations

- Requires at least 10 data points for meaningful trend analysis (30+ recommended)
- Trend direction (improving/declining) is based on linear regression and can be misleading with high variance
- Phase timing accuracy depends on ContentForge logging completeness
- Cannot retroactively analyze content produced before tracking was enabled
- Cross-session persistence follows the tracking backend: local JSON persists on the host filesystem; Google Sheets and Airtable persist in the cloud (and support team access)

## Agents Used

**None.** This skill operates entirely on tracked data — no content generation agents are invoked. It reads records written by the Output Manager (Phase 8) to the brand's tracking backend. The aggregation and trend logic is documented in `utilities/analytics-tracker.md` — a pseudocode reference doc (not a script); follow it for the calculations.

## Integration with Other Skills

**Data Sources:**
- `/contentforge:create-content` — Each completed piece adds a tracking record
- `/contentforge:batch-process` — Batch completions add multiple records
- `/contentforge:content-refresh` — Refresh completions add versioned records

**Acts On Insights:**
- Quality decline detected: Review brand profile, run `/contentforge:brand-setup` refresh
- Timing bottleneck found: Adjust phase configuration in `config/scoring-thresholds.json`
- Citation drop flagged: Update Phase 3 citation density targets

## Related Skills

- **[/contentforge:create-content](../../commands/create-content.md)** — Full content production pipeline (generates tracking data)
- **[/contentforge:batch-process](../batch-process/SKILL.md)** — Sequential, checkpointed batch processing (generates batch tracking data)
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** — Content updates (generates refresh tracking data)
- **[/contentforge:cf-variants](../cf-variants/SKILL.md)** — A/B test variation generation
- **[/contentforge:cf-switch-backend](../cf-switch-backend/SKILL.md)** — Change where tracking data lives

---

**Agents:** None (data analysis only; pseudocode reference: `utilities/analytics-tracker.md`)
**Output:** ASCII analytics dashboard with trends, comparisons, alerts, and recommendations
