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

Cowork is **the recommended environment for teams** as of v3.12.9 — it has the friendliest UX, lowest setup friction, and works for non-CLI users. But it requires one extra setup step (connecting Google Drive) because the sandbox filesystem doesn't persist. After Drive is wired, everything works.

**Also check: is a Drive MCP available in this session?** Scan your available tools for `mcp__*drive*` or the Anthropic-platform Drive integration. The capability matrix below splits on that.

```
=== ContentForge in Cowork ===

| Capability                                  | Cowork + Drive   | Cowork alone   |
|---------------------------------------------|-------------------|----------------|
| /plugin commands                            | YES               | YES            |
| HTTP MCP connectors (Slack, HubSpot, ...)   | YES               | YES            |
| npx / stdio MCP connectors                  | NO                | NO             |
|                                             |                   |                |
| Final .docx delivery                        | -> Drive folder   | -> sandbox (gone after session) |
| Brand profile persistence                   | -> Drive          | sandbox only   |
| Per-phase checkpoint files                  | -> Drive          | sandbox only   |
| /contentforge:resume across sessions        | YES (via Drive)   | NO             |
| Team sharing of outputs                     | YES (Drive)       | NO             |
| Files visible to user without download      | YES (Drive)       | NO             |
| Full 10-phase pipeline                      | YES               | LOGICAL ONLY -- outputs sandbox-only |
```

**If Cowork + Drive:** This is the recommended team setup. Run `/contentforge:cf-cowork-setup` once to wire the Drive folder layout, then use ContentForge normally. Every `.docx`, brand profile, and run record lands in `My Drive/ContentForge/...` where your team can access it from anywhere.

**If Cowork without Drive:** Connect Drive first. Easiest path: Cowork → **Settings** → **Integrations** → **Google Drive** → Connect (60 seconds). Then run `/contentforge:cf-cowork-setup`. Until that's done, generated files will only exist for the current session and won't be retrievable after you close the chat.

Local Claude Code (CLI or IDE extension) is the alternative if you don't want to use Drive — files land directly in `~/Documents/ContentForge/<brand>/...` on your machine. But for team usage, Cowork+Drive is simpler.

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
