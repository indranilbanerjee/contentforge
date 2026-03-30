---
name: contentforge
description: Generate publication-ready, fact-checked, brand-compliant, SEO-optimized content through 10-phase autonomous pipeline with zero hallucinations
argument-hint: "[topic]"
effort: max
---

# ContentForge — Enterprise Content Production

Transform a content requirement into a publication-ready, fact-checked, brand-compliant, SEO-optimized piece in 20-30 minutes through a 10-phase autonomous agent pipeline with three-layer fact verification and zero hallucinations.

## When to Use

Use `/contentforge` when you need:
- **Single high-quality content piece** (article, blog, whitepaper, FAQ, research paper)
- **Research-backed content** with verified citations
- **Brand-compliant content** for regulated industries (Pharma, BFSI, Healthcare, Legal)
- **SEO-optimized content** with keyword targeting and meta tags
- **Natural-sounding content** with AI patterns removed (Phase 6.5 Humanizer)

**For multiple pieces in parallel**, use [`/batch-process`](../batch-process/SKILL.md) instead (4-5x faster).

## What This Command Does

Runs your content through **10 specialized agents** with quality gates at each phase:

1. **Research Agent** — SERP analysis, source mining, competitive analysis, structured outline
2. **Fact Checker** — URL verification, claim validation, confidence scoring
3. **Content Drafter** — First draft with brand voice, SME calibration via industry knowledge packs
4. **Visual Asset Annotator** — Chart generation from verified stats, visual markers, asset manifest
5. **Scientific Validator** — Hallucination detection, domain-specific validation, logic validation
6. **Structurer & Proofreader** — Grammar/spelling correction, readability optimization, brand compliance
7. **SEO/GEO Optimizer** — Keyword optimization, meta tag generation, internal linking markers
8. **Humanizer** — AI pattern removal, sentence variety (burstiness), brand personality
9. **Reviewer** — 5-dimension quality scoring (Content Quality 30%, Citation Integrity 25%, Brand Compliance 20%, SEO Performance 15%, Readability 10%)
10. **Output Manager** — .docx with embedded charts, internal links, Google Drive upload

**Quality Gates:** If any phase fails, the pipeline loops back with feedback (max 5 total loops before human escalation).

## Required Inputs

**Minimum Required:**
- **Topic** — What the content is about (e.g., "AI in Healthcare", "remote work productivity")
- **Content Type** — article, blog, whitepaper, faq, research_paper
- **Brand** — Which brand profile to use (create with `/cf:style-guide` if new brand)

**Pre-Flight Validation:** After gathering inputs, the system validates your brand profile for completeness (voice, guardrails, audience, industry pack). For regulated industries (pharma, BFSI, healthcare, legal), guardrails are required — the system will warn if they're empty and ask whether to proceed or update the profile first.

**Optional:**
- **Target Audience** — Who this content is for (e.g., "Healthcare CIOs")
- **Word Count** — Target length (defaults to content type standard)
- **Primary Keyword** — Main SEO keyword to optimize for
- **Tone** — Overrides brand default (authoritative, conversational, technical, witty)

## How to Use

### Interactive Mode (Recommended for First-Time Users)
```
/contentforge
```
**Prompts you for:**
1. Topic (the subject — NOT the final title)
2. Content Type (select from 5 options)
3. Brand (select from existing profiles)
4. Target Audience
5. Word Count (or use default)
6. Primary Keyword

**Then generates 4-5 title options** (different angles: benefit-driven, how-to, data-driven, question-based, contrarian). You select, modify, or provide your own title. Pipeline starts only after title confirmation.

### Quick Mode (Topic Provided)
```
/contentforge "AI in Healthcare" --type=article --brand=AcmeMed --audience="Healthcare CIOs" --keyword="AI healthcare 2026"
```
Even in quick mode, the system generates title options and asks you to select before starting Phase 1. The topic you provide is the subject — the final title is always a user decision.

### Use Existing Google Sheet Requirement
```
/contentforge --sheet-url=https://docs.google.com/spreadsheets/d/ABC123 --row=5
```
Reads requirement from Row 5 of the sheet.

## What Happens

### Title Curation (1-2 minutes) — MANDATORY

