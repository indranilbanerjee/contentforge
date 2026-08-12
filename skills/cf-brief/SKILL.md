---
name: cf-brief
description: "Generate a research-backed content brief from a keyword or topic — keyword data with volume and difficulty, top-5 competitor and E-E-A-T analysis, search-intent classification, audience pain points, a section-by-section outline with word counts and citation targets, plus SEO and AEO/GEO strategy (AI Overview status, answer-block map, entity list). Triggers on \"/contentforge:cf-brief\", \"write a content brief\", \"keyword research for this topic\", \"what should this article cover\", \"analyze competitors before we write\". Uses the researcher agent with Ahrefs/Similarweb MCPs when connected (labeled heuristic estimates otherwise) and aligns terminology to a brand profile when --brand is given. Produces a plan, not the article — feed it to /contentforge:create-content via --brief."
argument-hint: "[topic]"
effort: high
---

# Content Brief Generator

Generate a comprehensive, research-backed content brief from a keyword or topic. The brief includes keyword data, competitor content analysis, search intent classification, audience pain points, a recommended outline, and an actionable SEO strategy — everything a writer needs to produce high-ranking content on the first draft.

## When to Use

Use `/contentforge:cf-brief` when:
- You need a **structured content brief** before starting production with `/contentforge:create-content`
- You want **data-driven keyword research** to inform topic selection
- You need to **analyze competitor content** to find gaps and differentiation angles
- You're planning a content calendar and need briefs for multiple upcoming pieces
- A client or stakeholder requires a **brief for approval** before production begins
- You want to understand **search intent** before committing to a content type

**For direct content production** (brief + draft in one step), use `/contentforge:create-content` instead.
**For multiple briefs**, run `/contentforge:cf-brief` once per topic.

## What This Command Does

1. **Keyword Research** — Primary keyword analysis with search volume, keyword difficulty, related and semantically adjacent terms, and long-tail opportunities
2. **Competitor Content & E-E-A-T Analysis** — Analyze top 5 ranking pages for word count, structure, key points covered, content gaps, unique angles, and E-E-A-T signals (author credentials, original research, first-hand experience)
3. **Search Intent Classification** — Determine whether the query is informational, commercial, transactional, or navigational, and recommend content type accordingly
4. **Audience Pain Points & Questions** — Map target audience needs, common questions, forum discussions, and "People Also Ask" patterns
5. **Recommended Outline** — Generate a structured outline with title options, section descriptions, word count allocations, and citation targets per section
6. **SEO Strategy** — Keyword placement plan, meta title/description recommendations, internal linking opportunities, featured snippet potential, and schema markup suggestions
7. **AEO/GEO Strategy** — AI Overview presence check, citation-worthiness checklist, entity consistency, answer-block recommendations, honest llms.txt note (not a ranking/citation signal)
8. **Success Metrics** — Define measurable goals: target word count, minimum citations, readability target, quality score goal (8.5+)

## Required Inputs

**Minimum Required:**
- **Keyword or Topic** — The primary keyword or topic to build the brief around (e.g., "AI in healthcare 2026", "best project management tools")
- **Target Audience** — Who this content is for (e.g., "Healthcare CIOs", "Small business owners", "Marketing managers at B2B SaaS companies")

**Optional:**
- **Content Type** — article, blog, whitepaper, faq, research_paper, video-script, case-study, newsletter (if not specified, the brief recommends the best type based on search intent)
- **Competitor URLs** — 1-5 specific competitor pages to analyze (if not provided, top 5 SERP results are used)
- **SEO Goals** — Primary goal: `traffic` (maximize organic visits), `conversions` (target bottom-of-funnel intent), or `awareness` (brand visibility and thought leadership)
- **Brand** — Brand profile name to align voice/terminology recommendations in the brief
- **`--no-mcp`** — Skip MCP-backed keyword/competitor lookups and build the brief from heuristic estimates instead (faster, lower fidelity)

