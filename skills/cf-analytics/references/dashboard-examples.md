# cf-analytics — synthetic ASCII dashboard examples

Verbatim synthetic example dashboards moved out of `skills/cf-analytics/SKILL.md` to keep the skill body within the ~500-line Agent Skills guidance. All numbers in every example below are invented — always compute the real dashboard from actual tracking records.

## Full Dashboard (Default View)

**SYNTHETIC EXAMPLE — fabricated for illustration.** All numbers below are invented; always compute from real tracking records.

```
================================================================
CONTENTFORGE ANALYTICS DASHBOARD
================================================================
Period: Last 30 Days (2026-01-26 to 2026-02-25)
Filters: All Brands | All Types | Focus: Quality
Records Analyzed: 42 pieces
================================================================

QUALITY SCORE OVERVIEW
----------------------------------------------------------------
                    Avg     Med     Min     Max     StdDev
Composite:          8.7     8.9     6.2     9.8     0.72
  Content Quality:  8.9     9.1     6.5     9.9     0.65
  Citation Integ.:  8.5     8.6     5.8     9.7     0.81
  Brand Compliance: 9.2     9.3     7.0     10.0    0.54
  SEO Performance:  8.6     8.7     6.0     9.8     0.68
  Readability:      8.8     8.9     6.8     9.6     0.52

Trend (30-day): +0.3 pts  [IMPROVING]

QUALITY TREND (Weekly Rolling Average)
----------------------------------------------------------------
10.0 |
 9.5 |          *----*
 9.0 |    *----*      *----*----*
 8.5 |---*
 8.0 |
 7.5 |
 7.0 |
     +----+----+----+----+----+----
     W1   W2   W3   W4   W5   Now
     8.4  8.6  8.7  8.9  8.8  8.9

Interpretation: Steady upward trend over 30 days.
Week 1 dip likely due to new brand onboarding
(AcmeMed cold-start penalty). Stabilized at 8.8+
from Week 3 onward.

PHASE TIMING BREAKDOWN (Minutes, Avg)
----------------------------------------------------------------
Phase               Avg    Bench   Delta    Status
................................................................
1. Research         4.2    4.0     +0.2     OK
2. Fact-Check       3.1    3.0     +0.1     OK
3. Drafting         5.8    6.0     -0.2     OK
4. Validation       2.4    2.0     +0.4     OK
5. Structuring      2.7    2.5     +0.2     OK
6. SEO              2.9    3.0     -0.1     OK
6.5 Humanizer       1.6    1.5     +0.1     OK
7. Reviewer         2.5    2.5     +0.0     OK
8. Output           1.3    1.5     -0.2     OK
................................................................
Total:             26.5   26.0     +0.5     OK

Slowest Phase: Drafting (22% of total time)
Fastest Phase: Output (5% of total time)

BRAND PERFORMANCE COMPARISON
----------------------------------------------------------------
Brand            Pieces   Avg Score   Trend     Top Dim
................................................................
AcmeMed            18      9.1        +0.4      Brand Comp (9.6)
TechCorp           12      8.5        +0.2      SEO Perf (9.0)
AgencyCo            8      8.4        stable    Readability (9.1)
FinanceFirst        4      8.8        new       Citation (9.2)

Best Performer: AcmeMed (9.1 avg, improving)
Most Improved: AcmeMed (+0.4 pts over period)
Needs Attention: AgencyCo (flat trend, lowest avg)

CONTENT TYPE AVERAGES
----------------------------------------------------------------
Type              Pieces   Avg Score   Avg Time   Loops/Piece
................................................................
Article              16      8.8        25.2 min    0.4
Blog                 14      8.9        17.8 min    0.2
Whitepaper            6      8.4        36.1 min    0.8
FAQ                   4      9.1        14.2 min    0.1
Research Paper        2      8.2        52.3 min    1.5

Best Quality: FAQ (9.1 avg, simplest structure)
Fastest: FAQ (14.2 min avg)
Most Loops: Research Paper (1.5 avg, citation density)

FEEDBACK LOOP ANALYSIS
----------------------------------------------------------------
Loop-Free Rate: 71% (30/42 pieces passed first review)
Avg Loops/Piece: 0.45
Max Loops Used: 3 (REQ-089, whitepaper)

Loop Frequency by Type:
  P4 > P3 (hallucination fix):  5 occurrences
  P7 > P5 (structure fix):     3 occurrences
  P7 > P6 (SEO fix):           2 occurrences
  P7 > P3 (content rewrite):   1 occurrence

Most Common Trigger: Hallucination detection in
validation phase (45% of all loops). Primarily
affects research papers and whitepapers with
high citation density requirements.

ALERTS
----------------------------------------------------------------
[!] QUALITY DECLINE: AgencyCo last 3 pieces scored
    below 8.0 (7.8, 7.6, 7.9). Review brand
    profile guardrails.

[!] PHASE SLOWDOWN: Whitepaper Phase 4 (validation)
    averaging 3.8 min vs. 2.0 min benchmark (1.9x).
    High citation count driving longer validation.

[i] VOLUME NOTE: Research paper sample size is low
    (2 pieces). Metrics may not be representative.
    Need 10+ data points for reliable trends.

IMPROVEMENT RECOMMENDATIONS
----------------------------------------------------------------
1. AgencyCo Brand Review: Update brand profile
   (last modified 45 days ago). Recent score
   decline suggests stale guardrails or
   terminology changes.

2. Whitepaper Validation: Consider pre-filtering
   sources in Phase 1 to reduce Phase 4
   validation load. Current avg: 22 sources
   per whitepaper vs. 15-25 target range.

3. Research Paper Pipeline: High loop frequency
   (1.5 avg) suggests tighter Phase 1 research
   briefs could reduce rework. Consider adding
   outline approval gate before drafting.

4. Citation Density: Blog citation rate (1 per
   380 words) is slightly below target (1 per
   300 words). Phase 3 keyword: increase
   inline citation frequency for blogs.

================================================================
Generated: 2026-02-25 14:30:00
Next suggested review: 2026-03-25 (monthly cadence)
================================================================
```

