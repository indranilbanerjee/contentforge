# ContentForge — Product Requirements Document (Full Vision)

**Product:** ContentForge — Enterprise Multi-Agent Content Generation Platform
**Author:** Indranil "Neel" Banerjee
**Version:** 1.0
**Date:** February 16, 2026
**Status:** Architecture Complete → Build Phase

---

## 1. EXECUTIVE SUMMARY

ContentForge is an enterprise-grade, multi-agent AI content generation system designed to produce research-backed, brand-compliant, SEO-optimized content at scale. It serves digital marketing agencies managing 50–200+ brands across industries like Pharma, BFSI, and Real Estate.

The system operates as an 8-phase autonomous pipeline — from research and fact-checking through drafting, validation, optimization, and formatted delivery — with quality gates, feedback loops, and brand-specific knowledge integration at every stage.

**Core Value Proposition:** Replace the 6–8 person content production workflow (researcher → writer → editor → SEO specialist → reviewer → formatter) with an AI-orchestrated pipeline that delivers publication-ready, cited, brand-compliant content in minutes instead of days.

---

## 2. PROBLEM STATEMENT

### Current Pain Points
- Content production for 50–200 brands is labor-intensive (6–8 touchpoints per piece)
- Brand voice consistency degrades at scale — different writers produce different voices
- Citation and fact-checking is manual, error-prone, and rarely systematic
- SEO optimization happens as an afterthought, not as part of the creation process
- Scientific/medical content requires specialized validation that's expensive to hire for
- Output formatting, filing, and delivery tracking is entirely manual
- No institutional memory — brand knowledge lives in people's heads, not systems

### Who Feels This Pain
- Digital marketing agency teams managing multi-brand content calendars
- Content leads who spend more time coordinating than strategizing
- Brand managers who can't enforce consistency across distributed teams
- Pharma/regulated industry clients who need citation-verified content

---

## 3. TARGET USERS & PERSONAS

| Persona | Role | Primary Need |
|---------|------|-------------|
| Agency Content Lead | Manages content calendar for 10–50 brands | Throughput + quality consistency |
| Brand Manager (Client-Side) | Owns brand voice and compliance | Brand fidelity + citation accuracy |
| SEO Strategist | Ensures content ranks and converts | Keyword integration + technical SEO |
| Scientific/Medical Reviewer | Validates claims in regulated content | Citation integrity + factual accuracy |
| Agency Operations Lead | Tracks delivery, SLAs, capacity | Pipeline visibility + output tracking |

---

## 4. PRODUCT VISION & PRINCIPLES

### Vision
The intelligent content factory that scales brand-perfect, research-backed content production from 10 to 10,000 pieces per month without proportional headcount growth.

### Design Principles
1. **Quality over speed** — every piece passes quality gates; no content ships below threshold
2. **Citation-first** — all claims are sourced; unsourced claims are flagged, never hidden
3. **Brand memory** — the system learns and remembers each brand's voice, rules, and preferences
4. **Human-in-the-loop where it matters** — automation handles the 90%; humans handle judgment calls
5. **Modular pipeline** — each agent is independent; phases can be swapped, skipped, or extended
6. **Transparent scoring** — every output comes with a quality scorecard; no black boxes

---

## 5. SYSTEM ARCHITECTURE OVERVIEW

