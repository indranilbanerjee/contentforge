# ContentForge Quality Contract

What ContentForge guarantees before a piece is delivered, and what it does not.

Every number below is read from the plugin's own configuration, not from marketing copy: `config/pipeline-graph.json` (phases, gates, loop budgets), `config/scoring-thresholds.json` (thresholds, weights, minimums), `config/humanization-patterns.json` (the humanizer catalog), and `scripts/run-audit.py` (the run auditor). A test (`tests/test_quality_contract.py`) parses this file and fails the build if any number here disagrees with those files, so this document cannot quietly go stale. Where the two ever disagree, the config wins.

## The promise

> ContentForge does not call a piece finished until every phase that ran has passed an orchestrator-checked gate against thresholds kept in version-controlled config, a reviewer has scored it at or above the approve line (7.0 by default, higher for regulated industries) with no dimension below its minimum, and a script has re-derived the run's claims from the files on disk. Anything that falls short is recorded as blocked, draft or not-checked. It never passes silently.

Read the promise as three layers, because they are not equally strong:

1. **Gates**: each of the 10 numbered phases has a gate. The orchestrator verifies it against the artifact, and a subagent's own "PASS" is never accepted as a gate pass.
2. **Score**: a reviewer rates the finished piece on five weighted dimensions. This is a rubric judgment, not a measurement.
3. **Audit**: `run-audit.py` re-derives what the run says about itself from the files on disk. `checkpoint-manager.py finalize --status completed` refuses unless that audit exists, its verdict is `CLEAN`, and none of the files it read has changed since.

## How each guarantee is enforced

Every row in the gate table below carries one or more of these tags.

| Tag | Meaning | How strong |
|---|---|---|
| script | A deterministic stdlib script computes the answer (`text-metrics.py`, `fix-ledger.py`, `authorship.py`, `generate-docx.py`, `run-audit.py`). Same input, same verdict. | Strongest. Reproducible by you. |
| orchestrator | The orchestrator counts or inspects the returned artifact against the criterion before checkpointing it. | Strong where the criterion is a count, weaker where it needs reading. |
| agent judgment | A specialist agent evaluates against a written rubric (fact-checking, hallucination diffing, scoring). | Real work, but a judgment. Not reproducible to the decimal. |

## The numbers at a glance

| Contract term | Value | Where it lives |
|---|---|---|
| Approve line (default) | 7.0 | `scoring-thresholds.json` → `default.minimum_pass_score` |
| Human-review line | 5.0 | `scoring-thresholds.json` → `default.human_review_threshold` |
| Numbered quality gates | 10 | `pipeline-graph.json` → every node whose gate reads "Gate N" |
| Loop budget per edge | 2 | `pipeline-graph.json` → `loop_budgets.per_edge` |
| Loop budget per run | 5 | `pipeline-graph.json` → `loop_budgets.total_per_run` |
| Humanizer catalog patterns | 43 | `humanization-patterns.json` → `signs_of_ai_writing_catalog` |
| Core patterns | 29 | catalog buckets: content, language and grammar, style, communication, filler and hedging |
| Structure and framing patterns | 6 | catalog bucket `structure_and_framing_patterns` |
| Detector-signal patterns | 8 | catalog bucket `detector_signal_patterns` |
| High-signal patterns (weight x2) | 7 | `humanization-patterns.json` → `ai_signal_scoring.weights.high_signal_x2` |
| Weighted checks in the signal score | 50 | 7 high-signal patterns counted twice plus the other 36 once |
| Remaining-AI-signal ceiling | 0.3 | `scoring-thresholds.json` → `default.quality_gates.phase_6_5_humanizer.max_ai_signal_score` |

## The 10 gates, in order

Step 0.5 (title curation) comes first, but it is a user checkpoint, not a numbered quality gate: you confirm the title, or pass `--title` to bypass it. Gates then run in this order. A gate that fails sends the run to the loop target in the "On failure" column, inside the budget described under "Loop budgets".

