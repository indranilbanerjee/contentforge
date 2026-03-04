# ContentForge Testing Guide — v3.4.0

Complete testing guide for the ContentForge enterprise content production plugin.

---

## Table of Contents

1. [Test Environment Setup](#1-test-environment-setup)
2. [Installation Tests](#2-installation-tests)
3. [Pipeline Tests](#3-pipeline-tests)
4. [Command Tests](#4-command-tests)
5. [Skill Tests](#5-skill-tests)
6. [Script Tests](#6-script-tests)
7. [Config & Industry Knowledge Pack Tests](#7-config--industry-knowledge-pack-tests)
8. [Hook Tests](#8-hook-tests)
9. [MCP Connector Tests](#9-mcp-connector-tests)
10. [Google Integration Tests](#10-google-integration-tests)
11. [Edge Cases & Error Scenarios](#11-edge-cases--error-scenarios)
12. [Regression Checklist](#12-regression-checklist)
13. [Test Priority Order](#13-test-priority-order)

---

## 1. Test Environment Setup

### Prerequisites

- **Claude Cowork** or **Claude Code** with plugin support
- Google service account credentials (optional, for Google Sheets/Drive tests)
- At least one brand profile set up (or plan to set up during testing)

### Installation Sources

| Method | URL |
|--------|-----|
| **Marketplace** | `https://github.com/indranilbanerjee/neels-plugins.git` |
| **Direct URL** | `https://github.com/indranilbanerjee/contentforge.git` |

### Pre-Test Cleanup

```
# Clear plugin cache (if reinstalling)
rm -rf ~/.claude/plugins/cache/

# Clear ContentForge brand data (for fresh brand setup test)
# WARNING: Only do this if you want to start fresh
rm -rf ~/.claude-marketing/
```

### Test Brands to Use

| Brand Name | Industry | Purpose |
|-----------|----------|---------|
| "TestBrand Alpha" | technology | Primary test brand |
| "HealthFirst Clinic" | healthcare | Regulated industry test |
| "GlobalFinance Corp" | bfsi | Financial compliance test |
| "QuickShop" | ecommerce | Simple B2C test |

---

## 2. Installation Tests

### 2.1 Marketplace Installation

**Steps:**
1. In Claude Cowork, go to Settings > Plugins > Add Marketplace
2. Enter URL: `https://github.com/indranilbanerjee/neels-plugins.git`
3. Install `contentforge`

**Expected Results:**
- [ ] Marketplace loads without errors
- [ ] ContentForge listed with version 3.4.0
- [ ] Description mentions "13 agents, 18 skills, 10 industry knowledge packs"
- [ ] Installation completes without rollback
- [ ] No "Host key verification failed" error (uses HTTPS, not SSH)

**If installation fails:**
- Check `~/.claude/logs/main.log` for `VMCLIRunner` errors
- Look for `virtiofs mount: Plan9 mount failed` (VM instability — retry)
- Look for `EXDEV` errors (known bug #25444)
- Clear `~/.claude/plugins/cache/` and retry

### 2.2 Direct URL Installation

**Steps:**
1. Settings > Plugins > Add Plugin
2. Enter URL: `https://github.com/indranilbanerjee/contentforge.git`

**Expected:** Same results as marketplace installation

### 2.3 Session Start Verification

**Test:** Start a new session after installation

**Expected Results:**
- [ ] SessionStart hook fires — setup.py runs without errors
- [ ] Version banner displays:
  ```
  ✓ ContentForge v3.4 loaded — Enterprise content production with zero hallucinations
    /contentforge — Single piece (20-30 min)
    /batch-process — Multiple pieces in parallel (4-5x faster)
    /content-refresh — Update old content with fresh data
    /cf:integrations — See connected integrations
    /cf:social-adapt — Repurpose content for social
    /cf:publish — Push to CMS
  ```
- [ ] 7 commands visible in Customize panel (create-content, content-brief, social-adapt, publish, translate, brand-setup, audit-content)
- [ ] 18 skills visible in Skills section
- [ ] 13 agents registered (check for no frontmatter errors in logs)

### 2.4 Plugin Structure Verification

**Test:** Verify all expected files are present after installation

**Expected file counts:**
- [ ] `agents/` — 13 files (01 through 11 + 03.5 + 06.5)
- [ ] `commands/` — 7 files
- [ ] `skills/` — 18 skill directories, each with SKILL.md
- [ ] `scripts/` — 4 files (setup.py, connector-status.py, sheets-tracker.py, drive-uploader.py)
- [ ] `config/` — 7 config files + `industries/` subdirectory with 10 JSON packs
- [ ] `templates/` — 10 template files
- [ ] `utilities/` — 6 utility files
- [ ] `.mcp.json` — 7 HTTP connectors
- [ ] `hooks/hooks.json` — 2 hook events (SessionStart, PreToolUse)

---

## 3. Pipeline Tests

The 10-phase pipeline is the core product. Test with different content types and industries.

### 3.1 Full Pipeline — Blog Post (Technology)

**Prompt:** `/contentforge Write a blog post about "How AI Agents Are Transforming Content Marketing in 2026" for a technology brand`

**Expected Results — Phase by Phase:**

| Phase | What to Verify |
|-------|---------------|
| **Phase 1: Research** | Finds 5+ live sources, competitor analysis, differentiation angle. Research brief output visible. |
| **Phase 2: Fact Check** | Verifies claims, checks URLs, flags unverified stats. 80%+ verification rate. Statistics Verification Report produced. |
| **Phase 3: Content Draft** | Loads technology knowledge pack (Step 0.3 SME Calibration). Uses correct terminology depth. Visual placeholders inserted. Draft Metadata includes SME Calibration Summary. |
| **Phase 3.5: Visual Asset Annotator** | Generates charts from Phase 2 data. Creates `<!-- VISUAL: ... -->` markers. Asset manifest written. Visual density 2-4 per 1000 words for blog. |
| **Phase 4: Scientific Validator** | Validates chart data accuracy. Domain-specific validation (Step 5) checks technology terminology. Zero hallucinations. |
| **Phase 5: Structurer** | Optimizes structure, fixes grammar. Preserves visual markers. |
| **Phase 6: SEO/GEO** | Keyword optimization. Produces `<!-- INTERNAL-LINK: ... -->` markers (if site structure provided). SEO scorecard output. |
| **Phase 6.5: Humanizer** | Removes AI telltale phrases. Adds natural voice. Preserves visual + link markers. |
| **Phase 7: Reviewer** | Scores all dimensions including Visual Asset Quality (1.6) and Internal Linking (4.6). Overall score 7+. |
| **Phase 8: Output** | .docx generated. Charts embedded. TODO boxes for human-needed visuals. Internal links as clickable hyperlinks. Completion summary shows visual asset and internal link counts. |

**v3.4.0 Feature Checks:**
- [ ] SME Calibration Summary appears in Draft Metadata (Phase 3)
- [ ] Technology knowledge pack loaded (verify terminology like "AI vs ML vs deep learning" distinction)
- [ ] Domain-Specific Validation report section appears in Phase 4 output
- [ ] Visual placeholders marked by Phase 3, annotated by Phase 3.5
- [ ] Phase 4 validates chart data against Phase 2 verified statistics
- [ ] Final output has charts embedded (if data available) or TODO boxes
- [ ] Internal link markers present (or generic recommendations if no site structure)

### 3.2 Full Pipeline — Whitepaper (Pharma)

**Prompt:** `/contentforge Write a whitepaper about "The Role of AI in Drug Discovery: From Target Identification to Clinical Trials" for a pharma company`

**Why this test matters:** Pharma is a heavily regulated industry with strict evidence standards.

**Specific Checks:**
- [ ] SME Calibration loads pharma knowledge pack
- [ ] Expertise stance: "Clinical researcher or pharmaceutical scientist"
- [ ] Uses FDA/EMA terminology correctly
- [ ] Evidence hierarchy: Clinical trials ranked above observational studies
- [ ] Required disclaimers present (investigational compound, not medical advice)
- [ ] Domain validation catches prohibited claims ("cure", "miracle", "100% effective")
- [ ] Visual density 3-5 per 1000 words (whitepaper target)
- [ ] Quality Gate 4 includes regulatory compliance check
- [ ] Word count 3000-6000 (whitepaper range)

### 3.3 Full Pipeline — Article (BFSI)

**Prompt:** `/contentforge Write an article about "Open Banking APIs: How Financial Institutions Can Monetize Data Safely" for a banking audience`

**Specific Checks:**
- [ ] BFSI knowledge pack loaded
- [ ] Regulatory awareness: GDPR, PCI DSS, SOX mentioned correctly
- [ ] Financial terminology used precisely (APR vs interest rate, etc.)
- [ ] Required disclaimers (not financial advice, regulatory specifics by jurisdiction)
- [ ] Common pitfalls avoided (no "guaranteed returns", no "risk-free")
- [ ] Evidence standards: regulatory filings and official reports cited

### 3.4 Full Pipeline — FAQ (Healthcare)

**Prompt:** `/contentforge Write an FAQ about "Understanding Telehealth: Patient Questions Answered" for a healthcare provider`

**Specific Checks:**
- [ ] Healthcare knowledge pack loaded
- [ ] HIPAA awareness in content
- [ ] Medical terminology appropriate for patient audience (simpler language)
- [ ] Disclaimers present (not a substitute for professional medical advice)
- [ ] Visual density 0-1 per 1000 words (FAQ target — minimal visuals)

### 3.5 Full Pipeline — Research Paper (Education)

**Prompt:** `/contentforge Write a research paper about "The Impact of AI Tutoring Systems on Student Learning Outcomes" for education researchers`

**Specific Checks:**
- [ ] Education knowledge pack loaded
- [ ] Academic structure: methodology, findings, discussion
- [ ] Evidence standards: peer-reviewed educational research cited
- [ ] FERPA awareness
- [ ] Citation density meets research paper requirements

### 3.6 Pipeline with No Brand Profile

**Prompt:** `/contentforge Write a blog post about "Remote Work Productivity Tips"`

**Without setting up a brand first.**

**Expected:** Pipeline should still work with generic defaults. No crash. Should offer to set up a brand profile.

### 3.7 Pipeline Feedback Loops

**Test:** Trigger a quality gate failure to see if the feedback loop works.

**How:** Request content with an intentionally complex or niche topic that might fail fact-checking. Observe whether Phase 4 → Phase 3.5 feedback loop triggers (max 1 iteration per `scoring-thresholds.json`).

**Expected:**
- [ ] Quality gate failure detected
- [ ] Feedback sent to earlier phase
- [ ] Re-run produces improved output
- [ ] Max loop limit respected (5 total loops, 1 for phase 4→3.5)

---

## 4. Command Tests

Test all 7 commands visible in the Customize panel.

### 4.1 `/brand-setup`

**Prompt:** "Set up brand profile for TestBrand Alpha — a B2B SaaS company that makes project management software"

**Step-by-Step Verification:**

| Step | Test | Expected |
|------|------|----------|
| **A: Brand Identity** | Provide brand name, URL, industry | Brand name stored, industry mapped to knowledge pack |
| **B: Voice & Tone** | Provide voice description or sample content | Voice profile created with tone dimensions |
| **C: Terminology** | Provide approved/banned terms | Terminology rules stored in brand profile |
| **D: Compliance** | Provide compliance rules | Guardrails configured |
| **E: Reference Content** | Provide sample URLs or documents | Reference content analyzed |
| **F: Key File Generation** | Let it auto-generate key files | brand-profile.json, guardrails.json, reference-content.md created |

**v3.4.0 Step F Checks:**
- [ ] Step F presented as an option (generate new or update existing)
- [ ] Key files generated from website analysis + user input
- [ ] Files saved to `~/.claude-marketing/{brand}/`
- [ ] Drive upload attempted (with graceful fallback if no credentials)
- [ ] brand-profile.json has correct industry field matching knowledge pack filename

### 4.2 `/create-content`

**Prompt:** `/create-content "5 B2B SaaS Pricing Strategies That Actually Work" blog`

**Expected:** Triggers full 10-phase pipeline. Same verification as Pipeline Tests above.

### 4.3 `/content-brief`

**Prompt:** `/content-brief "kubernetes security best practices"`

**Expected:**
- [ ] Keyword research with search volume data
- [ ] Competitor analysis (top 5 ranking pages)
- [ ] Search intent classification
- [ ] Audience insights
- [ ] Recommended outline
- [ ] SEO strategy

### 4.4 `/social-adapt`

**Requires:** An existing piece of content (run `/create-content` first)

**Prompt:** `/social-adapt [previous article] for linkedin and twitter`

**Expected:**
- [ ] LinkedIn version: professional tone, longer format, hashtags
- [ ] Twitter/X version: punchy, within character limit, thread if needed
- [ ] Each platform follows `social-platform-specs.json` rules
- [ ] Brand voice maintained across platforms

### 4.5 `/publish`

**Requires:** Webflow or WordPress MCP connector configured

**Prompt:** `/publish [previous content] --platform=webflow --status=draft`

**Expected:**
- [ ] Preview shown before publishing
- [ ] HTML export fallback if MCP not connected
- [ ] Draft status respected (not published live)

### 4.6 `/translate`

**Prompt:** `/translate [previous content] --language=es --level=adapted`

**Expected:**
- [ ] Spanish translation with brand voice preservation
- [ ] Citations maintained in original language with translations
- [ ] SEO elements translated (meta title, description)
- [ ] "Adapted" level: cultural nuances adjusted, not literal word-for-word

### 4.7 `/audit-content`

**Prompt:** `/audit-content [provide a Drive folder URL or WordPress URL]`

**Expected:**
- [ ] Content library scanned
- [ ] Freshness decay identified (outdated statistics, stale references)
- [ ] Coverage gaps flagged
- [ ] Optimization opportunities listed

---

## 5. Skill Tests

Test each of the 18 skills individually.

### Core Pipeline Skills

| # | Skill | Test Prompt | Key Checks |
|---|-------|-------------|------------|
| 1 | `/contentforge` | "Write article about cloud migration" | Full 10-phase pipeline triggers |
| 2 | `/batch-process` | "Create 3 blog posts about: AI agents, no-code tools, API security" | Parallel processing, queue management, progress tracking |
| 3 | `/content-refresh` | "Update [old article] with current data" | Identifies outdated stats, refreshes sources, preserves structure |

### Integration Skills

| # | Skill | Test Prompt | Key Checks |
|---|-------|-------------|------------|
| 4 | `/cf:integrations` | (no argument) | Shows 7 HTTP connectors, grouped by category, connected vs available |
| 5 | `/cf:connect` | `/cf:connect notion` | Step-by-step Notion setup instructions |
| 6 | `/cf:add-integration` | `/cf:add-integration "I want to connect Airtable"` | Custom connector setup guide, no crash |
| 7 | `/cf:publish` | `/cf:publish [content] to webflow` | CMS publishing with preview |

### Content Enhancement Skills

| # | Skill | Test Prompt | Key Checks |
|---|-------|-------------|------------|
| 8 | `/cf:social-adapt` | "Adapt this article for LinkedIn and Instagram" | Platform-specific adaptations per social-platform-specs.json |
| 9 | `/cf:translate` | "Translate to French with cultural adaptation" | Preserves voice, citations, SEO |
| 10 | `/cf:variants` | "Generate A/B variants for this headline" | Scored variations with rationale |
| 11 | `/cf:video-script` | "Create a YouTube script from this article" | Timestamps, B-roll, hooks |

### Planning & Analysis Skills

| # | Skill | Test Prompt | Key Checks |
|---|-------|-------------|------------|
| 12 | `/cf:brief` | "Create brief for 'DevOps automation trends'" | Keyword data, competitor analysis, outline |
| 13 | `/cf:calendar` | "Plan content calendar for Q2 2026" | Schedule, deadlines, team assignments |
| 14 | `/cf:audit` | "Audit our blog for content decay" | Freshness analysis, gap identification |
| 15 | `/cf:analytics` | "Show content quality trends" | Score trends, pipeline timing, insights |

### Brand & Config Skills

| # | Skill | Test Prompt | Key Checks |
|---|-------|-------------|------------|
| 16 | `/cf:style-guide` | "Import style guide from [URL]" | Extracts voice, terminology, guardrails |
| 17 | `/cf:template` | "Create a case study template" | Custom content type beyond built-in 5 |
| 18 | `/cf:help` | (no argument) | Shows v3.4.0, 13 agents, 18 skills, 7 connectors, 10-phase pipeline |

**`/cf:help` Argument Tests:**

| Argument | Expected Output |
|----------|----------------|
| `--pipeline` | 10-phase pipeline with timing and quality gates |
| `--skills` | All 18 skills listed with descriptions |
| `--brand` | Brand profile setup methods |
| `--examples` | Example workflows from brief to publish |
| `--troubleshoot` | Common issues and solutions |
| `--connectors` | Connector status (shortcut for /cf:integrations) |

---

## 6. Script Tests

### 6.1 setup.py

**Trigger:** Runs automatically on session start (SessionStart hook)

**Expected output:**
- [ ] Plugin root path printed
- [ ] Scripts directory path printed
- [ ] .mcp.json validated (7 HTTP connectors)
- [ ] Google credentials check (present or not)
- [ ] pip package check (gspread, google-auth)

### 6.2 connector-status.py

**Trigger:** Via `/cf:integrations` skill

**Expected:**
- [ ] Lists all 7 HTTP connectors with status (Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar)
- [ ] Shows Google Sheets/Drive as "script" transport type
- [ ] Reports which connectors are configured vs available
- [ ] Platform-level integration notes for Google Drive/Docs

### 6.3 sheets-tracker.py (requires Google credentials)

**Test each operation:**

| Operation | Test | Expected |
|-----------|------|----------|
| `init` | Initialize tracking sheet | Creates sheet with correct 20-column headers |
| `add-row` | Add a content request | New row with auto-incremented requirement_id |
| `get-pending` | List pending content | Returns rows with pending status, sorted by priority |
| `get-row` | Get specific row | Returns correct row data |
| `update-row` | Update status | Row updated, no data loss |
| `mark-complete` | Complete a request | Status changed, completion date set |

**Edge cases:**
- [ ] requirement_id uses max existing ID (not row count) — handles deleted rows correctly
- [ ] Priority clamped to 1-5 range
- [ ] Crash-safe sort in get_pending()
- [ ] Auto-installs gspread + google-auth on first run in Cowork VM

### 6.4 drive-uploader.py (requires Google credentials)

**Test each operation:**

| Operation | Test | Expected |
|-----------|------|----------|
| `ensure-folders` | Create folder hierarchy | Brand/Type/Year/Month/ structure created |
| `upload` | Upload a .docx file | File uploaded to correct folder |
| `list` | List files in folder | Returns file list with metadata |
| `upload-assets` | Upload chart images | Assets uploaded to assets subfolder |

**Edge cases:**
- [ ] Brand names with apostrophes handled safely (client-side matching, no query injection)
- [ ] `~` path resolution works (expanduser)
- [ ] Folder creation is idempotent (doesn't create duplicates)

---

## 7. Config & Industry Knowledge Pack Tests

### 7.1 Validate All 10 Industry Knowledge Packs

For each pack, create a short blog post and verify SME Calibration + Domain Validation:

| Industry | File | Key Terminology to Check |
|----------|------|------------------------|
| technology | `technology.json` | AI vs ML distinction, latency vs throughput, open source definitions |
| pharma | `pharma.json` | Phase I/II/III trials, NDA/BLA, p-values, FDA/EMA protocols |
| bfsi | `bfsi.json` | APR vs interest rate, fiduciary duty, Basel III, KYC/AML |
| healthcare | `healthcare.json` | ICD codes, HIPAA, evidence-based vs experimental |
| real_estate | `real_estate.json` | Cap rate, NOI, fair housing, appraisal vs assessment |
| b2b_saas | `b2b_saas.json` | ARR vs MRR, churn rate, CAC:LTV, net revenue retention |
| legal | `legal.json` | Precedent, statute of limitations, jurisdiction, discovery |
| ecommerce | `ecommerce.json` | AOV, conversion rate, cart abandonment, fulfillment |
| consumer_goods | `consumer_goods.json` | FMCG, SKU rationalization, shelf life, brand equity |
| education | `education.json` | Pedagogy, assessment types, FERPA, accreditation |

**For each pack verify:**
- [ ] SME Calibration Summary references the correct knowledge pack
- [ ] Terminology depth matches the audience level
- [ ] Regulatory awareness matches the industry
- [ ] Evidence standards are applied correctly
- [ ] Domain-specific validation catches industry-specific pitfalls

### 7.2 Scoring Thresholds

Verify `config/scoring-thresholds.json`:
- [ ] `phase_3_5_visual_assets` quality gate present (require_data_chart_verification, min_visual_density, require_alt_text, require_captions)
- [ ] `phase_4_to_3_5` feedback loop limit = 1
- [ ] Regulated industries (pharma, bfsi, healthcare, legal) use stricter thresholds
- [ ] Higher minimum citation accuracy for regulated content
- [ ] Max 5 total feedback loops

### 7.3 Brand Registry Template

Verify `config/brand-registry-template.json`:
- [ ] `industry` field accepts all 10 knowledge pack names
- [ ] `seo_preferences.internal_linking` has `sitemap_url`, `page_registry`, `pillar_pages`
- [ ] `google_integration` section present (`credentials_path`, `tracking_sheet_id`, `drive_output_folder_id`)
- [ ] `output_preferences.brand_colors` available for chart styling

### 7.4 Other Config Files

| Config File | Test |
|-------------|------|
| `social-platform-specs.json` | Verify character limits match current platform specs |
| `multilingual-patterns.json` | Verify language codes and brand voice patterns |
| `content-type-defaults.json` | Verify word count ranges per content type |

---

## 8. Hook Tests

### 8.1 SessionStart Hook

**Test:** Start a new session

**Expected:**
- [ ] setup.py runs without errors
- [ ] Version banner shows "v3.4"
- [ ] All 6 skill shortcuts listed in banner
- [ ] No Python errors or tracebacks

### 8.2 PreToolUse — Hallucination Detection (Write/Edit)

**Test:** Generate content and watch for the hallucination check during Write/Edit operations

**Expected behavior:**
- [ ] Hook fires on Write/Edit of content deliverables
- [ ] Hook SKIPs for non-content files (plugin config, scripts, etc.)

**Test with intentionally bad content — the hook should catch all three:**

| Bad Content | Expected Detection |
|-------------|-------------------|
| "Studies show 87% of companies..." (no source) | CRITICAL — unattributed statistic |
| "Visit https://example.com/dashboard" | CRITICAL — placeholder URL |
| "The #1 leading solution in the market" | WARNING — unsubstantiated superlative |

**Additional checks:**
- [ ] Fix suggestions provided for each flag
- [ ] Severity levels correct (CRITICAL for stats/URLs in headlines, WARNING for body text)
- [ ] Doesn't over-flag — legitimate cited statistics pass through

---

## 9. MCP Connector Tests

### 9.1 ContentForge HTTP Connectors (7)

| # | Connector | URL | Test Action | Expected |
|---|-----------|-----|------------|----------|
| 1 | **Notion** | `mcp.notion.com/mcp` | Read a Notion page | Content retrieved via MCP |
| 2 | **Canva** | `mcp.canva.com/mcp` | Generate a design | Design created or template listed |
| 3 | **Figma** | `mcp.figma.com/mcp` | Access design file | Design data retrieved |
| 4 | **Webflow** | `mcp.webflow.com/sse` | Publish draft content | Content appears in Webflow CMS |
| 5 | **Slack** | `mcp.slack.com/mcp` | Send notification | Message delivered to channel |
| 6 | **Gmail** | `gmail.mcp.claude.com/mcp` | Draft email | Email draft created |
| 7 | **Google Calendar** | `gcal.mcp.claude.com/mcp` | Create content calendar event | Calendar event created |

**Note:** Each connector requires OAuth authorization on first use. The Claude platform handles this — you'll see an authorization prompt. Not all testers will have accounts for all services.

### 9.2 Connector Categories

Verify connectors map to the right workflow categories per CONNECTORS.md:

| Category | Connector | Workflow Impact |
|----------|-----------|----------------|
| Knowledge base | Notion | Core requirement storage |
| Design | Canva, Figma | Featured images, social graphics |
| CMS | Webflow | Publishing destination (`/cf:publish`) |
| Chat | Slack | Batch status notifications |
| Email | Gmail | Draft delivery, review notifications |
| Calendar | Google Calendar | Content calendar events (`/cf:calendar`) |

### 9.3 Graceful Degradation

**Test:** Invoke a skill that uses a connector that's NOT authorized/connected

**Expected:**
- [ ] Skill doesn't crash
- [ ] Clear message about which connector is needed
- [ ] Instructions on how to connect it (or suggestion to run `/cf:connect <name>`)
- [ ] Fallback behavior (manual data input or skip)

### 9.4 Platform-Level Integrations

**Test:** Verify Google Drive/Docs work through Claude platform integration (Settings > Integrations)

**Expected:**
- [ ] Google Drive documents accessible for brand knowledge
- [ ] `/cf:integrations` notes that platform-level integrations exist separately
- [ ] connector-status.py can't detect platform integrations (expected — mentions this)

---

## 10. Google Integration Tests

**Prerequisites:** Google service account with Sheets API + Drive API enabled

### 10.1 Initial Setup

1. Create service account in Google Cloud Console
2. Download JSON credentials
3. Place at `~/.claude-marketing/google-credentials.json`
4. Create a Google Sheet and share with service account email
5. Create a Google Drive folder and share with service account email
6. Configure brand profile with `tracking_sheet_id` and `drive_output_folder_id`

### 10.2 Sheets Tracking (End-to-End)

**Test:** Run a full content pipeline and verify tracking

- [ ] Content request added to sheet on pipeline start (`add-row`)
- [ ] Status updates as pipeline progresses (`update-row`)
- [ ] Completion marked when finished (`mark-complete`)
- [ ] requirement_id auto-increments correctly
- [ ] Multiple rows don't collide on IDs after deletions

### 10.3 Drive Delivery (End-to-End)

**Test:** Complete a content piece and verify Drive upload

- [ ] Folder hierarchy created: `Brand/Blog/2026/03/`
- [ ] .docx file uploaded to correct folder
- [ ] Chart assets uploaded to assets subfolder
- [ ] File metadata correct (name, MIME type)

### 10.4 Without Google Credentials

**Test:** Run the full pipeline without Google credentials configured

**Expected:**
- [ ] Pipeline completes normally — no crash
- [ ] Graceful message about Google integration not configured
- [ ] Content saved locally to `~/.claude-marketing/{brand}/`
- [ ] No error loops or retries

---

## 11. Edge Cases & Error Scenarios

### 11.1 Empty/Minimal Input

| Test | Expected |
|------|----------|
| `/contentforge` (no topic) | Asks for topic, doesn't crash |
| `/brand-setup` (no name) | Asks for brand name |
| `/cf:translate` (no language) | Asks for target language |
| `/cf:connect` (no service name) | Shows available connectors |
| `/cf:help` (no argument) | Shows full help overview |

### 11.2 Very Long Content

| Test | Expected |
|------|----------|
| Whitepaper 5000+ words | Pipeline completes, all phases handle length |
| Topic with 50+ research sources | Phase 2 handles gracefully, may take longer |
| Very long brand name (100+ chars) | Paths handled correctly, no truncation issues |

### 11.3 Unsupported Industry

| Test | Expected |
|------|----------|
| Brand with industry "aerospace" | Falls back to general defaults (no knowledge pack), warns user |
| Brand with industry "" (empty) | Uses defaults, no crash |
| Brand with misspelled industry "tecnology" | Should suggest "technology" or fall back |

### 11.4 Special Characters in Brand Names

| Test | Expected |
|------|----------|
| Apostrophe: "O'Reilly Media" | Drive uploader uses client-side matching (no query injection) |
| Spaces: "Test Brand Alpha" | Paths handled correctly |
| Unicode: "Cafe Express" | No encoding errors |
| Ampersand: "Johnson & Johnson" | No URL encoding issues in Drive/Sheets |

### 11.5 Network Failures

| Test | Expected |
|------|----------|
| Run pipeline without internet | Research phase handles gracefully, may ask for manual input |
| MCP connector timeout | Skill shows error, doesn't crash pipeline |
| Google API quota exceeded | Script shows quota error, content saved locally |

### 11.6 Concurrent Operations

| Test | Expected |
|------|----------|
| `/batch-process` with 5 pieces | Queue managed, no interleaving of outputs |
| Start pipeline while another is running | Handled gracefully (queued or error message) |

### 11.7 Pipeline Interruption

| Test | Expected |
|------|----------|
| Cancel mid-pipeline (Ctrl+C or close session) | No corrupt data, can restart |
| Reconnect after interruption | Fresh start, no stale state |

---

## 12. Regression Checklist

Run this after any changes to verify nothing is broken.

### Core Pipeline

- [ ] Session start hook fires with correct version (v3.4)
- [ ] Brand setup completes all steps A-F
- [ ] Full pipeline runs for blog content type
- [ ] Full pipeline runs for whitepaper content type
- [ ] Phase 3 loads industry knowledge pack (SME Calibration)
- [ ] Phase 3.5 generates visual annotations
- [ ] Phase 4 runs domain-specific validation
- [ ] Phase 6 produces internal link markers
- [ ] Phase 8 embeds charts and link markers in output
- [ ] Hallucination hook catches bad content
- [ ] Hallucination hook skips non-content files

### Skills & Commands

- [ ] All 18 skills respond to invocation
- [ ] All 7 commands appear in Customize panel
- [ ] `/cf:help` shows complete, accurate information
- [ ] `/cf:integrations` shows 7 HTTP connectors with correct status

### Scripts

- [ ] setup.py runs on session start without errors
- [ ] connector-status.py lists 7 HTTP + script connectors
- [ ] sheets-tracker.py operations work (if Google credentials configured)
- [ ] drive-uploader.py operations work (if Google credentials configured)

### Versioning Consistency

- [ ] `plugin.json` version = 3.4.0
- [ ] `hooks.json` version string = v3.4
- [ ] `README.md` version = 3.4.0
- [ ] Marketplace entry version = 3.4.0
- [ ] `13 agents` in all descriptions (not 12)
- [ ] `18 skills` in all descriptions
- [ ] `7 commands` in all descriptions
- [ ] `7 HTTP connectors` in all descriptions (not 6)
- [ ] `10 industry knowledge packs` mentioned
- [ ] `10-phase pipeline` everywhere (not 9-phase)

---

## 13. Test Priority Order

If time is limited, test in this order:

| Priority | Test | Section | Why |
|----------|------|---------|-----|
| 1 | Installation | 2 | Nothing else works without this |
| 2 | Full pipeline — blog/technology | 3.1 | Validates core product |
| 3 | Brand setup (all steps A-F) | 4.1 | Validates v3.4.0 Step F |
| 4 | Pipeline — pharma whitepaper | 3.2 | Validates industry knowledge packs |
| 5 | All 18 skills invocation | 5 | Validates skill registration |
| 6 | `/cf:help` with all arguments | 5 (#18) | Validates help accuracy |
| 7 | Hook tests | 8 | Validates compliance guardrails |
| 8 | Google integration | 10 | Validates Sheets/Drive scripts |
| 9 | Edge cases | 11 | Robustness testing |
| 10 | MCP connectors | 9 | Requires external service accounts |
