---
description: Audit your content library for freshness decay, coverage gaps, and optimization opportunities
argument-hint: "<content source: drive folder|wordpress url|csv> [--scope=freshness|gaps|both]"
---

# Audit Content

This command is a thin wrapper. The complete audit procedure — including the canonical
freshness scoring model — lives in [`skills/cf-audit/SKILL.md`](../skills/cf-audit/SKILL.md).
Read that file and execute it end to end. Do not improvise a different scoring model here.

## Trigger

User runs `/contentforge:audit-content` or asks to audit their content, check for content
decay, find content gaps, or assess content health.

## Gather inputs

If not provided in the arguments, ask before proceeding:

1. **Content source** — Google Drive folder URL, WordPress site URL, CSV file
   (columns: `title`, `url`, `publish_date`, `content_type`, `word_count`), or a pasted list
2. **Audit scope** — `freshness` | `gaps` | `both` (default)
3. **Optional** — aging threshold in months (default 12), brand filter, target keywords CSV, competitor URLs

## Canonical scoring (defined in the skill — summarized here for orientation only)

Freshness = 4 factors: Age 35% / Statistics currency 25% / Link health 20% / Citation
recency 20%. Bands: Fresh 90-100, Good 70-89, Aging 50-69, Stale 30-49, Expired 0-29.
The skill file is authoritative if this summary ever disagrees.

## Execute

Follow `skills/cf-audit/SKILL.md` in full:
load inventory → freshness scoring → coverage gap analysis → performance analysis
(if analytics connected) → prioritized recommendations (refresh / new / retire).

## After the audit

Ask: "Would you like me to:
- Create content briefs for the top gap opportunities? (`/contentforge:content-brief`)
- Start refreshing the highest-priority piece? (`/contentforge:content-refresh`)
- Build a quarterly content calendar from these recommendations? (`/contentforge:cf-calendar`)
- Run a deeper SEO analysis for specific pieces? (`/digital-marketing-pro:seo-audit` — requires the Digital Marketing Pro plugin)
- Export this audit to a spreadsheet?"
