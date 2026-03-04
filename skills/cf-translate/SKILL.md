---
name: cf-translate
description: Translate content into 15+ languages while preserving brand voice, citations, and SEO — with literal, adapted, or transcreated localization levels
argument-hint: "[target-language]"
---

# Content Translation — Multilingual Publishing

Translate publication-ready ContentForge content into 15+ languages while preserving brand voice integrity, citation accuracy, and SEO optimization. Three localization levels let you control the depth of cultural adaptation.

## When to Use

Use `/cf-translate` when you need:
- **Translated content** for international markets (15+ languages)
- **Brand-consistent multilingual content** that matches your source voice in the target language
- **SEO-localized content** with keywords adapted for target market search behavior
- **Citation-safe translations** where URLs, source references, and inline citations remain intact
- **Cultural adaptation** beyond word-for-word translation (adapted or transcreated levels)

**Prerequisite:** Content must be produced (or imported) through the ContentForge pipeline first. Raw untreated content should go through `/contentforge` before translation.

## Supported Languages

| Code | Language | Direction | Notes |
|------|----------|-----------|-------|
| `es` | Spanish | LTR | Spain + Latin America variants |
| `fr` | French | LTR | France + Canadian French |
| `de` | German | LTR | Compound word handling |
| `pt` | Portuguese | LTR | Brazil + Portugal variants |
| `it` | Italian | LTR | |
| `nl` | Dutch | LTR | |
| `ja` | Japanese | LTR | Honorifics and formality levels |
| `zh` | Chinese (Simplified) | LTR | Simplified by default, Traditional on request |
| `ko` | Korean | LTR | Honorific levels mapped to brand formality |
| `ar` | Arabic | RTL | Right-to-left layout considerations |
| `hi` | Hindi | LTR | Devanagari script handling |
| `ru` | Russian | LTR | |
| `pl` | Polish | LTR | |
| `tr` | Turkish | LTR | |
| `vi` | Vietnamese | LTR | Diacritics preservation |

## Localization Levels

### Literal (Level 1)
**Word-for-word structural translation.** Preserves the exact document structure, sentence order, and paragraph boundaries. Translates meaning accurately but does not adapt cultural references, humor, or idiomatic expressions.

**Best for:** Technical documentation, legal disclaimers, regulatory content, data-heavy research papers.

### Adapted (Level 2) — Recommended
**Cultural adaptation with structural fidelity.** Adjusts cultural references (dates, currencies, idioms, humor) to resonate in the target market while preserving the original content structure and argument flow.

**Best for:** Articles, blog posts, whitepapers, marketing content for established global brands.

### Transcreated (Level 3)
**Reimagined for the target market.** Preserves the core message and intent but rebuilds the content to feel native in the target language. May restructure sections, replace examples, and adjust tone for maximum local impact.

**Best for:** Advertising copy, brand storytelling, thought leadership targeting specific regional audiences.

## Required Inputs

**Minimum Required:**
- **Source Content** -- Google Drive URL, file ID, or local .docx path (must be ContentForge output)
- **Target Language** -- Language code from the supported list (e.g., `es`, `fr`, `de`)
- **Brand** -- Brand profile name (must exist, source language profile required)

**Optional:**
- **Localization Level** -- `literal`, `adapted`, or `transcreated` (defaults to `adapted`)
- **Regional Variant** -- Specify when multiple variants exist (e.g., `es-latam`, `pt-br`, `fr-ca`)
- **Target Keywords** -- Override SEO keywords for target market (auto-researched if not provided)
- **Glossary Override** -- Brand-specific term translations that override defaults

## How to Use

### Interactive Mode
```
/cf-translate
```
**Prompts you for:**
1. Source content (URL or file path)
2. Target language (select from 15 options)
3. Brand profile
4. Localization level (literal / adapted / transcreated)
5. Regional variant (if applicable)

### Quick Mode
```
/cf-translate "https://drive.google.com/file/d/ABC123" --lang=es --brand=AcmeMed --level=adapted
```

### Multi-Language Batch
```
/cf-translate "https://drive.google.com/file/d/ABC123" --lang=es,fr,de,pt --brand=AcmeMed --level=adapted
```
Queues translations for all specified languages and processes them sequentially.

## What Happens

