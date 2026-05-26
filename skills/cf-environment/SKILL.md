---
name: cf-environment
description: "Detect the runtime environment (Cowork sandbox vs local Claude Code) and report which ContentForge capabilities work in it. Use this when the user asks 'will this work in Cowork', sees unexpected file-path behavior, or wants a capability matrix before running a long pipeline."
argument-hint: "[--verbose]"
effort: low
---

# /contentforge:cf-environment

Detect where ContentForge is running and report which of its capabilities work in that environment. ContentForge has different real-world behavior on each surface because filesystem access, MCP transports, and subprocess invocation all differ.

## When to use this skill

- User asks "will my files actually save to my Documents folder?"
- User asks "does this work in Cowork?"
- User reports that `~/Documents/ContentForge/` is empty after a run
- Before kicking off a long (20-60 min) content pipeline, to set expectations
- During brand-setup, to decide between MCP-Drive and service-account routes

## Behavior

### Step 1 — Run the environment probe

```bash
python scripts/plugin-metadata.py --section environment
```

This returns JSON with `environment` (one of `cowork-sandbox`,
`claude-code-windows`, `claude-code-mac`, `claude-code-linux`, `unknown`),
filesystem indicators, and a `cowork_warning` field that's non-null when
the Cowork sandbox is detected.

### Step 2 — Present the capability matrix for the detected environment

Render one of the three matrices below based on the JSON `environment`.

#### `cowork-sandbox`

```
=== ContentForge in Cowork ===

| Capability                                  | Works in Cowork?            |
|---------------------------------------------|------------------------------|
| /plugin commands (install / update / list)  | YES                         |
| All HTTP MCP connectors (Slack, HubSpot,    | YES                         |
|   Klaviyo, Ahrefs, Notion, Canva, etc.)     |                              |
| npx / stdio MCP connectors (Google Ads,     | NO (sandbox blocks npx)     |
|   Meta Ads, mcp-mailchimp, mcp-sendgrid,    |                              |
|   etc.) -- need aggregator alternative      |                              |
| Google Drive via Anthropic platform         | YES (Settings -> Integrations) |
| Google Drive via Pipedream aggregator       | YES (HTTP)                  |
| Google Drive via service-account JSON       | LIMITED (sandbox FS only)   |
| Reading files from your Windows / Mac host  | NO                          |
| Writing to ~/Documents/ContentForge/        | NO -- writes go to sandbox  |
| Writing to ~/.claude-marketing/             | NO -- writes go to sandbox  |
| Dual-copy save (host + tracking dir)        | NO -- sandbox-only          |
| /contentforge:resume across sessions        | LIMITED -- sandbox FS may   |
|                                             |   be recycled between tabs  |
| Running the full 10-phase pipeline          | LOGICALLY YES, but file     |
|                                             |   outputs are sandbox-only  |

WARNING: Cowork is a Linux sandbox. ContentForge's file-system layer assumes
the user's host filesystem (Windows / Mac). In Cowork, every write lands in
the sandbox -- which is fine for testing the logical flow but means the
.docx you produce won't be in your real ~/Documents folder.

RECOMMENDED IN COWORK:
- Brand setup walkthrough (logical flow + MCP connector wiring)
- HTTP-connector integrations (Slack, HubSpot, Klaviyo, etc.)
- Single-shot content production where you'll download the .docx
  from the Cowork file panel before closing the session

NOT RECOMMENDED IN COWORK:
- Production-grade client work requiring the canonical filesystem layout
- Multi-session work that relies on checkpoint resume
- Any workflow requiring service-account-based Drive uploads to your host
- Any workflow that needs to read files from your Windows / Mac home dir

FOR FULL FUNCTIONALITY, RUN CONTENTFORGE IN LOCAL CLAUDE CODE
(CLI or the VS Code / JetBrains extension at claude.com/code).
```

#### `claude-code-windows`, `claude-code-mac`, `claude-code-linux`

```
=== ContentForge in local Claude Code (<platform>) ===

| Capability                                  | Works locally?              |
|---------------------------------------------|------------------------------|
| /plugin commands                            | YES                         |
| All HTTP MCP connectors                     | YES                         |
| npx / stdio MCP connectors                  | YES (requires Node.js)      |
| Google Drive via Anthropic platform         | LIMITED -- depends on       |
|                                             |   whether the host Claude   |
|                                             |   Code session has the      |
|                                             |   Drive integration         |
| Google Drive via Pipedream / Composio       | YES (HTTP)                  |
| Google Drive via service-account JSON       | YES                         |
| Reading files from your host                | YES                         |
| Writing to ~/Documents/ContentForge/        | YES                         |
| Writing to ~/.claude-marketing/             | YES                         |
| Dual-copy save (host + tracking dir)        | YES                         |
| /contentforge:resume across sessions        | YES (checkpoints persist)   |
| Running the full 10-phase pipeline          | YES, full functionality     |

This is the reference environment. Every ContentForge feature is designed
to work here. Use the env var CONTENTFORGE_PUBLISH_DIR to redirect the
visible-copy folder to a Dropbox / OneDrive / shared team drive if your
team has one.
```

#### `unknown`

```
=== ContentForge in an unrecognized environment ===

Environment heuristics couldn't classify this runtime. The plugin will run,
but file-system behavior may differ from the documented assumptions.

Probe data (raw):
<dump indicators from JSON>

Recommended: report this environment in a GitHub issue at
https://github.com/indranilbanerjee/contentforge/issues so we can extend
the environment detector to recognize it.
```

### Step 3 — Verbose mode

If `--verbose` is passed, also include the raw `indicators` block from the
JSON (platform, Python version, cwd, home dir, writable_cwd boolean). This
helps debug edge cases like a permissions-locked home dir.

## Why this skill exists

Before v3.12.8, ContentForge documentation implicitly assumed the local
Claude Code environment. Cowork users would run /contentforge:create-content,
see the success message, then ask "where are my files?" and find empty
Windows folders. The root cause is that Cowork's bash sandbox can't write
to the user's host -- it writes to its own Linux sandbox FS.

v3.12.8 surfaces this honestly with this skill plus an automatic warning
in /contentforge:cf-help when the cowork-sandbox environment is detected.

## What this skill does NOT do

- It does not change ContentForge's behavior. Cowork still has the same
  filesystem limits after running this skill -- you just understand them.
- It does not enable Cowork-to-host file writes. That's an Anthropic
  platform feature, not something a plugin can add.

## See also

- `scripts/plugin-metadata.py --section environment` -- the underlying probe
- `/contentforge:cf-help` -- automatically surfaces the Cowork warning
- README "Cross-platform compatibility" section -- the canonical doc
