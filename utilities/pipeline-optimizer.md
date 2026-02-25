# Utility: Pipeline Optimizer

**Purpose:** Analyze pipeline performance, score content freshness, detect coverage gaps, identify bottlenecks, and generate prioritized recommendations for the `/cf:audit` skill.

---

## Responsibilities

1. **Audit Analysis** — Process content inventory and calculate health metrics
2. **Freshness Scoring** — Score each content piece 0-100 using a 4-factor weighted algorithm
3. **Bottleneck Detection** — Identify pipeline performance issues and content production constraints
4. **Gap Analysis** — Compare existing content coverage against keyword opportunity universe
5. **Recommendation Ranking** — Prioritize actions by projected traffic impact and effort

---

## How It Works

### Processing Pipeline

```
Content Inventory
       │
       ▼
┌──────────────┐
│ Audit        │  Load metadata (titles, dates, types, scores)
│ Analysis     │  Validate inventory completeness
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Freshness    │  Score each piece 0-100 (4-factor algorithm)
│ Scoring      │  Categorize: Fresh / Good / Aging / Stale / Expired
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Bottleneck   │  Identify production constraints
│ Detection    │  Flag capacity issues and timing patterns
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Gap          │  Map coverage vs keyword opportunities
│ Analysis     │  Calculate opportunity scores for missing topics
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Recommendation│  Rank all actions by (impact x feasibility)
│ Ranking      │  Produce prioritized action list
└──────────────┘
       │
       ▼
  Audit Report
```

---

## Data Structures

### AuditRequest

```python
audit_request = {
    'source_type': 'google_drive',  # google_drive | wordpress | csv
    'source_url': 'https://drive.google.com/drive/folders/ABC123',
    'audit_scope': 'both',  # freshness | gaps | both
    'time_threshold_months': 12,
    'brand_filter': 'AcmeMed',  # optional, filter to specific brand
    'target_keywords': [],  # optional, list of target keywords for gap analysis
    'analytics_available': False,  # True if Google Analytics/GSC MCP connected
    'timestamp': '2026-02-25T14:30:00Z'
}
```

### AuditResponse

```python
audit_response = {
    'request': audit_request,
    'inventory': {
        'total_pieces': 47,
        'by_type': {'article': 22, 'blog': 15, 'whitepaper': 6, 'faq': 4},
        'by_brand': {'AcmeMed': 32, 'AcmePharma': 15},
        'date_range': {'earliest': '2024-06-15', 'latest': '2026-01-20'},
        'avg_quality_score': 8.6
    },
    'freshness': {
        'overall_score': 58,
        'distribution': {
            'fresh': {'count': 5, 'percentage': 11},
            'good': {'count': 12, 'percentage': 26},
            'aging': {'count': 16, 'percentage': 34},
            'stale': {'count': 10, 'percentage': 21},
            'expired': {'count': 4, 'percentage': 8}
        },
        'scores': [freshness_score_1, freshness_score_2, ...],  # per piece
        'refresh_candidates': [candidate_1, candidate_2, ...]  # top 10
    },
    'gaps': {
        'keywords_covered': 38,
        'keywords_total': 52,
        'coverage_percentage': 73,
        'missing_keywords': [gap_1, gap_2, ...],  # sorted by opportunity score
        'content_plan': [plan_item_1, plan_item_2, ...]  # recommended new content
    },
    'performance': {  # only if analytics_available
        'top_performers': [...],
        'declining': [...],
        'underperformers': [...]
    },
    'recommendations': [recommendation_1, recommendation_2, ...],
    'processing_time_seconds': 480,
    'timestamp': '2026-02-25T14:38:00Z'
}
```

### FreshnessScore