| Gate | Phase | What it checks | On failure | Enforced by |
|---|---|---|---|---|
| 1 | Research | 12–15 candidate sources collected; at least 10 verified live and citable, at least 5 of them with reliability 8 or higher; top 5 competitors analysed; a differentiated angle and an outline; Client Site Reconnaissance complete, with at least 3 verified deep brand URLs when the brand has a website. | Re-run Phase 1 with a broader search. | orchestrator (counts), agent judgment |
| 2 | Fact Check | At least 80% of claims verified; zero unresolved flags (a flagged claim is removed or re-sourced inside the phase, never carried forward); at most 3 unverified claims tolerated, each hedged or attributed in the draft; every cited URL live; sources inside the age window (2 years by default, tighter for pharma); a key statistic needs a second independent source. | Loop to Phase 1 for alternative sources. There is no conditional pass with open flags. | agent judgment (web verification), orchestrator |
| 3 | Content Draft | `body_word_count` within ±10% of the target (the counting convention is stated in the orchestrator skill, so the number is a measurement, not a reading); every outline section present; at least 1 citation per 300 words. | Re-run Phase 3. | script (`text-metrics.py`), orchestrator |
| 3.5 | Visual Assets | Every chart traceable to a verified statistic (a chart on unverified data is rejected); manifest complete (placement, alt text, data source); alt text and captions present; visual density at or above the per-type minimum; human-action items marked. | Re-run Phase 3.5. | orchestrator (manifest inspection), agent judgment |
| 4 | Scientific Validation | Zero hallucinations and zero unsourced claims (every factual claim in the draft is diffed against the Phase 2 ledger; this phase does not fetch the web again); accuracy confidence at least 0.85; logic consistent; `fix-ledger.py validate --target` exits 0 and every correction the report names is in the fix ledger. | Loop to Phase 3 with the exact claims to fix (Phase 3.5 for a visual-data mismatch). | agent judgment, script (`fix-ledger.py`) |
| 5 | Structure & Proofread | `fix-ledger.py verify` reports zero unresolved blocking items (hard); zero grammar and spelling errors on re-scan; readability within ±0.5 grade of the content-type target and a Flesch Reading Ease of 60–80 (30–50 for whitepapers and research papers); brand terminology and guardrail scan with zero unresolved violations; VISUAL anchors preserved. | Re-run Phase 5. | script (`fix-ledger.py`, `text-metrics.py`), agent judgment |
| 6 | SEO / GEO | Keyword placements: title, first 100 words, at least 2 H2s, conclusion, meta description; meta title up to 60 characters and meta description up to 155; structure manifest emitted; readability not degraded; every internal-link URL live (hard: one dead link fails the gate); at least 2 deep brand links when the site is known (a flagged deficiency, not a hard stop). | Re-run Phase 6. | script (`text-metrics.py`), orchestrator |
| 6.5 | Humanizer | Grounding pass complete; the full 43-pattern catalog walked with none remaining; GEO structure and SEO keywords preserved; remaining-AI-signal score at most 0.3; brand personality integrated; with an author draft, zero author sentences rewritten or dropped (hard); `fix-ledger.py verify` must not exit 3, so a style pass cannot undo an applied correction (hard); AI-tell scan reported (advisory). | Re-run Phase 6.5 with the violated constraint stated. | script (`authorship.py`, `fix-ledger.py`), agent judgment |
| 7 | Reviewer | Five weighted dimensions scored; composite at or above the approve line (7.0 by default) and every dimension at or above its minimum; a dead internal link is a hard fail; `fix_ledger` is copied from the script output, never re-derived by hand; `publication_status` recorded. | Score 5.0–6.9 loops to the responsible phase; below 5.0 stops for human review. | agent judgment (rubric), script (`fix-ledger.py`) |
| 8 | Output Manager | `.docx` produced by script with all 4 appendices (A SEO Scorecard, B Quality Scorecard, C Production Details, D Internal Link Map); no production scaffolding in the body; every generated asset anchored and only user-approved assets embedded; delivery verified; `fix-ledger.py verify` sets `publication_status`, and a blocked piece is delivered as a `DRAFT-` file. | Re-run Phase 8; if generation still fails, save markdown and reports locally and report the failure. | script (`generate-docx.py`, `text-metrics.py`, `fix-ledger.py`) |

Gates 2, 4 and 7 are identical in the express lane and the full pipeline. Express skips Phase 3.5 and Phase 6 by default and runs Phase 5 and Phase 6.5 unless you opt out; every skipped phase is recorded in `run.json` (`mode`, `skipped_phases`), and the reviewer then scores those qualities from the piece itself.

### Three layers of fact verification

| Layer | Phase | What it can do | What it cannot do |
|---|---|---|---|
| Fact Checker | 2 | Fetches every source URL, matches each statistic to its source text, looks for a second independent source, checks publication dates. A paywalled source stays unverified unless an open source corroborates it. | It can only verify what its tools can reach. |
| Scientific Validator | 4 | Diffs every factual claim in the draft against the Phase 2 ledger and flags what is not there. | It does not re-fetch sources, so a claim Phase 2 verified wrongly is checked against that same ledger. |
| Reviewer | 7 | Spot-checks 10–15 claims against verified sources and scores Citation Integrity. | A spot-check, not a re-verification of every claim. |

