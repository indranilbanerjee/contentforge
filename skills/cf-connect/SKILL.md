---
name: cf-connect
description: "Set up a specific MCP connector for ContentForge — step-by-step instructions for connecting Notion, Canva, Webflow, Google Sheets, etc."
argument-hint: "[connector-name]"
---

# Guided Connector Setup

Set up a specific MCP integration for ContentForge with step-by-step instructions tailored to the connector's transport type. Handles HTTP connectors (OAuth-based, zero config), npx connectors (API keys, environment variables, `.mcp.json` entry), unknown connector names (fuzzy matching), and post-setup verification.

## When to Use

Use `/cf:connect <name>` when:
- You want to connect a specific service (e.g., `/cf:connect wordpress`)
- A skill told you a connector is missing and suggested using this command
- You're setting up a new ContentForge installation and configuring integrations
- You need the exact environment variables and `.mcp.json` entry for an npx connector
- You want to verify an existing connector is working correctly

## What This Command Does

1. **Look Up Connector** — Find the connector in the registry, handle typos and close matches
2. **Check Current Status** — Determine if already connected or needs setup
3. **Present Setup Instructions** — Tailored to transport type (HTTP vs npx)
4. **Guide Credential Acquisition** — Where to get API keys, which permissions to set
5. **Provide .mcp.json Entry** — Ready-to-paste configuration for npx connectors
6. **Verify After Setup** — Confirm environment variables are set and configuration is valid

## Required Inputs

**Required:**
- **Connector name** — The service to connect (e.g., `notion`, `wordpress`, `google-sheets`, `canva`)
- Fuzzy matching is supported: `wp` matches `wordpress`, `gsheets` matches `google-sheets`, `ga` matches `google-analytics`

**Optional:**
- **Environment** — `cowork` or `claude-code` (auto-detected if not specified)

## How to Use

### Basic Usage
```
/cf:connect wordpress
```
Shows step-by-step setup instructions for WordPress.

### Already Connected Connector
```
/cf:connect notion
```
If Notion is already configured, shows confirmation and which skills it enables.

### Unknown Connector Name
```
/cf:connect wp
```
Fuzzy matches to `wordpress` and shows setup guide.

### With Environment Override
```
/cf:connect google-sheets --env=claude-code
```
Forces Claude Code-specific instructions (relevant for npx connectors).

## What Happens

### Step 1: Look Up Connector (Instant)

Run the setup guide lookup:

```
python3 scripts/connector-status.py --action setup-guide --name <connector>
```

This returns:
- Connector metadata (name, category, description, transport type)
- Whether it's already configured
- Setup steps specific to the transport type
- Skills unlocked by this connector
- For npx: required environment variables and `.mcp.json` entry

**If the connector name is not found:**
- The script returns an error with a hint to list available connectors
- Before showing the error, check for common aliases and close matches:

| Input | Matches To |
|-------|-----------|
| `wp`, `wordpress` | `wordpress` |
| `gsheets`, `sheets`, `google-sheets` | `google-sheets` |
| `gdrive`, `drive`, `google-drive` | `google-drive` |
| `ga`, `ga4`, `google-analytics` | `google-analytics` |
| `gsc`, `search-console` | `google-search-console` |
| `gcal`, `calendar` | `google-calendar` |
| `x`, `twitter` | `twitter-x` |
| `li`, `linkedin` | `linkedin-publishing` |
| `ig`, `insta` | `instagram` |
| `hs`, `hubspot` | `hubspot-cms` |
| `sw`, `similarweb` | `similarweb` |
| `sarvam` | `sarvam-ai` |

If no match is found after alias lookup, present the full list of available connectors and ask the user to pick one.

### Step 2: Check Current Status (Instant)

Run the status check:

```
python3 scripts/connector-status.py --action check --name <connector>
```

This returns:
- `connected` or `not_connected`
- For npx connectors: which env vars are set vs missing
- Transport type and URL (HTTP) or package name (npx)

**If already connected:**
```
-----------------------------------------------------------
  CONNECTOR STATUS: Notion
-----------------------------------------------------------

  Status:       Connected
  Transport:    HTTP
  Category:     Knowledge base
  URL:          https://mcp.notion.com/mcp

  Skills enabled by this connector:
  - /contentforge — content production pipeline
  - /batch-process — parallel content processing
  - /content-refresh — update existing content
  - /cf:brief — data-driven content briefs
  - /cf:audit — content quality audit
  - /cf:style-guide — brand style guide management

  This connector is working. No action needed.

  Tip: Try /contentforge to start producing content with Notion
  as your requirement and brand document source.
-----------------------------------------------------------
```

**If not connected, proceed to Step 3.**

### Step 3: Present Setup Instructions

Instructions differ based on transport type.

#### HTTP Connectors (7 pre-configured: Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar; plus Ahrefs, Similarweb available)

