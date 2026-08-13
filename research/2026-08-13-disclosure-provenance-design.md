# Design: AI-Assistance Disclosure + Two-Tier AI-Tell Review Sheet

**Date:** 2026-08-13 · **Target:** ContentForge v3.22.0 · **Status:** approved direction, this doc is the committed spec.

## Why

Anthropic began embedding statistical watermarks in Claude text output (models
launched ≥ 2026-08-02, all surfaces, no opt-out; a mark proves *processed by*
Claude, not *authored by*). Separately, the StoryScope paper (arXiv 2604.03136)
showed AI text is detectable on **narrative structure** at 93.2% F1 — and that
surface-style editing (what our 41-pattern humanizer does) barely dents
structural detection (−1.6 points). Decisions taken with the user:

1. **No watermark removal or evasion features — ever.** The plugin's posture is
   honest disclosure + genuinely human-shaped quality. The humanizer is a
   quality tool and will not be marketed or extended as a watermark tool.
2. **Disclosure layer** (Component A): author-OPTIONAL, vendor-neutral,
   brand-configurable, default-gated to Claude surfaces per user decision.
3. **Two-tier review sheet** (Component B): surface tells (existing Tier 1)
   + new structural tells (Tier 2, from StoryScope, adapted to non-fiction),
   highlighted for the human reviewer. Advisory, never a gate. All surfaces.
4. CF first; DMP/SF mirror in a later pass.

## Component A — AI-Assistance Disclosure

**Brand config** (brand-profile JSON, set up via `/contentforge:cf-style-guide`):

```json
"ai_disclosure": {
  "mode": "claude-surfaces",     // "claude-surfaces" (default) | "always" | "off"
  "text": null,                   // null => default text below
  "author": null                  // optional; when set, also feeds the E-E-A-T byline
}
```

Default text (no author): `Created with AI assistance and reviewed by our
editorial team.` With author: `Created with AI assistance; researched,
fact-checked, and edited by {author}.`

**Invariants (guard-tested):**
- Default text contains NO vendor or model names (hard rule + keeps the wording
  valid on every surface). Brands may name models in custom text — their words.
- Claims stay true: default wording claims only review, which CF's mandatory
  Phase-7 + human approval actually performs.
- Author absent → clean nameless rendering, nothing breaks.

**Surface gate** — `scripts/detect_surface.py`:
- Reuses `classify_environment` (plugin-metadata.py) for Cowork/sandbox.
- Affirmative Claude signals: `CLAUDECODE`, `CLAUDE_CODE_*` env,
  `ANTHROPIC_COWORK_SESSION_ID`, cowork-sandbox classification.
- Affirmative non-Claude signals (best-effort): Codex / Copilot / Cursor /
  Antigravity env fingerprints.
- Output: `{"surface": "claude"|"non-claude"|"uncertain", "basis": [...]}`.
- **Fail-safe: `uncertain` ⇒ disclosure applies** (over-disclosure is
  harmless; under-disclosure is the compliance risk).
- Mode semantics: `always` ⇒ apply; `off` ⇒ never; `claude-surfaces` ⇒ apply
  unless a NON-Claude surface is affirmatively detected.

**Application point:** Phase 8 output manager appends the disclosure as a
delimited content block INSIDE the deliverable body (so it survives
`/contentforge:publish` to Webflow/WordPress and the .docx export).
`run.json` records `{"disclosure": {"applied": bool, "mode": ..., "surface": ...}}`.

## Component B — Two-Tier AI-Tell Review Sheet

**Tier 1 (exists):** `text-metrics.py --ai-tell-scan` — banned lexemes,
aphorisms, em-dash rate, connective/participial openers, uniform runs; extend
`flagged_sentences` coverage so more tells carry sentence spans.

**Tier 2 (new):** `text-metrics.py --structure-scan` — deterministic proxies
for StoryScope's structural findings, adapted to non-fiction:

| Structural tell | Deterministic proxy |
|---|---|
| Over-explanation / moralizing | conclusion-marker + moralizing-phrase density per 1000 words ("in conclusion", "ultimately", "the key takeaway", "it's important to remember", "this matters because", ...) |
| Template symmetry | coefficient of variation of H2-section word counts (too-uniform = template); parallel-heading-syntax share |
| Specificity density | numbers + proper-noun tokens + quoted strings + citation markers per 1000 words (low = generic-center) |
| Stance absence | hedging-word density ("may", "can", "often", "typically", ...) vs first-person/stance markers |
| Structural evenness | paragraph-length coefficient of variation (Claude-fingerprint "uniform voice" proxy) |

Output: per-metric value + advisory band (OK / NOTE / ATTENTION) + the spans
(section names / sentence indices) that drove each flag. **Thresholds are
advisory constants in the script, never wired into scoring-thresholds gates.**

**Review sheet:** `scripts/build_review_sheet.py --draft X.md --brand B --out
phase-6.5-review-sheet.html` runs both scans and renders a self-contained HTML:
draft text with Tier-1 sentence highlights + Tier-2 structural callouts per
section, each with the pattern name and a suggested *human* edit direction.
Deliberately mirrors SF's review-gallery pattern (esc() everything).

**Pipeline wiring:** humanizer (6.5) emits the sheet next to the humanized
draft; reviewer (7) references it on the Completion Card ("N surface spans,
M structural notes — review sheet: <path>"); in `--skip-humanizer` express
runs the reviewer generates it from the latest artifact so it always exists.
Advisory, never a publish gate (consistent with the existing ai-tell rule).

**What it is NOT (stated in the sheet header + docs):** it detects visible
stylistic/structural patterns; it cannot see and has no relationship to any
statistical watermark.

## Tests (tests/test_disclosure_layer.py + tests/test_structural_tells.py)

1. Disclosure matrix: mode × surface (claude/non-claude/uncertain) → applied?
   — incl. the uncertain⇒apply fail-safe pin.
2. Default-text guards: no vendor/model names; author-optional rendering.
3. detect_surface: CLAUDECODE env ⇒ claude; cowork signals ⇒ claude; forced
   non-Claude fingerprint ⇒ non-claude; empty ⇒ uncertain.
4. Structural fixtures: planted AI-shaped text (uniform sections, moralizing
   closers, zero specifics) fires ATTENTION; human-shaped fixture (varied
   sections, specifics, stance) stays OK. Plant-check both directions.
5. Advisory-not-gate: structure-scan keys absent from scoring-thresholds.json;
   orchestrator/agent contracts contain the "advisory" language.
6. Review sheet: builds, escapes hostile draft content, contains both tiers.
7. Doc pins: humanizer emits sheet; reviewer surfaces it; output-manager
   applies disclosure per run.json contract.

## Out of scope (explicit)

- DMP / SocialForge mirroring (later pass, same pattern).
- JSON-LD machine-readable disclosure (future; visible block first).
- Any watermark detection/removal (permanently out).
