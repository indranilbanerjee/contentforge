---
name: contentforge
description: Produce publication-ready, fact-checked, brand-aligned content via 10-phase autonomous pipeline. Use for any content need.
argument-hint: "[topic]"
effort: max
---

# ContentForge — Enterprise Content Production

Transform a content requirement into a publication-ready, fact-checked, brand-compliant, SEO-optimized piece through a 10-phase autonomous agent pipeline (plus Step 0.5 title curation) with three-layer fact verification and 10 quality gates.

## Context efficiency

Pipeline phase. **Grep before Read** for `references/`, `humanization-patterns.json`, brand voice profiles. Hand subagents artifact **file paths** plus a ≤10-line summary — never reload or inline full drafts (see Context & Handoff Rules). On `/contentforge:resume`, load `run.json` plus only the artifacts the next phase contractually needs.

## Execution Protocol (CRITICAL — read first)

This skill orchestrates 10 phases plus Step 0.5 (Title Curation). **Each numbered phase MUST be executed by invoking its dedicated subagent via the `Task` tool — DO NOT generate the deliverable yourself in a single inference pass.** A single-pass generation skips the quality gates, fact-checking layers, humanizer 29-pattern catalog, and reviewer scoring that define ContentForge.

The one exception is Step 0.5: title curation is performed **inline by the orchestrator** (no subagent), because it requires user interaction and subagents must never wait on the user. Any subagent that needs a user decision returns a `{"status": "needs_user_decision", ...}` payload to the orchestrator, which owns all user interaction (including image-generation opt-in/approval).

### Step 0 — Initialize the run (orchestrator only, before Step 0.5)

```bash
# 1. Create the checkpoint run (returns run_id). Capture run metadata so a
#    cross-session resume can recover keyword, audience, word count, and tone.
RUN_RESULT=$(python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py init \
    --brand <brand-slug> --topic "<topic>" --content-type <type> \
    --meta '{"keyword": "<primary keyword>", "audience": "<audience>", "word_count_target": <n>, "tone": "<tone>"}')
# Parse RUN_ID from the JSON result's "run_id" field.

# 2. Initialize the performance tracker for this run.
python ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-tracker.py --action init \
    --brand <brand-slug> --run-id "$RUN_ID" --content-type <type> --topic "<topic>"
```

Rules:
- `pipeline-tracker.py` is called by the **orchestrator only** — subagents never call it.
- Step 0.5 is **exempt** from tracker calls (no `phase-start`/`phase-end` for 0.5). After the title is confirmed, checkpoint it directly (see contract table).

### Required Per-Phase Workflow (Phases 1–8)

For every numbered phase:

1. **Mark phase start** (orchestrator):
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-tracker.py --action phase-start --brand <slug> --run-id "$RUN_ID" --phase <N>
   ```
2. **Call `Task` with the phase's qualified `subagent_type`** (e.g. `contentforge:researcher`). The Task prompt contains ONLY:
   - the artifact **file paths** the phase reads (per the Pipeline Contract table),
   - a **≤10-line orchestrator summary** of pipeline state,
   - the **brand-profile path** (required for phases 0.5, 3, 5, 6, 6.5, 7),
   - the **original-requirements block** (topic, confirmed title, content type, audience, primary keyword, word-count target, tone).

   Subagents `Read` what they need from those paths. **Never inline a full draft into a Task prompt.**
3. **Verify the quality gate yourself.** Gate ownership belongs to the **orchestrator**: check the returned artifact against the gate criteria in the Pipeline Contract table — count sources, check word count and citation density, and run `python ${CLAUDE_PLUGIN_ROOT}/scripts/text-metrics.py` for burstiness, Flesch-Kincaid grade, and keyword-placement checks. A subagent's self-reported "PASS" alone is **not** a gate pass.
4. **On gate PASS, checkpoint the artifact** so the run is resumable:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py save \
       --brand <slug> --run-id "$RUN_ID" --phase <N> --content-file <artifact-path> --extension <md|json|txt>
   ```
   Phases 3.5 and 6 also produce a companion manifest (`phase-3.5-visual-manifest.json`, `phase-6-structure-manifest.json`) — place it at its canonical path inside the same run directory.
