---
name: cf-brief
description: Generate comprehensive content briefs with keyword research, competitor analysis, search intent classification, audience insights, and SEO strategy from a topic or keyword
---

# Content Brief Generator

Generate a comprehensive, research-backed content brief from a keyword or topic. The brief includes keyword data, competitor content analysis, search intent classification, audience pain points, a recommended outline, and an actionable SEO strategy — everything a writer needs to produce high-ranking content on the first draft.

## When to Use

Use `/cf:brief` when:
- You need a **structured content brief** before starting production with `/contentforge`
- You want **data-driven keyword research** to inform topic selection
- You need to **analyze competitor content** to find gaps and differentiation angles
- You're planning a content calendar and need briefs for multiple upcoming pieces
- A client or stakeholder requires a **brief for approval** before production begins
- You want to understand **search intent** before committing to a content type

**For direct content production** (brief + draft in one step), use `/contentforge` instead.
**For multiple briefs in parallel**, run `/cf:brief` for each topic individually (batch brief support planned for v2.2).

## What This Command Does

1. **Keyword Research** — Primary keyword analysis with search volume, keyword difficulty, related keywords, LSI terms, and long-tail opportunities
2. **Competitor Content Analysis** — Analyze top 5 ranking pages for word count, structure, key points covered, content gaps, and unique angles
3. **Search Intent Classification** — Determine whether the query is informational, commercial, transactional, or navigational, and recommend content type accordingly
4. **Audience Pain Points & Questions** — Map target audience needs, common questions, forum discussions, and "People Also Ask" patterns
5. **Recommended Outline** — Generate a structured outline with title options, section descriptions, word count allocations, and citation targets per section
6. **SEO Strategy** — Keyword density targets, meta title/description recommendations, internal linking opportunities, featured snippet potential, and schema markup suggestions
7. **Success Metrics** — Define measurable goals: target word count, minimum citations, readability target, quality score goal, and expected production time

## Required Inputs

**Minimum Required:**
- **Keyword or Topic** — The primary keyword or topic to build the brief around (e.g., "AI in healthcare 2026", "best project management tools")
- **Target Audience** — Who this content is for (e.g., "Healthcare CIOs", "Small business owners", "Marketing managers at B2B SaaS companies")

**Optional:**
- **Content Type** — article, blog, whitepaper, faq, video-script (if not specified, the brief recommends the best type based on search intent)
- **Competitor URLs** — 1-5 specific competitor pages to analyze (if not provided, top 5 SERP results are used)
- **SEO Goals** — Primary goal: `traffic` (maximize organic visits), `conversions` (target bottom-of-funnel intent), or `awareness` (brand visibility and thought leadership)
- **Brand** — Brand profile name to align voice/terminology recommendations in the brief

## How to Use

### Interactive Mode (Recommended)
```
/cf:brief
```
**Prompts you for:**
1. Keyword or topic
2. Target audience
3. Content type (or let the brief recommend one)
4. Competitor URLs (skip to use SERP top 5)
5. SEO goal (traffic / conversions / awareness)

### Quick Mode (All Parameters)
```
/cf:brief "AI diagnostics precision medicine" --audience="Healthcare Executives" --type=article --goal=traffic
```

### With Competitor URLs
```
/cf:brief "best CRM for startups" --audience="Startup founders" --competitors="https://example1.com/crm-guide,https://example2.com/best-crm" --goal=conversions
```

### With Brand Context
```
/cf:brief "cloud security best practices" --audience="IT Directors" --brand=AcmeTech --type=whitepaper
```

## What Happens

### Phase 1: Keyword Research (2-3 minutes)

Gather keyword data for the primary keyword and discover related opportunities.

**Data Collected:**
- **Primary Keyword:** Search volume (monthly), keyword difficulty (0-100), CPC indicator, trend direction
- **Related Keywords:** 10-15 semantically related terms with volume and difficulty
- **LSI Keywords:** 8-12 latent semantic indexing terms for natural content enrichment
- **Long-Tail Opportunities:** 5-8 long-tail variants with lower difficulty and clear intent
- **Question Keywords:** 5-10 question-format queries from "People Also Ask" and forums

