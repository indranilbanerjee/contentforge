# contentforge (orchestrator) — Troubleshooting

Verbatim troubleshooting prose moved out of `skills/contentforge/SKILL.md` to keep the orchestrator skill body within the ~500-line Agent Skills guidance. Covers brand-profile, quality-score, loop-limit, stalled-pipeline, and empty-guardrail failure modes, plus the per-phase "what you'll see" reference table.

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
