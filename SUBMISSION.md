# Anthropic Software Directory — Submission Packet

**Plugin:** ContentForge
**Version at submission:** 3.10.0
**Submitter:** Indranil Banerjee — neel@neelverse.com
**Repository:** https://github.com/indranilbanerjee/contentforge
**Marketplace:** https://github.com/indranilbanerjee/neels-plugins
**Last updated:** 2026-05-17

This file is the submission packet for the Anthropic Software Directory. It is **not** the directory listing — that is submitted via the form at https://platform.claude.com/plugins/submit. This packet pre-stages every input the form will ask for so submission takes ~5 minutes, not hours.

## 1. One-line description

> Enterprise content production via 11-phase autonomous pipeline — research, fact-check, draft, visualize, validate, structure, SEO/GEO, humanize, review, output (.docx). 29-pattern AI-detection humanizer. EU AI Act Article 50 C2PA provenance.

## 2. Long description

ContentForge is an enterprise-grade content production system for marketing teams running on Claude Code & Cowork. It replaces 6–8 person content workflows with a coordinated 13-agent pipeline that turns a one-line topic into a publication-ready, fact-checked, brand-compliant Microsoft Word document in 30–60 minutes through 11 quality gates with three-layer fact verification (Phase 2 fact-checker → Phase 4 scientific validator → Phase 7 reviewer).

**v3.10.0** adds end-to-end-tested C2PA content provenance for the .docx output (EU AI Act Article 50 compliance, applicable 2 August 2026) via `--c2pa-sign` on `scripts/generate-docx.py` — embeds inline when c2pa-python supports the format, falls back to a verifiable `.c2pa.json` sidecar otherwise. Plus May 2026 AEO reality updates in the Phase 6 SEO/GEO optimizer (Google AI Overviews 55% prevalence, LLMs.txt companion standard, Profound/Otterly/Conductor measurement references).

**v3.9.5** introduced the three-category internal linking framework — topical (informational), commercial (brand product/service pages), conversion (audience-matched CTA), authority (brand-name attribution) — with a `brand_pages` schema in the brand profile, color-coded inline Word hyperlinks in the .docx, and an Appendix D internal link map. Marketers verify funnel coverage at a glance rather than producing a "face document" with no commercial pathway.

**v3.9.4** fixed pipeline orchestration so every phase actually invokes its subagent via the Task tool rather than single-pass generating. **v3.9** rebuilt the Phase 6.5 humanizer around a 29-pattern AI-detection catalog (adapted from Wikipedia: Signs of AI Writing + blader/humanizer) with a self-critique meta-pass and optional voice calibration from a brand `writing_sample` field.

13 agents, 19 skills, 7 commands, 16 opt-in HTTP MCP connectors. Multi-plugin coexistence by design (zero global hooks, zero auto-connecting MCP servers). Full Cowork compatibility — all connectors are HTTP, all Python scripts run natively in the Anthropic Desktop computer-use environment.

## 3. Category

`Marketing & Sales` (primary) · `Productivity` (secondary)

## 4. Target audience

- Digital marketing agencies producing 20–200 long-form pieces per month
- In-house marketing teams in regulated industries (Pharma, BFSI, Healthcare, Legal) needing brand-voice + compliance enforcement
- Content marketing teams running multi-brand portfolios
- Solo content marketers who need agency-grade output without a team

## 5. Working use cases (Anthropic policy requirement: 3+)

### Use case 1 — Generate a publication-ready white paper

```
/contentforge:brand-setup       # one-time per brand
/contentforge:create-content
```

The 11-phase pipeline runs ~45–75 min for a 3500–4500-word whitepaper: Title curation → Research (5+ verified sources) → Fact-check (URL verification + claim cross-reference) → Drafting (SME calibration via industry knowledge pack) → Visual asset annotation → Scientific validation (hallucination detection + regulatory rules) → Structuring + proofreading → SEO/GEO with three-category internal linking → Humanizer (29-pattern catalog + self-critique meta-pass) → Reviewer (5-dimension scoring) → Output Manager (.docx with embedded SEO/Quality/Production scorecards + Appendix D internal link map).