### 5.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                     │
│              (SKILL.md — Pipeline Controller)              │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  INPUT LAYER          KNOWLEDGE LAYER       OUTPUT LAYER   │
│  ┌─────────────┐     ┌───────────────┐    ┌────────────┐  │
│  │ Google Sheet │     │ Brand Vault   │    │ .docx Gen  │  │
│  │ (Require-   │     │ (Drive PDFs)  │    │ Drive Org  │  │
│  │  ments)     │     │ Data Sources  │    │ Sheet      │  │
│  │             │     │ Brand Cache   │    │  Update    │  │
│  └─────────────┘     └───────────────┘    └────────────┘  │
│                                                            │
│  ┌──────────── 8-PHASE AGENT PIPELINE ──────────────────┐  │
│  │                                                       │  │
│  │  Phase 1: Research → Phase 2: Fact-Check →            │  │
│  │  Phase 3: Draft → Phase 4: Scientific Validation →    │  │
│  │  Phase 5: Structure & Proofread → Phase 6: SEO/GEO → │  │
│  │  Phase 7: Review & Score → Phase 8: Output & Deliver  │  │
│  │                                                       │  │
│  │  [Quality Gates between each phase]                   │  │
│  │  [Feedback loops: Phase 4→3, Phase 6→5, Phase 7→Any] │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                            │
├──────────────────────────────────────────────────────────┤
│                   INTEGRATION LAYER                        │
│  Google Sheets MCP │ Google Drive MCP │ Web Search/Fetch   │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Technology Stack

| Layer | Phase A (Cowork Plugin) | Phase B (Scale — 50+ brands) |
|-------|------------------------|------------------------------|
| Orchestration | SKILL.md (Claude native) | Cloud Run + task queue |
| Agent Runtime | Claude sequential processing | Multi-LLM orchestration (Claude + Gemini + LLaMA) |
| Knowledge/RAG | JSON brand cache in Drive | Vector DB (Pinecone/Weaviate) |
| Research | Claude web_search + web_fetch | + SerpAPI / Browserless for deep scraping |
| Document Gen | docx library via Claude | Same + templating engine |
| Storage | Google Drive (MCP) | Same + CDN for assets |
| I/O | Google Sheets (MCP) | Same + webhook triggers + dashboard |
| Monitoring | Sheet-based status tracking | Dedicated monitoring dashboard |
| Cost | ₹0 incremental (Claude subscription) | Variable based on API usage |

---

## 6. DETAILED AGENT PIPELINE

### Phase 1 — Research Agent

**Purpose:** Conduct comprehensive web research to build a factual foundation for content creation.

**Inputs:** Topic, primary keywords, secondary keywords, content type, brand industry

**Process:**
- Search top 10 SERP results for primary keyword + topic
- Mine trusted sources (Google Scholar, PubMed for pharma, industry databases)
- Analyze top 5 competitor content pieces (structure, depth, angle, gaps)
- Identify content angle and unique positioning opportunity
- Compile citations with URL, source authority, publication date, key data points

**Output → Research Brief:**
- SERP Analysis (top 10 breakdown: title, URL, word count, structure, strengths, gaps)
- Competitive Content Gap Analysis
- Recommended Content Angle + Rationale
- Structured Outline (H1 → H2 → H3 hierarchy)
- Citation Library (min 8–12 sources with metadata)
- Key Statistics & Data Points (with source attribution)

**Quality Gate 1:**
- ✅ Minimum 5 citable, live sources
- ✅ Top 5 competitor analysis completed
- ✅ Clear, differentiated content angle identified
- ✅ Outline maps to target word count
- ❌ FAIL if: fewer than 5 sources, no competitor analysis, vague angle

---

### Phase 2 — Fact Checker Agent

**Purpose:** Verify all claims, statistics, and citations from the Research Brief before they enter the draft.

**Inputs:** Research Brief from Phase 1

**Process:**
- Cross-reference every claim against 2+ independent sources
- Verify all URLs are live and accessible
- Check recency — flag data older than 2 years (configurable per industry)
- Identify single-source claims and flag for additional verification
- Assign confidence scores to each fact/citation

**Confidence Scoring:**
- **Verified** (3+ corroborating sources, peer-reviewed or authoritative)
- **Likely** (2 corroborating sources, reputable but not peer-reviewed)
- **Unverified** (single source only, needs human review)
- **Flagged** (contradictory sources found, or source credibility concerns)

**Output → Verified Research Brief:**
- Original brief with confidence scores per claim
- Flagged items list with explanation
- Source replacement recommendations for weak citations
- Recency warnings

