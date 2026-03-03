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

#### Step F: Key File Creation & Update

After verifying the knowledge vault (Step E), **always ask** whether the user wants to create, update, or keep their key files as-is. This applies to both new brands (files don't exist) and existing brands (files may be outdated or incomplete).

**Decision prompt — adapt based on Step E result:**

**If key files are missing (status: "partial" or "incomplete"):**
> "Some key files are missing from your brand folder. I can generate them for you by analyzing your brand's website, the information you've provided, and any reference files already in Drive. Want me to create them?"
>
> - **Yes, create them** → proceed to Generation Flow below
> - **No, I'll upload them myself** → skip to After Setup

**If all key files exist (status: "ok"):**
> "Your brand files are all present. Would you like to:"
>
> - **Review and update them** — I'll check the content, flag anything that looks outdated or incomplete, and offer to regenerate
> - **Keep them as-is** — skip to After Setup
> - **Start fresh** — regenerate all files from scratch using your website and the latest information

---

##### Generation Flow

This flow creates or updates the three key files: `{Brand}-brand-profile.json`, `{Brand}-guardrails.json`, and `{Brand}-reference-content.md`.

**Source 1: Brand website analysis**

Ask: **"What's the brand's website URL?"**

- If already provided in earlier steps or known from the brand profile → confirm: "I have `{url}` — is that correct?"
- WebFetch the following pages (skip any that 404):
  1. Homepage — extract tagline, value proposition, tone
  2. About/Company page — extract mission, history, leadership
  3. Services/Products page — extract offerings, terminology, positioning
  4. 2-3 recent blog posts — extract writing style, voice patterns, content structure
  5. Contact/Legal/Privacy page — extract compliance requirements, disclaimers

**Source 2: Existing reference files in Drive**

- If Step E found files in the brand folder (even if key files are missing), read what's already there.
- Other uploaded documents (PDFs, additional markdown, style guides) provide context.
- Use this to avoid contradicting what the user has already established.

**Source 3: Earlier setup information**

- Voice, tone, formality, terminology, and compliance information gathered in Steps 1-3 of brand setup (the interactive or imported settings).
- These take priority over website-inferred values — the user explicitly chose them.

**Source 4: Targeted follow-up questions**

After analyzing sources 1-3, ask the user **only about gaps** — don't re-ask things already answered. Typical gap questions:

- "I found these terms on your website: {list}. Should any be added to the approved or prohibited terminology list?"
- "Your website mentions {industry/regulatory body}. Are there specific compliance requirements I should include in the guardrails?"
- "I see your blog posts use {style pattern}. Should I match this in the reference content, or do you want a different style for new content?"
- "Any specific claims the brand should NEVER make? (e.g., 'guaranteed results', 'best in class')"
- "Who is the primary reader? What's their role and what do they care about?"

Only ask questions where the answer isn't already clear from the sources. If all information is available, confirm: "I have everything I need from your website and the settings above. Generating files now."

---

##### File Generation

**File 1: `{Brand}-brand-profile.json`**

Generate a complete brand profile following the `config/brand-registry-template.json` schema. Fill every field with real values derived from the sources above. Key sections:

- `brand_name`, `industry`, `company_info` — from website analysis
- `voice` — from setup steps + website writing style analysis
- `terminology` — from setup steps + website term extraction
- `citation_rules` — infer from industry (pharma → APA + PubMed priority, tech → IEEE, general → Chicago)
- `content_patterns` — from blog post analysis (structure, headings, lists, statistics usage)
- `seo_preferences` — reasonable defaults for the industry, ask for sitemap URL if available
- `target_audience` — from website messaging + user input
- `quality_thresholds` — use template defaults unless user specifies otherwise
- `google_integration` — copy from Step D configuration
- `knowledge_vault_config` — copy from Step E configuration

Show the user a summary of key extracted values before saving. Let them correct anything.

**File 2: `{Brand}-guardrails.json`**

Generate compliance guardrails. Structure:

```json
{
  "brand_name": "{Brand}",
  "prohibited_claims": ["..."],
  "required_disclaimers": ["..."],
  "compliance_notes": "...",
  "sensitive_topics": {
    "avoid": ["..."],
    "handle_with_care": ["..."]
  },
  "regulatory_requirements": {
    "industry_body": "...",
    "disclosure_requirements": ["..."],
    "review_required_for": ["..."]
  },
  "content_restrictions": {
    "max_superlatives_per_piece": 2,
    "require_evidence_for_statistics": true,
    "competitor_mention_policy": "neutral_comparison_only | never_mention | acknowledge_respectfully"
  }
}
```

- Infer from industry (pharma → FDA, HIPAA; financial → SEC, FINRA; healthcare → HIPAA)
- Include any disclaimers found on the website
- Add standard guardrails for the industry even if not explicitly mentioned (better safe than sorry)

**File 3: `{Brand}-reference-content.md`**

Generate a reference content document that demonstrates the brand's voice. Structure:

```markdown
# {Brand} — Reference Content

## Voice Calibration Sample

[A 300-500 word sample article in the brand's exact voice, tone, and style.
Written about a topic relevant to the brand's industry.
Uses the brand's approved terminology and follows the writing patterns
extracted from the website.]

## Style Patterns

- Sentence structure: {short/medium/long/mixed}
- Paragraph length: {short/medium/long}
- Uses questions: {yes/no}
- Uses contractions: {yes/no}
- Person: {first/second/third}
- Technical depth: {beginner/intermediate/advanced/expert}

## Terminology Quick Reference

### Always Use
| Instead of | Use |
|-----------|-----|
| {generic term} | {brand-preferred term} |

### Never Use
- {prohibited term 1}
- {prohibited term 2}

## Sample Headlines

1. {Example headline in brand voice — blog style}
2. {Example headline in brand voice — whitepaper style}
3. {Example headline in brand voice — article style}
```

- The voice calibration sample is the most important part — it's what the pipeline uses to match tone
- Base it on actual blog content from the website (rewrite in a fresh topic, not copy)
- Include 3-5 example headlines in different content type styles

---

##### Saving Generated Files

Save all files locally first:
```
~/.claude-marketing/{brand-slug}/Brand-Guidelines/{Brand}-brand-profile.json
~/.claude-marketing/{brand-slug}/Guardrails/{Brand}-guardrails.json
~/.claude-marketing/{brand-slug}/Reference-Content/{Brand}-reference-content.md
```

**Then attempt Drive upload** (if Google integration is configured):
- Try uploading each file to the corresponding subfolder in the brand's Drive folder
- If upload succeeds → confirm: "Files uploaded to Drive: {folder path}"
- If upload fails (storage quota) → tell user: "Files saved locally. Please upload them manually to your Drive brand folder. Here are the local paths: {paths}"

**After saving, re-run verify-structure** to confirm everything is in place.

---

##### Updating Existing Files

When the user chooses to **review and update** existing key files:

1. Download (read) the existing files from Drive
2. Analyze each file for completeness:
   - Are all fields populated with real values (not template placeholders)?
   - Does the voice profile match the current website?
   - Are guardrails appropriate for the industry?
   - Is the reference content a good representation of the brand voice?
3. Show a report:
   > **Brand Profile Review:**
   > - Voice: Complete / 2 fields still using template defaults
   > - Terminology: 12 preferred terms, 8 prohibited — looks good
   > - Guardrails: Missing required disclaimers for {industry}
   > - Reference Content: Voice sample is 150 words (recommend 300-500)
4. Ask: "Want me to fix the flagged issues? I'll regenerate only the incomplete sections."
5. If yes → regenerate only the sections that need updating, merge with existing data
6. Save updated files (same local + Drive flow as above)

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
| Key files | Generated / Updated / Pre-existing / Not created |

Ask: "Brand profile for [name] is ready. Would you like to:
- Start producing content? (`/create-content`)
- Generate a content brief? (`/content-brief`)
- Import additional guidelines from another source?
- Create a test piece to validate the voice settings?
- Update brand knowledge files? (re-run Step F to regenerate or refresh)
- Check which connectors are active? (`/integrations`)"