The 7 pre-configured HTTP connectors are the easiest to set up because they're already in ContentForge's `.mcp.json` file. No API keys, no environment variables, no manual configuration. Ahrefs and Similarweb are also HTTP connectors but must be added to `.mcp.json` by the user.

```
-----------------------------------------------------------
  SETUP GUIDE: Canva
-----------------------------------------------------------

  Transport:    HTTP (pre-configured)
  Category:     Design
  URL:          https://mcp.canva.com/mcp

  SETUP STEPS:
  -----------------------------------------------------------

  Step 1: Nothing to configure.
          This connector is already defined in ContentForge's
          .mcp.json file. HTTP connectors are managed by the
          platform automatically.

  Step 2: Use a skill that needs Canva.
          Try: /contentforge (with image generation enabled)
          Or:  /cf:social-adapt (for social media graphics)

  Step 3: Authorize when prompted.
          The first time a skill accesses Canva, the platform
          will display an OAuth authorization prompt. Sign in
          with your Canva account and grant the requested
          permissions.

  Step 4: Done.
          After authorization, Canva is fully connected. The
          OAuth token is managed by the platform — you won't
          need to re-authorize unless you revoke access.

  SKILLS UNLOCKED:
  -----------------------------------------------------------
  - /contentforge — generate featured images alongside content
  - /batch-process — auto-generate images for batch runs
  - /cf:social-adapt — create platform-specific social graphics

  ENVIRONMENT:
  -----------------------------------------------------------
  Works in: Cowork and Claude Code
  Credentials: Managed by platform (OAuth)
  .mcp.json: Already configured (no changes needed)

-----------------------------------------------------------
```

#### npx Connectors (WordPress, Google Sheets, Google Drive, Semrush, DeepL, etc.)

npx connectors require environment variables and a `.mcp.json` entry. They work in Claude Code only.

```
-----------------------------------------------------------
  SETUP GUIDE: WordPress
-----------------------------------------------------------

  Transport:    npx (local server)
  Category:     CMS
  Package:      mcp-wordpress

  SETUP STEPS:
  -----------------------------------------------------------

  Step 1: Obtain API credentials.
          - Log in to your WordPress admin panel
          - Go to Users > Your Profile > Application Passwords
          - Create a new application password for "ContentForge"
          - Copy the generated password (shown once only)
          - Note your site URL (e.g., https://example.com)

  Step 2: Set environment variables.
          Add these to your shell profile (.bashrc, .zshrc) or .env file:

          export WORDPRESS_SITE_URL="https://your-site.com"
          export WORDPRESS_AUTH_TOKEN="your-application-password"

          Then reload your shell:
          source ~/.bashrc   # or source ~/.zshrc

  Step 3: Add to .mcp.json.
          Add this entry to the mcpServers object in your
          ContentForge .mcp.json file:

          "wordpress": {
            "command": "npx",
            "args": ["-y", "mcp-wordpress"],
            "env": {
              "WORDPRESS_SITE_URL": "${WORDPRESS_SITE_URL}",
              "WORDPRESS_AUTH_TOKEN": "${WORDPRESS_AUTH_TOKEN}"
            }
          }

          If you prefer, copy the full .mcp.json.example file
          which includes all npx connectors pre-configured:

          cp .mcp.json.example .mcp.json

  Step 4: Verify the connection.
          Restart Claude Code to pick up the new .mcp.json entry.
          Then test with:

          /cf:integrations --category=cms

          WordPress should appear as [connected].

  ENVIRONMENT VARIABLES:
  -----------------------------------------------------------
  | Variable              | Status  | Description                    |
  |-----------------------|---------|--------------------------------|
  | WORDPRESS_SITE_URL    | missing | Your WordPress site URL        |
  | WORDPRESS_AUTH_TOKEN   | missing | Application password from WP   |

  .MCP.JSON ENTRY (ready to paste):
  -----------------------------------------------------------
  "wordpress": {
    "command": "npx",
    "args": ["-y", "mcp-wordpress"],
    "env": {
      "WORDPRESS_SITE_URL": "${WORDPRESS_SITE_URL}",
      "WORDPRESS_AUTH_TOKEN": "${WORDPRESS_AUTH_TOKEN}"
    }
  }

  SKILLS UNLOCKED:
  -----------------------------------------------------------
  - /cf:publish — publish directly to WordPress from ContentForge
  - /contentforge — end-to-end pipeline with WordPress as publish target
  - /batch-process — auto-publish batch runs to WordPress

  ENVIRONMENT:
  -----------------------------------------------------------
  Works in: Claude Code only (requires Node.js + npx)
  Does NOT work in: Cowork (npx servers not supported)
  Requirements: Node.js 18+, npx available in PATH

  NOTES:
  -----------------------------------------------------------
  - API keys are read from environment variables at runtime.
    Never hardcode credentials in .mcp.json or plugin files.
  - If you use .env files, make sure they're loaded before
    starting Claude Code (e.g., via direnv or shell profile).
  - The npx package is downloaded automatically on first use.
    No separate npm install step required.

-----------------------------------------------------------
```

