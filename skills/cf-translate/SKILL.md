---
name: cf-translate
description: "Translate publication-ready ContentForge content into any of 15 languages at three localization levels (literal, adapted, transcreated) — preserving brand voice, keeping citation URLs and DOIs untouched, and adapting SEO keyword placements for the target market — delivered as a translated .docx plus a quality report via the brand's tracking backend. Triggers on \"/contentforge:cf-translate\", \"translate this article to Spanish\", \"localize this for the German market\", \"make a French version of this post\", \"transcreate this for Japan\". Dispatches the contentforge:translator agent, maps voice via config/multilingual-patterns.json, and runs a target-language humanizer pass. Requires pipeline output scoring >=7.0 and a brand profile; pairs with /contentforge:create-content upstream."
disable-model-invocation: true
argument-hint: "[target-language]"
effort: high
---

# Content Translation — Multilingual Publishing

Translate publication-ready ContentForge content into 15 languages while preserving brand voice integrity, citation accuracy, and SEO optimization. Three localization levels let you control the depth of cultural adaptation.

## When to Use

Use `/contentforge:cf-translate` when you need:
- **Translated content** for international markets (15 languages)
- **Brand-consistent multilingual content** that matches your source voice in the target language
- **SEO-localized content** with keywords adapted for target market search behavior
- **Citation-safe translations** where URLs, source references, and inline citations remain intact
- **Cultural adaptation** beyond word-for-word translation (adapted or transcreated levels)

**Prerequisite:** Content must be produced (or imported) through the ContentForge pipeline first. Raw untreated content should go through `/contentforge:create-content` before translation.

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
/contentforge:cf-translate
```
**Prompts you for:**
1. Source content (URL or file path)
2. Target language (select from 15 options)
3. Brand profile
4. Localization level (literal / adapted / transcreated)
5. Regional variant (if applicable)

### Quick Mode
```
/contentforge:cf-translate "https://drive.google.com/file/d/ABC123" --lang=es --brand=AcmeMed --level=adapted
```

### Multi-Language Batch
```
/contentforge:cf-translate "https://drive.google.com/file/d/ABC123" --lang=es,fr,de,pt --brand=AcmeMed --level=adapted
```
Queues translations for all specified languages and processes them sequentially.

## What Happens

### Step 1: Source Analysis
- Loads source content and brand profile
- Identifies content type, word count, citation count, SEO keywords
- Detects source language (auto-detected or confirmed)
- **Quality Gate:** Source must be ContentForge output with quality score >= 7.0

### Step 2: Element Classification
- Separates content into translatable and immutable elements
- **Translatable:** Body text, headings, meta tags, alt text, CTAs
- **Immutable:** Citation URLs, DOIs, proper nouns (configurable), brand names, code snippets, email addresses, phone numbers
- Creates element map with translation instructions per element
- **Quality Gate:** All elements classified, immutable list confirmed

### Step 3: Translation Execution

**Dispatch the agent — do not translate inline.** Call `Task` with `subagent_type: contentforge:translator`, the same way the main orchestrator dispatches its pipeline phases. The Task prompt carries only the source-content path, the brand-profile path, the element map from Step 2, the target language(s) and the localization level. The agent `Read`s the content itself — never inline a full article into the Task prompt. `agents/11-translator.md` owns the translation rules, brand-voice mapping, citation preservation and the per-language quality gate; this skill owns argument parsing, source validation and result presentation.

- Translator Agent (11-translator) processes content section by section
- Applies localization level rules (literal / adapted / transcreated)
- Uses DeepL MCP if available (optional) -- falls back to built-in translation
- Preserves document structure, heading hierarchy, and formatting
- **Quality Gate:** All translatable elements processed, document structure intact

### Step 4: Brand Voice Mapping
- Loads brand voice mapping from `config/multilingual-patterns.json`
- Maps source voice characteristics to target language equivalents
  - Example: "authoritative" in English maps to "formal, datos primero" in Spanish
- Applies target language formality defaults
- Adjusts personality markers for cultural appropriateness
- **Quality Gate:** Brand voice rating >= 8/10 in target language

### Step 5: Citation Preservation Check
- Verifies all citation URLs remain unchanged
- Translates article and book titles in bibliography (preserving original in brackets)
- Confirms inline citation formatting matches source pattern
- Verifies DOIs, ISBNs, and reference identifiers are untouched
- **Quality Gate:** Zero citation URL changes, zero broken references

### Step 6: SEO Adaptation
- Researches target market keywords (or uses provided overrides)
- Translates meta title (<= 60 chars in target language)
- Translates meta description (<= 155 chars in target language)
- Monitors keyword density for target language norms (advisory only — never pad copy to hit a number)
- Generates localized URL slug
- **Quality Gate:** Meta tags within char limits, and the source's keyword **placements** (title, H1, first 100 words, 2-3 H2s, conclusion) preserved in the target language. Density is reported, not gated.

### Step 7: Target Language Humanization
- Runs Humanizer Agent for target language fluency
- Removes AI telltale phrases specific to target language (loaded from `config/multilingual-patterns.json`)
- Checks sentence variety (burstiness) against target language norms
- Ensures natural reading flow for native speakers
- **Quality Gate:** `ai_signal_score` <= 0.3 for the target language (burstiness is measured and reported but advisory — no minimum to hit, matching the Phase 6.5 humanizer)

### Step 8: Quality Verification
- Readability check calibrated for target language (grade level equivalents)
- Brand voice consistency rating (target: >= 8/10)
- Citation integrity confirmation (zero errors)
- SEO keyword placements preserved (density reported as advisory drift, not gated)
- Back-translation spot check (3-5 key sentences translated back to source for meaning verification)
- **Quality Gate:** All checks pass, composite translation score >= 8.0/10

### Step 9: Output
- Generates translated .docx with proper formatting
- Delivers via the brand's tracking backend (`tracking.backend` in the brand profile): Google Drive folder, Airtable attachment, or local filesystem (`~/Documents/ContentForge/{brand}/{type}/{YYYY-MM}/{slug}_{lang}.docx`)
- Creates translation report with quality metrics
- Adds a translation entry to the tracking backend

## Output

**Translated Content Package — SYNTHETIC EXAMPLE, fabricated for illustration:**

```
Translation Complete: "AI in Healthcare: 2026 Trends" --> Spanish (es)

