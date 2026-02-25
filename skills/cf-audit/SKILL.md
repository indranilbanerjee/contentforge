---
name: cf-audit
description: Audit existing content library for freshness decay, coverage gaps, and optimization opportunities with prioritized refresh recommendations
---

# Content Library Audit

Audit your existing content library for freshness decay, coverage gaps, and optimization opportunities. The audit scores every piece for freshness, identifies content that needs refreshing, maps coverage gaps against keyword opportunities, and produces a prioritized action list with projected impact.

## When to Use

Use `/cf:audit` when:
- You need a **quarterly or annual content health check** across your library
- Search rankings are declining and you need to **identify which content to refresh first**
- You want to find **coverage gaps** — topics your competitors rank for but you don't
- You need to **prioritize refresh candidates** for `/content-refresh` based on data
- A new client wants an **audit before production** to avoid duplicating existing content
- You're planning next quarter's content calendar and need to **balance new vs refresh**

**For refreshing specific pieces**, use `/content-refresh` after the audit identifies candidates.
**For producing new content** for identified gaps, use `/cf:brief` then `/contentforge`.

## What This Command Does

1. **Load Content Inventory** — Import content list from Google Drive folder, WordPress site, or CSV
2. **Freshness Scoring** — Score each piece 0-100 based on publication date, statistic currency, link health, and citation recency
3. **Coverage Gap Analysis** — Compare topics covered against keyword opportunities to find missing content
4. **Performance Analysis** — Pull traffic and engagement data if analytics are connected
5. **Prioritize Refresh Candidates** — Rank pieces by (high original value) + (low freshness score) to find the best ROI refreshes
6. **Generate Recommendations** — Produce actionable audit report with top 10 refresh candidates, coverage gaps, optimization recommendations, and projected impact

## Required Inputs

**Content Source (one of):**
- **Google Drive Folder URL** — Folder containing .docx files (e.g., `ContentForge Output/AcmeMed/`)
- **WordPress Site URL** — WordPress REST API endpoint (e.g., `https://blog.acme.com`)
- **CSV List** — CSV file with columns: `title`, `url`, `publish_date`, `content_type`, `word_count`

**Audit Scope:**
- **freshness** — Freshness scoring and refresh candidate identification only
- **gaps** — Coverage gap analysis only (compares your topics against keyword opportunities)
- **both** (default) — Full audit: freshness scoring + coverage gap analysis

**Optional:**
- **Time Threshold** — How many months old before content is considered "aging" (default: 12 months)
- **Brand** — Filter audit to a specific brand (if multi-brand library)
- **Target Keywords** — CSV of keywords to check coverage against (for gap analysis)

## How to Use

### Basic Usage (Google Drive)
```
/cf:audit https://drive.google.com/drive/folders/ABC123
```
**Prompt:** "Audit scope? (freshness / gaps / both)"

### WordPress Site Audit
```
/cf:audit https://blog.acme.com --scope=both --threshold=12
```

### CSV Inventory Audit
```
/cf:audit content-inventory.csv --scope=freshness --threshold=6
```

### Freshness-Only Audit
```
/cf:audit https://drive.google.com/drive/folders/ABC123 --scope=freshness --threshold=18
```

### Gap Analysis Only
```
/cf:audit https://drive.google.com/drive/folders/ABC123 --scope=gaps --keywords=target-keywords.csv
```

## What Happens

### Step 1: Load Content Inventory (1-3 minutes)

Load content metadata from the specified source.

**From Google Drive:**
- List all .docx files in the specified folder (and subfolders)
- Extract metadata: title, publish date, word count, brand, content type
- Read ContentForge quality scores from document properties (if originally produced by ContentForge)

**From WordPress:**
- Call WordPress REST API (`/wp-json/wp/v2/posts?per_page=100`)
- Extract: title, URL, publish date, modified date, word count, categories, tags
- Paginate through all posts if >100

**From CSV:**
- Parse CSV with required columns: title, url, publish_date
- Optional columns: content_type, word_count, quality_score, brand

**Example Inventory Output:**
```
Content Inventory Loaded
================================================================

Source: Google Drive / ContentForge Output / AcmeMed
Total Pieces: 47
Content Types: 22 articles, 15 blogs, 6 whitepapers, 4 FAQs

Date Range: 2024-06-15 to 2026-01-20
  Published in last 6 months: 12 (26%)
  Published 6-12 months ago: 18 (38%)
  Published 12-24 months ago: 14 (30%)
  Published 24+ months ago: 3 (6%)

Brands: AcmeMed (32), AcmePharma (15)
Average Original Quality Score: 8.6/10
================================================================
```