### Step 4: Handle Unknown Connectors

When a connector name is not found in the registry and no fuzzy match exists:

```
-----------------------------------------------------------
  CONNECTOR NOT FOUND: "monday"
-----------------------------------------------------------

  "monday" is not in the ContentForge connector registry.

  Did you mean one of these?
  - notion (knowledge-base) — content requirements, brand docs
  - confluence (knowledge-base) — team wikis, brand guidelines

  Or browse all 22 available connectors:
  /cf:integrations --show=available

  MANUAL CONFIGURATION:
  -----------------------------------------------------------
  If you have an MCP server for Monday.com, you can add it
  manually to .mcp.json:

  For HTTP MCP servers:
  "monday": {
    "type": "http",
    "url": "https://your-mcp-server-url/mcp"
  }

  For npx MCP servers:
  "monday": {
    "command": "npx",
    "args": ["-y", "mcp-monday"],
    "env": {
      "MONDAY_API_KEY": "${MONDAY_API_KEY}"
    }
  }

  Note: Manually added connectors will work with Claude but
  won't appear in /cf:integrations until added to the registry.

-----------------------------------------------------------
```

### Step 5: Verify After Setup (npx only)

After the user follows the setup steps for an npx connector, help them verify:

```
-----------------------------------------------------------
  VERIFICATION: WordPress
-----------------------------------------------------------

  Checking environment variables...
  WORDPRESS_SITE_URL:    set ("https://example.com")
  WORDPRESS_AUTH_TOKEN:  set (value hidden)

  Checking .mcp.json...
  "wordpress" entry:     found

  Result: Configuration looks correct.

  Next step: Restart Claude Code and try:
  /cf:publish --platform=wordpress --test

  This will attempt a test connection to verify credentials
  are valid and the WordPress site is reachable.

-----------------------------------------------------------
```

For HTTP connectors, verification is not needed — they authenticate on first use via OAuth.

## Output

The complete setup guide includes these sections:

| Section | Description |
|---------|------------|
| **Connector Info** | Name, category, description, transport type |
| **Current Status** | Connected or not connected, with details |
| **Setup Steps** | Numbered walkthrough tailored to transport type |
| **Skills Unlocked** | Which ContentForge skills this connector enables |
| **Credential Requirements** | For npx: environment variables needed with set/missing status |
| **.mcp.json Entry** | For npx: ready-to-paste JSON configuration block |
| **Environment Notes** | Cowork vs Claude Code compatibility, Node.js requirements |
| **Verification Steps** | How to confirm the connector is working after setup |
| **Alternative Connectors** | Other connectors in the same category if this one doesn't fit |
| **Next Steps** | Suggested skill to try first with the new connector |

## Connector Quick Reference

### HTTP Connectors (7 Pre-Configured + 2 Available)

| Connector | Category | URL | Pre-configured | Skills |
|-----------|----------|-----|----------------|--------|
| Notion | Knowledge base | `https://mcp.notion.com/mcp` | Yes | contentforge, batch-process, content-refresh, cf-brief, cf-audit, cf-style-guide |
| Canva | Design | `https://mcp.canva.com/mcp` | Yes | contentforge, batch-process, cf-social-adapt |
| Figma | Design | `https://mcp.figma.com/mcp` | Yes | contentforge, cf-social-adapt |
| Webflow | CMS | `https://mcp.webflow.com/sse` | Yes | cf-publish, contentforge, batch-process |
| Slack | Chat | `https://mcp.slack.com/mcp` | Yes | batch-process, cf-publish, cf-calendar |
| Gmail | Email | `https://gmail.mcp.claude.com/mcp` | Yes | batch-process, cf-publish |
| Google Calendar | Calendar | `https://gcal.mcp.claude.com/mcp` | Yes | cf-calendar, batch-process |
| Ahrefs | SEO | `https://api.ahrefs.com/mcp/mcp` | No | cf-brief, cf-audit, content-refresh |
| Similarweb | SEO | `https://mcp.similarweb.com` | No | cf-brief, cf-audit |

### npx Connectors (Require Setup)

