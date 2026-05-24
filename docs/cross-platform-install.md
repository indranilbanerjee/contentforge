# Cross-platform install guide

ContentForge v3.12.0 ships **five platform-compatible install surfaces** from a single source repository — same 19 Agent Skills, 8 Python scripts, and 16 opt-in HTTP MCP connectors:

| Platform | Manifest path | Status |
|---|---|---|
| **Claude Code** (CLI + Desktop) + **Anthropic Cowork** | `.claude-plugin/plugin.json` | Full support — agents, skills, commands, hooks, MCP, scripts |
| **OpenAI Codex** (CLI) | `.codex-plugin/plugin.json` | Skills + MCP + hooks + scripts; commands and agents via Codex-native invocation patterns |
| **Cursor** (IDE + CLI) | `.cursor-plugin/plugin.json` | Skills + hooks + scripts; MCP via Cursor's global mcp.json (see below) |
| **GitHub Copilot CLI** | auto-discovers `.claude-plugin/plugin.json` (no new manifest needed) | Skills + MCP + hooks + scripts. Copilot CLI explicitly checks `.claude-plugin/plugin.json` as one of its plugin manifest discovery paths |
| **Google Antigravity 2.0 CLI** | `.antigravity/plugin.json` (**experimental** — see Antigravity section) | Skills work today via Antigravity's Gemini-CLI-extensions importer; full v2-native spec pending Antigravity publication |

The key insight: **Agent Skills are an open standard.** The `name:` + `description:` SKILL.md frontmatter is interpreted the same way by every major coding agent surface as of May 2026. ContentForge reuses the same `skills/` directory across all platform manifests — no skill duplication, no maintenance fork.

---

## Install on Claude Code (canonical)

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

See the [main README](../README.md) for the full Claude Code experience.

---

## Install on OpenAI Codex

```bash
codex plugin install indranilbanerjee/contentforge
```

After install, restart your Codex session. Try:

```
"Run the ContentForge 10-phase pipeline for an article on EU AI Act compliance."
"Humanize this draft against the 29-pattern AI-detection catalog."
"Fact-check the claims in this draft against authoritative sources."
"Generate a .docx of this article with C2PA provenance for EU distribution."
```

**What works on Codex:**
- All 19 Agent Skills (auto-discovered via SKILL.md frontmatter — same open standard as Claude Code)
- All 16 opt-in HTTP MCP connectors (catalog in `.mcp.json.connectors-reference`) — Codex reads `.mcp.json` directly; copy connectors in as needed
- All 8 Python scripts (`humanizer.py`, `fact-checker.py`, `generate-docx.py --c2pa-sign`, etc.) run when Python 3.8+ is present
- `hooks/hooks.json` (empty by default — zero global hooks, matches Claude Code v3.9+ behaviour)

**What's Claude-Code-native and isn't auto-invoked on Codex:**
- Slash commands in `commands/` (e.g., `/contentforge:run-pipeline`) — on Codex, invoke via natural language and the SKILL.md routing picks up the same handler
- 13 specialist sub-agents in `agents/*.md` — Codex has its own sub-agent / app concept (`.app.json`); ContentForge skills embed agent instructions inline so outputs are equivalent

---

## Install on Cursor

```bash
cursor plugin install indranilbanerjee/contentforge
```

After install, restart Cursor (or `Cursor: Reload Window`).

**What works on Cursor:**
- All 19 Agent Skills auto-discovered via SKILL.md frontmatter
- `hooks/hooks.json` empty by default
- All 8 Python scripts run from Cursor's terminal context

**MCP on Cursor — manual one-time configuration:**

Cursor reads MCP servers from a global `mcp.json` (no leading dot). To enable any of ContentForge's 16 opt-in HTTP MCP connectors on Cursor:

1. Open Cursor → Settings → MCP Servers
2. Copy the connector(s) you want from `.mcp.json.connectors-reference` into Cursor's MCP configuration
3. Set required env vars per connector (see `docs/integrations.md` if present, or the connector-reference comments)

This is a Cursor platform constraint, not a ContentForge limitation. Cursor's plugin-scoped MCP is not yet GA (May 2026).

**What's Claude-Code-native and isn't auto-invoked on Cursor:**
- Slash commands (`/contentforge:*`) — Cursor Agent picks the right skill from natural-language intent
- 13 specialist sub-agents — Cursor has rules and modes instead of sub-agents; skills embed agent instructions inline

