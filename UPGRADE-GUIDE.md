# ContentForge v3.0.0 Upgrade Guide

Upgrading from v2.1.0 to v3.0.0. No breaking changes.

---

## What Changed

| Category | v2.1.0 | v3.0.0 |
|----------|--------|--------|
| Skills | 3 | 17 (+14 new) |
| Agents | 10 | 12 (+2 new, 4 upgraded) |
| Scripts | 0 | 2 |
| Configs | 4 | 7 (+3 new, 1 updated) |
| Templates | 7 | 10 (+3 new) |
| Utilities | 2 | 6 (+4 new) |
| Connectors | 6 HTTP | 6 HTTP + 16 npx available |

---

## Breaking Changes

**None.** All existing skills, agents, and configurations work identically.

---

## New Skills

### Connector Discovery
- `/cf:integrations` — See which connectors are active and what they unlock
- `/cf:connect <name>` — Guided setup for any of 22 supported connectors

### Publishing & Social
- `/cf:social-adapt` — Transform articles into LinkedIn, Twitter/X, Instagram, Facebook, Threads posts
- `/cf:publish` — Push content to Webflow/WordPress via MCP, or export as HTML

### Content Optimization
- `/cf:variants` — Generate 3-10 A/B variations of headlines, hooks, CTAs
- `/cf:analytics` — Quality score trends, timing breakdown, brand performance

### Multilingual & Video
- `/cf:translate` — Translate preserving brand voice, 15+ languages, 3 localization levels
- `/cf:video-script` — Timestamped scripts for YouTube, TikTok, Instagram Reels

### Content Management
- `/cf:brief` — Research-backed content brief with keyword analysis and outline
- `/cf:audit` — Content freshness scoring, decay detection, gap analysis
- `/cf:calendar` — Production scheduling with deadline tracking
- `/cf:style-guide` — Import brand voice, generate brand profile JSON
- `/cf:template` — Create custom content type templates

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

- **`setup.py`** — Runs automatically on session start via hooks. Validates Python version, reports paths, checks .mcp.json
- **`connector-status.py`** — Registry of 22 connectors across 12 categories. Powers `/cf:integrations` and `/cf:connect`

**Requirements:** Python 3.8+ (available in Cowork VM as Python 3.10)

---

## Verification Steps

After upgrading, verify everything works:

1. **Session startup** — Should show setup.py output + v3.0 banner
2. `/cf:integrations` — Should show 6 connected HTTP connectors
3. `/contentforge` — Existing pipeline should work unchanged
4. `/cf:social-adapt [article]` — Should generate social posts
5. `/cf:brief "AI tools"` — Should generate content brief

---

## Recommended Adoption Path

1. **Start with** `/cf:integrations` — understand your connector status
2. **Try** `/cf:social-adapt` — immediate value from existing content
3. **Try** `/cf:brief` — better briefs lead to better content
4. **Explore** `/cf:publish` — if you have Webflow/WordPress connectors
5. **Set up** `/cf:analytics` — start tracking quality trends
6. **When ready** — `/cf:translate`, `/cf:video-script`, `/cf:calendar`

---

## Questions?

- [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- [CHANGELOG.md](CHANGELOG.md) for full details
