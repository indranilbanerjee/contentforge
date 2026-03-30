---
name: cf-template
description: Create and manage custom content type templates beyond the 5 built-in types, with quality standards, section structure, and pipeline compatibility
argument-hint: "[content-type]"
effort: high
---

# Custom Content Template Manager

Create and manage custom content type templates beyond the 5 built-in types (article, blog, whitepaper, faq, research-paper). Define section structure, word count ranges, readability targets, citation requirements, and quality standards — then use the template with `/contentforge` for consistent, repeatable content production.

## When to Use

Use `/cf:template` when:
- You need a **content type not covered** by the 5 built-in templates (case study, product comparison, landing page copy, email newsletter, press release, etc.)
- You want to **standardize a content format** your team produces regularly
- You need to **modify an existing template** (e.g., add a section to the article template)
- You're onboarding a client who has **specific content format requirements**
- You want to **import a content structure** from an example file

**For producing content using a template**, use `/contentforge --type=custom:template-name`.
**For the 5 built-in templates**, see `templates/content-types/` (these are pre-configured and cannot be deleted).

## What This Command Does

1. **Define Template** — Specify content type name, base type (or custom), word count range, readability target, and citation requirements
2. **Create Section Structure** — Define sections with names, descriptions, word count allocations, and ordering
3. **Set Quality Standards** — Readability target (grade level), citation density, keyword placement rules, and custom quality criteria
4. **Generate Template File** — Create the template .md file in `templates/content-types/`
5. **Validate Pipeline Compatibility** — Test that the template works with all ContentForge pipeline phases

## Required Inputs

**Minimum Required:**
- **Template Name** — Name for the custom template (e.g., "case-study", "product-comparison", "email-newsletter")

**Optional:**
- **Base Type** — Start from an existing template and modify: article, blog, whitepaper, faq, research-paper, or `custom` (blank slate)
- **Word Count Range** — Minimum and maximum word count (e.g., 1500-2500)
- **Readability Target** — Flesch-Kincaid grade level target (e.g., 8-10 for general, 12-14 for professional)
- **Citation Minimum** — Minimum number of citations required (e.g., 5)
- **Section Structure** — Array of section names with descriptions and word count allocations

## How to Use

### Interactive Mode (Recommended)
```
/cf:template
```
**Prompts you for:**
1. Template name
2. Base type (or custom)
3. Word count range
4. Readability target
5. Citation minimum
6. Sections (add one at a time, or import from example)

### Quick Mode
```
/cf:template case-study --base=article --words=1500-2500 --readability=10-12 --citations=8
```

### Import from Example File
```
/cf:template product-comparison --from-example=./example-product-comparison.docx
```
Analyzes the example file's structure (headings, sections, word count) and creates a template matching that format.

### Modify Existing Template
```
/cf:template article --modify --add-section="Expert Quotes:Include 3-5 expert quotes with attribution:200-300"
```

### List All Templates
```
/cf:template --list
```
Shows built-in and custom templates with key specifications.

## What Happens

### Step 1: Template Definition (1-2 minutes)

Define the template's core specifications.

**From Base Type:**
- Load the base template's structure and specifications
- Allow modifications (add/remove/reorder sections, change word counts, adjust quality standards)

**From Example File:**
- Parse the example document's heading structure (H1/H2/H3)
- Measure word counts per section
- Identify citation patterns
- Generate a template matching the observed structure

**From Custom (Blank Slate):**
- Start with no predefined structure
- User defines every section from scratch

**Example:**
```
Template Definition
================================================================

Name: case-study
Base: article (modified)
Word Count Range: 1,500 - 2,500 words
Readability Target: Grade 10-12 (professional audience)
Citation Minimum: 8 sources
Keyword Strategy: 1 primary + 2 secondary keywords
Production Time Estimate: 25-35 minutes

Modifications from Base (article):
  + Added "Client Challenge" section
  + Added "Solution Implementation" section
  + Added "Results & Metrics" section
  + Added "Client Quote" section
  - Removed generic "Background" section
  * Changed conclusion to "Key Takeaways + CTA"
================================================================
```

