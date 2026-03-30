---
name: cf-integrations
description: "Show which MCP connectors are active, which are available, and which ContentForge workflows each connector enables. Integration status dashboard."
effort: low
---

# Integration Status Dashboard

Show the complete integration status for your ContentForge installation — connected vs available connectors, grouped by category, with workflow impact analysis and quick-win recommendations.

## When to Use

Use `/cf:integrations` when:
- You just installed ContentForge and want to see what's connected out of the box
- You're troubleshooting why a skill can't reach an external service
- You want to know which connectors to add next for maximum workflow coverage
- You need a quick overview before onboarding a new team member
- You're planning which integrations to set up for a new project

## What This Command Does

1. **Scan All Connectors** — Check 22 connectors across 12 categories against your current configuration
2. **Build Status Dashboard** — Group results by category with clear connected/available distinction
3. **Calculate Coverage** — Show X of Y connectors active with percentage
4. **Recommend Quick Wins** — Highlight the top 3 connectors to add based on workflow impact
5. **Surface Category Gaps** — Identify entire categories with zero coverage
6. **Provide Next Steps** — For each available connector, show what it takes to connect

## Required Inputs

**Optional:**
- **Category filter** — Show only a specific category (e.g., `--category=seo`)
- **Show filter** — `connected`, `available`, or `all` (default: `all`)

## How to Use

### Basic Usage (Full Dashboard)
```
/cf:integrations
```
Shows the complete status across all 12 categories.

### Filter by Category
```
/cf:integrations --category=cms
```
Shows only CMS connectors (Webflow, WordPress, HubSpot CMS).

### Show Only Connected
```
/cf:integrations --show=connected
```
Lists only the connectors that are currently active.

### Show Only Available (Not Connected)
```
/cf:integrations --show=available
```
Lists connectors you could add, with setup effort and workflow impact for each.

## What Happens

### Step 1: Connector Status Check (5-10 seconds)

Run the connector status script to scan all known connectors:

```
python3 scripts/connector-status.py --action status
```

This checks:
- `.mcp.json` for HTTP connectors (7 pre-configured: Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar; plus Ahrefs, Similarweb when user-added)
- Environment variables for npx connectors (Google Sheets, Google Drive, WordPress, Semrush, DeepL, etc.)
- Returns JSON with connected/available status per connector, grouped by category

### Step 2: Format Dashboard by Category

Organize results into a visual dashboard. Each category shows:
- Category name and description
- Connected connectors (with check mark)
- Available connectors (with setup type indicator)

**Dashboard Format:**
```
===========================================================
  ContentForge Integration Dashboard
  Connected: 7 of 22 (32%)
===========================================================

  KNOWLEDGE BASE
  Store requirements, brand docs, reference material
  -----------------------------------------------------------
  [connected]  Notion (HTTP) — content requirements, brand docs, editorial calendars
  [available]  Confluence (npx) — team wikis, brand guidelines, knowledge bases

  DESIGN
  Visual design and creative assets
  -----------------------------------------------------------
  [connected]  Canva (HTTP) — featured images, social graphics, infographics, brand kit
  [connected]  Figma (HTTP) — design assets, illustrations, visual elements

  CMS
  Content management and publishing
  -----------------------------------------------------------
  [connected]  Webflow (HTTP) — publish articles, blog posts, landing pages to CMS
  [available]  WordPress (npx) — publish posts, pages, manage categories and metadata
  [available]  HubSpot CMS (npx) — blog posts, landing pages, email content

  ...
===========================================================
```

### Step 3: Highlight Quick Wins

Identify the top 3 connectors to add next based on workflow impact. The priority ranking:

1. **Notion** — Powers 6 skills (contentforge, batch-process, content-refresh, cf-brief, cf-audit, cf-style-guide). If Notion is not connected, this is always the #1 recommendation.
2. **Google Sheets** — Powers 3 skills (batch-process, cf-analytics, cf-audit). Critical for batch requirement intake and quality tracking.
3. **CMS (Webflow or WordPress)** — Powers 3 skills (cf-publish, contentforge, batch-process). Required for end-to-end publish workflow.
4. **Design (Canva or Figma)** — Powers 3 skills (contentforge, batch-process, cf-social-adapt). Featured images and social graphics.
5. **SEO (Ahrefs or Similarweb)** — Powers 3 skills (cf-brief, cf-audit, content-refresh). Keyword data and competitive analysis.

