# ContentForge — Directory Submission Bundle

Prepared 2026-08-16 for the two official directories. Everything below is
ready to paste; items marked **[owner action]** need the account holder.

## Targets

| Directory | Route | Status |
|---|---|---|
| Anthropic official plugin directory | [submission form](https://clau.de/plugin-directory-submission) | bundle ready — **[owner action]** submit |
| OpenAI universal Plugins Directory (ChatGPT + Codex) | [submission portal](https://developers.openai.com/plugins/deploy/submission) | bundle ready — **[owner action]** verified publisher identity + Apps Management permission, then submit as a **skills-only** package (no MCP server → no domain verification) |

**The name is final: `contentforge`.** Names are immutable once listed.

## Listing metadata

- **Name:** contentforge · **Display name:** ContentForge
- **Category:** Content / Writing / Marketing
- **Short description:** Open-source enterprise content pipeline — 22 skills,
  13 agents, a 43-pattern AI humanizer, verified fix ledger, run auditor, and
  real .docx output.
- **Long description:** An 11-phase content pipeline where every quality claim
  is measured, not asserted: research → fact-check (verified claim ledger) →
  draft → visuals → hallucination validation → structure → SEO/GEO →
  humanize (43-pattern catalog, author-sentence protection) → review (weighted
  scorecard) → delivery (.docx with appendices). Corrections travel as a
  machine-verified fix ledger; a run auditor re-derives every gate from the
  artifacts before a run may call itself completed. Works with subagent
  dispatch or fully portable single-context execution.
- **Homepage / repo / support:** https://github.com/indranilbanerjee/contentforge
- **License:** MIT
- **Policy note for reviewers:** no hardcoded model ids, prices, or vendors
  (guarded by tests); AI-assistance disclosure layer on by default; no watermark
  detection or removal anywhere, permanently.

## Starter prompts (OpenAI requirement)

1. "Write a 1,200-word blog post about [topic] for [brand] — run the full
   ContentForge pipeline with fact-checking and review."
2. "I've written a rough draft myself — build the article around my words
   without rewriting them." (`--source-draft`)
3. "Run the express lane on this brief: I already have the research, I need it
   verified, structured, humanized, and reviewed."
4. "Audit my last content run — prove every quality gate actually passed."
5. "Set up a brand profile for [company] so every piece matches our voice."

## Test cases (OpenAI requirement: 5 positive + 3 negative)

**Positive**
1. *Full pipeline, blog.* Prompt: starter 1 with a real topic. Expected: 11
   phases execute in order with checkpoints; delivery includes a .docx with
   Appendices A–D; `run-audit.json` verdict CLEAN; word count inside ±10% of
   target. Reproduce: any brand profile + any factual topic.
2. *Author-draft protection.* Prompt: starter 2 with a 10-sentence rough draft
   containing typos. Expected: every author sentence verbatim in the deliverable
   (`authorship.py` exit 0, zero rewritten/dropped); typos preserved; the
   humanizer's catalog does not fire on author sentences.
3. *Fact-check gate blocks fabrication.* Prompt: full pipeline on a topic, then
   inspect `phase-2-factcheck.md` and `phase-4-validation.md`. Expected: every
   statistic in the draft traces to a verified-ledger entry; a claim absent from
   the ledger is flagged, never silently kept.
4. *Fix ledger closes the loop.* Prompt: a run where Phase 4 issues corrections.
   Expected: `phase-4-fixes.json` written; corrections applied by script at
   Phase 5; `fix-ledger.py verify` shows zero regressed at review.
5. *Blocked run tells the truth.* Prompt: run with `image_gen_mode: none` and
   decline the feature card. Expected: deliverable produced with `DRAFT-`
   prefix, `publication_status: BLOCKED`, blocker named on the completion card;
   tracking row does NOT read "completed".

**Negative**
1. *No brand profile.* Prompt: "write a post for BrandThatDoesNotExist".
   Expected: setup guidance, not a hallucinated brand voice; no run directory
   created for a nonexistent brand.
2. *Fabrication request.* Prompt: "add a statistic that 87% of CFOs agree, I
   don't have a source". Expected: refusal to fabricate — the claim is excluded
   or flagged for a source; it never enters the verified ledger.
3. *Unverifiable-gate finalize.* Prompt: finalize a run whose artifacts were
   hand-deleted. Expected: `finalize --status completed` refuses (no clean
   run-audit); the error names the failing checks and the recovery options.

## Release notes for first submission

v3.33.0 — see CHANGELOG.md. Versioning note for the OpenAI portal: published
skills are snapshots; every ContentForge release requires re-scan → re-review →
re-publish there (added to the release ritual).

## Known platform caveats to disclose

- Codex applies instruction caps at runtime; the orchestrator skill is large.
  Validate on a current Codex build before publishing. The portable execution
  lane (SKILL.md) is the supported mode on hosts without subagent dispatch.
- Scripts require Python 3.10+; charts/cards need matplotlib + pillow
  (auto-install attempted, documented in Requirements).
