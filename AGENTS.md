# ContentForge — agent context

This file is auto-loaded by OpenAI Codex, Google Antigravity, GitHub Copilot CLI, Cursor (when in the agent context chain), and other Agent Skills runtimes. Equivalent of `CLAUDE.md` for non-Claude surfaces.

## What this plugin is

ContentForge is an open-source enterprise content production pipeline — turn a one-line topic into a publication-ready, fact-checked, brand-compliant Microsoft Word document (`.docx` with C2PA content provenance signing for EU AI Act Article 50 compliance) in 30–60 minutes. **22 skills · 13 specialist agents · 8 built-in content types · 10 quality gates · 41-pattern AI-detection humanizer · fact-checker subagent · three-category internal linking · author/E-E-A-T byline layer.**

**Supported surfaces (v3.20.0):** Claude Code (CLI + IDE extensions), Anthropic Cowork, OpenAI Codex (CLI + IDE + App), Google Antigravity 2.0 (CLI + IDE).

## How to use it as an agent

1. **Discover skills by description.** All 22 skills auto-discover via SKILL.md frontmatter (`name:` + `description:`). Match user intent.
2. **Pipeline order matters.** ContentForge assumes the canonical 10-phase pipeline plus Step 0.5: Step 0.5 title curation → Step 0 Client Site Reconnaissance (brand facts + Internal-Link Inventory, required when the brand has a website) → Phase 1 research → Phase 2 fact-check → Phase 3 drafting → Phase 4 scientific validation → Phase 5 structuring/proofreading → Phase 6 SEO/AEO/GEO optimization (deep-link rule + thin-`brand_pages` guard) → Phase 6.5 humanizer (41-pattern AI-detection sweep, grounding-first) → Phase 7 reviewer scorecard → Phase 8 output (.docx export). Social adaptation and translation run post-pipeline. Reviewer is Phase 7; Output Manager is Phase 8.
3. **Skill bodies reference Python scripts at `scripts/<name>.py`** — invoke via Bash / `run_shell_command`. Critical scripts: `generate-docx.py` (with C2PA signing flags), `checkpoint-manager.py`, `plugin-metadata.py`, `connector-status.py`, `harvest-brand-pages.py` (stdlib, robots-respecting site crawler used by brand-setup), `text-metrics.py` (burstiness/FK/placement gates plus `--ai-tell-scan`). Humanization and fact-checking are agent behaviors defined in `agents/` and `config/humanization-patterns.json` — there are no `humanizer.py` or `fact-checker.py` scripts.
4. **HTTP MCP connectors are opt-in.** Full catalog at `.mcp.json.connectors-reference` (Slack, Notion, Canva, Webflow, Gmail, Google Calendar, Figma + 9 more). Users opt in by configuring env vars or MCP servers.
5. **C2PA content provenance signing for the .docx is required for EU distribution.** Article 50 enforcement starts 2 Aug 2026. `--c2pa-sign` flag on `scripts/generate-docx.py`.
6. **AI-detectability is advisory, never a gate.** `text-metrics.py --ai-tell-scan` is a deterministic, dependency-free proxy scan (aphorism density, banned lexemes, connective/participial openers, uniform runs) that reports a LOW/MODERATE/HIGH rating, surfaced in the Phase 6.5 report, the reviewer's Readability sub-score, and the Completion Card. It never blocks publication and the pipeline never claims to "beat" any specific detector — see `references/ai-detection-signals.md` for the reasoning it's built on.

## Canonical entry points

| User intent | Run skill |
|---|---|
| "Help me get started" | `cf-help` |
| "Create new content" | `cf-style-guide` (brand profile) then the `create-content` command (full pipeline) |
| "Set up Cowork + Google Drive for the team" | `cf-cowork-setup` |
| "Check my environment / what's connected" | `cf-environment` |
| "Resume an interrupted pipeline run" | `resume` command + `checkpoint-manager.py` |
| "Set up a brand profile with a real site inventory" | `brand-setup` (auto-harvests `brand_pages` + `brand_facts` via `harvest-brand-pages.py` when a website is given, one confirmation step) |
| "Translate content" | `cf-translate` |
| "Audit existing content" | `cf-audit` |
| "Adapt for social" | `cf-social-adapt` |
| "Generate a video script" | `cf-video-script` |
| "Publish to CMS" | `cf-publish` |
| "Did AI engines cite my published piece?" | `cf-aeo-check` |
| "Write a client case study" | `create-content` command with content type `case_study` (client data supplied at intake — never fabricated) |
| "Write our newsletter" | `create-content` command with content type `newsletter` |

## Files in this repo

- `skills/<name>/SKILL.md` — 22 Agent Skills (the surface area).
- `agents/<name>.md` — 13 specialist agent definitions (Claude Code subagent format; on Codex convert to TOML).
- `commands/<name>.md` — Claude Code slash commands (`/contentforge:<name>`).
- `scripts/*.py` — Python helpers. Key: `generate-docx.py`, `checkpoint-manager.py`, `drive-sync-state.py`, `detect-drive-mcp.py`, `plugin-metadata.py`, `connector-status.py`, `harvest-brand-pages.py`, `text-metrics.py`.
- `hooks/hooks.json` — `{"hooks":{}}` (zero global hooks).
- `.mcp.json` — `{"mcpServers":{}}` (zero auto-connecting MCPs).
- `templates/` + `config/` — pipeline configuration, content-type structures, voice patterns, brand profile template, humanization catalogue (41-pattern catalog).
- `references/ai-detection-signals.md` — internalized AI-detector knowledge base (what detectors measure, why grounding beats tricks, the two hard guardrails).

## Cowork-with-Drive routing (v3.12.9+)

When running in Anthropic Cowork AND a Google Drive MCP is connected (Settings → Integrations), output-manager uploads the final `.docx` to `My Drive/<root>/<brand>/<type>/<YYYY-MM>/` instead of the ephemeral sandbox. Brand profiles persist across sessions via Drive. Per-phase checkpoints sync after each phase; `resume` command downloads checkpoints from Drive first. Multi-team namespace isolation via team-chosen Drive root folder name.

## Cross-platform notes

- **Skills are the universal interface.** Open standard (agentskills.io). Same SKILL.md works on Claude Code, Codex, Antigravity, Cursor, Copilot CLI.
- **Subagents are Claude-only as `agents/*.md`.** On Codex convert to `~/.codex/agents/*.toml`. On Antigravity use `/agent` for ad-hoc.
- **Slash commands `commands/*.md` are Claude-only.** On other surfaces invoke skills by name.
- **MCP env-var syntax differs.** Our `.mcp.json` ships empty so neither syntax bites.

## Identity / authority

Built and maintained by Indranil Banerjee (https://indranil.in). MIT-licensed. No telemetry. Part of the Neelverse Marketing Suite.