Only connectors that are NOT already connected appear as quick wins.

**Quick Wins Format:**
```
-----------------------------------------------------------
  QUICK WINS — Top connectors to add next
-----------------------------------------------------------

  1. Google Sheets (npx)
     Unlocks: /batch-process requirement intake, /cf:analytics tracking, /cf:audit data
     Setup: Set GOOGLE_APPLICATION_CREDENTIALS env var
     Impact: HIGH — enables batch content production at scale

  2. WordPress (npx)
     Unlocks: /cf:publish direct publishing, end-to-end content pipeline
     Setup: Set WORDPRESS_SITE_URL and WORDPRESS_AUTH_TOKEN env vars
     Impact: HIGH — publish directly from ContentForge without manual copy-paste

  3. Ahrefs (HTTP)
     Unlocks: /cf:brief keyword research, /cf:audit content gap analysis
     Setup: Already in .mcp.json — just use a skill that needs it
     Impact: MEDIUM — data-driven content briefs with real keyword volumes
```

### Step 4: Show Coverage Summary

Present the high-level numbers:

```
-----------------------------------------------------------
  COVERAGE SUMMARY
-----------------------------------------------------------

  Total connectors:     22
  Connected:            7 (32%)
  Available:            15

  HTTP connectors:      9 total, 7 connected (78%)
  npx connectors:       13 total, 0 connected (0%)

  Categories covered:   6 of 12 (50%)
  Categories empty:     6 (spreadsheets, file-storage, social-media, analytics,
                           translation, seo)
```

### Step 5: Provide Next Steps

Based on the dashboard results, present actionable next steps:

```
-----------------------------------------------------------
  NEXT STEPS
-----------------------------------------------------------

  1. Connect Google Sheets for batch requirement intake:
     /cf:connect google-sheets

  2. Connect WordPress for direct publishing:
     /cf:connect wordpress

  3. See setup guide for any connector:
     /cf:connect <name>

  4. Full connector reference:
     See CONNECTORS.md
```

## Output

The complete dashboard includes these sections:

| Section | Description |
|---------|------------|
| **Coverage Summary** | X of Y connected, percentage, HTTP vs npx breakdown |
| **Connected Integrations** | Grouped by category, showing transport type and skills enabled |
| **Available Integrations** | Grouped by category, showing setup effort (HTTP = easy, npx = moderate) |
| **Quick Wins** | Top 3 recommended connectors ranked by workflow impact |
| **Category Gaps** | Categories with zero connectors configured |
| **Next Steps** | Actionable commands to connect recommended integrations |

## Output Example

**Scenario:** Fresh install with only HTTP connectors from `.mcp.json`

