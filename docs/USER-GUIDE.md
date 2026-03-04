# ContentForge v3.4 — Complete User Guide

**From zero to first published article.** This guide walks you through every step of using ContentForge in Claude Cowork or Claude Code, from initial setup to running the full content production pipeline.

---

## Table of Contents

1. [Before You Start](#1-before-you-start)
2. [Installation & Verification](#2-installation--verification)
3. [Understanding the Startup Banner](#3-understanding-the-startup-banner)
4. [Setting Up Your Brand Profile](#4-setting-up-your-brand-profile)
5. [Setting Up Google Sheets (Optional)](#5-setting-up-google-sheets-optional)
6. [Setting Up Google Drive Knowledge Vault (Optional)](#6-setting-up-google-drive-knowledge-vault-optional)
7. [Running Your First Content Piece](#7-running-your-first-content-piece)
8. [Understanding the 10-Phase Pipeline](#8-understanding-the-10-phase-pipeline)
9. [Reading the Quality Scorecard](#9-reading-the-quality-scorecard)
10. [Publishing & Social Adaptation](#10-publishing--social-adaptation)
11. [Batch Processing (Multiple Pieces)](#11-batch-processing-multiple-pieces)
12. [Content Refresh (Updating Old Content)](#12-content-refresh-updating-old-content)
13. [Content Briefs & Planning](#13-content-briefs--planning)
14. [A/B Variants & Testing](#14-ab-variants--testing)
15. [Translation & Multilingual Content](#15-translation--multilingual-content)
16. [Video Scripts](#16-video-scripts)
17. [Content Audits & Calendar](#17-content-audits--calendar)
18. [Style Guides & Custom Templates](#18-style-guides--custom-templates)
19. [Analytics & Quality Tracking](#19-analytics--quality-tracking)
20. [Connector Management](#20-connector-management)
21. [Troubleshooting](#21-troubleshooting)
22. [Skill Reference](#22-skill-reference)

---

## 1. Before You Start

### What You Need

| Requirement | Details |
|-------------|---------|
| **Claude Cowork or Claude Code** | Latest version |
| **ContentForge plugin installed** | Via marketplace or manual install |
| **Internet connection** | Required for research phase (web search) |

### What's Optional (But Recommended)

| Optional | What It Unlocks |
|----------|----------------|
| **Google Sheets MCP** | Requirement intake for batch processing, tracking sheets |
| **Google Drive MCP** | Brand knowledge vault, output file storage, .docx uploads |
| **Webflow or WordPress MCP** | Direct CMS publishing via `/cf:publish` |
| **Slack MCP** | Pipeline completion notifications |
| **Google Calendar MCP** | Content calendar sync via `/cf:calendar` |
| **Notion MCP** | Content brief storage, knowledge base |

**Key point:** ContentForge works fully without any MCP connectors. The core pipeline runs entirely within the Claude session. Connectors add platform integrations but are NOT required.

### How Long Things Take

| Task | Time |
|------|------|
| First-time brand setup | 5-10 minutes |
| Single article (1,800 words) | 20-30 minutes |
| Single blog post (1,200 words) | 15-22 minutes |
| Whitepaper (3,500 words) | 30-45 minutes |
| Batch of 10 articles | 60-90 minutes (parallel) |
| Social adaptation of 1 article | 3-5 minutes |
| Content brief | 5-8 minutes |

---

## 2. Installation & Verification

### Method A: Claude Marketplace (Recommended)

In Claude Cowork, go to Settings > Plugins > Marketplace and search for "ContentForge" from the `neels-plugins` marketplace.

Or, if using CLI:
```
claude plugins install contentforge
```

### Method B: Manual Install

```bash
git clone https://github.com/indranilbanerjee/contentforge.git
```

Move the cloned folder to your Claude plugins directory:
- **Mac/Linux:** `~/.claude/plugins/`
- **Windows:** `%USERPROFILE%\.claude\plugins\`

### Verify Installation

Start a new Claude session. You should see the ContentForge banner:

```
✓ ContentForge v3.1 loaded — Enterprise content production with zero hallucinations
  /contentforge — Single piece (20-30 min)
  /batch-process — Multiple pieces in parallel (4-5x faster)
  /content-refresh — Update old content with fresh data
  /cf:integrations — See connected integrations
  /cf:social-adapt — Repurpose content for social
  /cf:publish — Push to CMS
```

**If you don't see this banner:**
1. Check the plugin is in the correct directory
2. Ensure `hooks/hooks.json` exists
3. Try reinstalling: clear `~/.claude/plugins/cache/` first

### Check Your Connectors

Run immediately after install:
```
/cf:integrations
```

This shows which connectors are active and what they unlock. You should see at least 7 HTTP connectors (Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar) if the plugin installed correctly.

---

## 3. Understanding the Startup Banner

When ContentForge loads, the `setup.py` script runs automatically and reports:

```
[ContentForge] Python 3.10.12 ✓
[ContentForge] PLUGIN_ROOT=/home/user/.claude/plugins/contentforge
[ContentForge] SCRIPTS_DIR=/home/user/.claude/plugins/contentforge/scripts
[ContentForge] CONNECTORS=7 HTTP connectors loaded
```

This tells you:
- **Python version** — Must be 3.8+. Cowork VM has 3.10.12.
- **PLUGIN_ROOT** — Where the plugin is installed. All scripts reference this path.
- **SCRIPTS_DIR** — Where Python scripts live.
- **CONNECTORS** — How many HTTP connectors are in `.mcp.json`.

If you see errors here, check the [Troubleshooting](#21-troubleshooting) section.

---

## 4. Setting Up Your Brand Profile

**This is the most important step.** Brand profiles control voice, tone, terminology, guardrails, citation rules, and quality thresholds for all content. Without a brand profile, ContentForge uses generic defaults.

### Method 1: Quick Setup with `/cf:style-guide` (Recommended)

The fastest way to create a brand profile:

```
/cf:style-guide
```

**What happens:**
1. You provide your brand name, industry, and website
2. Optionally share existing documents (style guide PDFs, voice guidelines, sample content)
3. ContentForge extracts: tone, formality, personality traits, terminology, guardrails
4. Generates a `brand-profile.json` file

**You can provide source material in several ways:**
- **Paste text** directly in the conversation
- **Share a URL** to your brand's style guide or website
- **Upload a document** (if in Claude Code with file access)
- **Reference a Google Drive file** (if Google Drive MCP is connected)

**Example:**
```
/cf:style-guide

Brand: AcmeMed
Industry: Healthcare/Pharma
Website: https://acmemed.com

Here's our brand voice guide:
- Tone: Professional, authoritative, data-driven
- We say "patients" not "consumers"
- We say "clinical outcomes" not "results"
- Never make health claims or guarantees
- Always cite peer-reviewed sources
- Reading level: College graduate
```

ContentForge generates a JSON profile that all 13 agents reference during content production.

### Method 2: Manual JSON Creation

Copy the template and fill in your values:

**Source template:** `config/brand-registry-template.json`

**Key sections to fill in:**

```json
{
  "brand_name": "Your Brand Name",
  "industry": "pharma | bfsi | technology | healthcare | legal | education | ecommerce",
  "voice": {
    "tone": "professional | conversational | authoritative | witty",
    "formality": "formal | business_casual | casual",
    "personality_traits": ["helpful", "trustworthy", "data-driven"],
    "writing_style": {
      "sentence_length": "mixed",
      "use_contractions": true,
      "technical_depth": "intermediate"
    }
  },
  "terminology": {
    "preferred_terms": { "customer": "client", "buy": "invest in" },
    "prohibited_terms": ["cheap", "revolutionary", "game-changing"]
  },
  "guardrails": {
    "prohibited_claims": ["Guaranteed results", "No side effects"],
    "required_disclaimers": ["Results may vary."]
  },
  "quality_thresholds": {
    "minimum_quality_score": 7.0,
    "auto_approve_threshold": 8.5
  }
}
```

**Save this file as:** `~/.claude-marketing/brands/YourBrandName-profile.json`

Or, if using Google Drive: save to `ContentForge-Knowledge/YourBrandName/brand-profile.json`

### Method 3: Google Drive Knowledge Vault (Most Comprehensive)

For enterprise brands with extensive guidelines, create a folder structure in Google Drive:

```
Google Drive/
└── ContentForge-Knowledge/
    └── AcmeMed/
        ├── Brand-Guidelines/
        │   ├── voice-and-tone.md          ← Brand voice rules
        │   ├── terminology.md             ← Approved/banned terms
        │   └── visual-identity.pdf        ← Optional, for reference
        ├── Reference-Content/
        │   ├── sample-article-1.md        ← Examples of good content
        │   └── sample-article-2.md        ← More examples
        └── Guardrails/
            ├── prohibited-claims.md       ← What NOT to say
            └── compliance-requirements.md ← Regulatory rules
```

**When ContentForge first runs for this brand:**
1. It reads all files from the Knowledge Vault
2. Processes them into a structured brand profile
3. Calculates a SHA256 hash of all source files
4. Caches the profile locally for fast future access

**On subsequent runs:**
1. Checks the SHA256 hash of source files
2. If unchanged → loads cached profile in <5 seconds
3. If changed → re-processes (2-5 minutes)

**Requirement:** Google Drive MCP must be connected. Run `/cf:integrations` to verify.

### What If I Don't Have a Brand Profile?

ContentForge will still work. It will:
- Use generic professional tone
- Apply default quality thresholds (≥7.0 to pass)
- Use standard citation rules (APA format)
- Not enforce any brand-specific terminology

**This is fine for testing** but not recommended for production content.

### How Brand Profiles Are Used

Every agent in the pipeline references the brand profile:

| Agent | What It Uses |
|-------|-------------|
| Phase 1 (Research) | Industry context, competitor URLs, target audience |
| Phase 3 (Drafter) | Voice, tone, terminology, writing style |
| Phase 5 (Structurer) | Formatting preferences, brand compliance rules |
| Phase 6 (SEO) | Keyword preferences, meta tag formats |
| Phase 6.5 (Humanizer) | Personality profile, industry-specific patterns |
| Phase 7 (Reviewer) | Quality thresholds, dimension weights, industry overrides |
| Phase 8 (Output) | File format, header/footer, brand colors |

---

## 5. Setting Up Google Sheets (Optional)

Google Sheets integration enables two things:
1. **Requirement intake** — Define what content to produce in a spreadsheet
2. **Tracking** — ContentForge updates the sheet with quality scores, status, output links

### When Do You Need Google Sheets?

| Scenario | Need Sheets? |
|----------|-------------|
| Running a single piece interactively | No |
| Running batch of 10+ pieces | Recommended |
| Tracking quality scores over time | Recommended |
| Agency managing multiple clients | Strongly recommended |

### Sheet Structure for Content Requirements

Create a Google Sheet with these columns:

| Column | Required? | Description | Example |
|--------|-----------|-------------|---------|
| A: Requirement ID | Yes | Unique identifier | REQ-001 |
| B: Content Type | Yes | article, blog, whitepaper, faq, research_paper | article |
| C: Title/Topic | Yes | What the content is about | "AI in Healthcare: 2026 Trends" |
| D: Target Audience | Recommended | Who reads this | "Healthcare CIOs" |
| E: Brand | Yes | Brand profile name | AcmeMed |
| F: Primary Keyword | Recommended | Main SEO keyword | "AI healthcare 2026" |
| G: Word Count Target | Optional | Target word count | 1800 |
| H: Priority | Optional | 1 (highest) to 5 (lowest) | 1 |
| I: Tone Override | Optional | Override brand default | conversational |
| J: Status | Auto-filled | pending → in_progress → complete → failed | pending |
| K: Quality Score | Auto-filled | Overall score (1-10) | 9.0 |
| L: Output URL | Auto-filled | Google Drive link to .docx | https://drive.google.com/... |
| M: Processing Time | Auto-filled | Minutes taken | 24 |
| N: Completed At | Auto-filled | Timestamp | 2026-02-25T14:30:00Z |

**Initial setup:**
1. Create a new Google Sheet
2. Add headers in Row 1 (columns A through N)
3. Fill in Rows 2+ with your content requirements
4. Set Status column to "pending" for all rows
5. Share the sheet URL with ContentForge

**Example:**
| Req ID | Type | Title | Audience | Brand | Keyword | Words | Priority |
|--------|------|-------|----------|-------|---------|-------|----------|
| REQ-001 | article | AI in Healthcare 2026 | Healthcare CIOs | AcmeMed | AI healthcare 2026 | 1800 | 1 |
| REQ-002 | blog | 10 Remote Team Tips | HR Managers | TechCorp | remote team management | 1200 | 3 |
| REQ-003 | whitepaper | Cloud Security Trends | CISOs | SecureCloud | cloud security 2026 | 3500 | 2 |

### Connecting Google Sheets

**If you see "Google Sheets" as connected in `/cf:integrations`:** You're ready. No additional setup needed.

**If not connected:**
```
/cf:connect google-sheets
```

This walks you through the setup. Google Sheets uses npx MCP (not HTTP), so you'll need:
1. A Google Cloud Project
2. Service Account with Sheets API enabled
3. Credentials JSON file
4. Add the npx server to `.mcp.json`

See [CONNECTORS.md](../CONNECTORS.md) for detailed instructions.

---

## 6. Setting Up Google Drive Knowledge Vault (Optional)

### When Do You Need Google Drive?

| Scenario | Need Drive? |
|----------|------------|
| Simple content with inline brand description | No |
| Multiple brands with detailed guidelines | Yes |
| Regulated industry (Pharma, BFSI, Legal) | Strongly recommended |
| Content output storage (.docx upload) | Yes |
| Team collaboration on brand profiles | Yes |

### Folder Structure

Create this folder structure in Google Drive:

```
ContentForge-Knowledge/
├── AcmeMed/                          ← One folder per brand
│   ├── Brand-Guidelines/
│   │   ├── voice-and-tone.md         ← Required: Voice, tone, formality
│   │   ├── terminology.md            ← Required: Preferred/banned terms
│   │   └── visual-identity.pdf       ← Optional: Logos, colors (for reference)
│   ├── Reference-Content/
│   │   ├── best-article.md           ← Optional: Example of great content
│   │   └── approved-blog.md          ← Optional: Another example
│   └── Guardrails/
│       ├── prohibited-claims.md      ← Required for regulated: What NOT to say
│       └── compliance-reqs.md        ← Required for regulated: FDA/SEC/HIPAA rules
├── TechCorp/                         ← Second brand
│   ├── Brand-Guidelines/
│   │   └── ...
│   └── ...
└── ContentForge-Output/              ← Auto-created by Output Manager
    ├── AcmeMed/
    │   └── AI-in-Healthcare-2026_v1.0.docx
    └── TechCorp/
        └── Remote-Team-Tips_v1.0.docx
```

### What Goes in Each File

**`voice-and-tone.md`** — The most important file:
```markdown
# AcmeMed Brand Voice

## Tone
Professional, authoritative, data-driven. We are trusted advisors, not salespeople.

## Formality
Business casual. Use contractions (it's, we're) but avoid slang.

## Personality
- Helpful: Always provide actionable takeaways
- Trustworthy: Back every claim with data
- Innovative: Show awareness of cutting-edge developments
- Empathetic: Acknowledge patient/provider challenges

## Writing Style
- Active voice preferred
- Short paragraphs (3-5 sentences)
- Use questions to engage readers
- Avoid jargon unless audience expects it
- Technical depth: Intermediate (explain complex concepts clearly)
```

**`terminology.md`** — Approved and banned terms:
```markdown
# AcmeMed Terminology

## Always Use
| Instead Of | Use |
|-----------|-----|
| customer | patient or healthcare provider |
| product | solution or platform |
| buy | invest in |
| cheap | cost-effective |
| users | clinicians |

## Never Use
- "revolutionary" (overused, unsubstantiated)
- "game-changing" (cliche)
- "cure" (regulatory risk)
- "guarantee" (legal liability)
- "best in class" (unsupported superlative)

## Product Names
- Always: "AcmeMed Platform" (with trademark: AcmeMed Platform™)
- Never: "the Acme system" or "AcmeMed software"
```

**`prohibited-claims.md`** (for regulated industries):
```markdown
# AcmeMed Guardrails

## Prohibited Claims
1. No health outcome guarantees ("will cure", "guaranteed to improve")
2. No unsupported superlatives ("best", "only", "first")
3. No competitor bashing by name
4. No off-label use suggestions
5. No patient testimonials without disclaimer

## Required Disclaimers
- Medical content: "Consult your healthcare provider before making treatment decisions."
- Data content: "Based on available data as of [date]. Results may vary."
- Financial content: "Not financial advice. Consult a qualified advisor."

## Regulatory Framework
- FDA 21 CFR Part 11 compliance for medical claims
- HIPAA considerations for patient data references
- FTC disclosure requirements for sponsored content
```

### How ContentForge Processes These Documents

1. **On first run for a brand:** ContentForge reads ALL files in the brand's Knowledge Vault folder
2. **Extracts structured data:** Voice → tone/formality/personality, Terminology → preferred/banned terms, Guardrails → prohibited claims/disclaimers
3. **Generates brand profile JSON:** Combines everything into the structured format from `config/brand-registry-template.json`
4. **Caches with SHA256 hash:** Saves the processed profile locally at `~/.claude-marketing/brands/`
5. **Future runs:** Compares file hashes → if unchanged, loads cache in <5 seconds

### Auto-Creation vs Manual

| Approach | When to Use |
|----------|------------|
| **Auto (via Knowledge Vault)** | You have existing brand documents. ContentForge extracts and structures them. |
| **Auto (via `/cf:style-guide`)** | You describe your brand verbally or share a URL. ContentForge generates the profile. |
| **Manual (copy template)** | You want full control over every field. Copy `config/brand-registry-template.json` and edit. |

**All three approaches produce the same result:** a structured brand profile JSON that all agents reference.

---

## 7. Running Your First Content Piece

### Simplest Possible Start (No Setup Required)

```
/contentforge "Write a 1500-word article about AI in healthcare for 2026"
```

ContentForge will:
1. Ask which brand to use (or use defaults if none exist)
2. Run the 10-phase pipeline
3. Output a quality scorecard + the content

### Interactive Mode (Recommended for First Time)

```
/contentforge
```

You'll be prompted for:
1. **Topic/Title** — e.g., "AI-Powered Diagnostics: The Future of Precision Medicine"
2. **Content Type** — Select: article, blog, whitepaper, faq, research_paper
3. **Brand** — Select from existing profiles (or "default")
4. **Target Audience** — e.g., "Healthcare Executives"
5. **Word Count** — e.g., 1800 (or press Enter for default)
6. **Primary Keyword** — e.g., "AI diagnostics precision medicine"

### Full Parameters Mode

```
/contentforge "AI-Powered Diagnostics: The Future of Precision Medicine" --type=article --brand=AcmeMed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine" --words=1800 --tone=authoritative
```

### From Google Sheet

```
/contentforge --sheet-url=https://docs.google.com/spreadsheets/d/ABC123 --row=5
```

Reads requirement from Row 5 of the sheet.

### What to Expect

After you provide inputs, the pipeline runs through 10 phases. You'll see progress updates:

```
Phase 1: Research Agent — Finding sources for "AI Diagnostics"...
✓ Phase 1 complete — 12 sources found, outline generated
Phase 2: Fact Checker — Verifying 12 sources...
✓ Phase 2 complete — 11 URLs live, 1 flagged for replacement
Phase 3: Content Drafter — Writing first draft...
✓ Phase 3 complete — 1,847 words, 12 citations
Phase 4: Scientific Validator — Checking for hallucinations...
✓ Phase 4 complete — 0 hallucinations, all claims traceable
Phase 5: Structurer & Proofreader — Polishing grammar and structure...
✓ Phase 5 complete — 0 errors, readability Grade 11.2
Phase 6: SEO/GEO Optimizer — Optimizing for search engines...
✓ Phase 6 complete — Keyword density 2.1%, GEO score 8.5
Phase 6.5: Humanizer — Removing AI patterns...
✓ Phase 6.5 complete — 14 AI patterns removed, burstiness 0.74
Phase 7: Reviewer — Scoring content quality...
✓ Phase 7 complete — Score: 9.0/10 (Grade A) — APPROVED
Phase 8: Output Manager — Generating deliverables...
✓ Phase 8 complete — .docx generated

TOTAL TIME: 24 minutes
```

---

## 8. Understanding the 10-Phase Pipeline

### Phase Flow

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│ Phase 1      │───▶│ Phase 2      │───▶│ Phase 3        │
│ Research     │    │ Fact Checker  │    │ Content Drafter │
│ (3-5 min)    │    │ (2-3 min)     │    │ (5-7 min)       │
└─────────────┘    └──────────────┘    └───────┬────────┘
                                               │
                              ┌────────────────┘
                              ▼
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│ Phase 6      │◀──│ Phase 5      │◀──│ Phase 4         │
│ SEO/GEO     │    │ Structurer    │    │ Sci. Validator  │
│ (2-3 min)    │    │ (2-3 min)     │    │ (2-3 min)       │
└──────┬──────┘    └──────────────┘    └────────────────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│ Phase 6.5    │───▶│ Phase 7      │───▶│ Phase 8         │
│ Humanizer   │    │ Reviewer      │    │ Output Manager  │
│ (1-2 min)    │    │ (2-3 min)     │    │ (1-2 min)       │
└─────────────┘    └──────────────┘    └────────────────┘
```

### Feedback Loops (When Things Fail)

The pipeline doesn't just run forward — it can loop back:

```
Phase 4 (Validator) finds hallucination → Loops to Phase 3 (Drafter) to fix it
Phase 6 (SEO) degrades readability → Loops to Phase 5 (Structurer) to rebalance
Phase 7 (Reviewer) scores <7.0 → Loops to weakest phase with feedback
```

**Loop limits:**
- Phase 4 → Phase 3: Max 2 loops
- Phase 6 → Phase 5: Max 1 loop
- Phase 7 → Any: Max 2 loops
- **Total:** Max 5 loops across entire pipeline
- **If exceeded:** Escalates to human review (never auto-publishes bad content)

### Three-Layer Fact Verification

This is what makes ContentForge different from single-prompt tools:

| Layer | Phase | What It Checks |
|-------|-------|----------------|
| Layer 1 | Phase 2 (Fact Checker) | Are sources real? Are URLs live? Are claims in the source material? |
| Layer 2 | Phase 4 (Scientific Validator) | Did the drafter fabricate any statistics? Are there logical inconsistencies? |
| Layer 3 | Phase 7 (Reviewer) | Final citation integrity audit as part of holistic quality assessment |

**Result:** 100% factual accuracy in production testing, zero hallucinations.

---

## 9. Reading the Quality Scorecard

After Phase 7, you get a detailed scorecard:

### Overall Score

```
OVERALL SCORE: 9.0 / 10
Decision: ✅ APPROVED
Grade: A
```

**What the scores mean:**

| Score | Grade | Decision |
|-------|-------|----------|
| 9.5-10.0 | A+ | APPROVED — Exceptional, repurpose aggressively |
| 9.0-9.4 | A | APPROVED — Excellent |
| 8.5-8.9 | A- | APPROVED — Very good |
| 8.0-8.4 | B+ | APPROVED — Good |
| 7.5-7.9 | B | APPROVED — Above average |
| 7.0-7.4 | B- | APPROVED — Meets minimum |
| 6.5-6.9 | C+ | LOOP — Below standard, needs fixes |
| 6.0-6.4 | C | LOOP — Significant improvement needed |
| 5.0-5.9 | C-/D | LOOP — Major revisions needed |
| <5.0 | F | HUMAN REVIEW — Cannot auto-fix |

### 5 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| **Content Quality** | 30% | Depth, originality, audience value, structure, completeness |
| **Citation Integrity** | 25% | Factual accuracy, source quality, formatting, recency |
| **Brand Compliance** | 20% | Voice, terminology, guardrails, POV consistency |
| **SEO Performance** | 15% | Keywords, meta tags, on-page elements, GEO readiness |
| **Readability** | 10% | Grade level, sentence variety, scannability, humanization |

### New in v3.0: Comparative Analysis

If you've produced content for this brand before, the scorecard also shows:

```
COMPARATIVE ANALYSIS
Percentile Ranking: 94th percentile (scores better than 94% of AcmeMed content)
vs. Brand Average: +1.2 above average (9.0 vs 7.8)
```

### New in v3.0: Recommendations

The reviewer now suggests next steps:

```
RECOMMENDATIONS
Score-Based Tier: Tier 1 — PUBLISH + REPURPOSE + AMPLIFY

Immediate Actions:
1. ✅ Proceed to publication
2. 📱 Run /cf:social-adapt — 5 shareworthy moments identified
3. 🎬 Run /cf:video-script — strong video potential

Strategic Actions:
4. 📊 Record to /cf:analytics for benchmark tracking
5. 🌍 Queue for /cf:translate --language=es,de
6. 📅 Add to /cf:calendar for 6-month refresh
```

---

## 10. Publishing & Social Adaptation

### Publishing to CMS

```
/cf:publish
```

**Supported platforms:**
- **Webflow** (via HTTP MCP) — Direct publishing
- **WordPress** (via npx MCP) — Direct publishing
- **HTML export** (fallback) — Copy HTML to any CMS manually

**What happens:**
1. ContentForge checks if Webflow or WordPress MCP is connected
2. If connected: formats content for the platform, shows preview, publishes on your confirmation
3. If not connected: exports clean HTML + metadata for manual upload

### Social Media Adaptation

```
/cf:social-adapt
```

Takes any ContentForge article and generates posts for:

| Platform | Format |
|----------|--------|
| **LinkedIn** | Professional post, 1,300 char max, 3-5 hashtags |
| **Twitter/X** | Thread of 3-5 tweets, 280 char each, 2-3 hashtags |
| **Instagram** | Caption with line breaks, 2,200 char max, 20-30 hashtags |
| **Facebook** | Engaging post, 500-1,000 chars, 1-2 hashtags |
| **Threads** | Conversational post, 500 char max, 3-5 hashtags |

**How to use:**
```
/cf:social-adapt "AI in Healthcare article we just produced"
```

Or provide the article directly:
```
/cf:social-adapt --source="path/to/article.md" --platforms=linkedin,twitter
```

The Social Adapter Agent (#10) identifies 10-15 shareworthy moments from your article (statistics, quotes, frameworks, surprising facts) and builds platform-specific posts around them.

---

## 11. Batch Processing (Multiple Pieces)

### When to Use

When you have 2+ content pieces to produce. `/batch-process` runs up to 5 pipelines in parallel, achieving 4-5x throughput vs. sequential.

### Setup

**Option A: Google Sheet**
1. Create a sheet with the structure from [Section 5](#5-setting-up-google-sheets-optional)
2. Fill in multiple rows
3. Run:
```
/batch-process --sheet-url=https://docs.google.com/spreadsheets/d/ABC123
```

**Option B: CSV**
```csv
requirement_id,content_type,title,target_audience,brand,word_count,priority,status
REQ-001,article,AI in Healthcare 2026,Healthcare CIOs,AcmeMed,2000,1,pending
REQ-002,blog,10 Tips for Remote Teams,HR Managers,TechCorp,1500,3,pending
REQ-003,whitepaper,Cloud Security Trends,CISOs,SecureCloud,3500,2,pending
```

**Option C: Interactive**
```
/batch-process
```
You'll be prompted for: source (sheet/CSV/manual), requirements, processing options.

### What Happens

1. **Queue builds** — All requirements sorted by priority
2. **Parallel execution** — Up to 5 pipelines run simultaneously
3. **Progress tracking** — Real-time dashboard showing each piece's phase and ETA
4. **Completion report** — Summary of all pieces with scores, times, links

### Completion Report

```
BATCH COMPLETE: 10 of 10 pieces

Results:
| Req ID | Title | Score | Grade | Time | Status |
|--------|-------|-------|-------|------|--------|
| REQ-001 | AI in Healthcare | 9.0 | A | 24m | ✅ Published |
| REQ-002 | Remote Team Tips | 8.3 | B+ | 18m | ✅ Published |
| REQ-003 | Cloud Security | 8.7 | A- | 38m | ✅ Published |
...

Summary:
- Average Score: 8.6/10
- Total Time: 87 minutes (vs. 240 min sequential = 2.8x faster)
- Failures: 0
- Human Review: 0
```

---

## 12. Content Refresh (Updating Old Content)

### When to Use

- Content is 6+ months old
- Search rankings are declining
- Statistics are outdated
- Competitor content has surpassed yours

### How to Use

```
/content-refresh "https://docs.google.com/document/d/XYZ123"
```

Or with local file:
```
/content-refresh --file="path/to/old-article.docx"
```

### Refresh Levels

| Level | What Changes | Time |
|-------|-------------|------|
| **Light (20%)** | Update statistics and citations only | 10-15 min |
| **Medium (50%)** | Rewrite intro/conclusion + update 3-5 sections | 15-25 min |
| **Heavy (80%)** | Near-complete rewrite using original as outline | 25-40 min |

### Version Control

Content Refresh NEVER overwrites the original. It saves as:
- Original: `AI-in-Healthcare_v1.0.docx`
- After refresh: `AI-in-Healthcare_v1.1.docx`

---

## 13. Content Briefs & Planning

### Creating a Brief

```
/cf:brief "AI diagnostics in healthcare"
```

**Output includes:**
- Keyword research (primary + secondary keywords, search volume, difficulty)
- Competitor analysis (top 5 SERP results, their angles, content gaps)
- Search intent analysis (informational, commercial, transactional)
- Audience pain points and questions
- Recommended outline with H2/H3 structure
- SEO strategy (target density, featured snippet opportunities)
- Suggested word count and content type

**Briefs feed into the pipeline:** You can pass a brief directly to `/contentforge`:
```
/contentforge --brief="the brief we just generated" --brand=AcmeMed
```

---

## 14. A/B Variants & Testing

### Generating Variants

```
/cf:variants "headline for the AI Healthcare article"
```

**Generates 3-10 variations** of:
- Headlines/titles
- Opening hooks
- CTAs (calls to action)

Each variant is scored on: clarity, emotional appeal, specificity, curiosity, keyword presence, and brand voice alignment.

**Example output:**
```
HEADLINE VARIANTS

1. "AI Diagnostics Cut Misdiagnosis Rates by 47% — Here's How" (Score: 9.2)
   Clarity: 9 | Emotion: 8 | Specificity: 10 | Curiosity: 9

2. "The Future of Precision Medicine Is Already Here" (Score: 7.8)
   Clarity: 8 | Emotion: 9 | Specificity: 5 | Curiosity: 8

3. "Why Every Hospital Will Use AI Diagnostics by 2028" (Score: 8.5)
   Clarity: 9 | Emotion: 7 | Specificity: 8 | Curiosity: 9
```

---

## 15. Translation & Multilingual Content

### Translating Content

```
/cf:translate --content="the article we just produced" --language=es --level=adapted
```

### Three Localization Levels

| Level | Description | When to Use |
|-------|-------------|------------|
| **Literal** | Word-for-word translation, minimal adaptation | Technical docs, legal content |
| **Adapted** | Natural language + cultural references adjusted | Blog posts, articles |
| **Transcreated** | Complete re-creation for target culture | Marketing campaigns, social content |

### Supported Languages

15+ languages including Spanish, French, German, Portuguese, Japanese, Korean, Chinese (Simplified/Traditional), Hindi, Arabic, Italian, Dutch, Russian, Turkish, Polish, Thai.

### How It Works

The Translator Agent (#11):
1. **Classifies elements** — What's translatable vs. what should stay (brand names, product names, URLs)
2. **Maps brand voice** — Translates tone characteristics to target language conventions
3. **Cultural adaptation** — Adjusts idioms, metaphors, cultural references
4. **SEO adaptation** — Researches equivalent keywords in target language
5. **Quality check** — Verifies brand voice preserved, no meaning drift

---

## 16. Video Scripts

### Generating a Video Script

```
/cf:video-script --source="the article we produced" --platform=youtube --duration=5min
```

### Supported Platforms

| Platform | Duration Range | Format |
|----------|---------------|--------|
| YouTube | 3-10 minutes | Full script with B-roll notes |
| TikTok | 30-60 seconds | Hook-heavy, visual-first |
| Instagram Reels | 30-90 seconds | Visual hooks, trending audio |
| Explainer | 2-5 minutes | Educational, step-by-step |

### Output Format

```
[0:00-0:15] HOOK
Dialogue: "47% fewer misdiagnoses. That's not a prediction — it's happening right now."
Visual: B-roll of medical professional reviewing AI scan
Music: Upbeat, modern

[0:15-0:45] CONTEXT
Dialogue: "In 2026, hospitals using AI diagnostic tools are seeing..."
Visual: Data visualization animation
B-roll: Hospital technology room
...
```

---

## 17. Content Audits & Calendar

### Content Audit

```
/cf:audit
```

**What it does:**
- Scans your content library for content decay (declining freshness)
- Scores each piece 0-100 on freshness
- Identifies coverage gaps (topics competitors cover that you don't)
- Recommends top 10 pieces for refresh
- Identifies topics for new content

### Content Calendar

```
/cf:calendar
```

**What it does:**
- Plans content production schedule
- Works backward from publish dates
- Detects deadline conflicts
- Syncs with Google Calendar (if connected via MCP)
- Tracks production status per piece

---

## 18. Style Guides & Custom Templates

### Creating a Style Guide

```
/cf:style-guide
```

See [Section 4](#4-setting-up-your-brand-profile) for full details. This skill creates brand profiles from natural language descriptions, URLs, or existing documents.

### Creating Custom Templates

ContentForge ships with 5 content type templates: Article, Blog, Whitepaper, FAQ, Research Paper.

Need a different type? Create it:

```
/cf:template "case study"
```

**Define:**
- Structure (sections, headers, flow)
- Quality standards (specific to this type)
- Word count range
- Readability target
- Citation minimum
- Any special requirements

The new template is saved and available for all future `/contentforge` and `/batch-process` runs.

---

## 19. Analytics & Quality Tracking

### Viewing Analytics

```
/cf:analytics
```

**Shows:**
- Quality score trends over time (improving, stable, declining)
- Phase timing breakdown (which phases take longest)
- Brand performance comparison (if managing multiple brands)
- Dimension trend analysis (which dimensions are consistent vs. volatile)
- Production velocity (pieces per week/month)

**Data sources:**
- **Google Sheets** (recommended) — Reads from tracking sheet
- **Local CSV** — Falls back to local tracking file at `~/.claude-marketing/contentforge/tracking/`

---

## 20. Connector Management

### Checking Connector Status

```
/cf:integrations
```

**Shows a dashboard:**
```
CONTENTFORGE CONNECTOR STATUS

Connected (6):                         What They Unlock
─────────────────────────────────────────────────────────
✅ Notion (HTTP)                       Knowledge base, brief storage
✅ Canva (HTTP)                        Design templates, image generation
✅ Webflow (HTTP)                      CMS publishing via /cf:publish
✅ Slack (HTTP)                        Pipeline completion notifications
✅ Gmail (HTTP)                        Content delivery via email
✅ Google Calendar (HTTP)              Calendar sync via /cf:calendar

Available (16):                        How to Connect
─────────────────────────────────────────────────────────
○ Google Sheets (npx)                  /cf:connect google-sheets
○ Google Drive (npx)                   /cf:connect google-drive
○ WordPress (npx)                      /cf:connect wordpress
○ HubSpot (HTTP)                       /cf:connect hubspot
...

Coverage: 6 of 22 (27%)
Quick wins: Google Sheets, Google Drive (unlock tracking + knowledge vault)
```

### Setting Up a Connector

```
/cf:connect google-sheets
```

**For HTTP connectors (Notion, Slack, etc.):**
1. Click the OAuth link
2. Authorize in your browser
3. Done — connector is active

**For npx connectors (Google Sheets, Google Drive, WordPress, etc.):**
1. Set up required credentials (API keys, service accounts)
2. Add environment variables to `.env`
3. Add the npx server config to `.mcp.json`
4. Restart Claude session

`/cf:connect` walks you through every step with copy-paste commands.

---

## 21. Troubleshooting

### Plugin Doesn't Load

**Symptom:** No ContentForge banner on session start.

**Fixes:**
1. Verify plugin is in `~/.claude/plugins/contentforge/`
2. Check `.claude-plugin/plugin.json` exists and has `"name": "contentforge"`
3. Check `hooks/hooks.json` is valid JSON
4. Clear plugin cache: delete `~/.claude/plugins/cache/` and reinstall

### "Brand profile not found"

**Symptom:** Pipeline asks for brand but can't find your profile.

**Fixes:**
1. Create a profile: `/cf:style-guide`
2. Or use default: run without specifying `--brand`
3. If using Knowledge Vault: verify Google Drive MCP is connected

### Pipeline Stuck in Loops

**Symptom:** Content keeps looping between phases, never approving.

**Fixes:**
1. Check the quality scorecard — which dimension is failing?
2. Run `/cf:brief` — a better brief leads to better content
3. Run `/cf:style-guide` — ensure brand profile is complete
4. Lower thresholds temporarily: edit `config/scoring-thresholds.json`
5. Check topic — very niche topics may lack sufficient sources

### Humanizer Degrades SEO

**Symptom:** SEO score drops after Phase 6.5.

**Expected behavior:** The pipeline auto-detects this and loops Phase 6.5 → Phase 6 for re-optimization. Usually resolves on second pass.

### Connector Not Working

**Symptom:** Skill says connector unavailable.

**Fixes:**
1. Run `/cf:integrations` to check status
2. Run `/cf:connect <name>` for setup guide
3. Verify `.mcp.json` has the connector entry
4. For npx: check environment variables are set

### Quality Scores Consistently Low

**Symptom:** Pieces scoring 5.0-6.5 regularly.

**Root causes and fixes:**
- **Weak briefs** → Run `/cf:brief` before `/contentforge`
- **Incomplete brand profile** → Run `/cf:style-guide` to enhance it
- **Complex topics** → ContentForge needs good source material; try broader topics first
- **Restrictive guardrails** → Review brand profile guardrails, ensure they're not overly limiting

---

## 22. Skill Reference

### Core Production

| Command | Purpose | Time |
|---------|---------|------|
| `/contentforge` | Full 10-phase content pipeline | 20-30 min |
| `/batch-process` | Parallel production (10-50+ pieces) | 4-5x faster |
| `/content-refresh` | Update old content with fresh data | 10-25 min |

### Publishing & Social

| Command | Purpose | Time |
|---------|---------|------|
| `/cf:social-adapt` | Article → LinkedIn, Twitter, Instagram, Facebook, Threads | 3-5 min |
| `/cf:publish` | Push to Webflow/WordPress or export HTML | 2-3 min |

### Content Optimization

| Command | Purpose | Time |
|---------|---------|------|
| `/cf:variants` | Generate 3-10 headline/hook/CTA variations | 2-3 min |
| `/cf:analytics` | Quality trends, timing, brand performance | 1-2 min |

### Multilingual & Video

| Command | Purpose | Time |
|---------|---------|------|
| `/cf:translate` | Translate preserving brand voice | 5-10 min |
| `/cf:video-script` | Generate timestamped video scripts | 3-5 min |

### Content Management

| Command | Purpose | Time |
|---------|---------|------|
| `/cf:brief` | Research-backed content brief | 5-8 min |
| `/cf:audit` | Content freshness/decay/gap analysis | 3-5 min |
| `/cf:calendar` | Production scheduling + Google Calendar sync | 2-3 min |
| `/cf:style-guide` | Import brand voice, generate profile JSON | 5-10 min |
| `/cf:template` | Create custom content type templates | 3-5 min |

### Connector Management

| Command | Purpose | Time |
|---------|---------|------|
| `/cf:integrations` | Dashboard of connected/available connectors | Instant |
| `/cf:connect <name>` | Guided setup for any connector | 2-10 min |

---

## Appendix A: Complete Workflow Example

**Scenario:** Agency producing 5 articles for healthcare client "AcmeMed"

### Step 1: Brand Setup (One-Time, 10 min)
```
/cf:style-guide
```
Provide AcmeMed's brand guidelines. ContentForge generates the profile.

### Step 2: Content Briefs (10 min)
```
/cf:brief "AI diagnostics in healthcare 2026"
/cf:brief "patient data privacy regulations 2026"
/cf:brief "telemedicine ROI for hospitals"
/cf:brief "healthcare AI implementation roadmap"
/cf:brief "clinical trial automation with AI"
```

### Step 3: Set Up Requirements Sheet (5 min)
Create Google Sheet with 5 rows using briefs from Step 2.

### Step 4: Batch Production (60-90 min)
```
/batch-process --sheet-url=https://docs.google.com/spreadsheets/d/ABC123
```
Pipeline runs 5 articles in parallel.

### Step 5: Review Scorecards
All 5 articles scored ≥7.0 → APPROVED.

### Step 6: Social Adaptation (15 min)
```
/cf:social-adapt --source="all 5 articles" --platforms=linkedin,twitter
```

### Step 7: Publish (5 min)
```
/cf:publish --platform=webflow
```

### Step 8: Track (Ongoing)
```
/cf:analytics
```

**Total time:** ~2 hours for 5 publication-ready articles + social posts + CMS publishing.

---

## Appendix B: File Reference

### Plugin Structure
```
contentforge/
├── .claude-plugin/plugin.json     # Manifest (name, version, description, author)
├── .mcp.json                      # 7 HTTP connectors (Notion, Canva, Figma, Webflow, Slack, Gmail, Calendar)
├── .mcp.json.example              # 67 npx servers (opt-in, copy to .mcp.json)
├── CONNECTORS.md                  # Full connector reference
├── README.md                      # Project overview
├── CHANGELOG.md                   # Release history
├── UPGRADE-GUIDE.md               # v2.x → v3.0 migration (historical)
│
├── agents/                        # 13 specialist agents
│   ├── 01-researcher.md           # Phase 1: SERP analysis, source mining
│   ├── 02-fact-checker.md         # Phase 2: URL verification, claim validation
│   ├── 03-content-drafter.md      # Phase 3: First draft with citations
│   ├── 03.5-visual-asset-annotator.md # Phase 3.5: Visual asset annotation
│   ├── 04-scientific-validator.md # Phase 4: Hallucination detection
│   ├── 05-structurer-proofreader.md # Phase 5: Grammar, readability, brand
│   ├── 06-seo-geo-optimizer.md    # Phase 6: Keywords, meta, GEO, AI Overview
│   ├── 06.5-humanizer.md          # Phase 6.5: AI pattern removal, personality
│   ├── 07-reviewer.md             # Phase 7: 5-dim scoring, comparative, trends
│   ├── 08-output-manager.md       # Phase 8: .docx, Medium, Substack, PDF, Social
│   ├── 09-batch-orchestrator.md   # Parallel pipeline coordination
│   ├── 10-social-adapter.md       # Social media post generation
│   └── 11-translator.md           # Multilingual translation
│
├── skills/                        # 18 skill commands
│   ├── contentforge/SKILL.md      # Main pipeline
│   ├── batch-process/SKILL.md     # Parallel processing
│   ├── content-refresh/SKILL.md   # Content updates
│   ├── cf-integrations/SKILL.md   # Connector dashboard
│   ├── cf-connect/SKILL.md        # Connector setup
│   ├── cf-publish/SKILL.md        # CMS publishing
│   ├── cf-social-adapt/SKILL.md   # Social adaptation
│   ├── cf-variants/SKILL.md       # A/B variants
│   ├── cf-analytics/SKILL.md      # Quality analytics
│   ├── cf-translate/SKILL.md      # Translation
│   ├── cf-video-script/SKILL.md   # Video scripts
│   ├── cf-brief/SKILL.md          # Content briefs
│   ├── cf-audit/SKILL.md          # Content audits
│   ├── cf-calendar/SKILL.md       # Content calendar
│   ├── cf-style-guide/SKILL.md    # Brand profile creation
│   └── cf-template/SKILL.md       # Custom templates
│
├── config/                        # 7 configuration files
│   ├── brand-registry-template.json    # Brand profile schema
│   ├── data-sources-template.json      # Trusted sources registry
│   ├── scoring-thresholds.json         # Quality scoring config
│   ├── humanization-patterns.json      # AI patterns + personality profiles
│   ├── analytics-config.json           # Analytics thresholds
│   ├── social-platform-specs.json      # Social platform constraints
│   └── multilingual-patterns.json      # Language-specific patterns
│
├── templates/                     # 10 content templates
│   ├── content-types/
│   │   ├── article-structure.md
│   │   ├── blog-structure.md
│   │   ├── whitepaper-structure.md
│   │   ├── faq-structure.md
│   │   ├── research-paper-structure.md
│   │   └── video-script-structure.md
│   ├── research-brief.md
│   ├── quality-scorecard.md
│   ├── social-post-templates.md
│   └── content-brief-template.md
│
├── utilities/                     # 6 workflow specifications
│   ├── batch-queue-manager.md
│   ├── progress-tracker.md
│   ├── analytics-tracker.md
│   ├── cms-publisher.md
│   ├── translation-manager.md
│   └── pipeline-optimizer.md
│
├── scripts/                       # 2 Python scripts
│   ├── setup.py                   # Session startup validation
│   └── connector-status.py        # Connector registry (22 connectors)
│
├── hooks/
│   └── hooks.json                 # Session start, pre-tool, pre-sub-agent
│
└── docs/
    └── USER-GUIDE.md              # This file
```

---

**ContentForge v3.4.0** — 13 agents, 18 skills, zero hallucinations.
