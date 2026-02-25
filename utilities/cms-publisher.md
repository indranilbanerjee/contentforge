# Utility: CMS Publisher

**Purpose:** Handle the end-to-end logic for publishing ContentForge content to external CMS platforms (Webflow, WordPress) via MCP connectors, with fallback to HTML export when no connector is available.

---

## Responsibilities

1. **Connector Check** -- Verify target CMS connector is active before attempting publish
2. **Content Formatting** -- Convert ContentForge output (markdown/docx) to platform-native format
3. **API Call** -- Push formatted content to the CMS via MCP connector or REST API
4. **Post-Publish Verification** -- Confirm the content is live, meta tags are correct, images loaded
5. **Tracking Update** -- Update the ContentForge tracking sheet with publish status and URL
6. **Fallback (HTML Export)** -- Generate standalone HTML file for manual upload when no connector is available

---

## How It Works

### Publish Flow (Happy Path)

```
1. CONNECTOR CHECK
   Is the target CMS connector active in .mcp.json?
   ├── YES → Proceed to step 2
   └── NO  → Jump to FALLBACK (step 6)

2. CONTENT FORMATTING
   Load content from Google Drive or local output
   ├── Extract: title, body, meta tags, slug, featured image, tags, author
   ├── Convert markdown → platform-native HTML/blocks
   └── Validate: all required fields present, quality score >= 7.0

3. PREVIEW
   Show user what will be published
   ├── URL, meta tags, featured image, content preview
   └── User confirms: yes / no / edit

4. API CALL
   Push content to CMS
   ├── Webflow: POST /collections/{slug}/items
   ├── WordPress: POST /wp-json/wp/v2/posts
   ├── Handle: draft / publish / schedule status
   └── Capture: item ID, live URL, API response

5. POST-PUBLISH VERIFICATION
   Confirm content is live and correct
   ├── GET the published URL → 200 OK?
   ├── Check meta tags: title, description, OG tags, canonical
   ├── Check content: H1 present, word count matches, images loaded
   ├── Check SEO: slug correct, robots meta, schema markup
   └── If any check fails → attempt auto-fix via PATCH, then re-verify

6. TRACKING UPDATE
   Update ContentForge tracking sheet
   ├── Status: "Published" / "Scheduled" / "Draft"
   ├── Published URL
   ├── Published timestamp
   ├── Platform name
   └── Verification result (pass/fail with details)

FALLBACK (if no connector):
   Generate standalone HTML file
   ├── Semantic HTML5 with inline CSS
   ├── Meta tags in <head>
   ├── Schema.org JSON-LD
   ├── Save to .tmp/publish-exports/
   └── Provide manual upload instructions
```

---

## Data Structures

### PublishRequest

```python
publish_request = {
    "content_source": {
        "type": "drive_url | local_path | requirement_id",
        "value": "https://drive.google.com/file/d/ABC123 | ./output/article.md | REQ-001"
    },
    "platform": "webflow | wordpress",
    "status": "draft | publish | schedule",
    "schedule_date": "2026-03-01T09:00:00Z",  # Required if status=schedule, null otherwise
    "collection": "blog-posts",                 # Webflow collection slug or WordPress category
    "featured_image": {
        "source": "https://example.com/hero.jpg | ./assets/hero.jpg",
        "alt_text": "AI-powered diagnostic tools in a modern hospital setting"
    },
    "author": "ContentForge",                   # Override default author
    "tags": ["AI", "Healthcare", "2026"],
    "slug_override": null,                      # null = use SEO-optimized slug from Phase 6
    "metadata": {
        "requirement_id": "REQ-001",
        "quality_score": 9.2,
        "word_count": 1947,
        "brand": "AcmeMed",
        "content_type": "article"
    }
}
```

### PublishResponse

```python
publish_response = {
    "status": "success | failed | fallback",
    "platform": "webflow | wordpress | html_export",
    "publish_status": "published | draft | scheduled",
    "item_id": "6432a1b2c3d4e5f6",             # CMS item ID
    "live_url": "https://acme-corp.webflow.io/blog/ai-healthcare-2026",
    "published_at": "2026-02-25T14:30:00Z",
    "verification": {
        "url_accessible": true,
        "status_code": 200,
        "meta_title_present": true,
        "meta_description_present": true,
        "og_tags_present": true,
        "canonical_present": true,
        "h1_present": true,
        "word_count_match": true,
        "images_loaded": true,
        "internal_links_valid": true,
        "slug_correct": true,
        "schema_markup_present": true,
        "robots_meta_correct": true,
        "checks_passed": 12,
        "checks_total": 12,
        "all_passed": true
    },
    "tracking_update": {
        "sheet_updated": true,
        "row": 5,
        "status_set": "Published",
        "url_recorded": true
    },
    "errors": [],
    "warnings": []
}
```

