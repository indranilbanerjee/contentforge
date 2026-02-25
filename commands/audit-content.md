---
description: Audit your content library for freshness decay, coverage gaps, and optimization opportunities
argument-hint: "<content source: drive folder|wordpress url|csv> [--scope=freshness|gaps|both]"
---

# Audit Content

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Audit your existing content library for freshness decay, coverage gaps, and optimization opportunities. Score every piece for freshness, identify content that needs refreshing, map coverage gaps against keyword opportunities, and produce a prioritized action list with projected impact.

## Trigger

User runs `/audit-content` or asks to audit their content, check for content decay, find content gaps, or assess content health.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Content source** — where the content library lives:
   - **Google Drive folder URL** — folder containing .docx files (e.g., `ContentForge Output/AcmeMed/`)
   - **WordPress site URL** — WordPress REST API endpoint (e.g., `https://blog.acme.com`)
   - **CSV file** — CSV with columns: `title`, `url`, `publish_date`, `content_type`, `word_count`
   - **Manual list** — paste titles and URLs directly

2. **Audit scope** — one of:
   - `freshness` — freshness scoring and refresh candidate identification only
   - `gaps` — coverage gap analysis only (compare topics against keyword opportunities)
   - `both` (default) — full audit: freshness + gap analysis

3. **Additional context** (optional):
   - Time threshold (months before content is "aging" — default: 12)
   - Brand filter (if multi-brand library)
   - Target keywords CSV (for gap analysis comparison)
   - Competitor URLs (for competitive gap analysis)

## Audit Process

### 1. Content Inventory

Load and catalog all content pieces:
- Title, URL, publication date, last updated date
- Content type (article, blog, whitepaper, FAQ, etc.)
- Word count
- Primary keyword (if identifiable)

### 2. Freshness Scoring (0-100)

Score each piece based on:

| Factor | Weight | Assessment |
|--------|--------|------------|
| Publication age | 30% | Months since publish/update |
| Statistic currency | 25% | Are cited stats still current? |
| Link health | 20% | Broken or redirected links? |
| Citation recency | 15% | Are sources still authoritative? |
| Industry relevance | 10% | Has the topic landscape changed? |

**Score interpretation:**
- 80-100: Fresh — no action needed
- 60-79: Aging — monitor, consider minor updates
- 40-59: Stale — schedule for refresh
- 0-39: Decayed — urgent refresh or retire

### 3. Coverage Gap Analysis

**If ~~SEO tools are connected:**
- Pull keyword data to identify topics competitors rank for that you don't

**Without SEO tools:**
- Use web search to identify high-value topics in your space

Map gaps:
- Topics your competitors cover that you don't
- High-volume keywords without matching content
- Content types competitors use that you're missing (guides, comparisons, tools, templates)
- Funnel stage gaps (awareness, consideration, decision content distribution)
- Topic cluster gaps (pillar pages without supporting content, or vice versa)

### 4. Performance Analysis (if analytics connected)

**If ~~analytics tools are connected:**
- Pull traffic trends per piece
- Identify declining traffic (content losing rankings)
- Cross-reference freshness with traffic to prioritize high-ROI refreshes

### 5. Prioritized Recommendations

Rank refresh candidates by:
- **Original value** — pieces that performed well historically deserve priority
- **Freshness score** — lower score = more urgent
- **Keyword opportunity** — pieces targeting high-value keywords get priority
- **Refresh effort** — quick updates vs. major rewrites

## Output Format

### Audit Summary

| Metric | Value |
|--------|-------|
| Total pieces audited | X |
| Fresh (80-100) | X (Y%) |
| Aging (60-79) | X (Y%) |
| Stale (40-59) | X (Y%) |
| Decayed (0-39) | X (Y%) |
| Coverage gaps found | X |

### Freshness Scorecard

| Title | Published | Score | Status | Top Issue | Recommended Action |
|-------|-----------|-------|--------|-----------|-------------------|

Top 20 pieces sorted by score (lowest first).

### Coverage Gap Opportunities

| Topic/Keyword | Search Demand | Competitor Coverage | Recommended Format | Priority | Effort |
|---------------|--------------|--------------------|--------------------|----------|--------|

### Refresh Priority List

| Rank | Title | Score | Keyword Value | Effort | Projected Impact |
|------|-------|-------|--------------|--------|------------------|

Top 10 refresh candidates ranked by ROI (impact / effort).

### Content Calendar Recommendations

Based on the audit, suggest a balanced calendar:
- X pieces to refresh (with deadlines)
- Y new pieces for gaps (with topics)
- Z pieces to retire or consolidate

## After the Audit

Ask: "Would you like me to:
- Create content briefs for the top gap opportunities? (`/content-brief`)
- Start refreshing the highest-priority piece? (`/create-content` with existing content as input)
- Build a quarterly content calendar from these recommendations? (`/calendar`)
- Run a deeper SEO analysis for specific pieces? (use Digital Marketing Pro `/seo-audit`)
- Export this audit to a spreadsheet?"
