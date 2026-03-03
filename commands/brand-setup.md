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

After setting up voice, terminology, and compliance, **automatically check** whether Google integration is configured. Do NOT ask the user to edit JSON manually — handle it conversationally.

> **Important:** Google integration is optional. ContentForge produces content without it. Google adds tracking (Sheets) and delivery (Drive) on top. Always offer: "Want to set up Google Sheets tracking and Drive delivery? You can skip this and add it later."

### If already configured → verify and skip.

Check if `~/.claude-marketing/google-credentials.json` exists AND `google_integration.tracking_sheet_id` is non-empty in the brand profile. If both are good, say "Google integration is already configured" and move on.

### If NOT configured → guide the user through setup.

#### Step A: Check for credentials file

Check if `~/.claude-marketing/google-credentials.json` exists:

**If the file exists:**
- Read the `client_email` field from the JSON
- Confirm: "Found Google service account: `{client_email}`. Using this for Sheets and Drive."
- Proceed to Step B.

**If the file does NOT exist:**
- The user needs to create their own service account. Every organization creates their own — this is NOT shared between plugin users. Walk them through it:

Tell the user:

> **You need a Google service account to connect Sheets and Drive. Here's how (5 minutes):**
>
> 1. Go to [console.cloud.google.com](https://console.cloud.google.com)
> 2. Create a project (or use an existing one) — any name works
> 3. Go to **APIs & Services > Library** — enable **Google Sheets API** and **Google Drive API**
> 4. Go to **IAM & Admin > Service Accounts** — click **+ Create Service Account**
>    - Name it anything (e.g., `contentforge`)
>    - Click **Create and Continue**, then **Done**
> 5. Click on the service account you just created
> 6. Go to **Keys** tab > **Add Key** > **Create new key** > **JSON**
> 7. A file downloads — save it as: `~/.claude-marketing/google-credentials.json`
>
> **Come back here when you've saved the file. I'll verify it automatically.**

Then wait. When the user returns, check the file again. If found, read `client_email` and proceed. If still not found, say "No rush — you can set this up later and re-run `/brand-setup`."

#### Step B: Get the tracking sheet URL

Ask: **"Paste your Google Sheets URL for content tracking (or say 'create new' and I'll tell you what to do)"**

**If they paste a URL:**
- Extract sheet ID: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit` → `SHEET_ID_HERE`
- The user should NEVER type a raw ID.

**If they say "create new":**
- Tell them: "Create a blank Google Sheet, name it anything (e.g., 'ContentForge Tracker'), then paste the URL here."

**After getting the sheet ID:**
- Remind: "Share this sheet with `{client_email from Step A}` as **Editor**."
- Run `sheets-tracker.py --action init --sheet-id {id}` to verify connection and create headers.
- If connection succeeds: "Sheet connected. Headers created."
- If it fails with permission error: "Can't access the sheet yet. Make sure you've shared it with `{client_email}` as Editor, then try again."

#### Step C: Get the Drive output folder URL (optional)

Ask: **"Paste your Google Drive folder URL for content delivery (or type 'skip' to deliver files in the conversation instead)"**

**If they paste a URL:**
- Extract folder ID: `https://drive.google.com/drive/folders/FOLDER_ID_HERE` → `FOLDER_ID_HERE`
- Remind: "Share this folder with `{client_email from Step A}` as **Editor**."
- Note: On personal Google accounts, Drive uploads may not work (service account storage quota limitation). If that happens, the pipeline saves files locally and delivers them in the conversation. Sheets tracking works regardless.

**If they type "skip":**
- Set `drive_output_folder_id` to empty string.
- Pipeline will save .docx locally and deliver in conversation.
- Tell them: "No problem. Content will be delivered directly in the conversation. You can add Drive delivery later."

#### Step D: Auto-fill the brand profile

```json
"google_integration": {
  "credentials_path": "~/.claude-marketing/google-credentials.json",
  "tracking_sheet_id": "<extracted from URL>",
  "tracking_sheet_tab": "ContentForge Tracking",
  "drive_output_folder_id": "<extracted from URL or empty>"
}
```

Save to the brand profile automatically. User never sees or edits this JSON.

#### Step E: Verify Knowledge Vault (Brand Files in Drive)

If Google integration was configured (Steps A-D completed), check whether the brand's knowledge files exist in the right Drive folder structure. This is critical — the pipeline uses these files for voice calibration, compliance checking, and content quality.

**Ask: "Paste the URL of your brand's Drive folder (the folder containing Brand-Guidelines, Guardrails, Reference-Content)"**

- Extract folder ID from URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
- This is a DIFFERENT folder from the output folder (Step C). This is where brand knowledge lives, not where content is delivered.

**Run the verification script:**
```
python scripts/drive-uploader.py \
  --action verify-structure \
  --folder-id {brand_folder_id} \
  --brand "{brand_name}" \
  --credentials {credentials_path}
```

**Parse the result and report to the user:**

**If `status: "ok"`:**
- All 3 subfolders exist with key files found.
- Show: "Brand knowledge vault verified:"
  - "Brand-Guidelines: {file_count} files (key: {key_file})"
  - "Guardrails: {file_count} files (key: {key_file})"
  - "Reference-Content: {file_count} files (key: {key_file})"

**If `status: "partial"` (folders exist but key files missing):**
- Show which files are missing with specific instructions:
  - "Brand-Guidelines folder exists but missing the brand profile JSON."
  - "Upload a file named `{Brand}-brand-profile.json` to the Brand-Guidelines folder."
- The pipeline CAN run without these — it just won't have full brand context. Tell the user: "You can start producing content now, but quality will improve significantly once these files are uploaded."

**If `status: "incomplete"` (subfolders missing):**
- Show exactly what to create:
  - "Your brand folder needs these subfolders: Brand-Guidelines/, Guardrails/, Reference-Content/"
  - "Create them in your Drive brand folder and upload the relevant files."
- Provide expected folder structure:
  ```
  {Brand Name}/
  ├── Brand-Guidelines/
  │   └── {Brand}-brand-profile.json (voice, tone, terminology)
  ├── Guardrails/
  │   └── {Brand}-guardrails.json (compliance rules, disclaimers)
  └── Reference-Content/
      └── {Brand}-reference-content.md (sample content for voice calibration)
  ```

**If the user says "skip" or doesn't have a brand folder yet:**
- Tell them: "No problem. The pipeline will use the voice/terminology settings from this brand setup. You can add Drive-based knowledge files later — they make the output significantly better."
- The pipeline runs without Drive knowledge files — it just relies on the brand profile JSON created during voice/terminology setup.

**Auto-fill the knowledge vault config:**

```json
"knowledge_vault_config": {
  "drive_folder_id": "<brand folder ID from URL>",
  "brand_guidelines_folder": "Brand-Guidelines/",
  "reference_content_folder": "Reference-Content/",
  "guardrails_folder": "Guardrails/"
}
```

Save to brand profile automatically. User never sees this.

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
| Knowledge vault | Verified (N files) / Partial / Not configured |

Ask: "Brand profile for [name] is ready. Would you like to:
- Start producing content? (`/create-content`)
- Generate a content brief? (`/content-brief`)
- Import additional guidelines from another source?
- Create a test piece to validate the voice settings?
- Check which connectors are active? (`/integrations`)"
