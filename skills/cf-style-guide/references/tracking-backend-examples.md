# cf-style-guide — Step G tracking backend example transcripts

Verbatim examples moved out of `skills/cf-style-guide/SKILL.md` Step G ("Tracking & Delivery
Backend") to keep the skill body within the ~500-line Agent Skills guidance.

## Three-option menu presentation

**Present the user with three options (only when G.0 found nothing):**

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

## Example Output (backend configured)

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

To switch backends later: /contentforge:cf-switch-backend
================================================================
```
