---
name: cf-publish
description: Publish finished content to Webflow or WordPress via MCP connectors with preview, verification, and HTML export fallback
---

# Publish Content — ContentForge CMS Publishing

Push publication-ready content from the ContentForge pipeline directly to your CMS (Webflow or WordPress) via MCP connectors. Preview before publishing, verify post-publish, and fall back to HTML export when no connector is available.

## When to Use

Use `/cf-publish` when:
- You have a **finished, reviewed content piece** (Phase 8 complete, score >=7.0)
- You want to **publish directly** to Webflow or WordPress without copy-pasting
- You need to **schedule content** for a future publish date
- You want **post-publish verification** (URL live, meta tags correct, images loaded)
- You want an **HTML export** for manual upload when no CMS connector is configured

**Do NOT use for:**
- Content still in pipeline (must be Phase 8 complete)
- Content flagged for human review (score <5.0)
- Platforms other than Webflow/WordPress (use `/cf-social-adapt` for social media)

## What This Command Does

1. **Verify Connector** -- Check if Webflow or WordPress MCP connector is active
2. **Load Content** -- Pull finished content from Google Drive or local output
3. **Format for Platform** -- Convert markdown/docx to platform-specific HTML/blocks
4. **Preview** -- Show rendered preview with meta tags, slug, featured image
5. **Publish/Schedule** -- Push to CMS as draft, published, or scheduled
6. **Post-Publish Verification** -- Confirm URL is live, meta tags are correct, content renders properly
7. **Fallback** -- If no connector, generate standalone HTML file for manual upload

## Required Inputs

**Minimum Required:**
- **Content Source** -- Google Drive URL, local file path, or requirement ID (e.g., `REQ-001`)
- **Platform** -- `webflow` or `wordpress`
- **Status** -- `draft`, `publish`, or `schedule`

**Optional:**
- **Schedule Date** -- ISO date/time for scheduled publishing (required if status=schedule)
- **Collection/Category** -- Webflow collection slug or WordPress category
- **Featured Image** -- URL or local path to hero image
- **Author** -- Override default author
- **Tags** -- Comma-separated list of tags
- **Slug Override** -- Custom URL slug (defaults to SEO-optimized slug from Phase 6)

## How to Use

### Interactive Mode
```
/cf-publish
```
**Prompts you for:**
1. Content source (Drive URL, file path, or requirement ID)
2. Platform (Webflow / WordPress)
3. Publish status (draft / publish / schedule)
4. Preview confirmation before pushing

### Quick Mode
```
/cf-publish REQ-001 --platform=webflow --status=publish
```

### Schedule for Later
```
/cf-publish REQ-001 --platform=wordpress --status=schedule --date="2026-03-01T09:00:00"
```

### Publish from Google Drive
```
/cf-publish https://drive.google.com/file/d/ABC123 --platform=webflow --status=draft
```

## What Happens

### Step 1: Connector Verification (5-10 seconds)

Before attempting any CMS operation, verify the target connector is available.

**Check MCP connector status:**
```
Platform: webflow
Connector: Webflow MCP (https://mcp.webflow.com/sse)
Status: CHECKING...
```

**Case A: Connector Active**
```
Webflow MCP: CONNECTED
Site: acme-corp.webflow.io
Collections available: blog-posts, case-studies, resources
Proceeding with direct publish...
```

**Case B: Connector Not Found**
```
Webflow MCP: NOT CONNECTED

No Webflow connector detected in .mcp.json.
Falling back to HTML export mode.

To enable direct publishing, add the Webflow connector:
  /dm:connect webflow

Generating standalone HTML file for manual upload...
```

### Step 2: Load and Validate Content (10-15 seconds)

**Load content from source:**
- Read .docx or markdown from Google Drive or local output directory
- Extract metadata: title, meta description, slug, keywords, author, featured image
- Validate quality score >= 7.0 (refuse to publish unreviewed content)

**Validation checks:**
```
Content Validation
---------------------------------------------------
Title: "AI in Healthcare: 2026 Trends"        OK
Quality Score: 9.2/10                          OK
Status: Approved (Phase 8 Complete)            OK
Word Count: 1,947                              OK
Meta Title: 58 chars                           OK
Meta Description: 152 chars                    OK
SEO Slug: ai-in-healthcare-2026-trends         OK
Featured Image: hero-ai-healthcare.jpg         OK
---------------------------------------------------
All checks passed. Ready to format for Webflow.
```

**Rejection cases:**
- Quality score < 7.0: "Content has not passed quality review. Score: 4.8/10. Run the full pipeline first."
- No Phase 8 completion: "Content pipeline incomplete. Phase 8 (Output Manager) has not run."
- Missing meta tags: "Meta title and description are required. Run Phase 6 (SEO Optimizer) first."

### Step 3: Format for Target Platform (10-20 seconds)

Convert ContentForge output into platform-native format.

**Webflow Formatting:**
- Convert markdown headings to Webflow rich text blocks
- Map H1 to `name` field, body to `post-body` rich text field
- Set `slug`, `meta-title`, `meta-description` fields
- Upload featured image to Webflow assets, link to `main-image` field
- Map tags to Webflow multi-reference field
- Preserve inline links, bold, italic, lists, blockquotes

