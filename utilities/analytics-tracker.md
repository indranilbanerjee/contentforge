# Utility: Analytics Tracker

**Purpose:** Parse ContentForge production tracking data to generate performance insights, trend analysis, outlier detection, and actionable recommendations.

---

## Responsibilities

1. **Load Tracking Data** — Read from Google Sheets or local CSV with configurable filters
2. **Aggregate Metrics** — Calculate averages, medians, percentiles, and standard deviations
3. **Detect Trends** — Linear regression on quality scores over rolling time windows
4. **Identify Outliers** — Flag data points beyond configurable standard deviation thresholds
5. **Generate Recommendations** — Translate metric patterns into specific improvement actions
6. **Format Dashboard** — Render ASCII analytics display for `/cf:analytics` skill

---

## How It Works

### Pipeline

```
Data Loading → Filtering → Aggregation → Trend Analysis → Outlier Detection → Recommendation Generation → Dashboard Rendering
```

### Step 1: Data Loading

```python
def load_tracking_data(source='google_sheets', fallback='local_csv'):
    """Load ContentForge tracking records from primary or fallback source."""

    if source == 'google_sheets':
        try:
            records = sheets_api.read_range(
                spreadsheet_id=config['tracking_sheet_id'],
                range_name='ContentForge Tracking!A:Z'
            )
            return parse_sheet_records(records)
        except ConnectionError:
            print("Google Sheets unavailable, falling back to local CSV")
            source = fallback

    if source == 'local_csv':
        csv_path = os.path.expanduser(
            '~/.claude-marketing/contentforge-tracking.csv'
        )
        if os.path.exists(csv_path):
            return parse_csv_records(csv_path)
        else:
            raise FileNotFoundError(
                f"No tracking data found at {csv_path}. "
                "Run /contentforge to generate tracking records."
            )
```

### Step 2: Filtering

```python
def apply_filters(records, time_period=30, brand=None, content_type=None):
    """Filter records by time period, brand, and content type."""

    cutoff_date = datetime.now() - timedelta(days=time_period)

    filtered = [
        r for r in records
        if r['completed_at'] >= cutoff_date
    ]

    if brand:
        filtered = [r for r in filtered if r['brand'] == brand]

    if content_type:
        filtered = [r for r in filtered if r['content_type'] == content_type]

    return filtered
```

### Step 3: Aggregation

```python
def calculate_aggregates(records):
    """Calculate statistical aggregates across all quality dimensions."""

    scores = [r['quality_score'] for r in records]

    aggregates = {
        'count': len(records),
        'composite': {
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'min': min(scores),
            'max': max(scores),
            'stdev': statistics.stdev(scores) if len(scores) > 1 else 0,
            'p25': percentile(scores, 25),
            'p75': percentile(scores, 75),
            'p90': percentile(scores, 90)
        }
    }

    # Calculate per-dimension aggregates
    dimensions = [
        'content_quality', 'citation_integrity',
        'brand_compliance', 'seo_performance', 'readability'
    ]

    for dim in dimensions:
        dim_scores = [r[dim] for r in records]
        aggregates[dim] = {
            'mean': statistics.mean(dim_scores),
            'median': statistics.median(dim_scores),
            'min': min(dim_scores),
            'max': max(dim_scores),
            'stdev': statistics.stdev(dim_scores) if len(dim_scores) > 1 else 0
        }

    return aggregates
```

### Step 4: Trend Analysis

```python
def calculate_trend(records, window_days=30):
    """Calculate quality score trend via linear regression."""

    if len(records) < 10:
        return {'direction': 'insufficient_data', 'slope': 0, 'confidence': 0}

    # Sort by completion date
    sorted_records = sorted(records, key=lambda r: r['completed_at'])

    # Convert dates to numeric (days since first record)
    base_date = sorted_records[0]['completed_at']
    x_values = [(r['completed_at'] - base_date).days for r in sorted_records]
    y_values = [r['quality_score'] for r in sorted_records]

    # Linear regression
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x ** 2 for x in x_values)

    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        slope = 0
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denominator

    # Classify trend direction
    if slope > 0.05:
        direction = 'improving'
    elif slope < -0.05:
        direction = 'declining'
    else:
        direction = 'stable'

    return {
        'direction': direction,
        'slope': round(slope, 4),
        'change_per_30_days': round(slope * 30, 2)
    }
```

