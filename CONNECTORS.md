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

## Advanced configuration (Claude Code)

For Claude Code CLI users who need Google Sheets, Google Drive, and other npx integrations, rename the example file:

```bash
cp .mcp.json.example .mcp.json
```

This adds npx servers alongside the HTTP connectors. Requires Node.js, npx, and the appropriate API keys configured as environment variables.