---

## Install on GitHub Copilot CLI

Copilot CLI (Public Preview as of May 2026) **explicitly auto-discovers `.claude-plugin/plugin.json` as one of its plugin manifest paths**, so ContentForge installs with no additional manifest file:

```bash
copilot plugin install indranilbanerjee/contentforge
```

After install:

```
copilot ask "Run the ContentForge 10-phase pipeline for an article on EU AI Act compliance."
copilot ask "Humanize this draft against the 29-pattern AI-detection catalog."
```

**What works on Copilot CLI:**
- All 19 Agent Skills (auto-discovered via SKILL.md frontmatter)
- All 8 Python scripts run via Copilot CLI's `command` exec
- `hooks/hooks.json` (empty by default)
- `.mcp.json` 16 opt-in HTTP connectors via the `mcpServers` field in the manifest

**What's Claude-Code-native and isn't auto-invoked on Copilot CLI:**
- Slash commands (`/contentforge:*`) — invoke via `copilot ask "..."`
- 13 specialist sub-agents — ContentForge skills embed agent instructions inline; output parity preserved

---

## Install on Google Antigravity 2.0 (experimental)

Google launched **Antigravity CLI** on 19 May 2026 as the successor to Gemini CLI. Antigravity preserves Agent Skills, Hooks, Subagents, and Extensions (now rebranded as Antigravity Plugins).

> **Status: experimental.** Antigravity has not yet published an open v2-native plugin manifest spec. ContentForge ships `.antigravity/plugin.json` mirroring the Gemini CLI Extensions format that Antigravity's `agy plugin import gemini` converter accepts.

```bash
# Most reliable today — via the Gemini CLI extension converter
agy plugin import gemini

# Or via the manifest discovery (works in Antigravity 2.0 preview builds)
agy plugin install indranilbanerjee/contentforge
```

**What works on Antigravity:**
- All 19 Agent Skills (SKILL.md frontmatter — open standard)
- All 8 Python scripts run via Antigravity's shell exec
- `hooks/hooks.json` (empty by default)
- `.mcp.json` 16 opt-in connectors — Antigravity 2.0 supports MCP natively

When Antigravity publishes the v2-native plugin spec, ContentForge will ship a properly-aligned `.antigravity/plugin.json` in a follow-up release.

---

## What's portable vs platform-specific

| Component | Claude Code | Codex | Cursor | Copilot CLI | Antigravity (exp.) | Notes |
|---|---|---|---|---|---|---|
| **Skills** (`skills/<name>/SKILL.md`) | yes | yes | yes | yes | yes | Open Agent Skills standard |
| **Python scripts** (`scripts/*.py`) | yes | yes | yes | yes | yes | Run when Python 3.8+ present; graceful fallback otherwise |
| **MCP catalog** (`.mcp.json`) | yes (catalog opt-in) | yes (catalog opt-in) | manual paste into Cursor global mcp.json | yes (via `mcpServers` field) | yes | All 16 connectors are HTTP — work cross-platform |
| **Hooks** (`hooks/hooks.json`) | yes | yes | yes | yes | yes | Empty by default — zero global hooks |
| **Slash commands** (`commands/*.md`) | yes | partial | n/a (natural language) | n/a (`copilot ask`) | n/a | |
| **Sub-agents** (`agents/*.md`) | yes | partial | n/a | partial | n/a | Skills embed agent instructions inline |

---

## Updating

| Platform | Update command |
|---|---|
| Claude Code | `/plugin update contentforge@neels-plugins` |
| Codex | `codex plugin update contentforge` |
| Cursor | `cursor plugin update contentforge` |
| Copilot CLI | `copilot plugin update indranilbanerjee/contentforge` |
| Antigravity | `agy plugin update contentforge` (experimental) |

All five platforms pull from the same GitHub `master` branch.

---

## Reporting platform-specific bugs

| Platform | Where to file |
|---|---|
| Claude Code platform bug | https://github.com/anthropics/claude-code/issues |
| Codex platform bug | https://github.com/openai/codex/issues |
| Cursor platform bug | https://github.com/cursor/plugins/issues |
| Copilot CLI platform bug | https://github.com/github/copilot-cli/issues |
| Antigravity platform bug | Antigravity issue tracker (see https://antigravity.google/docs) |
| ContentForge skill/content bug (any platform) | https://github.com/indranilbanerjee/contentforge/issues |
