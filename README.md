# ContentForge — Enterprise Multi-Agent Content Production Pipeline

**Version:** 3.1.0
**Platform:** Claude Code & Cowork
**Status:** Production-Ready

> Transform content requirements into publication-ready, fact-checked, brand-compliant, SEO-optimized content in 20-30 minutes through a 12-agent autonomous pipeline with 18 skills. **New in v3.0:** Social adaptation, CMS publishing, content briefs, A/B variants, translation, video scripts, content audits, calendars, style guides, analytics dashboards, connector discovery, and upgraded agents with AI Overview optimization, comparative scoring, personality profiles, and industry-specific humanization.

### What's New in v3.0.0

- **📱 Social Adaptation** — Transform articles into LinkedIn, Twitter/X, Instagram, Facebook, Threads posts with platform-specific formatting
- **🌐 CMS Publishing** — Push content to Webflow and WordPress directly via MCP, with HTML export fallback
- **🌍 Translation** — Translate content preserving brand voice across 15+ languages with 3 localization levels
- **🎬 Video Scripts** — Generate timestamped scripts for YouTube, TikTok, Instagram Reels, and explainers
- **🔬 Content Briefs** — Generate research-backed briefs with keyword analysis, competitor gaps, and outlines
- **📊 Analytics Dashboard** — Track quality scores over time, phase timing, brand patterns, and trend analysis
- **🔀 A/B Variants** — Generate 3-10 headline, hook, and CTA variants with composite scoring
- **📋 Content Audits** — Score content freshness (0-100), identify decay, find coverage gaps
- **📅 Content Calendar** — Plan production schedules with deadline tracking and Google Calendar sync
- **🎨 Style Guides** — Import brand voice from documents/URLs, generate brand profile JSON
- **📄 Custom Templates** — Create content type templates beyond the 5 built-in types
- **🔌 Connector Discovery** — `/cf:integrations` dashboard and `/cf:connect` guided setup for 22 connectors
- **🤖 AI Overview Optimization** — SEO optimizer now structures content for Google AI Overviews and Perplexity
- **📈 Comparative Scoring** — Reviewer shows percentile ranking against brand's historical content
- **🎭 Personality Profiles** — Humanizer supports 4 configurable profiles: authoritative, conversational, technical, witty
- **🏭 Industry Patterns** — Humanizer removes industry-specific AI telltale phrases for healthcare, finance, tech, legal, education

---

## What is ContentForge?

ContentForge is an enterprise-grade content generation system that replaces 6-8 person content workflows with a coordinated multi-agent AI pipeline. Unlike single-prompt tools, ContentForge runs content through 9 specialized quality gates with three-layer fact verification, preventing hallucinations and ensuring brand compliance.

**Target Users:**
- Digital marketing agencies managing 50-200 brands
- In-house marketing teams with high content volume
- Content operations in regulated industries (Pharma, BFSI, Healthcare, Legal)
- Enterprise brands requiring consistent quality at scale

**What Makes ContentForge Different:**
- **Zero Hallucinations:** Three-layer verification (Phases 2, 4, 7) catches fabricated data
- **95%+ Citation Accuracy:** All claims traceable to verified sources
- **Brand Voice Consistency:** Load and apply brand guidelines automatically
- **Natural Language:** Phase 6.5 Humanizer removes AI writing patterns with 4 personality profiles
- **Quality Transparency:** Every piece scored 1-10 across 5 dimensions with comparative benchmarks
- **Human Oversight:** Content <5.0/10 escalates to review, never auto-publishes
- **18 Skills + 7 Commands:** Full content lifecycle — from brief to publish to repurpose, with top commands visible in the Customize panel

---

## Quick Results

**Sample Output (Article - "Multi-Agent AI Systems"):**
- **Processing Time:** 28 minutes
- **Quality Score:** 9.0/10 (Grade A)
- **Word Count:** 1,855 (Target: 1,500-2,000)
- **Citations:** 14 sources (92% strongly verified)
- **SEO:** Primary keyword 1.62% density, all critical placements
- **GEO:** AI Overview optimized, 3 citeable moments, GEO score 8.8
- **Readability:** Grade 10.4 (Target: 10-12 for articles)
- **Humanization:** Zero AI patterns, burstiness 0.72 (natural human rhythm)
- **Comparative:** 94th percentile vs. brand average
- **Loops:** Zero (approved on first review)

---

## Commands (visible in Customize panel)