**Quality Gate 2:**
- ✅ Zero "Flagged" items remain (resolved or removed)
- ✅ All URLs verified as live
- ✅ "Unverified" items explicitly marked for human awareness
- ❌ FAIL if: any "Flagged" items unresolved

---

### Phase 3 — Content Drafter Agent

**Purpose:** Write the first complete draft using verified research, brand voice, and content type structure.

**Inputs:** Verified Research Brief, Brand Profile (from Knowledge Vault), Content Type Template, Target Word Count

**Process:**
- Load brand profile: voice, tone, terminology, guardrails, style rules
- Select content type template (article, blog, whitepaper, FAQ, research paper)
- Draft content section by section following the approved outline
- Integrate citations naturally (inline references, not footnotes unless specified)
- Maintain word count within ±10% of target
- Apply brand-specific terminology and avoid flagged terms

**Output → Draft v1:**
- Complete content piece with inline citations
- Word count report
- Brand voice compliance self-assessment
- List of citations used with placement

**Quality Gate 3:**
- ✅ Word count within ±10% of target
- ✅ All outline sections covered
- ✅ Citations integrated (minimum 1 per 300 words for articles/whitepapers)
- ❌ FAIL if: word count >15% off, missing sections, zero citations

---

### Phase 4 — Scientific/Content Validator Agent

**Purpose:** Re-verify factual accuracy of the drafted content, catch hallucinations, validate logical consistency.

**Inputs:** Draft v1, Verified Research Brief (for cross-reference)

**Process:**
- Re-verify every cited claim against source material
- Identify unsourced claims that snuck into the draft
- Check for logical consistency and argument flow
- Flag potential hallucinations (claims not traceable to any source)
- Validate industry-specific accuracy (pharma dosage claims, financial data, legal references)
- Check for outdated information

**Output → Validated Draft:**
- Draft with validation annotations
- Hallucination flags (if any)
- Unsourced claims list
- Accuracy confidence score

**Quality Gate 4:**
- ✅ Zero hallucinations
- ✅ All claims traceable to verified sources
- ✅ Logic and argument flow validated
- 🔄 LOOP: Returns to Phase 3 if critical issues found (max 2 loops)
- ❌ FAIL to human review if: persistent hallucinations after 2 loops

---

### Phase 5 — Structurer & Proofreader Agent

**Purpose:** Polish the validated draft — restructure for readability, proofread, apply formatting standards, ensure brand compliance.

**Inputs:** Validated Draft, Brand Profile, Content Type Template

**Process:**
- Restructure for optimal readability (paragraph length, transition sentences, flow)
- Apply formatting: headers, subheaders, bullet points where appropriate
- Proofread: grammar, spelling, punctuation, style consistency
- Check brand compliance: terminology, banned words, required disclaimers
- Standardize citation format per brand guidelines
- Ensure accessibility: reading level appropriate to audience

**Output → Polished Draft:**
- Fully formatted and proofread content
- Readability score (Flesch-Kincaid or equivalent)
- Brand compliance checklist (pass/fail per rule)
- Changes log (what was restructured and why)

**Quality Gate 5:**
- ✅ Zero grammatical/spelling errors
- ✅ Readability score within target range
- ✅ Brand compliance checklist all-pass
- ✅ Formatting matches content type template
- ❌ FAIL if: brand compliance failures

---

### Phase 6 — SEO/GEO Optimizer Agent

**Purpose:** Optimize content for search engine visibility and AI discoverability without compromising readability.

**Inputs:** Polished Draft, Primary Keywords, Secondary Keywords

**Process:**
- Verify keyword placement: title, H1, first 100 words, at least 2 H2s, conclusion
- Check keyword density: primary (1.5–2.5%), secondary (0.5–1%)
- Generate: meta title (≤60 chars), meta description (≤155 chars), URL slug
- Check internal linking opportunities (if brand content library available)
- Evaluate readability vs. keyword integration balance
- Add schema markup recommendations (FAQ schema, article schema, etc.)
- GEO optimization: structure for AI citation (clear claims, attributable statements)