### Step 2: Freshness Scoring (3-5 minutes)

Score each piece 0-100 for freshness using four weighted factors.

**Freshness Score Formula:**
```
Freshness Score = (Age Score x 0.35) +
                  (Statistics Currency x 0.25) +
                  (Link Health x 0.20) +
                  (Citation Recency x 0.20)
```

**Factor 1: Age Score (35% weight)**
```
Months since publication:
  0-6 months:   100 (fresh)
  6-12 months:  80-99 (aging)
  12-18 months: 50-79 (stale)
  18-24 months: 25-49 (outdated)
  24+ months:   0-24 (expired)

Formula: max(0, 100 - (months_since_publish * 4.2))
```

**Factor 2: Statistics Currency (25% weight)**
```
Scan content for statistics, data points, market projections.
For each statistic found:
  - Extract the year referenced (e.g., "2024 market report")
  - Compare against current year (2026)
  - Score: 100 if current year, -20 per year old

Aggregate: Average score across all statistics found
  If no statistics: Score = 70 (neutral, not penalized)
```

**Factor 3: Link Health (20% weight)**
```
Check all outbound links in the content:
  - Live (HTTP 200): +1 per link
  - Redirect (301/302): +0.5 per link
  - Broken (404/500): -2 per link
  - Timeout: -1 per link

Score = (live_score / total_links) * 100
  If no links: Score = 50 (neutral)
```

**Factor 4: Citation Recency (20% weight)**
```
For each citation/source:
  - Extract publication date of the cited source
  - Score: 100 if published within 12 months
  - Score: 70 if published within 24 months
  - Score: 40 if published within 36 months
  - Score: 10 if published 36+ months ago

Aggregate: Average score across all citations
  If no citations: Score = 50 (neutral)
```

**Freshness Categories:**
```
90-100: Fresh — No action needed
70-89:  Good — Monitor, refresh in 3-6 months
50-69:  Aging — Schedule for refresh this quarter
30-49:  Stale — Refresh priority HIGH
0-29:   Expired — Refresh or retire immediately
```

**Example Freshness Report:**
```
Freshness Scoring Report
================================================================

Overall Library Freshness: 58/100 (Aging)

Distribution:
  Fresh (90-100):   5 pieces (11%)
  Good (70-89):     12 pieces (26%)
  Aging (50-69):    16 pieces (34%)
  Stale (30-49):    10 pieces (21%)
  Expired (0-29):   4 pieces (8%)

Top 10 Refresh Candidates (sorted by priority):
┌────────────────────────────────────────────────────────────────┐
│ #  │ Title                          │ Fresh │ Orig  │ Priority│
│    │                                │ Score │ Score │         │
├────────────────────────────────────────────────────────────────┤
│ 1  │ AI in Healthcare: 2024 Trends  │ 18    │ 9.2   │ URGENT  │
│ 2  │ Best EHR Systems Comparison    │ 22    │ 8.8   │ URGENT  │
│ 3  │ HIPAA Compliance Guide 2024    │ 31    │ 9.0   │ HIGH    │
│ 4  │ Telemedicine ROI Framework     │ 35    │ 8.5   │ HIGH    │
│ 5  │ Patient Engagement Strategies  │ 42    │ 8.7   │ HIGH    │
│ 6  │ Healthcare Data Security       │ 48    │ 8.3   │ MEDIUM  │
│ 7  │ Value-Based Care Guide         │ 51    │ 8.9   │ MEDIUM  │
│ 8  │ Digital Health Trends 2025     │ 55    │ 8.4   │ MEDIUM  │
│ 9  │ Remote Patient Monitoring      │ 58    │ 7.9   │ MEDIUM  │
│ 10 │ Clinical Trial Technology      │ 61    │ 8.1   │ LOW     │
└────────────────────────────────────────────────────────────────┘

Priority Logic: High original quality score + Low freshness = Best ROI
  URGENT: Freshness <30, Original Score >8.5
  HIGH: Freshness <50, Original Score >8.0
  MEDIUM: Freshness <70, Original Score >7.5
  LOW: Freshness <70, Original Score <7.5
================================================================
```

### Step 3: Coverage Gap Analysis (3-5 minutes)

Compare your content topics against keyword opportunities to find missing coverage.

**Process:**
1. Extract topics and keywords from existing content inventory
2. Identify target keyword universe (from provided keywords CSV, Ahrefs data, or SERP analysis)
3. Map existing content to keywords (which keywords are already covered?)
4. Identify gaps (high-value keywords with no matching content)
5. Rank gaps by search volume and keyword difficulty

