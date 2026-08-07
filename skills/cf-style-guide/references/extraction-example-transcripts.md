# cf-style-guide — extraction example transcripts

Verbatim example output transcripts moved out of `skills/cf-style-guide/SKILL.md` to keep the
skill body within the ~500-line Agent Skills guidance. Each section below corresponds to a step
in "What Happens" in the SKILL.md body.

## Step 1 — Load Style Guide Source

**Example:**
```
Style Guide Loaded
================================================================

Source: https://acmemed.com/brand-guidelines
Page Title: "AcmeMed Brand Voice & Content Guidelines"
Sections Found: 8
  1. Brand Overview
  2. Voice & Tone
  3. Writing Style
  4. Approved Terminology
  5. Banned Terms & Phrases
  6. Regulatory Compliance
  7. Visual Identity (skipped — not relevant to content)
  8. Social Media Guidelines

Content Length: 4,200 words
Parsing: Complete
================================================================
```

## Step 2 — Extract Voice Characteristics

**Example Output:**
```
Voice Characteristics Extracted
================================================================

Tone:
  Primary: Authoritative
  Secondary: Empathetic
  By Content Type:
    Article: Authoritative + data-driven
    Blog: Authoritative + approachable
    Whitepaper: Authoritative + academic

Formality: 4 (Formal)
  No contractions in articles/whitepapers
  Contractions OK in blog posts only

Personality Traits: data-driven, trustworthy, innovative, empathetic, precise

Writing Style:
  Sentence Length: Medium (15-25 words average)
  Paragraphs: 3-5 sentences
  Voice: Active (90%+)
  Person: Third person for articles, second person for blogs
  Rhetorical Questions: Sparingly (1-2 per piece max)
  Statistics: Heavy use, always cited
  Storytelling: Patient stories as examples (anonymized)

Confidence: 92% (style guide was explicit about most elements)
================================================================
```

## Step 3 — Identify Terminology

**Example Output:**
```
Terminology Extracted
================================================================

Approved Terms (47 total):
  Brand Terms:
    "AcmeMed" (never "Acme Med" or "ACMEMED")
    "AcmeDiagnostics" (product name, always capitalized)
    "AcmeCare Platform" (full name on first use, "the Platform" after)

  Industry Terms:
    "healthcare" (one word, not "health care")
    "precision medicine" (preferred over "personalized medicine")
    "clinical decision support" (preferred over "clinical AI")
    "value-based care" (preferred over "value-driven care")

  Acronyms:
    "AI" — Artificial Intelligence (expand on first use)
    "EMR" — Electronic Medical Record (expand on first use)
    "HIPAA" — never expand (universally known in target audience)

Banned Terms (23 total):
  "revolutionary" — overpromising, use "innovative" instead
  "breakthrough" — overpromising, use "advancement" instead
  "cure" — regulatory risk, use "treatment" or "therapy"
  "guaranteed" — compliance violation in healthcare
  "CompetitorX", "CompetitorY" — no competitor mentions
  "patients love it" — unsubstantiated claim
  "cutting-edge" — cliche, use specific technology descriptions
  ... (16 more)

Conditional Terms (8 total):
  "FDA-cleared" — only for products with actual FDA clearance
  "clinically validated" — only with citation to clinical trial
  "reduces costs" — only with specific percentage and source
================================================================
```

## Step 4 — Parse Compliance Requirements

**Example Output:**
```
Compliance Requirements Extracted
================================================================

Required Disclaimers (4):
  1. All articles: "This content is for informational purposes only
     and does not constitute medical advice."
  2. Product mentions: "AcmeDiagnostics is pending FDA clearance
     for [specific use case]." (update status quarterly)
  3. Patient stories: "Patient names and identifying details have
     been changed to protect privacy."
  4. Clinical data: "Results may vary. Clinical outcomes depend
     on individual patient factors."

Prohibited Claims (6):
  1. No efficacy claims without peer-reviewed citation
  2. No "FDA-approved" (use "FDA-cleared" for 510(k) devices)
  3. No cost savings claims without specific study reference
  4. No comparison claims vs competitors
  5. No absolute claims ("best", "only", "first") without qualification
  6. No patient testimonials as efficacy evidence

Compliance Rules:
  HIPAA: Never include PHI (Protected Health Information)
  FDA: Follow 510(k) promotional guidelines for device content
  FTC: Disclose any sponsored or partnership content

Sensitivity Guidelines:
  Language: Person-first (e.g., "patients with diabetes" not "diabetics")
  Imagery descriptions: Diverse, inclusive, respectful
  Avoid: Military metaphors for disease ("battle cancer", "fight disease")

Confidence: 96% (compliance section was highly structured)
================================================================
```

## Step 6 — Save and Validate

**Example Validation:**
```
Brand Profile Validation
================================================================

Profile: AcmeMed v1.0.0
  JSON Valid: Yes
  Required Fields: 12/12 present
  Voice Complete: Yes (tone, formality, personality, style)
  Terminology: 47 approved, 23 banned, 8 conditional
  Guardrails: 4 disclaimers, 6 prohibited claims, 3 compliance rules
  Acronyms: 12 defined

Pipeline Compatibility Test:
  Phase 3 (Drafting): Can apply voice settings — PASS
  Phase 5 (Brand Compliance): Can check terminology — PASS
  Phase 6 (SEO): No conflicts with SEO settings — PASS
  Phase 6.5 (Humanizer): Can apply personality — PASS

Profile Saved:
  Local: ~/.claude-marketing/acmemed/Brand-Guidelines/AcmeMed-brand-profile.json
  Drive (Cowork mode): <drive_root>/_brands/acmemed/profile.json
  Cache Hash: SHA256:a3f2c1... (for fast cache lookup)

Status: READY — Profile can be used with /contentforge:create-content --brand=AcmeMed
================================================================
```

## Final pipeline completion transcript (Output Example)

```
Style Guide Import Complete
================================================================

Brand: AcmeMed
Source: https://acmemed.com/brand-guidelines
Import Scope: All (voice + terminology + guardrails)
Processing Time: 6 minutes

Results:
  Voice: Authoritative + Empathetic, Formality 4/5
  Personality: data-driven, trustworthy, innovative, empathetic, precise
  Terminology: 47 approved, 23 banned, 8 conditional, 12 acronyms
  Guardrails: 4 disclaimers, 6 prohibited claims, 3 compliance rules
  Audience: {persona_title} at {company_size} ({reading_level})
  Competitors: {count} competitors analyzed
  Content Pillars: {count} pillars defined
  Visual Identity: {primary_color} / {secondary_color} | Style: {image_style}
  Import Confidence: 94%

Validation: PASS (all pipeline phases compatible)

Saved to:
  Local: ~/.claude-marketing/acmemed/Brand-Guidelines/AcmeMed-brand-profile.json
  Drive (Cowork mode): <drive_root>/_brands/acmemed/profile.json

Use with: /contentforge:create-content --brand=AcmeMed
================================================================
```
