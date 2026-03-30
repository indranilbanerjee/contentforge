---
name: cf-variants
description: Generate scored A/B test variations of content elements (headlines, hooks, CTAs, intros, conclusions) with optimization-goal-driven ranking
argument-hint: "[content-element]"
effort: medium
---

# Content Variant Generator — A/B Test Optimization

Generate multiple scored variations of any content element — headlines, hooks, CTAs, introductions, or conclusions — ranked by composite quality score and aligned to your optimization goal.

## When to Use

Use `/cf:variants` when you need:
- **A/B test candidates** for headlines, subject lines, or CTAs
- **Higher-performing alternatives** to existing content elements
- **Data-informed decisions** about which hook or intro to deploy
- **Systematic variation** rather than guessing what works better
- **Brand-consistent alternatives** that maintain voice while testing angles

**For full content production**, use [`/contentforge`](../contentforge/SKILL.md) instead.
**For refreshing entire pieces**, use [`/content-refresh`](../content-refresh/SKILL.md) instead.

## What This Command Does

Takes a single content element and generates N variations (3-10), scores each across 6 quality dimensions, ranks by composite score weighted toward your optimization goal, and presents the top 3 with detailed reasoning and A/B test setup guidance.

**Process Flow:**

1. **Extract & Analyze** — Parse the source element, identify its type, tone, structure, and current strengths/weaknesses
2. **Generate Variations** — Create N distinct alternatives using Humanizer patterns (sentence variety, natural phrasing) and Reviewer scoring logic (quality dimensions)
3. **Score Each Variation** — Rate across 6 dimensions (0-10 scale)
4. **Rank & Recommend** — Weight scores by optimization goal, present top 3 with explanations
5. **A/B Test Guidance** — Provide test setup recommendations (sample size, duration, success metrics)

## Required Inputs

**Minimum Required:**
- **Source Content** — The existing element to generate variations for (or a topic/brief if creating from scratch)
- **Element Type** — `headline` | `hook` | `cta` | `intro` | `conclusion`

**Optional:**
- **Variation Count** — Number of variations to generate (3-10, default: 5)
- **Optimization Goal** — `clicks` | `engagement` | `conversions` | `readability` (default: `engagement`)
- **Brand** — Brand profile to enforce voice/tone (if registered via `/brand-setup`)
- **Target Audience** — Who the content is for (influences language and appeal)
- **Tone Override** — Override brand default (authoritative, conversational, technical, witty)

## How to Use

### Interactive Mode
```
/cf:variants
```
**Prompts you for:**
1. Source content or element text
2. Element type (select from 5 options)
3. Variation count (default 5)
4. Optimization goal (select from 4 options)

### Quick Mode (All Parameters)
```
/cf:variants "AI Will Transform Your Business in 2026" --type=headline --count=5 --goal=clicks --brand=AcmeMed
```

### From Existing ContentForge Output
```
/cf:variants --source-doc=https://docs.google.com/document/d/XYZ123 --element=headline --count=7 --goal=conversions
```
Extracts the headline from the document and generates 7 conversion-optimized alternatives.

## What Happens

### Step 1: Element Analysis (30 seconds)

Parse the source element and assess its current performance profile:

- **Structure**: Length, word count, punctuation, question vs. statement
- **Emotional Register**: Neutral, urgent, curious, aspirational, fear-based
- **Specificity**: Vague ("improve results") vs. concrete ("increase CTR by 34%")
- **Keyword Presence**: SEO keywords included or missing
- **Brand Voice Alignment**: Matches registered brand profile or deviates

**Analysis Output:**
```
Source Element Analysis
-------------------------------------------------------------
Element: "AI Will Transform Your Business in 2026"
Type: Headline
Word Count: 8
Structure: Statement (declarative)
Emotional Register: Aspirational (moderate)
Specificity: Low (no numbers, no concrete outcome)
Curiosity Gap: Low (no open question, no surprise)
Keyword Presence: "AI" present, "business transformation" absent
Brand Voice: Neutral (no brand-specific markers)

Improvement Opportunities:
- Add specificity (numbers, concrete outcomes)
- Increase curiosity gap (why 2026? what changes?)
- Strengthen emotional pull (urgency or fear of missing out)
- Include target keyword for SEO
-------------------------------------------------------------
```

### Step 2: Variation Generation (1-2 minutes)

Generate N variations using two complementary patterns:

