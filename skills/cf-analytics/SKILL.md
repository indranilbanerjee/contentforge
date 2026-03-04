---
name: cf-analytics
description: Track content quality scores, pipeline timing, brand performance, and compliance trends over time with actionable insights and alert flags
---

# Content Analytics Dashboard

Track ContentForge production quality, pipeline timing, brand-specific patterns, and compliance trends over configurable time periods with automated insights and alert flags.

## When to Use

Use `/cf:analytics` when you need:
- **Quality trend visibility** — Are scores improving or declining over time?
- **Pipeline performance audit** — Which phases are slowest? Where are bottlenecks?
- **Brand comparison** — Which brands consistently score highest/lowest?
- **Content type analysis** — Are articles scoring better than whitepapers?
- **Compliance monitoring** — Citation rates, brand adherence, loop frequency
- **Capacity planning** — Average throughput for estimating batch timelines

**For real-time batch monitoring**, use the Progress Tracker (built into `/batch-process`).
**For individual content production**, use [`/contentforge`](../contentforge/SKILL.md).

## What This Command Does

Loads historical production data from Google Sheets (if connected) or local CSV tracking files, calculates aggregate metrics across configurable dimensions, identifies statistical outliers and concerning trends, generates an ASCII dashboard with actionable recommendations, and flags alerts when performance degrades.

**Process Flow:**

1. **Load Data** — Read tracking records from Google Sheets (primary) or local CSV fallback
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
- **Content Type Filter** — `article` | `blog` | `whitepaper` | `faq` | `research_paper` (default: all types)
- **Metric Focus** — `quality` | `timing` | `compliance` | `citations` (default: `quality`)

## How to Use

### Default Dashboard (Last 30 Days, All Brands)
```
/cf:analytics
```

### Specific Time Period
```
/cf:analytics --period=90
```

### Brand-Specific Analysis
```
/cf:analytics --brand=AcmeMed --period=30
```

### Content Type Focus
```
/cf:analytics --type=whitepaper --period=90
```

### Metric-Specific Deep Dive
```
/cf:analytics --focus=timing --period=30
```

### Combined Filters
```
/cf:analytics --brand=AcmeMed --type=article --focus=quality --period=90
```

## Data Sources

### Primary: Google Sheets Tracking
ContentForge's Output Manager (Phase 8) logs every completed piece to a tracking sheet with these columns:

| Column | Type | Description |
|--------|------|-------------|
| requirement_id | string | Unique content ID (REQ-001) |
| title | string | Content title |
| brand | string | Brand profile used |
| content_type | enum | article, blog, whitepaper, faq, research_paper |
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

### Fallback: Local CSV
If Google Sheets is not connected, ContentForge writes tracking data to:
```
~/.claude-marketing/contentforge-tracking.csv
```
Same column schema as the Sheets version.

## What Happens

### Step 1: Data Loading (5-10 seconds)

```
Loading analytics data...
Source: Google Sheets (ContentForge Tracking)
Records found: 147 total
After filters: 42 records (last 30 days, all brands)
Date range: 2026-01-26 to 2026-02-25
```

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