## The approve line and the five dimensions

The reviewer scores five dimensions from 1 to 10 and combines them with fixed weights. The default approve line is 7.0.

| Dimension | Weight | Minimum score | Gate 7 failure loops back to |
|---|---|---|---|
| Content quality | 0.30 | 6.0 | Phase 3 |
| Citation integrity | 0.25 | 7.0 | Phase 2 or Phase 4 |
| Brand compliance | 0.20 | 7.0 | Phase 5 |
| SEO performance | 0.15 | 6.0 | Phase 6 |
| Readability | 0.10 | 6.0 | Phase 5 or Phase 6.5 |

Decision bands: a composite at or above the approve line is **approved**; 5.0 up to the approve line **loops** back to the weakest dimension's phase; below 5.0 is **human review**, and the output manager delivers a `DRAFT-` file marked Pending Human Review. A dimension below its minimum fails Gate 7 whatever the composite says. A piece can be approved on score and still blocked on publication status: the score says the writing is good enough, `publication_status` says whether it is finished.

Regulated industries use a higher approve line, their own weights and, in some cases, raised dimension minimums. An industry override replaces the default weights entirely; the weights are never blended.

| Industry | Approve line | Weights: content / citation / brand / SEO / readability | Raised minimums |
|---|---|---|---|
| Default (all other industries) | 7.0 | 0.30 / 0.25 / 0.20 / 0.15 / 0.10 | — |
| Pharma | 8.0 | 0.25 / 0.35 / 0.25 / 0.10 / 0.05 | citation 8.5, brand 8.0 |
| BFSI | 7.5 | 0.25 / 0.25 / 0.30 / 0.15 / 0.05 | citation 7.5, brand 8.0 |
| Healthcare | 8.0 | 0.25 / 0.35 / 0.25 / 0.10 / 0.05 | — |
| Legal | 8.0 | 0.30 / 0.30 / 0.30 / 0.05 / 0.05 | — |
| Real estate | 7.0 | 0.30 / 0.15 / 0.20 / 0.25 / 0.10 | — |

The reviewer applies one resolution rule, read from config at run time: start from the default, apply the content-type override if there is one, then the industry override, and let each later layer replace whatever it defines. That yields the approve line, the weights and the dimension minimums together, so an industry's raised minimums bind exactly as its raised approve line does. The reviewer records what it resolved (`industry`, `minimum_pass_score_applied`, `weights_applied`) and the run auditor re-resolves the same policy from config, taking the industry from the review and, independently, from the brand profile. It applies the stricter of the two and fails a review that recorded a laxer industry than the profile's: a reviewer cannot move a pharma piece to the default line by writing a different word. Pharma also tightens Gates 1 and 2 (more verified sources, a higher verified-claim percentage, a shorter source-age window), and the fact-checker is instructed to apply industry overrides. The config states that a brand may tighten these defaults and never loosen them.

Content is also sent to human review, and is never delivered as finished, when a critical brand violation is found, when loop budgets run out below the approve line, or when the run used No-Brand Mode (Brand Compliance is then scored `SKIPPED` and the run is flagged for manual review). Regulated-industry topics must not run without a brand profile that has guardrails.

## Loop budgets

A failing gate sends the run back to an earlier phase: at most 2 loops per edge and 5 loops per run. Every loop is recorded in `run.json` with its reason.

| Loop edge | Budget | Config key |
|---|---|---|
| Any single edge (default) | 2 | `graph:loop_budgets.per_edge` |
| Whole run, all edges together | 5 | `graph:loop_budgets.total_per_run` |
| Phase 4 → Phase 3 | 2 | `default.feedback_loop_limits.phase_4_to_3` |
| Phase 4 → Phase 3.5 (visual-data mismatch) | 1 | `default.feedback_loop_limits.phase_4_to_3_5` |
| Phase 6 → Phase 5 | 1 | `default.feedback_loop_limits.phase_6_to_5` |
| Phase 7 → any phase | 2 | `default.feedback_loop_limits.phase_7_to_any` |
| Total across all phases | 5 | `default.feedback_loop_limits.max_total_loops` |
| Phase 4 validation re-runs | 2 | `default.quality_gates.phase_4_validation.max_validation_loops` |
| Phase 6 SEO re-runs | 1 | `default.quality_gates.phase_6_seo.max_seo_loops` |

