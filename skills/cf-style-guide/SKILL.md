---
name: cf-style-guide
description: Import and manage brand voice profiles from style guide documents or URLs, extracting tone, terminology, guardrails, and compliance requirements into structured brand profile JSON
argument-hint: "[brand-name or URL]"
---

# Brand Style Guide Importer

Import brand voice profiles from existing style guide documents, URLs, or manual input. Extracts tone, formality, personality traits, writing style, approved/banned terminology, and compliance guardrails into a structured brand profile JSON that the ContentForge pipeline uses for every piece of content it produces.

## When to Use

Use `/cf:style-guide` when:
- You're **onboarding a new brand** and have an existing style guide document (.docx, .pdf) or URL
- You need to **update an existing brand profile** with revised guidelines
- You want to **extract terminology and guardrails** from compliance documents
- You're setting up ContentForge for a **regulated industry** (Pharma, BFSI, Healthcare, Legal) where guardrails are critical
- You want to **validate** that an existing brand profile matches current guidelines
- A client provided a **style guide URL** (Notion page, Google Doc, website page) and you need to import it

**For creating a brand profile from scratch** (no existing style guide), use `/brand-setup` with interactive mode.
**For using an existing brand profile**, just reference it by name in `/contentforge --brand=BrandName`.

## What This Command Does

1. **Load Style Guide** — Fetch style guide from URL (via WebFetch), parse .docx/.pdf document, or accept manual input
2. **Extract Voice Characteristics** — Identify tone (authoritative, conversational, technical, witty), formality level (1-5), personality traits, and writing style patterns
3. **Identify Terminology** — Parse approved terms, banned/prohibited terms, industry-specific jargon, preferred spellings, and acronym definitions
4. **Parse Compliance Requirements** — Extract guardrails, required disclaimers, prohibited claims, regulatory requirements, and sensitivity guidelines
5. **Generate Brand Profile JSON** — Create or update a structured JSON profile following the `brand-registry-template.json` schema
6. **Save and Validate** — Save profile to Google Drive (via MCP) or local cache using the brand-cache-manager pattern, and validate the profile works with the ContentForge pipeline
7. **Configure Tracking Backend** — Choose where ContentForge tracks quality scores and delivers output files: Google Sheets + Drive, Airtable, or local filesystem

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

### Import from URL
```
/cf:style-guide AcmeMed --source=https://acmemed.com/brand-guidelines
```

### Import from Document
```
/cf:style-guide AcmeMed --source=./AcmeMed-Style-Guide.docx
```

### Import from Notion Page
```
/cf:style-guide AcmeMed --source=https://www.notion.so/acme/Brand-Guidelines-abc123
```

### Import Only Terminology
```
/cf:style-guide AcmeMed --source=https://acmemed.com/terminology --scope=terminology
```

### Import Only Guardrails (Compliance)
```
/cf:style-guide AcmeMed --source=./compliance-requirements.pdf --scope=guardrails
```

### Manual Input (No Document)
```
/cf:style-guide AcmeMed --source=manual
```
**Prompts you for:**
1. Voice & Tone (select from presets or describe)
2. Formality level (1-5)
3. Personality traits (3-5 adjectives)
4. Approved terminology (comma-separated)
5. Banned terminology (comma-separated)
6. Guardrails and compliance requirements

### Update Existing Profile
```
/cf:style-guide AcmeMed --source=https://acmemed.com/updated-guidelines --update
```
Merges new information into the existing profile without overwriting unchanged fields.

## What Happens

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

**Example:**
```
Style Guide Loaded
================================================================

Source: https://acmemed.com/brand-guidelines
Page Title: "AcmeMed Brand Voice & Content Guidelines"
Sections Found: 8
  1. Brand Overview
  2. Voice & Tone
  3. Writing Style
  4. Approved Terminology
  5. Banned Terms & Phrases
  6. Regulatory Compliance
  7. Visual Identity (skipped — not relevant to content)
  8. Social Media Guidelines

Content Length: 4,200 words
Parsing: Complete
================================================================
```

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

**Example Output:**
```
Voice Characteristics Extracted
================================================================

Tone:
  Primary: Authoritative
  Secondary: Empathetic
  By Content Type:
    Article: Authoritative + data-driven
    Blog: Authoritative + approachable
    Whitepaper: Authoritative + academic

Formality: 4 (Formal)
  No contractions in articles/whitepapers
  Contractions OK in blog posts only

Personality Traits: data-driven, trustworthy, innovative, empathetic, precise

Writing Style:
  Sentence Length: Medium (15-25 words average)
  Paragraphs: 3-5 sentences
  Voice: Active (90%+)
  Person: Third person for articles, second person for blogs
  Rhetorical Questions: Sparingly (1-2 per piece max)
  Statistics: Heavy use, always cited
  Storytelling: Patient stories as examples (anonymized)

Confidence: 92% (style guide was explicit about most elements)
================================================================
```

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