### Step 2: Section Structure Definition (2-3 minutes)

Define each section with name, description, word count allocation, and requirements.

**Section Definition Format:**
```
Section Name: [Name]
  Description: [What this section should contain]
  Word Count: [min-max] words
  Required: [yes/no]
  Citation Target: [number of citations expected]
  Keyword Placement: [yes/no — should primary keyword appear here?]
  Notes: [Additional guidance for the drafter]
```

**Example Section Structure (Case Study):**
```
Section Structure: case-study
================================================================

1. Title & Meta
   Description: SEO-optimized title with client name (if permitted)
                and key result
   Word Count: N/A (title + meta description only)
   Required: Yes
   Keyword Placement: Yes (primary keyword in title)

2. Executive Summary (150-200 words)
   Description: 2-3 paragraph overview of the client, challenge,
                solution, and headline result. Should stand alone
                as a compelling summary.
   Required: Yes
   Citation Target: 1 (for the headline metric)
   Keyword Placement: Yes (within first 100 words)

3. Client Profile (100-150 words)
   Description: Brief overview of the client organization — industry,
                size, market position. Establish context without
                revealing confidential details unless authorized.
   Required: Yes
   Citation Target: 0
   Keyword Placement: No

4. The Challenge (200-300 words)
   Description: Describe the specific problem or pain point the
                client faced. Include business impact metrics
                (cost, time, risk) where available. Make the
                reader identify with the challenge.
   Required: Yes
   Citation Target: 1-2 (industry context for the challenge)
   Keyword Placement: Yes (secondary keyword)

5. Solution Implementation (300-400 words)
   Description: How the solution was implemented — phases, timeline,
                key decisions, technical approach. Be specific enough
                to be credible without revealing proprietary methods.
   Required: Yes
   Citation Target: 1-2 (technology references, methodology citations)
   Keyword Placement: Yes (primary keyword)

6. Results & Metrics (250-350 words)
   Description: Quantified outcomes with before/after comparisons.
                Include at least 3 metrics (e.g., cost reduction %,
                time savings, accuracy improvement, ROI). Use data
                visualizations descriptions (tables, charts).
   Required: Yes
   Citation Target: 2-3 (verified metrics, industry benchmarks)
   Keyword Placement: No

7. Client Testimonial (100-150 words)
   Description: Direct quote from a client stakeholder about the
                experience and results. Include name, title, and
                organization (with permission).
   Required: Yes (can use anonymized if needed)
   Citation Target: 1 (the testimonial itself)
   Keyword Placement: No

8. Key Takeaways (150-200 words)
   Description: 3-5 bullet points summarizing lessons learned
                and transferable insights for the reader.
   Required: Yes
   Citation Target: 0
   Keyword Placement: Yes (primary keyword in closing)

9. Call to Action (50-100 words)
   Description: Clear next step for the reader — contact form,
                demo request, related case study, whitepaper download.
   Required: Yes
   Citation Target: 0
   Keyword Placement: No

Total Sections: 9
Total Word Count: 1,300 - 1,850 (core) + title/meta
Within Range: Yes (1,500 - 2,500 with CTA and formatting)
================================================================
```

### Step 3: Quality Standards Definition (1 minute)

Set the quality criteria specific to this template.

**Quality Standards:**
```
Quality Standards: case-study
================================================================

Readability:
  Target Grade Level: 10-12 (Flesch-Kincaid)
  Target Reading Ease: 45-55 (Flesch)
  Audience: Business professionals, decision-makers

Citations:
  Minimum Total: 8 sources
  Minimum Density: 1 citation per 300 words
  Required Types: At least 1 client-provided metric,
                  at least 2 industry benchmarks
  Recency: 80% of sources within 24 months

SEO:
  Primary Keyword Density: 1.5-2.0%
  Primary Keyword Placements: Title, Executive Summary,
                               Challenge, Solution, Takeaways
  Secondary Keywords: 2 keywords at 0.5-0.8% density
  Meta Title: Under 60 characters
  Meta Description: Under 155 characters

Content Quality:
  Metrics Required: Minimum 3 quantified results
  Testimonial: Required (anonymized acceptable)
  Implementation Detail: Specific enough for credibility
  Before/After: At least 1 before/after comparison

Brand Compliance:
  Follows brand profile voice and terminology
  Required disclaimers included (if applicable)
  No prohibited claims

Humanization:
  Burstiness Target: 0.70+ (sentence variety)
  AI Pattern Check: Standard (20+ telltale phrases)
================================================================
```