These 7 commands appear in the **Commands** section of the Customize sidebar, providing quick access to the most common content workflows:

| Command | What It Does |
|---------|-------------|
| `/create-content` | Run the full 9-phase pipeline — research, draft, fact-check, humanize, publish |
| `/content-brief` | Generate research-backed briefs with keyword data, competitor analysis, and outlines |
| `/social-adapt` | Repurpose articles into posts for LinkedIn, Twitter/X, Instagram, Facebook, Threads |
| `/publish` | Push content to Webflow or WordPress with preview, verification, and HTML fallback |
| `/translate` | Translate into 15+ languages preserving brand voice, citations, and SEO |
| `/brand-setup` | Configure brand voice, terminology, compliance guardrails, and style guide |
| `/audit-content` | Audit content library for freshness decay, coverage gaps, and optimization opportunities |

---

## Skills Overview

### Core Production
| Skill | Command | Purpose |
|-------|---------|---------|
| Content Pipeline | `/contentforge` | Full 9-phase production (20-30 min per piece) |
| Batch Processing | `/batch-process` | Process 10-50+ pieces in parallel (4-5x faster) |
| Content Refresh | `/content-refresh` | Update old content with current data, preserve SEO |

### Publishing & Social
| Skill | Command | Purpose |
|-------|---------|---------|
| Social Adaptation | `/cf:social-adapt` | Article → LinkedIn, Twitter/X, Instagram, Facebook, Threads posts |
| CMS Publishing | `/cf:publish` | Push to Webflow/WordPress via MCP or HTML export |

### Content Optimization
| Skill | Command | Purpose |
|-------|---------|---------|
| A/B Variants | `/cf:variants` | Generate 3-10 headline, hook, CTA variations with scoring |
| Analytics Dashboard | `/cf:analytics` | Quality trends, timing breakdown, brand performance |

### Multilingual & Video
| Skill | Command | Purpose |
|-------|---------|---------|
| Translation | `/cf:translate` | Translate preserving brand voice, 15+ languages, 3 levels |
| Video Scripts | `/cf:video-script` | Timestamped scripts for YouTube, TikTok, Instagram Reels |

### Content Management
| Skill | Command | Purpose |
|-------|---------|---------|
| Content Brief | `/cf:brief` | Research-backed brief with keyword analysis and outline |
| Content Audit | `/cf:audit` | Freshness scoring, decay detection, gap analysis |
| Content Calendar | `/cf:calendar` | Production scheduling with deadline tracking |
| Style Guide | `/cf:style-guide` | Import brand voice, generate brand profile JSON |
| Custom Template | `/cf:template` | Create content type templates beyond the 5 built-in |

### Connector Management
| Skill | Command | Purpose |
|-------|---------|---------|
| Integrations | `/cf:integrations` | Dashboard showing connected vs. available connectors |
| Connect | `/cf:connect` | Guided setup for any of 22 supported connectors |

---

## The 9-Phase Pipeline

```
Phase 1: Research Agent
↓ Quality Gate 1: 5+ live sources, competitor analysis, differentiated angle
Phase 2: Fact Checker
↓ Quality Gate 2: 80%+ verified claims, zero flagged items, all URLs live
Phase 3: Content Drafter
↓ Quality Gate 3: Word count ±10%, all sections covered, min 1 citation/300 words
Phase 4: Scientific Validator
↓ Quality Gate 4: Zero hallucinations, all claims traceable, logic validated
Phase 5: Structurer & Proofreader
↓ Quality Gate 5: Zero grammar errors, readability on target, brand compliant
Phase 6: SEO/GEO Optimizer ⬆ UPGRADED
↓ Quality Gate 6: Keywords optimized, meta tags ready, GEO score ≥7, AI Overview structured
Phase 6.5: Humanizer ⬆ UPGRADED
↓ Quality Gate 6.5: AI patterns removed, personality profile applied, industry patterns cleared
Phase 7: Reviewer ⬆ UPGRADED
↓ Quality Gate 7: Score ≥7.0, comparative ranking, trend analysis, recommendations
Phase 8: Output Manager ⬆ UPGRADED
↓ .docx + Medium + Substack + Newsletter + PDF + Social Package
```

**Post-Pipeline Agents (New in v3.0):**
- **Agent 10: Social Adapter** — Extracts shareworthy moments, generates platform-specific posts
- **Agent 11: Translator** — Element classification, brand voice mapping, cultural adaptation

