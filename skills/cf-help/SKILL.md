---
name: cf-help
description: "Show the ContentForge user guide, available skills, pipeline overview, examples, and troubleshooting"
argument-hint: "[--pipeline | --skills | --commands | --examples | --connectors | --troubleshoot | --brand]"
effort: low
---

# /contentforge:cf-help

Show the ContentForge user guide with live plugin state (version, asset counts, connector counts, runtime environment) pulled from disk — not hardcoded — plus pipeline overview, available skills, usage examples, and troubleshooting.

## CRITICAL: never hardcode version, asset counts, or connector counts

Versions and counts in this plugin used to be baked into this skill body as
literal version strings and count strings ("Agents: 13 · Skills: 19 ·
Connectors: 9 HTTP + 19 npx"). Those drifted out of sync with the actual
install every release (reported by users in v3.12.7 testing: "I'm on 3.12.7,
but the help output shows an old version").

**Always read live values from `scripts/plugin-metadata.py`. Never quote a
version number, skill count, agent count, or connector count from memory or
from this skill body.**

## Behavior

### Step 1 — Fetch live plugin metadata

Run **first**, every time this skill is invoked (any argument or none):

```bash
python scripts/plugin-metadata.py --section all-with-environment
```

This returns JSON with `version`, `assets` (agent/skill/command/script counts),
`connectors` (HTTP + npx counts), `skills` list, `commands` list,
`pipeline_phases` list (read from agent file names), and `environment`
(detects Cowork sandbox vs local Claude Code, with a warning if filesystem
writes won't reach the user's host).

Substitute the values from this JSON into every place the help output
references a count, a version, or a slash-command list. Do **not** invent
or quote numbers from elsewhere.

### Step 2 — Default rendering (no args)

Render a clean help overview using the live data. Suggested format:

```
=== CONTENTFORGE ===
Version: <version from JSON>
Agents: <agents> | Skills: <skills_total> | Commands: <commands> | Scripts: <scripts>
Connectors: <available_http> HTTP + <available_npx> npx available
  (<active_count> currently active in your .mcp.json)
  Cowork-compatible: <cowork_compatible_count> (HTTP only — npx connectors don't run in Cowork)
Environment: <environment from JSON>
<if environment.cowork_warning is non-null, show it as a WARNING block>

Getting Started:
  1. /contentforge:brand-setup           -- Configure brand voice, terminology, guardrails
  2. /contentforge:cf-integrations       -- See which connectors are active
  3. /contentforge:create-content        -- Run the full content pipeline
  4. /contentforge:cf-help --examples    -- Worked example workflows
```

### Step 3 — Cowork warning (when applicable)

If `environment.cowork_warning` is non-null, surface it prominently after
the orientation block:

```
⚠ COWORK SANDBOX DETECTED
<cowork_warning text from JSON>

What this means in practice:
  - File writes to ~/Documents/ContentForge/ and ~/.claude-marketing/
    land inside the sandbox, NOT on your Windows / macOS host
  - Files persist only for this Cowork session
  - The full /contentforge:create-content pipeline can run, but the
    dual-copy save and per-phase checkpointing target the sandbox FS
  - For full host-filesystem behavior, run ContentForge in local
    Claude Code (CLI or VS Code / JetBrains IDE extension) instead
```

### Step 4 — Argument routing

| Argument | What to render |
|----------|---------------|
| (none) | Steps 2 + 3 + Quick command list |
| `--pipeline` | Steps 2 + 3 + full phase-by-phase overview (use `pipeline_phases` from JSON) |
| `--skills` | Steps 2 + 3 + list every skill from JSON `skills` array with slash command + description |
| `--commands` | Steps 2 + 3 + list every command from JSON `commands` array with slash command + description |
| `--connectors` | Steps 2 + 3 + redirect: "For active/available connector status, run /contentforge:cf-integrations" |
| `--examples` | Steps 2 + 3 + the worked-example workflows (see below) |
| `--troubleshoot` | Steps 2 + 3 + troubleshooting matrix (see below) |
| `--brand` | Steps 2 + 3 + brand setup methods (see below) |

When rendering the skills/commands list, **iterate over the JSON arrays** —
do not paste a hand-maintained list. Each row should show the
`slash_command` field as the user-facing label and the `description` field
as the explanation.

### Pipeline phase rendering (--pipeline)

The pipeline phases come from agent file names (`01-researcher.md` →
"Phase 01: Researcher"). Iterate `pipeline_phases` from the JSON and render
phase + role + description. Add this preamble:

```
=== CONTENTFORGE PIPELINE (10 phases) ===
Step 0.5: Title Curation runs BEFORE Phase 1 (SERP recon + 4-5 SEO title options;
          user selects before draft starts).

Quality gates: composite score >=7.0 to pass | max 2 loops per phase |
3-layer verification (Fact Checker -> Scientific Validator -> Reviewer).
```

Then list every phase from the JSON. **Do not invent timing estimates** —
they vary by topic complexity and model speed. If the agent description in
the JSON includes a timing hint, surface it; otherwise omit.

### Brand setup rendering (--brand)

Show the three brand-setup methods (interactive / JSON template / Drive Knowledge Vault), referencing the actual current commands. v3.12.7 added Drive MCP autodetection at the start of brand-setup — call this out as the recommended path for Cowork and Anthropic-platform users.

```
=== BRAND PROFILE SETUP (3 methods) ===

Method 1: Interactive (recommended)
  /contentforge:brand-setup "Brand Name"
  -> Walks you through voice, terminology, industry, guardrails
  -> v3.12.7+ first probes .mcp.json for Drive MCPs (Anthropic platform
     integration, Pipedream / Composio / Zapier / Make Drive aggregator)
     and short-circuits the legacy service-account flow if one is found

Method 2: Manual JSON
  -> Copy config/brand-registry-template.json
  -> Fill in your brand details
  -> Save to ~/.claude-marketing/<brand-slug>/profile.json

Method 3: Google Drive Knowledge Vault
  -> Create a Drive folder: <Brand Name>/
  -> Subfolders: Brand-Guidelines/, Guardrails/, Reference-Content/
  -> Run /contentforge:brand-setup -- it will offer to verify or
     scaffold the structure
```

### Troubleshooting (--troubleshoot)

Surface this matrix. Use the live skill/command names from the JSON; the
table below references the user-visible behaviors.

| Issue | What to try |
|-------|-------------|
| "Brand profile not found" | Run `/contentforge:brand-setup` to create the brand profile first |
| Files don't appear in ~/Documents/ContentForge/ | Check Cowork sandbox warning above. In local Claude Code: `/contentforge:output-folder` shows the resolved path; verify `CONTENTFORGE_PUBLISH_DIR` env var if you've customized it |
| Headers in .docx aren't semantic Heading 1/2/3 | Verified fixed in v3.12.4 -- if you see this, you're on an older version; run `/plugin update contentforge@neels-plugins` |
| Pipeline interrupted, lost work | Use `/contentforge:resume` to pick up from the last completed phase (v3.12.3+) |
| Google Drive connector ignored at brand-setup | Fixed in v3.12.7. Run `python scripts/detect-drive-mcp.py` to verify the autodetect can see your MCP |
| Quality score below 5.0 | Content flagged for human review -- check topic complexity, source availability, and brand profile completeness |
| Pipeline taking too long | Normal: 20-30 min for articles. Use batch-process from a Google Sheet for parallel runs |

### Documentation references

| Guide | What it covers |
|-------|---------------|
| `docs/USER-GUIDE.md` | Comprehensive end-to-end guide |
| `CHANGELOG.md` | Full version history (the canonical record of what's in your install) |
| `CONNECTORS.md` | Connector categories and setup paths |
| `config/brand-registry-template.json` | Brand profile JSON template |

## Output formatting rules

- Render in clean, scannable tables and code blocks
- **Always** quote `version` and counts from the JSON, never from this file
- Match each user invocation argument to its section above; the help body
  contains only instructions, not pre-rendered output
- If `scripts/plugin-metadata.py` fails to run (e.g. Python not available),
  fall back to: "Live metadata script could not run. Plugin version is in
  .claude-plugin/plugin.json; skill list is in skills/; command list is in
  commands/." Do not invent numbers in the fallback either.

## What this skill explicitly avoids

- Quoting version numbers from this file body
- Quoting count strings ("13 agents", "19 skills") from this file body
- Listing slash commands manually -- always derived from the JSON
- Personalized advice for any specific user (this skill is for everyone)
- Stale references to deprecated skill names (always use the names from JSON)