## Timing-Focused Dashboard (--focus=timing)

```
================================================================
CONTENTFORGE TIMING ANALYTICS
================================================================
Period: Last 30 Days | Records: 42 pieces
================================================================

TOTAL PROCESSING TIME DISTRIBUTION
----------------------------------------------------------------
< 15 min:  ████████████████  14 pieces (33%)
15-25 min: ██████████████████████  18 pieces (43%)
25-35 min: ██████████  8 pieces (19%)
> 35 min:  ██  2 pieces (5%)

Average: 26.5 min | Median: 24.8 min
P90: 35.2 min (90% of pieces finish within)

TIME BY CONTENT TYPE
----------------------------------------------------------------
                Min     Avg     Max     P90     vs Bench
Article:       18.2    25.2    32.1    29.5     +0.2 min
Blog:          12.4    17.8    24.6    21.3     -0.2 min
Whitepaper:    28.5    36.1    44.2    42.0     +1.1 min
FAQ:           10.1    14.2    18.3    17.0     -0.8 min
Research:      48.1    52.3    56.5    55.8     +12.3 min

PHASE WATERFALL (% of Total Time)
----------------------------------------------------------------
Research:     ████████████████  16% (4.2 min)
Fact-Check:   ████████████  12% (3.1 min)
Drafting:     ██████████████████████  22% (5.8 min)
Validation:   █████████  9% (2.4 min)
Structuring:  ██████████  10% (2.7 min)
SEO:          ███████████  11% (2.9 min)
Humanizer:    ██████  6% (1.6 min)
Reviewer:     █████████  10% (2.5 min)
Output:       █████  5% (1.3 min)

BOTTLENECK ANALYSIS
----------------------------------------------------------------
Primary Bottleneck: Drafting (22% of time)
  - Expected: 18% (per phase weight config)
  - Overrun: +4% (+1.0 min above weighted expectation)
  - Root Cause: Higher word count targets in recent
    batch (avg 2,100 words vs. 1,750 typical)

Secondary Bottleneck: Fact-Check for Whitepapers
  - Whitepaper avg: 4.8 min (vs. 3.0 min benchmark)
  - Cause: 22 sources avg per whitepaper (high end
    of 15-25 range)

THROUGHPUT METRICS
----------------------------------------------------------------
Single Pipeline: 2.3 pieces/hour (avg)
Batch (5x): 9.4 pieces/hour (effective)
Batch Efficiency: 82% (18% overhead for queue mgmt)

================================================================
```

## Compliance-Focused Dashboard (--focus=compliance)

```
================================================================
CONTENTFORGE COMPLIANCE ANALYTICS
================================================================
Period: Last 30 Days | Records: 42 pieces
================================================================

CITATION COMPLIANCE
----------------------------------------------------------------
Avg Citations/Piece: 11.2
Target Range: 5-25 (varies by type)
Pieces Meeting Target: 40/42 (95%)

Citation Density (per 300 words):
  Article:   1.2 (target: 1.0)  PASS
  Blog:      0.8 (target: 1.0)  BELOW
  Whitepaper: 1.4 (target: 1.0) PASS
  FAQ:       0.9 (target: 1.0)  BELOW (marginal)

Broken Links Detected: 0/42 pieces (100% clean)
Source Age: 94% within 2-year freshness window

BRAND COMPLIANCE SCORES
----------------------------------------------------------------
Brand            Avg Score   Min Score   Violations
AcmeMed:         9.6         8.8         0
TechCorp:        9.0         7.5         1 (terminology)
AgencyCo:        8.8         7.0         2 (tone drift)
FinanceFirst:    9.4         9.0         0

FEEDBACK LOOP COMPLIANCE
----------------------------------------------------------------
Loop Budget Usage:
  Avg loops/piece:     0.45 (budget: 5 max)
  Loop-free rate:      71%
  Max loops any piece: 3 (within budget)
  Budget exhaustions:  0 (no human escalations)

Human Review Escalations: 0/42 (0%)
Score <5.0 Pieces: 0/42 (0%)

HALLUCINATION REPORT
----------------------------------------------------------------
Hallucinations Detected: 0 in final output
Phase 4 Catches: 5 instances caught and fixed
  - 3x fabricated statistics (corrected in loop)
  - 1x misattributed quote (corrected in loop)
  - 1x outdated regulatory reference (corrected)

Three-Layer Verification: 100% effective
  Layer 1 (Fact-Check): Caught 0 (pre-filtered)
  Layer 2 (Validator): Caught 5 (primary defense)
  Layer 3 (Reviewer): Caught 0 (nothing escaped)

================================================================
```