5. **Mark phase end** with the output word count:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/pipeline-tracker.py --action phase-end --brand <slug> --run-id "$RUN_ID" --phase <N> --content-words <count>
   ```
6. **Emit the audit line** (so users can see real-time progress):
   ```
   [PHASE-AUDIT] phase=<N> name=<name> status=<PASS|FAIL> output_summary="<one line>" gate=<PASS|FAIL>
   ```
7. **On gate FAIL, loop per the contract table's loop-target column.** Before looping, record the loop and check limits:
   ```bash
   python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py loop --brand <slug> --run-id "$RUN_ID" --edge phase_<N>_to_<target>
   ```
   **Limits: max 2 loops per edge, max 5 loops total per run.** If a limit is reached: do NOT loop — mark the run for human review, `finalize --status failed`, and halt. When Phase 7 orders rework, the `pending_rework` field in `run.json` records the target phase and the reviewer's feedback so `/contentforge:resume` continues the rework instead of skipping it. Do not overwrite the saved checkpoint of an upstream phase that already passed — re-save only the looped phase when it passes.

### Image approval (orchestrator-owned, after Phase 3.5)

The visual-asset-annotator never waits on the user. It generates candidates (when image generation is opted in) and records each in `phase-3.5-visual-manifest.json` with `approved_by_user: false`. After Gate 3.5 passes, the **orchestrator** presents the generated visuals to the user for approval:

1. Show each generated asset (path + description + placement) and ask approve / regenerate / drop.
2. Update `approved_by_user` in the manifest for approved assets.
3. For rejects, re-invoke `contentforge:visual-asset-annotator` with the rejection feedback (counts as a Phase 3.5 re-run, not a loop edge).
4. Phase 8 embeds **only** assets with `approved_by_user: true` — unapproved assets stay out of the .docx.

If the annotator returns `{"status": "needs_user_decision", ...}` (e.g., image-generation opt-in was never given), ask the user, then re-invoke with the answer.

### Pipeline Contract (inputs → outputs → gate → loop target)

All artifacts live in the canonical run directory `~/.claude-marketing/{brand-slug}/runs/{run_id}/` alongside `run.json` (the manifest).

| Phase | subagent_type | Reads (paths) | Writes (artifact) | Quality gate (orchestrator-verified) | Gate-FAIL loop target |
|-------|---------------|---------------|-------------------|--------------------------------------|-----------------------|
| 0.5 | — inline (orchestrator) | brand profile, requirements | `phase-0.5-title.txt` | User-confirmed title (or `--title` bypass) — user checkpoint, not a numbered quality gate | Regenerate title options |
| 1 | `contentforge:researcher` | `phase-0.5-title.txt`, requirements, brand profile | `phase-1-research.md` | **Gate 1:** 12–15 sources collected; ≥10 citable; ≥5 with reliability ≥8; differentiated angle documented | Re-run Phase 1 with broader search |
| 2 | `contentforge:fact-checker` | `phase-1-research.md` | `phase-2-factcheck.md` | **Gate 2:** ≥80% of claims verified; zero UNRESOLVED flags (flagged claims must be removed or re-sourced); ≤3 unverified tolerated; all cited URLs live | Phase 1 (find alternative sources) |
| 3 | `contentforge:content-drafter` | `phase-1-research.md`, `phase-2-factcheck.md`, brand profile, requirements | `phase-3-draft.md` | **Gate 3:** word count ±10% of target; all outline sections covered; ≥1 citation per 300 words | Re-run Phase 3 |
| 3.5 | `contentforge:visual-asset-annotator` | `phase-3-draft.md`, `phase-2-factcheck.md` | `phase-3.5-visuals.md` + `phase-3.5-visual-manifest.json` | **Gate 3.5:** every chart traceable to a verified statistic; manifest complete (placement, alt text, data source); human-action TODOs marked | Re-run Phase 3.5 |
| 4 | `contentforge:scientific-validator` | `phase-3-draft.md`, `phase-3.5-visual-manifest.json`, `phase-2-factcheck.md` | `phase-4-validation.md` | **Gate 4:** zero hallucinations; every claim traceable to a cited source; logic consistent | Phase 3 (with the specific claims to fix) |
| 5 | `contentforge:structurer-proofreader` | `phase-3-draft.md`, `phase-4-validation.md`, brand profile | `phase-5-structured.md` | **Gate 5:** zero grammar/spelling errors on re-scan; readability within ±0.5 grade of the content-type target (`text-metrics.py`); brand terminology compliance | Re-run Phase 5 |
| 6 | `contentforge:seo-geo-optimizer` | `phase-5-structured.md`, brand profile, requirements (keyword) | `phase-6-seo.md` + `phase-6-structure-manifest.json` | **Gate 6:** keyword PLACEMENTS present — title, first 100 words, ≥2 H2s, conclusion, meta description (density is advisory, ~1–2%); meta title + description generated | Re-run Phase 6 |
| 6.5 | `contentforge:humanizer` | `phase-6-seo.md`, `phase-6-structure-manifest.json`, brand profile | `phase-6.5-humanized.md` | **Gate 6.5:** AI patterns removed; burstiness ≥0.7 (`text-metrics.py`); keyword placements preserved per structure manifest | Re-run Phase 6.5 with the violated constraint stated (incl. structure-manifest mismatch) |
| 7 | `contentforge:reviewer` | ALL prior artifact paths, brand profile, requirements, `config/scoring-thresholds.json` | `phase-7-review.json` | **Gate 7:** reviewer decision tree per `config/scoring-thresholds.json` — approve ≥7.0 (industry-adjusted); all dimension minimums met | 5.0–6.9 → loop to responsible phase (recorded as `pending_rework`); <5.0 → human review, halt |
| 8 | `contentforge:output-manager` | `phase-6.5-humanized.md`, `phase-7-review.json`, `phase-3.5-visual-manifest.json`, `run.json` | `phase-8-output.json` + `.docx` | **Gate 8:** .docx generated; Appendices A/B/C present; delivery location verified | Re-run Phase 8; if generation still fails, save markdown + reports locally and report the failure |

That is **10 quality gates** — one for each of phases 1, 2, 3, 3.5, 4, 5, 6, 6.5, 7, and 8.

**Single source of truth for numbers:** approval thresholds, loop bands, dimension weights, dimension minimums, and industry overrides live in `config/scoring-thresholds.json`. Prose in this document references those values; if they ever disagree, the config wins.

### Context & Handoff Rules

- Subagents receive artifact **paths**, a **≤10-line orchestrator summary**, the **brand-profile path** (phases 0.5, 3, 5, 6, 6.5, 7), and the **original-requirements block**. They `Read` what they need.
- Never inline a full draft into a Task prompt, and never reload a full draft into the orchestrator's context when a path reference will do.
- The reviewer (Phase 7) must receive the paths of **all** prior artifacts, not just the Phase 6.5 output.

### Final Output Requirements

After Phase 8 completes, the output-manager subagent **must produce a Microsoft Word `.docx` file** by calling:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/generate-docx.py \
    --content <article.md> \
    --output <local-path>.docx \
    --reports <reports.json> \
    --brand "<brand>" \
    --content-type <type>
```

