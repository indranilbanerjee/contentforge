---
description: Publish finished content to Webflow or WordPress with preview, verification, and HTML export fallback
argument-hint: "<content source> --platform=<webflow|wordpress> [--status=draft|publish|schedule]"
---

# Publish

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Push publication-ready content from the ContentForge pipeline directly to your CMS (Webflow or WordPress) via MCP connectors. Preview before publishing, verify post-publish, and fall back to HTML export when no connector is available.

## Trigger

User runs `/publish` or asks to publish, push, or deploy content to a CMS platform.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Content source** — the finished piece to publish, provided as:
   - Google Drive URL
   - Local file path
   - Requirement ID (e.g., `REQ-001`)

2. **Platform** — `webflow` or `wordpress`

3. **Publish status** — one of:
   - `draft` — save as draft for review
   - `publish` — publish immediately
   - `schedule` — schedule for a specific date/time (requires ISO date)

4. **Additional options** (optional):
   - Schedule date (ISO format, e.g., `2026-03-15T09:00:00`)
   - Collection or category (Webflow collection slug, WordPress category)
   - Featured image (URL or local path)
   - Author override
   - Tags (comma-separated)
   - Custom URL slug (defaults to SEO-optimized slug from Phase 6)

## Prerequisites

- Content must have completed Phase 8 (Reviewer) with a score of 7.0 or above
- Content flagged for human review (score below 5.0) cannot be auto-published

## Process

### 1. Verify Connector

**If ~~CMS connector is active (Webflow or WordPress):**
- Confirm connection is live
- Retrieve available collections/categories
- Proceed to publishing flow

**If no connector is available:**
- Notify the user and offer alternatives:
  - Set up the connector: `/connect webflow` or `/connect wordpress`
  - Generate HTML export for manual upload (proceed to fallback)

### 2. Load Content
- Pull finished content from the specified source
- Extract metadata: title, meta description, keywords, featured image, author
- Verify quality score meets publishing threshold

### 3. Format for Platform

**Webflow:**
- Convert to Webflow-compatible rich text
- Map headings, images, links, and embeds
- Handle custom fields and CMS collections

**WordPress:**
- Convert to WordPress blocks (Gutenberg) or classic HTML
- Map categories and tags
- Handle featured image and excerpt

### 4. Preview

Show the user a formatted preview:
- Title and slug
- Meta title and description
- Featured image
- First 500 characters of body
- Categories/tags
- Scheduled date (if applicable)

Ask: "Does this look correct? Publish now, save as draft, or make changes?"

### 5. Publish or Schedule
- Push content to the CMS with selected status
- Return the live URL (or draft preview URL)

### 6. Post-Publish Verification
- Confirm the URL is accessible
- Verify meta tags rendered correctly
- Check that images loaded
- Validate structured data (if applicable)
- Report any issues

### Fallback: HTML Export

When no CMS connector is available:
- Generate a standalone HTML file with:
  - Full content with proper formatting
  - Inline styles for consistent rendering
  - Meta tags in the `<head>`
  - Open Graph and Twitter Card tags
  - Schema markup (Article schema)
- Save to local output directory
- Provide copy-paste-ready content for manual upload

## Output

| Field | Value |
|-------|-------|
| Platform | Webflow / WordPress / HTML Export |
| Status | Published / Draft / Scheduled |
| URL | Live URL or preview link |
| Quality Score | Composite score from Phase 7 |
| Meta Title | SEO-optimized title |
| Meta Description | Click-optimized description |

## After Publishing

Ask: "Would you like me to:
- Create social media posts to promote this? (`/social-adapt`)
- Submit the URL to Google Search Console for indexing?
- Set up rank monitoring for the target keywords? (use Digital Marketing Pro)
- Publish to another platform?
- Schedule the next content piece?"
