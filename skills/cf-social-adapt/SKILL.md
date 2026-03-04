---
name: cf-social-adapt
description: Repurpose finished articles into platform-specific social media posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads
argument-hint: "[article-path]"
---

# Social Content Adaptation — ContentForge Post-Pipeline

Repurpose any ContentForge article into ready-to-publish social media posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads. Each post is tailored to platform character limits, audience expectations, hashtag conventions, and optimal posting times.

## When to Use

Use `/cf-social-adapt` when:
- You have a **published or approved article** and want to promote it on social media
- You need **platform-native posts** (not the same text copy-pasted everywhere)
- You want **multiple posts per platform** to sustain engagement over days/weeks
- You need **hashtag strategies**, **image specifications**, and **posting schedules**
- You want to **repurpose one article into 15-25 social posts** across 5 platforms

**Do NOT use for:**
- Content still in pipeline (must be Phase 7+ approved or Phase 8 complete)
- Creating original social content from scratch (this repurposes existing articles)
- Paid ad copy (different skill set and compliance requirements)

## What This Command Does

1. **Load Source Content** -- Pull the finished article from Google Drive, local output, or by requirement ID
2. **Extract Shareworthy Moments** -- Identify 10-15 key points (statistics, insights, quotes, tips)
3. **Apply Platform Specs** -- Load character limits, hashtag rules, and format guidelines from `config/social-platform-specs.json`
4. **Generate Posts** -- Create platform-specific posts with hooks, CTAs, and engagement elements
5. **Add Metadata** -- Character counts, hashtags, image specs, recommended posting times
6. **Quality Check** -- Ensure each post is self-contained, under character limit, and has a CTA

## Required Inputs

**Minimum Required:**
- **Source Content** -- Google Drive URL, local file path, or requirement ID (e.g., `REQ-001`)
- **Platforms** -- Comma-separated list: `linkedin`, `twitter`, `instagram`, `facebook`, `threads` (or `all`)

**Optional:**
- **Posts Per Platform** -- Number of posts per platform (default: 3, max: 10)
- **Brand** -- Brand profile for voice/tone alignment (auto-detected from content metadata if not specified)
- **Campaign Hashtag** -- Branded hashtag to include in all posts (e.g., `#AcmeMedInsights`)
- **Published URL** -- URL of the live article (for link-sharing posts)
- **Image Assets** -- URLs or paths to images/graphics available for social use
- **Tone Override** -- Override brand default (e.g., `casual`, `professional`, `provocative`)

## How to Use

### Interactive Mode
```
/cf-social-adapt
```
**Prompts you for:**
1. Content source (Drive URL, file path, or requirement ID)
2. Platforms (select from list or type `all`)
3. Posts per platform (default: 3)
4. Published article URL (if available)

### Quick Mode (All Parameters)
```
/cf-social-adapt REQ-001 --platforms=linkedin,twitter,instagram --count=5 --url=https://acme-corp.com/blog/ai-healthcare-2026
```

### All Platforms, Default Count
```
/cf-social-adapt REQ-001 --platforms=all
```

### With Campaign Hashtag
```
/cf-social-adapt REQ-001 --platforms=all --hashtag=#AcmeMedInsights --count=4
```

## What Happens

### Step 1: Load and Analyze Source Content (15-30 seconds)

**Load the finished article and extract key metadata:**
```
Source Content Loaded
---------------------------------------------------
Title: "AI in Healthcare: 2026 Trends"
Brand: AcmeMed
Word Count: 1,947
Quality Score: 9.2/10
Key Topics: AI diagnostics, precision medicine, patient care, cost reduction
Primary Keyword: "AI in healthcare"
---------------------------------------------------
```

### Step 2: Extract Shareworthy Moments (30-60 seconds)

The Social Adapter Agent (`agents/10-social-adapter.md`) identifies 10-15 moments from the article that will resonate on social media.

**Extraction criteria:**
- Statistics and data points (numbers grab attention)
- Counterintuitive insights (challenge assumptions)
- Actionable tips (practical value)
- Quotable statements (from sources or the article itself)
- Provocative questions (drive engagement)
- Before/after comparisons (transformation stories)
- Lists and frameworks (easy to visualize)

