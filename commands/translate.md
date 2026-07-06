---
description: Translate content into 15+ languages while preserving brand voice, citations, and SEO optimization
argument-hint: "<content source> --language=<code> [--level=literal|adapted|transcreated]"
---

# Translate

This command is a thin wrapper. The complete translation procedure lives in
[`skills/cf-translate/SKILL.md`](../skills/cf-translate/SKILL.md) — read that file and execute
it end to end. Do not improvise a different flow from this wrapper.

## Trigger

User runs `/contentforge:translate` or asks to translate content, localize for a market, or
create multilingual versions.

## Gather inputs

If not provided in the arguments, ask before proceeding:

1. **Content source** — Google Drive URL, local file path, requirement ID (e.g., `REQ-001`), or pasted content
2. **Target language** — a language code from the supported list in `skills/cf-translate/SKILL.md` (es, fr, de, pt, it, nl, ja, zh, ko, ar, hi, ru, pl, tr, vi). Multiple languages allowed: `--language=es,fr,de`
3. **Localization level** (optional, default `adapted`) — `literal` | `adapted` | `transcreated`
4. **Optional** — regional variant (e.g., `es-MX` vs `es-ES`), brand profile for multilingual voice mapping, target-market SEO keywords

## Execute

Follow `skills/cf-translate/SKILL.md` in full:
source analysis → element classification (translatable vs immutable) → translation →
brand voice mapping via `config/multilingual-patterns.json` → citation preservation
(URLs/DOIs never change) → SEO localization → target-language humanization →
quality verification → output via the brand's tracking backend.

## After translation

Ask: "Would you like me to:
- Translate into additional languages?
- Publish the translated version? (`/contentforge:publish`)
- Create social media posts in the translated language? (`/contentforge:social-adapt`)
- Review a specific section for cultural accuracy?
- Generate a side-by-side comparison of source and translation?"