Empirically tested on a pharma whitepaper ("Antibody-Drug Conjugates in HER2-Low Metastatic Breast Cancer"): 4,353 words, 18 citations including 5 NEJM papers with verified DOIs, all 3 required compliance disclaimers, 0 prohibited terms, 8.4/10 B+ APPROVED at the pharma 8.0 threshold, 0 hallucinations.

### Use case 2 — EU AI Act Article 50 compliant .docx

```
/contentforge:create-content
# pipeline runs ...
python3 scripts/generate-docx.py \
    --content output/humanized.md --output output/article.docx \
    --reports output/reports.json --brand "Acme Corp" \
    --content-type article \
    --c2pa-sign
```

Produces the .docx + a `.c2pa.json` sidecar with the manifest: claim_generator_info (ContentForge 11-phase pipeline), c2pa.actions.v2 (c2pa.created + c2pa.edited with "Human-reviewed via Phase 7 reviewer scorecard before delivery"), stds.schema-org.CreativeWork (Article type, Organization author, headline). The sidecar travels with the .docx. Verifiable by any C2PA tool.

### Use case 3 — Three-category internal linking for commercial impact

```
/contentforge:create-content
```

When the brand profile has `seo_preferences.brand_pages` populated with `product_or_service_pages`, `conversion_pages`, and `authority_pages`, the SEO/GEO optimizer (Phase 6) emits typed `<!-- INTERNAL-LINK: type=... -->` markers across the body. The output-manager (Phase 8) renders them as real inline Word hyperlinks color-coded by category — topical blue, commercial green, conversion purple, authority slate. The .docx Appendix D shows every link with anchor text, target URL, section, and reason. Empirically verified: a pharma whitepaper produced 5 typed links (3 topical + 1 commercial + 1 conversion), all clickable in Word.

### Use case 4 — Batch production across a multi-brand portfolio

```
/contentforge:batch-process
```

Processes 10–50+ pieces in parallel across multiple brands with queue management, priority scheduling, and progress tracking. 4–5× faster than sequential. Each piece carries its own brand profile, industry knowledge pack, jurisdiction rules.

## 6. Testing account / sample data

**Testing account:** Reviewers install from the public marketplace at `indranilbanerjee/neels-plugins` and use `config/brand-registry-template.json` as sample brand input. Knowledge-only mode (default) runs all 19 skills + 13 agents + 16 industry knowledge packs with zero external API keys beyond Claude. Optional Python deps: `python-docx` (auto-installed on first .docx generation), `c2pa-python` + `cryptography` (auto-installed on first `--c2pa-sign` invocation).

**Sample worked output:** the pharma whitepaper described in Use Case 1 above demonstrates the full pipeline output shape (humanized.md + reports.json + .docx with 4 appendices). Reviewers can reproduce by running `/contentforge:create-content` with the same topic.

## 7. Ownership verification

- **Repo:** github.com/indranilbanerjee/contentforge — owned by @indranilbanerjee
- **Marketplace:** github.com/indranilbanerjee/neels-plugins — same owner
- **Third-party services referenced:** all MCP connectors point to official endpoints (Notion, Canva, Figma, Webflow, Slack, Gmail, Google Calendar, fal.ai, Replicate, Pipedream / Composio / Zapier / Make aggregators). No scraping, no credential interception, no impersonation.
- **Trademarks:** "ContentForge" is the submitter's mark.

## 8. Compliance with Anthropic Software Directory Policy

