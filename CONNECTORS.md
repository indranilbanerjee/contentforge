# Connectors

## How tool references work

Plugin files use `~~category` as a placeholder for whatever tool the user connects in that category. For example, `~~knowledge base` might mean Notion, Confluence, or any other knowledge management tool with an MCP server.

Plugins are **tool-agnostic** — they describe workflows in terms of categories (knowledge base, design, CMS, etc.) rather than specific products. The `.mcp.json` pre-configures specific MCP servers, but any MCP server in that category works.

## Connectors for this plugin

| Category | Placeholder | Included servers | Other options |
|----------|-------------|-----------------|---------------|
| Knowledge base | `~~knowledge base` | Notion | Confluence, Guru, Google Drive |
| Design | `~~design` | Canva | Figma, Adobe Creative Cloud |
| CMS | `~~CMS` | Webflow | WordPress, HubSpot CMS |
| Chat | `~~chat` | Slack | Microsoft Teams |
| Email | `~~email` | Gmail | Outlook |
| Calendar | `~~calendar` | Google Calendar | Outlook Calendar |

## Categories without HTTP connectors (Claude Code only)

The following integrations require local npx/stdio MCP servers. They work in Claude Code but not in Cowork. See `.mcp.json.example` for configuration.

| Category | Available via npx | Notes |
|----------|------------------|-------|
| Spreadsheets | Google Sheets | Core requirement intake — configure in Claude Code |
| File storage | Google Drive | Brand knowledge vault — configure in Claude Code |

## Advanced configuration (Claude Code)

For Claude Code CLI users who need Google Sheets and Google Drive integration, rename the example file:

```bash
cp .mcp.json.example .mcp.json
```

This adds the Google Sheets and Google Drive npx servers alongside the HTTP connectors. Requires Node.js, npx, and Google Application Credentials.