### FallbackResponse (HTML Export)

```python
fallback_response = {
    "status": "fallback",
    "platform": "html_export",
    "reason": "No Webflow MCP connector detected in .mcp.json",
    "export_path": ".tmp/publish-exports/ai-in-healthcare-2026-trends.html",
    "file_size_kb": 48,
    "contents": {
        "semantic_html5": true,
        "inline_css": true,
        "meta_tags": true,
        "og_tags": true,
        "schema_json_ld": true,
        "responsive": true
    },
    "manual_instructions": [
        "Open your CMS dashboard",
        "Create a new blog post / article",
        "Switch to HTML/code view",
        "Copy the contents of the <article> tag",
        "Paste into the content editor",
        "Copy meta title and description from the <head> section",
        "Upload featured image separately",
        "Set URL slug to: ai-in-healthcare-2026-trends",
        "Preview and publish"
    ],
    "connector_setup_command": "/dm:connect webflow"
}
```

---

## Webflow-Specific Logic

### Connector Detection

```python
def check_webflow_connector():
    """Check if Webflow MCP connector is active."""
    # Look for Webflow in .mcp.json
    mcp_config = load_mcp_json()

    if 'webflow' in mcp_config:
        endpoint = mcp_config['webflow'].get('url', '')
        if 'mcp.webflow.com' in endpoint:
            return {
                'connected': True,
                'endpoint': endpoint,
                'type': 'http_mcp'
            }

    return {
        'connected': False,
        'endpoint': None,
        'setup_command': '/dm:connect webflow'
    }
```

### Content Formatting for Webflow

```python
def format_for_webflow(content, metadata):
    """Convert ContentForge output to Webflow CMS item format."""
    return {
        'fieldData': {
            'name': metadata['title'],
            'slug': metadata['slug'],
            'post-body': markdown_to_webflow_richtext(content['body']),
            'meta-title': metadata['meta_title'],
            'meta-description': metadata['meta_description'],
            'main-image': upload_image_to_webflow_assets(
                metadata['featured_image']
            ),
            'author': metadata.get('author', 'ContentForge'),
            'tags': metadata.get('tags', []),
            'publish-date': metadata.get('publish_date', datetime.now().isoformat())
        },
        'isDraft': metadata['status'] != 'publish'
    }
```

### Webflow API Flow

```
1. Upload featured image → POST /assets (get asset ID)
2. Create CMS item → POST /collections/{collection_id}/items
3. If status=publish → POST /sites/{site_id}/publish
4. Verify → GET published URL

Rate limit: 60 requests/minute
Auth: OAuth 2.0 via MCP connector (no manual token management)
```

### Webflow Gotchas

- **Publish is a two-step process.** Creating a CMS item does NOT make it live. You must also trigger a site publish via the API.
- **Rich text field limits.** Webflow rich text does not support all HTML. Unsupported elements (iframes, custom scripts) are stripped.
- **Image upload required before reference.** You cannot reference an external image URL directly in a CMS item. Upload to Webflow Assets first.
- **Slug uniqueness.** Webflow rejects duplicate slugs within a collection. Check before creating.

---

## WordPress-Specific Logic

### Connector Detection

```python
def check_wordpress_connector():
    """Check if WordPress REST API is reachable."""
    # WordPress does not have an MCP endpoint
    # Check for configured WordPress URL in .env or config
    wp_url = os.getenv('WORDPRESS_URL')
    wp_auth = os.getenv('WORDPRESS_APP_PASSWORD')

    if wp_url and wp_auth:
        # Test API endpoint
        response = requests.get(
            f"{wp_url}/wp-json/wp/v2/posts?per_page=1",
            auth=('username', wp_auth),
            timeout=10
        )
        if response.status_code == 200:
            return {
                'connected': True,
                'endpoint': f"{wp_url}/wp-json/wp/v2",
                'type': 'rest_api'
            }

    return {
        'connected': False,
        'endpoint': None,
        'setup_instructions': [
            'Set WORDPRESS_URL in .env',
            'Set WORDPRESS_APP_PASSWORD in .env',
            'Create Application Password in WordPress admin: Users > Profile > Application Passwords'
        ]
    }
```

### Content Formatting for WordPress

