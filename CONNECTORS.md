# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~knowledge base` might mean Notion, Confluence, or any other knowledge management tool with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (knowledge base, design, CMS, etc.) rather than specific products. As of v3.9.0, no MCP servers are pre-configured: no `.mcp.json` ships and the catalog of supported HTTP connectors lives in `.mcp.json.connectors-reference`. This is an opt-in model — see "Connectors for this plugin" and "Enabling connectors" below.

## Connectors for this plugin

The HTTP connector catalog (opt-in via `.mcp.json.connectors-reference`):

| Category | Placeholder | Reference catalog entry | Other options | Workflow impact |
|----------|-------------|------------------------|---------------|----------------|
| Knowledge base | `~~knowledge base` | Notion | Confluence, Guru, Google Drive | Core requirement storage — powers all content workflows |
| Design | `~~design` | Canva, Figma | Adobe Creative Cloud | Featured images, social graphics, infographics |
| CMS | `~~CMS` | Webflow | WordPress, HubSpot CMS | Publishing destination — enables `/contentforge:publish` |
| Chat | `~~chat` | Slack | Microsoft Teams | Batch status notifications, content approval alerts |
| Email | `~~email` | Gmail | Outlook | Draft delivery, review notifications |
| Calendar | `~~calendar` | Google Calendar | Outlook Calendar | Content calendar events |
| Image generation | `~~image gen` | fal.ai, Replicate | — | Feature images, contextual illustrations, social graphics — enables Phase 3.5 AI generation |

## Enabling connectors (opt-in model, v3.9.0+)

ContentForge no longer auto-connects MCP servers on plugin enable. To activate a specific connector:

1. **Interactive walkthrough:** ask Claude to use the `cf-connect` skill (e.g., "Use cf-connect to enable Notion")
2. **Slash command:** run `/contentforge:cf-add-integration` and follow prompts
3. **Manual edit:** copy the entry you want from `.mcp.json.connectors-reference` into the `mcpServers` object in `.mcp.json`

Most HTTP connectors require platform-side OAuth on first connection. Auth is handled by Claude Code, not by ContentForge.

## Platform-level integrations

Some services are connected at the **Claude platform level** rather than through MCP. These are managed in Claude Desktop → Settings → Integrations and work automatically in Cowork sessions.

| Service | Platform integration | MCP alternative |
|---------|---------------------|-----------------|
| Google Drive | Yes — connect in Settings → Integrations | `pipedream-google-drive` (HTTP, in `.mcp.json.connectors-reference`) |
| Google Docs | Yes — connect in Settings → Integrations | `pipedream-generic` / `composio-generic` (HTTP, in `.mcp.json.connectors-reference`) |

Platform-level integrations work even if they don't appear in the `/contentforge:cf-integrations` connector dashboard. Google Drive connected at the platform level provides document access for brand knowledge and reference materials.

## Tracking & delivery backends

ContentForge supports three backends for content tracking and output delivery, configured per-brand during setup (Step G):

| Backend | Auth Setup | Tracking | File Delivery | Switch with |
|---------|-----------|----------|---------------|-------------|
| **Google Sheets + Drive** | Service account (~5 min) | `sheets-tracker.py` | `drive-uploader.py` | `/contentforge:cf-switch-backend google` |
| **Airtable** | Personal Access Token (~2 min) | `airtable-tracker.py` | Record attachments (same script) | `/contentforge:cf-switch-backend airtable` |
| **Local** | None | `local-tracker.py` | Local filesystem | `/contentforge:cf-switch-backend local` |

**Airtable** handles both tracking AND file delivery in a single platform (output files attach to the tracking record). No separate uploader needed.

**Local** works immediately with zero setup. Data at `~/.claude-marketing/{brand}/tracking/`. Good for getting started — switch to Google or Airtable anytime.

**Migration** between backends is supported via `/contentforge:cf-switch-backend`. Source data is never deleted.

## Categories `/contentforge:cf-add-integration` can guide you through

ContentForge ships no connector for the categories below — they are not in the `.mcp.json.connectors-reference` catalog and (with one exception, noted in the table) not in `.mcp.json.example` either. Run `/contentforge:cf-add-integration` and it walks you through wiring up any MCP server, npm package, or custom HTTP API. The Pipedream / Composio / Zapier / Make aggregator entries in the connectors-reference reach many of these services without a bespoke server.

