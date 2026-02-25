# Utility: Translation Manager

**Purpose:** Orchestrate the translation workflow from source analysis through quality verification, managing element classification, brand voice mapping, citation preservation, and SEO adaptation across 15+ languages.

---

## How It Works

The Translation Manager coordinates a 5-stage pipeline that ensures translated content matches source quality while reading as native target-language content.

### Stage 1: Source Analysis
- Load source content from Google Drive or local path
- Verify source is ContentForge output (quality score >= 7.0)
- Extract metadata: content type, word count, citation count, SEO keywords, brand profile
- Determine translation complexity (word count x localization level x language difficulty)
- Estimate processing time

### Stage 2: Element Classification
- Scan source content and tag every element as translatable or immutable
- Build Element Registry linking each element to its translation instruction
- Immutable elements: citation URLs, DOIs, ISBNs, brand names, product names, proper nouns, code snippets, email addresses, phone numbers
- Translatable elements: body text, headings, meta tags, alt text, CTAs, bibliography titles
- Output: ElementRegistry object with counts and validation

### Stage 3: Translation Execution
- Route to Translator Agent (11-translator) with source content, target language, and localization level
- If DeepL MCP is connected: use as baseline, then refine for brand voice and cultural adaptation
- If DeepL is not available: Translator Agent handles all translation natively
- Process section by section preserving document structure
- Apply brand voice mapping from `config/multilingual-patterns.json`

### Stage 4: Brand Voice Application
- Load brand voice mapping for target language
- Verify translated content matches source brand personality in target language equivalents
- Run target-language Humanizer pass to remove AI telltale phrases specific to the target language
- Score brand voice consistency (target: >= 8/10)

### Stage 5: Quality Verification
- Readability check calibrated for target language
- Citation integrity verification (zero tolerance for URL changes)
- SEO keyword density check (within +/- 0.5% of target)
- Meta tag character limit verification
- Back-translation spot check (3-5 key sentences)
- Composite translation score calculation

---

## Data Structures

### TranslationRequest

```python
class TranslationRequest:
    """Input to the Translation Manager."""

    # Required
    source_content_url: str          # Google Drive URL or local file path
    target_language: str             # Language code (es, fr, de, pt, it, nl, ja, zh, ko, ar, hi, ru, pl, tr, vi)
    brand: str                       # Brand profile name

    # Optional (with defaults)
    localization_level: str = "adapted"  # literal | adapted | transcreated
    regional_variant: str = None     # e.g., "es-latam", "pt-br", "fr-ca"
    target_keywords: list = None     # Override SEO keywords for target market
    glossary_override: dict = None   # Brand-specific term translation overrides

    # Computed during processing
    source_language: str = "en"      # Auto-detected or confirmed
    content_type: str = None         # article, blog, whitepaper, faq, research_paper
    source_word_count: int = 0
    source_citation_count: int = 0
    source_quality_score: float = 0.0
    estimated_time_minutes: int = 0
```

### TranslationResponse

```python
class TranslationResponse:
    """Output from the Translation Manager."""

    # Content
    translated_content: str          # Full translated content (markdown)
    translated_word_count: int       # Target language word count
    word_count_delta_pct: float      # % change from source (e.g., +12.5% for Spanish)

    # Quality Metrics
    composite_score: float           # Overall translation score (1-10)
    brand_voice_rating: float        # Brand voice consistency (1-10)
    readability_score: float         # Target language readability metric value
    readability_grade_equivalent: str  # Grade level equivalent description
    burstiness_score: float          # Sentence variety (target: >= 0.7)
    ai_patterns_detected: int        # Target language AI patterns found (target: 0)

    # Citation Integrity
    source_citation_count: int       # Citations in source
    target_citation_count: int       # Citations in target (must match source)
    urls_preserved: int              # Count of URLs unchanged
    url_errors: int                  # Count of URL mismatches (must be 0)
    bibliography_titles_translated: int  # Titles translated with originals in brackets

    # SEO Metrics
    meta_title: str                  # Translated meta title
    meta_title_chars: int            # Character count
    meta_description: str            # Translated meta description
    meta_description_chars: int      # Character count
    url_slug: str                    # Localized URL slug
    primary_keyword_density: float   # Keyword density in target (%)
    keyword_density_delta: float     # Variance from source density

    # Back-Translation
    back_translation_checks: int     # Number of sentences checked
    back_translation_passed: int     # Number verified correct

    # Cultural Adaptations
    adaptations_applied: list        # List of cultural adaptations made
    # Each entry: {"element": str, "source": str, "target": str, "reason": str}

    # Metadata
    processing_time_minutes: int
    localization_level: str
    regional_variant: str
    deepl_used: bool                 # Whether DeepL MCP was available
    timestamp: str                   # ISO 8601 timestamp

    # Output Locations
    content_drive_url: str           # Google Drive URL for translated content
    report_drive_url: str            # Google Drive URL for translation report
```