**MCP Integration:**
- **Ahrefs (optional, HTTP):** If connected, pulls real search volume, keyword difficulty, SERP features, and related keywords from the Ahrefs API. Data is more accurate and comprehensive than estimates.
- **Similarweb (optional, HTTP):** If connected, pulls traffic estimates for competitor URLs and category benchmarks.
- **Without MCP:** Uses web search analysis, SERP pattern analysis, and heuristic estimation for keyword metrics. Results are directionally accurate but less precise than API data.

**Example Output:**
```
Keyword Research
================================================================

Primary Keyword: "AI diagnostics precision medicine"
  Search Volume: ~2,400/mo (estimated)
  Keyword Difficulty: 62/100 (Medium-High)
  CPC Indicator: $4.80 (commercial value present)
  Trend: Rising (+35% YoY)
  SERP Features: Featured snippet, People Also Ask, Knowledge panel

Related Keywords:
  "AI in medical diagnostics" — ~1,800/mo, KD 55
  "precision medicine AI applications" — ~1,200/mo, KD 48
  "machine learning healthcare diagnostics" — ~900/mo, KD 52
  "AI diagnostic tools for doctors" — ~720/mo, KD 41
  "predictive diagnostics AI" — ~580/mo, KD 38
  ... (10 more)

Long-Tail Opportunities:
  "how AI improves diagnostic accuracy in hospitals" — ~320/mo, KD 28
  "AI diagnostics precision medicine use cases 2026" — ~210/mo, KD 22
  "best AI diagnostic platforms for healthcare" — ~180/mo, KD 31
  ... (5 more)

Question Keywords (People Also Ask):
  "How is AI used in precision medicine?"
  "What are the benefits of AI diagnostics?"
  "Is AI more accurate than doctors at diagnosing?"
  "What diseases can AI diagnose?"
  "How much does AI diagnostic software cost?"
================================================================
```

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

**Aggregate Analysis:**
- **Average Word Count:** Across top 5 results
- **Common Sections:** Topics that appear in 3+ competitor pieces
- **Universal Gaps:** Topics that NO competitor covers well
- **Content Freshness:** Publication dates, last-updated dates
- **Format Patterns:** Listicles vs. guides vs. research-style content

**Example Output:**
```
Competitor Content Analysis
================================================================

Competitor #1: healthtechmagazine.com/ai-diagnostics-guide
  Word Count: 2,850
  Structure: 8 H2 sections (intro, definition, use cases x4, challenges, future)
  Strengths: Comprehensive use cases, good data visualizations
  Gaps: No 2026 data, no cost analysis, no implementation guide

Competitor #2: mckinsey.com/healthcare/ai-diagnostics
  Word Count: 3,200
  Structure: 6 H2 sections (executive summary, market size, applications, barriers, recommendations, appendix)
  Strengths: Strong data and market projections, authoritative tone
  Gaps: Overly theoretical, no practitioner perspective, paywalled sources

... (3 more)

Aggregate Findings:
  Average Word Count: 2,640 (range: 1,800 - 3,200)
  Common Sections: Definition, Use Cases, Benefits, Challenges, Future Outlook
  Universal Gaps:
    - No piece covers 2026 regulatory changes (FDA AI/ML framework update)
    - No practical implementation timeline or cost framework
    - Limited real-world case studies from 2025-2026
    - No comparison of AI diagnostic platforms/vendors
  Format: 4/5 are long-form guides, 1 is research-style
  Freshness: 3/5 published before 2025 (outdated data)
================================================================
```

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

**Example Output:**
```
Search Intent Classification
================================================================

Primary Intent: Commercial Investigation (72% confidence)
Secondary Intent: Informational (28% confidence)

Evidence:
  - SERP shows 3 comparison/guide pages, 2 vendor pages
  - "precision medicine" modifier suggests professional research
  - Featured snippet is a definition paragraph (informational signal)
  - 2 ads present targeting enterprise buyers (commercial signal)
  - People Also Ask skews toward "how" and "what" (informational)

Recommended Content Type: Article (long-form guide)
  Rationale: Mixed intent favors comprehensive guide that educates
  AND positions solutions. Article format matches 4/5 top results.

Alternative: Whitepaper
  If targeting enterprise decision-makers specifically, a whitepaper
  with gated download could capture higher-intent leads.

Word Count Recommendation: 2,500-3,000 words
  Rationale: Avg competitor is 2,640 words. To compete, match or
  exceed by 10-15% while adding unique depth.
================================================================
```

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