| Category | Services | How to reach it | Workflow impact |
|----------|----------|-----------------|----------------|
| Spreadsheets | Google Sheets | `pipedream-google-sheets` or `composio-google-sheets` (HTTP, in connectors-reference) | Batch requirement intake — critical for `/batch-process` |
| File storage | Google Drive | `pipedream-google-drive` (HTTP), or the platform-level Drive integration in Cowork | Brand knowledge vault, reference docs, output delivery |
| SEO | Ahrefs, Similarweb, Semrush | Ahrefs: registry-known HTTP endpoint, add manually (see below). Similarweb + Semrush: aggregator or custom server | Keyword data for `/contentforge:cf-brief` content briefs |
| Translation | DeepL, Sarvam AI | DeepL: the vendor-published npm package in `.mcp.json.example`. Sarvam AI: no verified connector (aggregator or custom server) | Machine translation for `/contentforge:translate` |
| Social media | Twitter/X, LinkedIn, Instagram | `cf-add-integration` or aggregator | Direct publishing for `/contentforge:social-adapt` |
| Analytics | Google Analytics, Google Search Console | `cf-add-integration` or aggregator | Performance data for `/contentforge:cf-analytics` and `/contentforge:cf-audit` |
| Image generation (extras) | Stability AI, Gemini nanobanana, Imagenate | No verified connector: the npm packages for these are community packages, so none ships. Use the fal.ai / Replicate HTTP entries | Additional image gen providers — alternatives to the fal.ai / Replicate HTTP entries |

**Ahrefs and Similarweb are known to the connector registry but are not in the 16-entry HTTP catalog.** `/contentforge:cf-integrations` reports them with an add-it-yourself note:

- **Ahrefs** — verified HTTP endpoint, manual add: put `{"type": "http", "url": "https://api.ahrefs.com/mcp/mcp"}` in your `.mcp.json` under `mcpServers`. Requires an Ahrefs API subscription.
- **Similarweb** — no verified MCP endpoint or package exists. Reach the API through `pipedream-generic`, `composio-generic`, `zapier`, or a custom server.

## Managing connectors

Use these skills to discover and manage your integrations:

| Skill | What it does |
|-------|-------------|
| `/contentforge:cf-integrations` | Status dashboard — see what's connected, what's available, which workflows each connector enables |
| `/contentforge:cf-connect <name>` | Guided setup — step-by-step instructions for connecting a specific service (e.g., `/contentforge:cf-connect wordpress`) |
| `/contentforge:cf-add-integration` | Custom setup — add any MCP server not in the registry (npm packages or custom APIs) |
| `/contentforge:cf-switch-backend` | Switch tracking backend — migrate between Google Sheets, Airtable, and local with optional data migration |

## Advanced configuration (Claude Code)

`.mcp.json.example` holds one local npx/stdio server, DeepL's own package (`deepl-mcp-server`). It runs in Claude Code only; Cowork cannot run stdio servers at all.

**Why only one.** `npx -y <name>` downloads and runs whatever is published under that name, with your API keys in its environment, and a name nobody has registered can be registered by anyone. ContentForge therefore gives a runnable command only for a package the service's vendor publishes. The list is `config/verified-npx-packages.json` (package, expected npm publisher, vendor repository); a test checks that nothing else is runnable, and a weekly check confirms each listed package still exists and still has the expected publisher. For every other service, connector setup says "no verified connector" and offers the vendor's own MCP server, an aggregator, or skipping it. Community npm packages for WordPress, HubSpot, Semrush, Confluence, Sarvam AI, Twitter/X, LinkedIn, Instagram and some image services exist, but they are unverified third parties: read the source and check the publisher before you run one, and remember it receives the credentials you give it.

The former `google-sheets` and `google-drive` npx entries were **removed in July 2026** (the package names were unverifiable), and the Stability AI, nanobanana and imagenate entries in October 2026 (community packages, not the vendors'). Use the HTTP equivalents in `.mcp.json.connectors-reference` instead (`pipedream-google-sheets`, `pipedream-google-drive`, `composio-google-sheets`), or the platform-level Google Drive integration in Cowork.

To enable an npx server, **merge** its entry into your `.mcp.json` (create the file if you have none; never overwrite one you already use):

```bash
# Inspect the npx connector catalog
cat .mcp.json.example

# Add the entries you need to .mcp.json under "mcpServers"
# (manual edit, or use /contentforge:cf-add-integration)
```

Requires Node.js, npx, and the API key configured as an environment variable. `npx -y` downloads and executes remote code, which is why ContentForge offers it only for packages the vendor publishes.

Note that anything you put in `.mcp.json` connects on **every** session, in every project, not just when you run a ContentForge skill. Add only the servers you actively need.
