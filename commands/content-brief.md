---
description: Generate a research-backed content brief with keyword data, competitor analysis, search intent, and SEO strategy
argument-hint: "<keyword or topic>"
---

# Content Brief

This command is a thin wrapper. The complete brief-generation procedure lives in
[`skills/cf-brief/SKILL.md`](../skills/cf-brief/SKILL.md) — read that file and execute it
end to end. Do not improvise a different flow from this wrapper.

## Trigger

User runs `/contentforge:content-brief` or asks to create a brief, plan content, research a
topic for writing, or prepare a content outline.

## Gather inputs

If not provided in the arguments, ask before proceeding:

1. **Keyword or topic** — the primary keyword or topic to build the brief around
2. **Target audience** — who this content is for (e.g., "Healthcare CIOs", "Small business owners")
3. **Optional** — content type preference (article, blog, whitepaper, FAQ, video script), 1-5 competitor URLs, SEO goal (`traffic` | `conversions` | `awareness`), brand profile name

## Execute

Follow `skills/cf-brief/SKILL.md` in full:
keyword research → competitor & E-E-A-T analysis → search intent classification →
audience pain points & questions → recommended outline → SEO strategy →
AEO/GEO strategy (AI Overview presence, citation-worthiness, answer blocks) →
success metrics (quality score goal 8.5+).

If SEO connectors (Ahrefs, Similarweb) are not connected, use the skill's web-search
fallback and label estimates as estimates. To connect: `/contentforge:cf-connect ahrefs`.

## After the brief

Ask: "Would you like me to:
- Start content production using this brief? (`/contentforge:create-content`)
- Create briefs for related topics?
- Adjust the brief for a different audience or content type?
- Check if this topic overlaps with existing content? (`/contentforge:audit-content`)
- Plan a content calendar around this topic cluster? (`/contentforge:cf-calendar`)"