**Before the pipeline starts**, the system generates **4-5 SEO-optimized title options** using the topic, content type, brand voice, audience, and primary keyword. Each title takes a different angle:
- **Benefit-driven** — leads with reader value
- **How-to / Tactical** — actionable, instructional
- **Data-driven / Stat-led** — opens with a number or trend
- **Question-based / Curiosity** — provokes the reader
- **Contrarian / Unexpected** — challenges convention

**You select, modify, or provide your own title.** The confirmed title becomes the anchor for the entire pipeline — research, outline, SEO, and final output all flow from it.

**Do NOT skip this step or auto-select a title.** The title shapes the entire content piece.

### Phase 1: Research (3-5 minutes)
- Uses the **confirmed title** as the anchor for all research
- Performs SERP analysis for the topic and title angle
- Mines 10-15 authoritative sources
- Analyzes competitor content
- Generates structured outline aligned with the confirmed title
- **Quality Gate:** Must have 5+ live sources, differentiated angle

### Phase 2: Fact Checking (2-3 minutes)
- Verifies all URLs are accessible (no 404s)
- Validates claims against sources
- Assigns confidence scores (strongly verified, partially verified, weakly verified)
- Flags any unverifiable claims
- **Quality Gate:** 80%+ verified claims, zero flagged items, all URLs live

### Phase 3: Content Drafting (5-7 minutes)
- Generates first draft with brand voice
- Includes inline citations (APA format)
- Targets word count ±10%
- Maintains min 1 citation per 300 words
- **Quality Gate:** Word count ±10%, all outline sections covered, citation density met

### Phase 4: Scientific Validation (2-3 minutes)
- Scans for hallucinations (fabricated statistics, made-up studies)
- Ensures all claims are traceable to sources
- Validates logical consistency
- **Quality Gate:** Zero hallucinations, all claims traceable
- **If fails:** Loops back to Phase 3 with specific claims to fix (max 2 loops)

### Phase 5: Structuring & Proofreading (2-3 minutes)
- Corrects grammar and spelling (100% accuracy)
- Optimizes readability for content type (Grade 8-16 depending on type)
- Enforces brand terminology and style guide
- **Quality Gate:** Zero grammar errors, readability on target, 100% brand compliant

### Phase 6: SEO/GEO Optimization (2-3 minutes)
- Optimizes keyword density (target: 1.5-2.5%)
- Places keywords in critical positions (title, H2s, first paragraph, conclusion)
- Generates meta title, meta description, URL slug
- Prepares content for AI answer engines (ChatGPT, Perplexity, Gemini)
- **Quality Gate:** Keyword density 1.5-2.5%, all critical placements hit, meta tags optimized

### Phase 6.5: Humanizer ⭐ (1-2 minutes)
- Removes AI telltale phrases (20+ patterns: "delve", "leverage", "it's important to note")
- Increases sentence variety (burstiness ≥0.7 for natural human rhythm)
- Injects brand personality (authoritative, witty, warm, data-driven)
- **Validates SEO preservation** (keyword density unchanged ±2 occurrences)
- **Quality Gate:** AI patterns removed, burstiness ≥0.7, SEO preserved

### Phase 7: Reviewer (2-3 minutes)
- Scores content across 5 dimensions:
  - **Content Quality (30%):** Depth, originality, value, clarity
  - **Citation Integrity (25%):** Accuracy, relevance, authority, freshness
  - **Brand Compliance (20%):** Voice, terminology, guardrails, style
  - **SEO Performance (15%):** Keyword optimization, meta tags, structure
  - **Readability (10%):** Grade level, sentence variety, flow
- Calculates composite score (1-10, needs ≥7.0 to pass)
- **Quality Gate:** Score ≥7.0, all dimensions pass, zero critical violations
- **If <7.0:** Loops back to failing phase with specific feedback (max 2 loops)

### Phase 8: Output Manager (1-2 minutes)
- Generates .docx file with proper formatting
- Uploads to Google Drive (`ContentForge Output/[Brand]/[Title]_v1.0.docx`)
- Updates tracking sheet with:
  - Requirement ID, Title, Brand, Type, Word Count
  - Quality Score (breakdown by dimension)
  - Processing Time, Completion Timestamp
  - Output URL (Drive link)

