# Brand Cache Manager — ContentForge Utility

## Purpose
Manage brand profile caching to avoid re-processing brand guidelines on every run.Implement hash-based cache invalidation to detect when source documents change.

---

## How It Works

### 1. Brand Profile Structure

Each brand has:
- **Google Drive Folder:** `ContentForge-Knowledge/{Brand Name}/`
- **Source Documents:**
  - `Brand-Guidelines/` → PDFs, docs with voice, tone, style guides
  - `Reference-Content/` → Exemplary past content pieces
  - `Guardrails/` → Prohibited terms, compliance rules, disclaimers
- **Cache File:** `{Brand Name}-profile-cache.json` (auto-generated, system-managed)

---

### 2. Cache File Schema

```json
{
  "brand_name": "Example Brand",
  "cache_version": "1.0",
  "generated_at": "2026-02-16T18:00:00Z",
  "source_docs_hash": "a3f5b8c9d2e1...",
  "profile": {
    "voice": {
      "tone": "professional",
      "formality": "business_casual",
      "personality_traits": ["helpful", "trustworthy", "innovative"]
    },
    "terminology": {
      "preferred": {"customer": "client", "product": "solution"},
      "prohibited": ["cheap", "revolutionary"],
      "industry_specific": {}
    },
    "citation_rules": {
      "format": "APA",
      "min_per_300_words": 1,
      "preferred_sources": ["PubMed", "Google Scholar"]
    },
    "guardrails": {
      "prohibited_claims": ["We are the best", "Guaranteed results"],
      "required_disclaimers": ["Results may vary. Consult a professional."],
      "compliance_notes": "All content must comply with FDA regulations."
    },
    "content_patterns": {
      "typical_structure": "intro_hook → problem → solution → benefits → cta",
      "avg_word_count": 1500
    },
    "seo_preferences": {
      "primary_keyword_density_target": 0.02,
      "meta_title_format": "{Primary Keyword} | {Brand Name}"
    },
    "quality_thresholds": {
      "minimum_quality_score": 7.0,
      "dimension_minimums": {
        "content_quality": 6.5,
        "citation_integrity": 7.5
      }
    }
  },
  "source_documents_processed": [
    {
      "path": "Brand-Guidelines/Brand-Voice-Guide-2025.pdf",
      "hash": "d4e5f6a7b8c9...",
      "last_modified": "2025-12-15T10:30:00Z",
      "pages": 12,
      "processed_at": "2026-02-16T18:00:00Z"
    },
    {
      "path": "Reference-Content/Best-Blog-Post-Example.docx",
      "hash": "e5f6g7h8i9j0...",
      "last_modified": "2026-01-10T14:22:00Z",
      "words": 1450,
      "processed_at": "2026-02-16T18:00:00Z"
    }
  ]
}
```

---

### 3. Cache Invalidation Logic

**On Brand Profile Load:**