**Feedback Loops:**
- Phase 4 → Phase 3 (max 2 iterations): If hallucinations detected
- Phase 6 → Phase 5 (max 1 iteration): If SEO degrades readability
- Phase 7 → Any phase (max 2 iterations): If dimension scores below threshold
- **Total loop limit:** 5 iterations before human escalation

---

## Installation

### Connectors (MCP Integrations)

ContentForge ships with **6 HTTP connectors** that work in both Cowork and Claude Code — Notion (knowledge base), Canva (design), Webflow (publishing), Slack (notifications), Gmail (delivery), and Google Calendar (scheduling).

**The plugin works fully WITHOUT any connectors** — you can run the complete content pipeline and get output locally. Connectors unlock platform integrations.

**New in v3.0:** Run `/cf:integrations` to see which connectors are active and what they unlock. Run `/cf:connect <name>` for guided setup of any of 22 supported connectors across 12 categories.

**Claude Code users** who need Google Sheets (requirement intake) and Google Drive (brand knowledge vault) can use the advanced setup:

```bash
cp .mcp.json.example .mcp.json
```

See [CONNECTORS.md](CONNECTORS.md) for the full connector reference.

### Step 1: Install Plugin

**Option A: Claude Marketplace (Recommended)**
```bash
# Search for "ContentForge" in Claude Code marketplace
claude plugins install contentforge
```

**Option B: Manual Install**
```bash
# Clone repository
git clone https://github.com/indranilbanerjee/contentforge.git

# Move to Claude plugins directory
# On Mac/Linux:
mv contentforge ~/.claude/plugins/

# On Windows:
mv contentforge %USERPROFILE%\.claude\plugins\
```

### Step 2: Verify Installation

```bash
# Session startup will show:
# ✓ ContentForge v3.1 loaded — Enterprise content production with zero hallucinations
#   /contentforge — Single piece (20-30 min)
#   /batch-process — Multiple pieces in parallel (4-5x faster)
#   /content-refresh — Update old content with fresh data
#   /cf:integrations — See connected integrations
#   /cf:social-adapt — Repurpose content for social
#   /cf:publish — Push to CMS
```

### Step 3: Configure MCP Servers (Optional)

**Copy the example config for full npx server support:**
```bash
cd ~/.claude/plugins/contentforge
cp .mcp.json.example .mcp.json
```

Edit `.mcp.json` with your credentials. See [CONNECTORS.md](CONNECTORS.md) for setup guides.

### Step 4: Set Up Brand Knowledge Vault (Optional)

**In Google Drive, create folder structure:**

```
ContentForge-Knowledge/
├── Brand-Name-1/
│   ├── Brand-Guidelines/
│   │   ├── voice-and-tone.md
│   │   ├── terminology.md
│   │   └── visual-identity.pdf (optional)
│   ├── Reference-Content/
│   │   ├── sample-article-1.md
│   │   └── sample-article-2.md
│   └── Guardrails/
│       ├── prohibited-claims.md
│       └── compliance-requirements.md
```

**Populate brand files using templates from [`config/brand-registry-template.json`](config/brand-registry-template.json)**

### Step 5: Test Installation

```bash
/contentforge "Write a 1500-word article about AI content automation for brand AcmeCorp"
```

**Expected:** Pipeline executes through all 9 phases, outputs .docx with quality scorecard.

---

## Architecture

### Agent Overview

| Phase | Agent | Purpose | Avg Time |
|-------|-------|---------|----------|
| 1 | Researcher | SERP analysis, source mining, outline creation | 8 min |
| 2 | Fact Checker | URL verification, claim validation, cross-referencing | 3 min |
| 3 | Content Drafter | First draft with brand voice and citations | 6 min |
| 4 | Scientific Validator | Hallucination detection, logic validation | 2 min |
| 5 | Structurer & Proofreader | Grammar, readability, brand compliance | 3 min |
| 6 | SEO/GEO Optimizer | Keywords, meta tags, AI Overview optimization, GEO scoring | 2 min |
| 6.5 | Humanizer | AI pattern removal, personality profiles, industry patterns | 2 min |
| 7 | Reviewer | 5-dimension scoring, comparative analysis, trend tracking, recommendations | 1 min |
| 8 | Output Manager | .docx, Medium, Substack, Newsletter, PDF, Social Package | 1 min |
| 10 | Social Adapter | Extract shareworthy moments, generate platform-specific posts | Post-pipeline |
| 11 | Translator | Element classification, brand voice mapping, cultural adaptation | Post-pipeline |

