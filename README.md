# ContentForge

🌐 **Read this in:** [English](README.md) · [हिन्दी](README.hi.md) · [中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Português](README.pt-BR.md) · [العربية](README.ar.md) · [اردو](README.ur.md) · [தமிழ்](README.ta.md) · [বাংলা](README.bn.md) · [Русский](README.ru.md)

> **You need to ship 30 articles this quarter that sound human, cite real sources, link into your funnel, and survive an editor who checks. Your team is three people. You have nine weeks. Your last "AI-written" batch got flagged for hallucinated stats — and the batch before that quietly went stale and nobody noticed.**

Run `/contentforge:create-content` against each topic. The 10-phase pipeline produces a publication-ready `.docx` with a 43-pattern humanizer, a fact-checker subagent, three-category internal linking, and C2PA provenance for EU AI Act compliance — in 30–60 minutes per piece. Then the part no single-shot tool has: **the lifecycle loop.** Every published piece is measured (`cf-aeo-check`), audited for decay (`cf-audit`), and fed back into the next calendar and the next brief — through durable file contracts, so what the system learns about your brand survives the session that learned it.

Open-source enterprise content production system — **22 skills · 13 specialist agents · 10 quality gates · 43-pattern AI-detection humanizer · a run auditor that re-derives every gate before a run may call itself finished · 28 Python scripts, stdlib-only**. Built for marketing teams producing high volumes of long-form content that needs brand voice consistency, citation integrity, and an internal-link strategy that turns content into a funnel. Installs on **Claude Code** (CLI + IDE), **Anthropic Cowork**, **OpenAI Codex**, **Cursor 2.5+**, **GitHub Copilot CLI**, **Google Antigravity 2.0**, **Hermes Agent**, **OpenClaw**, and **Grok** (xAI Build CLI) + 35+ Agent Skills platforms — with hero skills uploadable to **claude.ai (web)** as `.skill` release assets. Created by [Indranil Banerjee](https://indranil.in) · [LinkedIn](https://www.linkedin.com/in/askneelnow/) · [X](https://x.com/askneelnow).

[![Version](https://img.shields.io/badge/version-4.1.2-blue.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/indranilbanerjee/contentforge?style=flat&logo=github&color=yellow)](https://github.com/indranilbanerjee/contentforge/stargazers)
[![Forks](https://img.shields.io/github/forks/indranilbanerjee/contentforge?style=flat&logo=github&color=blue)](https://github.com/indranilbanerjee/contentforge/network/members)
[![Issues](https://img.shields.io/github/issues/indranilbanerjee/contentforge?logo=github)](https://github.com/indranilbanerjee/contentforge/issues)
[![Last commit](https://img.shields.io/github/last-commit/indranilbanerjee/contentforge?logo=github)](https://github.com/indranilbanerjee/contentforge/commits/master)
[![Tests](https://img.shields.io/badge/tests-522%2F522%20passing-brightgreen.svg)](tests/)
[![Platforms](https://img.shields.io/badge/platforms-9%20native%20%2B%2035%20Agent%20Skills-success.svg)](#supported-surfaces-v412)
[![Cowork](https://img.shields.io/badge/cowork-compatible-purple.svg)](#cross-platform-compatibility)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Article%2050%20ready-darkred.svg)](docs/c2pa-production-cert.md)
[![Sponsor](https://img.shields.io/badge/sponsor-%E2%9D%A4-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/indranilbanerjee)

[![Built by Indranil "Neel" Banerjee — Neelverse Marketing Suite — Sponsor this project](docs/assets/author-banner.svg)](https://github.com/sponsors/indranilbanerjee)

> 🆕 **Just shipped — v4.1.2 (August 17, 2026): schema-clean hooks manifest.** Cowork's plugin validation rejects unknown top-level fields in `hooks.json`, and ours carried a `_readme` rationale field ([digital-marketing-pro#9](https://github.com/indranilbanerjee/digital-marketing-pro/issues/9) — the same defect shipped in all three suite plugins). The rationale now lives in [hooks/README.md](hooks/README.md), `hooks.json` is exactly `{"hooks": {}}`, and a new guard keeps it that way. Translations re-stamped. Previously —
>
> **v4.1.1 (August 17, 2026): the README goes global, and shows its receipts.** This README now reads in **12 languages** (हिन्दी, 中文, 日本語, 한국어, Español, Português, العربية, اردو, தமிழ், বাংলা, Русский — switcher at the top, every translation version-stamped and guard-checked), carries **the real artifacts from a real validated run** — the actual chart the pipeline rendered, the actual humanizer before/after edits, the actual 9.0/A scorecard and CLEAN audit verdict ([see them](#the-artifacts-themselves--real-output-you-can-inspect)) — and documents **running ContentForge on OpenAI surfaces** (Codex CLI/IDE/App and ChatGPT via Agent Plugins 1.0) with the same depth as the Claude surfaces, including [updating on all nine platforms](#updating). Previously —
>
> **v4.1.0 (August 17, 2026): two new surfaces.** ContentForge now installs natively on **Grok (xAI Build CLI)** — `grok plugin install indranilbanerjee/contentforge` — via a first-class `.grok-plugin/` manifest pair, version-locked to every other manifest by the release-consistency suite. And five **hero skills now ship as claude.ai-uploadable `.skill` release assets** (`cf-brief`, `cf-social-adapt`, `cf-translate`, `cf-video-script`, `cf-aeo-check`), built by a deterministic packager (`scripts/build-skill-assets.py`) that bundles each skill's config/template dependencies and *refuses to package* any skill whose prose references a file that wouldn't exist after upload — so a claude.ai user never downloads a skill with broken references. [Install for your platform →](#supported-surfaces-v412)
>
> **v4.0.0 (August 17, 2026): the lifecycle release.** ContentForge 3.x was a production pipeline; 4.0 makes it a content **system**. Three architectural changes, each grounded in a defect a real run exposed: **(1) The lifecycle loop closed.** `cf-audit` findings now land in a validated, canonical per-brand store (`scripts/audit-ledger.py`) that `cf-calendar` and `content-refresh` read across sessions; AI-visibility history (`aeo/checks.json`) feeds the freshness model; and each run's verified link inventory merges back into `brand_pages` automatically — conversion pages only ever *staged* for your confirmation, because a CTA is a commercial decision the system must not make for you. Before 4.0 every one of those handoffs was conversational, and worked only while one session held both ends. **(2) The pipeline contract is data.** `config/pipeline-graph.json` declares every phase's reads, writes, gates, and budgeted loop edges — drift-guarded both directions against the agent contracts, the checkpoint manager, and the run auditor. Encoding it immediately found six under-declared inputs the prose table had lost. **(3) The pipeline learns, with floors.** New `scripts/telemetry.py` aggregates loop history, phase timings, and the humanizer's per-pattern hit counts across runs — recurring patterns reach the next drafter brief as advisories behind a recurrence floor, and never touch a gate, a threshold, or a verdict. 22 skills · 27 scripts · 498 tests. [Release notes →](#release-notes) · [Full changelog →](CHANGELOG.md)

```bash
# Install in Claude Code (CLI or VS Code/JetBrains extension):
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins

# Install in Cowork: use the Plugins panel in the UI -- /plugin slash
# commands DON'T work in Cowork (or Claude.ai / Claude Desktop).
# Open Plugins panel -> Add marketplace -> paste indranilbanerjee/neels-plugins
# -> Install ContentForge from the listed plugins.

# Install on Hermes Agent (Nous Research):
hermes plugins install indranilbanerjee/contentforge

# Install on OpenClaw:
openclaw plugins install git:github.com/indranilbanerjee/contentforge

# Install on Grok (xAI Build CLI):
grok plugin install indranilbanerjee/contentforge
```

> If ContentForge saves your team time, [give it a star ⭐](https://github.com/indranilbanerjee/contentforge/stargazers) — it's the single thing that helps other marketing teams find it.

---

## Why ContentForge

Most AI writing tools produce one draft, in one tone, with no quality gates, and forget the piece the moment it ships. The output reads like AI, factual claims are unverified, internal links don't exist, brand voice drifts, the file format is markdown when the editor wants Word — and six months later nobody knows which pieces went stale. ContentForge fixes this end to end:

| Capability | Why it matters |
|---|---|
| **10-phase pipeline with a quality gate after every phase** | Bad output is caught and re-run before it propagates downstream |
| **43-pattern AI-detection humanizer** + self-critique meta-pass | Output reads human, not AI — measured advisory tell-scan + burstiness metrics (`text-metrics.py --ai-tell-scan`) |
| **Fact-checker subagent** verifies URLs and cross-references claims | Citations work and aren't hallucinated — every statistic traces to a verified ledger entry |
| **Three-category internal linking** (topical / commercial / authority) | Content becomes a funnel, not a stranded page |
| **Real `.docx` output** with embedded SEO + Quality + Production + Internal-Link appendices | Editor / design team gets a working Word file, not markdown |
| **A run auditor that re-derives every gate from the artifacts** | "The pipeline says it finished" and "the artifacts prove it finished" can never drift apart silently — `finalize --status completed` refuses without a fresh CLEAN verdict |
| **The lifecycle loop (v4.0)** — audit → refresh → measure → plan, joined by file contracts | Published content stops being fire-and-forget: decay is detected, refreshes are prioritized from data, and what the pipeline learns about your brand compounds |
| **C2PA content provenance signing** for EU AI Act Article 50 compliance | Long-form AI-assisted content distributed in EU markets needs provenance from 2 Aug 2026 |

---

## Supported surfaces (v4.1.2)

| Platform | Install command | Manifest path | Status |
|---|---|---|---|
| **Claude Code** CLI + IDE extension | `/plugin install contentforge@neels-plugins` | `.claude-plugin/plugin.json` | Full support (canonical for solo devs) |
| **Anthropic Cowork** | Plugins panel in UI → Add marketplace → `indranilbanerjee/neels-plugins` → Install ContentForge | same `.claude-plugin/` files | **Recommended for teams** — `/contentforge:cf-cowork-setup` wires Google Drive for team-shareable output (and, in 4.0, for the lifecycle stores that make the loop compound across sessions) |
| **OpenAI Codex** CLI + IDE + App | `codex plugin marketplace add indranilbanerjee/neels-plugins` then `codex plugin install contentforge@neels-plugins` | `.codex-plugin/plugin.json` (published OpenAI schema) | Full skills + MCP support |
| **Cursor 2.5+** | In any Cursor Agent chat: `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` | `.cursor-plugin/plugin.json` (verified Cursor 2.5+ JSON Schema) | Full skills + agents + commands support |
| **GitHub Copilot CLI** | `copilot plugin marketplace add indranilbanerjee/neels-plugins` then `copilot plugin install contentforge@neels-plugins` | `.github/plugin/plugin.json` (Copilot also recognizes `.claude-plugin/plugin.json` as fallback) | Full skills + MCP support |
| **Google Antigravity 2.0** CLI + IDE | `agy plugin install https://github.com/indranilbanerjee/contentforge` | `gemini-extension.json` (at repo root, per Google's reference pattern) | Full skills + hooks support |
| **Hermes Agent** (Nous Research) — Desktop + CLI on macOS / Windows / Linux | `hermes plugins install indranilbanerjee/contentforge` | `plugin.yaml` + `__init__.py` at repo root (Hermes native spec) | Native plugin — adapter walks `skills/` at register time and exposes all 22 skills via `ctx.register_skill()`. Targets Hermes Desktop v0.15.2+ (public preview June 2 2026). |
| **OpenClaw** (formerly Clawdbot / Moltbot) | `openclaw plugins install git:github.com/indranilbanerjee/contentforge` | `openclaw.plugin.json` at repo root (also auto-detects `.claude-plugin/plugin.json` as Claude-compatible bundle) | Native plugin via `openclaw.plugin.json`; `skills` field points at `./skills`. |
| **Grok** (xAI Build CLI) | `grok plugin install indranilbanerjee/contentforge` — or add the marketplace: `grok plugin marketplace add indranilbanerjee/neels-plugins` then `grok plugin install contentforge` (append `--trust` to skip the install confirmation) | `.grok-plugin/plugin.json` + `.grok-plugin/marketplace.json` ([Grok Build](https://docs.x.ai/build/features/skills-plugins-marketplaces) also reads the `.claude-plugin/` manifests for compatibility; the native pair is the first-class lane) | Full skills support; the pipeline runs via the portable execution lane |
| **claude.ai (web)** | Download a hero skill from [the latest release](https://github.com/indranilbanerjee/contentforge/releases/latest) (e.g. [`cf-brief.skill`](https://github.com/indranilbanerjee/contentforge/releases/latest/download/cf-brief.skill)) → claude.ai → **Settings → Capabilities** (enable *Code execution and file creation*) → **Customize → Skills → Upload skill** | built from `config/skill-assets.json` by `scripts/build-skill-assets.py` | **Hero skills only** — `cf-brief`, `cf-social-adapt`, `cf-translate`, `cf-video-script`, `cf-aeo-check`. The full pipeline needs subagent dispatch, which claude.ai uploads don't have |
| **Agent Plugins 1.0 hosts** (ChatGPT, Kiro, VS Code, and other adopters of OpenAI's vendor-neutral standard) | via the root `plugin.json` (closed AP1.0 schema) | `plugin.json` at repo root | Skills-only package; `${PLUGIN_ROOT}` / `${PLUGIN_DATA}` accepted everywhere; the **portable execution lane** runs the full pipeline on hosts without subagent dispatch |

**Why this works:** Agent Skills became an open standard in December 2025 (41+ agent products by June 2026). All 22 SKILL.md files in ContentForge are platform-portable as written. The sibling manifests are thin platform-specific wrappers around the same `skills/` directory — no skill duplication.

**Works on 35+ additional Agent Skills platforms** without per-platform manifests — Goose (Block), OpenHands, OpenCode (sst), Junie (JetBrains), Gemini CLI, Roo Code, Cline/Windsurf, Kiro, Amp, Letta, Mux, Factory, Workshop, Tabnine, Mistral Vibe, and more. Point any Agent-Skills-compatible client at `https://github.com/indranilbanerjee/contentforge/tree/master/skills` and all 22 ContentForge skills are immediately discoverable.

---

## Quick start

### 1. Install the plugin

**In Claude Code (CLI or VS Code/JetBrains extension):**

```bash
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install contentforge@neels-plugins
```

**In Anthropic Cowork:**

1. Open the **Plugins** panel in the Cowork UI (sidebar / settings)
2. Click **Add marketplace**, paste `indranilbanerjee/neels-plugins`
3. After the marketplace syncs, find **ContentForge** in the listed plugins and click **Install**
4. Then run `/contentforge:cf-cowork-setup` once to wire Google Drive as your team's output destination

> ⚠ `/plugin` slash commands work **only in Claude Code (CLI + IDE extension)**. They do NOT work in Cowork, Claude.ai web, or Claude Desktop — use UI navigation in those environments. The `/contentforge:*` skills (like `/contentforge:create-content`) work in all environments where plugins are loaded; only the `/plugin` management family is Claude-Code-only.

### 2. Turn on auto-update (one-time, recommended)

**Third-party marketplaces — including this one — have auto-update OFF by default in Claude Code.** When a newer version is on the marketplace and you're still running an older one, nothing tells you. There's no banner, no badge, no notification. So the first thing to do after install is enable updates:

Open `/plugin`, go to the **Marketplaces** tab, find `neels-plugins`, and toggle **Enable auto-update**. Done — Claude Code will refresh and pull new ContentForge releases at startup from now on, prompting you to run `/reload-plugins` to pick up changes mid-session (no full restart, conversation context preserved).

If you'd rather update manually each time instead, see the [Updating](#updating) section below.

### 3. Set up your first brand

```
/contentforge:brand-setup
```

The agent walks you through brand voice, terminology, guardrails, citation rules, internal-linking site structure, and (if you want commercial impact) the **brand_pages** block — your product/service URLs, conversion CTAs, and authority pages. When you give it a website, it runs a robots-respecting crawler and harvests a verified page inventory in one confirmation step. It saves a `brand-profile.json` to `~/.claude-marketing/<brand-slug>/`.

### 4. Generate content

```
/contentforge:create-content
```

The skill prompts you for content type, brand, topic, target word count, and audience. It then runs 10 phases via specialized subagents (research → fact-check → draft → visuals → validate → proofread → SEO → humanize → review → output), enforces a quality gate after each phase, audits the finished run against its own artifacts, and writes a real `.docx` you can hand to your editor or design team.

### 5. Find your output

ContentForge writes the finished `.docx` to **two** places:

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

The intermediate phase artefacts (research brief, fact-check report, draft, SEO scorecard, review report, etc.) plus rendered chart PNGs land alongside the tracking copy in the run directory. The `.docx` includes the body, references, and four appendices — **A** SEO Scorecard, **B** Quality Scorecard, **C** Production Details, **D** Internal Link Map.

> **Historical note (fixed in v3.12.3):** earlier versions only wrote to the hidden `~/.claude-marketing/` dotfolder, which Windows Explorer hides by default. Multiple users reported "the file isn't saving on local drive" — it was saving, just somewhere they couldn't see. The dual-copy design is the resolution; `/contentforge:output-folder` is the quick-reveal command.

### 6. If the run gets interrupted, resume it

The 10-phase pipeline runs 20–60 minutes end to end. If the session terminates partway through (context-window exhaustion, network blip, Ctrl-C, machine sleep), every completed phase is saved to disk via `scripts/checkpoint-manager.py`. Resume the run with:

```
/contentforge:resume                 # auto-picks the most recent in-progress run for the active brand
/contentforge:resume <run-id>        # pick a specific run from `checkpoint-manager.py list`
```

The resumer reloads the saved Phase 1..N outputs and continues from Phase N+1 — no re-running phases that already completed. It also reports **orphaned artifacts** (a phase whose artifact exists but was never checkpointed — precisely the window a crash creates), so finished work is verified rather than re-run blind or trusted blind.

### 7. Close the loop (the v4.0 habit)

After you've published a few pieces, three commands turn production into a lifecycle:

```
/contentforge:cf-aeo-check      # did AI engines cite the piece? appends to per-brand history
/contentforge:audit-content     # score the library for decay; findings recorded durably
/contentforge:cf-calendar --from-audit=latest   # next period's plan, fed from the recorded audit
```

Each one writes or reads a durable per-brand file — the loop works across sessions, across weeks, and (with Cowork + Drive) across your whole team. Details in [The content lifecycle loop](#the-content-lifecycle-loop-v40).

---

## What ContentForge does (the 10-phase pipeline)

![The 10-phase ContentForge pipeline: title curation, research, fact-check, draft, visual assets, scientific validation, structure and proofread, SEO/GEO, humanizer, reviewer, and output manager — with budgeted gate-fail loop edges](docs/assets/pipeline-dag.svg)

```
0.5  Title Curation        → 4-5 SERP-aware title options; user selects
 1   Research              → 12-15 verified sources, competitive analysis, site recon + link inventory
 2   Fact Checking         → URL verification, claim cross-reference → the verified claim ledger
 3   Content Drafting      → SME-calibrated first draft, every statistic ledger-traceable
 3.5 Visual Asset Annotator → deterministic charts from verified data + visual anchors
 4   Scientific Validation → hallucination check vs the ledger; corrections filed in the fix ledger
 5   Structuring & Proofread → grammar, readability, brand compliance; fix ledger applied BY SCRIPT
 6   SEO/GEO Optimization  → keyword placements, meta tags, schema, internal links (3 categories, live-verified)
 6.5 Humanizer             → 43-pattern AI-detection catalog + self-critique + pattern-hit telemetry
 7   Review                → 5-dimension scoring (Content, Citation, Brand, SEO, Readability)
 8   Output Manager        → real .docx with embedded scorecards + link map; run audit gates "completed"
```

Each phase has a quality gate **verified by the orchestrator with scripts, never taken from an agent's self-report**. If a gate fails, the orchestrator loops back to the offending phase — max 2 loops per edge, 5 per run, every loop recorded with its reason. All phases run via the **Task** tool against dedicated subagent definitions in `agents/01-researcher.md` through `agents/08-output-manager.md` — there is no single-pass shortcut. On platforms without subagent dispatch, the **portable execution lane** runs the same phases sequentially from the same agent contracts: same artifacts, same gates, same budgets.

The pipeline's shape — every phase's inputs, outputs, gate, and loop target — is declared as data in **`config/pipeline-graph.json`** (v4.0) and drift-guarded against the agent contracts, the checkpoint manager, and the run auditor. A phase asked to verify something its inputs never gave it is now a failing test, not a latent bug.

**And when the last phase ends, the run still has to prove it.** `scripts/run-audit.py` re-derives every claim the finished run makes from the artifacts on disk — completed phases vs artifacts, scaffolding in the delivered body, unanchored assets, corrections lost or undone, an APPROVED decision backed by its own score, a `completed` status hiding a blocked publication. `finalize --status completed` **refuses** without a fresh CLEAN verdict; `--skip-audit` exists as an escape hatch that stamps `audit_skipped: true` into the manifest, because a skipped audit should be a fact on the record, not a silence.

**Realistic timing:** FAQ 30–35 min · article 35–45 min · whitepaper 45–75 min · research paper 60–90 min.

---

## The content lifecycle loop (v4.0)

![The v4.0 content lifecycle loop: plan, produce, publish, measure, audit — joined by durable per-brand file contracts](docs/assets/lifecycle-loop.svg)

A pipeline makes a piece. A lifecycle keeps a library alive. ContentForge has had every stage of this loop for a while — what 4.0 adds is the connective tissue that makes it a **system**: every joint is now a file with a schema, so the loop survives the session that ran it.

| Joint | Store (per brand) | Producer → Consumer |
|---|---|---|
| Audit findings | `audits/audit-<date>.json` | `/contentforge:audit-content` records via `scripts/audit-ledger.py` (schema-validated — a malformed record is refused with every problem listed) → `cf-calendar --from-audit=latest` and `content-refresh` read the ranked candidates and recommended scopes by file |
| AI-visibility history | `aeo/checks.json` | `/contentforge:cf-aeo-check` appends every check with deltas → `cf-audit`'s freshness model deducts for lost AI citations (a piece that lost its citations is decaying regardless of its age) |
| Verified brand links | `brand-profile.json` → `brand_pages` | Phase 1's reconnaissance writes `phase-1-link-inventory.json` each run → after Gate 1, the orchestrator merges it via `harvest-brand-pages.py --merge-inventory`. Product/authority pages upsert with freshness stamps; **conversion pages only ever stage for your confirmation** — a CTA is a commercial decision, and the system collects the evidence without making the decision |
| Pipeline learning | `runs/*/phase-6.5-pattern-hits.json` + `runs/*/run.json` | Every run records which humanizer patterns fired and which gate-fail loops ran → `scripts/telemetry.py` aggregates across runs → recurring patterns reach the next Phase 3 brief as advisories, `cf-analytics` shows loop edges and pattern trends |

Three rules keep the loop honest, and they are enforced in code, not intentions:

1. **Absence of measurement is never zero.** A pre-4.0 run without pattern telemetry is `not_instrumented`, not clean; an audit that never saw AEO history says `"n/a — no aeo/checks.json"` in a required field — "not consulted" and "consulted, no signal" can never be the same answer.
2. **Learning has floors.** Telemetry advisories require a recurrence floor (default: a pattern seen in ≥3 instrumented runs) before a word of them reaches a brief. Below the floor the answer is `insufficient_history` and nothing is advised — a brief fed from fewer runs than the floor is fed from anecdote.
3. **Loops inform; they never gate.** Advisories shape drafting style and dashboards. They are forbidden — by contract and by test — from modifying a gate, a threshold, or a verdict. The quality machinery stays human-set and re-derived.

On **Cowork**, these stores ride the same Drive sync as brand profiles and checkpoints (`/contentforge:cf-cowork-setup`). Without Drive routing, the Cowork sandbox forgets them at session end — the loop still works within a session, but compounding across sessions is most of its point, so teams should treat Drive routing as required.

---

## Internal linking — the three categories

ContentForge is a **marketing system**, not a search-engine pipeline. Informational links alone don't drive any commercial outcome. Links are scored in three independent categories:

| Category | What it does | Brand profile field |
|---|---|---|
| **Topical** (informational) | Link to related content on the brand's own site | `seo_preferences.internal_linking.{sitemap_url,page_registry,pillar_pages}` |
| **Commercial** (revenue) | Link a natural anchor in the body to the brand's product/service/program page | `seo_preferences.brand_pages.product_or_service_pages` |
| **Conversion** (funnel handoff) | One audience-matched CTA near the end (request MSL, book demo, talk to sales, subscribe) | `seo_preferences.brand_pages.conversion_pages` |
| **Authority** (optional) | Hyperlink the brand's first name occurrence to the about / leadership page | `seo_preferences.brand_pages.authority_pages` |

The SEO agent emits typed `<!-- INTERNAL-LINK: type=... | anchor=... | url=... -->` markers; the .docx generator renders each as a real Word hyperlink, **color-coded by type** (topical blue, commercial green, conversion purple, authority slate). Where the brand has not provided a URL, the marker stays as a visibly-distinct red `[anchor] [LINK TBD: type]` placeholder — the human reviewer fills it in before publication, instead of the link opportunity being silently skipped.

**Auto-harvest:** `/contentforge:brand-setup` runs `scripts/harvest-brand-pages.py` against the brand's website — a stdlib, robots-respecting crawler that returns an HTTP-verified page inventory (service/conversion/authority pages) plus verbatim `brand_facts` (one source URL per fact; where pages disagree, both versions are kept with an `inconsistency_note` for you to resolve, never silently merged). One confirmation step and it's saved straight into the `brand_pages` block. If you decline, the crawl fails, or the brand genuinely has no site, `harvest_status` records exactly which — honestly, never as a silent skip.

**And from v4.0, the inventory stays alive:** every pipeline run re-verifies deep brand URLs during Phase 1 reconnaissance, and the orchestrator merges the verified rows back into `brand_pages` after Gate 1 — freshness stamps updated, new pages added with provenance, your manual curation never overwritten, and conversion candidates staged (never activated) for your review under `brand_pages.recon_candidates`.

**Deep-link rule + thin-`brand_pages` guard:** the researcher (Phase 1) builds a live Internal-Link Inventory of deep brand URLs the piece could naturally reference, HTTP-verified on the day of the run. Phase 6 requires **≥2 deep links** (not just the homepage) whenever the brand's site has them — if `brand_pages` is empty or homepage-only, Phase 6 falls back to that Phase 1 inventory, then a just-in-time sitemap fetch, instead of silently skipping commercial linking.

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

The reviewer (Phase 7) scores 6a Topical / 6b Commercial / 6c Conversion **independently**. Categories the brand has not configured score N/A and don't penalize — but a brand **with** a website whose `brand_pages` was never harvested is a scored deficiency, not an N/A free-pass; homepage-only linking caps the 6b sub-score with a mandatory finding; and any dead internal-link URL is a hard publish-blocking FAIL. The agent must produce useful link markers (real URLs or placeholders) to earn credit.

> See `config/brand-registry-template.json` for the full schema.

---

## Examples

### Run a real white paper — worked example

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

The pipeline runs ~60 min. When it finishes you get a `.docx` in `~/Documents/ContentForge/acme-pharma/whitepaper/<YYYY-MM>/`. Open it in Word: the body, the references, then **Appendix A** (SEO scorecard with keyword placements, meta tags, schema), **Appendix B** (5-dimension quality scorecard), **Appendix C** (production details — phase timings, source reliability, accuracy figures with their phase attributions), and **Appendix D** (internal link map showing every topical / commercial / conversion / authority link the agent placed, with target URLs and anchor text). All inline hyperlinks are clickable in Word.

### What a real gated run looks like — from a live validation run

This is an actual run (August 2026, a digital-preservation test brand, 1,200-word blog, keyword "link rot") — reported exactly as it happened, because the failure-catching is the product:

- **Phase 2 caught Phase 1 misreading a statistic.** The research summarized a source as "the Wayback Machine recovers ~16% of dead URLs"; the fact-checker read the primary source, found 16% was a share of the *entire dataset* (not of dead URLs), locked corrected wording into the verified ledger, and **banned the original sentence from the draft**. The correction survived — verbatim — through six more phases into the delivered Word file, with the disambiguation printed for the reader.
- **Phase 4 diffed 42 claims against the ledger: zero hallucinations**, one minor citation-placement correction — filed in the fix ledger, applied *by script* at Phase 5, and verified still intact at Phases 6.5, 7, and 8.
- **Phase 7 approved at 9.0/10** — and honestly sub-scored internal linking down because the test brand had no `conversion_pages` configured, naming the config gap instead of hiding it.
- **Phase 8's Appendix C corrected a number the orchestrator supplied.** Asked to print "source reliability 8.1", the output manager recomputed it from the research artifact, got 7.9, and printed 7.9 with its reasoning. The honesty discipline binds in every direction.
- **The run auditor re-derived all of it** — 14 checks passed, 0 failed — and only then did `finalize --status completed` accept the run.

Single-prompt tools produce none of these paper trails. The point isn't that the pipeline never errs — it's that its errors get caught by its own machinery, on the record, before your editor ever sees the file.

### The artifacts themselves — real output you can inspect

Everything below is from that same run — not a mock-up, not a demo. The numbers are read from the run's own JSON artifacts (`phase-7-review.json`, `run-audit.json`, `phase-6.5-report.md`, `pipeline-run.json`):

![Scorecard of the real run: overall 9.0 grade A approved; dimension scores 8.8 / 8.9 / 9.6 / 8.6 / 8.8; run audit CLEAN with 14 checks passed and 0 failed; 42 claims verified with zero hallucinations; 20 AI-pattern instances removed; the 10-phase timeline with real durations](docs/assets/real-run-scorecard.svg)

**A chart the pipeline actually rendered** (Phase 3.5 annotates the visual opportunity from verified Phase 2 data; a stdlib matplotlib-free renderer produces the PNG; the data citations ride in the caption):

![Horizontal bar chart of four link-rot benchmarks: 70 percent of web-citing STM articles suffer reference rot (Klein et al., 2014); 66.5 percent of outbound links have rotted since January 2013 (Ahrefs, 2024); 38 percent of webpages that existed in 2013 are no longer available (Pew, 2024); 25 percent of webpages collected 2013-2023 were inaccessible by October 2023 (Pew, 2024)](docs/assets/real-run/link-rot-benchmarks-chart.png)

**The opening the reader actually gets** (from the delivered file — note there's no "In today's digital landscape" anywhere in sight):

> 38% of webpages that existed in 2013 are not available today (Chapekis et al., 2024). Not redesigned. Not moved. Gone. The same Pew study found that 21% of government webpages contain at least one broken link.
>
> The uncomfortable part is the cause, not the scale. When institutional pages disappear, the trigger is usually organizational rather than slow technical decay: a CMS (content management system) migration that dropped a URL structure, or a decision to take pages down. That has a practical upside: events can be planned for, and decay can't.

**What the humanizer actually did to earn that opening** — three of the 20 logged edits, verbatim from the Phase 6.5 report (every edit records before → after, and whether SEO placements survived):

| Pattern | Before | After |
|---|---|---|
| #09 negative parallelism | "link rot isn't a distant hazard, it's already on the premises" | "For public institutions, link rot is already on the premises." — the contrast now rides on "already" |
| #28 signposting | a 38-word roadmap sentence ("What follows is the evidence: …") | **DELETED** (logged in the Deletion Ledger — announcements that the next part matters never survive) |
| #14 em-dash overuse | 14 em dashes (~5.4 per 500 words) | 5 (~1.9 per 500) — nine converted to periods, commas, colons, parentheses; the two kept include a dash-gloss pair that matches the brand's own writing sample, which the voice calibration step protected |

**And the honesty layer, in one JSON excerpt** — the run auditor's verdict that gated `finalize --status completed`:

```json
{
  "run_id": "20260816-131632-link-rot-…",
  "pass": 14, "fail": 0, "na": 1,
  "verdict": "CLEAN"
}
```

One more real detail worth knowing: Phase 8 was killed twice mid-run by session limits. Both times the checkpoint contract resumed it from the artifacts on disk — the delivered `.docx` exists because resume is a contract, not a hope. (The run brand is an internal validation persona for the digital-preservation space, not client work — which is why we can show you its artifacts.)

### Close the loop on a growing library

```
# After a month of publishing:
/contentforge:cf-aeo-check           # record which pieces AI engines cite (history + deltas)
/contentforge:audit-content          # freshness-score the library; the findings are RECORDED
/contentforge:cf-calendar --period=90 --from-audit=latest   # next quarter: refreshes + gaps, from data
/contentforge:content-refresh        # execute a refresh at the audit's recommended scope
```

Every command reads what the previous one recorded — in a new session, on a different day, by a different teammate.

---

## Commands (visible in the Customize sidebar)

These 9 commands are the user-facing entry points:

| Command | What it does |
|---|---|
| `/contentforge:create-content` | Run the full 10-phase pipeline for a single piece |
| `/contentforge:content-brief` | Generate a research-backed brief with keyword data, competitor analysis, outline |
| `/contentforge:social-adapt` | Repurpose an article into LinkedIn / Twitter / Instagram / Facebook / Threads posts |
| `/contentforge:publish` | Push to Webflow or WordPress with preview, verification, HTML fallback |
| `/contentforge:translate` | Translate into 15+ languages preserving brand voice, citations, SEO |
| `/contentforge:brand-setup` | Configure brand voice, terminology, guardrails, internal linking, **brand_pages** (with auto-harvest) |
| `/contentforge:audit-content` | Audit content library for freshness decay and coverage gaps — findings recorded to the durable audit ledger (v4.0) |
| `/contentforge:output-folder` | Print + open the user-visible output folder (`~/Documents/ContentForge/<brand>/`) — answers "where did my file go?" |
| `/contentforge:resume` | Resume an interrupted pipeline run from the last completed phase instead of starting over |

> Slash command syntax is canonical `/<plugin-name>:<command>` — the older `/cf:` shortcuts no longer work as of v3.9.3.

---

## Skills (run via the Skill tool — superset of commands)

| Skill | Purpose |
|---|---|
| `contentforge` | Full 10-phase production (the default skill the `/contentforge:create-content` command invokes) |
| `batch-process` | Process 10–50+ pieces as a sequential, checkpointed queue — survives interruption, resumes mid-piece |
| `content-refresh` | Update old content with current data, preserve SEO — reads recorded audit candidates by file (v4.0) |
| `cf-brief` | Research-backed brief with keyword analysis and outline |
| `cf-audit` | Freshness scoring, decay detection, gap analysis — records findings to `audits/` via `audit-ledger.py`, consumes AEO history (v4.0) |
| `cf-calendar` | Production scheduling with deadline tracking — imports refresh slots from the recorded audit (v4.0) |
| `cf-style-guide` | Import brand voice, generate brand profile JSON |
| `cf-template` | Create custom content type templates beyond the 8 built-in |
| `cf-variants` | Generate 3–10 headline / hook / CTA variations with scoring |
| `cf-analytics` | Quality trends, timing breakdown, brand performance — plus loop-edge and humanizer-pattern telemetry panels (v4.0) |
| `cf-translate` | Translate preserving brand voice (15+ languages, 3 levels) |
| `cf-video-script` | Timestamped scripts for YouTube / TikTok / Instagram Reels |
| `cf-social-adapt` | Article → social media platform-specific posts |
| `cf-publish` | Push to Webflow / WordPress |
| `cf-integrations` | Dashboard of connected vs. available connectors |
| `cf-connect` | Guided setup for any of 22 supported connectors |
| `cf-add-integration` | Add a custom MCP connector for any API |
| `cf-switch-backend` | Switch tracking backend (local / Airtable / Google) with optional data migration |
| `cf-help` | User guide, pipeline overview, examples, troubleshooting |
| `cf-aeo-check` | Post-publication AI-citation check — AI Overview presence, own-citation status, extractability audit, append-only per-brand history with deltas |
| `cf-cowork-setup` | One-time Cowork + Google Drive wiring so team runs — and the v4.0 lifecycle stores — persist across sessions |
| `cf-environment` | Detect the runtime environment and show its capability matrix |

---

## Architecture

### 13 agents

| Phase | Agent | Purpose | Avg Time |
|---|---|---|---|
| 1 | Researcher | SERP analysis, source mining, outline, site recon + link inventory | 6–8 min |
| 2 | Fact Checker | URL verification, claim cross-reference → verified ledger | 4–6 min |
| 3 | Content Drafter | First draft with brand voice + SME calibration | 4–6 min |
| 3.5 | Visual Asset Annotator | Chart generation, visual anchors, asset manifest | 3–9 min |
| 4 | Scientific Validator | Hallucination detection, domain validation, fix ledger | 3–9 min |
| 5 | Structurer & Proofreader | Grammar, readability, brand compliance, ledger application | 2–7 min |
| 6 | SEO/GEO Optimizer | Keywords, meta tags, AI Overview, **3-category internal linking** | 3–8 min |
| 6.5 | Humanizer | 43-pattern AI-detection catalog + self-critique meta-pass + pattern telemetry | 5–8 min |
| 7 | Reviewer | 5-dimension scoring with comparative ranking | 1–4 min |
| 8 | Output Manager | `.docx` with hyperlinks, charts, scorecards, link map | <1 min |
| 9 | Batch Orchestrator | Sequential, checkpointed queue coordination | post-pipeline |
| 10 | Social Adapter | Platform-specific repurposing | post-pipeline |
| 11 | Translator | Brand voice mapping, cultural adaptation | post-pipeline |

### The pipeline graph (v4.0)

`config/pipeline-graph.json` is the machine-readable form of the pipeline contract: nodes are phases, edges are the file-based handoffs, loop targets carry their budgets. `tests/test_pipeline_contract_graph.py` fails the build if the graph, the agent contracts, the orchestrator's table, `checkpoint-manager.py`, or `run-audit.py` ever disagree — in either direction. Encoding the contract as data immediately surfaced six inputs the prose table had under-declared (including one the agent file itself annotated as "was missing from this list" after a previous drift incident). The portable execution lane and the resumer walk this graph rather than re-deriving the order from prose.

### Quality scoring (Phase 7 reviewer, 5 dimensions)

| Dimension | Weight | What it measures |
|---|---|---|
| Content Quality | 30% | Depth, originality, audience value, structure, completeness |
| Citation Integrity | 25% | Factual accuracy, source quality, formatting, recency |
| Brand Compliance | 20% | Voice/tone, terminology, guardrails, POV consistency, industry compliance |
| SEO Performance | 15% | Keywords, meta tags, on-page SEO, GEO, schema, **internal linking (6a/6b/6c split)** |
| Readability | 10% | Reading level, sentence variety, paragraph structure, scannability, humanization |

Decision thresholds: **9.0+ A** publish + repurpose · **7.0–8.9 B** publish · **5.0–6.9 C** loop back · **<5.0 D** human escalation. Thresholds, weights, dimension minimums, and industry overrides live in `config/scoring-thresholds.json` — the single source of truth; where prose and config disagree, the config wins.

### Three-layer fact verification

Single-pass fact-checking misses 15–20% of hallucinations. ContentForge uses three independent layers — Phase 2 (Fact Checker) verifies sources before drafting and builds the verified claim ledger, Phase 4 (Scientific Validator) re-diffs the draft against that ledger claim by claim, Phase 7 (Reviewer) audits factual accuracy as part of holistic scoring. Corrections travel in a machine-verified **fix ledger** (`phase-4-fixes.json`): applied by script at Phase 5, guarded so a style pass cannot undo an accuracy fix, re-verified at every later phase, and enforced at Phase 8 — unresolved blocking corrections don't stop the document being produced; they stop it being called ready (`DRAFT-` prefix, named blockers, blocked tracking status).

### The run auditor

`scripts/run-audit.py` re-checks a finished run the way an outside auditor would: every completed phase has its artifact, no orphaned artifacts in a finalized run, the delivered body carries no production scaffolding and anchors every generated asset, the authorship record matches a fresh measurement, no fix-ledger correction was lost or undone, an APPROVED decision is backed by its own score, and no `completed` status hides a blocked publication. Every check corresponds to a failure that actually happened in a real run while every individual artifact looked healthy. Two disciplines throughout: **re-derive, never trust** (gate fields are compared against fresh script output), and **a missing input is reported-N/A, never silent-pass**.

### Industry knowledge packs

10 domain-specific configs at `config/industries/` (pharma, BFSI, healthcare, legal, real estate, technology, B2B SaaS, e-commerce, consumer goods, education) calibrate the Content Drafter as a subject-matter expert and give the Scientific Validator domain-specific terminology, evidence standards, regulatory rules, and common pitfalls to check against. A brand whose industry has no pack gets an honest "generic writing mode" declaration that travels to the reviewer — never a silent pretense of expertise.

### Phase 6.5 Humanizer (the differentiator)

43-pattern AI-detection catalog (7 buckets: content, language/grammar, style, communication, filler/hedging, structure/framing, detector-signal) adapted from Wikipedia: Signs of AI Writing + blader/humanizer. Includes a self-critique meta-pass ("what makes this still obviously AI?") and optional voice calibration from a brand `writing_sample` field.

**Grounding-first, not trick-first.** The old move — inserting short punchy sentences to raise the burstiness number — is gone: it manufactured the exact aphoristic-maxim tell modern detectors flag. In its place, a **Human-Expert Grounding Pass** grounds every standing maxim, impersonal assertion, and flat-confidence claim in a specific from the Phase 2 verified ledger — or removes it; nothing is invented for style. Sentence variety is **content-derived**: uniform runs get broken by material the content already earns, never by content-free filler. Burstiness is reported as advisory context, not a pass/fail gate. Significance markers ("here's the thing", "let that sink in") are **deleted, never reworded**. When an author supplies their own draft (`--source-draft`), their sentences are carried verbatim, exempt from the catalog, and `scripts/authorship.py` **blocks** if any were paraphrased or dropped — the one hard check in the phase, because "the author wrote this and it is gone" is a fact, not a probability.

**Advisory `--ai-tell-scan`.** `scripts/text-metrics.py --ai-tell-scan` runs a deterministic, zero-dependency proxy scan (aphorism density, banned lexemes, connective/participial-opener rate, uniform sentence runs) and reports a **LOW / MODERATE / HIGH** advisory rating — surfaced in the Phase 6.5 report, the reviewer's Readability sub-score, and the Completion Card. It is never a publish gate, and ContentForge never claims to "beat" any specific detector — see the [FAQ](#faq) and `references/ai-detection-signals.md` for the full reasoning.

**And from v4.0 the phase reports what it fixed, durably:** `phase-6.5-pattern-hits.json` records per-pattern fire counts for `scripts/telemetry.py`, so a pattern your brand's drafts keep producing eventually reaches the drafter's brief as an advisory — behind the recurrence floor, never as a gate. The pipeline stops re-making mistakes its own quality machinery keeps catching.

### Model curator — no hardcoded model ids

Frontier models change every ~6 weeks. ContentForge ships a shared registry + resolver so model ids are never hardcoded across scripts: edit `scripts/model_registry.json` in one place and every script picks up the change next call. Aliases resolve at call time; deprecated ids auto-fall-forward to their replacement; `scripts/refresh_models.py` polls live provider catalogs and reports drift. See [`docs/MODEL-CURATOR.md`](docs/MODEL-CURATOR.md).

```bash
python scripts/resolve_model.py --alias latest-balanced-anthropic
python scripts/resolve_model.py --check <some-old-model-id>      # warns when deprecated + names the replacement
```

### Where your data lives

```
~/.claude-marketing/<brand-slug>/
├── brand-profile.json        # voice, terminology, guardrails, brand_pages (+ recon_candidates)
├── runs/<run-id>/            # per-run artifacts, checkpoints, fix ledger, run-audit.json, telemetry
├── audits/                   # recorded cf-audit findings (v4.0) — what the calendar reads
├── aeo/checks.json           # append-only AI-visibility history (per-check deltas)
├── tracking/outputs/         # the internal system-of-record .docx copies
└── output/                   # intermediate artifacts + rendered charts
```

Plus the user-visible deliverables in `~/Documents/ContentForge/<brand>/`. Everything under the brand directory rides Drive sync on Cowork once `/contentforge:cf-cowork-setup` has run.

---

## Connectors (MCP integrations)

ContentForge ships with **9 HTTP connectors** that work in both Cowork and Claude Code: Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar, fal.ai (AI image generation), Replicate (AI image generation). All are **opt-in** — the plugin works fully without any connectors and produces output locally.

For Cowork users who need Google Sheets / Drive / and ~1000 other SaaS services that have no first-party HTTP MCP, see `.mcp.json.connectors-reference` for Pipedream / Composio / Zapier / Make.com aggregator paths.

For Claude Code users who want stdio MCPs (Google Sheets via service account, Google Drive, etc.), copy the example config:

```bash
cp .mcp.json.example .mcp.json
```

See [CONNECTORS.md](CONNECTORS.md) for the full reference.

---

## Troubleshooting

### Pipeline stops early in `--print` / one-shot mode

`claude --print` exits at the first interactive prompt (e.g., title selection). When scripting non-interactive runs, **pre-supply every input** in the prompt — including the title selection from Phase 0.5.

### Pipeline didn't actually invoke subagents (everything happened "in one inference")

Verify v3.9.4 or later is installed (`claude plugin list`). Pre-v3.9.4 versions had a SKILL.md bug that allowed single-pass generation. The fix mandates Task-tool dispatch per phase. On platforms with no Task dispatch at all, the portable execution lane is the supported mode — sequential, same gates.

### `finalize --status completed` was refused

Working as designed: the run auditor found something the artifacts don't support — the refusal lists the failing checks and the recovery options. Fix the findings and re-run `scripts/run-audit.py`, or finalize honestly as `blocked` if the run is legitimately unpublishable as it stands. `--skip-audit` exists but stamps `audit_skipped: true` into the record.

### `cf-calendar --from-audit=latest` says no recorded audits exist

The calendar reads recorded audits (`audits/`), not conversations. Run `/contentforge:audit-content` first — since v4.0 it records its findings via `audit-ledger.py` as the final, required step. An audit rendered but not recorded did not happen, as far as the lifecycle is concerned.

### `.docx` has no internal links

Check your brand profile has `seo_preferences.internal_linking.page_registry` (or `sitemap_url`) populated. For commercial and conversion links, populate `seo_preferences.brand_pages.product_or_service_pages` and `conversion_pages`. If those are empty, the agent has nothing to link to. Re-run `/contentforge:brand-setup` to fill them in — or, from v4.0, just run the pipeline: verified pages found during research merge back into the profile automatically (conversion pages staged for your confirmation under `brand_pages.recon_candidates`).

### Pipeline fails at Phase 1 (Research)

Topic too niche, no search volume, or `WebSearch` not enabled. Broaden the topic or use a related keyword with more search volume.

### Content score below 7.0 and keeps looping

Review Phase 7 Quality Scorecard for the weakest dimension. Most common cause: weak brand profile. Run `/contentforge:brand-setup` and verify voice, guardrails, and audience are filled in. For regulated industries (pharma, BFSI, healthcare, legal) the threshold is 8.0 and guardrails are required. Loops are budgeted (2 per edge, 5 per run) — at the limit the run stops for human review instead of burning tokens. If the same edge keeps firing across runs, check `cf-analytics`'s loop panel: a recurring edge is a contract/template problem, not a run problem.

### Phase 6.5 Humanizer degrades SEO

Expected — the humanizer auto-loops back to Phase 6 once if SEO degrades, and the second pass usually balances both.

### Connector not working

Run `/contentforge:cf-integrations` to check status. Run `/contentforge:cf-connect <name>` for guided setup.

### Manifest install error: "repository field is an object" or "$schema unknown"

Fixed in v3.9.2. Update: `claude plugin marketplace update neels-plugins && claude plugin update contentforge@neels-plugins`.

### `/cf:` shortcut commands no longer work

As of v3.9.3 the canonical namespace is `/contentforge:`. The `/cf:` prefix was removed in the namespace sweep — use `/contentforge:create-content`, `/contentforge:brand-setup`, etc.

---

## Updating

> **If you see "/plugin isn't available in this environment"** — you're in Cowork, Claude.ai web, or the Claude Desktop app. The `/plugin` slash command for plugin management is **only** supported in **Claude Code** (CLI + IDE extension at [claude.com/code](https://claude.com/code), `npm install -g @anthropic-ai/claude-code`). Everywhere else — Cowork, `claude.ai`, Claude Desktop, mobile — plugins are managed through the UI panel, not slash commands.
>
> The plugin IS installed (your `/contentforge:*` skills still work in chat); only the management command is unavailable. Fix:
>
> 1. **In Cowork** — open the **Plugins** panel (sidebar / Settings → Plugins). Find ContentForge → look for Update / Refresh. If there's no Update option, **Remove** the plugin, then re-install it from the `neels-plugins` marketplace — the re-pull fetches the latest version. If the marketplace itself is stale, also Remove + re-add the marketplace.
> 2. **In Claude.ai web or Claude Desktop** — same UI flow as Cowork: open the chat's Plugins UI button at the bottom → **Manage plugins** → Remove + Add to re-pull.
> 3. **For slash-command management** — switch to **Claude Code (CLI or IDE extension)**. The plugin runs identically across every Anthropic surface; you're choosing where to type management commands.
>
> Once you're in Claude Code, the rest of this section applies.

**Third-party marketplaces (including this one) have auto-update DISABLED by default in Claude Code.** Anthropic's official marketplace updates itself; ours does not. So when a newer version is on the marketplace and you're still running an older one, nothing tells you — there is no update banner, no badge, no notification.

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

### Updating on every other surface

The sections above cover Claude Code because that's where update *management* has the most footguns (the auto-update default). Everywhere else, updating is one command or one UI action:

| Surface | How to update |
|---|---|
| **Anthropic Cowork** | Plugins panel → ContentForge → **Update** (or Remove + re-install from `neels-plugins` — the re-pull fetches latest). If the marketplace itself is stale, Remove + re-add the marketplace too. |
| **claude.ai web / Claude Desktop** (plugin) | Plugins UI button at the bottom of the chat → Manage plugins → Remove + Add to re-pull. |
| **claude.ai web** (hero `.skill` uploads) | Re-download the skill from the [latest release](https://github.com/indranilbanerjee/contentforge/releases/latest) and re-upload — uploaded skills never self-update. |
| **OpenAI Codex** | `codex plugin update contentforge` |
| **Cursor 2.5+** | Re-run `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` — it re-pulls the repository. |
| **GitHub Copilot CLI** | `copilot plugin update contentforge` |
| **Google Antigravity 2.0** | `agy plugin update contentforge` |
| **Hermes Agent** | `hermes plugins update contentforge` (then `hermes plugins list` to confirm the version) |
| **OpenClaw** | `openclaw plugins update contentforge` |
| **Grok (xAI Build CLI)** | `grok plugin update contentforge` |

After any update, the fastest sanity check on every surface is asking the agent: *"What version of ContentForge is installed?"* — `scripts/plugin-metadata.py` answers from the installed manifest, not from memory.

### Upgrading from 3.x to 4.x

No breaking changes to existing runs, brands, or artifacts — 4.x is additive. Pre-4.0 runs simply read as `not_instrumented` in telemetry (unknown, never zero), and the first recorded audit starts the lifecycle stores. See [UPGRADE-GUIDE.md](UPGRADE-GUIDE.md).

### Installs in Cowork

Cowork is the Anthropic Desktop computer-use product (macOS/Windows). It supports third-party plugins from custom marketplaces — same `/plugin marketplace add` install pattern. Cowork has local filesystem access, so the full ContentForge pipeline including the `generate-docx.py` step runs and produces real `.docx` files, just as in Claude Code CLI/Desktop. The only Cowork limitation that affects ContentForge is **HTTP MCPs only** (no stdio/npx) — which is why our `.mcp.json.connectors-reference` documents Pipedream / Composio / Zapier / Make.com aggregator paths for any service that doesn't ship a first-party HTTP MCP.

---

## FAQ

**Q: How does ContentForge compare to ChatGPT or Claude directly?**
Single-prompt tools produce content in 30 seconds with ~15–20% hallucination rate, generic voice, and visible AI patterns. ContentForge takes 35–60 minutes but applies three-layer fact verification, brand voice calibration, AI-pattern removal, dimensioned quality scoring, and a run audit that re-derives every gate before the run may call itself finished. Each piece comes with a transparent scorecard — and from 4.0, each brand gets a lifecycle: published pieces are measured, decay is detected, and the next plan is fed from data.

**Q: Can I use ContentForge without Google Drive / Sheets?**
Yes. Three tracking backends: Google Sheets + Drive, Airtable, or local filesystem. Local works zero-config. Switch any time with `/contentforge:cf-switch-backend`.

**Q: How much does it cost to run?**
Plugin is MIT-licensed and free. Claude API costs are typically $1–4 per piece depending on length and how many quality-gate loops are needed.

**Q: What content types are supported?**
8 built-in: articles (1,500–2,000 words), blog posts (800–1,500), whitepapers (2,500–5,000), FAQs (600–1,200), research papers (4,000–8,000), video scripts (duration-driven, 15s–10min), case studies (case_study, 1,200–2,000, with a client-data provenance rule), and newsletters (500–1,200, subject-line package + one-CTA rule). Use `/contentforge:cf-template` to add custom types.

**Q: Can I batch multiple pieces?**
Yes — `/contentforge:batch-process` queues 10–50+ pieces and runs them one at a time, fully gated and checkpointed per phase. The win is unattended throughput and interruption-proof resume, not concurrency: pieces do NOT run simultaneously (shared per-brand state and API limits make that unsafe).

**Q: How do I add internal links to a brand's own pages?**
Populate `seo_preferences.brand_pages.{product_or_service_pages, conversion_pages, authority_pages}` in the brand profile — `/contentforge:brand-setup` harvests most of it from your website in one confirmation step, and from v4.0 every pipeline run keeps it fresh automatically. See the [Internal linking](#internal-linking--the-three-categories) section above.

**Q: What exactly does "the loop learns" mean — is my quality bar changing by itself?**
No, and that's a design rule with tests on it. Telemetry advisories shape the *drafting brief* (e.g., "this brand's drafts keep producing em-dash overuse — avoid it up front") behind a recurrence floor, and dashboards show trends. Gates, thresholds, weights, and verdicts are set in `config/scoring-thresholds.json` by humans and re-derived by scripts — no loop output ever modifies them.

**Q: If my word count target is 1,200, do image captions count against it?**
No. `body_word_count` counts the prose a reader reads (including H2/H3 headings) and excludes figure furniture — image alt text and the caption line under an embed — along with reference sections and production scaffolding. The counting convention is stated in the Pipeline Contract, because a gate whose verdict depends on an unstated convention isn't a measurement.

**Q: How does the AI-detectability score work?**
Honestly: we don't optimize against any detector. ContentForge writes so there's little to detect — the Phase 6.5 Human-Expert Grounding Pass grounds every claim in a specific from the verified research (a real perplexity-raising move, not a trick), and sentence variety comes from the content, not from inserted filler. On top of that, `scripts/text-metrics.py --ai-tell-scan` runs a deterministic, dependency-free proxy scan for known detector-signal patterns and reports an advisory **LOW / MODERATE / HIGH** rating in the Phase 6.5 report, the reviewer scorecard, and the Completion Card. If an external AI-detector is reachable via a connected MCP, at most one optional validation pass may also run — still advisory. **None of this is ever a publish gate, and we never promise to "beat" any specific detector** — the evidence shows one-shot static tricks do little (and can backfire) while genuine grounding is durable. Full reasoning in `references/ai-detection-signals.md`.

---

## ContentForge on OpenAI surfaces — Codex and ChatGPT

The Claude surfaces get most of this README's screen time because they're where the plugin standard was born — but ContentForge is engineered to run at full depth on OpenAI's surfaces too, and here is exactly how that works, with no hand-waving.

### OpenAI Codex (CLI + IDE + App) — full pipeline, today

```bash
codex plugin marketplace add indranilbanerjee/neels-plugins
codex plugin install contentforge@neels-plugins
```

What happens after install, mechanically:

1. **Codex reads `.codex-plugin/plugin.json`** (OpenAI's published schema — not a converted Claude file) and discovers all 22 skills from the shared `skills/` directory. [AGENTS.md](AGENTS.md) is auto-loaded into context, so Codex knows the plugin's capabilities, storage layout, and current version before you type anything.
2. **You invoke by intent, not slash command**: say *"Create a blog post for my brand using ContentForge"* or *"Run contentforge brand-setup"*. Codex matches your request against the skill descriptions — the same trigger-dense descriptions the routing layer maintains for exactly this purpose.
3. **The pipeline runs through the portable execution lane.** Claude Code dispatches each phase to its specialist agent as a Task-tool subagent; on Codex builds without subagent dispatch, the lane runs the same 10 phases in one conversation — each agent contract read as phase instructions, writing the same numbered artifacts (`phase-1-research.md` → `phase-8-output.json`), passing the same quality gates, respecting the same loop budgets. Same `.docx` at the end, same appendices, same run audit before "completed" is allowed.
4. **Storage lands in the same places** — `~/.claude-marketing/<brand>/` for state (the `${PLUGIN_DATA}` name is accepted everywhere the `CLAUDE_*` names are), `~/Documents/ContentForge/` for deliverables. A brand you set up in Codex is immediately usable from Claude Code, and vice versa.

Two honest caveats: Codex enforces `[a-z0-9-]+` skill names (all 22 of ours pass — test-guarded), and phases that lean on web search inherit whatever browsing capability your Codex build has, exactly as they inherit Claude's.

### ChatGPT and the Agent Plugins 1.0 ecosystem

OpenAI's **Agent Plugins 1.0** standard (announced August 6, 2026; adopted by ChatGPT, Codex, Cursor, GitHub Copilot, VS Code, and Kiro) reads a root [`plugin.json`](plugin.json) on a closed schema. ContentForge ships that manifest — version-synced with every other manifest and guarded by `tests/test_agent_plugins_portability.py`, which verifies the closed-schema rules, the name constraints, and that all 22 skills resolve in the standard's layout.

What that means in practice, stated honestly:

- **The package is listing-ready today.** Any AP1.0 host that can point at this repository gets a skills-complete ContentForge with the portable execution lane — `${PLUGIN_ROOT}` and `${PLUGIN_DATA}` are honored everywhere, so a compliant non-Claude host resolves real storage instead of nothing.
- **The official ChatGPT plugin directory requires a verified-publisher listing**, which is an owner-side submission step (the bundle is prepared in [docs/distribution/submission-bundle.md](docs/distribution/submission-bundle.md)). Until that listing is live, ChatGPT users' cleanest path is Codex (above) — same OpenAI account, full pipeline — or the claude.ai hero-skill uploads if they also use Claude.
- **On any AP1.0 host without subagent dispatch**, the pipeline behaves exactly as described for Codex: sequential phases, every gate intact, the run auditor still the last word.

### Cursor, Copilot CLI, Antigravity, Grok, Hermes, OpenClaw — the same contract

Every remaining surface follows the same pattern — a native manifest wrapping the same `skills/` directory, the portable lane where subagent dispatch is missing:

- **Cursor 2.5+**: `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` — full skills + agents + commands.
- **GitHub Copilot CLI**: `copilot plugin install contentforge@neels-plugins` — full skills + MCP; custom slash commands aren't supported by Copilot CLI yet (open issue), so invoke by natural language.
- **Google Antigravity 2.0**: `agy plugin install https://github.com/indranilbanerjee/contentforge` — full skills + hooks; subagents spawn via the `/agent` CLI.
- **Grok (xAI Build CLI)**: `grok plugin install indranilbanerjee/contentforge` — native `.grok-plugin/` pair; Grok also reads the Claude manifests for compatibility.
- **Hermes Agent / OpenClaw**: native adapters at repo root (`plugin.yaml` + `__init__.py`, `openclaw.plugin.json`) registering all 22 skills.

Whatever the surface, the invariants hold: same skills, same scripts, same artifacts, same gates, same honesty rules. The platform changes how phases are *dispatched*, never what they must *prove*.

---

## Cross-platform compatibility

| Platform | Status | Notes |
|---|---|---|
| **Anthropic Cowork + Google Drive** | ✅ **Recommended for teams** | The friendliest UX for non-CLI marketing teams. `/plugin` commands + HTTP MCPs work natively. Pipeline outputs — and the v4.0 lifecycle stores — route to Google Drive instead of the Cowork sandbox: files persist, are team-shareable, and the loop compounds across sessions. One-time setup: `/contentforge:cf-cowork-setup` after install. |
| Anthropic Cowork (without Drive) | ⚠️ Single-session only | All ContentForge commands run, but generated files land in the Cowork Linux sandbox — visible during the session, **gone after** — and the lifecycle loop cannot compound. Connect Google Drive in Cowork Settings → Integrations (60 seconds) to upgrade. |
| Claude Code CLI | ✅ Full local support | Reference environment for developers. Files land in `~/Documents/ContentForge/<brand>/...` on your host. Every feature tested here first. |
| Claude Code IDE extension (VS Code / JetBrains) | ✅ Full local support | Same as CLI; uses host filesystem. |
| Standard Claude chat (browser `claude.ai` OR installed Claude Desktop app) | ❌ `/plugin` slash commands not available | Plugins still install and run via the **Plugins** UI button at the bottom of the chat. Additionally (v4.1.0): five hero skills ship as [`.skill` release assets](https://github.com/indranilbanerjee/contentforge/releases/latest) you can upload directly — claude.ai → Settings → Capabilities (enable *Code execution and file creation*) → Customize → Skills → Upload skill. |
| **OpenAI Codex** CLI + IDE + App | ✅ Full skills + MCP support | `codex plugin install contentforge@neels-plugins`. Same 22 skills, same scripts. On builds without subagent dispatch, the portable execution lane runs the full pipeline sequentially with every gate intact. |
| **Cursor 2.5+** | ✅ Full skills + agents + commands | `/add-plugin contentforge@https://github.com/indranilbanerjee/contentforge` in any Cursor Agent chat. |
| **GitHub Copilot CLI** | ✅ Full skills + MCP | `copilot plugin install contentforge@neels-plugins`. Custom slash commands not yet supported in Copilot CLI (open issue) — invoke skills by natural language. |
| **Google Antigravity 2.0** CLI + IDE | ✅ Full skills + hooks | `agy plugin install https://github.com/indranilbanerjee/contentforge`. Subagents need `/agent` CLI spawning; slash commands fold into skills. |
| **Grok** (xAI Build CLI) | ✅ Full skills | `grok plugin install indranilbanerjee/contentforge` (native `.grok-plugin/` pair; Grok also reads the Claude Code manifests for compatibility). Pipeline runs via the portable execution lane. |

### How to pick

- **For agencies, in-house content teams, or anyone whose team isn't deep in CLI tools** → Use Cowork + Drive. Run `/contentforge:cf-cowork-setup` once, then everyone uses `/contentforge:create-content` normally and outputs land in your shared Drive folder. No local installs needed per team member.
- **For solo developers or technical content engineers** → Use local Claude Code (CLI or IDE extension). Files land in `~/Documents/ContentForge/` on your machine. Git-friendly. No Drive setup needed.
- **For shipping to clients with strict on-prem-only data policies** → Use local Claude Code (no cloud dependency).

Run `/contentforge:cf-environment` after install to see exactly what's available in your specific runtime, with a per-capability matrix. Run `/contentforge:cf-cowork-setup` if you're in Cowork and haven't wired Drive yet.

---

## Star history

[![Star History Chart](https://api.star-history.com/svg?repos=indranilbanerjee/contentforge&type=Date)](https://star-history.com/#indranilbanerjee/contentforge&Date)

---

## About the maintainer

ContentForge is built and maintained by **[Indranil "Neel" Banerjee](https://indranil.in)** — a builder and systems thinker with roots in information security and a second act across growth marketing, enterprise digital operations, and AI transformation. This repository is one public implementation of a broader focus on trustworthy AI execution: preserve context, make evidence inspectable, and keep people at consequential decision points.

- 🌐 **Website:** [indranil.in](https://indranil.in)
- 💼 **LinkedIn:** [linkedin.com/in/askneelnow](https://www.linkedin.com/in/askneelnow)
- 🐦 **X / Twitter:** [@askneelnow](https://x.com/askneelnow)
- 💻 **GitHub:** [@indranilbanerjee](https://github.com/indranilbanerjee)
- 📦 **Other plugins:** [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) · [SocialForge](https://github.com/indranilbanerjee/socialforge)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/contentforge/discussions)
- 🐛 **Bug reports:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- 🔒 **Security:** [Private Security Advisory](https://github.com/indranilbanerjee/contentforge/security/advisories/new) (see [SECURITY.md](SECURITY.md))

If ContentForge saves your team time, [⭐ star the repo](https://github.com/indranilbanerjee/contentforge/stargazers). Sharing it on **LinkedIn** or **X** helps people discover the work too.

---

## Contributing

PRs welcome — especially on the 43-pattern AI-detection catalog, industry-specific content templates, and platform-specific schema improvements. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) for the PR checklist, and [TESTING-GUIDE.md](TESTING-GUIDE.md) for the per-phase test checklist. All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Security issues: use [Private Security Advisories](https://github.com/indranilbanerjee/contentforge/security/advisories/new) per [SECURITY.md](SECURITY.md) — do not file public issues for vulnerabilities.

---

## Neelverse Marketing Suite

ContentForge is part of a three-plugin suite by [Indranil Banerjee](https://indranil.in) that share the same brand profiles and marketplace. **Each plugin is fully standalone** — install any one by itself and every capability it documents works; the others simply add more tools:

| Plugin | What it does |
|---|---|
| [Digital Marketing Pro](https://github.com/indranilbanerjee/digital-marketing-pro) | End-to-end engagement methodology — 12-Part Strategy Flow, Four Core Documents, 24 agents, 163 skills |
| **ContentForge** (this plugin) | Publication-ready content via 10-phase pipeline + lifecycle loop, fact-checker, 43-pattern AI-detection humanizer, `.docx` export with C2PA signing |
| [SocialForge](https://github.com/indranilbanerjee/socialforge) | Social media calendar with asset-first compositing, AI image + video via your connected providers, delivery audit, C2PA signing |

```
/plugin marketplace add indranilbanerjee/neels-plugins
/plugin install digital-marketing-pro@neels-plugins
/plugin install contentforge@neels-plugins
/plugin install socialforge@neels-plugins
```

---

## Release notes

**v4.1.2 (2026-08-17)** — **Schema-clean hooks manifest.** Cowork's plugin validation rejects unknown top-level fields in `hooks.json`; ours carried a `_readme` rationale field (reported as [digital-marketing-pro#9](https://github.com/indranilbanerjee/digital-marketing-pro/issues/9) — all three suite plugins shipped the same defect). Rationale moved to `hooks/README.md`, manifest reduced to exactly `{"hooks": {}}`, guarded by `TestHooksManifestSchemaClean`. Translations re-stamped. **Tests 520 → 522.**

**v4.1.1 (2026-08-17)** — **The README goes global, and shows its receipts.** **(1) Twelve languages.** The README now ships in English plus 11 full translations (हिन्दी, 中文, 日本語, 한국어, Español, Português, العربية, اردو, தமிழ், বাংলা, Русский), each version-stamped ("Synced with English README v4.1.1") and guarded by a new `tests/test_readme_translations.py` — a translation that silently falls behind the shipping version fails the suite, the same discipline every other count and claim in this repo lives under. The English README is declared the source of truth in every file. **(2) Real artifacts in the Examples.** The validated August run's actual outputs are now embedded: the chart the pipeline rendered, the delivered opening prose, three verbatim before→after humanizer edits from the Phase 6.5 report, the run auditor's CLEAN verdict JSON, and a scorecard SVG whose every number is read from the run's own artifacts. **(3) OpenAI surfaces documented at full depth.** A new section walks through exactly how the pipeline runs on Codex (CLI/IDE/App) and what Agent Plugins 1.0 means for ChatGPT — mechanically, with the portable execution lane's guarantees stated and the directory-listing status stated honestly. The Updating section now covers all nine platforms plus claude.ai re-uploads, not just Claude Code. **(4)** Author banner + sponsor call-to-action at the top; the real-run chart and scorecard live in `docs/assets/`.

**v4.1.0 (2026-08-17)** — **Two new surfaces.** **(1) Grok (xAI Build CLI) becomes the ninth native platform.** A first-class `.grok-plugin/` manifest pair (`plugin.json` + single-plugin `marketplace.json`) makes `grok plugin install indranilbanerjee/contentforge` work directly — Grok also reads the Claude Code manifests for compatibility, but the native pair is what an official xAI marketplace listing points at. Both files are version-locked into the release-consistency suite, so they can never drift from the other manifests silently. **(2) Hero skills ship as claude.ai `.skill` release assets.** `config/skill-assets.json` declares the five skills that are safe standalone on claude.ai (`cf-brief`, `cf-social-adapt`, `cf-translate`, `cf-video-script`, `cf-aeo-check`) plus each one's config/template dependencies; `scripts/build-skill-assets.py` packages them deterministically (byte-identical rebuilds) with those dependencies bundled at the same relative paths the prose references — and **refuses to build** any skill whose SKILL.md references `${CLAUDE_PLUGIN_ROOT}` or an undeclared repo file (plant-checked, both directions). The pipeline skill is guard-excluded: it needs subagent dispatch and must never masquerade as a standalone upload. **Tests 498 → 514.**

**v4.0.0 (2026-08-17)** — **The lifecycle release.** ContentForge 3.x produced excellent pieces and forgot them; 4.0 makes production, measurement, and planning one auditable system. **(1) The lifecycle loop closed by file contracts.** New `scripts/audit-ledger.py`: `/contentforge:audit-content` now RECORDS its findings (schema-validated — pieces with freshness scores, ranked refresh priorities, recommended scopes, gap topics, and a required `aeo_history_considered` field, because "not consulted" and "consulted" must never be the same answer) into `audits/` per brand; `cf-calendar --from-audit=latest` and `content-refresh` read the recorded candidates by file, across sessions — before this, the calendar's documented read of "the most recent cf-audit output" resolved to nothing once the session ended. `cf-aeo-check`'s append-only history now feeds the freshness model (lost AI citations deduct, with the deduction named). And Phase 1's verified link inventory merges into `brand_pages` automatically after Gate 1 (`harvest-brand-pages.py --merge-inventory`): product/authority pages upsert with freshness stamps, manual curation never overwritten, **conversion pages only staged for human confirmation** — a CTA is a commercial decision the system must not make. **(2) The pipeline contract as data.** `config/pipeline-graph.json` declares nodes, reads/writes, gates, and budgeted loop edges; `tests/test_pipeline_contract_graph.py` drift-guards it both directions against agent contracts, the orchestrator's table, `checkpoint-manager.py`, and `run-audit.py`. Encoding the table immediately surfaced six under-declared inputs (including Phase 8's real dependency on the SEO scorecard and humanization report, and Phase 5's on the annotated draft whose anchors must survive). **(3) Telemetry with floors.** New `scripts/telemetry.py` aggregates loop edges + reasons, phase timings, and the humanizer's new `phase-6.5-pattern-hits.json` across runs; `cf-analytics` renders loop-edge and pattern panels; recurring patterns reach the Phase 3 brief as advisories behind a ≥3-run recurrence floor. Pre-4.0 runs count as `not_instrumented` — unknown, never zero — and advisories never touch a gate, a threshold, or a verdict, by contract and by test. Design specs for the two follow-on stores (the living link graph and the per-brand claim library) are committed at `research/2026-08-17-link-graph-and-claim-library-spec.md` — deliberately specified before being built. **Tests 464 → 498.**

**v3.33.x (2026-08-16/17)** — **The audit-hardening arc.** v3.33.0: `scripts/run-audit.py` productized (the instrument that found most of the month's 38 defects), `finalize --status completed` refuses without a CLEAN verdict, deterministic `feature_card.py` closes the last blocker class with no pipeline-native exit. v3.33.1: Agent Plugins 1.0 listing metadata + the directory submission bundle. v3.33.2: the documentation truth pass (every live count re-derived from the filesystem; the count guard grew the phrasings that had been escaping it). v3.33.3: a valid VISUAL anchor with `->` arrows in its description was invisible to a `[^>]` parser — found by the first fully-live customer-perspective run, fixed with regression tests proven against the shipped parser. v3.33.4: figure furniture (alt text + captions) no longer counts as body prose, and the keyword-in-conclusion check reads the Conclusion, not the References tail. **Tests 452 → 464.**

**v3.32.0 (2026-08-16)** — **Agent Plugins 1.0 + the portable execution lane.** Root `plugin.json` on OpenAI's vendor-neutral closed schema; `${PLUGIN_DATA}` accepted everywhere the `CLAUDE_*` names were; and on platforms with no subagent dispatch the pipeline runs sequentially in one conversation — each agent contract read as phase instructions, same artifacts, same gates, same loop budgets. Also: the Phase 3.5 embedding-contract reconciliation, label-bearing diagrams routed off the AI image path, reviewer RE-REVIEW MODE, comparative percentiles need five prior pieces. **Tests 409 → 430.**

**v3.27.0–v3.31.1 (2026-08-15/16)** — **The fix-ledger arc.** Five releases, each found by running the real pipeline and auditing the artifacts: corrections that were unappliable by contract got a machine-verified ledger (applied by script, authorship-guarded, re-verified after every phase); the reader stopped being shown production scaffolding; `mark_complete` stopped undoing the publication gate; a remedy that manufactured false regression accusations was replaced by `resolve`; and Gate 4's evidence became evidence (`validate --target` proves every correction lands). Plus the counting convention, byte-stable checkpoints, and orphaned-artifact-aware resume. **Tests 335 → 409.**

**v3.23.x–v3.26.x (2026-08-14/15)** — **Craft + calibration.** Author-draft protection (`--source-draft`: your sentences verbatim, catalog-exempt, `authorship.py` BLOCKS on paraphrase/drop), significance markers deleted never reworded, entity development, provenance-accurate disclosure gated on the authorship record; the humanize gate measured against a pre-ChatGPT human corpus (39 documents, 272 chunks) and told the truth about what it proves; the aphorism proxy stopped marking down a genuinely good published essay. **Tests 248 → 335.**

**v3.22.0 (2026-08-13)** — **Honest provenance + the structural tier.** Brand-configurable `ai_disclosure` (uncertain⇒disclose fail-safe), StoryScope-derived `--structure-scan`, two-tier human review sheet (`build_review_sheet.py`) in every lane. Built on transparency, never evasion — no watermark detection or removal, permanently. **Tests 248 → 273.**

**v3.21.x (2026-08-12)** — **The Express Lane, battle-tested — and craft-complete.** Bring-your-own-research lane keeping every verification gate; structure + humanizer default-ON in express (craft ≠ ceremony); execution battle-test with planted defects; all 22 skill descriptions trigger-dense; vendor-neutrality guard. **Tests 224 → 248.**

**v3.19.x–v3.20.0 (2026-08-07/12)** — **Client-site intelligence + the creator-craft wave.** `harvest-brand-pages.py`, Client Site Reconnaissance + deep-link rule, humanizer catalog 35→43 with the Human-Expert Grounding Pass, advisory `--ai-tell-scan`, Deletion Ledger, climax-first openings, video scripts through the full quality machinery, `references/` contract machine-enforced, `test_doc_counts.py`. **Tests 173 → 224.**

**v3.16.0–v3.18.x (2026-07-07/30)** — **Reliability & Truth + the audit series + four capabilities.** Checkpoint/resume actually wired, file-based phase handoff contract, measured gates via `text-metrics.py`, `_common.py` (single slugifier, atomic writes, UTF-8 guard), honest "10 phases / 10 quality gates" claim; the interconnection audit that found three never-dispatched agents; E-E-A-T byline layer, case studies (client-data provenance rule — fabricating a client metric halts the pipeline), newsletters, `cf-aeo-check`; the source-anonymity guard. **Tests 53 → 173.**

**v3.9.x–v3.15.x (2026-05/06)** — **The foundation releases.** Task-tool orchestration mandate (v3.9.4), real `.docx` output with appendices, three-category internal linking + `brand_pages` schema (v3.9.5), C2PA provenance for EU AI Act Article 50 (v3.10.0), model curator (v3.12.2), dual-copy output + checkpoint/resume (v3.12.3), native manifests for 8 platforms (v3.13.0–v3.15.0), release-consistency test suite (v3.15.1).

**Earlier versions:** see [CHANGELOG.md](CHANGELOG.md) for the complete history back to v3.0.

---

## License

MIT — see [LICENSE](LICENSE).

## Sponsor this project

This plugin is MIT-licensed, free to use commercially, and collects no telemetry. What
sponsorship pays for is the unglamorous half of keeping it accurate: platform-API updates
when a vendor ships a breaking version, model-registry refreshes when a model is retired,
compliance passes when regulatory guidance moves, and issue triage.

If it saves your team time, you can [sponsor the work](https://github.com/sponsors/indranilbanerjee).
Sponsors from $25/mo are listed in [SPONSORS.md](SPONSORS.md).

[![Sponsor](https://img.shields.io/badge/sponsor%20on%20GitHub-%E2%9D%A4-ea4aaa?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/indranilbanerjee)

---

## Support

- **Issues:** [GitHub Issues](https://github.com/indranilbanerjee/contentforge/issues)
- **Discussions:** [GitHub Discussions](https://github.com/indranilbanerjee/contentforge/discussions)

## Credits

Created by [Indranil Banerjee](https://indranil.in). Built for Claude Code and Anthropic Cowork. Powered by Anthropic Claude.

---

<sub>Made with care by [Indranil Banerjee](https://indranil.in) · MIT-licensed · [⭐ Star the repo](https://github.com/indranilbanerjee/contentforge) if it helps you</sub>

Humanizer 43-pattern catalog adapted from [Wikipedia: Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) (CC BY-SA, WikiProject AI Cleanup) with structure influenced by [blader/humanizer](https://github.com/blader/humanizer) (MIT).