**Output → Optimized Content + SEO Scorecard:**
- Final optimized content
- SEO Scorecard: keyword placement ✅/❌, density report, meta tags, slug
- GEO readiness assessment
- Schema markup recommendations

**Quality Gate 6:**
- ✅ Primary keyword in title, H1, first 100 words, conclusion
- ✅ Density within range
- ✅ Meta title ≤60 chars, meta description ≤155 chars
- ✅ Readability not degraded vs. Phase 5 output
- 🔄 LOOP: Returns to Phase 5 if SEO score below threshold (max 1 loop)

---

### Phase 7 — Reviewer Agent (Final Quality Gate)

**Purpose:** Comprehensive final review — the last checkpoint before output. Scores content across all dimensions and makes the go/no-go decision.

**Inputs:** Optimized Content, SEO Scorecard, Original Requirements, Brand Profile

**Process:**
- Verify all original requirements met (topic, word count, content type, keywords)
- Final brand compliance review
- Review citation integrity one last time
- Check for guardrail violations (brand-specific prohibited content)
- Score across 5 dimensions

**Scoring Dimensions (1–10 each):**
1. **Content Quality** — depth, originality, value to reader
2. **Citation Integrity** — accuracy, recency, authority of sources
3. **Brand Compliance** — voice, terminology, guidelines adherence
4. **SEO Performance** — keyword optimization, meta tags, structure
5. **Overall Score** — weighted average (configurable per brand)

**Decision Logic:**
- **Score ≥ 7.0** → Proceed to Phase 8 (Output)
- **Score 5.0–6.9** → Loop back to appropriate phase with specific feedback
- **Score < 5.0** → Flag for human review, do NOT auto-publish

**Output → Review Report:**
- Scores per dimension with justification
- Decision: Approved / Loop / Human Review
- Specific feedback for loop iterations (if applicable)

---

### Phase 8 — Output Manager Agent

**Purpose:** Generate the final deliverable, organize in Drive, update tracking sheet.

**Inputs:** Approved Content, Quality Scores, Original Requirements, Brand Config

**Process:**
- Generate formatted .docx file with proper headers, footers, citation formatting
- Create/navigate Drive folder structure: `ContentForge/{Brand}/{ContentType}/{Year}/{Month}/`
- Upload .docx to correct folder
- Update Google Sheet requirement row: Status → "Completed", Output Link, Scores, Timestamp
- If flagged for human review: Status → "Pending Human Review" with notes

**Output:**
- Formatted .docx in organized Drive folder
- Updated requirement sheet with link, scores, metadata
- Pipeline execution log

---

## 7. KNOWLEDGE INFRASTRUCTURE

### 7.1 Brand Knowledge Vault

**Drive Structure:**
```
ContentForge-Knowledge/
├── {Brand Name}/
│   ├── Brand-Guidelines/         ← PDFs: voice, tone, style guides
│   ├── Reference-Content/        ← Exemplary past content
│   ├── Guardrails/               ← Prohibited terms, compliance rules
│   └── brand-profile.json        ← Auto-generated cache (system-managed)
```

**brand-profile.json Schema:**
```json
{
  "brand_name": "string",
  "industry": "string",
  "voice": { "tone": "string", "formality": "string", "personality_traits": [] },
  "terminology": { "preferred": {}, "prohibited": [], "industry_specific": {} },
  "citation_rules": { "format": "string", "min_per_300_words": "number", "preferred_sources": [] },
  "guardrails": { "prohibited_claims": [], "required_disclaimers": [], "compliance_notes": "string" },
  "content_patterns": { "typical_structure": "string", "avg_word_count": "number" },
  "last_updated": "ISO timestamp",
  "source_docs_hash": "string (for cache invalidation)"
}
```

### 7.2 Data Source Vault (Trusted Sources Registry)