```python
# Pseudocode for cache validation

def load_brand_profile(brand_name):
    cache_file = f"{brand_name}-profile-cache.json"

    # Check if cache exists
    if not cache_exists(cache_file):
        return generate_new_cache(brand_name)

    # Load cached profile
    cache = read_json(cache_file)

    # Calculate current source hash
    current_hash = calculate_source_hash(brand_name)

    # Compare with cached hash
    if current_hash != cache["source_docs_hash"]:
        # Source documents changed → invalidate cache
        log("Source documents modified, regenerating cache")
        return generate_new_cache(brand_name)

    # Check cache age (optional: invalidate if >30 days old)
    if cache_age_days(cache) > 30:
        log("Cache expired (>30 days), regenerating")
        return generate_new_cache(brand_name)

    # Cache is valid
    log(f"Using cached profile (generated {cache['generated_at']})")
    return cache["profile"]


def calculate_source_hash(brand_name):
    """
    Calculate SHA256 hash of all source documents
    to detect any changes
    """
    folder = f"ContentForge-Knowledge/{brand_name}/"
    all_files = list_files(folder, recursive=True)

    # Concatenate all file hashes
    combined = ""
    for file in all_files:
        if file.extension in [".pdf", ".docx", ".doc", ".txt"]:
            file_hash = sha256(file.content)
            file_modified = file.last_modified
            combined += f"{file.path}:{file_hash}:{file_modified}"

    return sha256(combined)


def generate_new_cache(brand_name):
    """
    Process all brand guidelines, extract profile,
    and save cache
    """
    folder = f"ContentForge-Knowledge/{brand_name}/"

    # Read all source documents
    guidelines = read_pdfs(f"{folder}/Brand-Guidelines/")
    reference_content = read_docs(f"{folder}/Reference-Content/")
    guardrails = read_files(f"{folder}/Guardrails/")

    # Extract brand profile using AI
    profile = extract_brand_profile(
        guidelines=guidelines,
        examples=reference_content,
        guardrails=guardrails
    )

    # Calculate source hash
    source_hash = calculate_source_hash(brand_name)

    # Create cache object
    cache = {
        "brand_name": brand_name,
        "cache_version": "1.0",
        "generated_at": now_iso(),
        "source_docs_hash": source_hash,
        "profile": profile,
        "source_documents_processed": list_processed_docs(folder)
    }

    # Save to Drive
    save_json(f"{folder}/{brand_name}-profile-cache.json", cache)

    log(f"New cache generated for {brand_name}")
    return profile
```

---

### 4. Agent Usage

**In Content Drafter (Phase 3):**

```markdown
Before drafting content, load brand profile:

1. Use Google Drive MCP to access brand folder
2. Call `load_brand_profile(brand_name)`
3. If cache valid → use cached profile (fast)
4. If cache invalid → regenerate from source docs (slow, first run)
5. Apply voice, tone, terminology from profile
```

**Example:**

```python
# In Phase 3 agent prompt
brand_profile = load_brand_profile("Example Brand")

voice_tone = brand_profile["voice"]["tone"]  # "professional"
personality = brand_profile["voice"]["personality_traits"]  # ["helpful", "trustworthy"]
preferred_terms = brand_profile["terminology"]["preferred"]  # {"customer": "client"}

# Use in content generation
# "Write in a {voice_tone} tone with {personality} traits..."
# "Always use 'client' instead of 'customer'"
```

---

### 5. Benefits

**Performance:**
- First run: 2-5 minutes (process all brand docs)
- Cached runs: <5 seconds (read JSON)
- 95%+ time savings on repeat runs

**Accuracy:**
- Hash-based detection ensures cache freshness
- Automatic invalidation when guidelines updated
- No stale brand voice issues

**Scalability:**
- Supports 50-200 brands without performance degradation
- Each brand independently cached
- Easy to add new brands (just create folder + docs)

---

### 6. Cache Refresh Triggers

**Automatic refresh when:**
1. Source document added/modified/deleted
2. Cache file doesn't exist
3. Cache >30 days old (configurable)
4. Cache version mismatch (if schema changes)

**Manual refresh:**
- Delete cache file from Drive
- Next run will regenerate automatically

---

### 7. Error Handling

**If source documents missing:**
- Warn user: "No brand guidelines found for {brand_name}"
- Use minimal default profile
- Flag content for human review

**If cache corrupted:**
- Log error
- Delete corrupted cache
- Regenerate from source

**If Drive access fails:**
- Retry with exponential backoff
- If persistent failure → abort with clear error message

---

## Implementation Checklist

For agents that need brand profiles:

- [ ] Load brand profile at start of phase
- [ ] Check cache validity before processing
- [ ] Use profile fields to guide agent behavior
- [ ] Log cache hits/misses for monitoring
- [ ] Handle missing/invalid profiles gracefully

---

**Used By:**
- Phase 3 (Content Drafter) — voice, tone, terminology
- Phase 5 (Structurer & Proofreader) — brand compliance, guardrails
- Phase 6.5 (Humanizer) — brand personality traits
- Phase 7 (Reviewer) — quality thresholds, compliance checks

**Maintained By:**
- System (automatic cache generation and invalidation)
- Users (update source documents in Drive as needed)