**Example extraction:**
```
Shareworthy Moments Extracted: 12

1. STATISTIC: "73% of healthcare organizations now use AI-powered diagnostics, up from 12% in 2024"
2. INSIGHT: "AI diagnostic accuracy now exceeds human radiologists by 14% for early-stage cancers"
3. TIP: "Three steps to evaluate AI diagnostic tools: accuracy benchmarks, integration requirements, compliance checklist"
4. QUOTE: "The question is no longer whether to adopt AI in healthcare, but how fast you can implement it"
5. DATA: "$4.2 billion saved annually by hospitals using AI triage systems"
6. PROVOCATIVE: "Manual diagnostic processes will be considered malpractice liability by 2030"
7. COMPARISON: "AI-assisted diagnosis: 4 minutes avg vs. traditional: 45 minutes"
8. FRAMEWORK: "The 3-layer AI healthcare stack: data ingestion, model inference, clinical integration"
9. TREND: "Precision medicine powered by AI will reduce misdiagnosis rates by 60% by 2028"
10. CASE STUDY: "Cleveland Clinic reduced diagnostic wait times by 78% after implementing AI triage"
11. LIST: "Top 5 AI healthcare applications: diagnostics, drug discovery, patient monitoring, administrative automation, clinical trials"
12. ACTIONABLE: "Start with radiology -- it has the highest AI ROI and lowest integration complexity"
```

### Step 3: Generate Platform-Specific Posts (1-2 minutes)

For each platform, generate the requested number of posts using platform specs from `config/social-platform-specs.json`.

**Each post includes:**
- Platform-optimized hook (first line grabs attention)
- Body content adapted to platform voice and length
- Hashtags (platform-appropriate count and style)
- Call-to-action or engagement hook
- Character count
- Recommended image spec
- Suggested posting time

### Step 4: Quality Check

**Every post is validated against:**
- Character limit for the platform
- Self-contained meaning (reader does not need to click a link to understand the value)
- Contains a CTA or engagement hook (question, poll prompt, or link)
- Hashtags within platform norms
- No broken or placeholder content
- Brand voice alignment

## Output Format

### Per-Platform Post Set

The output is organized by platform with all metadata included.