```python
def format_for_wordpress(content, metadata):
    """Convert ContentForge output to WordPress REST API format."""

    # Convert markdown to Gutenberg blocks
    gutenberg_content = markdown_to_gutenberg_blocks(content['body'])

    post_data = {
        'title': metadata['title'],
        'content': gutenberg_content,
        'excerpt': metadata['meta_description'],
        'slug': metadata['slug'],
        'status': map_status(metadata['status']),  # draft | publish | future
        'meta': {
            '_yoast_wpseo_title': metadata['meta_title'],
            '_yoast_wpseo_metadesc': metadata['meta_description']
        }
    }

    # Handle scheduled publishing
    if metadata['status'] == 'schedule' and metadata.get('schedule_date'):
        post_data['status'] = 'future'
        post_data['date'] = metadata['schedule_date']

    # Handle categories (lookup by name, get ID)
    if metadata.get('collection'):
        category_id = lookup_category_id(metadata['collection'])
        if category_id:
            post_data['categories'] = [category_id]

    # Handle tags (lookup by name, create if missing)
    if metadata.get('tags'):
        tag_ids = lookup_or_create_tags(metadata['tags'])
        post_data['tags'] = tag_ids

    return post_data
```

### WordPress API Flow

```
1. Upload featured image → POST /wp-json/wp/v2/media (get media ID)
2. Create post → POST /wp-json/wp/v2/posts (include featured_media: media_id)
3. If status=publish → post goes live immediately
4. If status=future → WordPress auto-publishes at scheduled date
5. Verify → GET published URL

Auth: Application Passwords (Basic Auth) or OAuth 2.0
Rate limit: Varies by host (typically 100-500 req/min)
```

### WordPress Gotchas

- **Gutenberg vs Classic Editor.** REST API v2 expects Gutenberg blocks by default. If Classic Editor plugin is active, raw HTML in `content` field works.
- **Yoast/RankMath meta.** SEO plugin meta fields vary. Yoast uses `_yoast_wpseo_title`, RankMath uses `rank_math_title`. Detect which plugin is active.
- **Category/Tag IDs.** WordPress requires numeric IDs, not names. Lookup by slug first: `GET /wp-json/wp/v2/categories?slug=healthcare`.
- **Featured image is separate.** Upload image via media endpoint FIRST, then reference its ID in the post's `featured_media` field.
- **Application Passwords.** Created in WordPress admin under Users > Profile. Each password is tied to a user account.

---

## Fallback Behavior (HTML Export)

### When Fallback Triggers

```python
def should_fallback(platform):
    """Determine if fallback to HTML export is needed."""
    if platform == 'webflow':
        connector = check_webflow_connector()
        return not connector['connected']
    elif platform == 'wordpress':
        connector = check_wordpress_connector()
        return not connector['connected']
    return True  # Unknown platform always falls back
```

### HTML Export Generation

```python
def generate_html_export(content, metadata):
    """Generate standalone HTML file for manual CMS upload."""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{metadata['meta_title']}</title>
  <meta name="description" content="{metadata['meta_description']}">
  <meta property="og:title" content="{metadata['meta_title']}">
  <meta property="og:description" content="{metadata['meta_description']}">
  <meta property="og:type" content="article">
  <meta property="og:image" content="{metadata.get('featured_image', '')}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{metadata['meta_title']}">
  <meta name="twitter:description" content="{metadata['meta_description']}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{metadata['title']}",
    "description": "{metadata['meta_description']}",
    "author": {{
      "@type": "Organization",
      "name": "{metadata.get('brand', 'ContentForge')}"
    }},
    "datePublished": "{datetime.now().isoformat()}"
  }}
  </script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6;
           color: #333; }}
    h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.5rem; margin-top: 2rem; }}
    h3 {{ font-size: 1.25rem; margin-top: 1.5rem; }}
    p {{ margin-bottom: 1rem; }}
    blockquote {{ border-left: 4px solid #ddd; padding-left: 1rem; color: #555; }}
    a {{ color: #0066cc; }}
    img {{ max-width: 100%; height: auto; }}
  </style>
</head>
<body>
  <article>
    <h1>{metadata['title']}</h1>
    {markdown_to_html(content['body'])}
  </article>
</body>
</html>"""

    # Save to .tmp/publish-exports/
    filename = f"{metadata['slug']}.html"
    filepath = f".tmp/publish-exports/{filename}"
    os.makedirs('.tmp/publish-exports', exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    return filepath
```

### What the Export Includes

