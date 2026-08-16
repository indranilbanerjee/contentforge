# ContentForge for Claude Cowork — Complete User Guide

**Version:** 3.16.1
**Platform:** Claude Cowork (Web-based)
**Audience:** Content teams, agencies, marketers using Cowork for content production

---

## 📖 Table of Contents

1. [What is ContentForge?](#what-is-contentforge)
2. [Installation in Cowork](#installation-in-cowork)
3. [MCP Integration Setup](#mcp-integration-setup)
4. [First-Time Setup (5 minutes)](#first-time-setup)
5. [Using ContentForge Commands](#using-contentforge-commands)
6. [Workflows for Different Use Cases](#workflows-for-different-use-cases)
7. [Understanding the 10-Phase Pipeline](#understanding-the-10-phase-pipeline)
8. [Quality Scores & What They Mean](#quality-scores--what-they-mean)
9. [Batch Processing for Agencies](#batch-processing-for-agencies)
10. [Content Refresh (Update Old Content)](#content-refresh)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## What is ContentForge?

ContentForge is an **enterprise-grade content production system** that transforms a simple content brief into publication-ready, fact-checked, brand-compliant content.

**Realistic timing per piece:** FAQ 30-35 min · article 35-45 min · whitepaper 45-75 min · research paper 60-90 min.

### What Makes It Different

Unlike single-prompt tools (ChatGPT, Gemini), ContentForge runs your content through **10 specialized quality gates**:

✅ **Three-Layer Fact Verification** — Phases 2, 4, and 7 each re-check claims against the verified source ledger. Production runs typically achieve high factual accuracy — verify every claim before publishing.
✅ **95%+ Citation Accuracy** — All claims traceable to verified sources
✅ **Brand Voice Consistency** — Automatically applies your brand guidelines
✅ **Natural Language** — Phase 6.5 Humanizer removes AI writing patterns
✅ **SEO Optimized** — Keyword targeting, meta tags, readability scoring
✅ **Human Oversight** — Content <5.0/10 escalates to review, never auto-publishes

### Who Should Use This

- **Digital marketing agencies** managing 50-200 brands
- **In-house content teams** with high volume (20-50+ pieces/month)
- **Regulated industries** (Pharma, BFSI, Healthcare, Legal) requiring fact-checking
- **SEO teams** needing research-backed, cited content at scale
- **Enterprise brands** requiring consistent quality across teams

---

## Installation in Cowork

### Step 1: Open Cowork
Go to [claude.ai](https://claude.ai) and log in to your Cowork workspace.

> **Important:** the `/plugin` slash command does **not** exist in Cowork — it is Claude Code CLI/IDE only. In Cowork you install and manage plugins from the **Plugins panel**. Once ContentForge is installed, its skills (`/contentforge:*`) work normally in Cowork chat; only the `/plugin` *management* commands are unavailable.

### Step 2: Open the Plugins Panel
In the Cowork sidebar, click **Plugins** (or go to **Settings → Plugins**).

### Step 3: Add the Marketplace
Click **Add marketplace** and enter:
```
indranilbanerjee/neels-plugins
```

The marketplace appears in the list with its available plugins.

### Step 4: Install ContentForge
Find **contentforge** in the marketplace listing and click **Install**.

The panel shows the installed version — **ContentForge v3.16.1**.

### Step 5: Verify Installation
Back in Cowork chat, type `/` and start typing `contentforge`. The skill list should autocomplete with:
```
/contentforge:create-content   — Run the full 10-phase pipeline on one piece
/contentforge:batch-process    — Work through a queue of pieces, one at a time
/contentforge:content-refresh  — Update old content
/contentforge:cf-variants      — Generate A/B variations of headlines, hooks, CTAs
/contentforge:cf-analytics     — Quality score trends and brand performance
/contentforge:publish          — Publish to Webflow/WordPress, or export HTML
  ... (22 skills total)
```

**✅ Installation Complete!** Now set up your integrations.

---

## MCP Integration Setup

ContentForge does **not** require Google Sheets or Google Drive. Local tracking is the zero-config default: brand profiles, run records, and finished `.docx` files are written to the filesystem with no integration set up at all.

Drive is **optional**, and its main job is Cowork team persistence — the Cowork sandbox filesystem disappears at session end, so a team that wants outputs it can reach later should route them to shared Drive. Other optional integrations (Notion, Webflow, Slack, Canva) unlock publishing, asset, and notification steps.

### Zero-config default (no setup needed)

Run `/contentforge:create-content` straight after install. Tracking and outputs go to local storage. Everything in the 10-phase pipeline works.

### Optional: Drive persistence for Cowork teams

Cowork supports **HTTP MCPs only** — stdio/`npx` MCP servers are a Claude Code CLI feature and cannot be added in Cowork.

**1. Connect Google Drive**
In Cowork: profile menu → **Settings** → **Integrations** → find **Google Drive** → **Connect**, and sign in with the account that owns your team's shared Drive.

**2. Run the setup skill**
```
/contentforge:cf-cowork-setup
```
It verifies the Cowork environment, confirms a Drive MCP is reachable, creates the canonical Drive folder layout, and persists the routing config. One run per team.

**What rides that persistence (v4.0):** everything under the brand directory — the profile and per-run checkpoints as before, plus the lifecycle stores the 4.0 loop depends on: `audits/` (recorded cf-audit findings that cf-calendar and content-refresh read across sessions), `aeo/checks.json` (AI-visibility history), and each run's telemetry files. On Cowork WITHOUT Drive routing these stores vanish with the session like everything else in the sandbox — the loop then still works within a session but cannot compound across sessions, which is most of its point. Teams that want the lifecycle loop should treat Drive routing as required, not optional.

**3. Verify**
```
/contentforge:cf-integrations
```
It lists what is connected and what each connector unlocks.

### Optional: other connectors

A fresh install ships an **empty** `.mcp.json` — zero connectors auto-connect. The full opt-in catalog of 16 HTTP connectors lives in `.mcp.json.connectors-reference` in the plugin repo (Notion, Canva, Webflow, Slack, Gmail, Google Calendar, Figma, fal.ai, Replicate, plus aggregator options — Pipedream, Composio, Zapier, Make).

Add one interactively:
```
/contentforge:cf-connect <name>
```

---

## First-Time Setup (5 minutes)

Before generating your first content, create a **brand profile**.

### Create Your First Brand Profile

In Cowork, type:
```
/contentforge:brand-setup
```

**Cowork will prompt you:**

**1. Brand Name:**
```
What is your brand name?
Example: AcmeCorp, TechStartup, HealthcareBrand
```
Type: `AcmeCorp` (or your brand name)

**2. Industry:**
```
What industry is this brand in?
Options: Technology, Healthcare, Finance (BFSI), Pharma, Legal, E-commerce, SaaS, Agency, Other
```
Type: `Technology`

**3. Voice:**
```
What is your brand's voice?
Options: Authoritative, Conversational, Technical, Witty, Professional, Warm, Data-Driven
```
Type: `Authoritative`

**4. Tone:**
```
What tone should content use?
Options: Formal, Casual, Professional, Friendly, Serious, Playful
```
Type: `Professional`

**5. Target Audience:**
```
Who is your primary audience?
Example: B2B SaaS decision-makers, Healthcare executives, Small business owners
```
Type: `B2B SaaS decision-makers`

**6. Key Terminology (Optional):**
```
Any specific terms or phrases your brand uses?
Example: Use "customer" not "user", "AI-powered" not "AI-driven"
Format: approved_term:banned_term, separated by commas
```
Type: `customer:user, AI-powered:AI-driven` (or leave blank)

**7. Guardrails (Optional):**
```
Any topics or phrases to avoid?
Example: Don't mention competitors, Avoid controversial political topics
```
Type: `Don't mention competitors directly` (or leave blank)

**Cowork will respond:**
```
✓ Brand profile created: AcmeCorp
✓ Saved to: ContentForge/AcmeCorp/Brand-Guidelines/AcmeCorp-brand-profile.json
  (mirrored to shared Google Drive if you ran /contentforge:cf-cowork-setup)

Your brand is ready! Use /contentforge:create-content to generate your first piece.
```

**✅ Brand Setup Complete!** This is a **one-time setup per brand**. For agencies managing 50 brands, you'll create 50 profiles (once), then reuse them.

---

## Using ContentForge Commands

### Command 1: `/contentforge:create-content` (Generate Single Piece)

**Use Case:** Create 1 high-quality content piece

#### Interactive Mode (Recommended for Beginners)

Type:
```
/contentforge:create-content
```

**Cowork prompts:**
```
1️⃣ What's the topic/title?
```
Type: `AI in Healthcare: 2026 Trends and Predictions`

```
2️⃣ What content type?
Options: article, blog, whitepaper, faq, research_paper
```
Type: `article`

```
3️⃣ Which brand?
Available: AcmeCorp, TechStartup
```
Type: `AcmeCorp`

```
4️⃣ Target audience? (Optional)
```
Type: `Healthcare CIOs`

```
5️⃣ Primary keyword? (Optional)
```
Type: `AI healthcare 2026`

**Cowork starts the pipeline:**
```
✓ Starting ContentForge pipeline for "AI in Healthcare: 2026 Trends and Predictions"
✓ Brand: AcmeCorp | Type: article | Estimated time: 35-45 minutes

Phase 1/10: Research Agent (3-7 min)
  → Analyzing SERP for "AI in Healthcare: 2026 Trends and Predictions"
  → Mining authoritative sources...
  → Found 12 sources (Nature, NEJM, HealthIT News, etc.)
  → Generating structured outline...
✓ Phase 1 complete (6m 40s)

Step 0.5: Title Curation (inline, needs your input)
  → 5 title options generated with character counts
  → You picked option 3: "AI in Healthcare: 2026 Trends and Predictions"
✓ Step 0.5 complete (1m 00s)

Phase 2/10: Fact Checker (2-3 min)
  → Verifying 12 source URLs...
  → All URLs accessible ✓
  → Validating claims against sources...
  → 18/20 claims strongly verified (90%)
✓ Phase 2 complete (2m 45s)

Phase 3/10: Content Drafter (5-9 min)
  → Drafting with AcmeCorp brand voice...
  → Target: 1,500-2,000 words
  → Current: 1,847 words ✓
  → Citations: 14 inline citations ✓
✓ Phase 3 complete (8m 30s)

Phase 3.5/10: Visual Asset Annotator (2-4 min)
  → Scanning draft for visual opportunities...
  → 2 charts generated from Phase 2 verified statistics ✓
  → Visual manifest complete: placement, alt text, data source ✓
  → 1 human-action TODO marked (product screenshot)
✓ Phase 3.5 complete (3m 10s)

Phase 4/10: Scientific Validator (2-3 min)
  → Scanning for hallucinations...
  → Checking for unsourced claims...
  → All claims traceable ✓
  → Zero hallucinations detected ✓
✓ Phase 4 complete (2m 32s)

Phase 5/10: Structurer & Proofreader (2-3 min)
  → Grammar check: 100% accurate ✓
  → Readability: Grade 11.2 (target 10-12) ✓
  → Brand compliance: 100% ✓
✓ Phase 5 complete (2m 51s)

Phase 6/10: SEO/GEO Optimizer (2-3 min)
  → Keyword placement (the gate): title ✓ first 100 words ✓ 2 H2s ✓ conclusion ✓ meta description ✓
  → Keyword density: 1.6% (advisory band 1.0-2.0%, no stuffing flag)
  → Meta title: "AI in Healthcare: 2026 Trends | AcmeCorp" ✓
  → Meta description: 155 chars ✓
✓ Phase 6 complete (2m 29s)

Phase 6.5/10: Humanizer (1-2 min)
  → Walking the 43-pattern catalog across all 7 buckets...
  → Removed: 12 instances of "delve", "leverage", "robust"
  → Burstiness score: 0.78 (content-derived variation, advisory)
  → SEO preserved: keyword placement unchanged ✓
✓ Phase 6.5 complete (1m 45s)

Phase 7/10: Reviewer (2-3 min)
  → Scoring across 5 dimensions...
  → Content Quality: 9.5/10
  → Citation Integrity: 9.0/10
  → Brand Compliance: 9.5/10
  → SEO Performance: 8.8/10
  → Readability: 9.0/10
  → Overall Score: 9.2/10 (approved, ≥7.0) ✓
✓ Phase 7 complete (2m 38s)

Phase 8/10: Output Manager (1-2 min)
  → Generating .docx file...
  → Saving to the brand output folder...
  → File: ContentForge/AcmeCorp/AI-in-Healthcare-2026-Trends_v1.0.docx
  → Updating tracking record...
✓ Phase 8 complete (1m 22s)

═══════════════════════════════════════════════════════════════
✅ CONTENT GENERATION COMPLETE
═══════════════════════════════════════════════════════════════
Title: AI in Healthcare: 2026 Trends and Predictions
Brand: AcmeCorp
Type: Article
Processing Time: 35 minutes 42 seconds

Quality Score: 9.2/10 (Grade A+)
  → Content Quality: 9.5/10
  → Citation Integrity: 9.0/10
  → Brand Compliance: 9.5/10
  → SEO Performance: 8.8/10
  → Readability: 9.0/10

Content Stats:
  → Word Count: 1,847 (Target: 1,500-2,000)
  → Citations: 14 sources
  → Keyword Placement: 5/5 required positions hit (density 1.6%, advisory)
  → Readability: Grade 11.2
  → Humanization: Burstiness 0.78, zero AI patterns
  → Loops Used: 0 (approved on first review)

Factual Accuracy: 100%
Hallucinations: 0
Broken Links: 0

Output Location:
📁 ContentForge/AcmeCorp/AI-in-Healthcare-2026-Trends_v1.0.docx
   (routed to shared Google Drive if you ran /contentforge:cf-cowork-setup)

[Click here to download] (Cowork generates download link)

Next Steps:
  → Review the content in the .docx file
  → Use /contentforge:publish to publish to WordPress/Notion
  → Use /contentforge:cf-variants to create A/B test variations
  → Use /contentforge:cf-analytics to track quality over time
═══════════════════════════════════════════════════════════════
```

#### Quick Mode (All Parameters at Once)

Type:
```
/contentforge:create-content "AI in Healthcare: 2026 Trends" --type=article --brand=AcmeCorp --audience="Healthcare CIOs" --keyword="AI healthcare 2026"
```

Same pipeline runs, skips the prompts. **Use this when you know all parameters.**

---

### Command 2: `/contentforge:batch-process` (Work Through a Queue of 10-50+ Pieces)

**Use Case:** Agency needs 20 blog posts for multiple clients, produced unattended from one queue

Batch processing is **sequential**: one full 10-phase pipeline at a time, in priority order. It is not faster per piece than running each piece yourself — the win is that you set up the queue once and walk away. Every piece is checkpointed as it finishes, so an interrupted batch picks up where it stopped via `/contentforge:resume`.

#### Step 1: Prepare the Requirements Queue

Local tracking is the default and needs no setup. If your team uses the Google Sheets backend instead, create a sheet with these columns:
| requirement_id | content_type | title | target_audience | brand | word_count | priority | status |
|----------------|--------------|-------|-----------------|-------|------------|----------|---------|
| REQ-001 | article | AI in Healthcare 2026 | Healthcare CIOs | AcmeCorp | 2000 | 1 | pending |
| REQ-002 | blog | 10 Remote Team Tips | HR Managers | TechStartup | 1500 | 2 | pending |
| REQ-003 | whitepaper | Future of SEO | Marketing Directors | AgencyCo | 4000 | 1 | pending |

**Important:**
- `status=pending` means "ready to process"
- `priority=1` is highest (urgent), `5` is lowest
- All brands must have profiles created (use `/contentforge:brand-setup` first)

#### Step 2: Make the Sheet Reachable (Google backend only)

Share the sheet with the Google account connected in **Settings → Integrations**, with Editor access. Skip this step entirely on the local backend.

#### Step 3: Run Batch Processing

In Cowork, type:
```
/contentforge:batch-process https://docs.google.com/spreadsheets/d/ABC123XYZ/edit
```

**Cowork responds:**
```
✓ Loading requirements from Google Sheet...
✓ Found 12 rows

╔═══════════════════════════════════════════════════════════════╗
║ Batch Queue Summary                                           ║
╠═══════════════════════════════════════════════════════════════╣
║ Total Rows: 12                                                ║
║ Valid: 12 | Skipped: 0 | Validation Errors: 0                 ║
╠═══════════════════════════════════════════════════════════════╣
║ Queue Breakdown:                                              ║
║   Priority 1: 3 pieces (Est: 130 min)                         ║
║   Priority 2: 5 pieces (Est: 195 min)                         ║
║   Priority 3: 4 pieces (Est: 150 min)                         ║
╠═══════════════════════════════════════════════════════════════╣
║ Execution Plan:                                               ║
║   Mode: sequential — one full pipeline at a time              ║
║   Order: priority 1 → 5, then queue order                     ║
║   Estimated Total Time: 475 minutes (~7.9 hours)              ║
║   Checkpointed: interrupted runs resume, no work is lost      ║
╚═══════════════════════════════════════════════════════════════╝

Ready to start batch processing? (yes/no)
```

Type: `yes`

**Progress Report (after each piece):**
```
╔═════════════════════════════════════════════════════════════════╗
║ ContentForge Batch Progress                                     ║
║ Total: 12 pieces | Completed: 4 | Review required: 0 | Failed: 0 ║
║ Now running: REQ-005 (5 of 12) | Remaining: 7 | Est: 285 min    ║
╠═════════════════════════════════════════════════════════════════╣
║ Current piece                                                   ║
║ REQ-005 | Case Study Acme      | Phase 6.5 → | Est: 8min        ║
╠═════════════════════════════════════════════════════════════════╣
║ Completed                                                       ║
║ ✓ REQ-001 | Whitepaper AI Health | Score: 9.2                   ║
║ ✓ REQ-002 | Remote Teams Blog    | Score: 8.7                   ║
║ ✓ REQ-003 | SEO Whitepaper       | Score: 9.1                   ║
║ ✓ REQ-004 | FAQ Product Launch   | Score: 8.8                   ║
╚═════════════════════════════════════════════════════════════════╝
```

**When the queue drains:**
```
═══════════════════════════════════════════════════════════════
✅ BATCH PROCESSING COMPLETE
═══════════════════════════════════════════════════════════════
Total Pieces: 12
Completed Successfully: 12 (100%)
Review Required: 0 (0%)
Failed: 0 (0%)

Average Quality Score: 8.9 / 10
Total Processing Time: 7h 46min (sequential)

Output Location:
📁 ContentForge/Batch_2026-07-17_14-30/

Next Steps:
  → Spot-check 2-3 completed pieces
  → Collect all 12 .docx files from the batch folder
  → Use /contentforge:publish to publish to CMS in bulk
═══════════════════════════════════════════════════════════════
```

---

### Command 3: `/contentforge:content-refresh` (Update Old Content)

**Use Case:** You have a 12-month-old article that needs updated stats

In Cowork, type:
```
/contentforge:content-refresh https://docs.google.com/document/d/OLD-ARTICLE-ID
```

**Cowork prompts:**
```
What refresh scope?
  → light (20%): Update stats/examples only (8-12 min)
  → medium (50%): Rewrite intro, conclusion, 3-5 sections (15-20 min)
  → heavy (80%): Near-complete rewrite (22-30 min)
```

Type: `medium`

**Cowork analyzes:**
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

Outdated Sections (Update):
⚠ Para 1: Intro references "2025 predictions" (now outdated)
⚠ Para 3: Statistics from 2024 market report
⚠ Citations: 6/15 links are broken (404 errors)

Recommendation: Medium Refresh (50% rewrite)
─────────────────────────────────────────────────────

Proceed with medium refresh? (yes/no)
```

Type: `yes`

**Pipeline runs (15-20 min)**, then:
```
✓ Content Refreshed!

Version Control:
  Original: AI-in-Healthcare-2025-Trends_v1.0.docx (preserved)
  Refreshed: AI-in-Healthcare-2025-Trends_v1.1.docx (new)

Quality Score: 9.1/10 (was 8.9/10) → +0.2 improvement
Freshness Score: 95/100 (was 42/100)

What Changed:
  → Introduction: Completely rewritten
  → 6 sections: Updated statistics (2024 → 2026 data)
  → 4 new sources added
  → 6 broken links fixed

SEO Preservation:
  → Keyword density: 2.3% → 2.4% (±0.1%, within target)
  → URL slug: Preserved (maintains backlinks)
  → Internal links: All preserved

Output: ContentForge Output/AcmeCorp/AI-in-Healthcare-2025-Trends_v1.1.docx
```

---

### Command 4: `/contentforge:cf-variants` (A/B Testing)

**Use Case:** Test 3 different angles for the same topic

In Cowork, type:
```
/contentforge:cf-variants "AI in Healthcare 2026" --count=3 --brand=AcmeCorp
```

**Cowork generates:**
```
✓ Generating 3 variants for A/B testing...

Variant A: "AI in Healthcare: How Machine Learning is Revolutionizing Patient Care"
Angle: Technology-focused, benefits-driven
Hook: "What if AI could predict disease before symptoms appear?"

Variant B: "The Doctor Will See You Now: AI's Role in Modern Healthcare"
Angle: Human-centric, accessibility-focused
Hook: "Healthcare is going digital, but the human touch remains"

Variant C: "AI Healthcare: $50 Billion Market by 2028 — Here's What's Driving Growth"
Angle: Data-driven, market analysis
Hook: "The numbers don't lie: AI is transforming healthcare economics"

Which variant(s) would you like to generate?
(Type: A, B, C, or 'all' for all 3)
```

Type: `all`

**Runs 3 pipelines one after another**, outputs 3 .docx files.

---

### Command 5: `/contentforge:cf-analytics` (Track Performance)

**Use Case:** View quality score trends over the last 30 days

In Cowork, type:
```
/contentforge:cf-analytics --days=30
```

**Cowork displays:**
```
═══════════════════════════════════════════════════════════════
Content Analytics Dashboard (Last 30 Days)
═══════════════════════════════════════════════════════════════

Total Pieces Produced: 47
Average Quality Score: 8.8/10

Quality Trend:
  Week 1: 8.5/10
  Week 2: 8.7/10
  Week 3: 8.9/10
  Week 4: 9.0/10
  → +0.5 improvement over 30 days ✓

Top Performing Content Types:
  1. Whitepaper: 9.2/10 avg (5 pieces)
  2. Article: 8.9/10 avg (25 pieces)
  3. Blog: 8.6/10 avg (15 pieces)

Brand-Specific Patterns:
  AcmeCorp: 9.1/10 avg (20 pieces)
  TechStartup: 8.7/10 avg (15 pieces)
  AgencyCo: 8.5/10 avg (12 pieces)

Bottleneck Analysis:
  Slowest Phase: Phase 3 (Content Drafter) — 6.5 min avg
  Recommendation: Consider shorter word count targets for blogs

Alerts:
  ⚠ TechStartup brand: 2 pieces this week scored <7.0
     Recommendation: Review brand profile, update terminology

Next Steps:
  → Review flagged TechStartup content
  → Continue high-performing whitepaper strategy
  → Optimize Phase 3 timing with shorter blog targets
═══════════════════════════════════════════════════════════════
```

---

### Command 6: `/contentforge:publish` (Publish to CMS)

**Use Case:** Publish finished content directly to WordPress

In Cowork, type:
```
/contentforge:publish AcmeCorp/AI-in-Healthcare-2026-Trends_v1.0.docx --platform=wordpress --status=publish
```

**Cowork prompts:**
```
Which WordPress site?
(You have 2 configured: acmecorp.com, blog.acmecorp.com)
```

Type: `acmecorp.com`

```
Select category:
(Available: Tech, Healthcare, AI, Uncategorized)
```

Type: `Healthcare`

**Cowork publishes:**
```
✓ Publishing to WordPress (acmecorp.com)...
✓ Post created successfully!

Post Details:
  Title: AI in Healthcare: 2026 Trends and Predictions
  URL: https://acmecorp.com/blog/ai-healthcare-2026-trends
  Category: Healthcare
  Status: Published
  Featured Image: Uploaded from .docx
  Meta Title: AI in Healthcare: 2026 Trends | AcmeCorp
  Meta Description: Explore AI in healthcare trends...

[View Post] (Cowork generates clickable link)
```

---

## Workflows for Different Use Cases

### Workflow 1: Freelance Content Writer (10 pieces/week)

**Goal:** Produce 10 high-quality blog posts per week for different clients

**Step 1: Setup (Monday morning, 30 min)**
- Create 3 brand profiles (one per client): `/contentforge:brand-setup`
- Fill the requirements queue with 10 rows (local tracking, or a Google Sheet if your team uses that backend)

**Step 2: Batch Process (Monday morning onward, unattended)**
- `/contentforge:batch-process https://docs.google.com/spreadsheets/d/requirements`
- Let it work through the queue one piece at a time (10 blogs ≈ 5-6 hours)
- If the session drops, `/contentforge:resume` picks up from the last checkpoint

**Step 3: Quality Check (30 min)**
- Spot-check 3 random pieces
- Review any flagged for human review (<5.0 score)

**Step 4: Deliver**
- Collect all 10 .docx files from the batch output folder
- Send to clients via email or project management tool

**Time Saved:** you spend ~1 hour of hands-on time instead of writing 10 pieces yourself

---

### Workflow 2: Agency Managing 50 Brands

**Goal:** Produce 100 pieces/month across 50 brands

**Step 1: One-Time Setup (2-3 hours)**
- Create 50 brand profiles: `/contentforge:brand-setup` (repeat 50 times)
- Set up Google Sheet with columns for all requirements
- Configure optional CMS integrations (WordPress, Notion)

**Step 2: Monthly Planning (1st of month, 1 hour)**
- Fill Google Sheet with 100 requirements
- Assign priorities (urgent client campaigns = priority 1)
- Verify all brands have profiles

**Step 3: Batch Processing (1st-5th of month, mostly unattended)**
- Run 4-5 batch runs (20-25 pieces per batch)
- `/contentforge:batch-process https://docs.google.com/spreadsheets/d/requirements`
- Each batch runs sequentially: ~12-15 hours for 20 pieces, spread across days and resumable

**Step 4: Quality Assurance (Ongoing)**
- Spot-check 10% of output (10 pieces)
- Review flagged content (<5% typically)

**Step 5: Publishing (5th-10th of month)**
- `/contentforge:publish` in bulk to client WordPress/Notion sites
- Or download and deliver via project management

**Step 6: Analytics (End of month)**
- `/contentforge:cf-analytics --days=30`
- Identify top-performing brands/types
- Optimize next month's strategy

**Time Saved:** 200-250 hours/month vs manual content creation

---

### Workflow 3: Regulated Industry (Pharma Brand)

**Goal:** Produce compliant, fact-checked content with zero hallucinations

**Step 1: Brand Setup with Strict Guardrails**
```
/contentforge:brand-setup PharmaCorpGlobal

Industry: Pharma
Voice: Authoritative
Tone: Formal
Guardrails:
  - All medical claims must be cited
  - Use "patients" not "consumers"
  - Avoid disease fearmongering
  - Comply with FDA/EMA regulations
  - Never mention off-label use
```

**Step 2: Generate Content with Extra Scrutiny**
```
/contentforge:create-content "New Diabetes Treatment Options in 2026" --type=whitepaper --brand=PharmaCorpGlobal --audience="Endocrinologists"
```

**Step 3: Review Quality Score Breakdown**
- **Target:** ≥9.0/10 overall, 100% brand compliance
- **Citation Integrity:** Must be 9.0+ (all claims cited to peer-reviewed sources)

**Step 4: Human Medical Review**
- Even if score is 9.5/10, have in-house medical writer review
- Verify all statistics against original sources
- Check regulatory compliance

**Step 5: Publish Only After Approval**
- Never auto-publish for regulated industries
- Use `/contentforge:publish` only after legal/medical sign-off

**Quality Assurance:** Three-layer fact verification + human review = zero compliance issues

---

## Understanding the 10-Phase Pipeline

### Visual Pipeline Flow

```
Input: "AI in Healthcare: 2026 Trends" (article, 2000 words, brand: AcmeCorp)
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Research Agent (3-5 min)                           │
│ → SERP analysis for topic                                   │
│ → Mine 10-15 authoritative sources                          │
│ → Analyze competitor content                                │
│ → Generate structured outline                               │
│ Quality Gate: 5+ live sources, differentiated angle ✓       │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 0.5: Title Curation (inline, needs your input)         │
│ → Generate 4-5 title options with character counts          │
│ → You pick one (or pass --title to skip the prompt)         │
│ Checkpointed before Phase 2 starts ✓                        │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Fact Checker (2-3 min)                             │
│ → Verify all URLs accessible (no 404s)                      │
│ → Validate claims against sources                           │
│ → Assign confidence scores                                  │
│ Quality Gate: 80%+ verified, zero flagged, URLs live ✓      │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Content Drafter (5-7 min)                          │
│ → Generate first draft with brand voice                     │
│ → Include inline citations (APA format)                     │
│ → Target word count ±10%                                    │
│ Quality Gate: Word count on target, citations ≥1/300w ✓     │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3.5: Visual Asset Annotator (2-4 min)                 │
│ → Generate charts from Phase 2 verified statistics          │
│ → Mark visual opportunities and human-action TODOs          │
│ → Build the asset manifest (placement, alt text, source)    │
│ Quality Gate: every chart traceable, manifest complete ✓    │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Scientific Validator (2-3 min)                     │
│ → Scan for hallucinations (fabricated stats/studies)        │
│ → Ensure all claims traceable to sources                    │
│ → Validate logical consistency                              │
│ Quality Gate: Zero hallucinations, all claims traceable ✓   │
│ IF FAILS → Loop back to Phase 3 (max 2 loops)               │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Structurer & Proofreader (2-3 min)                 │
│ → Correct grammar/spelling (100% accuracy)                  │
│ → Optimize readability (Grade 10-12 for articles)           │
│ → Enforce brand terminology                                 │
│ Quality Gate: Zero errors, readability on target ✓          │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: SEO/GEO Optimizer (2-3 min)                        │
│ → Place keywords in the 5 required positions                │
│ → Check density against the 1.0-2.0% advisory band          │
│ → Generate meta title, description, URL slug                │
│ Quality Gate: all 5 placements hit, meta optimized ✓        │
│ (Density is advisory — placement is the gate)               │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6.5: Humanizer ⭐ (1-2 min)                            │
│ → Remove AI telltale phrases (43-pattern catalog)           │
│ → Content-derived variation (burstiness advisory)           │
│ → Inject brand personality                                  │
│ → Verify SEO preserved (keyword placement unchanged)        │
│ Quality Gate: AI patterns removed, grounding pass complete ✓│
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: Reviewer (2-3 min)                                 │
│ → Score across 5 dimensions:                                │
│   • Content Quality (30%): 9.5/10                           │
│   • Citation Integrity (25%): 9.0/10                        │
│   • Brand Compliance (20%): 9.5/10                          │
│   • SEO Performance (15%): 8.8/10                           │
│   • Readability (10%): 9.0/10                               │
│ → Overall: 9.2/10 (approved)                                │
│ Quality Gate: Score ≥7.0 AND every dimension floor met ✓    │
│ IF 5.0-6.9 → Loop back to the weakest phase (max 2 loops)   │
│ IF <5.0 → Stop, escalate to a human                         │
└─────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 8: Output Manager (1-2 min)                           │
│ → Generate .docx file with the 3 required appendices        │
│ → Save to the brand output folder (or Drive, if routed)     │
│ → Update the tracking record                                │
│ Output: AI-in-Healthcare-2026-Trends_v1.0.docx ✓            │
└─────────────────────────────────────────────────────────────┘
  ↓
✅ COMPLETE (article: 35-45 min total)
```

### Key Concept: Feedback Loops

If a phase fails its quality gate, the pipeline **loops back** with specific feedback:

**Example: Hallucination Detected**
```
Phase 4: Scientific Validator
  ❌ Found unsourced claim: "85% of hospitals use AI by 2026"
  → Looping back to Phase 3 with feedback:
     "Claim '85% of hospitals...' needs citation. Check sources from Phase 2."

Phase 3: Content Drafter (Loop 1)
  → Rewrites paragraph
  → Adds citation: [Source: McKinsey Healthcare Report 2025]

Phase 4: Scientific Validator (Retry)
  ✓ All claims now traceable
  → Continues to Phase 5
```

**Max Loops:**
- Phase 4 → Phase 3: 2 loops
- Phase 7 → Any phase: 2 loops
- **Total: 5 iterations max** before human escalation

This prevents infinite loops while allowing quality improvements.

---

## Quality Scores & What They Mean

### 5-Dimension Scoring System

Every piece is scored across **5 dimensions** (weighted):

#### 1. Content Quality (30% weight)
**What it measures:**
- Depth of analysis
- Originality (not just rehashing existing content)
- Actionable insights
- Clarity and structure

**Scoring:**
- **9-10:** Exceptional depth, unique insights, highly actionable
- **7-8:** Good depth, some original angles, useful
- **5-6:** Basic coverage, minimal originality, somewhat useful
- **<5:** Superficial, repetitive, low value

#### 2. Citation Integrity (25% weight)
**What it measures:**
- Accuracy of citations
- Relevance to claims
- Authority of sources (peer-reviewed > blog)
- Freshness (2024-2026 sources > 2020)

**Scoring:**
- **9-10:** All citations accurate, highly authoritative, <2 years old
- **7-8:** 80-90% accurate, mostly authoritative, some older sources
- **5-6:** 60-80% accurate, mixed authority, many older sources
- **<5:** <60% accurate, weak sources, very outdated

#### 3. Brand Compliance (20% weight)
**What it measures:**
- Voice match (authoritative, conversational, etc.)
- Terminology adherence (approved terms used, banned terms avoided)
- Style guide compliance (formatting, citation style)
- Guardrails respected (no prohibited topics)

**Scoring:**
- **9-10:** Perfect voice match, 100% terminology compliance
- **7-8:** Good voice match, 1-2 minor terminology slips
- **5-6:** Voice mostly matches, 3-5 terminology issues
- **<5:** Voice mismatch, multiple guardrail violations

#### 4. SEO Performance (15% weight)
**What it measures:**
- Keyword density (target: 1.5-2.5%)
- Keyword placement (title, H2s, first para, conclusion)
- Meta tag optimization (title length, description)
- Readability for search engines

**Scoring:**
- **9-10:** Perfect keyword density, all placements hit, meta optimized
- **7-8:** Good density, most placements hit, minor meta issues
- **5-6:** Density off-target, missed some placements
- **<5:** Poor keyword usage, meta tags missing/bad

#### 5. Readability (10% weight)
**What it measures:**
- Grade level appropriate for content type
- Sentence variety (burstiness)
- Flow and coherence
- Grammar and spelling accuracy

**Scoring:**
- **9-10:** Perfect grade level, excellent flow, zero errors
- **7-8:** On-target grade level, good flow, 1-2 minor errors
- **5-6:** Slightly off-target grade level, choppy flow, 3-5 errors
- **<5:** Wrong grade level, poor flow, many errors

### Composite Score Calculation

**Example:**
- Content Quality: 9.5/10 × 30% = 2.85
- Citation Integrity: 9.0/10 × 25% = 2.25
- Brand Compliance: 9.5/10 × 20% = 1.90
- SEO Performance: 8.8/10 × 15% = 1.32
- Readability: 9.0/10 × 10% = 0.90

**Overall Score: 9.22/10** (rounds to 9.2)

### Decision Bands

These three bands come from `config/scoring-thresholds.json`, the single source of truth for every quality number:

- **≥7.0 — Approved.** Passes the composite gate and is delivered.
- **5.0-6.9 — Loop.** The pipeline sends the piece back to its weakest phase for rework. It is **never** auto-delivered at this score.
- **<5.0 — Human escalation.** The run stops and a person has to decide.

Note that the composite score is not the only gate: every dimension also has a floor (Citation Integrity ≥7.0, Brand Compliance ≥7.0, Content Quality / SEO / Readability ≥6.0). A piece can score 7.4 overall and still loop because one dimension sits under its floor. Regulated industries raise the bar further — Pharma, Healthcare, and Legal require ≥8.0; BFSI ≥7.5.

### What to Do Based on Score

**Score ≥7.0 (approved):** ✅ Delivered. Give it a read, then publish.

**Score 5.0-6.9 (loop band):** ⚠️ The pipeline already tried to fix it. If it reaches you at this score, its revision budget ran out:
- Check the dimension breakdown for the weakest one
- If Citation Integrity is low: add more authoritative sources
- If Brand Compliance is low: review the brand profile and terminology
- If SEO Performance is low: rerun Phase 6 with better keyword placement

**Score <5.0 (human escalation):** 🚫 Auto-flagged, never auto-published
- Review the run output for the specific failures
- Fix manually, or regenerate with a sharper brief

---

## Batch Processing for Agencies

### What Batch Processing Actually Does

Batch processing runs the **same** 10-phase pipeline you'd run by hand, once per queued piece, **one at a time**. It does not make any individual piece faster.

What it buys you:
- **Unattended operation** — queue 20 pieces, walk away, come back to 20 .docx files
- **Priority ordering** — urgent client work runs first
- **Checkpointed and resumable** — a dropped session doesn't lose completed pieces; `/contentforge:resume` continues the run
- **Per-piece status tracking** — every row ends as `completed`, `review_required`, or `failed`
- **Failure isolation** — one bad row doesn't halt the rest of the queue

**Plan the wall-clock time accordingly:** 20 blog posts ≈ 20 × 30-35 min ≈ 10-12 hours of sequential runtime.

### Setting Up Batch Processing

#### Queue Columns

The canonical required-column list lives in `agents/09-batch-orchestrator.md` (see **Required Columns**). Reproduced here for convenience:

| Column | Type | Description | Required | Example |
|--------|------|-------------|----------|---------|
| requirement_id | string | Unique ID | ✅ | REQ-001 |
| content_type | enum | article, blog, whitepaper, faq, research_paper | ✅ | article |
| title | string | Content topic/title | ✅ | "AI in Healthcare 2026" |
| target_audience | string | Who this is for | ✅ | "Healthcare CIOs" |
| brand | string | Brand profile name (must exist) | ✅ | "AcmeCorp" |
| word_count | integer | Target word count | ✅ | 2000 |
| priority | integer | 1-5 (1=highest) | ✅ | 1 |
| status | enum | pending, in_progress, completed, failed, review_required | ✅ | pending |
| primary_keyword | string | SEO keyword | ❌ | "AI healthcare" |
| notes | string | Special instructions | ❌ | "Mention new FDA regulations" |

**Important Rules:**
1. `status=pending` means "ready to process" (batch will skip others)
2. `priority=1` processes first, `priority=5` last
3. All brands must have profiles created first
4. Word count must be within the content type's canonical range in `config/scoring-thresholds.json` (blog 800-1500, article 1500-2000, whitepaper 2500-5000, research paper 4000-8000, FAQ 600-1200)

### Priority System Explained

**Priority Levels:**
- **1 (Urgent):** Client deadline tomorrow, campaign launch imminent
- **2 (High):** Important but not urgent, next week's content
- **3 (Normal):** Standard blog posts, regular cadence
- **4 (Low):** Evergreen content, no specific deadline
- **5 (Backlog):** Nice-to-have, filler content

**How Batch Processes Priorities:**
```
Queue before sorting:
  REQ-005 (Priority 3, Article)
  REQ-001 (Priority 1, Whitepaper)
  REQ-003 (Priority 2, Blog)
  REQ-002 (Priority 1, Article)

Queue after sorting:
  1. REQ-001 (Priority 1, Whitepaper) ← runs first, alone
  2. REQ-002 (Priority 1, Article)    ← starts only when REQ-001 finishes
  3. REQ-003 (Priority 2, Blog)
  4. REQ-005 (Priority 3, Article)
```

**Pro Tip:** Put anything with a hard deadline at priority 1 — the queue never runs two pieces at once, so position in the queue is what determines when a piece lands.

### Monitoring Batch Progress

**Progress report after each piece:**
```
╔═════════════════════════════════════════════════════════════════╗
║ ContentForge Batch Progress                                     ║
║ Started: 2:30 PM | Elapsed: 3h 42min                            ║
╠═════════════════════════════════════════════════════════════════╣
║ Summary                                                         ║
║ Total: 12 pieces | Completed: 7 | Review required: 0 | Failed: 0 ║
║ Now running: REQ-010 (8 of 12) | Remaining: 4                   ║
║ Average Quality Score: 8.9 / 10 (from 7 completed)              ║
╠═════════════════════════════════════════════════════════════════╣
║ Current piece                                                   ║
║ ┌─────────────────────────────────────────────────────────────┐ ║
║ │ REQ-010 | Article Remote Work | Phase 6.5 → | Est: 8min     │ ║
║ │ Progress: ████████████████░░░░  (72%)                        │ ║
║ └─────────────────────────────────────────────────────────────┘ ║
╠═════════════════════════════════════════════════════════════════╣
║ Pace                                                            ║
║ Avg Time per Piece: 31.7 minutes                                ║
║ Est. Remaining: ~2h 15min                                       ║
╚═════════════════════════════════════════════════════════════════╝
```

**What to Watch:**
- **Now running:** Exactly one piece at a time — that's by design, not a stall
- **Failed:** Should be 0 (errors auto-retry once)
- **Avg Quality Score:** Should be ≥8.5 (if dropping, check brand profiles)
- **Est. Remaining:** Recalculated from the running average as pieces complete

### Error Handling in Batch

**Auto-Retry Errors:**
- API rate limit → waits 60s, retries
- Network timeout → retries immediately
- Source URL unavailable → tries alternate sources

**Human Escalation:**
- Brand profile not found → marks as `failed`, continues with remaining
- Validation errors (missing fields) → marks as `failed`, saves to `failed-requirements.csv`
- Score still 5.0-6.9 after the loop limits are exhausted → marks as `review_required`, never `completed`
- Score <5.0 → marks as `review_required` and escalates to a human

**What Happens to Failed/Review-Required:**
- Batch continues with remaining pieces (doesn't halt entire batch)
- Tracking row status updated to `failed` or `review_required`
- Summary report at end lists all issues

### Batch Completion Report

After batch finishes:
```
═══════════════════════════════════════════════════════════════
✅ BATCH PROCESSING COMPLETE
═══════════════════════════════════════════════════════════════
Batch ID: Batch_2026-07-17_14-30
Total Pieces: 12
Completed Successfully: 10 (83%)
Review Required: 2 (17%)
Failed: 0 (0%)

Average Quality Score: 8.9 / 10
Total Processing Time: 6h 22min (sequential, 12 pieces)

═══════════════════════════════════════════════════════════════
Completed Pieces (Quality Score ≥7.0 — approved):
═══════════════════════════════════════════════════════════════
✓ REQ-001 | Whitepaper AI in Healthcare       | Score: 9.1 | 58min
✓ REQ-002 | Article Remote Team Management    | Score: 8.8 | 39min
✓ REQ-003 | Article SEO Best Practices        | Score: 9.0 | 42min
... (10 total)

═══════════════════════════════════════════════════════════════
Review Required (5.0-6.9 after loop limits, or <5.0 escalation):
═══════════════════════════════════════════════════════════════
⚠ REQ-011 | Article AI Ethics in Marketing    | Score: 6.2
   Reason: Phase 4 flagged 3 unsourced claims, exceeded loop limit
   Action: Review citations, add sources, rerun Phase 4-7

⚠ REQ-012 | Whitepaper Future of Advertising  | Score: 4.5
   Reason: Below the 5.0 human-review threshold (Citation Integrity: 3.2/10)
   Action: Verify all citations, fix broken URLs, rerun Phase 7

═══════════════════════════════════════════════════════════════
Output Locations:
═══════════════════════════════════════════════════════════════
Batch folder: ContentForge/Batch_2026-07-17_14-30/
  ├── Completed/
  │   ├── REQ-001_Whitepaper-AI-in-Healthcare_v1.0.docx
  │   ├── REQ-002_Article-Remote-Team-Management_v1.0.docx
  │   └── ... (10 files)
  └── Review/
      ├── REQ-011_Article-AI-Ethics-in-Marketing_v1.0.docx
      └── REQ-012_Whitepaper-Future-of-Advertising_v1.0.docx

Next Steps:
  → Spot-check 2-3 completed pieces for quality verification
  → Review and fix the 2 pieces flagged for human review
  → Deliver completed pieces to clients or publish to CMS
  → Confirm the tracking rows show final status and links
═══════════════════════════════════════════════════════════════
```

---

## Content Refresh

### When to Refresh vs. Create New

**Refresh (Update Existing) When:**
- Content is 6-24 months old
- Core thesis is still valid
- Content has backlinks or SEO equity
- Topic is evergreen with updated stats available
- Original scored ≥7.0/10

**Create New (Don't Refresh) When:**
- Content is 24+ months old
- Core thesis outdated (industry changed)
- Topic is no longer relevant
- Original scored <5.0/10
- Starting from scratch is faster

### Refresh Scopes Explained

#### Light Refresh (20% rewrite, 8-12 min)
**What Changes:**
- Update statistics to current year (2024 → 2026)
- Replace 1-2 outdated examples
- Fix broken citation links
- Refresh intro sentence

**What Stays:**
- All structure (H2/H3 headings)
- 80% of original paragraphs
- Target keywords unchanged

**Use Case:** Content is 6-12 months old, mostly accurate, just needs stats updated

**Example:**
```
Original (2025):
  "In 2024, 62% of hospitals used AI for diagnostics..."

Refreshed (2026):
  "In 2025, 68% of hospitals used AI for diagnostics..."
```

#### Medium Refresh (50% rewrite, 15-20 min)
**What Changes:**
- Rewrite intro and conclusion completely
- Update 40-60% of body paragraphs
- Add 3-5 new sections for emerging trends
- Replace 50% of citations with current sources

**What Stays:**
- Article structure (same H2 sections, order may change)
- Evergreen definitions, frameworks, principles
- Target keywords (may add 2-3 new secondary keywords)

**Use Case:** Content is 12-24 months old, core is valid but needs significant updates

**Example:**
```
Original H2 Sections (2025):
  1. Introduction
  2. AI in Diagnostics
  3. AI in Treatment Planning
  4. Challenges and Limitations
  5. Conclusion

Refreshed H2 Sections (2026):
  1. Introduction (NEW)
  2. AI in Diagnostics (UPDATED)
  3. AI in Treatment Planning (UPDATED)
  4. AI in Patient Monitoring (NEW)
  5. Regulatory Landscape 2026 (NEW)
  6. Challenges and Limitations (UPDATED)
  7. Conclusion (NEW)
```

#### Heavy Refresh (80% rewrite, 22-30 min)
**What Changes:**
- Complete rewrite using original as outline only
- New research from scratch (Phase 1 full run)
- Update target keywords based on current search intent
- Add 5-10 new sections
- Replace 80% of citations

**What Stays:**
- Core topic and brand voice
- 1-2 evergreen sections (definitions, historical context)
- SEO URL slug (to preserve backlinks)

**Use Case:** Content is 24+ months old, industry has changed significantly, needs near-complete overhaul

**Example:**
```
Original (2024): "AI in Healthcare: 2024 Predictions"
  → Title, stats, examples all outdated

Heavy Refresh → "AI in Healthcare: 2026 Reality and 2028 Outlook"
  → New title, all new sections, 80% new content
  → Preserves URL: /blog/ai-healthcare-predictions (backlinks maintained)
```

### SEO Preservation Strategy

**Critical:** Content refresh must NOT hurt your SEO rankings.

**How ContentForge Preserves SEO:**

1. **Keyword Density Maintained:**
   - Original: 2.3% for "AI in healthcare"
   - Target for refresh: 2.0-2.6% (±0.3%)
   - Phase 6 monitors and adjusts rewritten sections

2. **URL Slug Preserved:**
   - Original: `/blog/ai-in-healthcare-2025-trends`
   - Refreshed: `/blog/ai-in-healthcare-2025-trends` (**SAME URL**)
   - Title updates to "2026 Trends" but URL stays (maintains backlinks)

3. **Internal Links Preserved:**
   - All internal links from original content are preserved
   - New internal links added to related updated content
   - Never break existing internal link structure

4. **Meta Description Updated (Not Replaced):**
   - Original: "Explore AI in healthcare trends for 2025..."
   - Refreshed: "Explore AI in healthcare trends for 2026..." (year updated)

### Version Control

**Original File:** `AI-in-Healthcare-2025-Trends_v1.0.docx` (never modified)
**1st Refresh:** `AI-in-Healthcare-2025-Trends_v1.1.docx` (new version)
**2nd Refresh:** `AI-in-Healthcare-2025-Trends_v1.2.docx`
**Heavy Refresh:** `AI-in-Healthcare-2025-Trends_v2.0.docx`

**Why Version Control Matters:**
- Rollback if refresh hurts SEO
- A/B test original vs. refreshed
- Track improvement over time

---

## Troubleshooting

### Issue 1: "Brand profile not found"

**Error Message:**
```
❌ Error: Brand profile 'AcmeCorp' not found
Action: Run /contentforge:brand-setup AcmeCorp first
```

**Cause:** You haven't created a brand profile yet.

**Solution:**
1. Run `/contentforge:brand-setup AcmeCorp`
2. Fill in brand details (voice, tone, terminology)
3. Retry content generation

---

### Issue 2: "Quality score <5.0, flagged for review"

**Error Message:**
```
⚠️ Quality Score: 4.8/10 (below threshold)
Dimension Breakdown:
  Content Quality: 7.5/10
  Citation Integrity: 3.2/10 ← FAILING
  Brand Compliance: 8.0/10
  SEO Performance: 7.0/10
  Readability: 7.5/10

Reason: 6/15 citations are broken (404 errors)
Action: Review citations, fix broken URLs, rerun
```

**Cause:** Content didn't meet quality threshold (likely citation issues).

**Solution:**
1. Check dimension breakdown (identify failing dimension)
2. If Citation Integrity <5.0:
   - Phase 2 found broken links
   - Manually verify sources are still live
   - Consider using more authoritative sources (peer-reviewed journals, not blogs)
3. Regenerate with better sources:
   ```
   /contentforge:create-content "AI in Healthcare 2026" --type=article --brand=AcmeCorp
   ```
   Provide hint: "Use peer-reviewed sources from Nature, NEJM, JAMA"

---

### Issue 3: "Max loops exceeded (5 iterations)"

**Error Message:**
```
❌ Max loops exceeded: 5 iterations
Pipeline stuck in feedback loop between Phase 4 and Phase 3

Loop History:
  Loop 1: Phase 4 → Phase 3 (hallucination: "95% of doctors use AI")
  Loop 2: Phase 4 → Phase 3 (hallucination: "AI reduces costs by 80%")
  Loop 3: Phase 7 → Phase 3 (citation integrity: 4.5/10)
  Loop 4: Phase 4 → Phase 3 (unsourced claim: "FDA approved 12 AI tools")
  Loop 5: Phase 7 → Phase 6 (SEO degraded readability)

Action: Human review required. Issue likely: vague topic or restrictive sources.
```

**Cause:** Pipeline can't meet quality gates after 5 attempts (usually vague topic or limited sources).

**Solution:**
1. **Make topic more specific:**
   - Instead of: "AI in Healthcare"
   - Try: "AI-Powered Diagnostics for Cardiovascular Disease"

2. **Check if sources are paywalled:**
   - If topic requires medical journals behind paywalls, ContentForge can't access them
   - Provide publicly accessible sources in your brief

3. **Relax brand guardrails temporarily:**
   - If brand profile has very restrictive guardrails, loosen them
   - `/contentforge:brand-setup AcmeCorp` → Edit guardrails

4. **Try different content type:**
   - If article is stuck, try blog (shorter, less citations needed)

---

### Issue 4: "MCP server connection failed"

**Error Message:**
```
❌ MCP Error: google-drive server not responding
Check MCP configuration in Cowork settings
```

**Cause:** the Google Drive integration isn't connected, or its authorization expired.

**Solution:**
1. **Check the integration in Cowork:**
   - Profile → Settings → Integrations
   - Verify **Google Drive** shows as connected; reconnect if it doesn't

2. **Re-run the setup skill:**
   - `/contentforge:cf-cowork-setup` re-verifies the Drive MCP and folder layout
   - `/contentforge:cf-integrations` lists what's currently connected

3. **Check any path you configured by hand:**
   - Use a fully-expanded absolute path — `~` is not expanded by every MCP host
   - Good: `/Users/you/ContentForge/output`
   - Risky: `~/ContentForge/output`

4. **Test Connection:**
   - In Cowork: "List files in my Google Drive folder 'ContentForge Output'"
   - If this works, the integration is live

5. **Restart Cowork:**
   - Log out and log back in
   - Integrations reload on session start

**Remember:** Drive is optional. If it stays broken, ContentForge falls back to local tracking and still produces the .docx.

---

### Issue 5: "Processing time well over the expected range"

**Error Message:**
```
⚠️ Warning: Processing time 78 minutes (article range: 35-45 min)
Phase 3 (Content Drafter) took 18 minutes (expected 5-7 min)
```

**Cause:** API rate limits, network issues, or unusually complex content.

**Solution:**
1. **Check integration quotas (if you use Drive/Sheets):**
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)
   - Check Drive API and Sheets API quotas
   - If near limit, wait or increase quota

2. **Retry Later:**
   - ContentForge auto-retries with backoff
   - If network issue, wait 10-15 min and retry

3. **Simplify Content:**
   - Reduce word count target (2000 → 1500)
   - Choose simpler content type (article → blog)

---

## FAQ

### General

**Q: How long does it take to set up ContentForge?**
**A:** 5-10 minutes total:
- Installation from the Plugins panel: 2 min
- First brand profile: 3-5 min
- Integrations: 0 min — none are required; add Drive later if your team needs shared persistence

**Q: Can I use ContentForge for free?**
**A:** Yes! ContentForge is free and open-source (MIT License). You only pay for:
- Your Claude Cowork subscription (if not already subscribed)
- Google Cloud API usage — only if you opt into the Drive/Sheets backend (free tier covers ~100 pieces/month)

**Q: How many brands can I manage?**
**A:** Unlimited. Agencies manage 50-200 brands. Each brand is a separate profile.

---

### Content Quality

**Q: How accurate are the citations?**
**A:** 95%+ accuracy. Three-layer verification (Phases 2, 4, 7) catches:
- Broken links (404 errors)
- Misattributed quotes
- Outdated statistics
- Fabricated sources

**Q: What about hallucinations?**
**A:** ContentForge applies three-layer fact verification (Phases 2, 4, 7). Production runs typically achieve high factual accuracy — verify every claim before publishing. Phase 4 (Scientific Validator) scans for:
- Fabricated statistics ("95% of doctors...")
- Made-up studies ("Harvard 2025 study found...")
- Unsourced claims

If detected, loops back to Phase 3 for rewrite.

**Q: Can I trust the quality scores?**
**A:** Treat them as a structured, repeatable review — the score tells you which of the 5 dimensions is weakest and whether the piece cleared the ≥7.0 approval gate. It is not a prediction of how the piece will rank; nothing in ContentForge measures search performance.

**Q: What if I disagree with the quality score?**
**A:** Review the dimension breakdown. If you think Citation Integrity should be higher:
1. Check the specific citations flagged
2. Verify sources are authoritative (peer-reviewed > blog)
3. If you disagree, use the content anyway (scores are guidance, not law)

---

### Batch Processing

**Q: Can I process more than 50 pieces at once?**
**A:** Yes, but split into batches of 20-30 so each run is easier to supervise. The queue is sequential, so plan on roughly (pieces × per-piece time) of wall-clock runtime — 100 blog posts is on the order of 50-60 hours across several sessions.

**Q: What happens if one piece fails in a batch?**
**A:** Batch continues with remaining pieces. The failed piece is marked `failed` or `review_required` in the tracking rows. Batch doesn't halt.

**Q: Can I cancel a batch mid-process?**
**A:** There's no cancel command, but closing the session stops the run — the batch does **not** continue in the background. Nothing already finished is lost: each completed piece is checkpointed, so `/contentforge:resume` picks the queue back up where it stopped.

---

### MCP & Integrations

**Q: Do I need to pay for Google Cloud?**
**A:** Free tier covers ~100 pieces/month. If you exceed:
- Drive API: $0.004 per 1,000 requests (very cheap)
- Sheets API: $0.004 per 1,000 requests

**Q: Can I use Dropbox instead of Google Drive?**
**A:** Google Drive is the only file-storage integration with a dedicated MCP path. But you don't need one: set `CONTENTFORGE_PUBLISH_DIR` to a folder your Dropbox (or OneDrive, or any sync client) already watches, and finished files land there via normal local output.

**Q: Can I publish to WordPress automatically?**
**A:** Yes, once a WordPress connector is available in your environment:
1. Add it with `/contentforge:cf-connect wordpress` (or Cowork Settings → Integrations)
2. Provide your WordPress site URL, username, and application password
3. Use `/contentforge:publish article.docx --platform=wordpress`

---

### Pricing & Limits

**Q: Is there a limit to how much content I can generate?**
**A:** Only limited by:
- Google Cloud API quotas (free tier: ~100 pieces/month)
- Claude Cowork usage (depends on your plan)

**Q: Does batch processing cost more?**
**A:** No. Batch processing runs the same pipeline, the same number of times — it just does the queueing for you.

---

### Support

**Q: Where can I get help?**
**A:** Three options:
1. **This guide** — Covers 95% of use cases
2. **GitHub Issues:** [github.com/indranilbanerjee/contentforge/issues](https://github.com/indranilbanerjee/contentforge/issues)
3. **Email:** indranilbanerjee21@gmail.com

**Q: Can I request new features?**
**A:** Yes! Open a feature request on [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues).

**Q: Is there a community or forum?**
**A:** Use GitHub Issues at [github.com/indranilbanerjee/contentforge/issues](https://github.com/indranilbanerjee/contentforge/issues).

---

## 🚀 You're Ready!

**Congratulations!** You now know how to use ContentForge in Cowork like a pro.

### Quick Start Checklist

✅ Installed ContentForge plugin from the Plugins panel
✅ (Optional) Connected Google Drive for team persistence
✅ Created first brand profile
✅ Generated first content piece
✅ (Optional) Set up batch processing
✅ (Optional) Configured WordPress/Notion for publishing

### Recommended First Week

**Day 1:** Generate 3-5 single pieces, get comfortable with the pipeline
**Day 2:** Try batch processing with 5-10 pieces
**Day 3:** Experiment with content refresh on old content
**Day 4:** Set up analytics tracking (`/contentforge:cf-analytics`)
**Day 5:** Configure CMS publishing (WordPress/Notion)

**By Week 2:** You'll be queueing work up front and spending your own time on review and delivery instead of drafting.

---

**Questions?** Email: indranilbanerjee21@gmail.com
**Issues?** GitHub: [github.com/indranilbanerjee/contentforge/issues](https://github.com/indranilbanerjee/contentforge/issues)
**Updates?** Watch the repo for the latest features!

---

**Version:** 3.16.1
**Last Updated:** 2026-07-29
**Author:** Indranil 'Neel' Banerjee
**License:** MIT