```python
freshness_score = {
    'title': 'AI in Healthcare: 2024 Trends',
    'content_type': 'article',
    'brand': 'AcmeMed',
    'publish_date': '2024-08-15',
    'original_quality_score': 9.2,
    'word_count': 2340,

    # Factor scores (each 0-100)
    'age_score': 15,
    'statistics_currency_score': 20,
    'link_health_score': 45,
    'citation_recency_score': 30,

    # Weighted composite
    'composite_score': 18,  # Expired

    # Factor breakdown for transparency
    'factor_breakdown': {
        'age': {
            'months_since_publish': 18,
            'raw_score': 15,
            'weight': 0.35,
            'weighted_contribution': 5.25
        },
        'statistics': {
            'stats_found': 8,
            'stats_current': 1,
            'stats_outdated': 7,
            'raw_score': 20,
            'weight': 0.25,
            'weighted_contribution': 5.00
        },
        'links': {
            'total_links': 15,
            'live': 9,
            'redirected': 2,
            'broken': 4,
            'raw_score': 45,
            'weight': 0.20,
            'weighted_contribution': 9.00
        },
        'citations': {
            'total_citations': 12,
            'within_12_months': 2,
            'within_24_months': 5,
            'older_than_24_months': 5,
            'raw_score': 30,
            'weight': 0.20,
            'weighted_contribution': 6.00
        }
    },

    # Classification
    'category': 'expired',  # fresh | good | aging | stale | expired
    'refresh_priority': 'urgent',  # urgent | high | medium | low | none
    'recommended_scope': 'heavy',  # light | medium | heavy | retire
    'projected_traffic_impact': '+40%'
}
```

---

## Freshness Scoring Algorithm

### Overview

The freshness score is a 0-100 composite of four weighted factors. Higher scores indicate fresher, more current content. Lower scores indicate content that needs refreshing.

### Factor 1: Age Score (Weight: 35%)

The most significant factor. Newer content scores higher.

```python
def calculate_age_score(publish_date):
    """Score based on how old the content is."""

    months_since_publish = months_between(publish_date, today())

    # Linear decay: lose ~4.2 points per month
    age_score = max(0, 100 - (months_since_publish * 4.2))

    return round(age_score)

# Examples:
#   Published today: 100
#   Published 3 months ago: 87
#   Published 6 months ago: 75
#   Published 12 months ago: 50
#   Published 18 months ago: 24
#   Published 24 months ago: 0
```

### Factor 2: Statistics Currency (Weight: 25%)

Scans content for year-referenced statistics and data points.

```python
def calculate_statistics_currency(content_text, current_year=2026):
    """Score based on how current the statistics are."""

    # Find all year references in the content (e.g., "2024 report", "in 2025")
    year_references = extract_year_references(content_text)

    if not year_references:
        return 70  # No statistics = neutral score (not penalized)

    scores = []
    for year in year_references:
        years_old = current_year - year
        if years_old <= 0:
            scores.append(100)  # Current or future year
        elif years_old == 1:
            scores.append(80)   # Last year
        elif years_old == 2:
            scores.append(50)   # 2 years old
        elif years_old == 3:
            scores.append(25)   # 3 years old
        else:
            scores.append(5)    # 4+ years old

    return round(sum(scores) / len(scores))

# Examples:
#   All stats reference 2026: 100
#   Mix of 2025 and 2026: 90
#   All stats reference 2024: 50
#   All stats reference 2022: 5
```

### Factor 3: Link Health (Weight: 20%)

Checks the HTTP status of all outbound links.

```python
def calculate_link_health(outbound_links):
    """Score based on the health of outbound links."""

    if not outbound_links:
        return 50  # No links = neutral score

    total_score = 0
    for link in outbound_links:
        status = check_http_status(link)
        if status == 200:
            total_score += 1.0   # Live
        elif status in [301, 302]:
            total_score += 0.5   # Redirect (still works, but not ideal)
        elif status in [404, 410]:
            total_score -= 2.0   # Broken (significant penalty)
        elif status == 0:  # timeout
            total_score -= 1.0   # Timeout (moderate penalty)

    # Normalize to 0-100
    max_possible = len(outbound_links) * 1.0
    normalized = max(0, (total_score / max_possible) * 100)

    return round(normalized)

# Examples:
#   15 links, all live: 100
#   15 links, 12 live + 3 broken: 40
#   15 links, 9 live + 2 redirect + 4 broken: 23
```

### Factor 4: Citation Recency (Weight: 20%)

Evaluates how recently the cited sources were published.