### ElementRegistry

```python
class ElementRegistry:
    """Tracks all elements and their translation status."""

    immutable_elements: list
    # Each entry: {
    #   "id": "IMM-001",
    #   "type": "url" | "brand_name" | "proper_noun" | "code" | "email" | "phone" | "doi" | "isbn",
    #   "content": str,
    #   "location": str,  # e.g., "Section 2, para 3"
    #   "occurrences": int
    # }

    translatable_elements: list
    # Each entry: {
    #   "id": "TRN-001",
    #   "type": "heading" | "body" | "meta" | "alt_text" | "cta" | "bibliography_title",
    #   "content_preview": str,  # First 100 chars
    #   "word_count": int,
    #   "instruction": str  # "TRANSLATE", "TRANSLATE (max 60 chars)", "TRANSLATE + [original]"
    # }

    total_immutable: int
    total_translatable: int
    immutable_preserved: int         # Post-translation verification count
    immutable_errors: int            # Must be 0
```

---

## Immutable Element Handling

### Detection Rules

| Element Type | Detection Pattern | Action |
|-------------|-------------------|--------|
| URLs | `https?://[^\s]+` | Tag as IMM, preserve exactly |
| DOIs | `10\.\d{4,}/[^\s]+` | Tag as IMM, preserve exactly |
| ISBNs | `978-\d-\d{2,}-\d{4,}-\d` | Tag as IMM, preserve exactly |
| Brand names | From brand profile `terminology.brand_names[]` | Tag as IMM, preserve exactly |
| Product names | From brand profile `terminology.product_names[]` | Tag as IMM, preserve exactly |
| Email addresses | `[\w.-]+@[\w.-]+\.\w+` | Tag as IMM, preserve exactly |
| Phone numbers | `\+?\d[\d\s\-().]+` | Tag as IMM, preserve (format may adapt) |
| Code snippets | Content between backticks or in code blocks | Tag as IMM, never translate |
| Proper nouns | Named entities (people, places) | Tag as IMM for literal/adapted; review for transcreated |

### Verification After Translation

```python
def verify_immutable_elements(registry, translated_content):
    """Post-translation check: all immutable elements must be unchanged."""

    errors = []

    for element in registry.immutable_elements:
        if element["content"] not in translated_content:
            errors.append({
                "id": element["id"],
                "type": element["type"],
                "expected": element["content"],
                "status": "MISSING"
            })

    registry.immutable_preserved = registry.total_immutable - len(errors)
    registry.immutable_errors = len(errors)

    return errors  # Must be empty for quality gate pass
```

---

## Brand Voice Consistency

### Mapping Process

```
Source brand profile --> multilingual-patterns.json --> Target voice characteristics
```

1. Read source brand personality traits (e.g., "authoritative", "data-driven")
2. Look up target language equivalents in `config/multilingual-patterns.json` under `brand_voice_mapping`
3. Apply target characteristics during translation
4. Score consistency after translation (5 criteria, averaged)

### Scoring Criteria

| Criterion | Weight | What It Measures |
|-----------|--------|-----------------|
| Register consistency | 25% | Correct formality level throughout |
| Data-leading style | 20% | Statistics placed prominently (if data-driven brand) |
| Definitive assertions | 20% | No hedging where source is confident |
| Terminology consistency | 20% | Brand terms and industry vocabulary uniform |
| Tone match | 15% | Overall feel matches source personality |

**Threshold:** >= 8.0/10 to pass quality gate.

---

## SEO Adaptation

### Keyword Translation Strategy

Keyword translation is NOT a direct word-for-word process. The correct approach:

1. **Identify source keywords** from the ContentForge SEO phase output
2. **Research target market search terms** -- what do people in the target market actually search for?
3. **Select best match** -- may be a direct translation, a local equivalent, or a different phrasing entirely
4. **Verify density** -- keyword density should be within +/- 0.5% of the source density target

### Meta Tag Constraints

| Language | Meta Title Max | Meta Description Max | Notes |
|----------|---------------|---------------------|-------|
| English | 60 chars | 155 chars | Baseline |
| Spanish | 60 chars | 155 chars | Typically 10-15% longer text |
| French | 60 chars | 155 chars | Typically 15-20% longer text |
| German | 60 chars | 155 chars | Compound words; 20-30% longer text |
| Japanese | 32 chars | 120 chars | Full-width characters |
| Chinese | 30 chars | 120 chars | Fewer characters, more meaning per char |
| Korean | 32 chars | 120 chars | Syllabic blocks |
| Arabic | 60 chars | 155 chars | Similar length to English |

**When translations exceed limits:** Shorten by removing secondary qualifiers, not by removing keywords or brand names.

---

## DeepL Integration (Optional)

### When Available

```
Source text --> DeepL API (section by section) --> Raw translation
Raw translation --> Translator Agent refinement --> Brand-voiced translation
```

