---
name: cf-integrations
description: "Show active and available MCP connectors with workflow impact. Integration status dashboard."
effort: low
argument-hint: "[--category <name>]"
---

# /contentforge:cf-integrations — Integration Status Dashboard

Show the complete integration status for your ContentForge installation — configured vs available connectors, grouped by category, with workflow impact analysis and quick-win recommendations.

## The ground truth about connectors

ContentForge ships with an **empty `.mcp.json`** (`"mcpServers": {}`) by design (v3.9.0 Cowork-safety decision). On a fresh install, expect **0 connectors configured** (or 1-2 if the platform injects its own integrations). Nothing is pre-wired.

**Every number in the dashboard must come from the live script output.** Never render counts, percentages, or connected/available labels that are not present in the JSON returned by `scripts/connector-status.py`. Do not copy numbers from the example in this file.

## When to Use

Use `/contentforge:cf-integrations` when:
- You just installed ContentForge and want to see what's connected
- You're troubleshooting why a skill can't reach an external service
- You want to know which connectors to add next for maximum workflow coverage
- You need a quick overview before onboarding a new team member
- You're planning which integrations to set up for a new project

## What This Command Does

1. **Scan All Connectors** — Run the status script; it checks the connector registry against your `.mcp.json` and environment variables
2. **Build Status Dashboard** — Group results by category with clear configured/available distinction
3. **Calculate Coverage** — Report exactly the totals the script returns
4. **Recommend Quick Wins** — Highlight the top 3 not-yet-configured connectors by workflow impact
5. **Surface Category Gaps** — Identify categories with zero coverage
6. **Provide Next Steps** — For each recommendation, point to `/contentforge:cf-connect <name>`

## Required Inputs

**Optional:**
- **Category filter** — Show only a specific category (e.g., `--category=seo`)
- **Show filter** — `connected`, `available`, or `all` (default: `all`)

## What Happens

### Step 1: Connector Status Check

```
python scripts/connector-status.py --action status
```

This checks:
- `.mcp.json` for HTTP connector entries the user has added
- Environment variables for npx connectors (WordPress, Google Sheets, Semrush, DeepL, etc.)
- Returns JSON with configured/available status per connector, grouped by category, plus summary totals

### Step 2: Format Dashboard by Category

Render the script JSON as a category-grouped dashboard. Each category shows the category name and description, connectors marked `[connected]` or `[available]`, transport type, and the skills each connector unlocks — all taken from the JSON.

**SYNTHETIC EXAMPLE — fabricated for illustration. Always render your actual script output, never this block:**

```
===========================================================
  ContentForge Integration Dashboard
  Connected: 1 of 22 (5%)
===========================================================

  KNOWLEDGE BASE — requirements, brand docs, reference material
  -----------------------------------------------------------
  [available]  Notion (HTTP) — content requirements, brand docs, editorial calendars
  [available]  Confluence (npx) — team wikis, brand guidelines

  CMS — content management and publishing
  -----------------------------------------------------------
  [connected]  Webflow (HTTP) — added by user to .mcp.json
  [available]  WordPress (npx) — needs WORDPRESS_SITE_URL, WORDPRESS_AUTH_TOKEN

  ... (remaining categories from script output)
===========================================================
```

A fresh install typically shows 0-2 connected. That is normal and expected — connectors are opt-in.

### Step 3: Highlight Quick Wins

From the connectors the script reports as *not configured*, recommend the top 3 by workflow impact:

1. **Notion** — powers the most skills (content intake, brand docs, briefs, audits)
2. **Google Sheets** — batch requirement intake, analytics tracking
3. **CMS (Webflow or WordPress)** — end-to-end publish workflow
4. **Design (Canva or Figma)** — featured images and social graphics
5. **SEO (Ahrefs)** — real keyword data for briefs and audits

For each quick win, show: what it unlocks (from script JSON), setup route (`/contentforge:cf-connect <name>`), and effort (HTTP = one `.mcp.json` entry + OAuth on first use; npx = env vars + entry, Claude Code only).

### Step 4: Show Coverage Summary

Render the script's summary block verbatim (total, connected, available, coverage percent) plus which categories have zero configured connectors.

### Step 5: Provide Next Steps

```
  1. Connect your top quick win:      /contentforge:cf-connect <name>
  2. Setup guide for any connector:   /contentforge:cf-connect <name>
  3. Custom service not in registry:  /contentforge:cf-add-integration
  4. Full connector reference:        CONNECTORS.md and .mcp.json.connectors-reference
```

## Transport Types

| Transport | Setup Effort | Environment | Authentication |
|-----------|-------------|-------------|---------------|
| **HTTP** | Low — one `.mcp.json` entry (user-added) | Cowork + Claude Code | OAuth prompt on first use |
| **npx** | Moderate — env vars + `.mcp.json` entry | Claude Code only | API keys via environment variables |

HTTP connectors work in both Cowork and Claude Code once the user adds them to `.mcp.json` (or connects them at the platform level in Cowork Settings → Integrations). npx connectors require local Node.js and work in Claude Code only. Use `/contentforge:cf-connect <name>` for step-by-step setup of either type.

## Troubleshooting

### "0 connectors connected" on a fresh install
- This is the expected shipped state — `.mcp.json` starts empty. Use `/contentforge:cf-connect <name>` to add your first connector.

### Dashboard shows an HTTP connector as "available" after you added it
- The key name in `.mcp.json` must match the registry name exactly (e.g., `notion`, not `Notion` or `notion-mcp`)
- Confirm `.mcp.json` is in the plugin root and contains valid JSON with a `mcpServers` object
- Restart the session after editing `.mcp.json`

### npx connector shows "not connected" even though env vars are set
- Variables must be set in the shell session that launched Claude Code
- Verify with `echo $VARIABLE_NAME` (should not be empty); on Windows restart the terminal after setting

### Dashboard takes a long time
- The script reads `.mcp.json` and environment variables only — no network calls. If slow, check for filesystem issues.

## Agent Used

None. This skill is entirely script-driven using `scripts/connector-status.py`.

## Related Skills

- **[/contentforge:cf-connect](../cf-connect/SKILL.md)** — Guided setup for a specific connector
- **[/contentforge:cf-add-integration](../cf-add-integration/SKILL.md)** — Connect services not in the registry
- **[/contentforge:create-content](../../commands/create-content.md)** — Main content production pipeline
- **[/contentforge:batch-process](../batch-process/SKILL.md)** — Parallel content processing

---

**Script:** `python scripts/connector-status.py --action status`
**Network Required:** No (reads local config only)