**Example Output:**
```
Terminology Extracted
================================================================

Approved Terms (47 total):
  Brand Terms:
    "AcmeMed" (never "Acme Med" or "ACMEMED")
    "AcmeDiagnostics" (product name, always capitalized)
    "AcmeCare Platform" (full name on first use, "the Platform" after)

  Industry Terms:
    "healthcare" (one word, not "health care")
    "precision medicine" (preferred over "personalized medicine")
    "clinical decision support" (preferred over "clinical AI")
    "value-based care" (preferred over "value-driven care")

  Acronyms:
    "AI" — Artificial Intelligence (expand on first use)
    "EMR" — Electronic Medical Record (expand on first use)
    "HIPAA" — never expand (universally known in target audience)

Banned Terms (23 total):
  "revolutionary" — overpromising, use "innovative" instead
  "breakthrough" — overpromising, use "advancement" instead
  "cure" — regulatory risk, use "treatment" or "therapy"
  "guaranteed" — compliance violation in healthcare
  "CompetitorX", "CompetitorY" — no competitor mentions
  "patients love it" — unsubstantiated claim
  "cutting-edge" — cliche, use specific technology descriptions
  ... (16 more)

Conditional Terms (8 total):
  "FDA-cleared" — only for products with actual FDA clearance
  "clinically validated" — only with citation to clinical trial
  "reduces costs" — only with specific percentage and source
================================================================
```

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

**Example Output:**
```
Compliance Requirements Extracted
================================================================

Required Disclaimers (4):
  1. All articles: "This content is for informational purposes only
     and does not constitute medical advice."
  2. Product mentions: "AcmeDiagnostics is pending FDA clearance
     for [specific use case]." (update status quarterly)
  3. Patient stories: "Patient names and identifying details have
     been changed to protect privacy."
  4. Clinical data: "Results may vary. Clinical outcomes depend
     on individual patient factors."

Prohibited Claims (6):
  1. No efficacy claims without peer-reviewed citation
  2. No "FDA-approved" (use "FDA-cleared" for 510(k) devices)
  3. No cost savings claims without specific study reference
  4. No comparison claims vs competitors
  5. No absolute claims ("best", "only", "first") without qualification
  6. No patient testimonials as efficacy evidence

Compliance Rules:
  HIPAA: Never include PHI (Protected Health Information)
  FDA: Follow 510(k) promotional guidelines for device content
  FTC: Disclose any sponsored or partnership content

Sensitivity Guidelines:
  Language: Person-first (e.g., "patients with diabetes" not "diabetics")
  Imagery descriptions: Diverse, inclusive, respectful
  Avoid: Military metaphors for disease ("battle cancer", "fight disease")

Confidence: 96% (compliance section was highly structured)
================================================================
```

### Step 5: Generate Brand Profile JSON (1 minute)

Create the structured JSON profile.

**Profile Schema (brand-registry-template.json):**
```json
{
  "brand_name": "AcmeMed",
  "version": "1.0.0",
  "last_updated": "2026-02-25T14:30:00Z",
  "source": "https://acmemed.com/brand-guidelines",
  "import_scope": "all",

  "voice": {
    "primary_tone": "authoritative",
    "secondary_tone": "empathetic",
    "formality_level": 4,
    "personality_traits": ["data-driven", "trustworthy", "innovative", "empathetic", "precise"],
    "tone_by_content_type": {
      "article": "authoritative + data-driven",
      "blog": "authoritative + approachable",
      "whitepaper": "authoritative + academic",
      "faq": "clear + helpful",
      "research_paper": "academic + precise"
    }
  },

  "writing_style": {
    "sentence_length": "medium",
    "paragraph_length": "3-5 sentences",
    "active_voice_target": 90,
    "person": {
      "article": "third",
      "blog": "second",
      "whitepaper": "third"
    },
    "contractions": {
      "article": false,
      "blog": true,
      "whitepaper": false
    },
    "rhetorical_questions": "sparingly",
    "statistics_usage": "heavy",
    "storytelling": "patient stories, anonymized"
  },

  "terminology": {
    "approved": [
      {"term": "AcmeMed", "note": "Never 'Acme Med' or 'ACMEMED'"},
      {"term": "healthcare", "note": "One word, not 'health care'"},
      {"term": "precision medicine", "note": "Preferred over 'personalized medicine'"}
    ],
    "banned": [
      {"term": "revolutionary", "replacement": "innovative"},
      {"term": "breakthrough", "replacement": "advancement"},
      {"term": "cure", "replacement": "treatment or therapy"},
      {"term": "guaranteed", "note": "Compliance violation in healthcare"}
    ],
    "conditional": [
      {"term": "FDA-cleared", "condition": "Only for products with actual FDA clearance"},
      {"term": "clinically validated", "condition": "Only with citation to clinical trial"}
    ],
    "acronyms": [
      {"acronym": "AI", "expansion": "Artificial Intelligence", "expand_on_first_use": true},
      {"acronym": "HIPAA", "expansion": "Health Insurance Portability and Accountability Act", "expand_on_first_use": false}
    ]
  },

  "guardrails": {
    "required_disclaimers": [
      {"context": "all_articles", "text": "This content is for informational purposes only and does not constitute medical advice."},
      {"context": "product_mentions", "text": "AcmeDiagnostics is pending FDA clearance for [specific use case]."}
    ],
    "prohibited_claims": [
      "No efficacy claims without peer-reviewed citation",
      "No 'FDA-approved' — use 'FDA-cleared' for 510(k) devices",
      "No cost savings claims without specific study reference"
    ],
    "compliance": {
      "hipaa": "Never include PHI",
      "fda": "Follow 510(k) promotional guidelines",
      "ftc": "Disclose sponsored or partnership content"
    },
    "sensitivity": {
      "language": "person-first",
      "avoid_metaphors": ["military metaphors for disease"],
      "inclusivity": "diverse, respectful, representative"
    }
  },

  "metadata": {
    "industry": "Healthcare",
    "sub_industry": "Health Technology / Medical Devices",
    "target_audiences": ["Healthcare Executives", "Clinical Decision Makers", "Health System IT Leaders"],
    "content_types_supported": ["article", "blog", "whitepaper", "faq", "research_paper"],
    "import_confidence": 94
  }
}
```