**Master Google Sheet — "Brand Registry":**

**Sheet 1 — Brands:**
| Brand Name | Industry | Knowledge Vault Drive Link | Data Source Vault Link | Default Guidelines | Active |
|---|---|---|---|---|---|

**Sheet 2 — Data Sources:**
| Brand Name | Source URL | Source Type | Citation Priority | Industry | Reliability Score | Notes |
|---|---|---|---|---|---|---|

Source Types: Academic Journal, Government Database, Industry Report, News (Tier 1), News (Tier 2), Company Official, Encyclopedia

### 7.3 RAG Implementation

**Phase A (Plugin):**
- At run start: agent reads brand's Drive folder, processes PDFs/docs
- Creates/updates brand-profile.json as cached summary
- Subsequent runs read cache first; re-process only if source docs modified (hash comparison)
- No external vector DB needed — Claude's context window handles per-run knowledge loading

**Phase B (Scale):**
- Persistent vector DB (Pinecone/Weaviate) with brand-partitioned indexes
- Embeddings updated on Drive file change (webhook trigger)
- Semantic retrieval for relevant brand knowledge chunks per content piece
- Cross-brand knowledge isolation enforced at query level

---

## 8. INPUT/OUTPUT SPECIFICATIONS

### 8.1 Input — Requirement Sheet Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| Row ID | Auto | Yes | Unique identifier |
| Brand Name | String | Yes | Must match Brand Registry |
| Topic | String | Yes | Content topic/title |
| Primary Keywords | String | Yes | Comma-separated |
| Secondary Keywords | String | No | Comma-separated |
| Content Type | Enum | Yes | Article / Blog / Whitepaper / FAQ / Research Paper |
| Target Word Count | Number | Yes | Target length |
| Priority | Enum | No | High / Medium / Low |
| Special Instructions | Text | No | Brand-specific notes for this piece |
| Status | Auto | — | Queued / In Progress / Completed / Pending Human Review / Failed |
| Output Link | Auto | — | Drive link to .docx |
| Quality Score | Auto | — | Overall score (1–10) |
| Content Quality | Auto | — | Dimension score |
| Citation Integrity | Auto | — | Dimension score |
| Brand Compliance | Auto | — | Dimension score |
| SEO Score | Auto | — | Dimension score |
| Actual Word Count | Auto | — | Final word count |
| Completed At | Auto | — | Timestamp |
| Notes | Auto | — | System notes, human review notes |

### 8.2 Output — Drive Structure

```
ContentForge/
├── {Brand Name}/
│   ├── Articles/
│   │   └── 2026/
│   │       └── 02-February/
│   │           └── topic-slug-2026-02-16.docx
│   ├── Blog-Posts/
│   ├── Whitepapers/
│   ├── FAQs/
│   └── Research-Papers/
```

### 8.3 Output — .docx Format

- Header: Brand name + content type
- Title page (whitepapers/research papers only)
- Table of contents (whitepapers/research papers only)
- Body content with proper heading hierarchy (H1/H2/H3)
- Inline citations with numbered references
- References/Bibliography section
- Footer: "Generated by ContentForge | {Date} | Quality Score: {Score}/10"
- Appendix: SEO Scorecard + Quality Report (optional, configurable per brand)

---

## 9. QUALITY FRAMEWORK

### 9.1 Scoring Thresholds (Configurable)

```json
{
  "minimum_pass_score": 7.0,
  "human_review_threshold": 5.0,
  "dimension_weights": {
    "content_quality": 0.30,
    "citation_integrity": 0.25,
    "brand_compliance": 0.20,
    "seo_performance": 0.15,
    "readability": 0.10
  },
  "industry_overrides": {
    "pharma": { "citation_integrity": 0.35, "content_quality": 0.25 },
    "bfsi": { "brand_compliance": 0.30, "citation_integrity": 0.25 }
  }
}
```

### 9.2 Feedback Loop Rules