### Step 5: Outlier Detection

```python
def detect_outliers(records, threshold=2.0):
    """Flag records with quality scores beyond threshold standard deviations."""

    scores = [r['quality_score'] for r in records]
    mean_score = statistics.mean(scores)
    stdev_score = statistics.stdev(scores) if len(scores) > 1 else 0

    if stdev_score == 0:
        return []

    outliers = []
    for record in records:
        z_score = abs(record['quality_score'] - mean_score) / stdev_score
        if z_score > threshold:
            outliers.append({
                'requirement_id': record['requirement_id'],
                'title': record['title'],
                'brand': record['brand'],
                'quality_score': record['quality_score'],
                'z_score': round(z_score, 2),
                'direction': 'below' if record['quality_score'] < mean_score else 'above',
                'completed_at': record['completed_at']
            })

    return outliers
```

### Step 6: Recommendation Generation

```python
def generate_recommendations(aggregates, trends, outliers, timing, alerts):
    """Generate actionable recommendations from analytics data."""

    recommendations = []

    # Quality decline recommendations
    if trends['direction'] == 'declining':
        recommendations.append({
            'priority': 'high',
            'category': 'quality',
            'title': 'Quality Score Declining',
            'detail': (
                f"Average quality dropped {abs(trends['change_per_30_days'])} pts "
                f"over 30 days. Review recent brand profile changes and "
                f"scoring threshold configuration."
            ),
            'action': 'Audit config/scoring-thresholds.json and brand profiles'
        })

    # Timing bottleneck recommendations
    for phase, data in timing['phase_breakdown'].items():
        if data['ratio_to_benchmark'] > 1.5:
            recommendations.append({
                'priority': 'medium',
                'category': 'timing',
                'title': f'Phase {phase} Slowdown',
                'detail': (
                    f"Phase {phase} averages {data['avg_time']} min "
                    f"vs. {data['benchmark']} min benchmark "
                    f"({data['ratio_to_benchmark']:.1f}x slower)."
                ),
                'action': f'Review Phase {phase} configuration and input quality'
            })

    # Citation density recommendations
    if aggregates.get('citation_density_below_target'):
        recommendations.append({
            'priority': 'medium',
            'category': 'compliance',
            'title': 'Citation Density Below Target',
            'detail': (
                f"Average citation density is "
                f"{aggregates['avg_citation_density']:.1f} per 300 words "
                f"vs. 1.0 target."
            ),
            'action': 'Increase Phase 3 citation frequency targeting'
        })

    # Outlier recommendations
    low_outliers = [o for o in outliers if o['direction'] == 'below']
    if low_outliers:
        brands_affected = set(o['brand'] for o in low_outliers)
        recommendations.append({
            'priority': 'high',
            'category': 'quality',
            'title': f'Low-Score Outliers Detected ({len(low_outliers)} pieces)',
            'detail': (
                f"Brands affected: {', '.join(brands_affected)}. "
                f"Scores ranged from "
                f"{min(o['quality_score'] for o in low_outliers)} to "
                f"{max(o['quality_score'] for o in low_outliers)}."
            ),
            'action': 'Review flagged pieces and brand configurations'
        })

    # Loop frequency recommendations
    if aggregates.get('avg_loops', 0) > 1.0:
        recommendations.append({
            'priority': 'medium',
            'category': 'efficiency',
            'title': 'High Feedback Loop Frequency',
            'detail': (
                f"Average {aggregates['avg_loops']:.1f} loops per piece. "
                f"Target: <1.0. Most common trigger: "
                f"{aggregates.get('most_common_loop', 'P4>P3')}."
            ),
            'action': (
                'Improve Phase 1 research depth to reduce '
                'downstream validation failures'
            )
        })

    return sorted(recommendations, key=lambda r: {'high': 0, 'medium': 1, 'low': 2}[r['priority']])
```

---

## Data Structures

### AnalyticsRequest