### Step 6: Save and Validate (1 minute)

**Save Profile:**
- **Google Drive (MCP):** Save to `ContentForge/[BrandName]-profile-cache.json`
- **Notion (MCP):** Save to brand database in Notion workspace
- **Local Cache:** Save to `~/.claude-marketing/brands/[BrandName]-profile.json`

**Validation Checks:**
- Profile JSON is valid and parseable
- All required fields are present
- Terminology lists are non-empty
- Pipeline compatibility test: run a mock Phase 5 (brand compliance check) with a test paragraph

**Example Validation:**
```
Brand Profile Validation
================================================================

Profile: AcmeMed v1.0.0
  JSON Valid: Yes
  Required Fields: 12/12 present
  Voice Complete: Yes (tone, formality, personality, style)
  Terminology: 47 approved, 23 banned, 8 conditional
  Guardrails: 4 disclaimers, 6 prohibited claims, 3 compliance rules
  Acronyms: 12 defined

Pipeline Compatibility Test:
  Phase 3 (Drafting): Can apply voice settings — PASS
  Phase 5 (Brand Compliance): Can check terminology — PASS
  Phase 6 (SEO): No conflicts with SEO settings — PASS
  Phase 6.5 (Humanizer): Can apply personality — PASS

Profile Saved:
  Google Drive: ContentForge/AcmeMed-profile-cache.json
  Local Cache: ~/.claude-marketing/brands/AcmeMed-profile.json
  Cache Hash: SHA256:a3f2c1... (for fast cache lookup)

Status: READY — Profile can be used with /contentforge --brand=AcmeMed
================================================================
```

### Step G: Tracking & Delivery Backend (1-2 minutes)

Choose where ContentForge tracks quality scores and delivers output files. This step configures the `tracking` section of the brand profile.

**Present the user with three options:**

```
Step G: Tracking & Delivery Backend
================================================================

Choose where ContentForge tracks quality scores and delivers
output files for this brand:

  1. Google Sheets + Drive (Recommended if you have Google Workspace)
     Tracks in Google Sheets, delivers .docx to Google Drive
     Requires: Service account credentials (~5 min setup)

  2. Airtable (Recommended for simplicity)
     Tracks in Airtable, delivers .docx as record attachments
     Requires: Personal Access Token (~2 min setup)

  3. Local (No setup required)
     Tracks in local JSON, delivers .docx to local filesystem
     No auth needed, but no cloud access or collaboration

Your choice: ___
================================================================
```

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
6. Run `python3 {scripts_dir}/sheets-tracker.py --action init --sheet-id {sheet_id}` to create the tracking schema

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
5. Run `python3 {scripts_dir}/airtable-tracker.py --action init --base-id {base_id}` to create the tracking table with schema

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
3. Run `python3 {scripts_dir}/local-tracker.py --action init --brand "{brand}"` to create the tracking directory and initial tracking.json

**If user skips Step G** (presses enter without choosing or says "skip"):
- Default to `"local"` with a note:
  ```
  Defaulted to local tracking. You can switch to Google Sheets or
  Airtable anytime by running /cf:switch-backend.
  ```

