# ContentForge Upgrade Guide — v2.1.0 → v3.0.0 (Historical)

This guide covers the v2.1.0 → v3.0.0 migration only. For changes since v3.0.0, see the CHANGELOG.md entries for v3.1.0 through v3.16.1.

Upgrading from v2.1.0 to v3.0.0. No breaking changes.

---

## What Changed

| Category | v2.1.0 | v3.0.0 | Current (v3.16.1) |
|----------|--------|--------|-------------------|
| Skills | 3 | 17 (+14 new) | 21 |
| Agents | 10 | 12 (+2 new, 4 upgraded) | 13 |
| Commands | 0 | 0 | 9 |
| Scripts | 0 | 2 | 17 |
| Configs | 4 | 7 (+3 new, 1 updated) | 7 + 10 industry packs |
| Templates | 7 | 10 (+3 new) | 10 |
| Utilities | 2 | 6 (+4 new) | 6 |
| Connectors | 6 HTTP | 6 HTTP + 16 npx available | 16 HTTP in the opt-in catalog, **0 connected by default** |

Counts are current as of v3.16.1; the README is the authority if this table drifts.

---

## Breaking Changes

**None.** All existing skills, agents, and configurations work identically.

---

## New Skills

### Connector Discovery
- `/contentforge:cf-integrations` — See which connectors are active and what they unlock
- `/contentforge:cf-connect <name>` — Guided setup for any of the 29 connectors in the registry

### Publishing & Social
- `/contentforge:social-adapt` — Transform articles into LinkedIn, Twitter/X, Instagram, Facebook, Threads posts
- `/contentforge:publish` — Push content to Webflow/WordPress via MCP, or export as HTML

### Content Optimization
- `/contentforge:cf-variants` — Generate 3-10 A/B variations of headlines, hooks, CTAs
- `/contentforge:cf-analytics` — Quality score trends, timing breakdown, brand performance

### Multilingual & Video
- `/contentforge:translate` — Translate preserving brand voice, 15+ languages, 3 localization levels
- `/contentforge:cf-video-script` — Timestamped scripts for YouTube, TikTok, Instagram Reels

### Content Management
- `/contentforge:cf-brief` — Research-backed content brief with keyword analysis and outline
- `/contentforge:cf-audit` — Content freshness scoring, decay detection, gap analysis
- `/contentforge:cf-calendar` — Production scheduling with deadline tracking
- `/contentforge:cf-style-guide` — Import brand voice, generate brand profile JSON
- `/contentforge:cf-template` — Create custom content type templates

---

## Agent Upgrades

### Output Manager (Phase 8)
5 new output formats: Medium article, Substack post, email newsletter, PDF export, social media package.

### SEO/GEO Optimizer (Phase 6)
New Step 7: AI Overview Optimization — structures content for Google AI Overviews and Perplexity answers. Adds GEO score to SEO Scorecard.

### Humanizer (Phase 6.5)
- New Step 6: Personality Profile Selection — 4 profiles (authoritative, conversational, technical, witty)
- New Step 7: Industry-Specific AI Pattern Removal — 5 industries (healthcare, finance, tech, legal, education)

### Reviewer (Phase 7)
- New Step 6: Comparative Scoring — percentile ranking vs. brand history
- New Step 7: Trend Tracking — pattern detection across last 10 pieces
- New Step 8: Recommendation Engine — score-based next steps with cross-skill suggestions

---

## Scripts (New)

v3.0.0 introduces a `scripts/` directory with Python utilities:

- **`setup.py`** — Run it manually (`python scripts/setup.py`) when you want to check your install. Validates Python version, reports paths, checks `.mcp.json`. It does **not** run on its own — ContentForge has shipped an empty `hooks.json` since v3.9.0, so nothing fires at session start
- **`connector-status.py`** — Registry of 29 connectors across 14 categories. Powers `/contentforge:cf-integrations` and `/contentforge:cf-connect`

**Requirements:** Python 3.8+ (available in Cowork VM as Python 3.10)

---

## Verification Steps

After upgrading, verify everything works:

1. `python scripts/setup.py` — Run it yourself; should report your Python version and resolved paths
2. `/contentforge:cf-integrations` — A fresh install shows **0 connected** connectors: `.mcp.json` ships empty by design. Add the ones you want with `/contentforge:cf-connect <name>` from the 16-connector catalog in `.mcp.json.connectors-reference`
3. `/contentforge:create-content` — Existing pipeline should work unchanged
4. `/contentforge:social-adapt [article]` — Should generate social posts
5. `/contentforge:cf-brief "AI tools"` — Should generate content brief

---

## Recommended Adoption Path

1. **Start with** `/contentforge:cf-integrations` — understand your connector status
2. **Try** `/contentforge:social-adapt` — immediate value from existing content
3. **Try** `/contentforge:cf-brief` — better briefs lead to better content
4. **Explore** `/contentforge:publish` — if you have Webflow/WordPress connectors
5. **Set up** `/contentforge:cf-analytics` — start tracking quality trends
6. **When ready** — `/contentforge:translate`, `/contentforge:cf-video-script`, `/contentforge:cf-calendar`

---

## Questions?

- [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- [CHANGELOG.md](CHANGELOG.md) for full details