The `.docx` must contain: title page, full article body, sources/citations, **Appendix A (SEO Scorecard)**, **Appendix B (Quality Scorecard)**, **Appendix C (Production Details)**.

**Dual-copy save:** the `.docx` is written into the run directory (`~/.claude-marketing/{brand-slug}/runs/{run_id}/`) AND copied to the user-visible folder `~/Documents/ContentForge/{Brand}/`. Always tell the user the `~/Documents/ContentForge/` path. If the brand has Google Drive configured (`tracking.backend == "google"`), additionally upload the .docx via `drive-uploader.py`.

Then finalize the run:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/checkpoint-manager.py finalize --brand <slug> --run-id "$RUN_ID" --status completed
```

### Why This Matters

Skipping the Task-tool orchestration means: no real fact-checking, no real humanizer (29-pattern AI removal won't fire), no real reviewer scoring — the pipeline becomes single-pass content generation labeled with fake phase names. The audit trail (`run.json`, the per-phase checkpoint artifacts, `[PHASE-AUDIT]` lines, real reviewer score) is the proof of execution. If those artifacts don't exist after a run, the pipeline didn't actually run.

## When to Use

Use `/contentforge` when you need:
- **Single high-quality content piece** (article, blog, whitepaper, FAQ, research paper)
- **Research-backed content** with verified citations
- **Brand-compliant content** for regulated industries (Pharma, BFSI, Healthcare, Legal)
- **SEO-optimized content** with keyword targeting and meta tags
- **Natural-sounding content** with AI patterns removed (Phase 6.5 Humanizer)

**For multiple pieces**, use [`/contentforge:batch-process`](../batch-process/SKILL.md) — a prioritized, checkpointed queue that runs the same pipeline per piece.

## What This Command Does

Runs your content through **10 specialized agents**, each behind a quality gate:

1. **Research Agent** — SERP analysis, source mining, competitive analysis, structured outline
2. **Fact Checker** — URL verification, claim validation, confidence scoring
3. **Content Drafter** — First draft with brand voice, SME calibration via industry knowledge packs
4. **Visual Asset Annotator** — Chart generation from verified stats, visual markers, asset manifest
5. **Scientific Validator** — Hallucination detection, domain-specific validation, logic validation
6. **Structurer & Proofreader** — Grammar/spelling correction, readability optimization, brand compliance
7. **SEO/GEO Optimizer** — Keyword placements, meta tag generation, internal linking markers
8. **Humanizer** — AI pattern removal, sentence variety (burstiness), brand personality
9. **Reviewer** — 5-dimension quality scoring (weights per `config/scoring-thresholds.json`)
10. **Output Manager** — .docx with embedded charts and internal links, dual-copy save, optional Drive upload

**Quality Gates:** 10 gates (phases 1–8 including 3.5 and 6.5). On failure the pipeline loops per the contract table — max 2 loops per edge, max 5 total, then human escalation.

## Required Inputs

**Minimum Required:**
- **Topic** — What the content is about (e.g., "AI in Healthcare", "remote work productivity")
- **Content Type** — article, blog, whitepaper, faq, research_paper
- **Brand** — Which brand profile to use (create with `/contentforge:cf-style-guide` if new brand). See No-Brand Mode below if none exists.

**Pre-Flight Validation:** After gathering inputs, validate the brand profile for completeness (voice, guardrails, audience, industry pack). For regulated industries (pharma, BFSI, healthcare, legal), guardrails are required — warn if they're empty and ask whether to proceed or update the profile first.

**Optional:**
- **Target Audience** — Who this content is for (e.g., "Healthcare CIOs")
- **Word Count** — Target length (defaults to content type standard)
- **Primary Keyword** — Main SEO keyword to optimize for
- **Tone** — Overrides brand default (authoritative, conversational, technical, witty)
- **`--sources=<urls or file>`** — User-supplied reference URLs (required in No-Web Mode; otherwise merged into Phase 1 research)
- **`--title="Exact Title"`** — Non-interactive title bypass (see Title Curation)

### No-Brand Mode

If the user has no brand profile and declines to create one:
- Proceed with generic defaults (neutral professional voice, no terminology enforcement).
- Phase 5 skips the brand-compliance sub-check.
- Phase 7 scores the **Brand Compliance dimension as `SKIPPED`** and flags the run for manual review; the Quality Scorecard notes "no brand profile configured."
- **Regulated-industry topics (pharma, BFSI, healthcare, legal) must NOT run in no-brand mode** — require a profile with guardrails first.

### No-Web Mode

If web research is unavailable (offline, no search tool, MCP down):
- Require user-supplied sources via `--sources=`.
- Skip SERP analysis; build the outline from the provided sources.
- Mark every citation **"user-provided, unverified"** in the fact-check ledger.
- Phase 7 **caps Citation Integrity at 6.0** and notes the cap in the scorecard.
- If neither web access nor user sources are available, stop and tell the user research is impossible — do not fabricate sources.

## How to Use

### Interactive Mode (Recommended for First-Time Users)
```
/contentforge
```
**Prompts you for:**
1. Topic (the subject — NOT the final title)
2. Content Type (select from 5 options)
3. Brand (select from existing profiles)
4. Target Audience
5. Word Count (or use default)
6. Primary Keyword

**Then generates 4-5 title options** (different angles: benefit-driven, how-to, data-driven, question-based, contrarian). You select, modify, or provide your own title. Pipeline starts only after title confirmation.

### Quick Mode (Topic Provided)
```
/contentforge "AI in Healthcare" --type=article --brand=acmemed --audience="Healthcare CIOs" --keyword="AI healthcare trends"
```
Even in quick mode, the system generates title options and asks you to select before starting Phase 1 — unless you pass `--title`.

### Non-Interactive Mode (evals, batch, CI)
```
/contentforge "AI in Healthcare" --type=article --brand=acmemed --title="How AI Is Reshaping Hospital Diagnostics"
```
`--title` skips option generation and uses the given title verbatim. The bypassed title is still checkpointed as `phase-0.5-title.txt`.

### Use Existing Google Sheet Requirement
```
/contentforge --sheet-url=https://docs.google.com/spreadsheets/d/ABC123 --row=5
```
Reads requirement from Row 5 of the sheet.

## What Happens

### Step 0.5: Title Curation — MANDATORY, inline

**Before the pipeline starts**, the orchestrator (inline — no subagent, no tracker calls) generates **4-5 SEO-optimized title options** using the topic, content type, brand voice, audience, and primary keyword. Each title takes a different angle:
- **Benefit-driven** — leads with reader value
- **How-to / Tactical** — actionable, instructional
- **Data-driven / Stat-led** — opens with a number or trend
- **Question-based / Curiosity** — provokes the reader
- **Contrarian / Unexpected** — challenges convention

**You select, modify, or provide your own title.** The confirmed title becomes the anchor for the entire pipeline — research, outline, SEO, and final output all flow from it.

**Do NOT auto-select a title.** The only exception is an explicit `--title="..."` bypass, which uses the supplied title verbatim (for non-interactive runs and evals). Either way, checkpoint the confirmed title as `phase-0.5-title.txt` before Phase 1.

### Phases 1–8 at a glance

Gate criteria and loop targets for every phase are defined once, in the **Pipeline Contract table** above.

- **Phase 1: Research** — SERP analysis anchored on the confirmed title; mines 12–15 authoritative sources; competitor analysis; structured outline. *Gate 1.*
- **Phase 2: Fact Checking** — verifies all URLs are live, validates claims against sources, assigns confidence tiers, flags unverifiable claims for removal or re-sourcing. *Gate 2.*
- **Phase 3: Content Drafting** — first draft in brand voice with inline citations (APA format), targeting word count ±10%. *Gate 3.*
- **Phase 3.5: Visual Assets** — charts from verified stats, visual markers, asset manifest with placement, alt text, and data source. *Gate 3.5.*
- **Phase 4: Scientific Validation** — hallucination scan, claim traceability, logic validation. *Gate 4; failures loop to Phase 3.*
- **Phase 5: Structure & Proofread** — grammar/spelling, readability to the content-type target (±0.5 grade), brand terminology and style. *Gate 5.*
- **Phase 6: SEO/GEO** — keyword placements (title, first 100 words, ≥2 H2s, conclusion, meta description), meta tags, URL slug, AI-answer-engine readiness, structure manifest. Density is advisory (~1–2%), not a gate. *Gate 6.*
- **Phase 6.5: Humanizer** — 29-pattern AI-telltale removal, burstiness ≥0.7, brand personality, SEO-placement preservation validated against the structure manifest. *Gate 6.5.*
- **Phase 7: Reviewer** — 5-dimension weighted scoring per `config/scoring-thresholds.json`; approve ≥7.0 (industry-adjusted), loop 5.0–6.9, human review <5.0. *Gate 7.*
- **Phase 8: Output** — .docx generation with appendices, dual-copy save, optional Drive upload, tracking update. *Gate 8.*

**If a phase loops back:** the system shows which phase failed, why, and what it's fixing. Loops are automatic — you don't need to do anything unless it escalates to human review.

## Output Example

Every pipeline run ends with a **Completion Card** showing scores, stats, and delivery status. This card is mandatory — it's shown in the conversation AND added as an appendix in the .docx file.

**Example Completion Card** (SYNTHETIC EXAMPLE — fabricated for illustration; never reuse these numbers):
```
CONTENTFORGE — COMPLETION CARD

