---
description: Run the full 9-phase content production pipeline — research, draft, fact-check, humanize, and publish
argument-hint: "<topic or title> [content type]"
---

# Create Content

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Transform a content requirement into a publication-ready, fact-checked, brand-compliant, SEO-optimized piece through a 9-phase autonomous agent pipeline with three-layer fact verification and zero hallucinations.

## Trigger

User runs `/create-content` or asks to write, draft, create, or produce content (articles, blog posts, whitepapers, FAQs, or research papers).

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Topic or title** — what the content is about (e.g., "AI in Healthcare: 2026 Trends")

2. **Content type** — one of:
   - Article (1500-3000 words)
   - Blog post (800-1500 words)
   - Whitepaper (3000-6000 words)
   - FAQ (structured Q&A format)
   - Research paper (2000-5000 words with methodology)

3. **Brand** — which brand profile to use for voice and compliance. If not specified, ask: "Which brand should I use? Or create a new one with `/brand-setup`."

4. **Target audience** (optional) — who this content is for (e.g., "Healthcare CIOs", "Small business owners")

5. **Additional context** (optional):
   - Primary keyword for SEO optimization
   - Word count target (overrides content type default)
   - Tone override (authoritative, conversational, technical, witty)
   - Specific sources or references to include
   - Competitor URLs to differentiate from

## The 9-Phase Pipeline

Each phase has a quality gate. If any phase fails, the pipeline loops back with feedback (max 5 loops before human escalation).

### Phase 1: Research Agent
- SERP analysis of top-ranking content for the topic
- Source mining — identify 10+ authoritative sources
- Competitive content analysis — what exists, what's missing
- Structured outline with section descriptions and citation targets

### Phase 2: Fact Checker (Layer 1)
- URL verification — confirm all sources are accessible and current
- Claim validation — cross-reference key claims against multiple sources
- Confidence scoring — rate each fact claim (verified, likely, unverified)

### Phase 3: Content Drafter
- First draft with brand voice applied throughout
- Inline citations for every factual claim
- Word count targeting within 10% of specification
- Natural flow with transitions between sections

### Phase 4: Scientific Validator (Layer 2)
- Hallucination detection — flag any claim not backed by cited sources
- Unsourced claim flagging — identify statements presented as fact without evidence
- Logic validation — check argument flow and reasoning consistency

### Phase 5: Structurer & Proofreader
- Grammar and spelling correction
- Readability optimization (target: grade 8-10 for general, grade 12+ for technical)
- Brand compliance check (terminology, restricted words, mandatory disclaimers)
- Formatting standardization

### Phase 6: SEO/GEO Optimizer
- Primary keyword optimization (title, H1, first 100 words, subheadings)
- Meta title and description generation
- Internal linking suggestions
- AI answer engine readiness (structured for Google AI Overviews, Perplexity)
- GEO score (1-10) for citation-worthiness

### Phase 6.5: Humanizer
- AI pattern removal — eliminate predictable sentence structures, filler phrases, hedge words
- Sentence variety (burstiness) — mix short punchy sentences with longer complex ones
- Brand personality injection — apply configured personality profile
- Industry-specific AI telltale removal

### Phase 7: Reviewer (Layer 3)
- 5-dimension quality scoring:
  - Content Quality (30%) — depth, accuracy, originality
  - Citation Integrity (25%) — source quality, link health, attribution
  - Brand Compliance (20%) — voice match, terminology, restrictions
  - SEO Performance (15%) — keyword usage, meta tags, structure
  - Readability (10%) — flow, clarity, engagement
- Composite score with pass/fail gate (7.0 minimum)
- Specific revision recommendations if below threshold

### Phase 8: Output Manager
- Generate .docx output with professional formatting
- Upload to ~~knowledge base (Google Drive) if connected
- Update tracking sheet with production metadata
- Generate social-ready excerpt for promotion

## Output

The final output includes:
- Publication-ready content piece with inline citations
- Quality scorecard (5 dimensions + composite)
- SEO meta package (title, description, keywords)
- Production metadata (word count, reading time, sources used, pipeline duration)

## After Content Creation

Ask: "Would you like me to:
- Promote this on social media? (`/social-adapt`)
- Publish to your CMS? (`/publish`)
- Translate for other markets? (`/translate`)
- Create A/B headline variants? (`/variants`)
- Generate a content brief for a related topic? (`/brief`)
- Run batch production for multiple topics? (`/batch-process`)"