**Example Gap Analysis:**
```
Coverage Gap Analysis
================================================================

Keywords Covered: 38 of 52 target keywords (73%)
Keywords Missing: 14 keywords with no matching content

Top 10 Coverage Gaps (by opportunity score):
┌─────────────────────────────────────────────────────────────────┐
│ #  │ Missing Keyword                │ Volume │ KD  │ Opportunity│
├─────────────────────────────────────────────────────────────────┤
│ 1  │ AI diagnostics precision med.  │ 2,400  │ 62  │ 92/100    │
│ 2  │ healthcare API integration     │ 1,800  │ 45  │ 88/100    │
│ 3  │ FHIR implementation guide      │ 1,200  │ 38  │ 85/100    │
│ 4  │ clinical decision support 2026 │ 980    │ 41  │ 82/100    │
│ 5  │ healthcare data interoperab.   │ 860    │ 52  │ 78/100    │
│ 6  │ AI radiology workflows         │ 720    │ 35  │ 76/100    │
│ 7  │ patient data privacy 2026      │ 650    │ 48  │ 72/100    │
│ 8  │ digital therapeutics guide     │ 580    │ 33  │ 70/100    │
│ 9  │ healthcare cloud migration     │ 520    │ 55  │ 65/100    │
│ 10 │ remote diagnostics platform    │ 440    │ 29  │ 63/100    │
└─────────────────────────────────────────────────────────────────┘

Opportunity Score = (Search Volume normalized) x (100 - KD) x relevance
  Higher score = easier to rank + more traffic potential

Recommended Content Plan for Top 5 Gaps:
  1. Create article: "AI Diagnostics in Precision Medicine" (2,500 words)
  2. Create whitepaper: "Healthcare API Integration Guide" (3,500 words)
  3. Create article: "FHIR Implementation: A 2026 Guide" (2,000 words)
  4. Create article: "Clinical Decision Support Systems in 2026" (1,800 words)
  5. Create article: "Healthcare Data Interoperability" (2,200 words)
================================================================
```

### Step 4: Performance Analysis (2-3 minutes, optional)

If analytics are connected, pull traffic and engagement data for each content piece.

**MCP Integrations:**
- **Google Analytics (optional)** — Page views, sessions, avg time on page, bounce rate, conversions per content URL
- **Google Search Console (optional)** — Impressions, clicks, CTR, average position per content URL

**Without Analytics MCP:**
Performance analysis is skipped. The audit still provides freshness scoring and coverage gap analysis, which are the two most actionable sections.

**Example Performance Data:**
```
Performance Analysis (Last 90 Days)
================================================================

Top Performers (high traffic + high quality):
  1. "Best EHR Systems Comparison" — 8,200 sessions, 4.2 min avg, Pos #4
  2. "AI in Healthcare: 2024 Trends" — 6,800 sessions, 3.8 min avg, Pos #6
  3. "HIPAA Compliance Guide 2024" — 5,100 sessions, 5.1 min avg, Pos #3

Declining Performers (traffic dropping):
  1. "AI in Healthcare: 2024 Trends" — -32% sessions (was #2, now #6)
  2. "Best EHR Systems Comparison" — -18% sessions (was #3, now #4)
  3. "Telemedicine ROI Framework" — -25% sessions (dropped to page 2)

Underperformers (high quality, low traffic):
  1. "Value-Based Care Guide" (Score: 8.9, only 320 sessions)
  2. "Patient Engagement Strategies" (Score: 8.7, only 280 sessions)
  Likely cause: Poor keyword targeting or insufficient backlinks
================================================================
```

### Step 5: Generate Recommendations (1-2 minutes)

Produce a prioritized action list combining freshness scores, coverage gaps, and performance data.

**Recommendation Types:**
1. **Refresh Candidates** — Existing content to update with `/content-refresh`
2. **New Content Opportunities** — Coverage gaps to fill with `/cf:brief` + `/contentforge`
3. **Quality Improvements** — Content with low quality scores to re-run through pipeline
4. **Retire Candidates** — Content so outdated it should be removed or redirected