### Step 4: Generate Template File (1 minute)

Create the template .md file in `templates/content-types/`.

**Generated File: `templates/content-types/case-study-structure.md`**
```markdown
# Case Study Content Template

**Template Name:** case-study
**Version:** 1.0.0
**Created:** 2026-02-25
**Base Type:** article (modified)

## Specifications

| Specification | Value |
|--------------|-------|
| Word Count | 1,500 - 2,500 |
| Readability | Grade 10-12 |
| Citations | 8+ sources |
| Primary Keywords | 1 |
| Secondary Keywords | 2 |
| Production Time | 25-35 min |
| Sections | 9 |

## Section Structure

[Full section definitions as defined in Step 2]

## Quality Standards

[Full quality standards as defined in Step 3]

## Usage

Use with ContentForge:
  /contentforge "Title" --type=custom:case-study --brand=BrandName

## Examples

See example case studies in templates/examples/case-study/
```

### Step 5: Pipeline Compatibility Validation (1 minute)

Test the template against all ContentForge pipeline phases.

**Validation Checks:**
- **Phase 1 (Research):** Can generate outline matching section structure
- **Phase 3 (Drafting):** Section word counts sum to within template range
- **Phase 5 (Structurer):** Heading hierarchy is valid (H1 > H2 > H3)
- **Phase 6 (SEO):** Keyword placement rules are compatible with section structure
- **Phase 6.5 (Humanizer):** Burstiness target is achievable for this word count
- **Phase 7 (Reviewer):** Quality standards are scoreable by the 5-dimension system

**Example Validation:**
```
Pipeline Compatibility: case-study
================================================================

Phase 1 (Research): PASS — Outline can target 9 sections
Phase 2 (Fact Check): PASS — Citation targets defined per section
Phase 3 (Drafting): PASS — Word counts sum to 1,300-1,850 (within range)
Phase 4 (Validation): PASS — Citation density achievable
Phase 5 (Structurer): PASS — H1 > H2 hierarchy valid
Phase 6 (SEO): PASS — Keyword placements in 5 sections
Phase 6.5 (Humanizer): PASS — Burstiness achievable at 1,500+ words
Phase 7 (Reviewer): PASS — All 5 quality dimensions scoreable
Phase 8 (Output): PASS — .docx generation compatible

Overall: PASS — Template is pipeline-compatible
================================================================
```

## Built-In Template Examples

For reference, here are templates others commonly create:

### Case Study
```
/cf:template case-study --base=article --words=1500-2500 --readability=10-12 --citations=8
```
Sections: Executive Summary, Client Profile, Challenge, Solution, Results, Testimonial, Takeaways, CTA

### Product Comparison
```
/cf:template product-comparison --base=article --words=2000-3500 --readability=9-11 --citations=12
```
Sections: Overview, Comparison Criteria, Product-by-Product Analysis (3-5 products), Feature Matrix, Pricing Comparison, Use Case Recommendations, Verdict, CTA

### Landing Page Copy
```
/cf:template landing-page --base=custom --words=500-1000 --readability=7-9 --citations=3
```
Sections: Hero Headline + Subhead, Problem Statement, Solution Overview, Key Benefits (3-5), Social Proof, Feature Highlights, FAQ (3-5 questions), CTA

### Email Newsletter
```
/cf:template email-newsletter --base=blog --words=400-800 --readability=7-9 --citations=2
```
Sections: Subject Line (A/B options), Preview Text, Opening Hook, Main Content (1-2 topics), Key Takeaway, CTA, PS Line

