---
name: cf-connect
description: "Set up an MCP connector with step-by-step instructions. Use to connect Notion, Canva, Webflow, etc."
argument-hint: "[connector-name]"
effort: low
---

# /contentforge:cf-connect — Guided Connector Setup

Set up a specific MCP integration for ContentForge with step-by-step instructions tailored to the connector's transport type. Handles HTTP connectors (OAuth-based), npx connectors (API keys, environment variables, `.mcp.json` entry), unknown connector names (fuzzy matching), and post-setup verification.

## The ground truth about connectors

ContentForge ships with an **empty `.mcp.json`** (`"mcpServers": {}`). This is deliberate (v3.9.0 Cowork-safety decision): no connector auto-connects when the plugin is installed. **Every connector is opt-in** — the user adds it to `.mcp.json` (or connects it at the platform level in Cowork/Desktop Settings → Integrations).

Never claim a connector is pre-wired or already connected. All status claims must come from running `python scripts/connector-status.py` — never from this file or from memory.

## When to Use

Use `/contentforge:cf-connect <name>` when:
- You want to connect a specific service (e.g., `/contentforge:cf-connect wordpress`)
- A skill told you a connector is missing and suggested using this command
- You're setting up a new ContentForge installation and configuring integrations
- You need the exact environment variables and `.mcp.json` entry for an npx connector
- You want to verify an existing connector is working correctly

## What This Command Does

1. **Look Up Connector** — Find the connector in the registry, handle typos and close matches
2. **Check Current Status** — Determine if already configured or needs setup
3. **Present Setup Instructions** — Tailored to transport type (HTTP vs npx)
4. **Guide Credential Acquisition** — Where to get API keys, which permissions to set
5. **Provide .mcp.json Entry** — Ready-to-paste configuration
6. **Verify After Setup** — Confirm environment variables are set and configuration is valid

## Required Inputs

**Required:**
- **Connector name** — The service to connect (e.g., `notion`, `wordpress`, `google-sheets`, `canva`)
- Fuzzy matching is supported: `wp` matches `wordpress`, `gsheets` matches `google-sheets`, `ga` matches `google-analytics`

**Optional:**
- **Environment** — `cowork` or `claude-code` (auto-detected if not specified)

## What Happens

### Step 1: Look Up Connector (Instant)

Run the setup guide lookup:

```
python scripts/connector-status.py --action setup-guide --name <connector>
```

This returns:
- Connector metadata (name, category, description, transport type)
- Whether it's already configured in this installation
- Setup steps specific to the transport type
- Skills unlocked by this connector
- For npx: required environment variables and `.mcp.json` entry

**If the connector name is not found**, check common aliases before showing an error:

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
| `sarvam` | `sarvam-ai` |

If no match is found after alias lookup, run `python scripts/connector-status.py --action list-available` and present the actual list.

### Step 2: Check Current Status (Instant)

```
python scripts/connector-status.py --action check --name <connector>
```

This returns `connected` or `not_connected`, plus (for npx connectors) which env vars are set vs missing. Render exactly what the script reports.

**If already configured:** confirm to the user, list the skills it enables (from the script JSON), and stop — no action needed.

**If not configured, proceed to Step 3.**

### Step 3: Present Setup Instructions

Instructions differ based on transport type. Both types require the user to add an entry to `.mcp.json` (or connect at the platform level) — nothing is pre-wired.

#### HTTP Connectors (e.g., Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar, Ahrefs)

HTTP connectors are the easiest: one `.mcp.json` entry, no API keys for OAuth-based ones, and they work in **both Cowork and Claude Code**.

Setup pattern to walk the user through:

