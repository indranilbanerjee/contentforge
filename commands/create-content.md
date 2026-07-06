---
description: Run the full 10-phase content production pipeline — research, draft, fact-check, humanize, and publish
argument-hint: "<topic> [content type]"
---

# Create Content

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

This command is a **thin wrapper** around the ContentForge pipeline skill. It parses the user's inputs, then invokes the `contentforge` skill ([skills/contentforge/SKILL.md](../skills/contentforge/SKILL.md)), which owns the full Execution Protocol: run initialization, Step 0.5 title curation, the Pipeline Contract (phases 1–8, 10 quality gates), per-phase checkpointing, loop management, and the final .docx delivery. **Do not re-implement any pipeline logic here.**

## Trigger

User runs `/contentforge:create-content` or asks to write, draft, create, or produce content (articles, blog posts, whitepapers, FAQs, or research papers).

## Step 1 — Parse and gather inputs

Collect the following. If a required input is missing, ask before proceeding:

**Required:**
1. **Topic** — the subject the content is about (e.g., "AI in Healthcare"). This is NOT the final title.
2. **Content type** — one of: `article`, `blog`, `whitepaper`, `faq`, `research_paper`. Word-count and readability standards per type are defined in the skill's Content Types & Specifications table.
3. **Brand** — which brand profile to use. If none exists, offer `/contentforge:brand-setup` or the skill's No-Brand Mode (non-regulated topics only).

**Optional flags (pass through to the skill unchanged):**
- `--audience="..."` — target audience (e.g., "Healthcare CIOs")
- `--keyword="..."` — primary SEO keyword
- `--word-count=<n>` — overrides the content-type default
- `--tone=<authoritative|conversational|technical|witty>` — overrides brand default
- `--sources=<urls or file>` — user-supplied references (required in No-Web Mode)
- `--title="Exact Title"` — non-interactive title bypass (skips Step 0.5 option generation)
- Competitor URLs to differentiate from

## Step 2 — Invoke the pipeline skill

Invoke the **contentforge skill** (`skills/contentforge/SKILL.md`) with the gathered inputs. The skill performs, in order:

1. Pre-flight brand-profile validation (guardrails required for regulated industries)
2. Step 0 run initialization (checkpoint-manager `init` with run metadata + pipeline-tracker `init`)
3. Step 0.5 title curation (inline, user-confirmed, unless `--title` was passed)
4. Phases 1–8 per the Pipeline Contract table, with orchestrator-verified gates and a checkpoint save after every gate PASS
5. Finalization: dual-copy .docx save (run directory + `~/Documents/ContentForge/{Brand}/`), optional Drive upload, Completion Card

Every gate-passed phase is checkpointed, so an interrupted run is resumable with `/contentforge:resume`.

## Output

Defined by the skill's Final Output Requirements: a publication-ready `.docx` (title page, article body, citations, Appendices A/B/C), the Quality Scorecard, the SEO meta package, and the Completion Card.

## After Content Creation

Ask: "Would you like me to:
- Promote this on social media? (`/contentforge:social-adapt`)
- Publish to your CMS? (`/contentforge:publish`)
- Translate for other markets? (`/contentforge:translate`)
- Create A/B headline variants? (`/contentforge:cf-variants`)
- Generate a content brief for a related topic? (`/contentforge:content-brief`)
- Run batch production for multiple topics? (`/contentforge:batch-process`)"
