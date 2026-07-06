---
name: cf-add-integration
description: "Add a custom MCP connector — connect any API or service to ContentForge via .mcp.json configuration."
disable-model-invocation: true
argument-hint: "[service-name]"
effort: medium
---

# /contentforge:cf-add-integration

## Purpose

Help users connect any external API, tool, or service to ContentForge as an MCP connector. Walk through the entire process conversationally — from finding the right MCP package to testing the connection — without requiring technical MCP knowledge.

## Input Required

The user provides (or will be asked):

- **What they want to connect**: The service name and what they want it to do — e.g., "Google Analytics to track content performance", "Ahrefs for keyword research", "our internal CMS to publish directly"
- **Credentials**: API keys, tokens, or OAuth setup they have (or will need to obtain). The system will guide them on exactly what's needed. **Never ask users to paste secrets into the conversation.**

## Process

### Step 1: Understand what the user wants

Ask the user what service they want to connect and what they want it to do within ContentForge. Map their intent to content workflow stages:

| Workflow Stage | Example Integrations |
|---------------|---------------------|
| Research (Phase 1) | Ahrefs, Similarweb, Google Search Console |
| Publishing (Phase 8) | Webflow, WordPress, HubSpot CMS |
| Collaboration | Notion, Slack, Google Drive |
| Tracking | Google Sheets, Google Analytics |
| Translation | DeepL, Sarvam AI |
| Social distribution | Twitter/X, LinkedIn, Instagram |

### Step 2: Check if a connector already exists

Run `python scripts/connector-status.py --action check <name>` to see if the connector is already in the registry.

- **If it exists and is connected**: Tell the user it's already active and which skills use it.
- **If it exists but not connected**: Run `python scripts/connector-status.py --action setup-guide <name>` and walk through the guided setup.
- **If it doesn't exist**: Proceed to Step 3.

### Step 3: Find an MCP package

Search for an existing MCP server package that provides the desired integration.

Note: ContentForge ships with an empty `.mcp.json` (`"mcpServers": {}`) by design — every connector is opt-in and user-added. Nothing is pre-wired.

1. **Check verified HTTP endpoints first** — hosted HTTP MCP servers are the easiest (work in both Cowork and Claude Code, no API keys for OAuth-based ones). The plugin's catalog of verified HTTP endpoints lives in **`.mcp.json.connectors-reference`** — use the URL from that file. If the service isn't listed there, check the vendor's official documentation for an MCP endpoint before guessing. Do not use endpoint URLs from memory: unverified URLs waste the user's setup time.

2. **Search npm for MCP packages** — Search for `mcp-<service-name>` or `<service-name>-mcp-server`. **Verify the package actually exists and is maintained before recommending it:** run `npm view <package-name> version` and check last-publish date and download counts. If nothing maintained exists, say so honestly.

3. **If no endpoint or package exists** — Guide the user through custom MCP server development (see Step 5).

### Step 4: Configure the connector

Generate the exact configuration entry for `.mcp.json`:

**For HTTP connectors:**
```json
{
  "mcpServers": {
    "service-name": {
      "type": "http",
      "url": "https://mcp.service.com/mcp",
      "description": "Service Name — what it provides for ContentForge"
    }
  }
}
```

**For npx connectors:**
```json
{
  "mcpServers": {
    "service-name": {
      "command": "npx",
      "args": ["-y", "mcp-package-name"],
      "env": {
        "SERVICE_API_KEY": "${SERVICE_API_KEY}"
      },
      "description": "Service Name — what it provides for ContentForge"
    }
  }
}
```

**Walk the user through:**
1. Open `.mcp.json` in the plugin root directory
2. Add the new entry inside the `mcpServers` object
3. Set up environment variables (explain where: `.env` file or system environment)
4. Save and restart the session

### Step 5: Custom MCP server (if needed)

If no existing package covers the user's needs, provide a development template:

```
Project Structure:
  my-mcp-server/
  ├── index.js          # Main server with tool definitions
  ├── package.json      # Dependencies
  └── .env.example      # Required credentials

Key Components:
  - Tool definitions (what Claude can call)
  - Authentication handler (API key, OAuth, etc.)
  - Request/response formatting
  - Error handling with meaningful messages

.mcp.json Entry:
  "my-service": {
    "command": "node",
    "args": ["path/to/my-mcp-server/index.js"],
    "env": { "MY_API_KEY": "${MY_API_KEY}" }
  }
```

Provide a starter skeleton specific to the user's API, with:
- Endpoint URLs pre-filled
- Authentication pattern matching their API
- Tool definitions for common operations

### Step 6: Test and verify

After configuration:

1. Ask the user to restart their Claude session
2. Run `/contentforge:cf-integrations` to verify the new connector shows up
3. Try a basic read operation to confirm it works
4. Report success or diagnose failures

### Step 7: Platform-level integrations

Some services (Google Drive, Google Docs) can be connected at the **Claude platform level** rather than through MCP. These are managed in:

- **Cowork/Claude Desktop**: Settings → Integrations → Connect
- **Benefit**: No API keys needed — uses OAuth through Anthropic's infrastructure
- **Limitation**: May offer fewer capabilities than a dedicated MCP server

If the user's desired service is available as a platform integration, mention this as the simpler option.

## Output

- **Configuration JSON**: Ready-to-paste `.mcp.json` entry
- **Credential setup**: Step-by-step instructions for API key or OAuth setup
- **Verification**: Confirm the connector is working or provide error diagnostics
- **Skills affected**: Which ContentForge skills gain capabilities from this connector

## Tone

Conversational and supportive. This skill exists so that non-technical users can connect services without understanding MCP internals. Avoid jargon. Use "connector" not "MCP server". Say "connect your API key" not "configure environment variables."
