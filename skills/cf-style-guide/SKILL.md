---
name: cf-style-guide
description: "Import a brand voice profile from an existing style guide — a .docx/.pdf document, a URL, or manual input — extracting tone, formality, personality, approved/banned terminology, compliance guardrails, and author profiles into a structured brand-profile JSON at ~/.claude-marketing/{brand-slug}/Brand-Guidelines/, then configure the tracking backend (Google Sheets + Drive, Airtable, or local). Triggers on \"/contentforge:cf-style-guide\", \"import our style guide\", \"set up a brand from this document\", \"update the brand profile with new guidelines\", \"extract our banned terms and disclaimers\". Deterministic parsing, no agent. The saved profile is read by every pipeline phase — drafting, brand compliance, humanizer; pairs with /contentforge:brand-setup and /contentforge:cf-switch-backend."
argument-hint: "[brand-name or URL]"
effort: medium
---

# Brand Style Guide Importer

Import brand voice profiles from existing style guide documents, URLs, or manual input. Extracts tone, formality, personality traits, writing style, approved/banned terminology, and compliance guardrails into a structured brand profile JSON that the ContentForge pipeline uses for every piece of content it produces.

## When to Use

Use `/contentforge:cf-style-guide` when:
- You're **onboarding a new brand** and have an existing style guide document (.docx, .pdf) or URL
- You need to **update an existing brand profile** with revised guidelines
- You want to **extract terminology and guardrails** from compliance documents
- You're setting up ContentForge for a **regulated industry** (Pharma, BFSI, Healthcare, Legal) where guardrails are critical
- You want to **validate** that an existing brand profile matches current guidelines
- A client provided a **style guide URL** (Notion page, Google Doc, website page) and you need to import it

**For creating a brand profile from scratch** (no existing style guide), use `/contentforge:brand-setup` with interactive mode.
**For using an existing brand profile**, just reference it by name in `/contentforge:create-content --brand=BrandName`.

## What This Command Does

1. **Load Style Guide** — Fetch style guide from URL (via WebFetch), parse .docx/.pdf document, or accept manual input
2. **Extract Voice Characteristics** — Identify tone (authoritative, conversational, technical, witty), formality level (1-5), personality traits, and writing style patterns
3. **Identify Terminology** — Parse approved terms, banned/prohibited terms, industry-specific jargon, preferred spellings, and acronym definitions
4. **Parse Compliance Requirements** — Extract guardrails, required disclaimers, prohibited claims, regulatory requirements, and sensitivity guidelines
5. **Capture Author Profiles (E-E-A-T)** — If the style guide names authors/spokespeople (About/Team sections, byline conventions), extract name, title, credentials, bio, and profile URLs into `author_profiles`; otherwise prompt for at least one default author (or an explicit "authorless" choice, recorded with its SEO/AEO trade-off). Only user-confirmed facts — never invent credentials
6. **Configure the AI-Assistance Disclosure** — Write the `ai_disclosure` block: `{"mode": "claude-surfaces", "text": null, "author": null}` by default. Explain the three modes plainly: `claude-surfaces` (default — the disclosure attaches when the pipeline runs on a Claude surface, or when the surface is uncertain; it is skipped only when a non-Claude harness is affirmatively detected), `always` (attach on every surface — the safest posture for brands with their own AI-transparency obligations), `off` (never attach; the brand owns that choice and its compliance implications). The `author` field is OPTIONAL and may stay null — the default wording ("reviewed by our editorial team") needs no name; when the brand does name someone, that name also feeds the E-E-A-T byline. Custom `text` replaces the default verbatim — note that the default is deliberately vendor-neutral and claims only the review the pipeline performs; a brand adding stronger claims owns them
6. **Generate Brand Profile JSON** — Create or update a structured JSON profile following the `brand-registry-template.json` schema
7. **Save and Validate** — Save profile to Google Drive (via MCP) or local cache using the brand-cache-manager pattern, and validate the profile works with the ContentForge pipeline
8. **Configure Tracking Backend** — Choose where ContentForge tracks quality scores and delivers output files: Google Sheets + Drive, Airtable, or local filesystem