```json
{
  "time_period": 30,
  "brand_filter": null,
  "content_type_filter": null,
  "metric_focus": "quality",
  "anonymize_brands": false,
  "export_format": null
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| time_period | integer | 30 | Days to analyze (7, 30, 90) |
| brand_filter | string | null | Filter to specific brand (null = all) |
| content_type_filter | string | null | Filter to content type (null = all) |
| metric_focus | enum | "quality" | Primary dashboard view: quality, timing, compliance, citations |
| anonymize_brands | boolean | false | Replace brand names with Brand A, Brand B, etc. |
| export_format | string | null | Export results: "json", "csv", or null (display only) |

### AnalyticsResponse

```json
{
  "metadata": {
    "generated_at": "2026-02-25T14:30:00Z",
    "period_start": "2026-01-26",
    "period_end": "2026-02-25",
    "total_records": 147,
    "filtered_records": 42,
    "filters_applied": {
      "time_period": 30,
      "brand": null,
      "content_type": null
    },
    "data_source": "google_sheets"
  },
  "quality_overview": {
    "composite": {
      "mean": 8.7,
      "median": 8.9,
      "min": 6.2,
      "max": 9.8,
      "stdev": 0.72,
      "p25": 8.2,
      "p75": 9.2,
      "p90": 9.5
    },
    "dimensions": {
      "content_quality": {"mean": 8.9, "median": 9.1, "min": 6.5, "max": 9.9},
      "citation_integrity": {"mean": 8.5, "median": 8.6, "min": 5.8, "max": 9.7},
      "brand_compliance": {"mean": 9.2, "median": 9.3, "min": 7.0, "max": 10.0},
      "seo_performance": {"mean": 8.6, "median": 8.7, "min": 6.0, "max": 9.8},
      "readability": {"mean": 8.8, "median": 8.9, "min": 6.8, "max": 9.6}
    },
    "trend": {
      "direction": "improving",
      "slope": 0.01,
      "change_per_30_days": 0.3
    }
  },
  "timing": {
    "total": {
      "mean": 26.5,
      "median": 24.8,
      "p90": 35.2
    },
    "by_content_type": {
      "article": {"mean": 25.2, "benchmark": 25, "delta": 0.2},
      "blog": {"mean": 17.8, "benchmark": 18, "delta": -0.2},
      "whitepaper": {"mean": 36.1, "benchmark": 35, "delta": 1.1},
      "faq": {"mean": 14.2, "benchmark": 15, "delta": -0.8},
      "research_paper": {"mean": 52.3, "benchmark": 40, "delta": 12.3}
    },
    "phase_breakdown": {
      "phase_1": {"mean": 4.2, "benchmark": 4.0, "pct_of_total": 16},
      "phase_2": {"mean": 3.1, "benchmark": 3.0, "pct_of_total": 12},
      "phase_3": {"mean": 5.8, "benchmark": 6.0, "pct_of_total": 22},
      "phase_4": {"mean": 2.4, "benchmark": 2.0, "pct_of_total": 9},
      "phase_5": {"mean": 2.7, "benchmark": 2.5, "pct_of_total": 10},
      "phase_6": {"mean": 2.9, "benchmark": 3.0, "pct_of_total": 11},
      "phase_6_5": {"mean": 1.6, "benchmark": 1.5, "pct_of_total": 6},
      "phase_7": {"mean": 2.5, "benchmark": 2.5, "pct_of_total": 10},
      "phase_8": {"mean": 1.3, "benchmark": 1.5, "pct_of_total": 5}
    }
  },
  "brand_performance": [
    {"brand": "AcmeMed", "pieces": 18, "avg_score": 9.1, "trend": "+0.4"},
    {"brand": "TechCorp", "pieces": 12, "avg_score": 8.5, "trend": "+0.2"},
    {"brand": "AgencyCo", "pieces": 8, "avg_score": 8.4, "trend": "stable"},
    {"brand": "FinanceFirst", "pieces": 4, "avg_score": 8.8, "trend": "new"}
  ],
  "content_type_performance": [
    {"type": "article", "pieces": 16, "avg_score": 8.8, "avg_time": 25.2, "avg_loops": 0.4},
    {"type": "blog", "pieces": 14, "avg_score": 8.9, "avg_time": 17.8, "avg_loops": 0.2},
    {"type": "whitepaper", "pieces": 6, "avg_score": 8.4, "avg_time": 36.1, "avg_loops": 0.8},
    {"type": "faq", "pieces": 4, "avg_score": 9.1, "avg_time": 14.2, "avg_loops": 0.1},
    {"type": "research_paper", "pieces": 2, "avg_score": 8.2, "avg_time": 52.3, "avg_loops": 1.5}
  ],
  "loops": {
    "loop_free_rate": 0.71,
    "avg_loops_per_piece": 0.45,
    "max_loops_used": 3,
    "human_escalations": 0,
    "loop_frequency": {
      "P4_to_P3": 5,
      "P7_to_P5": 3,
      "P7_to_P6": 2,
      "P7_to_P3": 1
    }
  },
  "outliers": [
    {
      "requirement_id": "REQ-089",
      "title": "Whitepaper: AI Governance",
      "brand": "AgencyCo",
      "quality_score": 6.2,
      "z_score": 3.47,
      "direction": "below"
    }
  ],
  "alerts": [
    {
      "rule": "quality_decline",
      "severity": "high",
      "message": "AgencyCo last 3 pieces scored below 7.0",
      "brand": "AgencyCo",
      "values": [7.8, 7.6, 7.9]
    },
    {
      "rule": "phase_slowdown",
      "severity": "medium",
      "message": "Whitepaper Phase 4 averaging 1.9x benchmark",
      "phase": "phase_4",
      "content_type": "whitepaper"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "category": "quality",
      "title": "AgencyCo Brand Review",
      "action": "Update brand profile (last modified 45 days ago)"
    },
    {
      "priority": "medium",
      "category": "timing",
      "title": "Whitepaper Validation Bottleneck",
      "action": "Pre-filter sources in Phase 1 to reduce Phase 4 load"
    }
  ]
}
```

---

## Metrics Tracked

### Quality Score Trends
- Composite score rolling average (7-day windows)
- Per-dimension score trends
- Score distribution (histogram buckets)
- Week-over-week delta

### Pipeline Timing
- Total processing time per piece
- Phase-by-phase duration breakdown
- Time vs. benchmark ratio
- Content type timing comparison
- Bottleneck identification (phase consuming most relative time)

### Brand Performance
- Per-brand average quality score
- Per-brand trend direction
- Per-brand strongest/weakest dimension
- Cross-brand comparison ranking

### Content Type Analysis
- Quality score by content type
- Processing time by content type
- Loop frequency by content type
- Citation density by content type

### Loop Frequency
- Overall loop-free rate
- Average loops per piece
- Loop type breakdown (which phase transitions)
- Human escalation count
- Loop budget utilization

---

## Insight Examples

### Pattern: New Brand Cold Start
```
Insight: AcmeMed's first 5 pieces averaged 8.2, but subsequent
15 pieces averaged 9.3. Brand cache warming improved scores
by +1.1 pts after initial calibration period.

