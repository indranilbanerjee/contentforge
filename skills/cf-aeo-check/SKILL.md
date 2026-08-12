---
name: cf-aeo-check
description: "Post-publication AI-visibility check — re-probes target queries via web search, records whether the published piece is cited in Google AI Overviews, audits on-page extractability (definition block, dates, schema, structures) via web fetch, and appends every check to per-brand history so deltas are tracked over time. Triggers on \"/contentforge:cf-aeo-check\", \"is our article cited in AI Overviews\", \"did we earn AI citations\", \"check AEO for this URL\", \"why is a competitor cited instead of us\". Measures Google-observable signals only (no ChatGPT/Perplexity probing unless an AEO-tracking connector is present, and then labeled); closes the loop /contentforge:cf-brief opens and routes absent verdicts to /contentforge:content-refresh with evidence. Reports and records — it does not edit or republish the page."
argument-hint: "[published URL or REQ-ID]"
effort: medium
---

# AEO Citation Check — Post-Publication

Close the loop that `/contentforge:cf-brief` opens. The brief checks AI Overview presence and citation patterns **before** production; this skill verifies — after publication — whether the piece actually earned citations, tracks the trend across re-checks, and routes losses to `/contentforge:content-refresh` with specific evidence.

## Honest scope — read before promising anything

- **What this skill measures directly:** Google SERP state for the target queries via web search (AI Overview present? which domains are cited/visible? does the piece rank?), and on-page extractability of the published URL via web fetch (definition block intact, dates visible, schema present, metrics tables surviving the CMS).
- **What it cannot measure directly:** citations inside ChatGPT, Perplexity, Gemini or Copilot answers — there is no public API for "was I cited," and probing chat UIs is not reproducible. Cross-engine measurement needs a third-party tracker (Profound, Otterly, Conductor AgentStack, HubSpot AEO — same list the Phase 6 optimizer names). **If such a connector is available in the tool list, use it and label the data's source; if not, say plainly that engine coverage is Google-observable-only.** Never present an estimate as a measurement.

## When to Use

Use `/contentforge:cf-aeo-check` when:
- A piece published **2+ weeks ago** and you want to know if AI engines are citing it (earlier checks mostly measure indexing lag, not merit)
- You're deciding **which content to refresh** and want citation evidence, not hunches
- A competitor appears in AI Overviews for your target query and you want the delta documented
- You want a standing **citation scoreboard** per brand across re-checks