Content:  "AI in Healthcare: Emerging Trends" | AcmeMed | Article | ✅ APPROVED

Quality Score: 9.2/10 (Grade A+)
  Content Quality:    9.5/10 ✅
  Citation Integrity: 9.0/10 ✅
  Brand Compliance:   9.5/10 ✅
  SEO Performance:    8.8/10 ✅
  Readability:        9.0/10 ✅

Content Stats:
  Words: 1,947 (target 1,500-2,000) ✅ | Citations: 14 sources ✅
  Keyword placements: all critical positions ✅ | Readability: Grade 11.2 ✅
  Burstiness: 0.78 ✅ | AI Patterns: 0 remaining ✅ | Hallucinations: 0 ✅

SEO Package:
  Meta Title: 58 chars ✅ | Meta Description: 152 chars ✅
  Internal Links: 4 applied | Feature Image: generated (user-approved)

Pipeline: 0 loops | Guardrails: verified | Run: {run_id}

Delivery:
  .docx: ✅ Generated
  Local: ✅ ~/Documents/ContentForge/AcmeMed/AI-in-Healthcare-Emerging-Trends_v1.0.docx
  Drive: ✅ uploaded (if configured) | Tracking: ✅ updated

Next: /contentforge:publish | /contentforge:social-adapt | /contentforge:translate | /contentforge:cf-variants
```

## Content Types & Specifications

| Type | Word Count | Readability | Citations |
|------|-----------|-------------|-----------|
| **Article** | 1,500-2,000 | Grade 10-12 | 8-12 |
| **Blog** | 800-1,500 | Grade 8-10 | 5-8 |
| **Whitepaper** | 2,500-5,000 | Grade 12-14 | 15-25 |
| **FAQ** | 600-1,200 | Grade 8-10 | 3-5 |
| **Research Paper** | 4,000-8,000 | Grade 14-16 | 25-50 |

Readability is gated at ±0.5 grade of the content-type target (verified via `text-metrics.py`).

## Brand Profile Setup

**Before using ContentForge**, create a brand profile:

```
/contentforge:cf-style-guide
```

Provide your brand name, industry, voice guidelines (or share existing documents/URLs), and ContentForge generates the profile JSON automatically.

**Alternatively**, copy `config/brand-registry-template.json` and fill in manually.

**Canonical profile location:** `~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json`, where the brand slug is lowercase alphanumerics + hyphens. Resolution order: local file first, then Drive cache (Cowork).

**Brand Profile Includes:**
- Voice & Tone (authoritative, conversational, technical, witty)
- Terminology (approved terms, banned phrases)
- Style Guide (formatting preferences, citation style)
- Guardrails (topics to avoid, compliance requirements)
- Industry Context (Pharma, BFSI, Healthcare, Legal)
- Personality Profile (authoritative, conversational, technical, witty)

**Brand profiles are cached** (SHA256 hash) so repeat runs skip re-parsing.

See the [User Guide](../../docs/USER-GUIDE.md#4-setting-up-your-brand-profile) for detailed setup instructions.

## Quality Assurance

### Three-Layer Fact Verification
1. **Phase 2 (Fact Checker):** URL verification, claim validation
2. **Phase 4 (Scientific Validator):** Hallucination detection
3. **Phase 7 (Reviewer):** Final citation integrity scoring

### Feedback Loop Management
- **Max 2 loops per edge** (e.g., Phase 4 → Phase 3, or Phase 7 → Phase X)
- **Max 5 loops total per run** before human escalation
- Loop counts are recorded in `run.json` via `checkpoint-manager.py loop` and survive resume.

### Human Review Escalation
Content is flagged for human review if:
- Quality score <5.0/10 (per `config/scoring-thresholds.json`)
- Critical brand violations detected
- Loop limits reached without passing
- User explicitly requests review
- Run executed in No-Brand Mode (Brand Compliance = SKIPPED)

**Flagged content is NEVER auto-published.**

## Integration with Other Skills

**Before ContentForge:**
- `/contentforge:cf-style-guide` — Create brand profile if new brand
- `/contentforge:content-brief` — Generate research-backed content brief with keyword analysis

**Instead of ContentForge (for scale):**
- `/contentforge:batch-process` — Queue 10-50+ pieces through the same pipeline

**After ContentForge:**
- `/contentforge:content-refresh` — Update content 6-12 months later with fresh data
- `/contentforge:cf-variants` — Create A/B test headline/hook/CTA variations
- `/contentforge:publish` — Publish to Webflow or WordPress via MCP
- `/contentforge:social-adapt` — Transform article into LinkedIn, Twitter/X, Instagram, Facebook, Threads posts
- `/contentforge:translate` — Translate preserving brand voice (15+ languages)
- `/contentforge:cf-video-script` — Generate timestamped video scripts from the article
- `/contentforge:cf-analytics` — Record quality scores for trend tracking

## Requirements

### MCP Integrations (Optional)
- **Google Sheets** — Requirement intake for batch processing, quality tracking
- **Google Drive** — Brand knowledge vault, output .docx storage
- **Webflow/WordPress** — Direct CMS publishing via `/contentforge:publish`

Run `/contentforge:cf-integrations` to check your connector status. Run `/contentforge:cf-connect <name>` for setup guides.

### Environment
- Claude Code or Cowork (latest version)
- Internet connection for Phase 1 web research — or `--sources=` in No-Web Mode

## Troubleshooting

### "Brand profile not found"

**When:** You run `/contentforge` with a brand that doesn't have a profile yet.

**Fix:**
1. **Create a brand profile (recommended):**
   ```
   /contentforge:cf-style-guide
   ```
   Answer 3 questions (name, tone, industry) and you're ready.
2. **Or specify a different brand:**
   ```
   /contentforge "your topic" --brand=existing-brand
   ```
3. **Or proceed in No-Brand Mode** (non-regulated topics only — see Required Inputs).

### "Quality score <5.0, flagged for review"

**When:** Content didn't meet the minimum quality threshold after all feedback loops.

**Common causes and fixes:**
- **Topic too vague** → Be more specific: "AI in healthcare" → "AI diagnostic tools for rural hospitals"
- **Sources behind paywalls** → Provide accessible reference URLs with `--sources=`
- **Brand profile incomplete** → Run `/contentforge:cf-style-guide --update [brand]` to add guardrails and terminology
- **Niche topic with few sources** → Consider a broader angle or provide your own source URLs

### "Max loops exceeded"

**When:** The pipeline hit a loop limit (2 per edge or 5 total) without reaching the quality threshold.

**Fix:**
1. Check which dimension scored lowest in `phase-7-review.json` (Content Quality? Citations? Brand Compliance?)
2. If **Content Quality** is low → topic needs more depth or the angle is too broad
3. If **Citation Integrity** is low → sources are weak or behind paywalls
4. If **Brand Compliance** is low → brand profile may be incomplete
5. Re-run with adjustments: more specific topic, better keywords, or updated brand profile

### "Pipeline appears stalled"

API rate limits or network latency cause delays; ContentForge auto-retries with backoff. If it persists:
1. Check internet connection
2. Run `/contentforge:cf-integrations` to verify MCP servers are responding
3. If the session died, run `/contentforge:resume` — every gate-passed phase is checkpointed
4. Long content types (whitepaper, research paper) legitimately take much longer than blogs

### "Guardrails empty — compliance skipped"

**When:** Your brand profile doesn't have prohibited claims or required disclaimers defined.

**Impact:** Phase 5 reports brand compliance "SKIPPED" instead of actually checking content. Phase 7 applies the empty-guardrails penalty per `config/scoring-thresholds.json`.

**Fix:**
```
/contentforge:cf-style-guide --update [brand]
```
Add at minimum: 3-5 prohibited claims, any required legal disclaimers, and industry-specific restrictions.

**For regulated industries (pharma, BFSI, healthcare, legal):** This is critical. Empty guardrails mean no compliance verification.

### Pipeline phase explanations

During content production, you'll see updates as each phase completes:

| Phase | What's Happening | What You'll See |
|-------|-----------------|----------------|
| Step 0.5: Title Curation | Generating 4-5 title options | Title options with character counts |
| Phase 1: Research | SERP analysis, source mining, outline | Source count, outline sections |
| Phase 2: Fact Check | URL verification, claim validation | Verified %, flagged claims |
| Phase 3: Draft | First draft with brand voice | Word count, citation density |
| Phase 3.5: Visuals | Charts, image generation (if opted in) | Visual count, chart specs |
| Phase 4: Validation | Hallucination detection | Zero hallucinations confirmed |
| Phase 5: Structure | Grammar, readability, brand compliance | Compliance status |
| Phase 6: SEO | Keyword placements, meta tags | Placement checklist, GEO score |
| Phase 6.5: Humanize | AI pattern removal, personality | Burstiness score |
| Phase 7: Review | 5-dimension quality scoring | Score breakdown, pass/fail |
| Phase 8: Output | .docx generation, tracking, delivery | Output location, final metrics |

## Example Workflow

(SYNTHETIC EXAMPLE — fabricated for illustration; never reuse these numbers.)

**Scenario:** Create 1 thought leadership article for the AcmeMed brand

### Step 1: Create Brand Profile (One-Time Setup)
```
/contentforge:cf-style-guide
```
Provide: Brand name (AcmeMed), Industry (Healthcare), Voice (Authoritative), Tone (Professional), Terminology, Guardrails

### Step 2: Start Content Production
```
/contentforge "AI-Powered Diagnostics in Precision Medicine" --type=article --brand=acmemed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine"
```

### Step 3: Select Title
ContentForge generates 4-5 title options:
1. "AI-Powered Diagnostics: The Future of Precision Medicine"
2. "How AI Diagnostics Are Transforming Precision Medicine for Healthcare Leaders"
3. "5 AI Diagnostic Breakthroughs Reshaping Precision Medicine Right Now"
4. "The Executive's Guide to AI-Powered Precision Medicine Diagnostics"
5. "Why AI Diagnostics in Precision Medicine Are Finally Delivering on the Promise"

You select Option 1 → Pipeline starts with that title as the anchor.

### Step 4: Review Output
- Quality Score: 9.1/10 ✅
- Word Count: 1,922 ✅
- Citations: 12 sources ✅
- SEO: all keyword placements hit ✅

### Step 5: Publish
```
/contentforge:publish --platform=webflow
```

## Limitations

- **Sequential phases** — the pipeline is strictly ordered; each gate consumes the previous phase's artifact
- **Depth takes time** — the pipeline cannot be rushed without compromising quality (use `--title` and `--sources` to shave the interactive steps)
- **Best with brand profile** — No-Brand Mode works but the Brand Compliance dimension is SKIPPED and the run is flagged for manual review

## Related Skills

- **[/contentforge:batch-process](../batch-process/SKILL.md)** — Queue 10-50+ pieces through the same pipeline
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** — Update old content with fresh data
- **[/contentforge:cf-variants](../cf-variants/SKILL.md)** — A/B test headline/hook/CTA variations
- **[/contentforge:cf-analytics](../cf-analytics/SKILL.md)** — Track quality scores and performance
- **[/contentforge:social-adapt](../cf-social-adapt/SKILL.md)** — Transform article into social media posts
- **[/contentforge:publish](../cf-publish/SKILL.md)** — Publish to Webflow/WordPress
- **[/contentforge:translate](../cf-translate/SKILL.md)** — Translate preserving brand voice
- **[/contentforge:content-brief](../cf-brief/SKILL.md)** — Generate research-backed content briefs

---

<!-- Version, agent count, and asset counts are pulled live by /contentforge:cf-help
     from scripts/plugin-metadata.py. Do not bake version strings into skill
     bodies -- they drift out of sync every release. The canonical source of
     truth is .claude-plugin/plugin.json + the agents/ + skills/ directories. -->

**Pipeline:** 10 phases plus Step 0.5 (Title Curation); 10 quality gates. Phase
agents are defined in `agents/*.md` and enumerated by `scripts/plugin-metadata.py
--section pipeline`. Post-pipeline agents include Batch Orchestrator, Social
Adapter, and Translator.

**Quality target:** composite Reviewer score ≥7.0 to pass (industry-adjusted per
`config/scoring-thresholds.json`); max 2 loops per edge, 5 total; three-layer
verification (Fact Checker → Scientific Validator → Reviewer).