**Humanizer Patterns Applied:**
- Sentence variety (different lengths, structures, rhythms)
- Natural phrasing (no AI-typical constructions like "delve" or "leverage")
- Brand personality injection (authoritative, witty, warm, data-driven)
- Diverse emotional angles (curiosity, urgency, authority, empathy, challenge)

**Reviewer Logic Applied:**
- Each variation targets a different angle while maintaining brand voice
- Variations span the full spectrum: safe/conservative to bold/provocative
- At least one variation prioritizes SEO keyword placement
- At least one variation prioritizes emotional pull

**Variation Strategies by Element Type:**

| Element Type | Strategy Mix |
|-------------|-------------|
| **Headline** | Question, number-driven, how-to, contrarian, emotional, keyword-rich |
| **Hook** | Statistic-lead, story-lead, question-lead, bold-claim, problem-agitate |
| **CTA** | Action-verb, benefit-driven, urgency, social-proof, low-friction |
| **Intro** | Problem-first, story-first, data-first, contrarian-first, question-first |
| **Conclusion** | Summary-CTA, future-vision, callback, challenge, resource-link |

### Step 3: Multi-Dimensional Scoring (1 minute)

Each variation is scored across 6 dimensions on a 0-10 scale:

| Dimension | Weight (Default) | What It Measures |
|-----------|-----------------|------------------|
| **Clarity** | 0.20 | Instantly understandable, no ambiguity |
| **Emotional Appeal** | 0.20 | Triggers feeling (curiosity, urgency, aspiration) |
| **Specificity** | 0.20 | Concrete details, numbers, outcomes |
| **Curiosity Gap** | 0.15 | Creates desire to read more |
| **Keyword Presence** | 0.10 | SEO keyword naturally included |
| **Brand Voice Fit** | 0.15 | Matches registered brand personality |

**Goal-Based Weight Adjustments:**

When an optimization goal is specified, dimension weights shift:

| Dimension | Default | Clicks | Engagement | Conversions | Readability |
|-----------|---------|--------|------------|-------------|-------------|
| Clarity | 0.20 | 0.15 | 0.15 | 0.20 | 0.35 |
| Emotional Appeal | 0.20 | 0.25 | 0.30 | 0.25 | 0.10 |
| Specificity | 0.20 | 0.20 | 0.15 | 0.25 | 0.15 |
| Curiosity Gap | 0.15 | 0.25 | 0.20 | 0.10 | 0.10 |
| Keyword Presence | 0.10 | 0.05 | 0.05 | 0.05 | 0.10 |
| Brand Voice Fit | 0.15 | 0.10 | 0.15 | 0.15 | 0.20 |

### Step 4: Ranking and Recommendations (30 seconds)

Sort variations by composite score (weighted sum), present top 3 with reasoning.

### Step 5: A/B Test Setup Guidance

Provide actionable test parameters:
- Recommended sample size per variant
- Suggested test duration (7-14 days typical)
- Primary success metric aligned to optimization goal
- Statistical significance threshold (95% confidence)
- Fallback plan if no variant wins

## Output: Variation Scorecard

### Example Output (5 headline variants, goal: clicks)