**Example Output:**
```
Audience Pain Points & Questions
================================================================

Target Audience: Healthcare Executives (CIOs, CMOs, VP Clinical Ops)

Top Pain Points:
  1. ROI uncertainty — "How do I justify $2M+ investment in AI diagnostics
     to the board when ROI timelines are unclear?"
  2. Integration complexity — "Our EMR vendor says AI integration takes
     18 months. Is that realistic?"
  3. Regulatory compliance — "FDA cleared vs 510(k) vs LDT — which
     pathway should we pursue for our use case?"
  4. Clinical staff resistance — "Radiologists see AI as a threat.
     How do I get buy-in from clinical teams?"
  5. Data readiness — "Our patient data is scattered across 12 systems.
     What data infrastructure do we need first?"

Top Questions:
  1. "What is the actual ROI of AI diagnostics in hospitals?"
  2. "Which AI diagnostic tools are FDA-cleared in 2026?"
  3. "How long does AI diagnostic implementation take?"
  4. "Can AI diagnostics reduce malpractice risk?"
  5. "What patient data is needed for AI diagnostics?"
  6. "How accurate is AI vs radiologists for imaging?"
  7. "What are the HIPAA implications of AI diagnostics?"
  8. "Which hospitals have successfully deployed AI diagnostics?"
  9. "How much does AI diagnostic software cost per bed?"
  10. "What happens when AI makes a wrong diagnosis?"

Desired Outcomes:
  - Clear framework for evaluating AI diagnostic vendors
  - Realistic implementation timeline and budget
  - Peer examples (what other health systems have done)
  - Regulatory compliance roadmap

Language Patterns:
  Uses: "clinical decision support", "evidence-based", "value-based care"
  Avoids: "disruptive", "revolutionary" (executive skepticism of hype)
  Tone: Data-driven, pragmatic, risk-aware
================================================================
```

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

**Example Output:**
```
Recommended Outline
================================================================

Title Options:
  1. "AI Diagnostics in Precision Medicine: A 2026 Executive Guide
     to Implementation, ROI, and Regulatory Compliance"
  2. "How AI Is Transforming Precision Medicine Diagnostics:
     What Healthcare Leaders Need to Know in 2026"
  3. "The Executive's Guide to AI-Powered Diagnostics:
     From Evaluation to Implementation"

Recommended: Option 2 (best keyword placement + audience alignment)

Introduction (200-250 words)
  Hook: Open with a compelling 2026 statistic on AI diagnostic accuracy
  vs human diagnosticians
  Problem: Healthcare executives face pressure to adopt AI but lack
  clear frameworks for evaluation and implementation
  Promise: This guide provides a data-driven roadmap
  Keyword: Include "AI diagnostics precision medicine" in first 100 words
  Citations: 1-2 (recent study + market projection)

Section 1: The State of AI Diagnostics in 2026 (350-400 words)
  H2: "Where AI Diagnostics Stands in 2026"
  - Market size and growth trajectory
  - FDA-cleared tools count and trend
  - Accuracy benchmarks across specialties
  - Adoption rates by health system size
  Keywords: "AI diagnostics", "precision medicine AI applications"
  Citations: 3-4 (market reports, FDA data, benchmark studies)

Section 2: Clinical Use Cases With Proven ROI (400-450 words)
  H2: "Proven AI Diagnostic Use Cases Delivering ROI"
  - Radiology (imaging analysis)
  - Pathology (slide analysis)
  - Cardiology (ECG interpretation)
  - Genomics (variant calling for precision medicine)
  Keywords: "AI diagnostic tools", "machine learning healthcare"
  Citations: 4-5 (case studies, peer-reviewed results)

Section 3: Evaluating AI Diagnostic Platforms (350-400 words)
  H2: "How to Evaluate AI Diagnostic Vendors"
  - Clinical validation criteria
  - Integration requirements (EMR compatibility)
  - Cost models (per-study, subscription, enterprise license)
  - Regulatory status (FDA clearance pathway)
  Keywords: "best AI diagnostic platforms"
  Citations: 2-3 (vendor comparison data, analyst reports)
  ** Gap-filling section: No competitor covers vendor evaluation **

Section 4: Implementation Roadmap (400-450 words)
  H2: "Implementation Timeline: From Pilot to Scale"
  - Phase 1: Data readiness assessment (months 1-3)
  - Phase 2: Pilot program design (months 3-6)
  - Phase 3: Clinical validation (months 6-12)
  - Phase 4: Full deployment (months 12-18)
  Keywords: "AI diagnostic implementation"
  Citations: 2-3 (implementation case studies)
  ** Gap-filling section: Competitors lack practical timelines **

Section 5: Regulatory Compliance Guide (300-350 words)
  H2: "Navigating FDA, HIPAA, and State Regulations"
  - 2026 FDA AI/ML framework updates
  - HIPAA considerations for patient data
  - State-level regulations to watch
  Keywords: "FDA AI diagnostics", "HIPAA AI compliance"
  Citations: 3-4 (FDA guidance, legal analysis)

Section 6: Building Clinical Staff Buy-In (250-300 words)
  H2: "Getting Radiologists and Clinicians on Board"
  - Augmentation vs replacement messaging
  - Training program design
  - Success stories from peer institutions
  Keywords: (natural placement of related terms)
  Citations: 2-3 (change management studies, hospital examples)

Section 7: ROI Framework and Business Case (350-400 words)
  H2: "Calculating the Business Case for AI Diagnostics"
  - Cost categories (software, integration, training, maintenance)
  - Revenue impact (throughput, accuracy, patient volume)
  - ROI timeline by use case
  - Board presentation template link
  Keywords: "ROI AI diagnostics", "AI diagnostics cost"
  Citations: 3-4 (financial analyses, ROI studies)

Conclusion (150-200 words)
  - Recap: Key decision points for executives
  - Forward look: Where AI diagnostics is heading in 2027-2028
  - CTA Options:
    A. "Download our AI Diagnostic Vendor Evaluation Checklist"
    B. "Schedule a consultation with our healthcare AI team"
    C. "Read our case study: How [Hospital] achieved 3.2x ROI"
  Keyword: Include primary keyword in final paragraph

Total Sections: 7 + intro + conclusion
Target Word Count: 2,750-3,000 words
Target Citations: 20-25 sources
================================================================
```