```python
def calculate_citation_recency(citations, current_year=2026):
    """Score based on how recent the cited sources are."""

    if not citations:
        return 50  # No citations = neutral score

    scores = []
    for citation in citations:
        pub_year = citation.get('publication_year')
        if not pub_year:
            scores.append(50)  # Unknown date = neutral
            continue

        years_old = current_year - pub_year
        if years_old <= 1:
            scores.append(100)  # Within 12 months
        elif years_old <= 2:
            scores.append(70)   # Within 24 months
        elif years_old <= 3:
            scores.append(40)   # Within 36 months
        else:
            scores.append(10)   # Older than 36 months

    return round(sum(scores) / len(scores))
```

### Composite Score Calculation

```python
def calculate_freshness_score(piece):
    """Calculate composite freshness score (0-100)."""

    age = calculate_age_score(piece['publish_date'])
    stats = calculate_statistics_currency(piece['content_text'])
    links = calculate_link_health(piece['outbound_links'])
    citations = calculate_citation_recency(piece['citations'])

    composite = (
        (age * 0.35) +
        (stats * 0.25) +
        (links * 0.20) +
        (citations * 0.20)
    )

    return round(composite)
```

### Category Classification

```python
def classify_freshness(score):
    """Classify freshness score into categories."""

    if score >= 90:
        return 'fresh'     # No action needed
    elif score >= 70:
        return 'good'      # Monitor, refresh in 3-6 months
    elif score >= 50:
        return 'aging'     # Schedule for refresh this quarter
    elif score >= 30:
        return 'stale'     # Refresh priority HIGH
    else:
        return 'expired'   # Refresh or retire immediately
```

### Refresh Priority Assignment

```python
def assign_refresh_priority(freshness_score, original_quality_score):
    """
    Assign refresh priority based on freshness AND original quality.
    High-quality content that has gone stale = best ROI for refresh.
    Low-quality content that has gone stale = consider retiring.
    """

    if freshness_score < 30 and original_quality_score >= 8.5:
        return 'urgent'    # High-value content, expired
    elif freshness_score < 50 and original_quality_score >= 8.0:
        return 'high'      # Good content, stale
    elif freshness_score < 70 and original_quality_score >= 7.5:
        return 'medium'    # Decent content, aging
    elif freshness_score < 70 and original_quality_score < 7.5:
        return 'low'       # Low-quality content, aging (consider rewrite vs refresh)
    else:
        return 'none'      # Fresh enough, no refresh needed
```

### Recommended Refresh Scope

```python
def recommend_refresh_scope(freshness_score, original_quality_score):
    """Recommend the appropriate refresh scope."""

    if freshness_score < 20:
        if original_quality_score >= 8.0:
            return 'heavy'   # High-value but very outdated
        else:
            return 'retire'  # Low-value and very outdated
    elif freshness_score < 40:
        return 'medium'      # Significant sections need updating
    elif freshness_score < 70:
        return 'light'       # Stats and links only
    else:
        return None          # No refresh needed
```

---

## Bottleneck Detection

### Production Bottlenecks

```python
def detect_bottlenecks(inventory, production_history):
    """Identify pipeline bottlenecks from production patterns."""

    bottlenecks = []

    # 1. Content velocity bottleneck
    pieces_per_month = calculate_monthly_velocity(production_history)
    if pieces_per_month < inventory['total_pieces'] / 12:
        bottlenecks.append({
            'type': 'velocity',
            'severity': 'high',
            'description': f'Production velocity ({pieces_per_month}/mo) is below '
                          f'replacement rate ({inventory["total_pieces"] / 12:.0f}/mo needed '
                          f'to refresh entire library annually)',
            'recommendation': 'Use /batch-process for parallel production to increase throughput'
        })

    # 2. Content type imbalance
    type_distribution = inventory['by_type']
    if type_distribution.get('whitepaper', 0) == 0:
        bottlenecks.append({
            'type': 'type_gap',
            'severity': 'medium',
            'description': 'No whitepapers in library. Missing lead-generation content.',
            'recommendation': 'Create 2-3 whitepapers for gated content / lead capture'
        })

    # 3. Brand concentration
    brand_counts = inventory['by_brand']
    if len(brand_counts) > 1:
        max_brand = max(brand_counts, key=brand_counts.get)
        max_pct = brand_counts[max_brand] / inventory['total_pieces'] * 100
        if max_pct > 80:
            bottlenecks.append({
                'type': 'brand_concentration',
                'severity': 'low',
                'description': f'{max_brand} accounts for {max_pct:.0f}% of all content. '
                              f'Other brands are underrepresented.',
                'recommendation': f'Increase production for non-{max_brand} brands'
            })

    # 4. Freshness decay rate
    expired_pct = inventory.get('expired_percentage', 0)
    if expired_pct > 15:
        bottlenecks.append({
            'type': 'freshness_decay',
            'severity': 'high',
            'description': f'{expired_pct}% of content is expired (freshness < 30). '
                          f'Library health is degrading faster than content is being refreshed.',
            'recommendation': 'Prioritize refresh of top 10 expired pieces this quarter using /content-refresh'
        })

    return bottlenecks
```

