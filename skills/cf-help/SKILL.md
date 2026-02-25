---
description: "Show the ContentForge user guide, available skills, pipeline overview, examples, and troubleshooting"
---

# /cf:help

Show the ContentForge user guide with setup instructions, pipeline overview, available skills, usage examples, and troubleshooting.

## Behavior

When invoked, display a structured help overview. Use the comprehensive documentation in `docs/USER-GUIDE.md` for full details.

### 1. Quick Start Summary

Display this quick orientation:

```
=== CONTENTFORGE — HELP ===

Version: 3.1.0
Agents: 12 (9-phase pipeline + 3 post-pipeline)
Skills: 18 slash commands (/cf:* + /contentforge + /batch-process + /content-refresh)
Connectors: 6 HTTP + 16 npx integrations

Getting Started:
  1. /cf:style-guide         — Create your brand profile (start here)
  2. /cf:integrations         — See which connectors are active
  3. /contentforge            — Run the full 9-phase content pipeline
  4. /cf:help --examples      — See example prompts and workflows
```

### 2. Arguments

| Argument | Effect |
|----------|--------|
| (none) | Show the full help overview |
| `--pipeline` | Show the 9-phase pipeline with timing and quality gates |
| `--skills` | List all 17 skills with descriptions |
| `--brand` | Explain brand profile setup methods |
| `--examples` | Show example workflows from brief to publish |
| `--troubleshoot` | Show common issues and solutions |
| `--connectors` | Show connector status (shortcut for /cf:integrations) |

### 3. Pipeline Overview

When `--pipeline` is specified, show the 9-phase pipeline:

```
=== CONTENTFORGE PIPELINE ===

Phase 1: Researcher (3-5 min)
  → Web research, 15-25 sources, relevance scoring

Phase 2: Fact Checker (2-3 min)
  → URL verification, claim validation, source grading

Phase 3: Content Drafter (5-8 min)
  → Brand-voiced draft with inline citations

Phase 4: Scientific Validator (2-3 min)
  → Hallucination detection, claim cross-referencing

Phase 5: Structurer & Proofreader (2-3 min)
  → Heading hierarchy, readability, grammar, formatting

Phase 6: SEO/GEO Optimizer (2-3 min)
  → Keywords, meta tags, schema, AI Overview optimization

Phase 6.5: Humanizer (2-3 min)
  → AI pattern removal, personality profiles, industry patterns

Phase 7: Reviewer (2-3 min)
  → 5-dimension scoring (needs ≥7.0), comparative analysis

Phase 8: Output Manager (1-2 min)
  → .docx generation, Drive upload, tracking sheet update

Post-Pipeline:
  → Social Adapter (#10): Article → social posts
  → Translator (#11): Multilingual with brand voice
  → Batch Orchestrator (#9): Parallel processing

Quality Gates: Score ≥7.0 required | Max 2 loops per phase | 5 total loops max
Three-Layer Verification: Fact Checker → Scientific Validator → Reviewer
Result: Zero hallucinations in production
```

### 4. All Skills

When `--skills` is specified, list all 17 skills:

| Skill | Description |
|-------|-------------|
| `/contentforge` | Run the full 9-phase content production pipeline |
| `/batch-process` | Process 10-50+ pieces in parallel from Google Sheets |
| `/content-refresh` | Update existing content with fresh data and sources |
| `/cf:style-guide` | Create or update a brand profile interactively |
| `/cf:integrations` | See which connectors are active and available |
| `/cf:connect <name>` | Step-by-step setup guide for any connector |
| `/cf:publish` | Push content to Webflow/WordPress or export HTML |
| `/cf:social-adapt` | Transform article into social posts (5 platforms) |
| `/cf:variants` | Generate A/B test variations of headlines, hooks, CTAs |
| `/cf:analytics` | Quality score trends, timing breakdown, brand performance |
| `/cf:translate` | Translate preserving brand voice (15+ languages) |
| `/cf:video-script` | Timestamped video scripts for YouTube, TikTok, Reels |
| `/cf:brief` | Research-backed content brief with keyword analysis |
| `/cf:audit` | Content freshness scoring, decay detection, gap analysis |
| `/cf:calendar` | Production scheduling with deadline tracking |
| `/cf:template` | Create custom content type templates |
| `/cf:help` | This help guide |

### 5. Brand Setup Quick Reference

When `--brand` is specified, explain the 3 setup methods:

