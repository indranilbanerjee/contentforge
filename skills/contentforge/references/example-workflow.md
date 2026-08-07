# contentforge (orchestrator) — Example Workflow walkthrough

Verbatim synthetic end-to-end walkthrough moved out of `skills/contentforge/SKILL.md` to keep the orchestrator skill body within the ~500-line Agent Skills guidance. This is a separate synthetic scenario from the Completion Card in "## Output Example" (which stays in the SKILL.md body) — it walks through brand setup, title selection, and review for a single illustrative run. Never reuse these numbers.

## Example Workflow

(SYNTHETIC EXAMPLE — fabricated for illustration; never reuse these numbers.)

**Scenario:** Create 1 thought leadership article for the AcmeMed brand

### Step 1: Create Brand Profile (One-Time Setup)
```
/contentforge:cf-style-guide
```
Provide: Brand name (AcmeMed), Industry (Healthcare), Voice (Authoritative), Tone (Professional), Terminology, Guardrails

### Step 2: Start Content Production
```
/contentforge "AI-Powered Diagnostics in Precision Medicine" --type=article --brand=acmemed --audience="Healthcare Executives" --keyword="AI diagnostics precision medicine"
```

### Step 3: Select Title
ContentForge generates 4-5 title options:
1. "AI-Powered Diagnostics: The Future of Precision Medicine"
2. "How AI Diagnostics Are Transforming Precision Medicine for Healthcare Leaders"
3. "5 AI Diagnostic Breakthroughs Reshaping Precision Medicine Right Now"
4. "The Executive's Guide to AI-Powered Precision Medicine Diagnostics"
5. "Why AI Diagnostics in Precision Medicine Are Finally Delivering on the Promise"

You select Option 1 → Pipeline starts with that title as the anchor.

### Step 4: Review Output
- Quality Score: 9.1/10 ✅
- Word Count: 1,922 ✅
- Citations: 12 sources ✅
- SEO: all keyword placements hit ✅

### Step 5: Publish
```
/contentforge:publish --platform=webflow
```