---

## Gap Analysis

### Opportunity Score Calculation

```python
def calculate_opportunity_score(keyword_data):
    """
    Score a keyword gap by its opportunity value (0-100).
    Higher score = more valuable content to create.
    """

    volume = keyword_data['search_volume']
    difficulty = keyword_data['keyword_difficulty']  # 0-100
    relevance = keyword_data.get('relevance_score', 80)  # 0-100, default 80

    # Normalize volume (log scale to avoid outliers dominating)
    import math
    volume_normalized = min(100, (math.log10(max(volume, 1)) / math.log10(10000)) * 100)

    # Invert difficulty (easier = better opportunity)
    difficulty_inverted = 100 - difficulty

    # Weighted opportunity score
    opportunity = (
        (volume_normalized * 0.40) +
        (difficulty_inverted * 0.35) +
        (relevance * 0.25)
    )

    return round(opportunity)

# Examples:
#   Volume 2400, KD 62, Relevance 90: opportunity = 68
#   Volume 1800, KD 45, Relevance 85: opportunity = 72
#   Volume 500, KD 25, Relevance 95:  opportunity = 70
```

### Coverage Mapping

```python
def map_coverage(existing_content, target_keywords):
    """Map which target keywords are covered by existing content."""

    covered = []
    missing = []

    for keyword in target_keywords:
        # Check if any existing content targets this keyword
        match = find_content_matching_keyword(existing_content, keyword)

        if match:
            covered.append({
                'keyword': keyword,
                'matched_content': match['title'],
                'freshness_score': match['freshness_score']
            })
        else:
            missing.append({
                'keyword': keyword['phrase'],
                'search_volume': keyword['volume'],
                'keyword_difficulty': keyword['difficulty'],
                'opportunity_score': calculate_opportunity_score(keyword)
            })

    # Sort missing by opportunity score (descending)
    missing.sort(key=lambda x: x['opportunity_score'], reverse=True)

    return covered, missing
```

---

## Recommendation Ranking

### Recommendation Types

```python
RECOMMENDATION_TYPES = {
    'refresh': {
        'description': 'Update existing content with fresh data',
        'effort': 'low-medium',  # 15-30 min per piece
        'impact': 'high',  # preserves existing rankings + SEO equity
        'command': '/content-refresh'
    },
    'new_content': {
        'description': 'Create new content for coverage gaps',
        'effort': 'medium-high',  # 25-45 min per piece
        'impact': 'medium-high',  # new rankings, no existing equity
        'command': '/cf:brief + /contentforge'
    },
    'quality_improvement': {
        'description': 'Re-run low-scoring content through pipeline',
        'effort': 'medium',  # 20-30 min per piece
        'impact': 'medium',  # better content quality, indirect SEO
        'command': '/contentforge (reprocess)'
    },
    'retire': {
        'description': 'Remove or redirect severely outdated content',
        'effort': 'low',  # 5 min per piece (301 redirect)
        'impact': 'low-positive',  # reduces crawl waste, improves site quality
        'command': '301 redirect to best matching fresh content'
    }
}
```

### Priority Score Calculation