When a budget is spent the run does not loop again: it is marked for human review and finalised as failed. Where the generic edge budget and a named cap differ, the smaller cap governs. `scoring-thresholds.json` states that rule once, in its notes (`default.feedback_loop_limits._precedence`), and the auditor applies it: a named edge cap bounds that edge; the Phase 7 cap bounds the sum of every edge leaving Phase 7; the validation and SEO caps bound the sum of the edges leaving Phase 4 and Phase 6; the per-run budget is the smaller of the graph's and the config's.

How this is enforced: the budgets are an orchestrator and agent protocol, and `checkpoint-manager.py loop` records each traversal with its reason without refusing it. The run auditor then holds the recorded counts to those caps, so a run that blew a budget fails the audit and cannot be finalised as completed. The audit catches it after the fact; nothing stops the loop while it happens.

## Key thresholds, exactly

Each row names the config key it was read from. The test resolves every key and compares the value.

| Gate | Threshold | Value | Config key |
|---|---|---|---|
| 1 | Candidate sources collected | 12-15 | `default.quality_gates.phase_1_research.sources_collected` |
| 1 | Verified sources (minimum) | 10 | `default.quality_gates.phase_1_research.min_verified_sources` |
| 1 | High-reliability sources (minimum) | 5 | `default.quality_gates.phase_1_research.min_high_reliability` |
| 1 | Competitor analyses (minimum) | 5 | `default.quality_gates.phase_1_research.min_competitor_analysis` |
| 2 | Claims verified (minimum %) | 80 | `default.quality_gates.phase_2_fact_check.min_verified_percentage` |
| 2 | Unresolved flags allowed | 0 | `default.quality_gates.phase_2_fact_check.max_unresolved_flags` |
| 2 | Unverified claims tolerated | 3 | `default.quality_gates.phase_2_fact_check.max_unverified_tolerated` |
| 2 | Source age window (years) | 2 | `default.quality_gates.phase_2_fact_check.max_source_age_years` |
| 3 | Word-count tolerance (%) | 10 | `default.quality_gates.phase_3_draft.word_count_tolerance_percent` |
| 3 | Citations per 300 words (minimum) | 1 | `default.quality_gates.phase_3_draft.min_citations_per_300_words` |
| 4 | Hallucinations allowed | 0 | `default.quality_gates.phase_4_validation.max_hallucinations` |
| 4 | Unsourced claims allowed | 0 | `default.quality_gates.phase_4_validation.max_unsourced_claims` |
| 4 | Accuracy confidence (minimum) | 0.85 | `default.quality_gates.phase_4_validation.min_accuracy_confidence` |
| 5 | Grammar errors allowed | 0 | `default.quality_gates.phase_5_structure.max_grammar_errors` |
| 5 | Flesch Reading Ease (minimum) | 60 | `default.quality_gates.phase_5_structure.min_flesch_reading_ease` |
| 5 | Flesch Reading Ease (maximum) | 80 | `default.quality_gates.phase_5_structure.max_flesch_reading_ease` |
| 5 | Grade tolerance | 0.5 | `default.quality_gates.phase_5_structure.readability_grade_tolerance` |
| 6 | H2 headings with the keyword (minimum) | 2 | `default.quality_gates.phase_6_seo.keyword_placement_required.min_h2_with_keyword` |
| 6 | Meta title length (maximum characters) | 60 | `default.quality_gates.phase_6_seo.meta_title_max_chars` |
| 6 | Meta description length (maximum characters) | 155 | `default.quality_gates.phase_6_seo.meta_description_max_chars` |
| 6.5 | Remaining-AI-signal score (maximum) | 0.3 | `default.quality_gates.phase_6_5_humanizer.max_ai_signal_score` |
| 7 | Approve line | 7.0 | `default.minimum_pass_score` |
| 7 | Human-review line | 5.0 | `default.human_review_threshold` |
| 8 | Appendices required | 4 | `default.quality_gates.phase_8_output.appendices_present` |

## What the run auditor re-checks before "completed"