| Component | Included | Notes |
|-----------|----------|-------|
| Article content | Yes | Full formatted HTML |
| Inline CSS | Yes | Portable, no external dependencies |
| Meta title + description | Yes | In `<head>` for copy-paste |
| Open Graph tags | Yes | For social sharing preview |
| Twitter Card tags | Yes | For Twitter/X link previews |
| Schema.org JSON-LD | Yes | Article structured data |
| Featured image | Reference only | User uploads separately |
| Responsive layout | Yes | Mobile-friendly max-width |

---

## Error Handling

### API Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| 401 Unauthorized | Auth expired or invalid | Prompt re-authentication |
| 403 Forbidden | Insufficient permissions | Check API key/token scope |
| 404 Not Found | Collection or endpoint missing | Verify collection slug, API URL |
| 409 Conflict | Duplicate slug | Append "-2" or update existing |
| 413 Payload Too Large | Content exceeds size limit | Compress images, split content |
| 429 Too Many Requests | Rate limited | Wait 60s, retry (max 3 attempts) |
| 500 Internal Server Error | CMS server issue | Retry with backoff (30s, 60s, 120s) |
| Timeout | Network or CMS slowness | Retry once, then fallback to HTML |

### Retry Strategy

```python
def publish_with_retry(publish_fn, max_retries=3):
    """Execute publish with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = publish_fn()
            if response.status_code in [200, 201]:
                return response
            elif response.status_code == 429:
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s
                time.sleep(wait)
            elif response.status_code >= 500:
                wait = 30 * (2 ** attempt)  # 30s, 60s, 120s
                time.sleep(wait)
            else:
                return response  # Client error, don't retry
        except requests.Timeout:
            if attempt < max_retries - 1:
                time.sleep(30)
            else:
                return None  # Trigger fallback

    return None  # All retries exhausted, trigger fallback
```

---

## Usage Notes

### From cf-publish Skill

The `/cf-publish` skill calls this utility's logic in sequence:

```python
# Step 1: Check connector
connector = check_connector(platform)

if not connector['connected']:
    # Fallback path
    export_path = generate_html_export(content, metadata)
    display_manual_instructions(export_path)
    return fallback_response

# Step 2: Format content
formatted = format_for_platform(platform, content, metadata)

# Step 3: Preview
preview = generate_preview(formatted, platform)
user_confirms = display_preview(preview)

if not user_confirms:
    return cancelled_response

# Step 4: Publish
response = publish_with_retry(
    lambda: push_to_cms(platform, formatted)
)

# Step 5: Verify
verification = verify_published_content(response['live_url'])

# Step 6: Update tracking
update_tracking_sheet(metadata['requirement_id'], response)

return publish_response
```

### From Output Manager Agent

The Output Manager (Phase 8) can optionally call the CMS publisher after Google Drive upload if the user has configured auto-publish in their brand profile:

```python
if brand_profile.get('auto_publish', {}).get('enabled', False):
    platform = brand_profile['auto_publish']['platform']
    status = brand_profile['auto_publish']['default_status']  # Usually 'draft'
    cms_publisher.publish(content, metadata, platform, status)
```

---

## Benefits

1. **Zero copy-paste publishing** -- Content goes from pipeline to CMS in one step
2. **Post-publish verification** -- Catches meta tag issues, broken images, and formatting problems before readers see them
3. **Graceful degradation** -- No connector? HTML export with complete metadata, ready for manual upload
4. **Platform-native formatting** -- Webflow rich text and WordPress Gutenberg blocks, not generic HTML
5. **Tracking integration** -- Published URL and status automatically recorded in the ContentForge tracking sheet

---

## Implementation Checklist

- [ ] Connector detection for Webflow MCP (`https://mcp.webflow.com/sse`)
- [ ] Connector detection for WordPress REST API (env vars)
- [ ] Markdown to Webflow rich text converter
- [ ] Markdown to WordPress Gutenberg block converter
- [ ] Image upload handler (Webflow Assets API, WordPress Media API)
- [ ] Preview generation with meta tags and content snippet
- [ ] Publish API call with draft/publish/schedule support
- [ ] Post-publish verification (12-point checklist)
- [ ] Auto-fix for common verification failures (missing meta tags)
- [ ] Retry logic with exponential backoff (3 attempts)
- [ ] HTML export fallback generator
- [ ] Manual upload instruction generator
- [ ] Tracking sheet update integration
- [ ] Duplicate slug detection and handling
- [ ] Error logging and user-facing error messages

---

## Version History

- **v2.1.0**: Initial implementation with Webflow and WordPress support, HTML fallback
- Future: Notion publishing, HubSpot CMS, Ghost CMS, Medium API

---

**The CMS publisher eliminates the last manual step in the content pipeline** -- taking content from "approved in Google Drive" to "live on your website" without leaving the ContentForge workflow.