```python
def calculate_recommendation_priority(rec_type, freshness_score, quality_score,
                                       traffic_data=None, opportunity_score=None):
    """
    Calculate a priority score (0-100) for a recommendation.
    Higher = do this first.
    """

    if rec_type == 'refresh':
        # Priority = (value of existing content) x (urgency of refresh)
        value = quality_score * 10  # 0-100
        urgency = 100 - freshness_score  # 0-100
        traffic_bonus = 0
        if traffic_data and traffic_data.get('monthly_sessions', 0) > 1000:
            traffic_bonus = 20  # High-traffic content gets priority

        priority = (value * 0.40) + (urgency * 0.40) + (traffic_bonus * 0.20)

    elif rec_type == 'new_content':
        # Priority = opportunity score (volume, difficulty, relevance)
        priority = opportunity_score or 50

    elif rec_type == 'quality_improvement':
        # Priority = how far below quality threshold
        quality_gap = max(0, 70 - (quality_score * 10))
        priority = quality_gap

    elif rec_type == 'retire':
        # Priority = how outdated x how low quality
        priority = max(0, (100 - freshness_score) * 0.3 + (100 - quality_score * 10) * 0.3)

    return round(min(100, priority))
```

### Generating the Final Recommendation List

```python
def generate_recommendations(freshness_scores, coverage_gaps, bottlenecks,
                              performance_data=None, max_recommendations=20):
    """Generate prioritized recommendation list."""

    recommendations = []

    # 1. Refresh candidates (from freshness scores)
    for piece in freshness_scores:
        if piece['refresh_priority'] in ['urgent', 'high', 'medium']:
            priority = calculate_recommendation_priority(
                'refresh', piece['composite_score'], piece['original_quality_score'],
                traffic_data=performance_data.get(piece['title']) if performance_data else None
            )
            recommendations.append({
                'type': 'refresh',
                'title': piece['title'],
                'priority_score': priority,
                'freshness_score': piece['composite_score'],
                'quality_score': piece['original_quality_score'],
                'recommended_scope': piece['recommended_scope'],
                'projected_impact': piece.get('projected_traffic_impact', 'Unknown'),
                'command': f"/content-refresh [Drive URL] --scope={piece['recommended_scope']}"
            })

    # 2. New content (from coverage gaps)
    for gap in coverage_gaps[:10]:  # Top 10 gaps
        priority = calculate_recommendation_priority(
            'new_content', opportunity_score=gap['opportunity_score']
        )
        recommendations.append({
            'type': 'new_content',
            'keyword': gap['keyword'],
            'priority_score': priority,
            'search_volume': gap['search_volume'],
            'keyword_difficulty': gap['keyword_difficulty'],
            'opportunity_score': gap['opportunity_score'],
            'projected_impact': f"+{gap['search_volume'] * 0.05:.0f} monthly sessions (est.)",
            'command': f"/cf:brief \"{gap['keyword']}\""
        })

    # 3. Retire candidates (expired + low quality)
    for piece in freshness_scores:
        if piece['recommended_scope'] == 'retire':
            recommendations.append({
                'type': 'retire',
                'title': piece['title'],
                'priority_score': 20,  # Low priority (do after refreshes/new content)
                'freshness_score': piece['composite_score'],
                'quality_score': piece['original_quality_score'],
                'command': '301 redirect to nearest fresh content'
            })

    # Sort all recommendations by priority score (descending)
    recommendations.sort(key=lambda x: x['priority_score'], reverse=True)

    return recommendations[:max_recommendations]
```

---

## Usage

### Called by /cf:audit

The pipeline optimizer is the analytical engine behind the `/cf:audit` skill:

```python
# In cf-audit SKILL.md execution:

# Step 1: Load inventory
inventory = load_content_inventory(source_url, source_type)

# Step 2: Score freshness
freshness_scores = []
for piece in inventory:
    score = calculate_freshness_score(piece)
    score['refresh_priority'] = assign_refresh_priority(
        score['composite_score'], score['original_quality_score']
    )
    score['recommended_scope'] = recommend_refresh_scope(
        score['composite_score'], score['original_quality_score']
    )
    freshness_scores.append(score)

# Step 3: Detect bottlenecks
bottlenecks = detect_bottlenecks(inventory, production_history)

# Step 4: Analyze gaps
covered, missing = map_coverage(inventory, target_keywords)

# Step 5: Generate recommendations
recommendations = generate_recommendations(
    freshness_scores, missing, bottlenecks,
    performance_data=analytics_data  # if available
)

# Step 6: Produce audit report
report = format_audit_report(
    inventory, freshness_scores, bottlenecks, covered, missing, recommendations
)
```