```
=== BRAND PROFILE SETUP ===

Method 1: Interactive (Recommended)
  /cf:style-guide
  → Answer questions about voice, terminology, industry, guardrails
  → Generates brand profile JSON automatically

Method 2: Manual JSON
  → Copy config/brand-registry-template.json
  → Fill in your brand details
  → Save to your brand config directory

Method 3: Google Drive Knowledge Vault
  → Create a folder: "ContentForge Brands/[Brand Name]/Knowledge Vault"
  → Add documents: voice-and-tone.md, terminology.md, prohibited-claims.md
  → ContentForge auto-extracts on first run (SHA256 cached)

Brand Profile Includes:
  - Voice & Tone (authoritative, conversational, technical, witty)
  - Terminology (approved terms, banned phrases)
  - Style Guide (formatting, citation style)
  - Guardrails (topics to avoid, compliance)
  - Industry Context (Pharma, BFSI, Healthcare, Legal)
  - Personality Profile (4 profiles for Humanizer)

Profiles are cached (SHA256 hash) — 95% time savings on repeat runs.
```

### 6. Example Workflows

When `--examples` is specified, show practical end-to-end examples:

```
=== EXAMPLE: First Article ===

Step 1: Create brand profile
  /cf:style-guide
  → Provide: Brand name, industry, voice, terminology, guardrails

Step 2: Generate content brief (optional but recommended)
  /cf:brief "AI-Powered Diagnostics in Healthcare"
  → Gets: Keyword analysis, competitor review, recommended outline

Step 3: Run the pipeline
  /contentforge "AI-Powered Diagnostics: The Future of Precision Medicine"
    --type=article --brand=AcmeMed --audience="Healthcare Executives"
    --keyword="AI diagnostics precision medicine"
  → 20-30 minutes → Quality score 9.1/10

Step 4: Publish
  /cf:publish --platform=webflow
  → Or: /cf:publish --export=html (for manual upload)

Step 5: Create social posts
  /cf:social-adapt
  → LinkedIn, Twitter/X, Instagram, Facebook, Threads posts

Step 6: Translate for global audience
  /cf:translate --language=es --level=adapted
  → Spanish version preserving brand voice


=== EXAMPLE: Batch Processing ===

Step 1: Prepare Google Sheets with columns A-N:
  A: Requirement ID | B: Content Type | C: Title | D: Audience
  E: Brand | F: Primary Keyword | G: Target Words | H: Priority
  I: Tone Override | J: Status | K: Score | L: Output URL
  M: Processing Time | N: Completed At

Step 2: Run batch
  /batch-process --sheet="Content Q1 2026" --rows=1-20
  → Processes 20 pieces in parallel (4-5x faster)

Step 3: Review results
  /cf:analytics --period=30
  → Quality trends, timing breakdown, brand performance
```

### 7. Troubleshooting

When `--troubleshoot` is specified, show common issues:

| Issue | Solution |
|-------|----------|
| "Brand profile not found" | Run `/cf:style-guide` to create your brand profile |
| Quality score below 5.0 | Content flagged for human review — check topic complexity and source availability |
| "Research timeout" | Check internet connection; ContentForge needs web access for Phase 1 research |
| Google Drive not showing in connectors | Google Drive is a platform-level integration — check Claude Desktop → Settings → Integrations |
| MCP connector not working | Run `/cf:integrations` to check status, `/cf:connect <name>` for setup |
| Pipeline taking too long | Normal: 20-30 min for articles. For faster: use `/batch-process` for parallel processing |
| Humanizer removing too much | Adjust personality profile: `/contentforge --tone=conversational` for lighter touch |

### 8. Documentation References

Point users to these resources:

| Guide | What it covers |
|-------|---------------|
| `docs/USER-GUIDE.md` | Comprehensive end-to-end guide (1,300+ lines) |
| `UPGRADE-GUIDE.md` | v2.1.0 → v3.0.0 migration guide |
| `CONNECTORS.md` | All available connectors by category |
| `CHANGELOG.md` | Full version history and release notes |
| `config/brand-registry-template.json` | Brand profile JSON template |
| `config/social-platform-specs.json` | Social platform constraints and specs |
| `config/multilingual-patterns.json` | Language-specific brand voice patterns |
| `templates/` | Content type templates and formats |

## Output Format

Present information in clean, scannable tables and code blocks. Keep the output concise. Link to `docs/USER-GUIDE.md` for full walkthroughs.
