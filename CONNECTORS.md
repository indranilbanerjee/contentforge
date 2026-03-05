# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~knowledge base` might mean Notion, Confluence, or any other knowledge management tool with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (knowledge base, design, CMS, etc.) rather than specific products. The `.mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options | Workflow impact |
|----------|-------------|-----------------|---------------|----------------|
| Knowledge base | `~~knowledge base` | Notion | Confluence, Guru, Google Drive | Core requirement storage — powers all content workflows |
| Design | `~~design` | Canva, Figma | Adobe Creative Cloud | Featured images, social graphics, infographics |
| CMS | `~~CMS` | Webflow | WordPress, HubSpot CMS | Publishing destination — enables `/cf:publish` |
| Chat | `~~chat` | Slack | Microsoft Teams | Batch status notifications, content approval alerts |
| Email | `~~email` | Gmail | Outlook | Draft delivery, review notifications |
| Calendar | `~~calendar` | Google Calendar | Outlook Calendar | Content calendar events — enables `/cf:calendar` |

## Platform-level integrations

Some services are connected at the **Claude platform level** rather than through MCP. These are managed in Claude Desktop → Settings → Integrations and work automatically in Cowork sessions.

| Service | Platform integration | MCP alternative |
|---------|---------------------|-----------------|
| Google Drive | Yes — connect in Settings → Integrations | Also available via npx (`mcp-google-drive`) |
| Google Docs | Yes — connect in Settings → Integrations | Also available via npx (`mcp-google-docs`) |

Platform-level integrations work even if they don't appear in the `/cf:integrations` connector dashboard. Google Drive connected at the platform level provides document access for brand knowledge and reference materials.

## Tracking & delivery backends

ContentForge supports three backends for content tracking and output delivery, configured per-brand during setup (Step G):

| Backend | Auth Setup | Tracking | File Delivery | Switch with |
|---------|-----------|----------|---------------|-------------|
| **Google Sheets + Drive** | Service account (~5 min) | `sheets-tracker.py` | `drive-uploader.py` | `/cf:switch-backend google` |
| **Airtable** | Personal Access Token (~2 min) | `airtable-tracker.py` | Record attachments (same script) | `/cf:switch-backend airtable` |
| **Local** | None | `local-tracker.py` | Local filesystem | `/cf:switch-backend local` |

**Airtable** handles both tracking AND file delivery in a single platform (output files attach to the tracking record). No separate uploader needed.

**Local** works immediately with zero setup. Data at `~/.claude-marketing/{brand}/tracking/`. Good for getting started — switch to Google or Airtable anytime.

**Migration** between backends is supported via `/cf:switch-backend`. Source data is never deleted.

## Categories without HTTP connectors (Claude Code only)

The following integrations require local npx/stdio MCP servers. They work in Claude Code but not in Cowork. See `.mcp.json.example` for configuration.

| Category | Available via npx | Workflow impact |
|----------|------------------|----------------|
| Spreadsheets | Google Sheets | Batch requirement intake — critical for `/batch-process` |
| File storage | Google Drive | Brand knowledge vault, reference docs, output delivery |
| SEO | Ahrefs (HTTP), Similarweb (HTTP), Semrush (npx) | Keyword data for `/cf:brief` content briefs |
| Translation | DeepL, Sarvam AI | Machine translation for `/cf:translate` |
| Social media | Twitter/X, LinkedIn, Instagram | Direct publishing for `/cf:social-adapt` |
| Analytics | Google Analytics, Google Search Console | Performance data for `/cf:analytics` and `/cf:audit` |

## Managing connectors

Use these skills to discover and manage your integrations:

| Skill | What it does |
|-------|-------------|
| `/cf:integrations` | Status dashboard — see what's connected, what's available, which workflows each connector enables |
| `/cf:connect <name>` | Guided setup — step-by-step instructions for connecting a specific service (e.g., `/cf:connect wordpress`) |
| `/cf:add-integration` | Custom setup — add any MCP server not in the registry (npm packages or custom APIs) |
| `/cf:switch-backend` | Switch tracking backend — migrate between Google Sheets, Airtable, and local with optional data migration |

## Advanced configuration (Claude Code)

For Claude Code CLI users who need Google Sheets, Google Drive, and other npx integrations, rename the example file:

```bash
cp .mcp.json.example .mcp.json
```

This adds npx servers alongside the HTTP connectors. Requires Node.js, npx, and the appropriate API keys configured as environment variables.