```
SOCIAL ADAPTATION REPORT
===================================================
Source: "AI in Healthcare: 2026 Trends"
Brand: AcmeMed
Platforms: 5 | Posts Per Platform: 3 | Total Posts: 15
===================================================


LINKEDIN (3 posts)
---------------------------------------------------

[LinkedIn Post 1 of 3] -- Type: Data-Driven Insight
Hook: Statistical lead
Recommended Time: Tuesday 8:00 AM

73% of healthcare organizations now use AI-powered diagnostics.

In 2024, that number was 12%.

That is not incremental adoption. That is a seismic shift in how
medicine gets practiced -- and the organizations still running
purely manual diagnostic workflows are falling behind fast.

Three things driving this acceleration:
-- Diagnostic accuracy that exceeds human radiologists by 14%
-- Average diagnosis time dropping from 45 minutes to 4 minutes
-- $4.2 billion in annual savings from AI triage systems alone

The question is no longer whether to adopt AI in healthcare.
It is how fast you can implement it without compromising patient safety.

Full analysis with 14 verified sources:
https://acme-corp.com/blog/ai-healthcare-2026

#AIinHealthcare #HealthTech #DigitalHealth #PrecisionMedicine #2026Trends

Character Count: 718 / 3,000
Image: Infographic showing 12% to 73% adoption curve (1200x627 px, PNG or JPG)

---------------------------------------------------

[LinkedIn Post 2 of 3] -- Type: How-To/Tip
Hook: Actionable framework
Recommended Time: Thursday 10:00 AM

Evaluating AI diagnostic tools? Here is a 3-step framework
that Cleveland Clinic used before their 78% reduction in
diagnostic wait times:

Step 1: Accuracy Benchmarks
Compare the AI system against board-certified specialists
on your specific case mix. Generic accuracy claims are
meaningless without your patient population data.

Step 2: Integration Requirements
Map every touchpoint between the AI system and your existing
EHR, PACS, and clinical workflows. The biggest failures happen
at integration, not accuracy.

Step 3: Compliance Checklist
FDA clearance, HIPAA data handling, audit trail requirements,
and clinician override protocols. Non-negotiable.

The full evaluation framework (with vendor comparison criteria):
https://acme-corp.com/blog/ai-healthcare-2026

#HealthcareAI #ClinicalAI #HealthTechStrategy #MedTech

Character Count: 812 / 3,000
Image: Checklist graphic with 3 steps (1200x627 px, PNG or JPG)

---------------------------------------------------

[LinkedIn Post 3 of 3] -- Type: Provocative Statement
Hook: Contrarian take
Recommended Time: Wednesday 12:00 PM

Manual diagnostic processes will be considered a malpractice
liability by 2030.

Controversial? Maybe. But consider the data:

AI diagnostic accuracy now exceeds human radiologists by 14%
for early-stage cancer detection. When a technology demonstrably
outperforms manual methods and a physician chooses not to use it,
the legal exposure is real.

This is not about replacing doctors. It is about augmenting them
with tools that catch what human eyes miss -- especially at 3 AM
on the seventh consecutive shift.

The hospitals getting this right are not asking "should we adopt AI?"
They are asking "how do we implement it responsibly?"

https://acme-corp.com/blog/ai-healthcare-2026

#HealthcareInnovation #AIdiagnostics #FutureOfMedicine #PatientSafety

Character Count: 745 / 3,000
Image: Split-screen comparison: manual vs AI-assisted diagnosis (1200x627 px)

===================================================


TWITTER / X (3 posts)
---------------------------------------------------

[Twitter Post 1 of 3] -- Type: Statistic Lead
Recommended Time: Tuesday 9:00 AM

73% of healthcare orgs now use AI diagnostics.

In 2024? Just 12%.

AI diagnostic accuracy exceeds human radiologists by 14% for
early-stage cancers. Average diagnosis time: 4 min vs 45 min.

The shift is happening fast.

https://acme-corp.com/blog/ai-healthcare-2026

#AIinHealthcare #HealthTech

Character Count: 267 / 280
Image: Data visualization card (1200x675 px, PNG)

---------------------------------------------------

[Twitter Post 2 of 3] -- Type: Thread Starter
Recommended Time: Wednesday 11:00 AM

Cleveland Clinic cut diagnostic wait times by 78% with AI triage.

Here is what they did differently (thread):

1/ Started with radiology -- highest ROI, lowest integration complexity
2/ Benchmarked AI against their own specialists, not vendor claims
3/ Built clinician override protocols before launch

Full breakdown: https://acme-corp.com/blog/ai-healthcare-2026

#HealthcareAI #ClinicalAI

Character Count: 274 / 280
Image: Cleveland Clinic case study card (1200x675 px, PNG)

---------------------------------------------------

[Twitter Post 3 of 3] -- Type: Question/Engagement
Recommended Time: Friday 8:00 AM

AI diagnostics now outperform human radiologists by 14%.

When a technology demonstrably outperforms manual methods,
does choosing not to use it become a liability?

Genuine question for healthcare leaders.

#AIinHealthcare #MedTech #HealthTech

Character Count: 228 / 280
Image: None (text-only engagement post)

===================================================


INSTAGRAM (3 posts)
---------------------------------------------------

[Instagram Post 1 of 3] -- Type: Carousel
Recommended Time: Monday 11:00 AM

Slide 1 (Cover): "AI in Healthcare: The Numbers That Matter in 2026"
Slide 2: 73% of healthcare orgs now use AI diagnostics (was 12% in 2024)
Slide 3: AI accuracy exceeds human radiologists by 14%
Slide 4: Diagnosis time: 4 minutes (AI) vs 45 minutes (manual)
Slide 5: $4.2 billion saved annually from AI triage
Slide 6: 78% reduction in wait times at Cleveland Clinic
Slide 7: CTA -- "Save this for your next strategy meeting"

Caption:
The AI healthcare revolution is not coming. It is here.

These numbers tell the story better than any prediction could.
Swipe through for the data that is reshaping how medicine
gets practiced in 2026.

The full analysis (14 verified sources, zero speculation)
is linked in bio.

Which stat surprised you the most? Drop a number in the comments.

#AIinHealthcare #HealthTech #DigitalHealth #MedTech
#PrecisionMedicine #HealthcareInnovation #FutureOfMedicine
#DataDriven #AIdiagnostics #HealthcareLeadership

Character Count: 562 / 2,200
Image: 7-slide carousel (1080x1080 px per slide, PNG)

---------------------------------------------------

[Instagram Post 2 of 3] -- Type: Single Image
Recommended Time: Wednesday 6:00 PM

Caption:
Manual diagnostic processes could become a malpractice
liability by 2030.

When AI outperforms human radiologists by 14% for early-stage
cancer detection, the legal question shifts from "why did you
use AI?" to "why didn't you?"

This is not about replacing physicians. It is about giving them
tools that catch what tired eyes miss.

Link in bio for the full analysis.

#AIinHealthcare #PatientSafety #HealthTech #MedTech
#HealthcareInnovation #ClinicalAI #FutureOfMedicine
#RadiologyAI #DigitalHealth #HealthcareLeaders

Character Count: 475 / 2,200
Image: Bold text overlay on medical-tech background (1080x1080 px, PNG)

---------------------------------------------------

[Instagram Post 3 of 3] -- Type: Reel Script
Recommended Time: Thursday 12:00 PM

Hook (0-3 sec): "One hospital cut wait times by 78%."
Body (3-20 sec): "Cleveland Clinic implemented AI triage and
  reduced diagnostic wait times by 78%. Here is the 3-step
  framework they used. Step 1: Start with radiology.
  Step 2: Benchmark against your own data.
  Step 3: Build override protocols first."
CTA (20-30 sec): "Full case study linked in bio. Follow for
  more healthcare innovation insights."

Caption:
Cleveland Clinic's AI triage playbook, broken down.

78% faster diagnostics. Not theory -- real results.

Save this if you are evaluating AI for your organization.

#AIinHealthcare #HealthTech #ClevelandClinic #HealthcareAI
#MedTech #Diagnostics #Innovation #ClinicalAI

Character Count: 278 / 2,200
Video: Vertical 9:16 (1080x1920 px), 30 seconds

===================================================


FACEBOOK (3 posts)
---------------------------------------------------

[Facebook Post 1 of 3] -- Type: Link Share
Recommended Time: Tuesday 10:00 AM

The numbers on AI in healthcare are staggering.

73% of healthcare organizations now use AI-powered diagnostics --
up from just 12% in 2024. That is not a gradual trend. That is
a complete transformation of how medicine gets practiced.

We dug into the data with 14 verified sources to understand
what is driving this shift and what it means for healthcare
leaders, practitioners, and patients.

Key findings:
-- AI diagnostic accuracy exceeds human radiologists by 14%
-- Average diagnosis time drops from 45 minutes to 4 minutes
-- Hospitals are saving $4.2 billion annually with AI triage
-- Cleveland Clinic cut diagnostic wait times by 78%

Read the full analysis:
https://acme-corp.com/blog/ai-healthcare-2026

#AIinHealthcare #HealthTech #DigitalHealth

Character Count: 712 / 63,206
Image: Article preview card (auto-generated from link, 1200x630 px)

---------------------------------------------------

[Facebook Post 2 of 3] -- Type: Question/Poll
Recommended Time: Thursday 2:00 PM

Quick question for healthcare professionals:

AI diagnostics now outperform human radiologists by 14% for
early-stage cancer detection. Diagnosis time drops from 45
minutes to 4 minutes.

Do you think:
A) AI-assisted diagnostics should be standard of care by 2028
B) We need more long-term data before mandating AI tools
C) It should remain a physician's choice, regardless of accuracy data

There is no wrong answer here -- we are genuinely curious where
the industry stands.

Our full analysis on the state of AI in healthcare:
https://acme-corp.com/blog/ai-healthcare-2026

#AIinHealthcare #HealthcarePoll #MedTech

Character Count: 595 / 63,206
Image: Poll graphic with A/B/C options (1200x630 px)

---------------------------------------------------

[Facebook Post 3 of 3] -- Type: Story/Case Study
Recommended Time: Saturday 9:00 AM

Cleveland Clinic had a problem.

Diagnostic wait times were climbing. Patient satisfaction
was dropping. And their best radiologists were burning out
from sheer volume.

Their solution? AI-powered triage.

The results:
-- 78% reduction in diagnostic wait times
-- AI accuracy exceeding their own specialists by 14%
-- Radiologists freed up for complex cases that need human judgment

But here is what most people miss: they did not just plug in
an AI tool and hope for the best. They followed a disciplined
3-step framework. And it started with one department.

The full case study (and the framework you can copy):
https://acme-corp.com/blog/ai-healthcare-2026

#HealthcareInnovation #AIinHealthcare #ClevelandClinic

Character Count: 701 / 63,206
Image: Cleveland Clinic case study graphic (1200x630 px)

===================================================


THREADS (3 posts)
---------------------------------------------------

[Threads Post 1 of 3] -- Type: Hot Take
Recommended Time: Tuesday 7:00 PM

73% of healthcare orgs use AI diagnostics now. Was 12% two years ago.

That is not a trend. That is a stampede.

And the orgs still running fully manual diagnostic workflows
are about to find out what "competitive disadvantage" looks like
in healthcare.

#AIinHealthcare #HealthTech

Character Count: 275 / 500
Image: None (text-only, conversational)

---------------------------------------------------

[Threads Post 2 of 3] -- Type: Quick Tip
Recommended Time: Wednesday 8:00 AM

If you are evaluating AI diagnostic tools, start with radiology.

Highest ROI. Lowest integration complexity. Largest evidence base.

Cleveland Clinic started there and cut wait times by 78%.

Do not try to boil the ocean. Pick the highest-impact department first.

#HealthcareAI #MedTech

Character Count: 268 / 500
Image: None (text-only)

---------------------------------------------------

[Threads Post 3 of 3] -- Type: Conversation Starter
Recommended Time: Friday 6:00 PM

AI outperforms human radiologists by 14% for early-stage cancer detection.

At what point does NOT using AI become the bigger risk?

Genuinely want to hear from people in healthcare on this one.

#AIinHealthcare #PatientSafety

Character Count: 224 / 500
Image: None (text-driven platform)

===================================================

SUMMARY
===================================================
Total Posts Generated: 15
Platforms: 5
Posts Per Platform: 3

Character Limit Compliance: 15/15 (100%)
Self-Contained Posts: 15/15 (100%)
Posts with CTA: 15/15 (100%)

Recommended Publishing Schedule:
  Week 1: LinkedIn 1, Twitter 1, Instagram 1, Facebook 1, Threads 1
  Week 2: LinkedIn 2, Twitter 2, Instagram 2, Facebook 2, Threads 2
  Week 3: LinkedIn 3, Twitter 3, Instagram 3, Facebook 3, Threads 3

Estimated Reach (based on typical organic performance):
  LinkedIn: 2,000-5,000 impressions per post
  Twitter/X: 500-2,000 impressions per post
  Instagram: 1,000-3,000 impressions per post
  Facebook: 800-2,500 impressions per post
  Threads: 300-1,000 impressions per post
===================================================
```

