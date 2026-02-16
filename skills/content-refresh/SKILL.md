---
name: content-refresh
description: Update existing content with fresh data, current statistics, new sources, and maintain brand compliance while preserving SEO rankings
skill_type: command
---

# Content Refresh Workflow

Re-optimize existing content with updated research, current statistics, new sources, refreshed SEO keywords, and Phase 6.5 humanization — while preserving what's working and maintaining search rankings.

## When to Use

Use `/content-refresh` when:
- Content is 6+ months old and needs updated stats/examples
- Search rankings are declining (lost top 10 position)
- Competitor content has surpassed yours
- Product/service features have changed
- Industry landscape has shifted
- Content scored well originally (≥7.0) but needs freshening

## What This Command Does

1. **Load Existing Content** — Read current .docx from Google Drive
2. **Analyze What to Keep** — Identify evergreen sections, high-performing segments
3. **Research Updates** — Find current statistics, new sources, recent examples
4. **Selective Rewrite** — Update outdated sections, preserve working content
5. **Re-run Quality Gates** — Fact-check new claims, re-humanize, re-score
6. **SEO Preservation** — Maintain target keywords, internal links, meta structure
7. **Version Control** — Save as v1.1, v1.2 (never overwrite v1.0)

## Required Inputs

**Existing Content:**
- Google Drive URL or File ID
- OR: Local .docx file path

**Refresh Scope (select one):**
- **Light Refresh** (20%): Update statistics, examples, citations only
- **Medium Refresh** (50%): Rewrite intro/conclusion, update 3-5 sections, add new research
- **Heavy Refresh** (80%): Complete rewrite using original as outline, keep only evergreen insights

**Optional:**
- New target keywords (if pivoting focus)
- Sections to preserve (mark as "DO NOT EDIT")
- Deadline (for priority ranking in batch)

## How to Use

### Basic Usage
```
/content-refresh https://docs.google.com/document/d/XYZ123
```
**Prompt:** "What refresh scope? (light / medium / heavy)"

### With Scope Specified
```
/content-refresh https://docs.google.com/document/d/XYZ123 --scope=medium
```

### Batch Refresh (multiple pieces)
```
/content-refresh-batch https://docs.google.com/spreadsheets/d/ABC123
```
Sheet columns: `doc_url`, `refresh_scope`, `priority`

## What Happens

### Step 1: Content Analysis (2-3 minutes)
- Load existing content from Google Drive
- Extract metadata (original publish date, current word count, quality score)
- Identify sections: intro, body paragraphs, conclusion, citations
- **Evergreen Detection**: Flag sections that are timeless (definitions, principles, frameworks)
- **Outdated Detection**: Flag statistics >12 months old, broken links, deprecated examples
- Calculate "freshness score" (0-100, based on %outdated)

**Output:**
```
Content Analysis Report
─────────────────────────────────────────────────────
Title: "AI in Healthcare: 2025 Trends and Predictions"
Original Publish: 2025-03-15
Current Word Count: 2,340 words
Original Quality Score: 8.9/10

Freshness Score: 42/100 (Needs Refresh)

Evergreen Sections (Keep):
✓ Para 2: Definition of AI in healthcare
✓ Para 5: Historical context (2010-2020)
✓ Para 8: Ethical considerations framework

Outdated Sections (Update):
⚠ Para 1: Intro references "2025 predictions" (now outdated)
⚠ Para 3: Statistics from 2024 market report
⚠ Para 6: Example of startup acquired in 2025
⚠ Para 10: Conclusion mentions "upcoming 2025 regulations"
⚠ Citations: 6/15 links are broken (404 errors)

Recommendation: Medium Refresh (50% rewrite)
─────────────────────────────────────────────────────
```

### Step 2: Research Phase (Targeted)
- Run Phase 1 (Research Agent) focused ONLY on outdated sections
- Search for: Current statistics (2026), new case studies, recent regulatory changes
- Find replacement sources for broken citations
- **Preserve existing sources** for evergreen content

### Step 3: Selective Rewrite
- **Keep evergreen sections unchanged** (no rewrite)
- **Update outdated sections** with new research
- **Rewrite intro/conclusion** to reflect current year, updated predictions
- **Maintain article structure** (same H2/H3 hierarchy)
- **Preserve internal links** and brand-specific terminology

### Step 4: Re-run Quality Pipelines
- **Phase 2 (Fact-Checker)**: Verify ONLY new claims and updated statistics
- **Phase 4 (Validator)**: Check for hallucinations in rewritten sections
- **Phase 5 (Structurer)**: Ensure refreshed content flows naturally with preserved sections
- **Phase 6 (SEO)**: Maintain keyword density ±0.3%, preserve meta structure
- **Phase 6.5 (Humanizer)**: Re-humanize rewritten sections
- **Phase 7 (Reviewer)**: Re-score (target: ±0.5 points from original score)