| Condition | Action | Max Loops |
|-----------|--------|-----------|
| Scientific validation fails | Return to Phase 3 (Drafter) | 2 |
| SEO score below threshold | Return to Phase 5 (Structurer) | 1 |
| Overall score 5.0–6.9 | Return to weakest-scoring phase | 2 |
| Overall score < 5.0 | Flag for human review | 0 |
| Hallucination detected | Return to Phase 3 with explicit flags | 2 |
| Brand compliance failure | Return to Phase 5 with brand rules | 1 |

### 9.3 Guardrail System

- **Hard Guardrails** (auto-reject): Hallucinations, fabricated citations, prohibited terms, compliance violations
- **Soft Guardrails** (flag + continue): Readability below target, word count ±10–15%, single-source claims
- **Brand-Specific Guardrails**: Loaded from brand-profile.json per run

---

## 10. IMPLEMENTATION PHASES

### Phase A — Cowork Plugin (Current Build)

**Scope:** Fully functional single-run pipeline
**Timeline:** 2–4 weeks to build + test
**Cost:** ₹0 incremental (Claude Pro/Team subscription only)

**Capabilities:**
- Complete 8-phase pipeline execution within single Claude session
- Brand knowledge loading from Google Drive per run
- Web research via Claude native search + fetch
- Google Sheets I/O via MCP
- Google Drive organization via MCP
- .docx generation via docx library
- Brand profile caching (JSON in Drive)
- Quality scoring and feedback loops
- Single content piece per run (sequential processing)

**Limitations:**
- No concurrent/batch processing
- No persistent vector DB (context window RAG only)
- No background processing (user must wait)
- Scale ceiling: ~10–20 pieces/day (sequential)

**Tech Stack:**
- SKILL.md (orchestrator) + 8 agent prompt files
- Google Sheets MCP server
- Google Drive MCP server
- Claude web_search + web_fetch (native)
- docx npm library

### Phase B — Batch Processing Layer

**Trigger:** When >20 pieces/day needed or >50 brands active
**Timeline:** 4–8 weeks after Phase A proven
**Cost:** ~₹5,000–15,000/month (cloud infrastructure)

**Additions:**
- Cloud Run backend for async pipeline execution
- Task queue (Cloud Tasks / Pub-Sub) for batch processing
- Webhook triggers from Google Sheets (new row → auto-queue)
- Parallel processing: 5–10 content pieces simultaneously
- Persistent brand profile storage (Firestore)
- Basic monitoring dashboard (Looker Studio on Sheet data)

### Phase C — Enterprise Scale

**Trigger:** When >200 brands or >100 pieces/day or client-facing SaaS needed
**Timeline:** 3–6 months after Phase B
**Cost:** ₹25,000–75,000/month

**Additions:**
- Vector DB (Pinecone/Weaviate) for persistent RAG
- Multi-LLM orchestration (Claude primary + Gemini/LLaMA for cost optimization)
- Real-time monitoring dashboard
- API layer for external integrations
- Multi-tenant architecture with RBAC
- Credit-based usage metering
- White-label capability
- Client portal for review/approval workflows

---

## 11. PROJECT STRUCTURE (Plugin Build)