| Policy area | Status |
|---|---|
| No High-Risk Use Cases | ✓ Marketing content generation; not medical/legal/financial advice. Industry knowledge packs (pharma, BFSI, legal) provide content guidelines only — plugin disclaims advisory authority. |
| No Usage Policy violation | ✓ Generates legitimate marketing content. Brand guardrails mechanism lets brands declare additional prohibited content per internal policy. |
| Testing account + sample data + 3+ use cases | ✓ Sections 5, 6 above. |
| Ownership of APIs/domains/UIs | ✓ Section 7. |
| Maintenance commitment | ✓ Quarterly+ release cadence demonstrated: v3.6 (Mar 2026) → v3.7 → v3.8 → v3.9 (May 3) → v3.9.1 (May 3) → v3.9.2 (May 3) → v3.9.3 (May 9) → v3.9.4 (May 12) → v3.9.5 (May 13) → v3.9.6 (May 15) → v3.10.0 (May 17). |
| Issue response timeframe | ✓ <72 hours acknowledgement; <7 days security/correctness patches via GitHub Issues. |
| Software Directory Terms agreement | ☐ Agreed at submission time via the form. |
| Design guidelines | ✓ Canonical `/contentforge:<command>` namespace; no bare slash commands; README onboarding-first per v3.9.5 restructure; all command frontmatter has `description`, `argument-hint`, `allowed-tools`. |

## 9. Cowork compatibility statement

- All 16 HTTP MCP connectors work in both Claude Code and Cowork.
- All Python scripts (including `scripts/generate-docx.py` with `--c2pa-sign`) run natively in Cowork — Cowork is the Anthropic Desktop computer-use product with local filesystem access.
- Plugin ships zero global hooks and zero auto-connecting MCP servers; multi-plugin coexistence by design.
- For services without first-party HTTP MCPs (Google Sheets / Drive / dozens more), `.mcp.json.connectors-reference` documents Pipedream / Composio / Zapier / Make aggregator paths.

## 10. Verified-badge eligibility

ContentForge qualifies based on:
- v3.9.4 pipeline orchestration fix (Task-tool subagent dispatch verified end-to-end on a pharma whitepaper)
- v3.9.5 three-category internal linking (empirically verified: 5 typed links in a real .docx)
- v3.10.0 C2PA Article 50 path (sidecar manifest empirically verified)
- Three-layer fact verification pattern (research → fact-check → reviewer) demonstrably produces 94–100% factual accuracy in production tests
- 16 industry knowledge packs maintained quarterly

If applying for Verified, additional materials to prepare:
- Review of the c2pa-python integration in `scripts/generate-docx.py` (signing keys — describe key-management expectations)
- Privacy review of brand-profile.json schema
- Code review of `agents/07-reviewer.md` (the Phase 7 scoring rubric is load-bearing)

## 11. Screenshots to include with submission

Capture before submitting:
1. Phase 7 reviewer scorecard for a real piece (shows the 5-dimension scoring UX)
2. The .docx Appendix D internal link map with the three color-coded link types
3. A C2PA sidecar manifest opened in a JSON viewer alongside its .docx
4. `/contentforge:create-content` pipeline running with the [N/11] phase progress indicators
5. The humanizer report showing 29-pattern catalog hits + before/after burstiness numbers

## 12. Submission steps

1. Open https://platform.claude.com/plugins/submit
2. Plugin name: `contentforge`
3. Marketplace source: `github.com/indranilbanerjee/neels-plugins` (custom marketplace) OR `github.com/indranilbanerjee/contentforge` (direct repo)
4. Paste section 1 (one-line) into Short description
5. Paste section 2 (long description) into Description
6. Category: Marketing & Sales (primary), Productivity (secondary)
7. Upload screenshots from section 11
8. Confirm testing-account + sample-data declaration (sections 5, 6)
9. Confirm ownership (section 7)
10. Check the Software Directory Terms box
11. Submit

Expected review timeline: 1–2 weeks basic listing, 4–6 weeks Anthropic Verified.

---

**Maintained in the repo so it can be refreshed each release before re-submission.**