**WordPress Formatting:**
- Convert markdown to WordPress Gutenberg blocks (paragraph, heading, list, quote, image)
- Set `title`, `content`, `excerpt`, `slug`, `meta` fields
- Upload featured image via media endpoint, set as `featured_media`
- Map categories and tags to taxonomy terms
- Preserve shortcodes if present in original content
- Add Yoast/RankMath SEO meta if plugin detected

**Shared formatting rules:**
- Strip .docx formatting artifacts (extra whitespace, page breaks)
- Ensure all internal links use relative paths where possible
- Validate all image URLs are accessible (no broken images)
- Preserve citation formatting (footnotes or inline links based on platform preference)

### Step 4: Preview Before Publish

Show the user exactly what will be published before pushing.

```
PUBLISH PREVIEW
===================================================

Platform: Webflow (acme-corp.webflow.io)
Collection: blog-posts
Status: PUBLISH (goes live immediately)

---------------------------------------------------
URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends

Meta Title: AI in Healthcare: 2026 Trends and Predictions
Meta Description: Explore how AI is transforming healthcare in 2026,
  from diagnostic tools to patient care. Data-driven analysis with
  14 verified sources.

Featured Image: hero-ai-healthcare.jpg (1200x630, 245KB)
Author: ContentForge
Tags: AI, Healthcare, Technology Trends, 2026
Word Count: 1,947
---------------------------------------------------

Content Preview (first 300 characters):
"Multi-agent AI systems are changing how healthcare organizations
approach diagnostics, patient care, and operational efficiency. The
approach? Deploy specialized AI agents -- one for imaging analysis,
another for patient history, a third for treatment recommendations..."

===================================================

Proceed with publish? (yes / no / edit)
```

**User options:**
- `yes` -- Push to CMS
- `no` -- Cancel, return to command line
- `edit` -- Open content for last-minute edits before publish

### Step 5: Publish / Schedule / Draft (5-15 seconds)

**Publish (immediate):**
```
Publishing to Webflow...
API call: POST /collections/blog-posts/items
Status: 201 Created
Item ID: 6432a1b2c3d4e5f6
Live URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends
```

**Schedule (future date):**
```
Scheduling for 2026-03-01 09:00 UTC...
API call: POST /collections/blog-posts/items (draft=true, scheduled_at=2026-03-01T09:00:00Z)
Status: 201 Created
Scheduled Publish: March 1, 2026 at 9:00 AM UTC
Draft URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends (not live yet)
```

**Draft (no publish):**
```
Saving as draft...
API call: POST /collections/blog-posts/items (draft=true)
Status: 201 Created
Draft URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends (draft, not live)
Edit in Webflow: https://webflow.com/dashboard/sites/acme-corp/editor
```

### Step 6: Post-Publish Verification (10-20 seconds)

After publishing, verify the content is live and correct.

**Verification checks:**
```
Post-Publish Verification
===================================================
URL Accessible: GET https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends
  Status Code: 200 OK                                  PASS
  Response Time: 340ms                                  PASS

Meta Tags:
  <title>: "AI in Healthcare: 2026 Trends..."          PASS
  <meta name="description">: Present, 152 chars         PASS
  <meta property="og:title">: Present                   PASS
  <meta property="og:image">: Present                   PASS
  <link rel="canonical">: Present                       PASS

Content Integrity:
  H1 present: "AI in Healthcare: 2026 Trends"           PASS
  Word count matches: 1,947 (expected 1,947)            PASS
  Images loaded: 3/3                                    PASS
  Internal links valid: 5/5                             PASS

SEO Elements:
  URL slug correct: ai-in-healthcare-2026-trends        PASS
  Schema markup: Article (JSON-LD)                      PASS
  Robots meta: index, follow                            PASS

===================================================
All 12 checks passed. Content is live and verified.
```

**If verification fails:**
```
VERIFICATION WARNING
===================================================
URL Accessible: 200 OK                                  PASS
Meta Description: MISSING                               FAIL
  Expected: "Explore how AI is transforming..."
  Found: (empty)

Action: Meta description did not save correctly.
  Attempting fix via API PATCH...
  Fixed: Meta description updated.
  Re-verification: PASS
===================================================
```

### Step 7: Update Tracking Sheet

After successful publish:
```
Tracking Sheet Updated:
  Row: 5
  Status: "Published"
  Published URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends
  Published At: 2026-02-25 14:30:00
  Platform: Webflow
  Verification: All 12 checks passed
```

## Fallback: HTML Export Mode

When no CMS connector is available, generate a standalone HTML file.

### What Gets Generated

```
Output: .tmp/publish-exports/ai-in-healthcare-2026-trends.html

HTML Export includes:
- Full article content in clean, semantic HTML5
- Inline CSS for typography (portable, no external dependencies)
- Meta tags in <head> (title, description, OG tags, Twitter cards)
- Schema.org Article markup (JSON-LD)
- Featured image with alt text
- Responsive formatting (mobile-friendly)
- Copy-paste ready for any CMS
```