### Standalone Usage

The optimizer can also be called directly for specific analysis:

```python
# Just freshness scoring (no gap analysis)
score = calculate_freshness_score(content_piece)

# Just gap analysis (no freshness)
covered, missing = map_coverage(inventory, keywords)

# Just recommendation ranking
recommendations = generate_recommendations(scores, gaps, bottlenecks)
```

---

## Benefits

### For Content Teams
- **Prioritized action list** — Know exactly which content to refresh first for maximum ROI
- **Projected traffic impact** — Estimate the value of each refresh or new content piece
- **Coverage visibility** — See which topics your library covers and where gaps exist
- **Freshness transparency** — Understand WHY content is aging (stats, links, citations, or age)

### For Agencies
- **Client reporting** — Produce data-backed audit reports showing content health
- **Quarterly planning** — Use audit data to plan refresh and new content schedules
- **ROI justification** — Projected traffic impact helps justify content investment

### For Pipeline Performance
- **Bottleneck identification** — Know where the content operation is constrained
- **Velocity tracking** — Monitor production rate against library refresh needs
- **Quality trends** — Track average quality scores over time

---

## Implementation Checklist

### Core Functions
- [ ] `calculate_age_score(publish_date)` — Age-based scoring
- [ ] `calculate_statistics_currency(content_text)` — Year-reference scanning
- [ ] `calculate_link_health(outbound_links)` — HTTP status checking
- [ ] `calculate_citation_recency(citations)` — Citation date scoring
- [ ] `calculate_freshness_score(piece)` — Composite 4-factor score
- [ ] `classify_freshness(score)` — Category assignment
- [ ] `assign_refresh_priority(freshness, quality)` — Priority ranking
- [ ] `recommend_refresh_scope(freshness, quality)` — Scope recommendation

### Gap Analysis Functions
- [ ] `calculate_opportunity_score(keyword_data)` — Keyword opportunity scoring
- [ ] `map_coverage(existing_content, target_keywords)` — Coverage mapping
- [ ] `find_content_matching_keyword(content_list, keyword)` — Content-keyword matching

### Bottleneck Functions
- [ ] `detect_bottlenecks(inventory, production_history)` — Constraint identification
- [ ] `calculate_monthly_velocity(production_history)` — Production rate calculation

### Recommendation Functions
- [ ] `calculate_recommendation_priority(type, freshness, quality, ...)` — Priority scoring
- [ ] `generate_recommendations(scores, gaps, bottlenecks, ...)` — Full recommendation list

### Output Formatting
- [ ] `format_audit_report(inventory, scores, bottlenecks, coverage, recommendations)` — Full report
- [ ] `format_freshness_table(scores)` — Top 10 refresh candidates table
- [ ] `format_gap_table(missing_keywords)` — Coverage gaps table
- [ ] `format_recommendation_list(recommendations)` — Prioritized action list

---

## Performance Targets

- **Freshness scoring:** <2 seconds per piece (excluding link health check)
- **Link health check:** <30 seconds per piece (HTTP timeout 5s per link, parallelized)
- **Gap analysis:** <5 seconds for 100 keywords against 50 content pieces
- **Full audit (50 pieces):** <5 minutes total
- **Full audit (200 pieces):** <15 minutes total

---

## Version History

- **v2.1.0**: Initial implementation with 4-factor freshness scoring, gap analysis, bottleneck detection, and recommendation ranking
- Future: Machine learning-based freshness prediction, historical trend analysis, automated refresh scheduling

---

**This utility is the analytical backbone of content library management** — it transforms raw content inventory into actionable intelligence for refresh prioritization, gap filling, and pipeline optimization.