```
================================================================
CONTENTFORGE ANALYTICS DASHBOARD
================================================================
Period: Last 30 Days (2026-01-26 to 2026-02-25)
Filters: All Brands | All Types | Focus: Quality
Records Analyzed: 42 pieces
================================================================

QUALITY SCORE OVERVIEW
----------------------------------------------------------------
                    Avg     Med     Min     Max     StdDev
Composite:          8.7     8.9     6.2     9.8     0.72
  Content Quality:  8.9     9.1     6.5     9.9     0.65
  Citation Integ.:  8.5     8.6     5.8     9.7     0.81
  Brand Compliance: 9.2     9.3     7.0     10.0    0.54
  SEO Performance:  8.6     8.7     6.0     9.8     0.68
  Readability:      8.8     8.9     6.8     9.6     0.52

Trend (30-day): +0.3 pts  [IMPROVING]

QUALITY TREND (Weekly Rolling Average)
----------------------------------------------------------------
10.0 |
 9.5 |          *----*
 9.0 |    *----*      *----*----*
 8.5 |---*
 8.0 |
 7.5 |
 7.0 |
     +----+----+----+----+----+----
     W1   W2   W3   W4   W5   Now
     8.4  8.6  8.7  8.9  8.8  8.9

Interpretation: Steady upward trend over 30 days.
Week 1 dip likely due to new brand onboarding
(AcmeMed cold-start penalty). Stabilized at 8.8+
from Week 3 onward.

PHASE TIMING BREAKDOWN (Minutes, Avg)
----------------------------------------------------------------
Phase               Avg    Bench   Delta    Status
................................................................
1. Research         4.2    4.0     +0.2     OK
2. Fact-Check       3.1    3.0     +0.1     OK
3. Drafting         5.8    6.0     -0.2     OK
4. Validation       2.4    2.0     +0.4     OK
5. Structuring      2.7    2.5     +0.2     OK
6. SEO              2.9    3.0     -0.1     OK
6.5 Humanizer       1.6    1.5     +0.1     OK
7. Reviewer         2.5    2.5     +0.0     OK
8. Output           1.3    1.5     -0.2     OK
................................................................
Total:             26.5   26.0     +0.5     OK

Slowest Phase: Drafting (22% of total time)
Fastest Phase: Output (5% of total time)

BRAND PERFORMANCE COMPARISON
----------------------------------------------------------------
Brand            Pieces   Avg Score   Trend     Top Dim
................................................................
AcmeMed            18      9.1        +0.4      Brand Comp (9.6)
TechCorp           12      8.5        +0.2      SEO Perf (9.0)
AgencyCo            8      8.4        stable    Readability (9.1)
FinanceFirst        4      8.8        new       Citation (9.2)

Best Performer: AcmeMed (9.1 avg, improving)
Most Improved: AcmeMed (+0.4 pts over period)
Needs Attention: AgencyCo (flat trend, lowest avg)

CONTENT TYPE AVERAGES
----------------------------------------------------------------
Type              Pieces   Avg Score   Avg Time   Loops/Piece
................................................................
Article              16      8.8        25.2 min    0.4
Blog                 14      8.9        17.8 min    0.2
Whitepaper            6      8.4        36.1 min    0.8
FAQ                   4      9.1        14.2 min    0.1
Research Paper        2      8.2        52.3 min    1.5

Best Quality: FAQ (9.1 avg, simplest structure)
Fastest: FAQ (14.2 min avg)
Most Loops: Research Paper (1.5 avg, citation density)

FEEDBACK LOOP ANALYSIS
----------------------------------------------------------------
Loop-Free Rate: 71% (30/42 pieces passed first review)
Avg Loops/Piece: 0.45
Max Loops Used: 3 (REQ-089, whitepaper)

Loop Frequency by Type:
  P4 > P3 (hallucination fix):  5 occurrences
  P7 > P5 (structure fix):     3 occurrences
  P7 > P6 (SEO fix):           2 occurrences
  P7 > P3 (content rewrite):   1 occurrence

Most Common Trigger: Hallucination detection in
validation phase (45% of all loops). Primarily
affects research papers and whitepapers with
high citation density requirements.

ALERTS
----------------------------------------------------------------
[!] QUALITY DECLINE: AgencyCo last 3 pieces scored
    below 8.0 (7.8, 7.6, 7.9). Review brand
    profile guardrails.

[!] PHASE SLOWDOWN: Whitepaper Phase 4 (validation)
    averaging 3.8 min vs. 2.0 min benchmark (1.9x).
    High citation count driving longer validation.

[i] VOLUME NOTE: Research paper sample size is low
    (2 pieces). Metrics may not be representative.
    Need 10+ data points for reliable trends.

IMPROVEMENT RECOMMENDATIONS
----------------------------------------------------------------
1. AgencyCo Brand Review: Update brand profile
   (last modified 45 days ago). Recent score
   decline suggests stale guardrails or
   terminology changes.

2. Whitepaper Validation: Consider pre-filtering
   sources in Phase 1 to reduce Phase 4
   validation load. Current avg: 22 sources
   per whitepaper vs. 15-25 target range.

3. Research Paper Pipeline: High loop frequency
   (1.5 avg) suggests tighter Phase 1 research
   briefs could reduce rework. Consider adding
   outline approval gate before drafting.

4. Citation Density: Blog citation rate (1 per
   380 words) is slightly below target (1 per
   300 words). Phase 3 keyword: increase
   inline citation frequency for blogs.

================================================================
Generated: 2026-02-25 14:30:00
Next suggested review: 2026-03-25 (monthly cadence)
================================================================
```

### Timing-Focused Dashboard (--focus=timing)

```
================================================================
CONTENTFORGE TIMING ANALYTICS
================================================================
Period: Last 30 Days | Records: 42 pieces
================================================================

TOTAL PROCESSING TIME DISTRIBUTION
----------------------------------------------------------------
< 15 min:  ████████████████  14 pieces (33%)
15-25 min: ██████████████████████  18 pieces (43%)
25-35 min: ██████████  8 pieces (19%)
> 35 min:  ██  2 pieces (5%)

Average: 26.5 min | Median: 24.8 min
P90: 35.2 min (90% of pieces finish within)

TIME BY CONTENT TYPE
----------------------------------------------------------------
                Min     Avg     Max     P90     vs Bench
Article:       18.2    25.2    32.1    29.5     +0.2 min
Blog:          12.4    17.8    24.6    21.3     -0.2 min
Whitepaper:    28.5    36.1    44.2    42.0     +1.1 min
FAQ:           10.1    14.2    18.3    17.0     -0.8 min
Research:      48.1    52.3    56.5    55.8     +12.3 min

PHASE WATERFALL (% of Total Time)
----------------------------------------------------------------
Research:     ████████████████  16% (4.2 min)
Fact-Check:   ████████████  12% (3.1 min)
Drafting:     ██████████████████████  22% (5.8 min)
Validation:   █████████  9% (2.4 min)
Structuring:  ██████████  10% (2.7 min)
SEO:          ███████████  11% (2.9 min)
Humanizer:    ██████  6% (1.6 min)
Reviewer:     █████████  10% (2.5 min)
Output:       █████  5% (1.3 min)

BOTTLENECK ANALYSIS
----------------------------------------------------------------
Primary Bottleneck: Drafting (22% of time)
  - Expected: 18% (per phase weight config)
  - Overrun: +4% (+1.0 min above weighted expectation)
  - Root Cause: Higher word count targets in recent
    batch (avg 2,100 words vs. 1,750 typical)

Secondary Bottleneck: Fact-Check for Whitepapers
  - Whitepaper avg: 4.8 min (vs. 3.0 min benchmark)
  - Cause: 22 sources avg per whitepaper (high end
    of 15-25 range)

THROUGHPUT METRICS
----------------------------------------------------------------
Single Pipeline: 2.3 pieces/hour (avg)
Batch (5x): 9.4 pieces/hour (effective)
Batch Efficiency: 82% (18% overhead for queue mgmt)

================================================================
```

