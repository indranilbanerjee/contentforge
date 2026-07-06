---
description: Publish finished content to Webflow or WordPress with preview, verification, and HTML export fallback
argument-hint: "<content source> --platform=<webflow|wordpress> [--status=draft|publish|schedule]"
---

# Publish

This command is a thin wrapper. The complete publishing procedure lives in
[`skills/cf-publish/SKILL.md`](../skills/cf-publish/SKILL.md) — read that file and execute it
end to end. Do not improvise a different flow from this wrapper.

## Trigger

User runs `/contentforge:publish` or asks to publish, push, or deploy content to a CMS platform.

## Gather inputs

If not provided in the arguments, ask before proceeding:

1. **Content source** — Google Drive URL, local file path, or requirement ID (e.g., `REQ-001`)
2. **Platform** — `webflow` or `wordpress`
3. **Publish status** — `draft`, `publish`, or `schedule` (schedule requires an ISO date, e.g. `2026-08-15T09:00:00`)
4. **Optional** — collection/category, featured image, author override, tags, custom URL slug

## Prerequisites (gate check)

- Content must have Phase 7 (Reviewer) approval — composite score >= 7.0 — AND Phase 8 (Output Manager) complete
- Content scoring below 5.0 is flagged for human review and cannot be auto-published

## Execute

Follow `skills/cf-publish/SKILL.md` in full:
connector verification → load & validate → platform formatting → preview →
AI disclosure & provenance check (EU AI Act Article 50, applicable from 2 Aug 2026) →
publish/schedule/draft → post-publish verification → tracking update.
If no CMS connector is available, use the skill's HTML export fallback.

To set up a missing connector: `/contentforge:cf-connect webflow` or `/contentforge:cf-connect wordpress`.

## After publishing

Ask: "Would you like me to:
- Create social media posts to promote this? (`/contentforge:social-adapt`)
- Publish to another platform?
- Set up rank monitoring for the target keywords? (`/digital-marketing-pro:rank-monitor` — requires the Digital Marketing Pro plugin)
- Schedule the next content piece? (`/contentforge:cf-calendar`)"