1. **Get the verified endpoint URL.** Use the endpoint from the setup-guide script output, cross-checked against `.mcp.json.connectors-reference` (the plugin's catalog of verified HTTP endpoints). Do not guess endpoint URLs from memory — unverified URLs waste the user's time.
2. **Add the entry to `.mcp.json`** in the plugin root:
   ```json
   "notion": {
     "type": "http",
     "url": "<verified endpoint from the reference file>"
   }
   ```
   In Cowork/Claude Desktop, the platform-level integration (Settings → Integrations) may be simpler — mention it when available.
3. **Restart the session** so the new entry is picked up.
4. **Authorize on first use.** The first time a skill accesses the connector, the platform shows an OAuth prompt. Sign in and grant permissions. The token is managed by the platform afterward.

#### npx Connectors (e.g., WordPress, Google Sheets, Semrush, DeepL)

npx connectors require environment variables and a `.mcp.json` entry. They work in **Claude Code only** (Cowork cannot run local Node.js servers).

Setup pattern:

1. **Get the package name and env vars** from `python scripts/connector-status.py --action setup-guide --name <connector>`.
2. **Verify the npm package actually exists before recommending it:**
   ```
   npm view <package-name> version
   ```
   If the package doesn't exist or looks abandoned (no updates in 12+ months, negligible downloads), tell the user and search npm for a maintained alternative rather than proceeding.
3. **Obtain credentials** from the service (e.g., WordPress: admin panel → Users → Profile → Application Passwords; create one named "ContentForge" and note the site URL).
4. **Set environment variables** (shell profile or `.env` loaded before Claude Code starts; on Windows: System Properties → Environment Variables, then restart the terminal):
   ```
   export WORDPRESS_SITE_URL="https://your-site.com"
   export WORDPRESS_AUTH_TOKEN="your-application-password"
   ```
5. **Add the `.mcp.json` entry** (use the exact block from the setup-guide output):
   ```json
   "wordpress": {
     "command": "npx",
     "args": ["-y", "<verified-package-name>"],
     "env": {
       "WORDPRESS_SITE_URL": "${WORDPRESS_SITE_URL}",
       "WORDPRESS_AUTH_TOKEN": "${WORDPRESS_AUTH_TOKEN}"
     }
   }
   ```
6. **Restart Claude Code** and verify (Step 5).

Never hardcode credentials in `.mcp.json` or plugin files — always reference environment variables.

### Step 4: Handle Unknown Connectors

When a connector name is not in the registry and no fuzzy match exists:

1. Say clearly it's not in the registry.
2. Suggest the closest same-category connectors from `--action list-available` output.
3. Offer manual configuration: an HTTP entry (`"type": "http", "url": ...`) if the service publishes an MCP endpoint, or an npx entry if a maintained npm MCP package exists (verify with `npm view` first).
4. Note: manually added connectors work with Claude but won't appear in `/contentforge:cf-integrations` until added to the registry.
5. For a fully guided custom flow, hand off to `/contentforge:cf-add-integration`.

### Step 5: Verify After Setup

For npx connectors, after the user follows the setup steps:

1. Re-run `python scripts/connector-status.py --action check --name <connector>` and render the result (env vars set/missing, `.mcp.json` entry found).
2. Remind the user to restart Claude Code — `.mcp.json` is read at startup only.
3. Suggest a first test, e.g. `/contentforge:cf-publish --platform=wordpress --status=draft` for WordPress.

For HTTP connectors, verification happens implicitly: the OAuth prompt appears on first real use.

## Output

The complete setup guide includes:

| Section | Description |
|---------|------------|
| **Connector Info** | Name, category, description, transport type (from script) |
| **Current Status** | Configured or not, with details (from script) |
| **Setup Steps** | Numbered walkthrough tailored to transport type |
| **Skills Unlocked** | Which ContentForge skills this connector enables (from script) |
| **Credential Requirements** | For npx: env vars needed with set/missing status |
| **.mcp.json Entry** | Ready-to-paste JSON block |
| **Environment Notes** | Cowork vs Claude Code compatibility, Node.js requirements |
| **Verification Steps** | How to confirm the connector works after setup |

## Troubleshooting

### "Unknown connector" even though you typed the right name
- Connector names use lowercase kebab-case: `google-sheets`, not `Google Sheets` or `googlesheets`
- Try the fuzzy match: the skill checks common aliases automatically
- Run `python scripts/connector-status.py --action list-available` to see all valid names

### npx connector configured but skills still can't use it
- Restart Claude Code after modifying `.mcp.json` — changes are read at startup only
- Verify the npm package name (`npm view <pkg> version`)
- Check that Node.js and npx are in your PATH: `npx --version`

### Environment variables set but still showing "missing"
- Variables must be exported, not just assigned: `export VAR=value`
- `.env` files must be loaded before the Claude Code session starts
- On Windows, set them in System Properties → Environment Variables, then restart the terminal

### OAuth prompt never appears for an HTTP connector
- HTTP connectors authenticate only when a skill actively requests data from them
- Confirm the entry exists in `.mcp.json` and the session was restarted after adding it

### "npx: command not found"
- Install Node.js 18+ from https://nodejs.org, then verify `node --version` and `npx --version`

### Connector works in Claude Code but not in Cowork
- npx connectors are Claude Code only — they require local Node.js
- In Cowork, prefer HTTP connectors or platform-level integrations (Settings → Integrations)
- Run `/contentforge:cf-integrations` to see which configured connectors are Cowork-compatible

## Example Workflows

### Workflow 1: Set Up WordPress Publishing
```
1. /contentforge:cf-connect wordpress
   -> Follow steps: verify package on npm, get application password, set env vars, add to .mcp.json
2. Restart Claude Code
3. /contentforge:cf-integrations
   -> Verify WordPress shows as configured (from script output)
4. /contentforge:create-content "Your Topic" --type=blog --brand=YourBrand
5. /contentforge:cf-publish --platform=wordpress --status=draft
```

### Workflow 2: Add Google Sheets for Batch Processing
```
1. /contentforge:cf-connect google-sheets
   -> Follow steps: create service account, download credentials JSON, set env var, add to .mcp.json
2. Restart Claude Code
3. /contentforge:batch-process <sheet URL>
   -> Reads requirements from the sheet, processes in parallel
```

### Workflow 3: Connect SEO Tools for Data-Driven Briefs
```
1. /contentforge:cf-connect ahrefs
   -> HTTP connector: add the verified endpoint to .mcp.json, restart, authorize on first use
2. /contentforge:cf-brief "AI in Healthcare 2026" --brand=AcmeMed
   -> Brief now includes real keyword data from Ahrefs
```

## Agent Used

None. This skill is entirely script-driven using `scripts/connector-status.py`.

## Related Skills

- **[/contentforge:cf-integrations](../cf-integrations/SKILL.md)** — Full integration status dashboard
- **[/contentforge:cf-add-integration](../cf-add-integration/SKILL.md)** — Guided flow for services not in the registry
- **[/contentforge:create-content](../../commands/create-content.md)** — Main content production pipeline
- **[/contentforge:batch-process](../batch-process/SKILL.md)** — Parallel content processing

---

**Script:** `python scripts/connector-status.py --action setup-guide --name <connector>`
**Network Required:** No for status checks (reads local config and env vars); yes only for `npm view` package verification