### Phase 1: Source Analysis (1-2 minutes)
- Loads source content and brand profile
- Identifies content type, word count, citation count, SEO keywords
- Detects source language (auto-detected or confirmed)
- **Quality Gate:** Source must be ContentForge output with quality score >= 7.0

### Phase 2: Element Classification (1-2 minutes)
- Separates content into translatable and immutable elements
- **Translatable:** Body text, headings, meta tags, alt text, CTAs
- **Immutable:** Citation URLs, DOIs, proper nouns (configurable), brand names, code snippets, email addresses, phone numbers
- Creates element map with translation instructions per element
- **Quality Gate:** All elements classified, immutable list confirmed

### Phase 3: Translation Execution (3-5 minutes)
- Translator Agent (11-translator) processes content section by section
- Applies localization level rules (literal / adapted / transcreated)
- Uses DeepL MCP if available (optional) -- falls back to built-in translation
- Preserves document structure, heading hierarchy, and formatting
- **Quality Gate:** All translatable elements processed, document structure intact

### Phase 4: Brand Voice Mapping (2-3 minutes)
- Loads brand voice mapping from `config/multilingual-patterns.json`
- Maps source voice characteristics to target language equivalents
  - Example: "authoritative" in English maps to "formal, datos primero" in Spanish
- Applies target language formality defaults
- Adjusts personality markers for cultural appropriateness
- **Quality Gate:** Brand voice rating >= 8/10 in target language

### Phase 5: Citation Preservation Check (1 minute)
- Verifies all citation URLs remain unchanged
- Translates article and book titles in bibliography (preserving original in brackets)
- Confirms inline citation formatting matches source pattern
- Verifies DOIs, ISBNs, and reference identifiers are untouched
- **Quality Gate:** Zero citation URL changes, zero broken references

### Phase 6: SEO Adaptation (2-3 minutes)
- Researches target market keywords (or uses provided overrides)
- Translates meta title (<= 60 chars in target language)
- Translates meta description (<= 155 chars in target language)
- Adjusts keyword density for target language norms
- Generates localized URL slug
- **Quality Gate:** Meta tags within char limits, keyword density within target range

### Phase 7: Target Language Humanization (2-3 minutes)
- Runs Humanizer Agent for target language fluency
- Removes AI telltale phrases specific to target language (loaded from `config/multilingual-patterns.json`)
- Checks sentence variety (burstiness) against target language norms
- Ensures natural reading flow for native speakers
- **Quality Gate:** Target language burstiness >= 0.7, zero AI patterns in target language

### Phase 8: Quality Verification (1-2 minutes)
- Readability check calibrated for target language (grade level equivalents)
- Brand voice consistency rating (target: >= 8/10)
- Citation integrity confirmation (zero errors)
- SEO keyword density within +/- 0.5% of target
- Back-translation spot check (3-5 key sentences translated back to source for meaning verification)
- **Quality Gate:** All checks pass, composite translation score >= 8.0/10

### Phase 9: Output (1 minute)
- Generates translated .docx with proper formatting
- Uploads to Google Drive (`ContentForge Output/[Brand]/[Language]/[Title]_[lang]_v1.0.docx`)
- Creates translation report with quality metrics
- Updates tracking sheet with translation entry

## Output

**Translated Content Package:**

```
Translation Complete: "AI in Healthcare: 2026 Trends" --> Spanish (es)

Processing Time: 16 minutes
Translation Score: 8.8/10

Localization Level: Adapted
Regional Variant: es (Spain, neutral)

Quality Metrics:
- Brand Voice Consistency: 9.0/10 (authoritative mapped to "formal, datos primero")
- Citation Integrity: 100% (14 URLs unchanged, 14 titles translated)
- SEO Adaptation: 8.5/10 (meta tags localized, keyword density 2.0%)
- Readability: 8.8/10 (Grade 11 equivalent for Spanish)
- Humanization: 9.0/10 (burstiness 0.74, zero AI patterns in Spanish)

Content Stats:
- Source Word Count: 1,947
- Translated Word Count: 2,134 (Spanish typically +10% vs English)
- Citations Preserved: 14/14 (100%)
- Immutable Elements: 23 (all preserved)
- Back-Translation Check: 5/5 sentences verified

Output Location:
Google Drive: ContentForge Output/AcmeMed/es/AI-in-Healthcare-2026-Trends_es_v1.0.docx

Translation Report:
Google Drive: ContentForge Output/AcmeMed/es/AI-in-Healthcare-2026-Trends_es_translation-report.json
```