**Example Output:**
```
Tracking Backend Configured
================================================================

Backend: Airtable
Base ID: appXXXXXXXXXXXXXX
Table: ContentForge Tracking (created with 20-column schema)
Token: AIRTABLE_TOKEN detected

Tracking table initialized with columns:
  requirement_id, brand, content_type, title, target_audience,
  word_count_target, priority, status, created_at, started_at,
  completed_at, quality_score, content_quality, citation_integrity,
  brand_compliance, seo_performance, readability, actual_word_count,
  output_file (Attachment), notes

To switch backends later: /cf:switch-backend
================================================================
```

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

```
Style Guide Import Complete
================================================================

Brand: AcmeMed
Source: https://acmemed.com/brand-guidelines
Import Scope: All (voice + terminology + guardrails)
Processing Time: 6 minutes

Results:
  Voice: Authoritative + Empathetic, Formality 4/5
  Personality: data-driven, trustworthy, innovative, empathetic, precise
  Terminology: 47 approved, 23 banned, 8 conditional, 12 acronyms
  Guardrails: 4 disclaimers, 6 prohibited claims, 3 compliance rules
  Import Confidence: 94%

Validation: PASS (all pipeline phases compatible)

Saved to:
  Google Drive: ContentForge/AcmeMed-profile-cache.json
  Local: ~/.claude-marketing/brands/AcmeMed-profile.json

Use with: /contentforge --brand=AcmeMed
================================================================
```

## MCP Integrations

### Optional (HTTP)
- **Notion** — Save brand profile to a Notion database for team-wide access and collaborative editing. Import style guides from Notion pages.
- **Google Drive** — Save brand profile JSON to Drive for shared access and backup. Read existing profiles from Drive.

### Fallback (No MCP)
Without MCP connections, profiles are saved to the local brand cache at `~/.claude-marketing/brands/`. Profiles can be manually shared by copying the JSON file. URL-based style guide import uses WebFetch (built-in), which works without any MCP connection.

## Troubleshooting

### "Could not extract voice characteristics"
**Cause:** Style guide doesn't have explicit voice/tone section, or the page structure is too unstructured.
**Solution:** Use `--source=manual` to provide voice characteristics interactively, then import terminology and guardrails from the document separately.

### "0 approved terms found"
**Cause:** Terminology is embedded in prose rather than structured lists.
**Solution:** Check if the style guide has a terminology table or glossary section. If not, use `--source=manual --scope=terminology` to add terms interactively.

### "URL fetch failed"
**Cause:** Page requires authentication (private Notion, Google Doc not published, login-required page).
**Solution:** If the page is in Notion, use the Notion MCP to access it instead of URL fetch. For Google Docs, use the published web link (File > Share > Publish to Web). For login-required pages, download the page as .docx or .pdf and use the document source.

### "Profile validation failed — Phase 5 incompatible"
**Cause:** Terminology lists contain conflicts (same term in approved and banned lists) or the profile JSON is malformed.
**Solution:** Review the profile JSON for conflicts. Use `--update` mode to fix specific fields without reimporting the entire guide.

### "Import confidence below 70%"
**Cause:** Style guide was vague, lacked structure, or covered primarily visual identity (not content voice).
**Solution:** Supplement with manual input for low-confidence sections. The profile will flag which sections have low confidence so you know what to manually verify.

## Limitations

- **PDF parsing** can miss complex layouts (multi-column, heavy formatting). For best results, convert to .docx first.
- **Non-English style guides** are processed but terminology extraction is less accurate outside English (multilingual support improving in v2.2)
- **Implicit voice** — If a style guide shows examples but doesn't explicitly state voice characteristics, extraction confidence will be lower
- **Visual identity** sections (logos, colors, fonts) are skipped — this tool focuses on content voice only
- **Maximum document size**: 50 pages / 25,000 words (larger documents should be split into sections)

## Agent Used

None. This skill uses deterministic parsing (document structure analysis, pattern matching for terminology, rule extraction for guardrails) combined with WebFetch for URL-based sources. No agent-based reasoning is needed since the extraction follows structured patterns.

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** — Uses brand profiles for Phase 3 (Drafting), Phase 5 (Brand Compliance), Phase 6.5 (Humanizer)
- **[/batch-process](../batch-process/SKILL.md)** — All pieces in a batch reference a brand profile
- **[/content-refresh](../content-refresh/SKILL.md)** — Refresh maintains brand compliance using the profile
- **[/cf:integrations](../cf-integrations/SKILL.md)** — Check Notion and Google Drive connector status
- **[/cf:switch-backend](../cf-switch-backend/SKILL.md)** — Switch tracking backend (local/airtable/google) after initial setup

---

**Version:** 3.5.0
**Agent:** None (deterministic parsing)
**MCP:** Google Drive (optional), Notion (optional)
**Processing Time:** 5-10 minutes
**Output:** Brand profile JSON, voice summary, terminology count, guardrails list, validation status, tracking backend config
