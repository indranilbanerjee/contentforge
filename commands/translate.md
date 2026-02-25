---
description: Translate content into 15+ languages while preserving brand voice, citations, and SEO optimization
argument-hint: "<content source> --language=<code> [--level=literal|adapted|transcreated]"
---

# Translate

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Translate publication-ready ContentForge content into 15+ languages while preserving brand voice integrity, citation accuracy, and SEO optimization. Three localization levels let you control the depth of cultural adaptation — from literal translation to full transcreation.

## Trigger

User runs `/translate` or asks to translate content, localize for a market, or create multilingual versions.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Content source** — the piece to translate, provided as:
   - Google Drive URL
   - Local file path
   - Requirement ID (e.g., `REQ-001`)
   - Pasted content

2. **Target language** — language code:

   | Code | Language | Notes |
   |------|----------|-------|
   | `es` | Spanish | Spain + Latin America variants |
   | `fr` | French | France + Canadian French |
   | `de` | German | Compound word handling |
   | `pt` | Portuguese | Brazil + Portugal variants |
   | `it` | Italian | |
   | `nl` | Dutch | |
   | `ja` | Japanese | Honorifics and formality |
   | `zh` | Chinese (Simplified) | Traditional on request |
   | `ko` | Korean | Formality mapped to brand |
   | `ar` | Arabic | RTL layout handling |
   | `hi` | Hindi | Devanagari script |
   | `ru` | Russian | |
   | `pl` | Polish | |
   | `tr` | Turkish | |
   | `vi` | Vietnamese | Diacritics preservation |

3. **Localization level** (optional, default: adapted):
   - **Literal** — word-for-word structural translation (best for technical docs, legal content)
   - **Adapted** — cultural adaptation with structural fidelity (recommended for most content)
   - **Transcreated** — full creative rewriting for the target culture (best for marketing copy, brand messaging)

4. **Additional context** (optional):
   - Regional variant (e.g., `es-MX` for Mexican Spanish vs. `es-ES` for Spain)
   - Brand profile for multilingual voice mapping
   - Target market SEO keywords in the target language
   - Multiple languages in one pass (e.g., `--language=es,fr,de`)

## Translation Process

### 1. Element Classification
Separate content into:
- **Translatable text** — body copy, headings, meta descriptions
- **Immutable elements** — URLs, citations, source references, proper nouns, brand names, technical terms, code snippets

### 2. Translation

**If ~~translation tools are connected (DeepL):**
- Use DeepL for initial translation, then apply brand voice refinement

**Without translation tools:**
- Translate using contextual understanding and cultural knowledge
- Cross-reference key terms against established translations

Apply:
- Grammar and syntax native to the target language
- Cultural references adapted for the target market (dates, currencies, idioms, humor)
- Formality level matched to brand settings for the target language

### 3. Brand Voice Mapping

Using `config/multilingual-patterns.json`:
- Map brand voice attributes to target language conventions
- Adjust formality (some languages have formal/informal distinction: French vous/tu, German Sie/du, Japanese keigo)
- Preserve brand personality while respecting cultural norms

### 4. SEO Localization
- Translate and adapt meta title and description
- Research target-market keywords (compound words in German, accent variations in Spanish)
- Adjust internal linking for multilingual site structure
- Preserve hreflang annotation recommendations

### 5. Citation Preservation
- Keep all source URLs unchanged
- Translate citation descriptions if they appear in running text
- Note language mismatches (English source cited in Spanish article) with appropriate formatting

### 6. Quality Check
- Readability score in target language (using language-specific benchmarks)
- Brand voice rating (8+/10 required)
- Citation integrity verification
- Character/word count comparison with source
- No untranslated passages remaining

## Output

The translated piece includes:
- Full translated content with preserved citations
- Translated SEO meta package (title, description)
- Quality metrics compared to source:
  | Metric | Source | Translation |
  |--------|--------|-------------|
  | Word count | X | Y |
  | Reading time | X min | Y min |
  | Brand voice score | X/10 | Y/10 |
  | Citations preserved | X | X (same) |
- Translation notes (cultural adaptations made, terms kept in original language, regional choices)

## After Translation

Ask: "Would you like me to:
- Translate into additional languages?
- Publish the translated version? (`/publish`)
- Create social media posts in the translated language? (`/social-adapt`)
- Review a specific section for cultural accuracy?
- Generate a side-by-side comparison of source and translation?
- Set up multilingual content calendar for ongoing production? (`/calendar`)"