### Step 5: Version Control
- Original: `Article-AI-Healthcare_v1.0.docx` (never modified)
- Refresh: `Article-AI-Healthcare_v1.1.docx` (new version)
- Track changes in metadata: "Refreshed 2026-02-17, updated 6 sections, added 4 new sources"

## Refresh Scopes

### Light Refresh (~20% rewrite, 8-12 min)
**What Changes:**
- Update statistics to current year
- Replace 1-2 outdated examples
- Fix broken citation links
- Refresh intro sentence ("As of 2026..." instead of "In 2025...")
- Re-run Phase 6.5 Humanizer only

**What Stays:**
- All structure (H2/H3 headings)
- 80% of original paragraphs
- All evergreen sections
- Target keywords unchanged

**Use Case:** Content is 6-12 months old, mostly accurate, just needs stats updated

### Medium Refresh (~50% rewrite, 15-20 min)
**What Changes:**
- Rewrite intro and conclusion completely
- Update 40-60% of body paragraphs
- Add 3-5 new sections for emerging trends
- Replace 50% of citations with current sources
- Re-run Phases 2, 4, 5, 6, 6.5, 7

**What Stays:**
- Article structure (same H2 sections, order may change)
- Evergreen definitions, frameworks, principles
- Target keywords (may add 2-3 new secondary keywords)

**Use Case:** Content is 12-24 months old, core thesis is valid but needs significant updates

### Heavy Refresh (~80% rewrite, 22-30 min)
**What Changes:**
- Complete rewrite using original as outline only
- New research from scratch (Phase 1 full run)
- Update target keywords based on current search intent
- Add 5-10 new sections
- Replace 80% of citations
- Full 9-phase pipeline (same as new content)

**What Stays:**
- Core topic and brand voice
- 1-2 evergreen sections (definitions, historical context)
- SEO URL slug (to preserve backlinks)

**Use Case:** Content is 24+ months old, industry has changed significantly, needs near-complete overhaul

## SEO Preservation Strategies

### Keyword Density Maintenance
```
Original keyword density: 2.3% for "AI in healthcare"
Target for refresh: 2.0-2.6% (±0.3%)
Action: Phase 6 monitors and adjusts rewritten sections
```

### URL Slug Preservation
```
Original: /blog/ai-in-healthcare-2025-trends
Refreshed: /blog/ai-in-healthcare-2025-trends (SAME URL)
Title updates to: "AI in Healthcare: 2026 Trends and Predictions"
```

### Internal Link Preservation
- All internal links from original content are preserved
- Add new internal links to related updated content
- Never break existing internal link structure

### Meta Description Update
```
Original: "Explore AI in healthcare trends for 2025..."
Refreshed: "Explore AI in healthcare trends for 2026..." (year updated)
```

## Quality Scoring (Refresh vs. Original)

**Target:** Refresh score should be within ±0.5 points of original

**Example:**
- Original: 8.9/10 (Content Quality: 9.2, Citations: 8.5, Brand: 9.0, SEO: 8.8, Readability: 9.0)
- Refreshed: 9.1/10 (Content Quality: 9.3, Citations: 9.0, Brand: 9.0, SEO: 8.9, Readability: 9.2)
- **Result: ✓ Within acceptable range** (+0.2 improvement)

**If refresh scores <8.4** (<0.5 below original):
- Flag for human review
- Identify which dimension dropped (likely Citations or SEO)
- Rerun Phase 2 (Fact-Checker) or Phase 6 (SEO Optimizer)

## Version Tracking

### Metadata in .docx
```
Document Properties:
  Title: AI in Healthcare: 2026 Trends and Predictions
  Version: 1.1
  Original Publish Date: 2025-03-15
  Last Refresh: 2026-02-17
  Refresh Scope: Medium (50%)
  Sections Updated: 6/12
  New Sources Added: 4
  Quality Score: 9.1/10 (was 8.9/10)
  Refreshed By: ContentForge v2.0.0
```

### Filename Convention
```
Original: Article-AI-Healthcare_v1.0.docx
1st Refresh: Article-AI-Healthcare_v1.1.docx
2nd Refresh: Article-AI-Healthcare_v1.2.docx
Major Rewrite: Article-AI-Healthcare_v2.0.docx (Heavy Refresh)
```

### Google Drive Organization
```
ContentForge Output/
└── Article-AI-Healthcare/
    ├── Article-AI-Healthcare_v1.0.docx (Original, 2025-03-15)
    ├── Article-AI-Healthcare_v1.1.docx (Refresh, 2026-02-17)
    └── refresh-comparison-report.txt
```

## Comparison Report

