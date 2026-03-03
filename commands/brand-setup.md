---
description: Configure brand voice, terminology, compliance guardrails, and style guide for content production
argument-hint: "<brand name> [--source=url|document|manual]"
---

# Brand Setup

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Create or update a brand voice profile that the ContentForge pipeline uses for every piece of content it produces. Import from existing style guide documents, URLs, or build interactively. Captures tone, formality, personality traits, approved and banned terminology, compliance guardrails, and industry-specific requirements.

## Trigger

User runs `/brand-setup` or asks to set up a brand, configure brand voice, import a style guide, or onboard a new client.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Brand name** — the name for this brand profile (used in `--brand=` across all skills)

2. **Style guide source** — one of:
   - **URL** — public URL to a style guide page (Notion, Google Docs published link, website, Confluence)
   - **Document** — path to a .docx or .pdf style guide file
   - **Manual** — interactive mode where you provide voice, terminology, and guardrails step by step

3. **Import scope** (optional, default: all):
   - `voice` — extract only voice and tone characteristics
   - `terminology` — extract only approved/banned terms
   - `guardrails` — extract only compliance requirements
   - `all` — extract everything

## Setup Methods

### Method 1: Import from Style Guide (Recommended)

If the user has an existing style guide document or URL:

1. **Fetch and parse** the style guide (WebFetch for URLs, document parser for .docx/.pdf)
2. **Extract voice characteristics:**
   - Tone (authoritative, conversational, technical, witty)
   - Formality level (1-5 scale)
   - Personality traits (e.g., "bold but not aggressive", "technical but accessible")
   - Writing style patterns (sentence length, paragraph structure, use of questions)
3. **Identify terminology:**
   - Approved terms and preferred spellings
   - Banned/prohibited words and phrases
   - Industry jargon (keep, simplify, or avoid)
   - Acronym handling rules
4. **Parse compliance requirements:**
   - Required disclaimers by content type
   - Prohibited claims (superlatives, health claims, financial promises)
   - Regulatory framework (HIPAA, GDPR, financial services, etc.)
   - Sensitivity guidelines

### Method 2: Interactive Setup

Walk through 3 sections:

#### Voice & Tone (5 questions)
1. "Describe your brand voice in 3 words" (e.g., bold, witty, professional)
2. "How formal is your communication?" (1=very casual, 5=very formal)
3. "Who is your reader? What do they expect?" (maps to audience expectations)
4. "Name a brand whose writing style you admire" (reference point)
5. "Should the content use first person (we), second person (you), or third person?"

#### Terminology (3 questions)
6. "Any specific terms you always use?" (product names, branded terms, preferred spellings)
7. "Any words or phrases to avoid?" (competitor names, outdated terms, banned language)
8. "How should industry jargon be handled — keep it, explain it, or avoid it?"

#### Compliance (2 questions)
9. "What industry are you in? Any regulatory requirements?" (infer HIPAA, GDPR, etc.)
10. "Any mandatory disclaimers or legal language required in content?"

### Method 3: Quick Start (Minimal Input)

For users who want to start producing content immediately:
1. Brand name
2. One-sentence description of what the brand does
3. Pick a tone: authoritative / conversational / technical / witty

The pipeline will use these defaults and refine the profile as more content is produced.

## Profile Storage

Profiles are saved as structured JSON and used automatically by every pipeline phase:
- Phase 3 (Drafter) — applies voice and terminology
- Phase 5 (Proofreader) — enforces compliance and restrictions
- Phase 6 (SEO) — uses approved terminology in meta tags
- Phase 6.5 (Humanizer) — applies personality profile
- Phase 7 (Reviewer) — scores brand compliance

## Google Integration (Auto-Configure)

After setting up voice, terminology, and compliance, **automatically check** whether the `google_integration` section is configured in the brand profile. Do NOT ask the user to edit JSON manually — handle it conversationally.

### If already configured → skip this section entirely.

### If NOT configured → ask 3 simple questions:

1. **"Do you have a Google service account credentials file? If yes, where is it?"**
   - Default path: `~/.claude-marketing/google-credentials.json`
   - If file exists at default path, confirm and use it. Don't ask.
   - If not found, explain: "Your agency admin provides this file. Save it to `~/.claude-marketing/google-credentials.json` and re-run setup."
   - If they provide a custom path, use that.

2. **"What's your tracking sheet URL? (paste the Google Sheets URL)"**
   - Extract the sheet ID from the URL automatically:
     - `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit` → extract `SHEET_ID_HERE`
   - The user should NEVER have to find or type a raw ID.

3. **"What's your Drive output folder URL? (paste the Google Drive folder URL)"**
   - Extract the folder ID from the URL automatically:
     - `https://drive.google.com/drive/folders/FOLDER_ID_HERE` → extract `FOLDER_ID_HERE`
   - The user should NEVER have to find or type a raw ID.

### Auto-fill the brand profile:

```json
"google_integration": {
  "credentials_path": "~/.claude-marketing/google-credentials.json",
  "tracking_sheet_id": "<extracted from URL>",
  "tracking_sheet_tab": "ContentForge Tracking",
  "drive_output_folder_id": "<extracted from URL>"
}
```

### Verify connectivity:

After filling in the values, run a quick connectivity test:
- Try opening the sheet via `sheets-tracker.py --action init`
- If it succeeds → "Sheet connected. Tracking is ready."
- If it fails → show the specific error and how to fix it (e.g., "Share the sheet with `<service_account_email>` as Editor")

### If credentials file doesn't exist → the pipeline still works.

All 9 phases run normally. Content is produced and returned directly in the conversation. Google integration is optional — it adds tracking and delivery but isn't required. Tell the user:
- "Google integration is optional. You can produce content right now without it."
- "To add tracking later, just run `/brand-setup` again."

## After Setup

After creating the profile, show a summary:

**Brand Profile: [Name]**
| Attribute | Value |
|-----------|-------|
| Tone | Authoritative / Conversational / etc. |
| Formality | 1-5 |
| Person | First / Second / Third |
| Approved terms | [count] |
| Banned terms | [count] |
| Compliance | [frameworks] |
| Sheets tracking | Connected / Not configured |
| Drive delivery | Connected / Not configured |

Ask: "Brand profile for [name] is ready. Would you like to:
- Start producing content? (`/create-content`)
- Generate a content brief? (`/content-brief`)
- Import additional guidelines from another source?
- Create a test piece to validate the voice settings?
- Check which connectors are active? (`/integrations`)"