Processing Time: 16 minutes
Translation Score: 8.8/10

Localization Level: Adapted
Regional Variant: es (Spain, neutral)

Quality Metrics:
- Brand Voice Consistency: 9.0/10 (authoritative mapped to "formal, datos primero")
- Citation Integrity: 100% (14 URLs unchanged, 14 titles translated)
- SEO Adaptation: 8.5/10 (meta tags localized, all keyword placements preserved; density 2.0% — advisory)
- Readability: 8.8/10 (Grade 11 equivalent for Spanish)
- Humanization: 9.0/10 (burstiness 0.74, ai_signal_score 0.18)

Content Stats:
- Source Word Count: 1,947
- Translated Word Count: 2,134 (Spanish typically +10% vs English)
- Citations Preserved: 14/14 (100%)
- Immutable Elements: 23 (all preserved)
- Back-Translation Check: 5/5 sentences verified

Output Location:
Google Drive: My Drive/ContentForge Output/AcmeMed/article/2026-07/AI-in-Healthcare-2026-Trends_es_v1.0.docx

Translation Report:
Google Drive: My Drive/ContentForge Output/AcmeMed/article/2026-07/AI-in-Healthcare-2026-Trends_es_translation-report.json
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

### Optional (none required)
- **Google Drive** -- Only needed if the brand's tracking backend is Google Sheets + Drive, or when running in Cowork (sandbox persistence). Local and Airtable backends work without it.
- **DeepL** -- Machine translation baseline. If a DeepL MCP server is configured in `.mcp.json`, the Translator Agent uses its output as a starting point and refines for brand voice, cultural adaptation, and SEO. Before recommending a DeepL MCP package, verify it exists and is maintained on npm (`npm view <package> version`). When unavailable, the Translator Agent handles all translation natively -- this is the default and works fine.

## Relative Effort

Literal is the fastest level; adapted adds cultural-adaptation passes; transcreated is the most thorough and may restructure content. Actual time varies with content length, model speed, and MCP availability — do not promise specific durations.

## Limitations

- **Source content must be ContentForge output** (or at minimum, well-structured markdown with citations)
- **RTL languages (Arabic)** require downstream layout adjustments in CMS/publishing tool
- **Transcreation** may change content structure significantly -- review recommended
- **Regional variants** (es-latam vs es-es) affect vocabulary but not pipeline structure
- **Free tiers of translation connectors** (e.g., DeepL) have character limits -- monitor usage for high-volume batches

## Troubleshooting

### "Brand profile not found"
```
Error: Brand profile "{brand}" not found at
  ~/.claude-marketing/{brand-slug}/Brand-Guidelines/{BrandName}-brand-profile.json
Action: Translation requires a brand profile for voice mapping.
  Run /contentforge:brand-setup "{brand}" first, then retry.
```

### "Source quality score below threshold"
**Cause:** Source content scored < 7.0 in the original pipeline.
**Solution:** Re-run `/contentforge:create-content` or `/contentforge:content-refresh` on the source first.

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

- **[/contentforge:create-content](../../commands/create-content.md)** -- Produce source content (prerequisite)
- **[/contentforge:batch-process](../batch-process/SKILL.md)** -- Batch translate multiple pieces
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** -- Update source before translating
- **[/contentforge:cf-social-adapt](../cf-social-adapt/SKILL.md)** -- Adapt translated content for social platforms

---

**Agents:** Translator (11-translator), Humanizer (06.5-humanizer); pseudocode reference: `utilities/translation-manager.md` (prose doc, not a script)
**Quality Guarantee:** Brand voice >= 8/10, zero citation errors, SEO keywords adapted for target market