Recommendation: When onboarding new brands, expect 3-5 pieces
at slightly lower quality before the pipeline calibrates to
brand voice. Flag this as normal behavior, not a concern.
```

### Pattern: Citation-Heavy Content Takes Longer
```
Insight: Whitepapers and research papers with 20+ citations
average 38% longer processing time than pieces with 10-15
citations. The extra time is concentrated in Phase 2 (fact-
checking) and Phase 4 (validation).

Recommendation: For citation-heavy content types, set client
expectations for 35-55 minute processing times rather than
the standard 25-30 minute estimate.
```

### Pattern: Humanizer Improves Reader Engagement Proxy
```
Insight: Pieces with burstiness scores above 0.75 (Phase 6.5)
consistently score higher on readability dimension (+0.6 pts
avg) compared to pieces at minimum threshold (0.7).

Recommendation: Consider raising burstiness target from 0.7
to 0.75 in config/scoring-thresholds.json for content types
where readability is high priority (blogs, FAQs).
```

---

## Usage

### Called by `/cf:analytics` Skill

The analytics tracker is the computation engine behind the `/cf:analytics` skill. The skill handles user interaction (parameter collection, mode selection), while this utility handles all data processing.

```python
# Invocation flow inside /cf:analytics
request = AnalyticsRequest(
    time_period=30,
    brand_filter='AcmeMed',
    metric_focus='quality'
)