After refresh, generate side-by-side comparison:
```
═══════════════════════════════════════════════════════════════
Content Refresh Comparison Report
═══════════════════════════════════════════════════════════════
Article: AI in Healthcare: 2026 Trends and Predictions
Refresh Date: 2026-02-17
Scope: Medium (50%)

Metrics Comparison:
─────────────────────────────────────────────────────────────
Metric                 │ Original (v1.0) │ Refreshed (v1.1) │ Change
─────────────────────────────────────────────────────────────
Word Count             │ 2,340           │ 2,485            │ +145 (+6%)
Quality Score          │ 8.9/10          │ 9.1/10           │ +0.2
Citations              │ 15              │ 19               │ +4
Broken Links           │ 6 (40%)         │ 0 (0%)           │ -6 (fixed)
Keyword Density        │ 2.3%            │ 2.4%             │ +0.1%
Readability (Grade)    │ 11.2            │ 10.8             │ -0.4 (easier)
Freshness Score        │ 42/100          │ 95/100           │ +53

Sections Changed:
─────────────────────────────────────────────────────────────
✓ Introduction (completely rewritten)
✓ Section 2: Statistics updated (2024 → 2026 data)
✓ Section 4: New case study added (2026 example)
✓ Section 7: Regulatory update (new FDA guidelines)
✓ Section 9: Predictions updated (2026-2028 outlook)
✓ Conclusion (completely rewritten)

Sections Preserved (Evergreen):
─────────────────────────────────────────────────────────────
  Section 1: AI Healthcare Definition
  Section 3: Historical Context (2010-2020)
  Section 6: Ethical Framework

SEO Impact Assessment:
─────────────────────────────────────────────────────────────
Target Keyword: "AI in healthcare"
  Density: 2.3% → 2.4% ✓ (within target)
  First mention: Para 1, Sentence 2 ✓ (unchanged)

Meta Title: "AI in Healthcare: 2026 Trends..."
  Length: 42 chars ✓ (optimal)
  Updated year: 2025 → 2026 ✓

URL Slug: /blog/ai-in-healthcare-2025-trends
  Preserved: ✓ (maintains backlinks)

Internal Links: 8 preserved, 3 added ✓

Estimated SEO Impact: +5-10% traffic (fresher content, fixed broken links)

═══════════════════════════════════════════════════════════════
Recommendation: Publish refreshed version, monitor rankings for 2 weeks
═══════════════════════════════════════════════════════════════
```

## Batch Content Refresh

### Use Case: Quarterly Content Audit
Agency has 50 blog posts, wants to refresh top 20 performers that are 12+ months old.

**Step 1: Prepare Refresh Sheet**
```csv
doc_url,refresh_scope,priority,notes
https://docs.google.com/.../article-1,medium,1,Rankings dropped from #3 to #7
https://docs.google.com/.../article-2,light,2,Just needs stat updates
https://docs.google.com/.../article-3,heavy,3,Topic outdated, needs rewrite
...
```

**Step 2: Run Batch Refresh**
```
/content-refresh-batch https://docs.google.com/spreadsheets/d/ABC123
```

**Step 3: Process (same as /batch-process)**
- Up to 5 concurrent refresh pipelines
- Prioritized by `priority` column
- Progress dashboard shows refresh status
- Completion report with before/after scores

**Time:** 20 pieces × 18 min avg = 6 hours sequential → 1.5 hours parallel = **4x faster**

## Integration with Other Skills

**Before Refresh:**
- `/seo-audit` — Identify which content needs refreshing (declining rankings)
- `/competitor-analysis` — See what competitors added that you're missing

**After Refresh:**
- `/publish-blog` — Push updated content to WordPress/Webflow
- `/performance-tracking` — Monitor SEO impact over 2-4 weeks

## Limitations

- Cannot refresh content not originally created by ContentForge (no baseline quality score)
- Heavy Refresh (80%) is almost same time as new content (use sparingly)
- Requires original .docx file in Google Drive (can't refresh from published URLs alone)

## Success Criteria

**Good Refresh:**
- Quality score within ±0.5 of original
- Freshness score improves to 85-100
- All broken links fixed
- Keyword density maintained
- SEO rankings stable or improve within 2-4 weeks

**Bad Refresh (requires redo):**
- Quality score drops >1.0 point
- Keyword density changes >1%
- Internal links broken
- Brand voice inconsistency

## Agent Used

- **All 9 Agents** (for Heavy Refresh)
- **Agents 2, 4, 5, 6, 6.5, 7** (for Medium Refresh)
- **Agents 6.5, 7** (for Light Refresh)

## Related Skills

- `/batch-process` — Create new content in parallel
- `/generate-variants` — A/B test refreshed vs. original

---

**Version:** 2.0.0
**Phase:** C (Advanced Features)
**Time Savings:** 4x faster for batch, preserves SEO equity, extends content lifespan