### Phase 6: SEO Strategy (1-2 minutes)

Define the SEO approach for the content piece based on keyword data and competitor analysis.

**Strategy Components:**
- Keyword density targets (primary and secondary)
- Meta title and meta description recommendations (2 options each)
- Internal linking opportunities (suggest related content to link to)
- Featured snippet optimization (format content for snippet capture)
- Schema markup recommendations (Article, FAQ, HowTo)
- Header tag optimization (keyword placement in H2s/H3s)

**Example Output:**
```
SEO Strategy
================================================================

Keyword Density Targets:
  Primary: "AI diagnostics precision medicine" — 1.8-2.2% (5-6 uses)
  Secondary: "AI diagnostic tools" — 0.8-1.0% (2-3 uses)
  Secondary: "precision medicine AI" — 0.5-0.8% (2 uses)

Meta Title Options:
  1. "AI Diagnostics in Precision Medicine: 2026 Executive Guide" (55 chars)
  2. "AI-Powered Precision Medicine Diagnostics: What Leaders Must Know" (64 chars)

Meta Description Options:
  1. "A data-driven guide for healthcare executives evaluating AI
     diagnostics for precision medicine. Covers ROI, implementation
     timelines, and FDA compliance in 2026." (155 chars)
  2. "Healthcare leaders: evaluate AI diagnostic tools with our 2026
     guide covering vendor selection, ROI frameworks, and regulatory
     compliance." (142 chars)

Featured Snippet Opportunity:
  Target query: "How is AI used in precision medicine?"
  Format: Paragraph snippet (40-60 words)
  Placement: Section 1, after H2, as a concise definition paragraph
  Backup: List snippet for "AI diagnostic use cases" in Section 2

Schema Markup: Article (MedicalWebPage subtype)
  - headline, author, datePublished, dateModified
  - medicalAudience: Healthcare Executives
  - about: AI Diagnostics, Precision Medicine

Internal Linking Opportunities:
  - Link to existing content on "healthcare AI trends"
  - Link to vendor comparison page (if exists)
  - Link to case study library
  - Link to regulatory compliance resource
================================================================
```

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
| **Keyword Research** | Primary keyword data, related keywords, LSI terms, long-tail opportunities, question keywords |
| **Competitor Analysis** | Top 5 competitor breakdown with word count, structure, gaps, aggregate findings |
| **Search Intent** | Intent classification with confidence, evidence, content type recommendation |
| **Audience Insights** | Pain points, questions, knowledge gaps, desired outcomes, language patterns |
| **Recommended Outline** | Title options, 5-7 sections with descriptions, word count allocations, citation targets |
| **SEO Strategy** | Keyword density, meta recommendations, featured snippet optimization, schema, internal links |
| **Success Metrics** | Word count target, citation minimum, readability target, quality score goal, production time |
| **Content Brief Checklist** | Pre-production verification items |