## Required Inputs

**Minimum Required:**
- **Brand Name** — The name for this brand profile (used in `--brand=` across all skills)

**Style Guide Source (one of):**
- **URL** — Public URL to a style guide page (Notion, Google Docs published link, website page, Confluence page)
- **Document** — Path to a .docx or .pdf style guide file
- **Manual Input** — Interactive mode where you provide voice/terminology/guardrails step by step

**Import Scope:**
- **voice** — Extract only voice and tone characteristics
- **terminology** — Extract only approved/banned terms
- **guardrails** — Extract only compliance requirements and guardrails
- **all** (default) — Extract everything: voice + terminology + guardrails

## How to Use

Basic invocation: `/contentforge:cf-style-guide AcmeMed --source=<url-or-path-or-manual> [--scope=voice|terminology|guardrails|all] [--update]`

**Before running this skill, read `references/cli-usage-examples.md` (in this skill's directory)** for the full set of worked examples — URL import, document import, Notion import, scope-limited imports, manual-input mode, and profile-update mode.

## What Happens

### Step 0: Check Drive for existing brand profile (v3.12.10+, Cowork only)

Before parsing any new source, check whether this brand already has a profile saved in Drive from a previous session. This is critical in Cowork because the sandbox FS is recycled — without this check, every Cowork session would re-create the same brand from scratch.

```bash
python {scripts_dir}/drive-sync-state.py --action read-config
```

If the config returns `configured: false` OR `environment != "cowork-sandbox"`, skip to Step 1 (this is the local-mode flow).

If the config returns `configured: true` AND a Drive MCP is available in your tool list:

1. Use the Drive MCP to search for `{drive_root_folder_name}/_brands/{brand-slug}/profile.json`
2. If found:
   - Download the profile JSON via the MCP, write to `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json` (the canonical local profile path)
   - Compute the content hash of the downloaded file
   - Mark synced state:
     ```bash
     python {scripts_dir}/drive-sync-state.py --action profile-mark-downloaded \
         --brand "{brand}" --drive-file-id "<id>" --content-hash "sha256:<hash>"
     ```
   - Tell the user: "Loaded existing brand profile for `{brand}` from Drive (last updated {timestamp}). Skipping new setup. To update voice/terminology, run `/contentforge:cf-style-guide --update {brand}`."
   - Skip Steps 1-6 (no re-creation needed)
3. If not found in Drive: proceed to Step 1 (normal creation flow). After Step 6 (Save and Validate), upload the new profile to Drive (Step 6.5 below).

### Step 6.5: Push new profile to Drive (v3.12.10+, Cowork only)

After Step 6 saves the profile locally, check if it needs uploading:

```bash
python {scripts_dir}/drive-sync-state.py --action profile-needs-upload --brand "{brand}"
```

If `needs_upload: true` AND Cowork+Drive is configured AND a Drive MCP is available:

1. Use the Drive MCP to upload `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json` to `{drive_root}/_brands/{brand-slug}/profile.json` (create the folder structure if missing).
2. Capture the returned Drive file ID and URL.
3. Mark synced:
   ```bash
   python {scripts_dir}/drive-sync-state.py --action profile-mark-uploaded \
       --brand "{brand}" --drive-file-id "<id>" --drive-url "<url>"
   ```
4. Tell the user: "Brand profile saved to Drive: `{drive_url}` (persists across sessions and is team-shareable)."

If local-mode (no Cowork config), skip — the profile is fine where it is on the host filesystem.

### Step 1: Load Style Guide Source (1-2 minutes)

**From URL:**
- Fetch page content using WebFetch
- Convert HTML to structured text
- Identify sections by heading hierarchy (H1/H2/H3)
- Handle multi-page style guides (follow pagination or table of contents links)

**From Document (.docx/.pdf):**
- Parse document structure (headings, paragraphs, lists, tables)
- Extract text with formatting context (bold = emphasis, tables = structured data)
- Handle multi-section documents with table of contents

**From Manual Input:**
- Interactive prompts for each profile section
- Provide examples and presets for each field
- Allow free-text input for complex requirements

**Prompts you for:**
1. Voice & Tone (select from presets or describe)
2. Formality level (1-5)
3. Personality traits (3-5 adjectives)
4. Approved terminology (comma-separated)
5. Banned terminology (comma-separated)
6. Guardrails and compliance requirements
7. Author profiles (name, title, credentials, profile URL — or explicitly skip for authorless output)

**For a sample "Style Guide Loaded" console transcript, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Step 1 — Load Style Guide Source".**

### Step 2: Extract Voice Characteristics (1-2 minutes)

Analyze the style guide to identify voice and tone patterns.

**Extraction Categories:**

**Tone:**
- Primary tone: authoritative, conversational, technical, witty, empathetic, inspiring
- Secondary tone: (optional, for nuance)
- Tone variations by content type (e.g., blog = conversational, whitepaper = authoritative)

**Formality Level (1-5):**
```
1 = Very Casual (slang OK, first person, contractions)
2 = Casual (contractions OK, approachable, some humor)
3 = Balanced (professional but warm, contractions selective)
4 = Formal (no contractions, third person preferred, structured)
5 = Very Formal (academic, no contractions, passive voice OK)
```

**Personality Traits (3-5 adjectives):**
- Extracted from explicit statements ("Our brand is...") or inferred from examples
- Examples: data-driven, empathetic, innovative, trustworthy, bold

**Writing Style Patterns:**
- Sentence length preference (short/medium/long)
- Paragraph length preference
- Use of rhetorical questions
- Active vs passive voice preference
- First/second/third person preference
- Use of statistics and data
- Storytelling style

**For a sample extracted-voice transcript, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Step 2 — Extract Voice Characteristics".**

### Step 3: Identify Terminology (1-2 minutes)

Parse approved and banned terminology from the style guide.

**Terminology Categories:**

**Approved Terms:**
- Brand-specific terminology (proprietary terms, product names)
- Industry-standard terms (preferred over alternatives)
- Preferred spellings (healthcare vs health care, e-health vs eHealth)
- Acronym definitions (with expansion rules)

**Banned Terms:**
- Competitor names or products
- Outdated terminology
- Insensitive or non-inclusive language
- Overpromising terms (for regulated industries)
- AI telltale phrases (if specified in guide)

**Conditional Terms:**
- Terms allowed in some contexts but not others
- Terms requiring disclaimers or qualifiers

**For a sample extracted-terminology transcript, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Step 3 — Identify Terminology".**

### Step 4: Parse Compliance Requirements (1-2 minutes)

Extract guardrails, disclaimers, and regulatory requirements.

**Guardrail Categories:**

**Required Disclaimers:**
- Legal disclaimers to include in specific content types
- Industry-specific disclaimers (e.g., "This is not medical advice")
- Regional disclaimers (jurisdiction-specific requirements)

**Prohibited Claims:**
- Claims that cannot be made without specific evidence
- Absolute claims ("best", "only", "first") without qualification
- Efficacy claims without clinical data
- Pricing claims without current verification

**Compliance Rules:**
- HIPAA requirements for patient data references
- FDA guidelines for product claims
- FTC requirements for endorsements
- Industry-specific regulations

**Sensitivity Guidelines:**
- Patient privacy (no identifiable information)
- Cultural sensitivity requirements
- Disability-inclusive language
- Age-appropriate content guidelines

**For a sample extracted-compliance transcript, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Step 4 — Parse Compliance Requirements".**

### Step 5: Generate Brand Profile JSON (1 minute)

Create the structured JSON profile.

**Schema — follow `config/brand-registry-template.json` exactly.** Its top-level sections are:
`brand_name`, `industry`, `company_info`, `voice`, `terminology`, `citation_rules`, `guardrails`, `content_patterns`, `seo_preferences`, `target_audience`, `quality_thresholds`, `tracking`, `google_integration`, `knowledge_vault_config`, `data_sources`, `output_preferences`, `visual_identity`, `content_pillars`, `competitor_analysis`, `notification_preferences`, `metadata`.
Fill the sections your import scope covers; leave the rest as template defaults.

**Before generating the brand profile JSON, read `references/brand-profile-json-example.md` (in this skill's directory) for a full synthetic excerpt (voice, content_patterns, terminology, guardrails, metadata) — it is not the full schema, and covers all 8 registered content types (article, blog, whitepaper, faq, research_paper, video_script, case_study, newsletter).**

### Step 6: Save and Validate (1 minute)

**Save Profile:**
- **Local (canonical path):** `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json` — this is the path every other ContentForge skill reads
- **Google Drive (Cowork mode, via MCP):** `{drive_root}/_brands/{brand-slug}/profile.json` (see Step 6.5)
- **Notion (MCP, optional):** additionally save to a brand database in the Notion workspace for team visibility

**Validation Checks:**
- Profile JSON is valid and parseable
- All required fields are present
- Terminology lists are non-empty
- Pipeline compatibility test: run a mock Phase 5 (brand compliance check) with a test paragraph

**For a sample validation transcript, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Step 6 — Save and Validate".**

If the imported style guide reveals a brand website that the profile does not yet carry, tell the user to re-run /contentforge:brand-setup so the Site Harvest can populate brand_pages and brand_facts — the SEO and research phases depend on them.

### Step G: Tracking & Delivery Backend (1-2 minutes)

Choose where ContentForge tracks quality scores and delivers output files. This step configures the `tracking` section of the brand profile.

#### Step G.0 — Probe environment + existing config FIRST

Before offering the three-option menu, run two probes (same flow as `commands/brand-setup.md`, which is the canonical brand-setup document):

```bash
python scripts/plugin-metadata.py --section environment
python scripts/detect-drive-mcp.py
```

- **If `environment == "cowork-sandbox"`:** the "Local" backend writes to the ephemeral Linux sandbox — files vanish at session end. A Drive route (Anthropic platform integration or a Pipedream/Composio/Zapier/Make Drive aggregator MCP) is effectively REQUIRED for persistent output. If a Drive MCP is visible in your tool list, confirm and use it (skip the menu). If not, warn the user and point them to Cowork → Settings → Integrations → Google Drive, or `/contentforge:cf-cowork-setup`.
- **If `detect-drive-mcp.py` returns `recommended_path: "mcp"`:** confirm the detected connector and go straight to the MCP-based Drive route — skip the service-account flow.
- **If it returns `recommended_path: "service_account"`:** confirm the found credentials (`client_email`) and use the service-account route.
- **If both are present:** ask which to use; default to MCP (simpler auth, Cowork-compatible).
- **If `recommended_path: "none"` in local Claude Code:** show the three-option menu (Local is a fine default on a real host filesystem) — **read `references/tracking-backend-examples.md` (in this skill's directory), section "Three-option menu presentation", for the exact menu text to present (only when G.0 found nothing).**

**If user picks Google Sheets + Drive:**

1. Check if Google credentials already exist at `~/.claude-marketing/google-credentials.json`
2. If not, guide through service account setup:
   - Create a GCP project at console.cloud.google.com
   - Enable Google Sheets API and Google Drive API
   - Create a service account and download the JSON key file
   - Save to `~/.claude-marketing/google-credentials.json`
   - Share the target Google Sheet and Drive folder with the service account email
3. Ask for the Google Sheet ID (from the Sheet URL)
4. Ask for the Google Drive folder ID (from the folder URL)
5. Set in brand profile:
   ```json
   "tracking": {
     "backend": "google_sheets",
     "google_sheets": {
       "sheet_id": "{user-provided}",
       "tab_name": "ContentForge Tracking",
       "credentials_path": "~/.claude-marketing/google-credentials.json"
     },
     "google_drive": {
       "folder_id": "{user-provided}",
       "credentials_path": "~/.claude-marketing/google-credentials.json"
     }
   }
   ```
6. Run `python {scripts_dir}/sheets-tracker.py --action init --sheet-id {sheet_id}` to create the tracking schema

**If user picks Airtable:**

1. Check if `AIRTABLE_TOKEN` environment variable exists
2. If not, guide through token creation:
   - Go to airtable.com/create/tokens
   - Create a Personal Access Token with `data.records:read`, `data.records:write`, `schema.bases:read`, `schema.bases:write` scopes
   - Select the target base (or create a new one)
   - Set the token as `AIRTABLE_TOKEN` environment variable
3. Ask for the Airtable Base ID (from the base URL: `airtable.com/{base_id}/...`)
4. Set in brand profile:
   ```json
   "tracking": {
     "backend": "airtable",
     "airtable": {
       "base_id": "{user-provided}",
       "table_name": "ContentForge Tracking"
     }
   }
   ```
5. Run `python {scripts_dir}/airtable-tracker.py --action init --base-id {base_id}` to create the tracking table with schema

**If user picks Local:**

1. No setup required
2. Set in brand profile:
   ```json
   "tracking": {
     "backend": "local",
     "local": {
       "tracking_dir": "~/.claude-marketing/{brand}/tracking"
     }
   }
   ```
3. Run `python {scripts_dir}/local-tracker.py --action init --brand "{brand}"` to create the tracking directory and initial tracking.json

**If user skips Step G** (presses enter without choosing or says "skip"):
- Default to `"local"` with a note:
  ```
  Defaulted to local tracking. You can switch to Google Sheets or
  Airtable anytime by running /contentforge:cf-switch-backend.
  ```

**For a sample "Tracking Backend Configured" transcript, read `references/tracking-backend-examples.md` (in this skill's directory), section "Example Output (backend configured)".**

### Step 7: Audience Personas

Ask the user about their target audience:

```
Who is the primary audience for this brand's content?

Please provide:
  1. Job title/role (e.g., "VP of Engineering", "Marketing Manager", "Small business owner")
  2. Industry/company size (e.g., "Enterprise SaaS, 1000+ employees")
  3. Reading level (executive summary / professional / technical / general public)
  4. Key pain points (what problems are they trying to solve?)
  5. Goals (what outcomes do they want from reading your content?)

Optional: Secondary audience(s) if the brand targets multiple personas.
```

Store in `target_audience.primary_persona` with fields: `title`, `industry`, `company_size`, `reading_level`, `pain_points` (array), `goals` (array).

If user skips: Set `target_audience.primary_persona` to default generic persona and log warning.

### Step 8: Competitor Analysis

Ask the user about competitors:

```
Who are your top 3-5 content competitors?

These are brands whose content ranks for the same keywords or targets the same audience.
For each competitor, provide:
  - Name and URL
  - What they do well in content (e.g., "great technical depth", "strong SEO")
  - What they miss or do poorly (e.g., "no video content", "outdated stats")

This helps ContentForge differentiate your content from theirs.
```

Store in `competitor_analysis.top_competitors` array. Each entry: `name`, `url`, `content_strengths` (array), `content_gaps` (array).

If user skips: Leave empty but note: "Competitor analysis skipped — Phase 1 Research will still analyze SERP competitors, but won't have your strategic differentiation context."

### Step 9: Content Pillars

Ask the user about content strategy:

```
What are your brand's core content pillars (topic areas you want to own)?

Examples:
  - "AI in Healthcare" — our flagship thought leadership topic
  - "Product Tutorials" — how-to content for our platform
  - "Industry Trends" — quarterly market analysis

List 3-5 pillars with a brief description and target keywords for each.
```

Store in `content_pillars` array. Each entry: `name`, `description`, `keywords` (array), `content_types` (array).

If user skips: Leave empty. Content will be produced without pillar context.

### Step 10: Visual Identity

Ask the user about brand visuals:

```
What are your brand's visual identity elements?

  1. Brand colors:
     - Primary color (hex, e.g., #0066CC)
     - Secondary color (hex)
     - Accent color (hex, optional)
  2. Preferred image style: photorealistic / illustration / flat design / mixed
  3. Logo description (brief text description — we don't store image files)

These are used for chart generation (Phase 3.5) and AI image prompts.
```

Store in `visual_identity` with fields: `brand_colors` (primary, secondary, accent), `image_style`, `logo_description`.

If user skips: Use defaults (primary: #0066CC, secondary: #FF6600) and note in profile.

## Output

The style guide import produces:

| Output | Description |
|--------|------------|
| **Brand Profile JSON** | Structured profile following brand-registry-template.json schema |
| **Voice Summary** | Human-readable summary of tone, formality, personality, style |
| **Terminology Count** | Total approved, banned, and conditional terms extracted |
| **Guardrails List** | Disclaimers, prohibited claims, compliance rules |
| **Validation Status** | Pipeline compatibility test results |
| **Save Location** | Where the profile was saved (Drive, Notion, local) |

## Output Example

**Before presenting the final completion summary to the user, read `references/extraction-example-transcripts.md` (in this skill's directory), section "Final pipeline completion transcript (Output Example)" — reproduce its shape with this run's actual values.**

## MCP Integrations

### Optional (HTTP)
- **Notion** — Save brand profile to a Notion database for team-wide access and collaborative editing. Import style guides from Notion pages.
- **Google Drive** — Save brand profile JSON to Drive for shared access and backup. Read existing profiles from Drive.

### Fallback (No MCP)
Without MCP connections, profiles are saved to the canonical local path `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json`. Profiles can be manually shared by copying the JSON file. URL-based style guide import uses WebFetch (built-in), which works without any MCP connection.

## Troubleshooting

**Hitting an error during import? Read `references/troubleshooting.md` (in this skill's directory)** for the five documented failure modes (voice extraction, zero terms found, URL fetch failure, Phase 5 validation failure, low import confidence) and their causes/solutions.

## Limitations

- **PDF parsing** can miss complex layouts (multi-column, heavy formatting). For best results, convert to .docx first.
- **Non-English style guides** are processed but terminology extraction is less accurate outside English
- **Implicit voice** — If a style guide shows examples but doesn't explicitly state voice characteristics, extraction confidence will be lower
- **Visual identity** sections (logos, colors, fonts) are skipped — this tool focuses on content voice only
- **Maximum document size**: 50 pages / 25,000 words (larger documents should be split into sections)

## Agent Used

None. This skill uses deterministic parsing (document structure analysis, pattern matching for terminology, rule extraction for guardrails) combined with WebFetch for URL-based sources. No agent-based reasoning is needed since the extraction follows structured patterns.

## Related Skills

- **[/contentforge:brand-setup](../../commands/brand-setup.md)** — The canonical brand-setup flow (this skill conforms to its save path and Step G.0 probes)
- **[/contentforge:create-content](../../commands/create-content.md)** — Uses brand profiles for Phase 3 (Drafting), Phase 5 (Brand Compliance), Phase 6.5 (Humanizer)
- **[/contentforge:batch-process](../batch-process/SKILL.md)** — All pieces in a batch reference a brand profile
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** — Refresh maintains brand compliance using the profile
- **[/contentforge:cf-integrations](../cf-integrations/SKILL.md)** — Check Notion and Google Drive connector status
- **[/contentforge:cf-switch-backend](../cf-switch-backend/SKILL.md)** — Switch tracking backend (local/airtable/google) after initial setup

---

<!-- Version is pulled live by /contentforge:cf-help. The source of truth is
     .claude-plugin/plugin.json. Don't hardcode versions in skill bodies. -->

**Agent:** None (deterministic parsing)
**MCP:** Google Drive (optional via Anthropic platform integration / Pipedream / Composio / Zapier / Make aggregator), Notion (optional)
**Output:** Brand profile JSON at `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json`, voice summary, terminology count, guardrails list, validation status, tracking backend config
