# Design spec: the living link graph and the per-brand claim library

**Status:** DESIGN PASS — deliberately not built in v4.0.
**Why deferred:** both introduce durable per-brand stores whose node/edge schemas
become expensive to migrate once brands accumulate data. v4.0 shipped the
conventions they will inherit (canonical per-brand stores under the brand
directory, `audit-ledger.py`-style validate-on-write, `telemetry.py`-style
read-only aggregation, reported-N/A for missing inputs, plant-tested guards,
atomic writes via `_common`); this spec exists so the eventual build starts from
decisions, not improvisation.

Constraint set (inherited, non-negotiable): stdlib only, no graph databases, no
vendors; every store rides the brand-directory Drive sync on Cowork; loops
inform briefs and dashboards, never gates; reuse means cheap re-verification,
never skipped verification; every guard proves it can fail before it ships.

---

## Part 1 — The living link graph (upgrade of `brand_pages`)

### Problem
`brand_pages` is a setup-time snapshot. Phase 1 re-verifies brand URLs every run
(v4.0 now merges them back), but nothing ages entries, nothing represents the
published pieces themselves, and gap questions ("which commercial pages have no
topical feeders?") have no data structure to run against.

### Store
`{brand_dir}/link-graph.json` — single JSON document, atomic writes.

```json
{
  "version": 1,
  "nodes": {
    "<node_id>": {
      "kind": "brand_page | published_piece | staged_candidate",
      "url": "https://…",
      "category": "product_or_service | authority | conversion | topical",
      "title": "…",
      "source": "manual | harvest | phase1_recon | phase8_delivery",
      "verified_live": "YYYY-MM-DD",
      "ttl_class": "site_page"
    }
  },
  "edges": [
    { "from": "<piece_node>", "to": "<page_node>",
      "type": "topical | commercial | conversion | authority",
      "anchor_text": "…", "added": "YYYY-MM-DD",
      "provenance": "phase6_marker | appendix_d" }
  ]
}
```

- `node_id` = the `_norm_url()` identity already shipped in
  `harvest-brand-pages.py` (host without www, path without trailing slash) —
  one identity function, imported, never duplicated.
- Published pieces enter at Phase 8: the output manager records the delivered
  piece as a node and its Appendix D rows as edges. brand_pages remains the
  human-curated register; the graph subsumes it read-only at build time
  (brand_pages entries project into nodes — no double bookkeeping, brand_pages
  stays authoritative for curation fields).

### TTL discipline
One decay table, in the store, never in prose: `site_page: 90d`,
`external_reference: 180d` (future), configurable per brand. A node past TTL is
`stale`, never deleted. Re-verification = HTTP status check via the harvester's
existing `fetch()` — batched, polite, capped.

### Consumers
- `cf-audit` link-health factor → graph traversal (piece node → outbound edges →
  target staleness) instead of per-piece re-crawling.
- `cf-calendar` / `cf-brief` gap queries: commercial nodes with zero inbound
  topical edges; clusters without a hub; orphan pieces.
- Phase 6: anchor-text diversity check across ALL edges to a target, not just
  this piece's.

### Guards (each plant-tested at build time)
- Schema validator on write (audit-ledger pattern).
- Graph invariants: every edge endpoint exists; no duplicate node identities;
  `staged_candidate` nodes carry `needs_review`.
- A planted stale node must surface in cf-audit's factor breakdown.

### Migration
First build reads brand_pages + all historical runs' Appendix D data (where
manifests survive) and emits the graph with `source` honesty; brands without
history start empty. No destructive change to brand_pages, ever.

---

## Part 2 — The per-brand claim library

### Problem
Phase 2 verifies 15–25 claims per run and starts cold every run. Refresh
re-verifies whole pieces because nothing records which claims aged. "Which
published sentences depend on this dead source?" has no queryable answer.

### Store
`{brand_dir}/claim-library.jsonl` — append-only JSONL (one claim event per
line), because claims are events with history, not rows to overwrite.

```json
{ "claim_id": "sha256(normalized locked_wording)[:16]",
  "locked_wording": "exact ledger wording",
  "source_url": "https://…", "source_title": "…",
  "reliability": 9, "verified_at": "YYYY-MM-DD",
  "ttl_class": "market_number | study_finding | evergreen_fact",
  "run_id": "…", "event": "verified | reverified | superseded | retracted",
  "supersedes": "<claim_id or null>" }
```

- TTL classes mirror the benchmark-book philosophy: `market_number: 90d`,
  `study_finding: 365d`, `evergreen_fact: no expiry but source liveness 180d`.
- Pieces reference claims: Phase 8 appends `{run_id, claim_ids[]}` usage events,
  so blast-radius ("source retracted → which pieces?") is a scan, not a search.

### The one rule that keeps it honest
**Reuse = cheap re-verification, never skipped verification.** Phase 2 consults
the library FIRST; a hit within TTL still gets its source URL liveness-checked
and its wording compared verbatim before the claim enters the run ledger with
`event: reverified`. A miss or an aged hit goes through full verification
exactly as today. The library makes Phase 2 faster; it is forbidden from making
it weaker — and the run auditor's authorship-style check for this store is that
every `reverified` event has a same-day liveness record.

### Consumers
- Phase 2 (warm start), `content-refresh` (scope = aged claims only, proven
  fresh claims listed as untouched), `cf-audit` statistics-currency factor
  (read the library instead of estimating), future trust appendix ("every
  statistic resolves to a dated verified node").

### Guards
- JSONL line validator; claim_id determinism test; supersede chains acyclic;
  a planted aged claim must scope a refresh; a planted dead source must appear
  in blast-radius output.

### Explicitly out of scope (both parts)
Cross-plugin sharing (format-first via the marketplace drift-guard pattern IF
ever), automatic gate changes from graph/library signals, any external service.

---

*Prepared 2026-08-17 alongside the v4.0 lifecycle release. Build order when
approved: link graph first (its identity function and TTL loop are already
half-shipped), claim library second (highest trust payoff, strictest honesty
rule).*