```
================================================================
CONTENTFORGE VARIANT SCORECARD
================================================================
Source: "AI Will Transform Your Business in 2026"
Element Type: Headline
Optimization Goal: Clicks
Variations Generated: 5
Brand: AcmeMed (Authoritative, Professional)
================================================================

VARIATION SCORES (Ranked by Composite)
----------------------------------------------------------------

#1  "The 5 AI Shifts That Will Reshape Healthcare
     Revenue by 2027"
    ┌────────────────────────────────────────────────┐
    │ Clarity:          8.5  ████████░░               │
    │ Emotional Appeal: 8.0  ████████░░               │
    │ Specificity:      9.5  █████████░               │
    │ Curiosity Gap:    9.0  █████████░               │
    │ Keyword Presence: 7.0  ███████░░░               │
    │ Brand Voice Fit:  8.5  ████████░░               │
    ├────────────────────────────────────────────────┤
    │ COMPOSITE SCORE:  8.6 / 10                     │
    └────────────────────────────────────────────────┘
    Why it works: Number-driven ("5 shifts") creates
    scannable promise. "Reshape revenue" adds concrete
    stakes. Industry-specific ("healthcare") signals
    relevance. Curiosity gap: which 5 shifts?

#2  "Why 73% of Executives Are Wrong About AI
     — And What It Will Cost Them"
    ┌────────────────────────────────────────────────┐
    │ Clarity:          7.5  ███████░░░               │
    │ Emotional Appeal: 9.0  █████████░               │
    │ Specificity:      8.5  ████████░░               │
    │ Curiosity Gap:    9.5  █████████░               │
    │ Keyword Presence: 6.5  ██████░░░░               │
    │ Brand Voice Fit:  7.5  ███████░░░               │
    ├────────────────────────────────────────────────┤
    │ COMPOSITE SCORE:  8.3 / 10                     │
    └────────────────────────────────────────────────┘
    Why it works: Contrarian angle ("wrong about AI")
    provokes click. Specific stat (73%) adds authority.
    Fear element ("what it will cost") drives urgency.
    Strong curiosity gap: wrong about what, exactly?

#3  "How AI-Powered Diagnostics Cut Time-to-Treatment
     by 40% (2026 Data)"
    ┌────────────────────────────────────────────────┐
    │ Clarity:          9.0  █████████░               │
    │ Emotional Appeal: 7.0  ███████░░░               │
    │ Specificity:      9.5  █████████░               │
    │ Curiosity Gap:    7.5  ███████░░░               │
    │ Keyword Presence: 9.0  █████████░               │
    │ Brand Voice Fit:  8.5  ████████░░               │
    ├────────────────────────────────────────────────┤
    │ COMPOSITE SCORE:  8.1 / 10                     │
    └────────────────────────────────────────────────┘
    Why it works: How-to structure sets clear
    expectation. Concrete outcome ("40%") adds
    credibility. Year tag ("2026 Data") signals
    freshness. Strong SEO keyword placement.

#4  "AI in Healthcare Is No Longer Optional
     — Here's Your 90-Day Action Plan"
    ┌────────────────────────────────────────────────┐
    │ Clarity:          8.5  ████████░░               │
    │ Emotional Appeal: 7.5  ███████░░░               │
    │ Specificity:      7.0  ███████░░░               │
    │ Curiosity Gap:    7.0  ███████░░░               │
    │ Keyword Presence: 8.0  ████████░░               │
    │ Brand Voice Fit:  8.0  ████████░░               │
    ├────────────────────────────────────────────────┤
    │ COMPOSITE SCORE:  7.6 / 10                     │
    └────────────────────────────────────────────────┘
    Why it works: Urgency framing ("no longer
    optional"). Actionable promise ("90-day plan")
    reduces perceived effort. Good keyword placement.

#5  "What Happened When 12 Hospitals Deployed AI
     Last Quarter"
    ┌────────────────────────────────────────────────┐
    │ Clarity:          8.0  ████████░░               │
    │ Emotional Appeal: 7.0  ███████░░░               │
    │ Specificity:      8.0  ████████░░               │
    │ Curiosity Gap:    8.5  ████████░░               │
    │ Keyword Presence: 6.0  ██████░░░░               │
    │ Brand Voice Fit:  7.5  ███████░░░               │
    ├────────────────────────────────────────────────┤
    │ COMPOSITE SCORE:  7.4 / 10                     │
    └────────────────────────────────────────────────┘
    Why it works: Story-lead ("what happened when")
    creates narrative pull. Specific ("12 hospitals",
    "last quarter") builds trust. Curiosity gap is
    strong but keyword integration is weaker.

================================================================
TOP 3 RECOMMENDATIONS
================================================================

1. BEST FOR CLICKS: Variant #1
   "The 5 AI Shifts That Will Reshape Healthcare
    Revenue by 2027"
   Rationale: Number-driven headlines consistently
   outperform in CTR testing. The specificity of
   "5 shifts" combined with revenue stakes creates
   both scannability and urgency.

2. BEST FOR ENGAGEMENT: Variant #2
   "Why 73% of Executives Are Wrong About AI
    — And What It Will Cost Them"
   Rationale: Contrarian angles drive shares and
   comments. The implicit challenge ("are you in
   the 73%?") creates personal relevance that
   extends dwell time and social sharing.

3. BEST FOR SEO: Variant #3
   "How AI-Powered Diagnostics Cut Time-to-Treatment
    by 40% (2026 Data)"
   Rationale: Natural keyword integration with
   "AI-powered diagnostics" matches high-intent
   search queries. The "how" structure aligns with
   featured snippet patterns.

================================================================
A/B TEST SETUP GUIDANCE
================================================================

Recommended Test Configuration:
- Variants to Test: #1 vs. #2 (or #1 vs. original)
- Sample Size: 1,000+ impressions per variant
- Duration: 7-14 days (avoid holidays, weekends-only)
- Primary Metric: Click-through rate (CTR)
- Secondary Metrics: Time on page, scroll depth,
  bounce rate
- Confidence Level: 95% statistical significance
- Winner Criteria: >10% relative CTR improvement

Test Channels:
- Email subject lines: Send to equal-sized segments
- Blog headlines: Use CMS A/B testing plugin
- Social posts: Run as separate posts, same time
- Ad copy: Split test in Google/Meta Ads Manager

Fallback Plan:
If no variant achieves statistical significance
after 14 days, deploy Variant #1 (highest composite
score) as the safe default.

================================================================
```