# Step 1: Load and filter data
records = load_tracking_data()
filtered = apply_filters(records, request.time_period, request.brand_filter)

# Step 2: Calculate metrics
aggregates = calculate_aggregates(filtered)
trends = calculate_trend(filtered)
outliers = detect_outliers(filtered)
timing = calculate_timing_breakdown(filtered)

# Step 3: Generate insights
alerts = check_alert_rules(aggregates, trends, config['alert_rules'])
recommendations = generate_recommendations(aggregates, trends, outliers, timing, alerts)

# Step 4: Build response
response = AnalyticsResponse(
    metadata=build_metadata(request, filtered),
    quality_overview=aggregates,
    timing=timing,
    brand_performance=calculate_brand_comparison(filtered),
    content_type_performance=calculate_type_comparison(filtered),
    loops=calculate_loop_analysis(filtered),
    outliers=outliers,
    alerts=alerts,
    recommendations=recommendations
)

# Step 5: Render dashboard
render_dashboard(response, focus=request.metric_focus)
```

### Export Options

```python
# JSON export
analytics_tracker.export_json(response, 'analytics-report-2026-02-25.json')

# CSV export (flattened metrics)
analytics_tracker.export_csv(response, 'analytics-report-2026-02-25.csv')
```

---

## Benefits

- **Visibility**: Turns black-box content production into measurable, trackable operations
- **Early Warning**: Alert rules catch quality degradation before it becomes systemic (3-piece rolling check vs. discovering issues after 20+ pieces)
- **Data-Driven Optimization**: Phase timing data reveals where pipeline improvements have the most impact (e.g., fixing a Phase 4 bottleneck saves 1.8 min/piece = 36 min saved per 20-piece batch)
- **Brand Accountability**: Per-brand scoring enables objective performance conversations with clients ("AcmeMed content averages 9.1 vs. industry benchmark of 8.7")
- **Capacity Planning**: Historical throughput data enables accurate time estimates for new batch requests (within +/-15% of actual)
- **Continuous Improvement**: Trend analysis quantifies whether configuration changes (threshold adjustments, prompt refinements) are actually improving output quality

---

## Implementation Checklist

- [ ] Data loading from Google Sheets via MCP connector
- [ ] Data loading fallback from local CSV (~/.claude-marketing/contentforge-tracking.csv)
- [ ] Time-period filtering (7, 30, 90 days)
- [ ] Brand filtering (single brand or all)
- [ ] Content type filtering (single type or all)
- [ ] Composite score aggregation (mean, median, min, max, stdev, percentiles)
- [ ] Per-dimension score aggregation (5 dimensions)
- [ ] Linear regression trend calculation with direction classification
- [ ] Outlier detection with configurable z-score threshold
- [ ] Phase timing breakdown with benchmark comparison
- [ ] Brand performance comparison table
- [ ] Content type performance comparison table
- [ ] Feedback loop frequency analysis
- [ ] Alert rule evaluation (quality_decline, phase_slowdown, citation_drop, loop_spike, score_floor, volume_gap)
- [ ] Recommendation generation from detected patterns
- [ ] ASCII dashboard rendering (quality focus)
- [ ] ASCII dashboard rendering (timing focus)
- [ ] ASCII dashboard rendering (compliance focus)
- [ ] JSON export
- [ ] CSV export
- [ ] Brand anonymization option
- [ ] Configuration loading from config/analytics-config.json

---

## Performance Targets

- **Data Loading**: <5 seconds for 500 records from Google Sheets
- **Aggregation**: <1 second for 500 records
- **Trend Calculation**: <500ms for 500 records
- **Dashboard Render**: <100ms
- **Total End-to-End**: <10 seconds for typical 30-day analysis

---

## Version History

- **v2.1.0**: Initial analytics tracker with quality, timing, compliance, and citation dashboards
- Future: Historical comparison (this month vs. last month), export to Google Sheets dashboard, Slack/Teams alert notifications, custom metric definitions

---

**The analytics tracker transforms raw production logs into strategic intelligence** -- enabling data-driven decisions about brand onboarding, pipeline tuning, content type prioritization, and quality improvement initiatives.