**Example Recommendations:**
```
Audit Recommendations (Prioritized)
================================================================

IMMEDIATE ACTIONS (This Week):
  1. REFRESH: "AI in Healthcare: 2024 Trends" — Freshness 18, declining traffic
     Scope: Heavy refresh (80%), update year references, new 2026 data
     Projected Impact: +40% traffic recovery ($3,200/mo value)
     Command: /content-refresh [Drive URL] --scope=heavy

  2. REFRESH: "Best EHR Systems Comparison" — Freshness 22, declining rankings
     Scope: Medium refresh (50%), update vendor list, new pricing data
     Projected Impact: +25% traffic recovery ($2,100/mo value)
     Command: /content-refresh [Drive URL] --scope=medium

THIS QUARTER:
  3. NEW: Create "AI Diagnostics in Precision Medicine" article
     Coverage gap: 2,400/mo volume, KD 62, no existing content
     Command: /cf:brief "AI diagnostics precision medicine"

  4. REFRESH: "HIPAA Compliance Guide 2024" — Freshness 31, high value
     Scope: Medium refresh, update for 2026 regulations
     Projected Impact: Maintain #3 ranking, prevent decline

  5. NEW: Create "Healthcare API Integration Guide" whitepaper
     Coverage gap: 1,800/mo volume, KD 45
     Command: /cf:brief "healthcare API integration"

NEXT QUARTER:
  6-10. [Additional refresh and new content recommendations]

RETIRE:
  - "COVID-19 Telemedicine Temporary Regulations" — Topic expired
    Action: 301 redirect to "Telemedicine ROI Framework"
================================================================
```

## Output

The complete audit report includes:

| Section | Description |
|---------|------------|
| **Inventory Summary** | Total pieces, content types, date distribution, brands |
| **Freshness Scores** | Every piece scored 0-100 with factor breakdown |
| **Top 10 Refresh Candidates** | Ranked by priority (high value + low freshness) |
| **Coverage Gaps** | Missing keywords with opportunity scores |
| **Performance Data** | Traffic, rankings, declining content (if analytics connected) |
| **Recommendations** | Prioritized action list with refresh scope and projected impact |
| **Next Steps** | Specific commands to run for each recommendation |

## MCP Integrations

### Optional (HTTP)
- **Google Analytics** — Traffic, engagement, and conversion data per content URL. Enables performance-based prioritization.
- **Google Search Console** — Ranking positions, impressions, CTR. Identifies declining content for urgent refresh.

### Optional (npx)
- **Google Sheets** — Export audit results to a shared Google Sheet for team review and tracking
- **Google Drive** — Read content inventory directly from Drive folders

### Fallback (No MCP)
Without analytics MCP, the audit provides freshness scoring and coverage gap analysis based on content metadata. This is still highly valuable since the freshness algorithm uses publication dates, statistic currency, link health, and citation recency — none of which require analytics data.

## Troubleshooting

### "Content inventory is empty"
**Cause:** Drive folder URL is incorrect or folder is empty.
**Solution:** Verify the Google Drive folder URL is correct and contains .docx files. If using WordPress, ensure the REST API is publicly accessible.

### "Freshness scores all showing 50"
**Cause:** Content metadata is missing (no publish dates, no statistics detected).
**Solution:** Ensure content files have publish dates in document properties or filenames. For WordPress, publish dates are extracted automatically.

### "Coverage gap analysis shows no gaps"
**Cause:** No target keyword list provided, and existing content covers the auto-detected keyword universe.
**Solution:** Provide a broader target keyword list using `--keywords=target-keywords.csv` with your full keyword strategy.

### "Performance data unavailable"
**Cause:** Google Analytics or Google Search Console MCP not connected.
**Solution:** Run `/cf:integrations` to check connector status. Performance analysis is optional; freshness scoring and gap analysis work without it.

## Limitations

- **Link health check** can be slow for large libraries (200+ outbound links)
- **WordPress audit** requires REST API access (some sites have it disabled)
- **Performance analysis** requires Google Analytics and/or Google Search Console MCP connections
- **Statistics currency** detection uses pattern matching (may miss unusual data formats)
- **CSV input** requires manual column mapping if headers don't match expected format

## Agent Used

None. This skill uses deterministic analysis (freshness scoring algorithm, keyword matching, link checking) without agent-based reasoning. The pipeline-optimizer utility handles the scoring and recommendation logic.

## Related Skills

- **[/content-refresh](../content-refresh/SKILL.md)** — Refresh content identified by the audit
- **[/cf:brief](../cf-brief/SKILL.md)** — Generate briefs for coverage gap topics
- **[/contentforge](../contentforge/SKILL.md)** — Produce new content for gap topics
- **[/cf:calendar](../cf-calendar/SKILL.md)** — Schedule refresh and new content production
- **[/cf:integrations](../cf-integrations/SKILL.md)** — Check which analytics connectors are available

---

**Version:** 3.1.0
**Agent:** None (deterministic analysis)
**Utility:** pipeline-optimizer.md (freshness scoring, recommendation ranking)
**MCP:** Google Analytics (optional), Google Search Console (optional)
**Processing Time:** 10-18 minutes (varies by library size)
**Output:** Audit report with freshness scores, refresh candidates, coverage gaps, recommendations