### Compliance-Focused Dashboard (--focus=compliance)

```
================================================================
CONTENTFORGE COMPLIANCE ANALYTICS
================================================================
Period: Last 30 Days | Records: 42 pieces
================================================================

CITATION COMPLIANCE
----------------------------------------------------------------
Avg Citations/Piece: 11.2
Target Range: 5-25 (varies by type)
Pieces Meeting Target: 40/42 (95%)

Citation Density (per 300 words):
  Article:   1.2 (target: 1.0)  PASS
  Blog:      0.8 (target: 1.0)  BELOW
  Whitepaper: 1.4 (target: 1.0) PASS
  FAQ:       0.9 (target: 1.0)  BELOW (marginal)

Broken Links Detected: 0/42 pieces (100% clean)
Source Age: 94% within 2-year freshness window

BRAND COMPLIANCE SCORES
----------------------------------------------------------------
Brand            Avg Score   Min Score   Violations
AcmeMed:         9.6         8.8         0
TechCorp:        9.0         7.5         1 (terminology)
AgencyCo:        8.8         7.0         2 (tone drift)
FinanceFirst:    9.4         9.0         0

FEEDBACK LOOP COMPLIANCE
----------------------------------------------------------------
Loop Budget Usage:
  Avg loops/piece:     0.45 (budget: 5 max)
  Loop-free rate:      71%
  Max loops any piece: 3 (within budget)
  Budget exhaustions:  0 (no human escalations)

Human Review Escalations: 0/42 (0%)
Score <5.0 Pieces: 0/42 (0%)

HALLUCINATION REPORT
----------------------------------------------------------------
Hallucinations Detected: 0 in final output
Phase 4 Catches: 5 instances caught and fixed
  - 3x fabricated statistics (corrected in loop)
  - 1x misattributed quote (corrected in loop)
  - 1x outdated regulatory reference (corrected)

Three-Layer Verification: 100% effective
  Layer 1 (Fact-Check): Caught 0 (pre-filtered)
  Layer 2 (Validator): Caught 5 (primary defense)
  Layer 3 (Reviewer): Caught 0 (nothing escaped)

================================================================
```

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
- All data stays within your Google Sheets or local CSV — no external transmission
- Brand names appear in dashboards but can be anonymized with `--anonymize` flag

## Limitations

- Requires at least 10 data points for meaningful trend analysis (30+ recommended)
- Trend direction (improving/declining) is based on linear regression and can be misleading with high variance
- Phase timing accuracy depends on ContentForge logging completeness
- Cannot retroactively analyze content produced before tracking was enabled
- Google Sheets connection required for cross-session data persistence (CSV is session-local fallback)

## Agents Used

**None.** This skill operates entirely on tracked data — no content generation agents are invoked. It reads from the tracking sheet populated by the Output Manager (Phase 8) of the ContentForge pipeline.

## Integration with Other Skills

**Data Sources:**
- `/contentforge` — Each completed piece adds a row to the tracking sheet
- `/batch-process` — Batch completions add multiple rows
- `/content-refresh` — Refresh completions add versioned rows

**Acts On Insights:**
- Quality decline detected: Review brand profile, run `/brand-setup` refresh
- Timing bottleneck found: Adjust phase configuration in `config/scoring-thresholds.json`
- Citation drop flagged: Update Phase 3 citation density targets

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** — Full content production pipeline (generates tracking data)
- **[/batch-process](../batch-process/SKILL.md)** — Parallel content processing (generates batch tracking data)
- **[/content-refresh](../content-refresh/SKILL.md)** — Content updates (generates refresh tracking data)
- **[/cf:variants](../cf-variants/SKILL.md)** — A/B test variation generation

---

**Version:** 3.4.0
**Agents:** None (data analysis only)
**Processing Time:** 5-15 seconds (data loading + aggregation)
**Output:** ASCII analytics dashboard with trends, comparisons, alerts, and recommendations