## Scoring Dimensions Explained

### Clarity (0-10)
How quickly a reader grasps the meaning. Penalizes jargon, ambiguity, overly long constructions, and unclear referents. Rewards plain language, active voice, and immediate comprehension.

### Emotional Appeal (0-10)
The strength of the emotional trigger. Measures curiosity, urgency, aspiration, fear, empathy, or challenge. A score of 5 is emotionally neutral; 8+ means strong pull. Penalizes flat, corporate-speak phrasing.

### Specificity (0-10)
Concrete details vs. vague promises. Numbers, percentages, timeframes, named entities, and measurable outcomes score high. Generic phrases like "improve your results" score low.

### Curiosity Gap (0-10)
The degree to which the element creates a desire to read more. Questions, incomplete information, surprising claims, and "what happened next" structures score high. Fully self-contained statements score lower.

### Keyword Presence (0-10)
Whether the primary SEO keyword appears naturally. Scores high for natural inclusion in prominent position. Scores low for absence, forced placement, or keyword stuffing. Evaluated only if a keyword is provided or extractable from brand profile.

### Brand Voice Fit (0-10)
Alignment with the registered brand personality. If no brand is specified, scores based on professional consistency. Checks tone (authoritative vs. casual), terminology (approved vs. banned words), and guardrails (topics to avoid).

## Element Type Guidelines

### Headlines
- Optimal length: 6-12 words (40-70 characters for search)
- At least one variation should be a question
- At least one should include a number
- Avoid clickbait that content cannot deliver on

### Hooks (Opening Sentences)
- Optimal length: 1-3 sentences (25-75 words)
- Must create immediate forward momentum
- At least one stat-led and one story-led variation
- Must connect to article thesis within 2 sentences

### CTAs (Calls to Action)
- Optimal length: 3-8 words for buttons, 1-2 sentences for inline
- Start with strong action verb (Get, Start, Discover, Download)
- At least one low-friction option ("Learn more" vs. "Buy now")
- Match CTA intensity to funnel stage (awareness vs. decision)

### Intros (Opening Paragraphs)
- Optimal length: 50-150 words
- Must establish relevance within first sentence
- At least one problem-first and one data-first variation
- Include primary keyword within first 100 words

### Conclusions
- Optimal length: 50-120 words
- Must include actionable next step
- At least one should callback to intro hook
- Include secondary CTA or resource link

## Integration with Other Skills

**Before Variants:**
- `/contentforge` — Generate the base content first
- `/content-refresh` — Update content before variant testing

**After Variants:**
- Deploy winning variant via CMS or publishing platform
- Track performance with `/cf:analytics`

## Agents Used

This skill uses existing **Humanizer** and **Reviewer** agent patterns — no additional agents required.

- **Humanizer Patterns**: Ensure variations read naturally with sentence variety, no AI-typical phrases, and brand personality
- **Reviewer Scoring Logic**: Apply multi-dimensional scoring with configurable weights per optimization goal

## Limitations

- Generates variations of **individual elements**, not full content pieces
- Scoring is predictive, not based on live traffic data — always validate with actual A/B tests
- Maximum 10 variations per run (diminishing returns beyond 7-8)
- Brand voice scoring requires a registered brand profile for best results

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** — Full content production pipeline
- **[/content-refresh](../content-refresh/SKILL.md)** — Update existing content with fresh data
- **[/batch-process](../batch-process/SKILL.md)** — Process multiple content pieces in parallel
- **[/cf:analytics](../cf-analytics/SKILL.md)** — Track quality scores and performance over time

---

**Version:** 3.4.0
**Agents:** Humanizer (patterns), Reviewer (scoring logic)
**Processing Time:** 2-4 minutes per element
**Output:** Scored variation cards with top 3 recommendations + A/B test setup guidance