**DeepL configuration:**
- Formality: Match brand profile (formal or informal)
- Preserve formatting: Enabled
- Tag handling: XML (to protect immutable elements marked with tags)
- Split sentences: Disabled (preserve paragraph structure)

### When Not Available

```
Source text --> Translator Agent (native translation) --> Brand-voiced translation
```

The Translator Agent handles all translation natively without quality loss. DeepL accelerates processing by ~30% but is not required for output quality.

### Fallback Strategy

- Check DeepL MCP connection at pipeline start
- If connected: Use DeepL baseline + agent refinement
- If not connected: Agent handles end-to-end
- Log which approach was used in TranslationResponse (`deepl_used` field)
- Quality gates are identical regardless of approach

---

## Usage

### Invoked By

The Translation Manager is called by the `/cf-translate` skill:

```
/cf-translate --> Translation Manager --> Translator Agent (11-translator)
                                      --> Humanizer Agent (06.5-humanizer)
                                      --> Google Drive (output)
```

### Processing Flow

```
1. /cf-translate receives user input
2. Translation Manager validates inputs and loads source content
3. Element Classification scans and tags all elements
4. Translator Agent processes content section by section
5. Brand Voice Mapping applies target language personality
6. Humanizer runs target-language AI pattern removal
7. Quality Verification checks all gates
8. Output Manager generates .docx and uploads to Drive
9. Translation Report generated and stored alongside content
```

### Multi-Language Batch

When multiple target languages are specified:

```
/cf-translate source.docx --lang=es,fr,de

Translation Manager:
  1. Source analysis (once, shared across all languages)
  2. Element classification (once, shared)
  3. Translation (per language, sequential):
     3a. es: Translate --> Voice map --> Humanize --> Verify
     3b. fr: Translate --> Voice map --> Humanize --> Verify
     3c. de: Translate --> Voice map --> Humanize --> Verify
  4. Output (per language)
```

**Caching benefit:** Source analysis and element classification happen once. Each additional language adds ~80% of single-language time.

---

## Benefits

1. **Zero citation errors** -- Immutable element handling guarantees 100% URL preservation
2. **Brand consistency across languages** -- Voice mapping ensures personality translates, not just words
3. **SEO-ready translations** -- Keywords researched for target market, not just word-for-word translated
4. **Cultural sensitivity** -- Adapted and transcreated levels prevent cultural missteps
5. **Quality metrics** -- Every translation gets a composite score with dimension breakdown
6. **DeepL flexibility** -- Works with or without the DeepL MCP connection
7. **Scalable** -- Multi-language batch processing with shared analysis

---

## Implementation Checklist

- [x] Element classification engine (immutable vs translatable tagging)
- [x] Brand voice mapping loader (reads from `config/multilingual-patterns.json`)
- [x] Citation URL verification (pre/post comparison, zero tolerance)
- [x] SEO keyword adaptation logic (research, not just translate)
- [x] Meta tag character limit enforcement (per-language limits)
- [x] Target language AI pattern detection (per-language phrase lists)
- [x] Readability scoring per language (metric selection from config)
- [x] Back-translation spot check (3-5 sentence sample)
- [x] DeepL MCP integration with graceful fallback
- [x] TranslationRequest / TranslationResponse data structures
- [x] ElementRegistry with post-translation verification
- [x] Multi-language batch orchestration with shared source analysis
- [x] Google Drive output organization (`[Brand]/[Language]/` structure)
- [x] Translation report generation (JSON + human-readable)

---

## Error Handling

### Source Quality Below Threshold
```
Error: Source quality score 5.8 < 7.0 minimum
Action: Return error to user, recommend /contentforge or /content-refresh first
```

### Unsupported Language
```
Error: Language code "sv" not in supported_languages
Action: Return error listing supported languages
```

### Citation Count Mismatch
```
Error: Source has 14 citations, target has 13
Action: Translator Agent retries affected section (max 2 retries)
Escalation: If persistent, flag for human review with specific missing citation
```

### Meta Tag Overflow
```
Error: German meta title "Kunstliche Intelligenz im Gesundheitswesen: Trends 2026 | AcmeMed" (69 chars) > 60 limit
Action: Auto-shorten to "KI im Gesundheitswesen: Trends 2026 | AcmeMed" (47 chars)
Rule: Remove secondary qualifiers first, preserve keyword + brand name
```

### DeepL Rate Limit
```
Error: DeepL API rate limit reached
Action: Switch to native translation for remaining sections
Note: Log in TranslationResponse, quality unaffected
```

---

## Version History

- **v2.1.0**: Initial implementation with 15 languages, 3 localization levels, DeepL integration
- Future: Add translation memory for repeated brand content, glossary management UI, translation comparison dashboard

---

**This utility is the backbone of multilingual content operations** -- reliable element handling and brand voice mapping are what separate machine translation from publication-ready localized content.