## Error Handling

### Content Not Found
```
Error: REQ-001 not found in Google Drive or local output
Action: Verify requirement ID or provide direct file path
```

### Content Not Approved
```
Error: Content quality score 4.8/10 (below 7.0 threshold)
Action: Content must pass quality review before social adaptation.
  Run /contentforge to complete the pipeline first.
```

### Platform Not Recognized
```
Error: Platform "tiktok" is not supported
Supported: linkedin, twitter, instagram, facebook, threads
Action: Use a supported platform or request feature addition
```

### Missing Published URL
```
Warning: No published URL provided for link-sharing posts.
Action: Posts generated without link. Add --url parameter to include article link.
  Some post types (link share, CTA) will use "[link in bio]" placeholder.
```

## Performance Metrics

**Typical Processing Times:**
- 1 platform, 3 posts: 30-60 seconds
- 3 platforms, 3 posts each: 1-2 minutes
- 5 platforms, 5 posts each: 2-4 minutes

**Quality Metrics (avg across beta testing):**
- Character limit compliance: 100%
- Self-contained readability: 95%+
- Brand voice alignment: 92%+
- Engagement hook present: 100%

## Agent Used

- **Social Adapter Agent** (post-pipeline) -- see `agents/10-social-adapter.md`

## Configuration

- **Platform specs:** `config/social-platform-specs.json`
- **Post templates:** `templates/social-post-templates.md`

## Integration with Other Skills

**Before Social Adaptation:**
- `/contentforge` -- Produce the source article
- `/cf-publish` -- Publish the article to your CMS (get the URL for social posts)

**After Social Adaptation:**
- Copy posts to your social scheduling tool (Buffer, Hootsuite, Sprout Social)
- Track engagement metrics per post to refine future adaptations

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** -- Full content production pipeline
- **[/cf-publish](../cf-publish/SKILL.md)** -- Publish to Webflow/WordPress
- **[/content-refresh](../content-refresh/SKILL.md)** -- Update existing content
- **[/batch-process](../batch-process/SKILL.md)** -- Parallel content production

---

**Version:** 3.4.0
**Agent:** Social Adapter (10-social-adapter)
**Config:** social-platform-specs.json
**Templates:** social-post-templates.md
**Platforms:** LinkedIn, Twitter/X, Instagram, Facebook, Threads
**Default:** 3 posts per platform (15 total for all platforms)
