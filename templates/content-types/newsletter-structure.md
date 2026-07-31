# Newsletter Structure Template — ContentForge

## Content Type: Newsletter
**Target Word Count:** 500-1200 words
**Target Reading Level:** Flesch-Kincaid Grade 7-9
**Minimum Citations:** 2-5 sources (inline links, not academic format)
**SEO Focus:** Low (email is the channel — subject line and preview text replace meta tags)

---

## Phase 6 Mapping — how SEO gates apply to email

Newsletters run the same 10-gate pipeline; Phase 6 fields map to email equivalents so Gate 6 stays checkable without special-casing the orchestrator:

| Pipeline field | Newsletter meaning | Constraint |
|----------------|--------------------|------------|
| Meta title | **Subject line** (selected primary) | ≤60 chars; no clickbait-that-underdelivers |
| Meta description | **Preview text** | Front-load the first ~90 chars (client truncation); ≤155 total |
| Keyword placements | Subject line + first 100 words + one section heading | Gate 6 checks these three; H2-count and conclusion placements are N/A for newsletters |
| Internal link map | The single CTA (`type=conversion`) + up to 2 topical links | Commercial links only if the edition is explicitly promotional |
| Schema markup | N/A — email has no JSON-LD | Phase 6 notes "N/A (email)" in the scorecard; reviewer scores Schema sub-component as 8 (neutral), like FAQ visuals |

## Standard Structure

### 1. Subject Line Package (produced first, chosen last)
- **3-5 subject line options**, ranked, with rationale (curiosity / benefit / news / question angles)
- **Preview text** written as a complement to the subject, never a repeat of it
- **A/B pair recommendation:** the two options that test a real variable (angle, not synonyms) — `/contentforge:cf-variants` can extend this
- Length guidance: 30-50 chars performs best on mobile; hard cap 60

### 2. Greeting & Hook (30-60 words)
- Skip "Hope you're doing well" — open with the edition's sharpest fact, question, or claim
- Personalization tokens as placeholders where the ESP supports them: `{{first_name}}` marked clearly so Phase 8 doesn't strip it

### 3. Lead Story (150-350 words)
- ONE main story per edition — the thing this send exists to say
- Structure: claim → evidence (cited inline as links) → why it matters to this audience → optional read-more link
- If adapted from a longer piece (via the pipeline or an existing article): compress to the 2-3 strongest points; the newsletter is the trailer, the article is the film

### 4. Secondary Items (2-4 items, 50-120 words each)
- Format each as: **bold one-line takeaway** + 1-3 sentences of context + inline link
- Scannable — a reader skimming only bold lines gets the edition's full value
- Curated external links are fine (with source named); this is the one content type where linking out is a feature

### 5. Single CTA (30-60 words)
- Exactly ONE primary call to action per edition (Phase 6 `type=conversion` marker)
- Button-ready phrasing: verb-first, ≤5 words ("Book a teardown call", "Get the template")
- Placement: after the lead story or at the end — never both with different CTAs

### 6. Sign-off & Footer (20-40 words + boilerplate)
- Human sign-off: a named sender (from the brand's `author_profiles` — a newsletter from a person outperforms a newsletter from a logo)
- Footer boilerplate placeholders Phase 8 must preserve: `{{unsubscribe_link}}`, physical address placeholder, and the brand's AI-disclosure line if the brand's guardrails or EU targeting require one (same rule as `/contentforge:cf-publish` Step 4.5)

---

## Email-Specific Constraints (Phase 8 / export)

- **Rendering:** single column, 600px max width, inline CSS only, no external stylesheets, no web fonts with system-font fallback missing
- **Images:** max 580px wide, alt text mandatory (image-blocking clients), never image-only content
- **Plain-text sanity:** the content must survive a plain-text render — no meaning carried solely by layout
- **Deliverability hygiene (content-level):** avoid spam-trigger patterns (ALL-CAPS subjects, "FREE!!!", excessive punctuation), keep text-to-link ratio healthy, one send = one topic focus. Infrastructure (SPF/DKIM/DMARC, list hygiene, warm-up) is out of scope for content production — note it, don't fake it.
- **Export:** `.docx` is the review/approval artifact; the send-ready form is the HTML export (`{title}-newsletter.html` per the Output Manager's extended formats, responsive, inline CSS, CTA button, unsubscribe placeholder)

## Phase Adaptations for Newsletters

- **Phase 1 (Research):** lighter — verify the lead story's facts and source the secondary items; no full SERP/competitor analysis unless the user asks for a positioning angle
- **Phase 3 (Draft):** the skeleton's H1 = internal edition title (subject line package travels in the metadata block, chosen at review)
- **Phase 5 (Structure):** scannability weighting is higher than any other type — bold-line skim test is part of the check
- **Phase 6.5 (Humanizer):** conversational register; contractions on; patterns 30-35 (structural tells) hit newsletters hardest — no "In this edition we'll explore..."
- **Phase 7 (Review):** Readability target Grade 7-9; SEO Performance scored via the Phase 6 mapping table above

## Quality Standards

- One idea per edition, one CTA per edition
- Subject line package present with a real A/B variable
- Every claim in the lead story cited inline
- Skim test passes: bold lines alone deliver the value
- Named human sender applied from `author_profiles`

## Common Pitfalls to Avoid

- **The everything-edition** — five stories of equal weight = zero stories read
- **Subject/body bait-and-switch** — the subject promises what the lead story doesn't deliver
- **CTA inflation** — three CTAs convert worse than one
- **Blog-post-in-an-envelope** — pasting an article instead of writing for the inbox
- **Logo-as-sender** — unsigned newsletters underperform; use a real author