```
contentforge-plugin/
├── SKILL.md                          # Orchestrator — pipeline controller + routing logic
├── README.md                         # Marketplace listing + setup guide
├── config/
│   ├── brand-registry-template.json  # Template for brand configuration
│   ├── data-sources-template.json    # Template for trusted sources
│   └── scoring-thresholds.json       # Quality gate configurations
├── agents/
│   ├── 01-researcher.md              # Research agent prompt + instructions
│   ├── 02-fact-checker.md            # Fact verification prompt
│   ├── 03-content-drafter.md         # Writing agent prompt
│   ├── 04-scientific-validator.md    # Validation prompt
│   ├── 05-structurer-proofreader.md  # Editing agent prompt
│   ├── 06-seo-geo-optimizer.md       # SEO optimization prompt
│   ├── 07-reviewer.md               # Final review + scoring prompt
│   └── 08-output-manager.md         # Delivery + filing prompt
├── templates/
│   ├── research-brief.md             # Research output format
│   ├── quality-scorecard.md          # Scoring template
│   ├── content-types/
│   │   ├── blog-structure.md
│   │   ├── whitepaper-structure.md
│   │   ├── faq-structure.md
│   │   ├── research-paper-structure.md
│   │   └── article-structure.md
│   └── requirement-sheet-schema.json
├── utils/
│   ├── drive-folder-manager.md       # Auto folder creation logic
│   ├── citation-formatter.md         # Citation standardization rules
│   └── brand-cache-manager.md        # Brand profile caching logic
└── examples/
    ├── sample-run.md                 # Example full pipeline run walkthrough
    └── sample-brand-setup.md         # How to onboard a new brand
```

---

## 12. METRICS & SUCCESS CRITERIA

### Phase A Success Metrics
- Pipeline produces publication-ready content for 1 brand in <15 minutes
- Quality score ≥7.0 on 80%+ of outputs without human intervention
- Citation accuracy ≥95% (all citations verified and live)
- Brand voice consistency rated "acceptable" by brand manager
- Zero hallucinations in published content

### Scale Metrics (Phase B/C)
- 50+ content pieces/day with ≥7.0 quality score
- <5% human review rate
- 200+ brands onboarded with isolated knowledge vaults
- Average pipeline time <10 minutes per piece
- Cost per content piece <₹50 at scale

---

## 13. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AI hallucinations in published content | Critical | Medium | 3-layer verification (Phase 2 + 4 + 7), hard guardrail auto-reject |
| Citation URLs go dead post-publication | Medium | High | URL verification at generation time, periodic re-check capability |
| Brand voice drift at scale | High | Medium | Persistent brand profiles, exemplar content comparison, human spot-checks |
| Claude context window limits for large brands | Medium | Medium | Chunked knowledge loading, cached brand profiles, Phase B vector DB |
| Google API rate limits during batch processing | Medium | High (Phase B) | Request throttling, exponential backoff, queue management |
| Cost escalation with multi-LLM orchestration | Medium | Medium (Phase C) | Cost-per-piece monitoring, LLM routing by task complexity |
| Over-reliance on single AI provider (Anthropic) | High | Low | Phase C multi-LLM architecture as hedge |

---

## 14. FUTURE ROADMAP

### Near-Term (Post Phase A)
- Content calendar integration (auto-schedule pipeline runs)
- Human review workflow (approve/reject/edit in Google Docs → auto-update sheet)
- Content performance tracking (post-publish SEO rank monitoring)

### Medium-Term (Phase B/C Era)
- Multi-language content generation
- Visual content suggestions (image briefs for designers)
- A/B content variant generation (same topic, different angles)
- Client-facing portal for review and approval
- Content repurposing pipeline (article → social posts → email snippets)

### Long-Term (Platform Play)
- ContentForge as standalone SaaS product
- Plugin marketplace for custom agent modules
- Industry-specific agent packs (Pharma Pack, Finance Pack, Legal Pack)
- White-label licensing for other agencies
- Content analytics and optimization intelligence layer

---

## 15. OPEN QUESTIONS & DECISIONS NEEDED

1. **Citation format standardization** — APA, Chicago, or custom per brand? (Current: configurable per brand)
2. **Human review UX** — Google Docs commenting vs. dedicated review interface? (Phase A: Docs, Phase C: custom)
3. **Content versioning** — keep all drafts or only final? (Current: final only, with quality log)
4. **Multi-language priority** — which languages after English? (Hindi? Regional?)
5. **Pricing model for SaaS** — per-piece, per-brand, or credit-based? (Phase C decision)

---

*This document serves as the complete product blueprint for ContentForge. It should be used as the foundation for detailed technical specifications, sprint planning, and build execution.*
