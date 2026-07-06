---
description: Repurpose articles into platform-specific social media posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads
argument-hint: "<article source> [platforms: all|linkedin|twitter|instagram|facebook|threads]"
---

# Social Adapt

This command is a thin wrapper. The complete adaptation procedure lives in
[`skills/cf-social-adapt/SKILL.md`](../skills/cf-social-adapt/SKILL.md) — read that file and
execute it end to end. Do not improvise a different flow from this wrapper.

## Trigger

User runs `/contentforge:social-adapt` or asks to repurpose content for social media, create
social posts from an article, or promote content on social platforms.

## Gather inputs

If not provided in the arguments, ask before proceeding:

1. **Source content** — Google Drive URL, local file path, requirement ID (e.g., `REQ-001`), or pasted article text
2. **Platforms** — `all` (default) or a comma-separated subset of the platforms defined in `config/social-platform-specs.json`
3. **Optional** — posts per platform (default 3, max 10), brand profile, campaign hashtag, published article URL, available image assets, tone override

## Platform rules — single source of truth

Character limits, hashtag counts, and format rules come from
`config/social-platform-specs.json`. Read that file at run time; never use remembered
limits or any table in this wrapper.

## Execute

Follow `skills/cf-social-adapt/SKILL.md` in full:
load source → extract shareworthy moments → apply platform specs from config →
generate posts (hook, body, CTA, hashtags, image spec, posting time) →
quality check (limit compliance, self-contained, CTA present, brand voice, no duplicates).

## After adaptation

Ask: "Would you like me to:
- Generate more posts for specific platforms?
- Adapt another article?
- Create A/B variants for the top-performing hooks? (`/contentforge:cf-variants`)
- Translate these posts for other markets? (`/contentforge:translate`)"