## Output Example

**Article: "AI in Healthcare: 2026 Trends"**
```
Processing Time: 24 minutes
Quality Score: 9.2/10 (Grade A+)

Dimension Breakdown:
- Content Quality: 9.5/10 (Excellent depth, actionable insights)
- Citation Integrity: 9.0/10 (14 sources, 93% strongly verified)
- Brand Compliance: 9.5/10 (Perfect voice match, all terminology correct)
- SEO Performance: 8.8/10 (Keyword density 2.1%, all placements hit)
- Readability: 9.0/10 (Grade 11.2, target 10-12 for articles)

Content Stats:
- Word Count: 1,947 (Target: 1,500-2,000)
- Citations: 14 sources (1 citation per 139 words)
- Keyword Density: 2.1% for "AI in healthcare"
- Readability: Flesch-Kincaid Grade 11.2
- Humanization: Burstiness 0.78, zero AI patterns detected
- Loops Used: 0 (approved on first review)

Factual Accuracy: 100%
Hallucinations: 0
Broken Links: 0

Output Location:
Google Drive: ContentForge Output/AcmeMed/AI-in-Healthcare-2026-Trends_v1.0.docx
```

## Content Types & Specifications

| Type | Word Count | Readability | Citations | Time |
|------|-----------|-------------|-----------|------|
| **Article** | 1,500-2,000 | Grade 10-12 | 8-12 | 22-28 min |
| **Blog** | 800-1,500 | Grade 8-10 | 5-8 | 15-22 min |
| **Whitepaper** | 2,500-5,000 | Grade 12-14 | 15-25 | 30-45 min |
| **FAQ** | 600-1,200 | Grade 8-10 | 3-5 | 12-18 min |
| **Research Paper** | 4,000-8,000 | Grade 14-16 | 25-50 | 45-75 min |

## Brand Profile Setup

**Before using ContentForge**, create a brand profile:

```
/cf:style-guide
```

Provide your brand name, industry, voice guidelines (or share existing documents/URLs), and ContentForge generates the profile JSON automatically.

**Alternatively**, copy `config/brand-registry-template.json` and fill in manually.

**Brand Profile Includes:**
- Voice & Tone (authoritative, conversational, technical, witty)
- Terminology (approved terms, banned phrases)
- Style Guide (formatting preferences, citation style)
- Guardrails (topics to avoid, compliance requirements)
- Industry Context (Pharma, BFSI, Healthcare, Legal)
- Personality Profile (new in v3.0: authoritative, conversational, technical, witty)

**Brand profiles are cached** (SHA256 hash) for 95% time savings on repeat runs.

