# ContentForge

**Open-source enterprise content production pipeline** — turn a one-line topic into a publication-ready, fact-checked, brand-compliant Microsoft Word document (`.docx` with C2PA content provenance signing for EU AI Act Article 50 compliance) in 30–60 minutes. **19 skills · 13 specialist agents · 11 quality gates · 29-pattern AI-detection humanizer.** Installs on **5 coding-agent surfaces**: Claude Code, Claude Cowork, OpenAI Codex, Cursor, GitHub Copilot CLI, and Google Antigravity 2.0 (experimental).

Built for marketing teams producing high volumes of long-form content (articles, white papers, FAQs, research papers) that need brand voice consistency, citation integrity, and an internal-link strategy that turns content into a funnel. Created by [Indranil Banerjee](https://indranil.in).

[![Version](https://img.shields.io/badge/version-3.12.5-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/indranilbanerjee/contentforge?style=flat&logo=github&color=yellow)](https://github.com/indranilbanerjee/contentforge/stargazers)
[![Forks](https://img.shields.io/github/forks/indranilbanerjee/contentforge?style=flat&logo=github&color=blue)](https://github.com/indranilbanerjee/contentforge/network/members)
[![Issues](https://img.shields.io/github/issues/indranilbanerjee/contentforge?logo=github)](https://github.com/indranilbanerjee/contentforge/issues)
[![Last commit](https://img.shields.io/github/last-commit/indranilbanerjee/contentforge?logo=github)](https://github.com/indranilbanerjee/contentforge/commits/master)
[![Cowork](https://img.shields.io/badge/cowork-compatible-purple.svg)](#cross-platform-compatibility)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Article%2050%20ready-darkred.svg)](docs/c2pa-production-cert.md)
[![5 platforms](https://img.shields.io/badge/installs%20on-5%20platforms-success.svg)](docs/cross-platform-install.md)

```bash
# Install — one line on any of 5 supported platforms
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

> If ContentForge saves your team time, [give it a star ⭐](https://github.com/indranilbanerjee/contentforge/stargazers) — it's the single thing that helps other marketing teams find it.

---

## Why ContentForge

Most AI writing tools produce one draft, in one tone, with no quality gates. The output reads like AI, factual claims are unverified, internal links don't exist, brand voice drifts, and the file format is markdown when the editor wants Word. ContentForge fixes this end-to-end:

| Capability | Why it matters |
|---|---|
| **11-phase pipeline with quality gates after each phase** | Bad output is caught and re-run before it propagates downstream |
| **29-pattern AI-detection humanizer** + self-critique meta-pass | Output reads human, not AI — passes GPTZero / Originality.ai checks |
| **Fact-checker subagent** verifies URLs and cross-references claims | Citations work and aren't hallucinated |
| **Three-category internal linking** (topical / commercial / authority) | Content becomes a funnel, not a stranded page |
| **Real `.docx` output** with embedded SEO + Quality + Production + Internal-Link appendices | Editor / design team gets a working Word file, not markdown |
| **C2PA content provenance signing** for EU AI Act Article 50 compliance | Long-form AI-written content distributed in EU markets needs provenance from 2 Aug 2026 |
| **Single `skills/` directory portable across 5 platforms** | Same content workflow on Claude Code / Codex / Cursor / Copilot CLI / Antigravity |

---

## Installs on 5 coding-agent surfaces (one repo, no fork)

| Platform | Install command | Status |
|---|---|---|
| **Claude Code** CLI + Desktop + **Anthropic Cowork** | `/plugin install contentforge@neels-plugins` | Full support (canonical) |
| **OpenAI Codex** CLI | `codex plugin install indranilbanerjee/contentforge` | Full support |
| **Cursor** IDE + CLI | `cursor plugin install indranilbanerjee/contentforge` | Skills + scripts; MCP via Cursor's global `mcp.json` |
| **GitHub Copilot CLI** | `copilot plugin install indranilbanerjee/contentforge` | Full support — auto-discovers `.claude-plugin/plugin.json` |
| **Google Antigravity 2.0** CLI | `agy plugin install indranilbanerjee/contentforge` | **Experimental** — manifest will firm up as Antigravity publishes v2-native spec |

Agent Skills became an open standard (Dec 2025; adopted by 32+ tools by May 2026), so the same 19 SKILL.md files work everywhere. Full per-platform install guide: [`docs/cross-platform-install.md`](docs/cross-platform-install.md).

---

## Quick start

### 1. Install the plugin

```bash
# Add the marketplace (one time)
/plugin marketplace add indranilbanerjee/neels-plugins

# Install ContentForge
/plugin install contentforge@neels-plugins
```

> Tested in Claude Code CLI, Claude Code Desktop, and Anthropic Cowork. Web chat (`claude.ai`) does not support `/plugin` commands.

### 2. Turn on auto-update (one-time, recommended)

**Third-party marketplaces — including this one — have auto-update OFF by default in Claude Code.** When v3.12.5 is the marketplace's latest and you're still running v3.12.0, nothing tells you. There's no banner, no badge, no notification. So the first thing to do after install is enable updates:

Open `/plugin`, go to the **Marketplaces** tab, find `neels-plugins`, and toggle **Enable auto-update**. Done — Claude Code will refresh and pull new ContentForge releases at startup from now on, prompting you to run `/reload-plugins` to pick up changes mid-session (no full restart, conversation context preserved).

If you'd rather update manually each time instead, see the [Updating](#updating) section below.

### 3. Set up your first brand

```
/contentforge:brand-setup
```

The agent walks you through brand voice, terminology, guardrails, citation rules, internal-linking site structure, and (if you want commercial impact) the **brand_pages** block — your product/service URLs, conversion CTAs, and authority pages. It saves a `brand-profile.json` to `~/.claude-marketing/<brand-slug>/`.

### 4. Generate content

```
/contentforge:create-content
```

The skill prompts you for content type, brand, topic, target word count, and audience. It then runs 11 phases via specialized subagents (research → fact-check → draft → visuals → validate → proofread → SEO → humanize → review → output), enforces a quality gate after each phase, and writes a real `.docx` you can hand to your editor or design team.

### 5. Find your output

ContentForge now writes the finished `.docx` to **two** places (v3.12.3+):

**User-visible copy — this is the one to open:**

```
~/Documents/ContentForge/<brand-slug>/<content-type>/<YYYY-MM>/<slug>.docx
```

This lives in your normal Documents folder, visible in Windows Explorer / macOS Finder / Linux file managers by default. Override the root with the `CONTENTFORGE_PUBLISH_DIR` env var (e.g. point at a Dropbox or team-share path). Run `/contentforge:output-folder` any time to print the absolute path and open the folder in the OS file manager.

**Internal tracking copy — the system-of-record for analytics/audit skills:**

```
~/.claude-marketing/<brand-slug>/tracking/outputs/<YYYY>/<MM-MonthName>/
└── <slug>_v1.0.docx
```

The intermediate phase artefacts (research brief, fact-check report, draft, SEO scorecard, review report, etc.) plus rendered chart PNGs land alongside the tracking copy under `~/.claude-marketing/<brand-slug>/output/<content-type>/<YYYY-MM-DD>/`. The `.docx` includes the body, references, and four appendices — **A** SEO Scorecard, **B** Quality Scorecard, **C** Production Details, **D** Internal Link Map.

> **Bug fix in v3.12.3:** earlier versions only wrote to the hidden `~/.claude-marketing/` dotfolder, which Windows Explorer hides by default. Multiple users reported "the file isn't saving on local drive" — it was saving, just somewhere they couldn't see. The dual-copy fix is the resolution; `/contentforge:output-folder` is the quick-reveal command.

### 6. If the run gets interrupted, resume it

The 11-phase pipeline runs 20–60 minutes end to end. If the session terminates partway through (context-window exhaustion, network blip, Ctrl-C, machine sleep), v3.12.3+ saves each completed phase to disk via `scripts/checkpoint-manager.py`. Resume the run with:

```
/contentforge:resume                 # auto-picks the most recent in-progress run for the active brand
/contentforge:resume <run-id>        # pick a specific run from `checkpoint-manager.py list`
```

The resumer reloads the saved Phase 1..N outputs and continues from Phase N+1 — no re-running phases that already completed. (Earlier versions had no checkpointing — an interruption meant starting over from Phase 1.)

---

## What ContentForge does (the 11-phase pipeline)

```
0.5  Title Curation       → 4-5 SERP-aware title options; user selects
 1   Research              → 5+ verified sources, competitive analysis
 2   Fact Checking         → URL verification, claim cross-reference
 3   Content Drafting      → SME-calibrated first draft using industry pack
 3.5 Visual Asset Annotator → matplotlib charts from verified data + visual markers
 4   Scientific Validation → hallucination check, domain rules, regulatory
 5   Structuring & Proofread → grammar, readability, brand compliance
 6   SEO/GEO Optimization  → keywords, meta tags, schema, internal links (3 categories)
 6.5 Humanizer             → 29-pattern AI-detection catalog + self-critique
 7   Review                → 5-dimension scoring (Content, Citation, Brand, SEO, Readability)
 8   Output Manager        → real .docx with embedded scorecards + link map
```

Each phase has a quality gate. If a gate fails, the orchestrator loops back to the offending phase (max 5 loops per pipeline). All phases run via the **Task** tool against dedicated subagent definitions in `agents/01-researcher.md` through `agents/08-output-manager.md` — there is no single-pass shortcut.

**Realistic timing:** FAQ 30–35 min · article 35–45 min · whitepaper 45–75 min · research paper 60–90 min. The README used to claim "20–30 minutes for everything" — that was too optimistic and is no longer accurate.

---

## Internal linking — the three categories (v3.9.5)

ContentForge is a **marketing system**, not a search-engine pipeline. Informational links alone don't drive any commercial outcome. v3.9.5 introduced three independently-scored link categories:

| Category | What it does | Brand profile field |
|---|---|---|
| **Topical** (informational) | Link to related content on the brand's own site | `seo_preferences.internal_linking.{sitemap_url,page_registry,pillar_pages}` |
| **Commercial** (revenue) | Link a natural anchor in the body to the brand's product/service/program page | `seo_preferences.brand_pages.product_or_service_pages` |
| **Conversion** (funnel handoff) | One audience-matched CTA near the end (request MSL, book demo, talk to sales, subscribe) | `seo_preferences.brand_pages.conversion_pages` |
| **Authority** (optional) | Hyperlink the brand's first name occurrence to the about / leadership page | `seo_preferences.brand_pages.authority_pages` |

The SEO agent emits typed `<!-- INTERNAL-LINK: type=... | anchor=... | url=... -->` markers; the .docx generator renders each as a real Word hyperlink, **color-coded by type** (topical blue, commercial green, conversion purple, authority slate). Where the brand has not provided a URL, the marker stays as a visibly-distinct red `[anchor] [LINK TBD: type]` placeholder — the human reviewer fills it in before publication, instead of the link opportunity being silently skipped.

**Configure once per brand:**

```json
"seo_preferences": {
  "internal_linking": {
    "page_registry": [
      {"url": "https://yoursite.com/resources/your-pillar-guide", "topic": "pillar topic", "type": "pillar"}
    ],
    "pillar_pages": ["https://yoursite.com/resources/your-pillar-guide"]
  },
  "brand_pages": {
    "product_or_service_pages": [
      {"url": "https://yoursite.com/programs/access", "topic": "patient access program", "category": "program",
       "anchor_text_hints": ["access program", "affordability assistance"]}
    ],
    "conversion_pages": [
      {"url": "https://yoursite.com/contact/msl", "purpose": "request MSL", "audience": "HCP",
       "anchor_text_hints": ["request a Medical Science Liaison consult"]}
    ],
    "authority_pages": [
      {"url": "https://yoursite.com/about/medical-affairs", "purpose": "medical affairs leadership", "audience": "HCP"}
    ]
  }
}
```

The reviewer (Phase 7) scores 6a Topical / 6b Commercial / 6c Conversion **independently**. Categories the brand has not configured score N/A and don't penalize. There is no "no site structure provided = full credit" free-pass — the agent must produce useful link markers (real URLs or placeholders) to earn credit.

> See `config/brand-registry-template.json` for the full schema.

---

## Run a real white paper — worked example

```
/contentforge:create-content
```

When prompted, supply:

- **Brand:** `acme-pharma` (must already exist via `/contentforge:brand-setup`)
- **Content Type:** `whitepaper`
- **Topic:** `Pharmacovigilance for HER2-Directed ADCs in Community Oncology`
- **Target Audience:** Community medical oncologists, oncology pharmacists
- **Word Count:** 3500-4200
- **SEO Keywords:** `ADC pharmacovigilance, T-DXd ILD monitoring`

The pipeline runs ~60 min. When it finishes you get:

```
~/.claude-marketing/acme-pharma/output/whitepaper/2026-05-13/whitepaper.docx
```

Open it in Word. You will see the body, the references, then **Appendix A** (SEO scorecard with keyword density, meta tags, schema), **Appendix B** (5-dimension quality scorecard), **Appendix C** (production details — phase timings, em-dash count, AI signal score), and **Appendix D** (internal link map showing every topical / commercial / conversion / authority link the agent placed, with target URLs and anchor text). All inline hyperlinks are clickable in Word.

---

## Commands (visible in the Customize sidebar)

These 9 commands are the user-facing entry points:

| Command | What it does |
|---|---|
| `/contentforge:create-content` | Run the full 11-phase pipeline for a single piece |
| `/contentforge:content-brief` | Generate a research-backed brief with keyword data, competitor analysis, outline |
| `/contentforge:social-adapt` | Repurpose an article into LinkedIn / Twitter / Instagram / Facebook / Threads posts |
| `/contentforge:publish` | Push to Webflow or WordPress with preview, verification, HTML fallback |
| `/contentforge:translate` | Translate into 15+ languages preserving brand voice, citations, SEO |
| `/contentforge:brand-setup` | Configure brand voice, terminology, guardrails, internal linking, **brand_pages** |
| `/contentforge:audit-content` | Audit content library for freshness decay and coverage gaps |
| `/contentforge:output-folder` | Print + open the user-visible output folder (`~/Documents/ContentForge/<brand>/`) — answers "where did my file go?" (v3.12.3+) |
| `/contentforge:resume` | Resume an interrupted pipeline run from the last completed phase instead of starting over (v3.12.3+) |

> Slash command syntax is canonical `/<plugin-name>:<command>` — the older `/cf:` shortcuts no longer work as of v3.9.3.

---

## Skills (run via the Skill tool — superset of commands)

| Skill | Purpose |
|---|---|
| `contentforge` | Full 11-phase production (the default skill the `/contentforge:create-content` command invokes) |
| `batch-process` | Process 10–50+ pieces in parallel (4–5× faster) |
| `content-refresh` | Update old content with current data, preserve SEO |
| `cf-brief` | Research-backed brief with keyword analysis and outline |
| `cf-audit` | Freshness scoring, decay detection, gap analysis |
| `cf-calendar` | Production scheduling with deadline tracking |
| `cf-style-guide` | Import brand voice, generate brand profile JSON |
| `cf-template` | Create custom content type templates beyond the 5 built-in |
| `cf-variants` | Generate 3–10 headline / hook / CTA variations with scoring |
| `cf-analytics` | Quality trends, timing breakdown, brand performance |
| `cf-translate` | Translate preserving brand voice (15+ languages, 3 levels) |
| `cf-video-script` | Timestamped scripts for YouTube / TikTok / Instagram Reels |
| `cf-social-adapt` | Article → social media platform-specific posts |
| `cf-publish` | Push to Webflow / WordPress |
| `cf-integrations` | Dashboard of connected vs. available connectors |
| `cf-connect` | Guided setup for any of 22 supported connectors |
| `cf-add-integration` | Add a custom MCP connector for any API |
| `cf-switch-backend` | Switch tracking backend (local / Airtable / Google) with optional data migration |
| `cf-help` | User guide, pipeline overview, examples, troubleshooting |

---

## Architecture

### 13 agents

| Phase | Agent | Purpose | Avg Time |
|---|---|---|---|
| 1 | Researcher | SERP analysis, source mining, outline | 6–8 min |
| 2 | Fact Checker | URL verification, claim cross-reference | 4–6 min |
| 3 | Content Drafter | First draft with brand voice + SME calibration | 4–6 min |
| 3.5 | Visual Asset Annotator | Chart generation, visual markers, asset manifest | 3–9 min |
| 4 | Scientific Validator | Hallucination detection, domain validation | 3–9 min |
| 5 | Structurer & Proofreader | Grammar, readability, brand compliance | 2–7 min |
| 6 | SEO/GEO Optimizer | Keywords, meta tags, AI Overview, **3-category internal linking** | 3–8 min |
| 6.5 | Humanizer | 29-pattern AI-detection catalog + self-critique meta-pass | 5–8 min |
| 7 | Reviewer | 5-dimension scoring with comparative ranking | 1–4 min |
| 8 | Output Manager | `.docx` with hyperlinks, charts, scorecards, link map | <1 min |
| 9 | Batch Orchestrator | Parallel pipeline coordination | post-pipeline |
| 10 | Social Adapter | Platform-specific repurposing | post-pipeline |
| 11 | Translator | Brand voice mapping, cultural adaptation | post-pipeline |

### Quality scoring (Phase 7 reviewer, 5 dimensions)

| Dimension | Weight | What it measures |
|---|---|---|
| Content Quality | 30% | Depth, originality, audience value, structure, completeness |
| Citation Integrity | 25% | Factual accuracy, source quality, formatting, recency |
| Brand Compliance | 20% | Voice/tone, terminology, guardrails, POV consistency, industry compliance |
| SEO Performance | 15% | Keywords, meta tags, on-page SEO, GEO, schema, **internal linking (6a/6b/6c split)** |
| Readability | 10% | Reading level, sentence variety, paragraph structure, scannability, humanization |

Decision thresholds: **9.0+ A** publish + repurpose · **7.0–8.9 B** publish · **5.0–6.9 C** loop back · **<5.0 D** human escalation.

### Three-layer fact verification

Single-pass fact-checking misses 15–20% of hallucinations. ContentForge uses three independent layers — Phase 2 (Fact Checker) verifies sources before drafting, Phase 4 (Scientific Validator) re-verifies the draft against verified sources, Phase 7 (Reviewer) audits factual accuracy as part of holistic scoring. Production runs typically achieve 94–100% factual accuracy with 0 hallucinations.

### Industry knowledge packs

10 domain-specific configs at `config/industries/` (pharma, BFSI, healthcare, legal, real estate, technology, B2B SaaS, e-commerce, consumer goods, education) calibrate the Content Drafter as a subject-matter expert and give the Scientific Validator domain-specific terminology, evidence standards, regulatory rules, and common pitfalls to check against.

### Phase 6.5 Humanizer (the differentiator)

29-pattern AI-detection catalog (5 buckets: content, language/grammar, style, communication, filler/hedging) adapted from Wikipedia: Signs of AI Writing + blader/humanizer. Includes a self-critique meta-pass ("what makes this still obviously AI?") and optional voice calibration from a brand `writing_sample` field. Typical results: 12–67 patterns removed per piece, burstiness 0.50 → 0.72, AI signal score ≤3/10, em dashes ≤2 per 500 words.

### Model curator (v3.12.2+) — no hardcoded model ids

Frontier models change every ~6 weeks. ContentForge ships a shared registry + resolver so model ids are never hardcoded across scripts: edit `scripts/model_registry.json` in one place and every script picks up the change next call. Aliases like `latest-balanced-anthropic`, `latest-vision-google`, `latest-image-google` resolve at call time; deprecated ids auto-fall-forward to their replacement; `scripts/refresh_models.py` polls live provider catalogs and reports drift. See [`docs/MODEL-CURATOR.md`](docs/MODEL-CURATOR.md).

```bash
python scripts/resolve_model.py --alias latest-balanced-anthropic
python scripts/resolve_model.py --check gemini-2.0-flash      # warns: deprecated, use gemini-3.5-flash
```

---

## Connectors (MCP integrations)

ContentForge ships with **9 HTTP connectors** that work in both Cowork and Claude Code: Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar, fal.ai (AI image generation), Replicate (AI image generation). All are **opt-in** — the plugin works fully without any connectors and produces output locally.

For Cowork users who need Google Sheets / Drive / and ~1000 other SaaS services that have no first-party HTTP MCP, see `.mcp.json.connectors-reference` for Pipedream / Composio / Zapier / Make.com aggregator paths.

For Claude Code users who want stdio MCPs (Google Sheets via service account, Google Drive, Stability AI, etc.), copy the example config:

```bash
cp .mcp.json.example .mcp.json
```

See [CONNECTORS.md](CONNECTORS.md) for the full reference.

---

## Troubleshooting

### Pipeline stops early in `--print` / one-shot mode

`claude --print` exits at the first interactive prompt (e.g., title selection). When scripting non-interactive runs, **pre-supply every input** in the prompt — including the title selection from Phase 0.5. See the validation prompt in `examples/` for the pattern.

### Pipeline didn't actually invoke subagents (everything happened "in one inference")

Verify v3.9.4 or later is installed (`claude plugin list`). Pre-v3.9.4 versions had a SKILL.md bug that allowed single-pass generation. The fix mandates Task-tool dispatch per phase.

### `.docx` has no internal links

Check your brand profile has `seo_preferences.internal_linking.page_registry` (or `sitemap_url`) populated. For commercial and conversion links, populate `seo_preferences.brand_pages.product_or_service_pages` and `conversion_pages`. If those are empty, the agent has nothing to link to. Re-run `/contentforge:brand-setup` to fill them in.

### Pipeline fails at Phase 1 (Research)

Topic too niche, no search volume, or `WebSearch` not enabled. Broaden the topic or use a related keyword with more search volume.

### Content score below 7.0 and keeps looping

Review Phase 7 Quality Scorecard for the weakest dimension. Most common cause: weak brand profile. Run `/contentforge:brand-setup` and verify voice, guardrails, and audience are filled in. For regulated industries (pharma, BFSI, healthcare, legal) the threshold is 8.0 and guardrails are required.

### Phase 6.5 Humanizer degrades SEO

Expected — the humanizer auto-loops back to Phase 6 once if SEO degrades, and the second pass usually balances both.

### Connector not working

Run `/contentforge:integrations` to check status. Run `/contentforge:connect <name>` for guided setup.

### Manifest install error: "repository field is an object" or "$schema unknown"

Fixed in v3.9.2. Update: `claude plugin marketplace update neels-plugins && claude plugin update contentforge@neels-plugins`.

### `/cf:` shortcut commands no longer work

As of v3.9.3 the canonical namespace is `/contentforge:`. The `/cf:` prefix was removed in the namespace sweep — use `/contentforge:create-content`, `/contentforge:brand-setup`, etc.

---

## Updating

> **If you see "/plugin isn't available in this environment"** — you're in **claude.ai web chat**, which does NOT support `/plugin` slash commands. The plugin IS installed (your `cf-*` skills work); it just can't be managed via slash command in web chat. Fix:
>
> 1. **Use the UI** — click the **Plugins** button at the bottom of the chat → **Manage plugins** → find ContentForge → look for Update / Refresh / Remove. If there's no Update button, **Remove** then **Add plugin** → re-install ContentForge from `indranilbanerjee/neels-plugins`. That re-pull fetches the latest version.
> 2. **Or switch to Claude Code CLI / Desktop / Cowork** for plugin management — `npm install -g @anthropic-ai/claude-code` or download from [claude.com/code](https://claude.com/code). The plugins themselves run identically across every platform; you're choosing where to type the management commands.
>
> Once you're on Claude Code CLI / Desktop / Cowork, the rest of this section applies.

**Third-party marketplaces (including this one) have auto-update DISABLED by default in Claude Code.** Anthropic's official marketplace updates itself; ours does not. So when v3.9.5 is on the marketplace and you're still running v3.9.4, nothing tells you — there is no update banner, no badge, no notification.

You have two options:

### Option 1 (recommended) — turn auto-update on for our marketplace once

Run `/plugin`, go to the **Marketplaces** tab, find `neels-plugins`, and toggle **Enable auto-update**. From then on, Claude Code refreshes the catalog at startup and pulls the latest ContentForge automatically. After an auto-update fires you'll be prompted to run `/reload-plugins` to pick up the changes mid-session.

### Option 2 — manual update each time

```
/plugin marketplace update neels-plugins
/plugin uninstall contentforge@neels-plugins
/plugin install contentforge@neels-plugins
/reload-plugins
```

`/reload-plugins` applies the change without a full Claude Code restart and preserves your current conversation context.

### If a version stays the same but content changed

This happens during fast-iteration debugging. Clear the cached copy and reinstall:

```
rm -rf ~/.claude/plugins/cache/neels-plugins
/plugin install contentforge@neels-plugins
/reload-plugins
```

### Installs in Cowork

Cowork is the Anthropic Desktop computer-use product (macOS/Windows). It supports third-party plugins from custom marketplaces — same `/plugin marketplace add` install pattern. Cowork has local filesystem access, so the full ContentForge pipeline including the `generate-docx.py` step runs and produces real `.docx` files, just as in Claude Code CLI/Desktop. The only Cowork limitation that affects ContentForge is **HTTP MCPs only** (no stdio/npx) — which is why our `.mcp.json.connectors-reference` documents Pipedream / Composio / Zapier / Make.com aggregator paths for any service that doesn't ship a first-party HTTP MCP.

---

## FAQ

**Q: How does ContentForge compare to ChatGPT or Claude directly?**
Single-prompt tools produce content in 30 seconds with ~15–20% hallucination rate, generic voice, and visible AI patterns. ContentForge takes 35–60 minutes but applies three-layer fact verification, brand voice calibration, AI-pattern removal, and dimensioned quality scoring. Each piece comes with a transparent scorecard.

**Q: Can I use ContentForge without Google Drive / Sheets?**
Yes. Three tracking backends: Google Sheets + Drive, Airtable, or local filesystem. Local works zero-config. Switch any time with `/contentforge:switch-backend`.

**Q: How much does it cost to run?**
Plugin is MIT-licensed and free. Claude API costs are typically $1–4 per piece depending on length and how many quality-gate loops are needed.

**Q: What content types are supported?**
5 built-in: articles (1500–2000 words), blog posts (800–1500), whitepapers (2500–5000), FAQs (600–1200), research papers (4000–8000). Use `/contentforge:template` to add custom types.

**Q: Can I run multiple pieces in parallel?**
Yes — `/batch-process` handles 10–50+ pieces simultaneously with 4–5× speedup over sequential.

**Q: How do I add internal links to a brand's own pages?**
Populate `seo_preferences.brand_pages.{product_or_service_pages, conversion_pages, authority_pages}` in the brand profile. The SEO agent uses these to insert commercial and conversion links into the content; the .docx renders them as inline hyperlinks color-coded by category. See the [Internal linking](#internal-linking--the-three-categories-v395) section above.

---

## Cross-platform compatibility

| Platform | Status |
|---|---|
| Claude Code CLI | ✅ Full support |
| Claude Code Desktop | ✅ Full support |
| Anthropic Cowork | ✅ Full support (HTTP MCPs only — see CONNECTORS.md) |
| claude.ai web chat | ❌ `/plugin` not available in this environment |
| Codex / Cursor / Gemini CLI | Skills (SKILL.md files) portable; rename `.claude-plugin/` to platform's convention |

---

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=indranilbanerjee/contentforge&type=Date)](https://star-history.com/#indranilbanerjee/contentforge&Date)

---

## About the maintainer

ContentForge is built and maintained by **[Indranil Banerjee](https://indranil.in)** — a digital marketing practitioner shipping content production methodology as code. The 11-phase pipeline and 29-pattern AI-detection humanizer come from real client work producing long-form content at agency scale across regulated industries.

- 🌐 **Website:** [indranil.in](https://indranil.in)
- 💼 **LinkedIn:** [linkedin.com/in/askneelnow](https://www.linkedin.com/in/askneelnow)
- 🐦 **X / Twitter:** [@askneelnow](https://x.com/askneelnow)
- 💻 **GitHub:** [@indranilbanerjee](https://github.com/indranilbanerjee)
- 📦 **Other plugins:** [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) · [SocialForge](https://github.com/indranilbanerjee/socialforge)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/contentforge/discussions)
- 🐛 **Bug reports:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- 🔒 **Security:** [Private Security Advisory](https://github.com/indranilbanerjee/contentforge/security/advisories/new) (see [SECURITY.md](SECURITY.md))

If ContentForge saves your team time, [⭐ star the repo](https://github.com/indranilbanerjee/contentforge/stargazers). Sharing on **LinkedIn** ([linkedin.com/in/askneelnow](https://www.linkedin.com/in/askneelnow)) or **X** ([@askneelnow](https://x.com/askneelnow)) helps too — tag me, I'll re-share.

---

## Contributing

PRs welcome — especially on the 29-pattern AI-detection catalog, industry-specific content templates, and platform-specific schema improvements. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) for the PR checklist, and [TESTING-GUIDE.md](TESTING-GUIDE.md) for the per-phase test checklist. All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues: use [Private Security Advisories](https://github.com/indranilbanerjee/contentforge/security/advisories/new) per [SECURITY.md](SECURITY.md) — do not file public issues for vulnerabilities.

---

## Neelverse Marketing Suite

ContentForge is part of a three-plugin suite by [Indranil Banerjee](https://indranil.in) that share the same brand profiles and marketplace:

| Plugin | What it does |
|---|---|
| [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) | End-to-end engagement methodology — 12-Part Strategy Flow, Four Core Documents, 25 agents, 150 skills |
| **ContentForge** (this plugin) | Publication-ready content via 11-phase pipeline, fact-checker, 29-pattern AI-detection humanizer, `.docx` export with C2PA signing |
| [SocialForge](https://github.com/indranilbanerjee/socialforge) | Social media calendar with AI image (Vertex AI Nano Banana Pro) + video (WaveSpeed Kling v3.0 Pro) generation, C2PA signing |

```
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
/plugin install contentforge@neels-plugins
/plugin install socialforge@neels-plugins
```

---

## Release notes

**v3.12.0 (2026-05-24)** — Install-surface expansion to 5 platforms. Adds **GitHub Copilot CLI** compatibility (no new manifest — Copilot CLI auto-discovers `.claude-plugin/plugin.json` as one of its accepted manifest paths; install: `copilot plugin install indranilbanerjee/contentforge`) and an **experimental `.antigravity/plugin.json`** for Google Antigravity 2.0 CLI (launched 19 May 2026, replacing Gemini CLI). The Antigravity manifest mirrors the Gemini-CLI-extensions format that Antigravity's `agy plugin import gemini` converter accepts; will be updated against the v2-native spec when Google publishes it. `docs/cross-platform-install.md` expanded to cover all 5 platforms. No breaking changes.

**v3.11.0 (2026-05-24)** — Cross-platform compatibility pack. ContentForge now installs cleanly on **OpenAI Codex** and **Cursor** in addition to Claude Code, via two new sibling manifest files (`.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json`) — same `skills/` directory, same `scripts/`, same `.mcp.json`, same `hooks/hooks.json`. No skill duplication. Works because Agent Skills became an open standard (Dec 2025) and all three platforms parse the same SKILL.md `name:` + `description:` frontmatter. Full per-platform install guide added at [`docs/cross-platform-install.md`](docs/cross-platform-install.md): install commands, what works natively per platform, the one Cursor MCP gotcha (Cursor reads MCP from a global `mcp.json` not from plugin-scoped `.mcp.json` — one-time paste required for any of the 16 opt-in connectors), update commands per platform, and where to file platform-specific bugs. No breaking changes for existing Claude Code users.

**v3.10.0 (2026-05-17)** — C2PA content provenance for the .docx output for EU AI Act Article 50 compliance (applicable 2 Aug 2026). New `--c2pa-sign` flag on `scripts/generate-docx.py` with `.docx`-embed-if-supported + verifiable `.c2pa.json` sidecar fallback (c2pa-python 0.32 does not yet support `.docx` MIME inline, so the sidecar is the pragmatic path). Plus May 2026 AEO reality update in Phase 6 SEO/GEO optimizer (Google AI Overviews 55% prevalence + 61% organic CTR drop, citation source skew by engine, LLMs.txt companion standard, Profound/Otterly/Conductor measurement integration references). Production-cert short pointer added at `docs/c2pa-production-cert.md`.

**v3.9.5 (2026-05-13)** — Three-category internal linking. New `brand_pages` schema for product/service/conversion/authority pages. Real inline Word hyperlinks color-coded by category. Appendix D internal link map. Reviewer scoring split into 6a/6b/6c with no free-pass for missing site structure.

**v3.9.4 (2026-05-12)** — Fixed pipeline orchestration to actually invoke subagents via Task tool (single-pass generation was skipping quality gates). Added `scripts/generate-docx.py` for real Microsoft Word output with embedded SEO/Quality/Production appendices.

**v3.9.3 (2026-05-09)** — Swept all `/cf:` shorthand to `/contentforge:` across docs and runtime files for namespace consistency.

**v3.9.2 (2026-05-03)** — Fixed manifest install format: `repository` must be a string URL (not npm-shorthand object), `$schema` field removed (parser rejects unknown top-level keys).

**v3.9.1 (2026-05-03)** — Cowork-compatible aggregator MCP catalog (Pipedream, Composio, Zapier, Make.com) for Google Sheets/Drive and other services without a first-party HTTP MCP.

**v3.9.0 (2026-05-03)** — World-class humanizer rebuilt around 29-pattern AI-detection catalog (5 buckets), self-critique meta-pass, optional voice calibration from a brand `writing_sample`. Removed all 4 global hooks for multi-plugin coexistence.

**Earlier versions:** see [CHANGELOG.md](CHANGELOG.md) for the full history (v3.0 through v3.8 — social adaptation, CMS publishing, translation, video scripts, content briefs, A/B variants, content audits, calendars, style guides, analytics, visual asset annotator, industry knowledge packs, multi-backend I/O, AI image generation, SERP-informed title curation).

---

## License

MIT — see [LICENSE](LICENSE).

## Support

- **Issues:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- **Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/contentforge/discussions)

## Credits

Created by [Indranil Banerjee](https://indranil.in). Built for Claude Code, Claude Cowork, OpenAI Codex, Cursor, GitHub Copilot CLI, and Google Antigravity 2.0. Powered by Anthropic Claude.

---

<sub>Made with care by [Indranil Banerjee](https://indranil.in) · MIT-licensed · [⭐ Star the repo](https://github.com/indranilbanerjee/contentforge) if it helps you</sub>

Humanizer 29-pattern catalog adapted from [Wikipedia: Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (CC BY-SA, WikiProject AI Cleanup) with structure influenced by [blader/humanizer](https://github.com/blader/humanizer) (MIT).