| Connector | Category | Package | Env Vars |
|-----------|----------|---------|----------|
| Confluence | Knowledge base | `mcp-confluence` | CONFLUENCE_URL, CONFLUENCE_TOKEN |
| WordPress | CMS | `mcp-wordpress` | WORDPRESS_SITE_URL, WORDPRESS_AUTH_TOKEN |
| HubSpot CMS | CMS | `mcp-hubspot-cms` | HUBSPOT_ACCESS_TOKEN |
| Google Sheets | Spreadsheets | `@anthropic/mcp-google-sheets` | GOOGLE_APPLICATION_CREDENTIALS |
| Google Drive | File storage | `@anthropic/mcp-google-drive` | GOOGLE_APPLICATION_CREDENTIALS |
| Semrush | SEO | `mcp-semrush` | SEMRUSH_API_KEY |
| DeepL | Translation | `deepl-mcp-server` | DEEPL_API_KEY |
| Sarvam AI | Translation | `sarvam-mcp-server` | SARVAM_API_KEY |
| Twitter/X | Social media | `mcp-twitter` | TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET |
| LinkedIn | Social media | `mcp-linkedin-publishing` | LINKEDIN_ACCESS_TOKEN |
| Instagram | Social media | `mcp-instagram` | INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ACCOUNT_ID |
| Google Analytics | Analytics | `@anthropic/mcp-google-analytics` | GA_PROPERTY_ID, GOOGLE_APPLICATION_CREDENTIALS |
| Google Search Console | Analytics | `@anthropic/mcp-google-search-console` | GSC_SITE_URL, GOOGLE_APPLICATION_CREDENTIALS |

## Troubleshooting

### "Unknown connector" even though you typed the right name
- Connector names use lowercase kebab-case: `google-sheets`, not `Google Sheets` or `googlesheets`
- Try the fuzzy match: the skill checks common aliases automatically
- Run `/cf:integrations --show=available` to see all valid connector names

### npx connector shows "connected" but skills still can't use it
- Restart Claude Code after modifying `.mcp.json` — changes are read at startup only
- Verify the npx package name is correct (check `.mcp.json.example` for reference)
- Check that Node.js and npx are in your PATH: `npx --version` should return a version number

### Environment variables set but still showing "missing"
- Variables must be exported, not just assigned: `export VAR=value`, not `VAR=value`
- If using `.env` files, they must be loaded before the shell session starts
- On Windows, set them in System Properties > Environment Variables, then restart the terminal

### OAuth prompt never appears for HTTP connector
- HTTP connectors authenticate only when a skill actively requests data from them
- Try using a skill first (e.g., `/contentforge` for Notion, `/cf:social-adapt` for Canva)
- If the prompt still doesn't appear, check that `.mcp.json` contains the connector's URL

### "npx: command not found"
- Install Node.js 18+ from https://nodejs.org
- Verify: `node --version` and `npx --version`
- On some systems, you may need to add Node.js to your PATH manually

### Connector works in Claude Code but not in Cowork
- npx connectors are Claude Code only — they require local Node.js
- If you need this integration in Cowork, check if an HTTP alternative exists:
  - WordPress (npx) has no HTTP equivalent — Claude Code only
  - Google Sheets (npx) has no HTTP equivalent — Claude Code only
  - Use `/cf:integrations` to see which connectors work in Cowork

## Example Workflows

### Workflow 1: Set Up WordPress Publishing
```
1. /cf:connect wordpress
   → Follow steps: get application password, set env vars, add to .mcp.json
2. Restart Claude Code
3. /cf:integrations --category=cms
   → Verify WordPress shows as [connected]
4. /contentforge "Your Topic" --type=blog --brand=YourBrand
   → Produces content
5. /cf:publish --platform=wordpress --status=draft
   → Pushes to WordPress as draft
```

### Workflow 2: Add Google Sheets for Batch Processing
```
1. /cf:connect google-sheets
   → Follow steps: create service account, download credentials JSON, set env var
2. Restart Claude Code
3. /cf:integrations --category=spreadsheets
   → Verify Google Sheets shows as [connected]
4. /batch-process https://docs.google.com/spreadsheets/d/ABC123
   → Reads requirements from sheet, processes in parallel
```

### Workflow 3: Connect SEO Tools for Data-Driven Briefs
```
1. /cf:connect ahrefs
   → HTTP connector, already in .mcp.json, just use it
2. /cf:brief "AI in Healthcare 2026" --brand=AcmeMed
   → Brief now includes real keyword volumes from Ahrefs
3. /cf:connect semrush (optional, for additional data)
   → Follow npx setup steps
```

## Agent Used

None. This skill is entirely script-driven using `scripts/connector-status.py`.

## Related Skills

- **[/cf:integrations](../cf-integrations/SKILL.md)** — Full integration status dashboard
- **[/contentforge](../contentforge/SKILL.md)** — Main content production pipeline
- **[/batch-process](../batch-process/SKILL.md)** — Parallel content processing
- **[/content-refresh](../content-refresh/SKILL.md)** — Update existing content

---

**Version:** 3.4.0
**Script:** `scripts/connector-status.py --action setup-guide --name <connector>`
**Processing Time:** <10 seconds
**Network Required:** No (reads local config and env vars only)