## How to Use

### Interactive Mode (Recommended)
```
/contentforge:cf-brief
```
**Prompts you for:**
1. Keyword or topic
2. Target audience
3. Content type (or let the brief recommend one)
4. Competitor URLs (skip to use SERP top 5)
5. SEO goal (traffic / conversions / awareness)

### Quick Mode (All Parameters)
```
/contentforge:cf-brief "AI diagnostics precision medicine" --audience="Healthcare Executives" --type=article --goal=traffic
```

### With Competitor URLs
```
/contentforge:cf-brief "best CRM for startups" --audience="Startup founders" --competitors="https://example1.com/crm-guide,https://example2.com/best-crm" --goal=conversions
```

### With Brand Context
```
/contentforge:cf-brief "cloud security best practices" --audience="IT Directors" --brand=AcmeTech --type=whitepaper
```

## What Happens

### Phase 1: Keyword Research (2-3 minutes)

Gather keyword data for the primary keyword and discover related opportunities.

**Data Collected:**
- **Primary Keyword:** Search volume (monthly), keyword difficulty (0-100), CPC indicator, trend direction
- **Related Keywords:** 10-15 semantically related terms with volume and difficulty (cover the topic's entities and subtopics naturally — do not treat these as terms to sprinkle for density)
- **Long-Tail Opportunities:** 5-8 long-tail variants with lower difficulty and clear intent
- **Question Keywords:** 5-10 question-format queries from "People Also Ask" and forums (these double as AEO answer-block targets in Phase 6.5)

**MCP Integration:**
- **Ahrefs (optional, HTTP):** If connected, pulls real search volume, keyword difficulty, SERP features, and related keywords from the Ahrefs API. Data is more accurate and comprehensive than estimates.
- **Similarweb (optional, HTTP):** If connected, pulls traffic estimates for competitor URLs and category benchmarks.
- **Without MCP:** Uses web search analysis, SERP pattern analysis, and heuristic estimation for keyword metrics. Results are directionally accurate but less precise than API data.

**For a sample keyword-research output transcript, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 1 — Keyword Research".**

**Quality Gate:** Must identify primary keyword with volume estimate, 10+ related keywords, and 5+ long-tail opportunities.

### Phase 2: Competitor Content Analysis (3-5 minutes)

Analyze top 5 ranking pages (or provided competitor URLs) to identify patterns, gaps, and differentiation opportunities.

**For Each Competitor:**
- **URL and Domain Authority:** Page URL, estimated domain strength
- **Word Count:** Total content length
- **Content Structure:** H1/H2/H3 hierarchy and section topics
- **Key Points Covered:** Main arguments, data points, examples used
- **Content Gaps:** What's missing, outdated, or insufficiently covered
- **Unique Angle:** What differentiates this piece from others
- **E-E-A-T Signals:** Named author with credentials? Original data or first-hand experience? Cited primary sources? Review/update dates? These determine what your piece must match or beat to be citable by both Google and AI answer engines

**Aggregate Analysis:**
- **Average Word Count:** Across top 5 results
- **Common Sections:** Topics that appear in 3+ competitor pieces
- **Universal Gaps:** Topics that NO competitor covers well
- **Content Freshness:** Publication dates, last-updated dates
- **Format Patterns:** Listicles vs. guides vs. research-style content

**For a sample competitor-analysis output transcript, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 2 — Competitor Content Analysis".**

**Quality Gate:** Must analyze at least 3 competitor pages with word count, structure, and identified gaps.

### Phase 3: Search Intent Classification (1-2 minutes)

Classify the primary keyword's search intent and recommend the optimal content type.

**Intent Categories:**
- **Informational:** User wants to learn (how-to, what-is, guide). Best content types: article, blog, whitepaper
- **Commercial Investigation:** User is comparing options before a decision. Best content types: article, whitepaper, comparison guide
- **Transactional:** User is ready to act (buy, sign up, download). Best content types: landing page, product page, FAQ
- **Navigational:** User is looking for a specific page or brand. Best content types: FAQ, product page

**Intent Signals Analyzed:**
- SERP composition (what types of pages rank?)
- Query modifiers ("best", "how to", "vs", "buy", "reviews")
- Featured snippet format (paragraph, list, table)
- Ads presence and positioning
- "People Also Ask" question types

**For a sample search-intent classification transcript, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 3 — Search Intent Classification".**

### Phase 4: Audience Pain Points & Questions (2-3 minutes)

Map the target audience's needs, frustrations, and information gaps related to the topic.

**Research Sources:**
- "People Also Ask" patterns from SERP
- Forum discussions (Reddit, Quora, industry forums)
- Review sites and comment sections
- Social media conversations
- Industry reports and surveys

**Analysis Produces:**
- **Top 5 Pain Points:** Ranked by frequency and severity
- **Top 10 Questions:** Questions the audience is actively asking
- **Knowledge Gaps:** What the audience doesn't know they don't know
- **Desired Outcomes:** What success looks like for this audience
- **Language Patterns:** How the audience talks about this topic (terminology, tone)

**For a sample audience pain-points/questions transcript, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 4 — Audience Pain Points & Questions".**

### Phase 5: Recommended Outline Generation (2-3 minutes)

Build a structured content outline that addresses audience needs, fills competitor gaps, optimizes for target keywords, and follows the content type template.

**Outline Includes:**
- 3 title options (SEO-optimized, with primary keyword)
- Introduction hook strategy
- 5-7 main sections with descriptions and target word counts
- Subsection detail where needed
- Citation targets per section (which sources to use where)
- Keyword placement map
- Conclusion with CTA options

**Before generating the outline, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 5 — Recommended Outline Generation", for a full worked example (title options, per-section word counts, keyword/citation targets, gap-filling notes) — reproduce this level of detail.**

### Phase 6: SEO Strategy (1-2 minutes)

Define the SEO approach for the content piece based on keyword data and competitor analysis.

**Strategy Components:**
- Keyword **placement plan** (title, H1, first 100 words, 2-3 H2s, conclusion). Density is advisory only (~1-2% typically emerges from natural coverage) — quality gates check placements, not percentages. Never pad copy to hit a density number.
- Meta title and meta description recommendations (2 options each)
- Internal linking opportunities (suggest related content to link to)
- Featured snippet optimization (format content for snippet capture)
- Schema markup recommendations (Article is the workhorse). Recommend FAQ and HowTo markup for **machine readability**, not for rich results: Google deprecated HowTo rich results in 2023 and in 2023 restricted FAQ rich results to government and health sites. The markup still helps AI engines and other consumers parse the page — just never promise a SERP feature from it.
- Header tag optimization (keyword placement in H2s/H3s)

**For a sample SEO strategy output transcript, read `references/example-output-transcripts.md` (in this skill's directory), section "Phase 6 — SEO Strategy".**

### Phase 6.5: AEO/GEO Strategy (2-3 minutes)

Optimize for AI answer engines (Google AI Overviews, ChatGPT, Perplexity, Gemini, Claude) — where a growing share of discovery happens in 2026. This is not a bolt-on: the brief should tell the writer exactly how to make the piece **citable by machines**, not just rankable.

**Strategy Components:**

1. **AI Overview presence check** — For the primary keyword and the top 3 question keywords, check (via web search) whether Google currently shows an AI Overview and which sources it cites. Record: AI Overview present yes/no, cited domains, and whether any competitor from Phase 2 is cited. If an AI Overview dominates the SERP, plan for citation capture rather than pure blue-link CTR.

2. **Citation-worthiness checklist** — AI engines cite content that is easy to quote. The brief must direct the draft to include:
   - Quotable statistics with clear attribution ("According to [source]'s 2026 survey, X% ...")
   - A crisp definitional sentence for the core concept within the first 150 words (one sentence an engine can lift verbatim)
   - Expert attribution — named author with credentials, or quoted subject-matter experts. When a brand is provided, recommend the byline author from the brand's `author_profiles` (match `expertise` to the topic); if the brand has none, flag the E-E-A-T gap in the brief
   - Original data, benchmarks, or first-hand experience competitors lack (the strongest citation magnet)
   - Publication and last-updated dates visible on the page

3. **Answer-block recommendations** — Map each "People Also Ask" question from Phase 1 to a section: use the question verbatim as an H2/H3, answer it directly in the first 40-60 words below the heading, then elaborate. Recommend definition boxes, comparison tables, and step lists — formats engines extract reliably.

4. **Entity consistency** — List the entities (brand, product, people, concepts) the piece must reference consistently. Names, spellings, and descriptions should match the brand's site, schema markup, and third-party profiles so knowledge graphs and LLMs resolve them to the same entity.

5. **llms.txt awareness** — Note whether the publishing domain has an `llms.txt` file, but frame it honestly: it is an **unadopted community proposal, not a standard** — Google has publicly said it does not use llms.txt, and no major AI engine has confirmed it as an eligibility signal (same stance as the Phase 6 optimizer). If the domain already maintains one, adding this piece to it is optional low-cost housekeeping; if it doesn't, do NOT present creating one as an AI-visibility tactic.

**Output for this phase:** an "AEO/GEO" section in the brief listing AI Overview status per target query, the citation-worthiness items the draft must include, the question-to-answer-block map, the entity list, and the honest llms.txt note.

### Phase 7: Success Metrics Definition (1 minute)

Define measurable targets for the content piece.

```
Success Metrics
================================================================

Production Targets:
  Word Count: 2,750-3,000 words
  Citations: 20-25 sources (min 1 per 150 words)
  Readability: Flesch-Kincaid Grade 11-13 (executive audience)
  Quality Score Goal: 8.5+/10
  Expected Production Time: 25-30 minutes via /contentforge

Performance Targets (post-publish):
  Organic Traffic: Top 10 ranking within 30 days
  Featured Snippet: Capture within 60 days
  Engagement: Avg time on page >4 minutes
  Conversions: Depends on CTA selected
================================================================
```

## Output

The complete content brief document follows the `content-brief-template.md` format and includes:

| Section | Description |
|---------|------------|
| **Keyword Research** | Primary keyword data, related keywords, long-tail opportunities, question keywords |
| **Competitor Analysis** | Top 5 competitor breakdown with word count, structure, gaps, E-E-A-T signals, aggregate findings |
| **Search Intent** | Intent classification with confidence, evidence, content type recommendation |
| **Audience Insights** | Pain points, questions, knowledge gaps, desired outcomes, language patterns |
| **Recommended Outline** | Title options, 5-7 sections with descriptions, word count allocations, citation targets |
| **SEO Strategy** | Keyword placement plan, meta recommendations, featured snippet optimization, schema, internal links |
| **AEO/GEO Strategy** | AI Overview status per query, citation-worthiness items, answer-block map, entity list, honest llms.txt note |
| **Success Metrics** | Word count target, citation minimum, readability target, quality score goal, production time |
| **Content Brief Checklist** | Pre-production verification items |

## Output Example

**Before presenting the final brief summary, read `references/example-output-transcripts.md` (in this skill's directory), section "Final pipeline Output Example" — reproduce its shape with this run's actual values.**

## Workflow: Brief to Production

### Step 1: Generate Brief
```
/contentforge:cf-brief "AI diagnostics precision medicine" --audience="Healthcare Executives" --type=article --goal=traffic
```

### Step 2: Review and Approve Brief
- Review the outline, keyword targets, and competitor analysis
- Adjust sections, add/remove topics, modify word count
- Share with stakeholders for approval if needed

### Step 3: Produce Content from Brief
```
/contentforge:create-content "AI Diagnostics in Precision Medicine: 2026 Executive Guide" --type=article --brand=AcmeMed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine" --brief=ContentForge-Briefs/AI-Diagnostics-Brief.md
```
When a `--brief` parameter is provided, ContentForge uses the brief's outline, keyword map, citation targets, and SEO strategy instead of running its own Phase 1 research from scratch. This produces more targeted content and saves 3-5 minutes of processing time.

### Step 4: Batch Production from Multiple Briefs
Generate briefs for 10 topics, review them, then feed approved briefs into `/contentforge:batch-process`, which runs them as a sequential, checkpointed queue.

## MCP Integrations

### Connected (HTTP) — Optional
- **Ahrefs** (optional connector) — Real keyword data when connected: search volume, keyword difficulty, related keywords, SERP features, backlink data for competitors. Significantly improves keyword research accuracy.
- **Similarweb** (optional connector) — Traffic estimates for competitor URLs when connected: category benchmarks, traffic sources. Improves competitor analysis depth.

### Fallback (No MCP)
Without Ahrefs or Similarweb connected, the brief uses:
- Web search SERP analysis for keyword estimation
- SERP pattern analysis for difficulty scoring
- Heuristic models for volume estimation
- Manual competitor page analysis

Results are directionally accurate but less precise. The brief clearly labels estimated vs API-sourced data.

## Troubleshooting

### "Insufficient keyword data"
**Cause:** Very niche topic with low search volume or no SERP data available.
**Solution:** Broaden the keyword (e.g., "AI diagnostics" instead of "AI diagnostics for rural hospitals in Ohio"). The brief will still find related keywords and questions.

### "Only 2 competitors found"
**Cause:** Very specialized topic with few ranking pages.
**Solution:** Provide competitor URLs manually using `--competitors` flag. The brief can analyze any URL, not just top SERP results.

### "Search intent unclear (50/50 split)"
**Cause:** Keyword has genuinely mixed intent (common for broad topics).
**Solution:** The brief will recommend the content type that serves both intents. Review the recommendation and override with `--type` if you have a strong preference.

### "Brief took >15 minutes"
**Cause:** Network latency or API rate limits (especially with Ahrefs/Similarweb connected).
**Solution:** Briefs auto-retry with backoff. If persists, run without MCP data (`--no-mcp`) for faster generation with estimated data.

## Limitations

- **English keyword research is strongest** — non-English keyword data is less reliable; brand voice for other languages is handled by `/contentforge:cf-translate`
- **One brief at a time** (no batch brief generation)
- **Keyword data accuracy** depends on MCP connections (Ahrefs > Similarweb > heuristic estimation)
- **Competitor analysis** limited to publicly accessible pages (paywalled content cannot be analyzed)
- **Brief is a plan, not content** — still requires `/contentforge:create-content` to produce the actual piece

## Agent Used

- **Researcher (Agent 01)** — Performs keyword research, SERP analysis, competitor content analysis, and audience research. Uses MCP tools (Ahrefs, Similarweb) when connected, falls back to web search analysis when not.

## Related Skills

- **[/contentforge:create-content](../../commands/create-content.md)** — Produce content from a brief (accepts `--brief` parameter)
- **[/contentforge:batch-process](../batch-process/SKILL.md)** — Process multiple briefs into content as a sequential, checkpointed queue
- **[/contentforge:cf-audit](../cf-audit/SKILL.md)** — Audit existing content to identify topics needing new briefs
- **[/contentforge:cf-calendar](../cf-calendar/SKILL.md)** — Schedule brief-to-production timelines
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** — Update existing content (generates refresh brief automatically)

---

**Agent:** Researcher (Agent 01)
**MCP:** Ahrefs (optional, HTTP), Similarweb (optional, HTTP)
**Output:** Content brief document following templates/content-brief-template.md
