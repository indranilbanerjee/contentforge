---
description: Generate a research-backed content brief with keyword data, competitor analysis, search intent, and SEO strategy
argument-hint: "<keyword or topic>"
---

# Content Brief

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate a comprehensive, research-backed content brief from a keyword or topic. Includes keyword research, competitor content analysis, search intent classification, audience insights, a recommended outline, and an actionable SEO strategy — everything needed to produce high-ranking content on the first draft.

## Trigger

User runs `/content-brief` or asks to create a brief, plan content, research a topic for writing, or prepare a content outline.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Keyword or topic** — the primary keyword or topic to build the brief around (e.g., "AI in healthcare 2026", "best project management tools")

2. **Target audience** — who this content is for (e.g., "Healthcare CIOs", "Small business owners", "Marketing managers at B2B SaaS companies")

3. **Additional context** (optional):
   - Content type preference (article, blog, whitepaper, FAQ, video script) — if not specified, the brief recommends the best type based on search intent
   - Competitor URLs to analyze (1-5 pages) — if not provided, top 5 SERP results are used
   - SEO goal: `traffic` (maximize organic visits), `conversions` (bottom-of-funnel intent), or `awareness` (thought leadership)
   - Brand profile name for voice and terminology alignment

## Research Process

### 1. Keyword Research

**If ~~SEO tools are connected (Ahrefs, Similarweb):**
- Pull search volume, keyword difficulty, related keywords, and SERP features automatically

**If tools are not connected:**
- Use web search to research the keyword landscape
- Note: "For precise volume data, connect Ahrefs via `/connect ahrefs`."

Deliver:
- Primary keyword with volume and difficulty signals
- 10-15 secondary and LSI keywords
- Long-tail variations with clear intent
- Question-based keywords (People Also Ask patterns)

### 2. Competitor Content Analysis

Analyze the top 5 ranking pages:
- Word count and content depth
- Structure (headings, sections, content format)
- Key points covered vs. missing
- Unique angles and differentiators
- Citation quality and source types
- E-E-A-T signals (author credentials, original research, experience)

### 3. Search Intent Classification

Determine:
- Primary intent: informational, commercial, transactional, or navigational
- Intent-matched content type recommendation
- SERP feature opportunities (featured snippet, PAA, knowledge panel)
- Content depth requirements based on competing content

### 4. Audience Pain Points & Questions

Map:
- Target audience needs and challenges related to this topic
- Common questions from forums, Reddit, Quora, PAA
- Pain points that the content should address
- Knowledge gaps in existing content

## Brief Output

### Recommended Title
- 2-3 title options optimized for search and click-through
- Character count and keyword placement

### Content Specifications

| Attribute | Recommendation |
|-----------|---------------|
| Content type | Article / Blog / Whitepaper / etc. |
| Word count | Based on competitor analysis |
| Readability | Target grade level |
| Citations | Minimum count |
| Production time | Estimated pipeline duration |

### Recommended Outline

For each section:
- Section title (H2/H3)
- Description of what to cover
- Key points to include
- Word count allocation
- Citation targets
- Keywords to incorporate

### SEO Strategy

- Primary keyword placement plan (title, H1, first 100 words, subheadings)
- Meta title and description recommendations
- Internal linking opportunities
- Featured snippet optimization approach
- Schema markup suggestions
- AI answer engine structuring

### Success Metrics

| Metric | Target |
|--------|--------|
| Quality score | 8.0+ |
| Word count | Per recommendation |
| Citations | Per section targets |
| Readability | Grade level target |
| SEO score | 8.0+ |

## After the Brief

Ask: "Would you like me to:
- Start content production using this brief? (`/create-content`)
- Create briefs for related topics?
- Adjust the brief for a different audience or content type?
- Check if this topic overlaps with existing content? (`/audit-content`)
- Plan a full content calendar around this topic cluster? (`/calendar`)"