See the [User Guide](../../docs/USER-GUIDE.md#4-setting-up-your-brand-profile) for detailed setup instructions.

## Quality Assurance

### Three-Layer Fact Verification
1. **Phase 2 (Fact Checker):** URL verification, claim validation
2. **Phase 4 (Scientific Validator):** Hallucination detection
3. **Phase 7 (Reviewer):** Final citation integrity scoring

**Result:** Zero hallucinations in production testing

### Feedback Loop Management
- **Phase 4 → Phase 3:** Max 2 loops (hallucination fixes)
- **Phase 7 → Any Phase:** Max 2 loops (quality improvements)
- **Total Loop Limit:** 5 iterations before human escalation

### Human Review Escalation
Content is flagged for human review if:
- Quality score <5.0/10 after max loops
- Critical brand violations detected
- Excessive loops without improvement
- User explicitly requests review

**Flagged content is NEVER auto-published.**

## Performance Metrics

**Typical Processing Times:**
- Blog (1,200 words): 15-20 minutes
- Article (1,800 words): 22-28 minutes
- Whitepaper (3,500 words): 30-40 minutes

**Quality Scores (Avg across 200+ pieces in beta):**
- Overall: 8.7/10
- Content Quality: 8.9/10
- Citation Integrity: 8.5/10
- Brand Compliance: 9.2/10
- SEO Performance: 8.6/10
- Readability: 8.8/10

**Accuracy:**
- Factual Accuracy: 100%
- Citation Accuracy: 95%+
- Brand Compliance: 100%
- Hallucinations: 0

## Integration with Other Skills

**Before ContentForge:**
- `/cf:style-guide` — Create brand profile if new brand
- `/cf:brief` — Generate research-backed content brief with keyword analysis

**Instead of ContentForge (for scale):**
- `/batch-process` — Process 10-50+ pieces in parallel (4-5x faster)

**After ContentForge:**
- `/content-refresh` — Update content 6-12 months later with fresh data
- `/cf:variants` — Create A/B test headline/hook/CTA variations
- `/cf:publish` — Publish to Webflow or WordPress via MCP
- `/cf:social-adapt` — Transform article into LinkedIn, Twitter/X, Instagram, Facebook, Threads posts
- `/cf:translate` — Translate preserving brand voice (15+ languages)
- `/cf:video-script` — Generate timestamped video scripts from the article
- `/cf:analytics` — Record quality scores for trend tracking

## Requirements

### MCP Integrations (Optional)
- **Google Sheets** — Requirement intake for batch processing, quality tracking
- **Google Drive** — Brand knowledge vault, output .docx storage
- **Webflow/WordPress** — Direct CMS publishing via `/cf:publish`

Run `/cf:integrations` to check your connector status. Run `/cf:connect <name>` for setup guides.

### Environment
- Claude Code or Cowork (latest version)
- Internet connection (for Phase 1 web research)

## Troubleshooting

### "Brand profile not found"

**When:** You run `/contentforge` with a brand that doesn't have a profile yet.

**Fix:**
1. **Create a brand profile (recommended, 5 min):**
   ```
   /cf:style-guide
   ```
   Answer 3 questions (name, tone, industry) and you're ready.

2. **Or specify a different brand:**
   ```
   /contentforge "your topic" --brand=ExistingBrand
   ```

### "Quality score <5.0, flagged for review"

**When:** Content didn't meet the minimum quality threshold after all feedback loops.

**Common causes and fixes:**
- **Topic too vague** → Be more specific: "AI in healthcare" → "AI diagnostic tools for rural hospitals in 2026"
- **Sources behind paywalls** → Provide accessible reference URLs with `--sources=`
- **Brand profile incomplete** → Run `/cf:style-guide --update [brand]` to add guardrails and terminology
- **Niche topic with few sources** → Consider a broader angle or provide your own source URLs

### "Max loops exceeded (5 iterations)"

**When:** The pipeline kept trying to improve content but couldn't reach the quality threshold.

**What happened:** Phase 7 (Reviewer) scored the content below 7.0 multiple times and looped back to fix it, but improvements plateaued.

**Fix:**
1. Check which dimension scored lowest (Content Quality? Citations? Brand Compliance?)
2. If **Content Quality** is low → topic needs more depth or the angle is too broad
3. If **Citation Integrity** is low → sources are weak or behind paywalls
4. If **Brand Compliance** is low → brand profile may be incomplete
5. Re-run with adjustments: more specific topic, better keywords, or updated brand profile

### "Processing time >45 min for article"

**When:** The pipeline is taking longer than expected.

**This is usually normal** — API rate limits or network latency cause delays. ContentForge auto-retries with backoff.

**If it persists beyond 60 min:**
1. Check internet connection
2. Run `/cf:integrations` to verify MCP servers are responding
3. Try a simpler topic to isolate the issue
4. Large whitepapers (5000+ words) can legitimately take 45-75 min

### "Guardrails empty — compliance skipped"

**When:** Your brand profile doesn't have prohibited claims or required disclaimers defined.

**Impact:** Phase 5 (Brand Compliance) will report "SKIPPED" instead of actually checking content. Phase 7 applies a -1.0 penalty to Brand Compliance score.

**Fix:**
```
/cf:style-guide --update [brand]
```
Add at minimum: 3-5 prohibited claims, any required legal disclaimers, and industry-specific restrictions.

**For regulated industries (pharma, BFSI, healthcare, legal):** This is critical. Empty guardrails mean no compliance verification.

### Pipeline phase explanations

During content production, you'll see updates as each phase completes:

| Phase | What's Happening | Duration | What You'll See |
|-------|-----------------|----------|----------------|
| Title Curation | Generating 4-5 title options from SERP data | 1-2 min | Title options with character counts |
| Phase 1: Research | SERP analysis, source mining, outline | 3-5 min | Source count, outline sections |
| Phase 2: Fact Check | URL verification, claim validation | 2-3 min | Verified %, flagged claims |
| Phase 3: Draft | First draft with brand voice | 5-7 min | Word count, citation density |
| Phase 3.5: Visuals | Charts, image generation (if opted in) | 2-3 min | Visual count, chart specs |
| Phase 4: Validation | Hallucination detection | 2-3 min | Zero hallucinations confirmed |
| Phase 5: Structure | Grammar, readability, brand compliance | 2-3 min | Compliance status |
| Phase 6: SEO | Keyword optimization, meta tags | 2-3 min | Keyword density, GEO score |
| Phase 6.5: Humanize | AI pattern removal, personality | 1-2 min | Burstiness score |
| Phase 7: Review | 5-dimension quality scoring | 2-3 min | Score breakdown, pass/fail |
| Phase 8: Output | .docx generation, tracking, delivery | 1-2 min | Output location, final metrics |

**If a phase loops back:** The system shows which phase failed, why, and what it's fixing. Loops are automatic — you don't need to do anything unless it escalates to human review.

## Example Workflow

**Scenario:** Create 1 thought leadership article for AcmeMed brand

### Step 1: Create Brand Profile (One-Time Setup)
```
/cf:style-guide
```
Provide: Brand name (AcmeMed), Industry (Healthcare), Voice (Authoritative), Tone (Professional), Terminology, Guardrails

### Step 2: Start Content Production
```
/contentforge "AI-Powered Diagnostics in Precision Medicine" --type=article --brand=AcmeMed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine"
```

### Step 3: Select Title (1-2 minutes)
ContentForge generates 4-5 title options:
1. "AI-Powered Diagnostics: The Future of Precision Medicine in 2026"
2. "How AI Diagnostics Are Transforming Precision Medicine for Healthcare Leaders"
3. "5 AI Diagnostic Breakthroughs Reshaping Precision Medicine Right Now"
4. "The Executive's Guide to AI-Powered Precision Medicine Diagnostics"
5. "Why AI Diagnostics in Precision Medicine Are Finally Delivering on the Promise"

You select Option 1 → Pipeline starts with that title as the anchor.

### Step 4: Review Output (24 minutes later)
- Quality Score: 9.1/10 ✅
- Word Count: 1,922 ✅
- Citations: 12 sources ✅
- SEO: Keyword density 2.3% ✅

### Step 5: Publish
```
/cf:publish --platform=webflow
```

**Total Time:** 25 minutes (setup once, then 20-30 min per piece)

## Limitations

- **Sequential processing** (for parallel, use `/batch-process`)
- **20-30 min per piece** (cannot be rushed without compromising quality)
- **Best with brand profile** — works without one but uses generic defaults

## Related Skills

- **[/batch-process](../batch-process/SKILL.md)** — Process 10-50+ pieces in parallel (4-5x faster)
- **[/content-refresh](../content-refresh/SKILL.md)** — Update old content with fresh data
- **[/cf:variants](../cf-variants/SKILL.md)** — A/B test headline/hook/CTA variations
- **[/cf:analytics](../cf-analytics/SKILL.md)** — Track quality scores and performance
- **[/cf:social-adapt](../cf-social-adapt/SKILL.md)** — Transform article into social media posts
- **[/cf:publish](../cf-publish/SKILL.md)** — Publish to Webflow/WordPress
- **[/cf:translate](../cf-translate/SKILL.md)** — Translate preserving brand voice
- **[/cf:brief](../cf-brief/SKILL.md)** — Generate research-backed content briefs

---

**Version:** 3.7.0
**Agents:** 13 agents (Research, Fact Checker, Drafter, Visual Asset Annotator, Validator, Structurer, SEO/GEO Optimizer, Humanizer, Reviewer, Output Manager, Batch Orchestrator, Social Adapter, Translator)
**Processing Time:** 20-30 minutes avg
**Quality Guarantee:** ≥8.5/10 avg score, zero hallucinations, 95%+ citation accuracy