```
===========================================================
  ContentForge Integration Dashboard
  Connected: 7 of 22 (32%)
===========================================================

  KNOWLEDGE BASE — Store requirements, brand docs, reference material
  -----------------------------------------------------------
  [connected]  Notion (HTTP)
               content requirements, brand docs, editorial calendars
               Skills: /contentforge, /batch-process, /content-refresh, /cf:brief, /cf:audit, /cf:style-guide
  [available]  Confluence (npx)
               team wikis, brand guidelines, knowledge bases
               Needs: CONFLUENCE_URL, CONFLUENCE_TOKEN

  DESIGN — Visual design and creative assets
  -----------------------------------------------------------
  [connected]  Canva (HTTP)
               featured images, social graphics, infographics, brand kit
               Skills: /contentforge, /batch-process, /cf:social-adapt
  [connected]  Figma (HTTP)
               design assets, illustrations, visual elements
               Skills: /contentforge, /cf:social-adapt

  CMS — Content management and publishing
  -----------------------------------------------------------
  [connected]  Webflow (HTTP)
               publish articles, blog posts, landing pages to CMS
               Skills: /cf:publish, /contentforge, /batch-process
  [available]  WordPress (npx)
               publish posts, pages, manage categories and metadata
               Needs: WORDPRESS_SITE_URL, WORDPRESS_AUTH_TOKEN
  [available]  HubSpot CMS (npx)
               blog posts, landing pages, email content
               Needs: HUBSPOT_ACCESS_TOKEN

  CHAT — Team messaging and notifications
  -----------------------------------------------------------
  [connected]  Slack (HTTP)
               batch status notifications, content approval alerts, team updates
               Skills: /batch-process, /cf:publish, /cf:calendar

  EMAIL — Email communication
  -----------------------------------------------------------
  [connected]  Gmail (HTTP)
               share drafts, deliver finished content, review notifications
               Skills: /batch-process, /cf:publish

  CALENDAR — Calendar and scheduling
  -----------------------------------------------------------
  [connected]  Google Calendar (HTTP)
               content calendar events, publishing deadlines, review reminders
               Skills: /cf:calendar, /batch-process

  SPREADSHEETS — Data intake and requirement management
  -----------------------------------------------------------
  [available]  Google Sheets (npx)
               batch requirement intake, content tracking, quality score history
               Needs: GOOGLE_APPLICATION_CREDENTIALS

  FILE STORAGE — File storage and brand knowledge
  -----------------------------------------------------------
  [available]  Google Drive (npx)
               brand knowledge vault, reference docs, output delivery
               Needs: GOOGLE_APPLICATION_CREDENTIALS

  SEO — Search engine optimization
  -----------------------------------------------------------
  [available]  Ahrefs (HTTP)
               keyword research, backlink data, content gap analysis
  [available]  Similarweb (HTTP)
               traffic analysis, competitor content benchmarks
  [available]  Semrush (npx)
               keyword research, site audit, position tracking
               Needs: SEMRUSH_API_KEY

  TRANSLATION — Translation and localization
  -----------------------------------------------------------
  [available]  DeepL (npx)
               professional translation, 30+ languages, brand voice preservation
               Needs: DEEPL_API_KEY
  [available]  Sarvam AI (npx)
               22 Indian languages specialist
               Needs: SARVAM_API_KEY

  SOCIAL MEDIA — Social media publishing
  -----------------------------------------------------------
  [available]  Twitter/X (npx)
               post tweets, threads, media uploads
               Needs: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
  [available]  LinkedIn (npx)
               post articles, share updates, company pages
               Needs: LINKEDIN_ACCESS_TOKEN
  [available]  Instagram (npx)
               publish images/carousels, insights
               Needs: INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID

  ANALYTICS — Website analytics
  -----------------------------------------------------------
  [available]  Google Analytics (npx)
               content traffic, engagement, conversions
               Needs: GA_PROPERTY_ID, GOOGLE_APPLICATION_CREDENTIALS
  [available]  Google Search Console (npx)
               rankings, impressions, CTR for content
               Needs: GSC_SITE_URL, GOOGLE_APPLICATION_CREDENTIALS

-----------------------------------------------------------
  QUICK WINS — Top 3 connectors to add next
-----------------------------------------------------------

  1. Google Sheets (npx) — HIGH IMPACT
     Unlocks: /batch-process requirement intake, /cf:analytics, /cf:audit
     Setup: Set GOOGLE_APPLICATION_CREDENTIALS, then /cf:connect google-sheets
     Why: Batch processing reads requirements from Google Sheets. Without it,
     you're limited to interactive mode or CSV uploads.

  2. Ahrefs (HTTP) — MEDIUM IMPACT
     Unlocks: /cf:brief keyword data, /cf:audit content gaps, /content-refresh SEO
     Setup: Already in .mcp.json — authorize on first use
     Why: Data-driven content briefs with real search volumes instead of estimates.

  3. Google Drive (npx) — MEDIUM IMPACT
     Unlocks: Brand knowledge vault, output delivery for all skills
     Setup: Set GOOGLE_APPLICATION_CREDENTIALS, then /cf:connect google-drive
     Why: Centralized brand assets and automatic output file delivery.

-----------------------------------------------------------
  COVERAGE SUMMARY
-----------------------------------------------------------

  Total connectors:     22
  Connected:            7 (32%)
  Available:            15

  HTTP connectors:      9 total, 7 connected (78%)
  npx connectors:       13 total, 0 connected (0%)

  Categories covered:   6 of 12 (50%)
  Categories empty:     6

-----------------------------------------------------------
  NEXT STEPS
-----------------------------------------------------------

  Connect your top quick win:
    /cf:connect google-sheets

  See setup guide for any connector:
    /cf:connect <name>

  Full connector reference:
    See CONNECTORS.md
===========================================================
```