**Not for:** pre-production research (that's `/contentforge:cf-brief`), rank tracking as a discipline (this is a citation check, not a rank tracker), or measuring engines it cannot observe (see Honest scope).

## Required Inputs

**Minimum required (one of):**
- **Published URL** — the live page to check
- **Requirement ID** (e.g., `REQ-001`) — resolved via the brand's tracking backend to the published URL recorded at completion; fails with a clear message if no URL was recorded

**Optional:**
- **Brand** — brand profile (auto-detected from the tracking record when using REQ-ID)
- **Queries** — comma-separated override of the queries to probe. Default: primary keyword + top 3 question keywords, recovered from the run's `phase-6-seo.md` (preferred) or the brief; if neither exists, derive 3-5 natural queries from the page's H1/H2s and say so. **Also fold in any FAQ-disposition questions from the Phase 7 review report** — the questions the reviewer found readers silently asking are the closest thing to real query data the pipeline produces, and they are exactly what answer engines get asked
- **`--compare`** — show deltas vs the previous check (default when history exists)

## How to Use

```
/contentforge:cf-aeo-check https://acme.com/blog/ai-in-healthcare-2026
/contentforge:cf-aeo-check REQ-001 --brand=AcmeMed
/contentforge:cf-aeo-check REQ-001 --queries="ai diagnostics accuracy,is AI better than radiologists"
```

## What Happens

### Step 1: Resolve target + queries (10-20 seconds)
- Resolve REQ-ID → published URL via the tracking backend (`local` / `google_sheets` / `airtable`)
- Assemble the query set (see Required Inputs); record which source the queries came from — scorecard honesty rule: derived queries are labeled `derived`, never passed off as the brief's targets

### Step 2: SERP + AI Overview probe (per query, 1-3 minutes total)
For each query, via web search:
1. **AI Overview present?** yes / no / unclear (record verbatim which sources are visibly cited when the search surface exposes them)
2. **Own-domain citation:** is the published piece (or its domain) among the cited/visible sources? `cited` / `visible-not-cited` / `absent`
3. **Competitor presence:** which Phase-1/Phase-2-era competitors (or new domains) hold the citations
4. **Organic position band** for the published URL where observable: top-3 / top-10 / beyond / not-found — a band, not a fake precise rank

### Step 3: On-page extractability audit (30-60 seconds)
Web-fetch the published URL and verify the machine-liftable elements survived the CMS:
- Definition sentence within the first 150 words — intact?
- Publication + last-updated dates visible?
- Structured elements (tables, numbered steps, Q&A headers) from the phase-6 structure manifest — still present in the rendered page?
- Article/Person schema in the page source — present? (CMSes routinely strip JSON-LD; this is the #1 silent AEO regression)
- Author byline with credentials — rendered?

### Step 4: Record + delta (10 seconds)
Append the check to `~/.claude-marketing/{brand-slug}/aeo/checks.json` (same storage-resolution rules as every other artifact — `$CLAUDE_MARKETING_HOME` → `$CLAUDE_PLUGIN_DATA` → `~/.claude-marketing`):

```json
{
  "url": "...", "requirement_id": "REQ-001", "checked_at": "YYYY-MM-DD",
  "queries": [{"q": "...", "source": "phase-6-seo|brief|derived|user",
               "ai_overview": "yes|no|unclear", "own_citation": "cited|visible-not-cited|absent",
               "cited_domains": ["..."], "position_band": "top-3|top-10|beyond|not-found"}],
  "extractability": {"definition_intact": true, "dates_visible": true,
                     "structures_intact": "4/5", "schema_present": false, "byline_rendered": true},
  "engine_coverage": "google-only|google+<connector-name>"
}
```

If history exists, compute deltas per query (gained / lost / unchanged citation status) and flag any extractability regression since the last check.

### Step 5: Report + routing
Render the AEO Check Report: per-query table, extractability checklist, deltas, and **one recommended action**:
- `cited` and holding → re-check in 6-12 weeks, no action
- `visible-not-cited` → extractability fixes first (they're free): restore stripped schema, tighten the definition block — then re-check in 2-4 weeks
- `absent` while competitors are cited → route to `/contentforge:content-refresh` with the specific gap evidence (which domains are cited and what they have that the piece lacks)
- Extractability regression (schema stripped, structures flattened by the CMS) → fix at the CMS level; note that `/contentforge:cf-publish` post-publish verification would have caught this at publish time

**Cadence recommendation:** check at ~2, ~6 and ~12 weeks post-publication, then quarterly. Record every check — the trend is the product.

## Output Example

**SYNTHETIC EXAMPLE — fabricated for illustration; never reuse these domains or results.**

```
AEO CITATION CHECK — acme.com/blog/ai-in-healthcare-2026
Checked: 2026-07-30 | Previous: 2026-07-02 | Engine coverage: google-only

| Query                                | AIO | Own citation        | Δ vs last  | Cited domains        |
|--------------------------------------|-----|---------------------|------------|----------------------|
| ai diagnostics precision medicine    | yes | cited               | ▲ gained   | acme.com, nih.gov    |
| how accurate is AI diagnosis         | yes | visible-not-cited   | = unchanged| examplehealth.com    |
| ai diagnostic tools for hospitals    | no  | — (top-10 organic)  | = unchanged| —                    |

Extractability: definition ✓ | dates ✓ | structures 5/5 ✓ | schema ✗ (JSON-LD stripped by CMS) | byline ✓

Action: schema was present at publish and is now missing — restore Article+Person
JSON-LD in the CMS template, then re-check query 2 in ~3 weeks.
```

## Limitations

- Google-observable signals only, unless an AEO-tracking connector is present (then per-connector coverage, labeled)
- AI Overview composition varies by location/session — single probes are evidence, not ground truth; the multi-check trend is the reliable signal
- A citation today is not a citation tomorrow; that is why checks append to history instead of overwriting

## Related Skills

- **[/contentforge:cf-brief](../cf-brief/SKILL.md)** — the pre-production half of this loop (AI Overview presence + citation-worthiness plan)
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** — where `absent` verdicts with competitor evidence get acted on
- **[/contentforge:cf-audit](../cf-audit/SKILL.md)** — library-wide freshness; this skill is per-piece citation depth
- **[/contentforge:cf-publish](../cf-publish/SKILL.md)** — its post-publish verification is the time-zero baseline this skill compares against