## Output Example

```
Content Brief: "AI Diagnostics in Precision Medicine"
Generated: 2026-02-25T14:30:00Z
Processing Time: 12 minutes

Brief Summary:
  Primary Keyword: "AI diagnostics precision medicine" (~2,400/mo, KD 62)
  Recommended Type: Article (long-form guide)
  Target Word Count: 2,750-3,000
  Target Citations: 20-25
  Competitor Avg Word Count: 2,640
  Universal Gap: No competitor covers vendor evaluation or
    implementation timelines

  Outline Sections: 7 + intro + conclusion
  SEO Strategy: 1.8-2.2% primary density, featured snippet target,
    Article schema markup
  Quality Score Goal: 8.5+/10
  Expected Production Time: 25-30 min via /contentforge

Brief saved to:
  Google Drive: ContentForge Briefs/AI-Diagnostics-Precision-Medicine-Brief.md
```

## Workflow: Brief to Production

### Step 1: Generate Brief
```
/cf:brief "AI diagnostics precision medicine" --audience="Healthcare Executives" --type=article --goal=traffic
```

### Step 2: Review and Approve Brief
- Review the outline, keyword targets, and competitor analysis
- Adjust sections, add/remove topics, modify word count
- Share with stakeholders for approval if needed

### Step 3: Produce Content from Brief
```
/contentforge "AI Diagnostics in Precision Medicine: 2026 Executive Guide" --type=article --brand=AcmeMed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine" --brief=ContentForge-Briefs/AI-Diagnostics-Brief.md
```
When a `--brief` parameter is provided, ContentForge uses the brief's outline, keyword map, citation targets, and SEO strategy instead of running its own Phase 1 research from scratch. This produces more targeted content and saves 3-5 minutes of processing time.

### Step 4: Batch Production from Multiple Briefs
Generate briefs for 10 topics, review them, then feed approved briefs into `/batch-process` for parallel production.

## MCP Integrations

### Connected (HTTP) — Optional
- **Ahrefs** — Real keyword data: search volume, keyword difficulty, related keywords, SERP features, backlink data for competitors. Significantly improves keyword research accuracy.
- **Similarweb** — Traffic estimates for competitor URLs, category benchmarks, traffic sources. Improves competitor analysis depth.

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

- **English keywords only** in v2.1 (multilingual keyword research planned for v2.2)
- **One brief at a time** (no batch brief generation yet)
- **Keyword data accuracy** depends on MCP connections (Ahrefs > Similarweb > heuristic estimation)
- **Competitor analysis** limited to publicly accessible pages (paywalled content cannot be analyzed)
- **Brief is a plan, not content** — still requires `/contentforge` to produce the actual piece

## Agent Used

- **Researcher (Agent 01)** — Performs keyword research, SERP analysis, competitor content analysis, and audience research. Uses MCP tools (Ahrefs, Similarweb) when connected, falls back to web search analysis when not.

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** — Produce content from a brief (accepts `--brief` parameter)
- **[/batch-process](../batch-process/SKILL.md)** — Process multiple briefs into content in parallel
- **[/cf:audit](../cf-audit/SKILL.md)** — Audit existing content to identify topics needing new briefs
- **[/cf:calendar](../cf-calendar/SKILL.md)** — Schedule brief-to-production timelines
- **[/content-refresh](../content-refresh/SKILL.md)** — Update existing content (generates refresh brief automatically)

---

**Version:** 2.1.0
**Agent:** Researcher (Agent 01)
**MCP:** Ahrefs (optional, HTTP), Similarweb (optional, HTTP)
**Processing Time:** 10-15 minutes
**Output:** Content brief document following content-brief-template.md