**Total:** ~28 minutes per piece (can vary based on complexity and word count)

### Quality Gate System

**Gate Structure:**
- **Criteria:** Specific pass/fail conditions (e.g., "Min 5 live sources")
- **Decision:** PASS (continue), FAIL (fix and re-run), or LOOP (return to earlier phase)
- **Feedback:** If FAIL or LOOP, specific issues documented for correction

**Gate Enforcement:**
- All gates enforced automatically by orchestrator
- No human intervention required unless score <5.0 or loops exceeded
- Loop limits prevent infinite iterations (max 2 per phase type, 5 total)

### Three-Layer Fact Verification

Single-pass fact-checking misses ~15-20% of hallucinations. ContentForge uses layered verification:

1. **Phase 2 (Fact Checker):** Verifies research sources before drafting begins
2. **Phase 4 (Scientific Validator):** Re-verifies drafted content against verified sources
3. **Phase 7 (Reviewer):** Final audit of factual accuracy as part of holistic quality assessment

**Result:** 100% factual accuracy in production tests, zero hallucinations in published content.

### Brand Profile Caching

SHA256 hash-based caching (see [`utils/brand-cache-manager.md`](utils/brand-cache-manager.md)):
1. On first run for a brand, process all guideline files
2. Calculate SHA256 hash of all source files
3. Save processed profile with hash to cache file
4. On subsequent runs: if hash matches → load cached profile (<5 seconds)

**Performance:** First run: 2-5 minutes. Cached runs: <5 seconds (95%+ time savings).

---

## Quality Scoring System

### 5 Dimensions (Phase 7)

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Content Quality | 30% | Depth, originality, audience value, structure, completeness |
| Citation Integrity | 25% | Factual accuracy, source quality, formatting, recency, cross-referencing |
| Brand Compliance | 20% | Voice/tone, terminology, guardrails, POV, industry compliance |
| SEO Performance | 15% | Keywords, meta tags, on-page elements, GEO readiness, schema |
| Readability | 10% | Reading level, sentence variety, paragraph structure, scannability, humanization |

### Decision Thresholds

| Score Range | Grade | Decision |
|-------------|-------|----------|
| 9.0-10.0 | A+ to A | APPROVED — Publish + repurpose aggressively |
| 7.0-8.9 | B- to A- | APPROVED — Publish with optional improvements |
| 5.0-6.9 | C- to C+ | LOOP — Return to weakest phase for fixes |
| <5.0 | D to F | HUMAN REVIEW — Escalate, do not auto-publish |

### New in v3.0: Comparative Scoring & Recommendations

The Reviewer now provides:
- **Percentile ranking** against the brand's historical content
- **Trend tracking** across last 10 pieces (strengths, weaknesses, trajectory)
- **Score-based recommendations** with cross-skill suggestions (e.g., "Run `/cf:social-adapt` — 5 shareworthy moments identified")

---

## Phase 6.5: Humanizer

**The ContentForge Differentiator**

Phase 6.5 removes AI writing patterns that make content sound robotic, while preserving all SEO keywords from Phase 6.

### How It Works

**1. AI Pattern Removal:** Scans for and removes 20+ telltale phrases from `config/humanization-patterns.json`

**2. Sentence Variety (Burstiness):** Achieves natural human rhythm:
```
Target: Short (≤12 words) 20% | Medium (13-25) 50% | Long (26+) 30%
Burstiness Score: ≥0.7 (standard deviation / mean)
```

**3. Personality Profiles (New in v3.0):** 4 configurable profiles:
- **Authoritative** — Data-first, definitive, minimal hedging
- **Conversational** — Direct address, questions, contractions
- **Technical** — Jargon preserved, precision, process-oriented
- **Witty** — Wordplay, unexpected comparisons, self-aware asides

**4. Industry-Specific Patterns (New in v3.0):** Removes industry-specific AI phrases for:
- Healthcare/Pharma (e.g., "healthcare landscape", "paradigm shift in medicine")
- Finance/BFSI (e.g., "financial landscape", "navigate the complexities")
- Technology/SaaS (e.g., "digital transformation journey", "seamless integration")
- Legal (e.g., "navigate the legal landscape", "legal complexities")
- Education (e.g., "educational landscape", "empowering learners")