### HTML Export File Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AI in Healthcare: 2026 Trends and Predictions</title>
  <meta name="description" content="Explore how AI is transforming...">
  <meta property="og:title" content="AI in Healthcare: 2026 Trends...">
  <meta property="og:description" content="Explore how AI is transforming...">
  <meta property="og:image" content="hero-ai-healthcare.jpg">
  <script type="application/ld+json">
    { "@context": "https://schema.org", "@type": "Article", ... }
  </script>
</head>
<body>
  <article>
    <h1>AI in Healthcare: 2026 Trends and Predictions</h1>
    <!-- Full formatted article content -->
  </article>
</body>
</html>
```

### Manual Upload Instructions

```
HTML Export Complete
===================================================
File: .tmp/publish-exports/ai-in-healthcare-2026-trends.html
Size: 48 KB

Manual Upload Instructions:
1. Open your CMS dashboard
2. Create a new blog post / article
3. Switch to HTML/code view
4. Copy the contents of the <article> tag
5. Paste into the content editor
6. Copy meta title and description from the <head> section
7. Upload featured image separately
8. Set URL slug to: ai-in-healthcare-2026-trends
9. Preview and publish

Alternatively, connect your CMS for direct publishing:
  /dm:connect webflow
  /dm:connect wordpress
===================================================
```

## Output Example

**Successful Publish:**
```
CONTENTFORGE PUBLISH COMPLETE
===================================================

Content: AI in Healthcare: 2026 Trends
Platform: Webflow
Status: Published (LIVE)
URL: https://acme-corp.webflow.io/blog/ai-in-healthcare-2026-trends

Quality Score: 9.2/10
Word Count: 1,947
Meta Tags: All present and verified
Images: 3 loaded
Verification: 12/12 checks passed

Tracking Sheet: Updated (Row 5)
Published At: 2026-02-25 14:30:00

===================================================
Content is live and verified. No further action required.
```

## Error Handling

### CMS API Rate Limit
```
Error: 429 Too Many Requests
Action: Wait 60 seconds, retry (max 3 attempts)
If persistent: Save as draft, notify user to publish manually
```

### Authentication Expired
```
Error: 401 Unauthorized
Action: Prompt user to re-authenticate
  Webflow: Re-authorize at https://webflow.com/oauth/authorize
  WordPress: Refresh application password
```

### Content Too Large
```
Error: 413 Payload Too Large (WordPress limit: 2MB per post)
Action: Split content into parts or compress images
Fallback: Generate HTML export, notify user
```

### Duplicate Slug
```
Error: Slug "ai-in-healthcare-2026-trends" already exists
Action: Check if this is an update (v1.1 refresh) or duplicate
  If update: PATCH existing post (preserve URL, update content)
  If duplicate: Append "-2" to slug, warn user
```

### Image Upload Failure
```
Error: Featured image upload failed (timeout)
Action: Retry image upload (3 attempts)
Fallback: Publish without featured image, flag for manual fix
  "Published successfully but featured image failed to upload.
   Please upload hero-ai-healthcare.jpg manually in your CMS."
```

## Platform-Specific Notes

### Webflow
- Uses Collection Items API for blog posts
- Rich text field supports HTML content directly
- Images must be uploaded to Webflow Assets first, then referenced
- Publish requires site publish after item creation (API call to publish site)
- CMS items are draft by default; explicit publish step needed
- Rate limit: 60 requests per minute

### WordPress
- Uses REST API v2 (`/wp-json/wp/v2/posts`)
- Gutenberg blocks preferred over classic editor HTML
- Featured image uploaded via `/wp-json/wp/v2/media`, then linked by ID
- Categories and tags are taxonomy term IDs (lookup by name first)
- Supports `date` field for scheduling
- Application Passwords or OAuth for authentication
- Rate limit: Varies by host (typically 100-500 requests/minute)

## Requirements

### MCP Integrations (Optional but Recommended)
- **Webflow MCP** (`https://mcp.webflow.com/sse`) -- For direct Webflow publishing
- **WordPress** -- Via REST API (no MCP endpoint; uses HTTP connector or direct API)

### Environment
- Claude Code or Cowork (latest version)
- Content must have completed Phase 8 (Output Manager)
- Quality score >= 7.0

## Integration with Other Skills

**Before Publishing:**
- `/contentforge` -- Generate the content piece
- `/batch-process` -- Generate multiple pieces for bulk publishing
- `/content-refresh` -- Update old content before republishing

**After Publishing:**
- `/cf-social-adapt` -- Generate social media posts to promote the published article
- `/content-refresh` -- Schedule future refresh for evergreen content

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** -- Full content production pipeline
- **[/batch-process](../batch-process/SKILL.md)** -- Parallel content production
- **[/content-refresh](../content-refresh/SKILL.md)** -- Update existing content
- **[/cf-social-adapt](../cf-social-adapt/SKILL.md)** -- Social media adaptation

---

**Version:** 3.1.0
**Agent:** Output Manager (Phase 8) + CMS Publisher utility
**Utilities:** cms-publisher.md
**Platforms:** Webflow, WordPress
**Fallback:** HTML export for manual upload