## Output

The template creation produces:

| Output | Description |
|--------|------------|
| **Template File** | .md file in `templates/content-types/[name]-structure.md` |
| **Usage Instructions** | Command to use the template with `/contentforge` |
| **Pipeline Validation** | Compatibility test results for all 10 phases |
| **Specifications Summary** | Word count, readability, citations, sections count |

## Output Example

```
Template Created: case-study
================================================================

File: templates/content-types/case-study-structure.md
Specifications:
  Word Count: 1,500 - 2,500
  Readability: Grade 10-12
  Citations: 8+ sources
  Sections: 9
  Production Time: 25-35 min

Pipeline Validation: PASS (all 10 phases compatible)

Usage:
  /contentforge "Client X: How AI Reduced Diagnostic Time by 40%"
    --type=custom:case-study --brand=AcmeMed

Templates Available (Built-In + Custom):
  Built-in: article, blog, whitepaper, faq, research-paper
  Custom: case-study (new)
================================================================
```

## Managing Templates

### List All Templates
```
/cf:template --list
```
```
Available Content Templates
================================================================

BUILT-IN (5):
  article          | 1,500-2,000 words | Grade 10-12 | 8-12 citations
  blog             | 800-1,500 words   | Grade 8-10  | 5-8 citations
  whitepaper       | 2,500-5,000 words | Grade 12-14 | 15-25 citations
  faq              | 600-1,200 words   | Grade 8-10  | 3-5 citations
  research-paper   | 4,000-8,000 words | Grade 14-16 | 25-50 citations

CUSTOM (1):
  case-study       | 1,500-2,500 words | Grade 10-12 | 8+ citations
================================================================
```

### View Template Details
```
/cf:template case-study --view
```
Displays the full template specification with all sections and quality standards.

### Delete Custom Template
```
/cf:template case-study --delete
```
Removes the custom template file. Built-in templates cannot be deleted.

### Export Template
```
/cf:template case-study --export=./case-study-template.json
```
Exports the template as JSON for sharing with other ContentForge installations.

## Troubleshooting

### "Word counts don't sum to range"
**Cause:** Section word count allocations don't add up to the template's total word count range.
**Solution:** Adjust individual section word counts or the template's total range. The template creator will warn you during definition if allocations are mismatched.

### "Pipeline validation failed at Phase 7"
**Cause:** Quality standards are too strict or conflicting (e.g., Grade 7 readability with 25 citations — low readability + high citation density is hard to achieve).
**Solution:** Relax either the readability target or the citation minimum. The validation will suggest which constraint to adjust.

### "Template not found when using --type=custom:name"
**Cause:** Template file doesn't exist in `templates/content-types/` or the name doesn't match.
**Solution:** Run `/cf:template --list` to see available templates. Names are kebab-case (e.g., `case-study`, not `Case Study`).

### "Can't modify built-in template"
**Cause:** Built-in templates (article, blog, whitepaper, faq, research-paper) are read-only.
**Solution:** Create a custom template based on the built-in one: `/cf:template my-article --base=article`. This creates a copy you can modify freely.

## Limitations

- **Custom templates** are local to the ContentForge installation (not synced to cloud unless exported)
- **Base type modification** copies the base — changes to the base later won't propagate to the custom template
- **Maximum sections**: 15 per template (more than 15 makes the pipeline unwieldy)
- **Minimum word count**: 300 words (below this, the quality scoring system is unreliable)
- **Import from example** works best with well-structured .docx files (clear heading hierarchy)

## Agent Used

None. This skill uses deterministic template creation (section definition, word count calculation, validation rules) without agent-based reasoning.

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** — Use templates with `--type=custom:template-name`
- **[/batch-process](../batch-process/SKILL.md)** — Batch can reference custom templates
- **[/cf:brief](../cf-brief/SKILL.md)** — Briefs can target custom template section structures

---

**Version:** 3.4.0
**Agent:** None (deterministic template creation)
**Processing Time:** 3-6 minutes
**Output:** Template .md file in templates/content-types/, pipeline validation, usage instructions