`scripts/run-audit.py` re-derives what a finished run claims from the artifacts on disk, using the plugin's own scripts. It holds two rules: it never trusts an agent's report (a report is a claim, the artifact is the evidence), and a missing input makes a check report `N/A`, never a silent pass. Its verdict, `CLEAN` or `VIOLATIONS`, is written to `run-audit.json` in the run directory together with a sha256 fingerprint of the files it read: `run.json`, every `phase-*` artifact, `source-draft.md` and every `.docx`. `finalize --status completed` refuses without a `CLEAN` verdict, and also refuses when any of those files changed, was added or was removed after the audit, so a verdict about an earlier version of the run cannot be stamped onto a later one. Hashes decide it, not timestamps: a sync or copy that rewrites modification times does not invalidate an audit, and a one-word edit does. An audit written without a fingerprint cannot prove it is fresh and is refused too. `--status blocked` needs no audit because it claims nothing; `--skip-audit` finalises anyway but stamps `audit_skipped: true` into `run.json`, so skipped verification is on the record.

| Section | Check (as the script names it) | Fails when |
|---|---|---|
| A manifest | run.json parses | The manifest is missing or corrupt. |
| A manifest | completed phases are known phases | The manifest lists a phase that does not exist. |
| A manifest | every completed phase has its artifact on disk | A phase is recorded complete but its file is absent. |
| A manifest | no orphaned artifacts in a finalized run | A finalized run has artifacts for phases it never recorded. |
| A manifest | total_loops equals the sum of loop_counts | The loop total disagrees with the per-edge counts. |
| A manifest | loop history arithmetic matches the counts | The number of loop-history rows disagrees with the counts. |
| A manifest | total loops within the per-run budget | The recorded loops exceed the per-run cap. |
| A manifest | every loop edge within its cap | An edge, or a capped group of edges, exceeds its cap; the smaller cap governs. |
| B body | no production scaffolding in the delivered body | Placeholders or production instructions remain in the body. |
| B body | body word count inside the gate | The body is outside ±10% of the target word count in the run's metadata. |
| B body | every generated inline asset has a body anchor | A valid chart exists but there is nowhere in the body to embed it. |
| B body | no manifest path points at a missing file | The visual manifest names a file that is not on disk. |
| C authorship | zero author sentences rewritten | An author draft exists and one of its sentences was paraphrased. |
| C authorship | zero author sentences dropped | An author draft exists and one of its sentences is gone. |
| C authorship | stored authorship record matches a fresh measurement | The stored record describes a body that has since changed. |
| D ledger | fix-ledger verify produced a readable result | The ledger script's output cannot be read. |
| D ledger | no correction was undone downstream | A later phase reversed an applied correction. |
| E review | APPROVED decision is backed by its own score | The decision says APPROVED but the score is below the approve line config resolves for the review's industry (or the brand profile's, whichever is stricter). |
| E review | review applied the approve line its industry resolves to | The review's recorded `minimum_pass_score_applied` differs from the line config resolves. |
| E review | review industry is not laxer than the brand profile's | The review recorded an industry whose approve line is lower than the brand profile's. |
| E review | APPROVED decision has every dimension at or above its minimum | An APPROVED review has a dimension below the minimum config resolves, raised industry minimums included. |
| E review | review weights match the configured weights for its industry | The review's `weights_applied` differ from the configured weights. |
| E review | overall score matches the weighted dimension scores | The overall score is more than 0.15 away from the review's own dimension scores weighted by config. |
| E review | review publication_status agrees with the ledger | The review and a fresh ledger verification disagree. |
| E review | review records a publication_status | A run with a fix ledger has a review that does not say whether the piece is publishable. |
| F deliverable | phase-8 status agrees with the ledger | The output record and a fresh ledger verification disagree. |
| F deliverable | blocked deliverable is marked DRAFT | A blocked piece is delivered without the `DRAFT-` prefix. |
| F deliverable | every .docx is valid OOXML | A delivered `.docx` is corrupt or missing its document part. |
| G honesty | 'completed' is not hiding a blocked publication | A completed run has open blocking corrections or a BLOCKED review. |
| G honesty | 'blocked' names at least one open blocker | A blocked run records no open blocker anywhere. |

One number is fixed inside the script, and a test pins it to config: the word-count band is ±10% (`word_count_tolerance_percent`). The approve line is not fixed there: the auditor resolves it from `scoring-thresholds.json` for the review's industry. The composite is recomputed from the review's own dimension scores and the configured weights and compared within a rounding tolerance of 0.15, because each dimension and the composite are reported to one decimal. The express lane renormalises the weights when a phase is skipped, so for express reviews the weights and composite checks report `N/A`. Reviews written before the reviewer recorded `industry`, `minimum_pass_score_applied` and `weights_applied` report `N/A` for the checks that need them, never a pass.

What the auditor does not do is on the list further down. The short version: it checks that the run's claims are backed by files and agree with config, not that the content is good.