## Category Reference

| Category | Connectors | Key Skills Enabled |
|----------|-----------|-------------------|
| Knowledge base | Notion, Confluence | contentforge, batch-process, content-refresh, cf-brief, cf-audit, cf-style-guide |
| Design | Canva, Figma | contentforge, batch-process, cf-social-adapt |
| CMS | Webflow, WordPress, HubSpot CMS | cf-publish, contentforge, batch-process |
| Chat | Slack | batch-process, cf-publish, cf-calendar |
| Email | Gmail | batch-process, cf-publish |
| Calendar | Google Calendar | cf-calendar, batch-process |
| Spreadsheets | Google Sheets | batch-process, cf-analytics, cf-audit |
| File storage | Google Drive | contentforge, batch-process, content-refresh, cf-style-guide, cf-audit |
| SEO | Ahrefs, Similarweb, Semrush | cf-brief, cf-audit, content-refresh |
| Translation | DeepL, Sarvam AI | cf-translate |
| Social media | Twitter/X, LinkedIn, Instagram | cf-social-adapt |
| Analytics | Google Analytics, Google Search Console | cf-analytics, cf-audit, cf-brief |

## Transport Types

| Transport | Setup Effort | Environment | Authentication |
|-----------|-------------|-------------|---------------|
| **HTTP** | Minimal — already in `.mcp.json` | Cowork + Claude Code | OAuth prompt on first use |
| **npx** | Moderate — env vars + `.mcp.json` entry | Claude Code only | API keys via environment variables |

HTTP connectors are pre-configured in ContentForge's `.mcp.json` and work immediately in both Cowork and Claude Code. When you first use a skill that needs an HTTP connector, the platform prompts you to authorize via OAuth. No manual credential management required.

npx connectors require local Node.js, the appropriate npm package, and API keys set as environment variables. They work in Claude Code only. Use `/cf:connect <name>` for step-by-step setup.

## Troubleshooting

### "0 connectors connected" but .mcp.json exists
- Verify `.mcp.json` is in the plugin root directory (same level as `skills/`)
- Confirm `.mcp.json` has valid JSON with a `mcpServers` object
- Check that the file is not `.mcp.json.example` (the example file is for npx servers)

### Dashboard shows HTTP connector as "available" instead of "connected"
- HTTP connectors appear as "connected" if their name exists as a key in `.mcp.json` under `mcpServers`
- If you renamed a connector key in `.mcp.json`, the dashboard may not match it
- Check that the key name matches exactly (e.g., `notion`, not `Notion` or `notion-mcp`)

### npx connector shows "not connected" even though env vars are set
- Environment variables must be set in the current shell session
- If using `.env` files, ensure they are loaded before running the skill
- Verify with: `echo $VARIABLE_NAME` (should not be empty)

### Dashboard takes a long time
- The script reads `.mcp.json` and checks environment variables only — no network calls
- If slow, check for filesystem issues or very large `.mcp.json` files

## Agent Used

None. This skill is entirely script-driven using `scripts/connector-status.py`.

## Related Skills

- **[/cf:connect](../cf-connect/SKILL.md)** — Guided setup for a specific connector
- **[/contentforge](../contentforge/SKILL.md)** — Main content production pipeline
- **[/batch-process](../batch-process/SKILL.md)** — Parallel content processing

---

**Version:** 3.4.0
**Script:** `scripts/connector-status.py --action status`
**Processing Time:** <10 seconds
**Network Required:** No (reads local config only)
