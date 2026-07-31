# Case Study Structure Template — ContentForge

## Content Type: Case Study
**Target Word Count:** 1200-2000 words
**Target Reading Level:** Flesch-Kincaid Grade 9-11
**Minimum Citations:** 5-10 sources (external claims only — see Data Provenance below)
**SEO Focus:** Medium (primary keyword + client/solution entities)

---

## Data Provenance — the rule that makes case studies different

A case study is built from **two kinds of facts**, and the pipeline treats them differently:

| Fact type | Source | Verification path |
|-----------|--------|-------------------|
| **Client-attested facts** — the client's name, situation, metrics, quotes, timeline | Supplied by the user at intake (`--case-data` file or interactive intake). The web cannot verify a private engagement. | Phase 2 marks them **CLIENT-ATTESTED** (never "VERIFIED"), confirms internal consistency (do the numbers add up? do dates order correctly?), and requires written client approval before publication is recommended. |
| **External context facts** — industry benchmarks, market size, competitor norms, regulatory context | Phase 1 research, normal citation rules | Standard Phase 2 verification (live URL, corroboration, recency) |

**Hard rules:**
- **NEVER fabricate a client, a metric, a quote, or an outcome.** If the user has not supplied case data, STOP and collect it — do not draft a hypothetical client and present it as real.
- An anonymized client ("a mid-market logistics company") is fine **when the user asks for anonymization** — the underlying data must still be user-supplied.
- Every client-attested metric in the draft carries the qualifier the client approved (e.g., "42% reduction in bounce rate over 6 months, per [Client]'s internal analytics").
- Quotes must be verbatim from intake material. Editing a quote for grammar requires flagging it for client re-approval.
- The synthetic-example rule applies to THIS template's samples: every example below is fabricated for illustration and must never appear in real output.

## Required Intake (before Phase 1)

Collect via `--case-data=<file>` (markdown or JSON) or interactively:

1. **Client** — name (or anonymization instruction), industry, size, market
2. **Challenge** — the situation before the engagement, ideally with a baseline metric
3. **Solution** — what was implemented, by whom, over what timeline
4. **Results** — 2-5 measurable outcomes with time windows and measurement source
5. **Quotes** — 1-3 attributed quotes (name, title) with confirmation they are approved for publication
6. **Approval status** — has the client approved public use? (If no: the output is marked DRAFT — INTERNAL until approval is recorded)

---

## Standard Structure

### 1. Title (H1)
- **Format:** Client + outcome, specific number where approved
- **Length:** 50-70 characters
- **Examples (SYNTHETIC):**
  - "How Northlake Logistics cut fulfillment errors 38% in one quarter"
  - "From 12% to 3% churn: inside Meridian SaaS's onboarding rebuild"
- Anonymized variant: "How a mid-market 3PL cut fulfillment errors 38% in one quarter"

### 2. Executive Snapshot (60-100 words + metrics table)
A results-first opening the reader can absorb in 10 seconds:

| | |
|---|---|
| **Client** | [Name or descriptor], [industry], [size] |
| **Challenge** | [One line] |
| **Solution** | [One line] |
| **Key results** | [2-3 headline metrics with time window] |

### 3. Client & Context (150-250 words)
- Who the client is, what market pressure made this matter
- 1-2 external context citations (industry benchmark, market trend) to frame the stakes
- SEO: primary keyword within first 100 words of body

### 4. The Challenge (200-350 words)
- The situation before, in concrete operational terms
- Baseline metrics (client-attested, with measurement source)
- What they had already tried and why it fell short
- What was at risk if nothing changed

### 5. The Solution (300-500 words)
- What was implemented — specific, not vendor-brochure abstract
- Implementation timeline (phases, weeks/months)
- Who was involved on both sides
- One honest friction point and how it was resolved (a frictionless story reads as fiction — humanizer pattern awareness)

### 6. Results (250-400 words + data)
- Each result: **metric → time window → measurement source → client attestation**
- Order results by business impact, not chronology
- Visual placeholder for the strongest before/after comparison: `[VISUAL-PLACEHOLDER: type=chart | description="before/after comparison" | data="client-attested metrics table"]` (Phase 3.5 charts client-attested data ONLY when the intake includes the underlying numbers; attribution line reads "Source: [Client] internal data, [period]")
- External benchmark comparison where a verified citation exists ("against an industry average of X% [citation]")

### 7. Client Voice (quote placement)
- 1-3 approved quotes woven into Challenge / Solution / Results sections — not ghettoized into a quote box at the end
- Attribution: full name, title, company (or approved anonymized form)

### 8. Lessons & Applicability (150-250 words)
- 2-4 transferable takeaways for the reader's own situation
- Honest scope limits: what about this result was situation-specific

### 9. CTA (30-60 words)
- One conversion-page link (Phase 6 `type=conversion` marker), audience-matched
- Natural action phrase tied to the problem this case study solves

---

## Phase Adaptations for Case Studies

- **Phase 1 (Research):** scope = external context only (benchmarks, market data, regulatory background). The client story comes from intake, not SERP mining. SERP analysis still runs on the primary keyword to position the piece against competing case studies.
- **Phase 2 (Fact Check):** two-track verification per the Data Provenance table. Gate 2's "≥80% verified" applies to **external** claims; client-attested items pass on internal consistency + intake traceability.
- **Phase 3.5 (Visuals):** charts may use client-attested numbers with "Source: [Client] internal data" attribution.
- **Phase 6 (SEO/GEO):** entities = client name (if public), solution category, industry terms. Case studies are strong AI-citation targets when the executive snapshot is machine-liftable — keep the metrics table intact (structure manifest protects it).
- **Phase 7 (Review):** Citation Integrity scores external claims normally; a case study with zero fabricated client data and full intake traceability is NOT penalized for having fewer web citations than an article.

## Quality Standards

- Zero fabricated client facts (hard fail — pipeline halts, not loops)
- Every metric carries a time window and measurement source
- At least one honest limitation or friction point included
- Approval status recorded in the Draft Metadata block
- Reads as a story with numbers, not a numbers dump with adjectives

## Common Pitfalls to Avoid

- **The hero-vendor narrative** — the client is the protagonist, not the vendor
- **Unanchored percentages** — "42% better" with no baseline, window, or source
- **Fabricated smoothness** — no friction = no credibility
- **Quote laundering** — paraphrasing a client and presenting it in quote marks
- **Benchmark smuggling** — comparing client results to an uncited "industry average"