**5. SEO Preservation Check:** Verifies keywords unchanged ±2 occurrences

### Results

- AI patterns removed: 12-15 per article
- Burstiness: 0.50 → 0.72 (+44%)
- AI detection scores: <30% (vs. 85-95% before humanization)
- SEO keyword variance: ±1 occurrence (negligible)

---

## Troubleshooting

### Pipeline Fails at Phase 1 (Research)

**Possible Causes:** Topic too niche, no search volume, web_search not working

**Solutions:**
1. Broaden topic or use related keyword with search volume
2. Check Claude's web_search capability is enabled
3. Verify internet connectivity

### Content Scores <7.0 and Keeps Looping

**Solutions:**
1. Review Phase 7 Quality Scorecard for weakest dimension
2. Run `/cf:brief` — weak briefs lead to weak content
3. Run `/cf:style-guide` — check brand profile completeness
4. Lower thresholds temporarily in `config/scoring-thresholds.json`

### Phase 6.5 Humanizer Degrades SEO

**Expected behavior:** Humanizer auto-loops to Phase 6 for re-optimization. Second pass usually balances both.

### Connector Not Working

Run `/cf:integrations` to check status. Run `/cf:connect <name>` for guided setup.

---

## FAQ

### Q: How does ContentForge compare to ChatGPT/Claude directly?

Single-prompt tools produce content in 30 seconds but with ~15-20% hallucination rate, generic voice, and AI writing patterns. ContentForge takes 28 minutes but delivers 0% hallucinations, consistent brand voice, human-sounding prose, and transparent quality scores.

### Q: Can I use ContentForge without Google Drive/Sheets?

Yes. The core pipeline works without any external integrations. Google Drive/Sheets are optional for brand knowledge storage and requirement tracking. Run `/cf:integrations` to see what's connected.

### Q: How much does it cost to run ContentForge?

ContentForge is free (open source, MIT license). Claude API costs are ~$0.50-1.50 per article depending on length and model.

### Q: What content types does ContentForge support?

5 built-in types: Articles (1,500-2,000 words), Blog Posts (800-1,500), Whitepapers (2,500-5,000), FAQs (600-1,200), Research Papers (4,000-8,000). Use `/cf:template` to create custom types.

### Q: Can I run multiple content pieces in parallel?

Yes. `/batch-process` handles 10-50+ pieces simultaneously with 4-5x speedup over sequential processing.

### Q: How do I repurpose content for social media?

Run `/cf:social-adapt` with any article. It generates platform-specific posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads with correct character limits, hashtags, and posting time recommendations.

### Q: Can I translate content while preserving brand voice?

Yes. `/cf:translate` supports 15+ languages with 3 localization levels (literal, adapted, transcreated). The Translator Agent maps brand voice characteristics to target language conventions.

---

## Roadmap

### v3.1 (Planned)
- [ ] Image generation integration (DALL-E, Midjourney via MCP)
- [ ] Audio content (podcast scripts, voice-over scripts)
- [ ] Web-based progress dashboard (HTML/CSS)
- [ ] Slack/Teams notifications for batch completion

### v3.2 (Planned)
- [ ] Expand multilingual support to 35+ languages
- [ ] Content performance tracking (organic traffic correlation)
- [ ] Predictive quality scoring from brief analysis
- [ ] Content decay detection with automated refresh triggers

### v4.0 (Planned)
- [ ] API mode (REST API for external integrations)
- [ ] Real-time collaboration (multiple agents editing simultaneously)
- [ ] Custom agent creation (define your own pipeline phases)
- [ ] Advanced analytics with ML-powered optimization recommendations

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Priority Contribution Areas:**
- Additional content type templates (landing pages, email sequences)
- Humanization pattern libraries for non-English languages
- Industry-specific quality rubrics
- Test coverage for individual agents

---

## License

MIT License — see [LICENSE](LICENSE) file.

---

## Support

**Issues:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
**Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/contentforge/discussions)

---

## Credits

**Created by:** Indranil Banerjee
**Built for:** Claude Code & Cowork platforms
**Powered by:** Anthropic Claude

**Special Thanks:**
- Anthropic for Claude and MCP framework
- Digital marketing agencies who provided feedback during beta testing
- Open source community for MCP server implementations

---

**ContentForge v3.1.0** — 12 agents, 18 skills, zero hallucinations. Transform requirements into publication-ready content in 20-30 minutes.