## Brand Voice Mapping Examples

The Translator Agent uses `config/multilingual-patterns.json` to map voice characteristics:

| Source Voice (EN) | Spanish (es) | French (fr) | German (de) | Japanese (ja) |
|-------------------|-------------|-------------|-------------|---------------|
| Authoritative | Formal, datos primero | Assertif, ton expert | Sachlich, faktenbasiert | Formal keigo, data-driven |
| Conversational | Cercano, tuteo | Decontracte, tutoiement | Locker, Du-Form | Casual desu/masu |
| Technical | Preciso, terminologia exacta | Technique, jargon specialise | Fachsprachlich, Komposita | Senmon-teki, katakana loanwords |
| Witty | Ingenioso, juegos de palabras | Spirituel, jeux de mots | Geistreich, Wortspiel | Witty is rare; use light irony |

## Immutable Element Handling

These elements are **never** translated:

| Element Type | Example | Handling |
|-------------|---------|----------|
| Citation URLs | `https://doi.org/10.1234` | Preserved exactly |
| Brand names | "ContentForge", "AcmeMed" | Kept in original form |
| Proper nouns (people) | "Dr. Sarah Chen" | Kept unless transcreated level |
| Code snippets | `config.json` | Never translated |
| Email addresses | `info@acmemed.com` | Preserved exactly |
| Phone numbers | +1-555-0123 | Preserved (format may adapt) |
| Product names | "MedAssist Pro" | Kept in original form |
| DOIs / ISBNs | `10.1038/s41586-024` | Preserved exactly |

## MCP Integrations

### Required
- **Google Drive** -- Content storage, brand profiles, output files

### Optional
- **DeepL** (npx: `@anthropic-ai/deepl-mcp-server`) -- Machine translation baseline. When available, Translator Agent uses DeepL output as a starting point and refines for brand voice, cultural adaptation, and SEO. When unavailable, Translator Agent handles all translation natively.

## Processing Times

| Localization Level | Typical Time | Notes |
|-------------------|-------------|-------|
| Literal | 10-14 min | Fastest, minimal adaptation |
| Adapted | 14-20 min | Recommended, balanced quality |
| Transcreated | 20-30 min | Most thorough, may restructure content |

**Multi-language batch:** Add ~80% of single-language time per additional language (caching effects).

## Limitations

- **Source content must be ContentForge output** (or at minimum, well-structured markdown with citations)
- **RTL languages (Arabic)** require downstream layout adjustments in CMS/publishing tool
- **Transcreation** may change content structure significantly -- review recommended
- **Regional variants** (es-latam vs es-es) affect vocabulary but not pipeline structure
- **DeepL free tier** has character limits -- monitor usage for high-volume batches

## Troubleshooting

### "Source quality score below threshold"
**Cause:** Source content scored < 7.0 in the original pipeline.
**Solution:** Re-run `/contentforge` or `/content-refresh` on the source first.

### "Brand voice mapping not found for [language]"
**Cause:** Target language not configured in `config/multilingual-patterns.json`.
**Solution:** Check supported languages list. If the language is supported but mapping is missing, update the config.

### "Citation count mismatch after translation"
**Cause:** A citation was accidentally merged or split during translation.
**Solution:** Translator Agent will auto-retry the affected section. If persistent, check for unusual citation formats in the source.

### "Meta title exceeds character limit in target language"
**Cause:** Target language is more verbose than English (common for German, Spanish).
**Solution:** Translator Agent auto-shortens while preserving primary keyword. Review the shortened version.

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** -- Produce source content (prerequisite)
- **[/batch-process](../batch-process/SKILL.md)** -- Batch translate multiple pieces
- **[/content-refresh](../content-refresh/SKILL.md)** -- Update source before translating
- **[/cf-social-adapt](../cf-social-adapt/SKILL.md)** -- Adapt translated content for social platforms

---

**Version:** 3.4.0
**Agents:** Translator (11-translator), Humanizer (06.5-humanizer)
**Processing Time:** 10-30 minutes depending on localization level
**Quality Guarantee:** Brand voice >= 8/10, zero citation errors, SEO keywords adapted for target market
