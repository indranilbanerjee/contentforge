export const meta = {
  name: 'audit-library',
  description: 'Freshness-audit a library from given URLs in parallel; records one audit to the ledger. Topic gaps, retire calls -> cf-audit. "audit these 20 URLs"',
  phases: ['Score each page', 'Record the audit'],
}

// args: { brand: "brand-slug", urls: ["https://..."], as_of?: "YYYY-MM-DD" }
// Reads public pages and the brand's AEO history; the only write is the final recorded audit.
const input = args || {}
const urls = Array.isArray(input.urls) ? input.urls.filter(Boolean) : []
if (!input.brand || urls.length === 0) {
  return 'audit-library needs args.brand (the ContentForge brand slug) and args.urls (the published pages to audit), e.g. {"brand": "acme", "urls": ["https://acme.com/blog/post-1"]}.'
}
const asOf = input.as_of || 'the current date'

const scored = {
  type: 'object',
  required: ['url', 'title', 'freshness_score', 'refresh_priority', 'recommended_scope', 'reasons'],
  properties: {
    url: { type: 'string' },
    title: { type: 'string' },
    freshness_score: { type: 'integer', minimum: 0, maximum: 100 },
    refresh_priority: { type: 'integer', minimum: 1 },
    recommended_scope: { type: 'string', enum: ['light', 'medium', 'heavy', 'retire', 'none'] },
    reasons: { type: 'array', items: { type: 'string' }, minItems: 1 },
  },
}

phase('Score each page')
const pages = await pipeline(urls, url =>
  agent(
    `Audit one published page for content freshness as of ${asOf}, for the ContentForge brand "${input.brand}".\n\n` +
    `Page: ${url}\n\n` +
    'Use the scoring rubric of the /contentforge:audit-content skill (read its SKILL.md if the skill is available): ' +
    'outdated statistics and dates, broken or dead outbound links, superseded facts, missing current developments, ' +
    'and lost AI-engine citations recorded in the brand\'s aeo/checks.json history. Open the page and its key cited sources. ' +
    'Every reason must name the specific evidence (the stale figure, the dead link, the newer fact with its source). ' +
    'refresh_priority is a rank hint (1 = refresh first); use "retire" only for pages with no remaining value.',
    { label: url, schema: scored },
  ),
)
const valid = pages.filter(Boolean)
log(`Scored ${valid.length} of ${urls.length} pages`)

phase('Record the audit')
return await agent(
  `Record this ContentForge library audit for brand "${input.brand}" using the /contentforge:audit-content skill's "Record the audit" step ` +
  '(scripts/audit-ledger.py --action record). Pieces (JSON):\n\n' +
  JSON.stringify(valid, null, 2) +
  `\n\nSet aeo_history_considered to true only if the brand's aeo/checks.json existed and was read during scoring; otherwise give the string "n/a — <reason>". ` +
  'Re-rank refresh_priority across the whole set (1..N, no ties). After recording, run the ledger\'s validate action and report its result, ' +
  'the recorded file path, and the top five refresh candidates. If recording fails, report the error verbatim and do not claim the audit was recorded.',
  { label: 'record' },
)