## Advisory signals that never gate

These are reported, shown to the human editor, and never block a piece by themselves.

- **AI-detectability scan.** `text-metrics.py --ai-tell-scan` returns a deterministic LOW, MODERATE or HIGH rating from banned-word, significance-marker, soft-adverb and connective-opener rates (thresholds in `default.quality_gates.phase_6_5_humanizer.ai_tell_scan`). It is a proxy for visible text, labelled advisory in its own output, and a HIGH rating must carry a one-line explanation in the humanizer report. It cannot fail a run. Its only route into the score is that a HIGH rating can lower one of the five Readability sub-scores.
- **Structural-tell scan.** `--structure-scan` flags moralizing closers, template symmetry, low specificity, stance absence, uniform rhythm and entity development. Advisory. The review sheet (`phase-6.5-review-sheet.html`) maps the flagged sentences for a human editor.
- **Burstiness.** Reported with no minimum to hit.
- **Keyword density.** An advisory band of 1.0–2.0 percent. Gate 6 checks placements, not density.
- **External detector scores**, only when a detector tool happens to be reachable in the session, as context in the report.
- **Telemetry advisories.** Recurring humanizer patterns can reach the next drafter brief behind a recurrence floor. They never change a gate, a threshold or a verdict.

Note the neighbour that is not advisory: the humanizer's remaining-AI-signal score (at most 0.3) is a criterion inside Gate 6.5. It is computed by the humanizer agent from the weighted catalog formula, not by a script, so the run auditor does not re-derive it.

Nothing here claims a piece is or is not AI-written, and nothing here promises how a third-party detector will score it. The scans read visible text only. ContentForge neither detects nor removes any provenance watermark, and it will not.

## What this contract does not promise

- **That every claim is true.** Facts are verified against the sources the tools can reach. Up to 3 unverified claims are tolerated in the draft when they are hedged or attributed, so a delivered piece can carry hedged claims that no source confirmed.
- **Independent verification at every layer.** The validator diffs against the Phase 2 ledger rather than re-fetching, and the reviewer spot-checks a sample. An error that survives Phase 2 can survive Phase 4.
- **That scores are measurements.** The Phase 7 dimension scores come from an agent applying a written rubric. The auditor re-derives the policy and the arithmetic (the approve line, the weights, the minimums, the composite) but not the judgment: it cannot tell whether a 7.8 in Citation Integrity was earned.
- **That every phase ran.** The auditor verifies that what the manifest claims is backed by files. It does not demand that every phase was recorded, because lanes such as express skip phases by recorded choice. N/A checks do not fail a `CLEAN` verdict unless you run the audit with `--strict`.
- **That a budget stops the loop.** Budgets are enforced after the fact: a run that exceeded one fails the audit and cannot be finalised as completed, but nothing refuses the loop while it happens.
- **That the audit covers every byte.** Its fingerprint covers the top level of the run directory (the manifest, the `phase-*` artifacts, the author draft, delivered `.docx` files). Files elsewhere, such as generated image assets, are checked for existence, not hashed.
- **Regulatory or legal sign-off.** Guardrails and disclaimers are checked against the brand profile and the industry pack. Empty guardrails lower Brand Compliance and flag the run. This is not a substitute for compliance counsel.
- **That links stay alive.** Internal-link URLs are fetched live during the run. They are not monitored afterwards.
- **Anything about the piece after delivery.** Edits after the `.docx` is delivered are outside the audit. Publishing to a CMS has its own verification step in `/contentforge:publish`.
- **Rankings or AI citations.** The SEO gates check placements and structure. Whether engines cite the piece is measured afterwards, from Google-observable signals only, by `/contentforge:cf-aeo-check`.

## Verify it yourself

From the plugin directory, with a finished run:

```bash
# Re-derive the run from its files; writes run-audit.json into the run directory
python scripts/run-audit.py --brand <slug> --run-id <run_id>

# The same, but N/A checks also fail the verdict
python scripts/run-audit.py --brand <slug> --run-id <run_id> --strict

# Do the carried-forward corrections survive in the delivered body?
python scripts/fix-ledger.py verify --run-dir <run-dir> --target phase-6.5-humanized.md

# The advisory AI-detectability scan, on the delivered body
python scripts/text-metrics.py --file <run-dir>/phase-6.5-humanized.md --ai-tell-scan
```

In `run.json`, `audit_verdict: CLEAN` means the audit passed before the run was finalised, and `audit_skipped: true` means it was waived and the run was closed unverified.
