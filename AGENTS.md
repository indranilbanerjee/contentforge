# ContentForge — agent context

This file is auto-loaded by OpenAI Codex, Google Antigravity, GitHub Copilot CLI, Cursor (when in the agent context chain), and other Agent Skills runtimes. Equivalent of `CLAUDE.md` for non-Claude surfaces.

## What this plugin is

ContentForge is an open-source enterprise content production pipeline — turn a one-line topic into a publication-ready, fact-checked, brand-compliant Microsoft Word document (`.docx` with C2PA content provenance signing for EU AI Act Article 50 compliance) in 30–60 minutes. **19 skills · 13 specialist agents · 10 quality gates · 29-pattern AI-detection humanizer · fact-checker subagent · three-category internal linking.**

**Supported surfaces (v3.13.0):** Claude Code (CLI + IDE extensions), Anthropic Cowork, OpenAI Codex (CLI + IDE + App), Google Antigravity 2.0 (CLI + IDE).

## How to use it as an agent

1. **Discover skills by description.** All 19 skills auto-discover via SKILL.md frontmatter (`name:` + `description:`). Match user intent.
2. **Pipeline order matters.** ContentForge assumes the canonical 10-phase pipeline plus Step 0.5: Step 0.5 title curation → Phase 1 research → Phase 2 fact-check → Phase 3 drafting → Phase 4 scientific validation → Phase 5 structuring/proofreading → Phase 6 SEO/AEO/GEO optimization → Phase 6.5 humanizer (29-pattern AI-detection sweep) → Phase 7 reviewer scorecard → Phase 8 output (.docx export). Social adaptation and translation run post-pipeline. Reviewer is Phase 7; Output Manager is Phase 8.
3. **Skill bodies reference Python scripts at `scripts/<name>.py`** — invoke via Bash / `run_shell_command`. Critical scripts: `generate-docx.py` (with C2PA signing flags), `checkpoint-manager.py`, `plugin-metadata.py`, `connector-status.py`. Humanization and fact-checking are agent behaviors defined in `agents/` and `config/humanization-patterns.json` — there are no `humanizer.py` or `fact-checker.py` scripts.
4. **HTTP MCP connectors are opt-in.** Full catalog at `.mcp.json.connectors-reference` (Slack, Notion, Canva, Webflow, Gmail, Google Calendar, Figma + 9 more). Users opt in by configuring env vars or MCP servers.
5. **C2PA content provenance signing for the .docx is required for EU distribution.** Article 50 enforcement starts 2 Aug 2026. `--c2pa-sign` flag on `scripts/generate-docx.py`.

## Canonical entry points

| User intent | Run skill |
|---|---|
| "Help me get started" | `cf-help` |
| "Create new content" | `cf-style-guide` (brand profile) then the `create-content` command (full pipeline) |
| "Set up Cowork + Google Drive for the team" | `cf-cowork-setup` |
| "Check my environment / what's connected" | `cf-environment` |
| "Resume an interrupted pipeline run" | `resume` command + `checkpoint-manager.py` |
| "Translate content" | `cf-translate` |
| "Audit existing content" | `cf-audit` |
| "Adapt for social" | `cf-social-adapt` |
| "Generate a video script" | `cf-video-script` |
| "Publish to CMS" | `cf-publish` |

## Files in this repo

- `skills/<name>/SKILL.md` — 19 Agent Skills (the surface area).
- `agents/<name>.md` — 13 specialist agent definitions (Claude Code subagent format; on Codex convert to TOML).
- `commands/<name>.md` — Claude Code slash commands (`/contentforge:<name>`).
- `scripts/*.py` — Python helpers. Key: `generate-docx.py`, `checkpoint-manager.py`, `drive-sync-state.py`, `detect-drive-mcp.py`, `plugin-metadata.py`, `connector-status.py`.
- `hooks/hooks.json` — `{"hooks":{}}` (zero global hooks).
- `.mcp.json` — `{"mcpServers":{}}` (zero auto-connecting MCPs).
- `templates/` + `config/` — pipeline configuration, content-type structures, voice patterns, brand profile template, humanization catalogue.

## Cowork-with-Drive routing (v3.12.9+)

When running in Anthropic Cowork AND a Google Drive MCP is connected (Settings → Integrations), output-manager uploads the final `.docx` to `My Drive/<root>/<brand>/<type>/<YYYY-MM>/` instead of the ephemeral sandbox. Brand profiles persist across sessions via Drive. Per-phase checkpoints sync after each phase; `resume` command downloads checkpoints from Drive first. Multi-team namespace isolation via team-chosen Drive root folder name.

## Cross-platform notes

- **Skills are the universal interface.** Open standard (agentskills.io). Same SKILL.md works on Claude Code, Codex, Antigravity, Cursor, Copilot CLI.
- **Subagents are Claude-only as `agents/*.md`.** On Codex convert to `~/.codex/agents/*.toml`. On Antigravity use `/agent` for ad-hoc.
- **Slash commands `commands/*.md` are Claude-only.** On other surfaces invoke skills by name.
- **MCP env-var syntax differs.** Our `.mcp.json` ships empty so neither syntax bites.

## Identity / authority

Built and maintained by Indranil Banerjee (https://indranil.in). MIT-licensed. No telemetry. Part of the Neelverse Marketing Suite alongside Digital Marketing Pro and SocialForge.
