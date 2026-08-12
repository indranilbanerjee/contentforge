---
name: cf-social-adapt
description: "Repurpose a finished article into ready-to-publish, platform-native social posts for LinkedIn, Twitter/X, Instagram, Facebook, Threads, TikTok, Bluesky, and YouTube Shorts — each with hook, hashtags, CTA, character count, image spec, and posting time, typically 24-40 posts per article. Triggers on \"/contentforge:cf-social-adapt\", \"turn this article into LinkedIn posts\", \"make social posts from this blog\", \"repurpose this for social media\", \"promote the published article\". Dispatches the contentforge:social-adapter agent, takes all platform limits from config/social-platform-specs.json, reads the brand profile for voice, and requires pipeline-approved content (score >=7.0). Pairs with /contentforge:cf-publish for the live article URL."
disable-model-invocation: true
argument-hint: "[article-path]"
effort: medium
---

# Social Content Adaptation — ContentForge Post-Pipeline

Repurpose any ContentForge article into ready-to-publish social media posts for LinkedIn, Twitter/X, Instagram, Facebook, Threads, TikTok, Bluesky, and YouTube Shorts. Each post is tailored to platform character limits, audience expectations, hashtag conventions, and optimal posting times.

## Platform rules — single source of truth

**All character limits, hashtag counts, ideal lengths, and format rules come from `config/social-platform-specs.json`. Read that file at run time and use its values. Never use remembered limits, and never trust any limit that appears in an example in this file.** The supported platform list is exactly the set of top-level keys in that config whose value contains a `character_limit` field (or, for video platforms, a `title_max_chars` field). Top-level keys without one of those fields are not platforms — `_description`, `_posting_times_note`, `hashtag_tiers`, and `post_frameworks` must be skipped. As shipped this resolves to 8 platforms: `linkedin`, `twitter`, `instagram`, `facebook`, `threads`, `tiktok`, `bluesky`, `youtube_shorts`.

## When to Use

Use `/contentforge:cf-social-adapt` when:
- You have a **published or approved article** and want to promote it on social media
- You need **platform-native posts** (not the same text copy-pasted everywhere)
- You want **multiple posts per platform** to sustain engagement over days/weeks
- You need **hashtag strategies**, **image specifications**, and **posting schedules**
- You want to **repurpose one article into 24-40 social posts** across 8 platforms

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
- **Platforms** -- `all`, or a comma-separated subset of the platform keys defined in `config/social-platform-specs.json`

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
/contentforge:cf-social-adapt
```
**Prompts you for:**
1. Content source (Drive URL, file path, or requirement ID)
2. Platforms (select from list or type `all`)
3. Posts per platform (default: 3)
4. Published article URL (if available)

### Quick Mode (All Parameters)
```
/contentforge:cf-social-adapt REQ-001 --platforms=linkedin,twitter,instagram --count=5 --url=https://acme-corp.com/blog/ai-healthcare-2026
```

### All Platforms, Default Count
```
/contentforge:cf-social-adapt REQ-001 --platforms=all
```

### With Campaign Hashtag
```
/contentforge:cf-social-adapt REQ-001 --platforms=all --hashtag=#AcmeMedInsights --count=4
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

**Dispatch the agent — do not do this inline.** Call `Task` with `subagent_type: contentforge:social-adapter`, exactly as the main orchestrator dispatches its pipeline phases. The Task prompt carries only:
- the source-content path (`phase-6.5-humanized.md` in pipeline mode, or the user-supplied file/URL in standalone mode),
- `phase-7-review.json` and `phase-6-seo.md` paths when running after a pipeline run,
- the brand-profile path, target platforms, posts-per-platform, published URL and campaign hashtag.

The agent `Read`s what it needs from those paths — never inline the full article into the Task prompt. `agents/10-social-adapter.md` owns the extraction rules, platform formatting, hashtag tiers and the post-quality gate; this skill owns argument parsing, the quality-score precondition, and presenting the result.

The Social Adapter Agent identifies 10-15 moments from the article that will resonate on social media.

**Extraction criteria:**
- Statistics and data points (numbers grab attention)
- Counterintuitive insights (challenge assumptions)
- Actionable tips (practical value)
- Quotable statements (from sources or the article itself)
- Provocative questions (drive engagement)
- Before/after comparisons (transformation stories)
- Lists and frameworks (easy to visualize)

**SYNTHETIC EXAMPLE — fabricated for illustration. All statistics and organizations below are invented; never reuse them in real output:**
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
10. CASE STUDY: "Northlake Clinic (a fictional example hospital) reduced diagnostic wait times by 78% after implementing AI triage"
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

**Before generating output, read `references/output-format-example.md` (in this skill's directory) for a full synthetic worked example** covering all 5 illustrative platforms (LinkedIn, Twitter/X, Instagram, Facebook, Threads) plus the summary block — reproduce this shape and level of per-post detail (hook, body, hashtags, character count, image spec, recommended time) for every requested platform, and follow with a SUMMARY block (total posts, character-limit compliance, self-contained rate, CTA rate, publishing schedule, estimated reach).

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
Error: Platform "<name>" is not in config/social-platform-specs.json
Supported: <list the platform keys actually present in the config>
Action: Use a supported platform, or add a spec block for the new
  platform to config/social-platform-specs.json
```

### Missing Published URL
```
Warning: No published URL provided for link-sharing posts.
Action: Posts generated without link. Add --url parameter to include article link.
  Some post types (link share, CTA) will use "[link in bio]" placeholder.
```

## AI-Content Labels (platform disclosure)

Major platforms provide AI-content labeling options, and EU AI Act Article 50 (applicable from 2 Aug 2026) requires disclosure of AI-generated content shown to EU audiences:

- **LinkedIn / Meta (Facebook, Instagram) / TikTok / YouTube** — each offers an "AI-generated or AI-assisted" label or disclosure toggle at posting time. If the brand targets EU audiences or the brand profile's guardrails require disclosure, remind the user to enable the platform label when scheduling these posts, and note it in the handoff summary.
- When disclosure applies, include a per-post metadata note in the output: `AI-label: recommended (EU targeting)`.

## Agent Used

- **Social Adapter Agent** (post-pipeline) -- see `agents/10-social-adapter.md`

## Configuration

- **Platform specs:** `config/social-platform-specs.json`
- **Post templates:** `templates/social-post-templates.md`

## Integration with Other Skills

**Before Social Adaptation:**
- `/contentforge:create-content` -- Produce the source article
- `/contentforge:cf-publish` -- Publish the article to your CMS (get the URL for social posts)

**After Social Adaptation:**
- Copy posts to your social scheduling tool (Buffer, Hootsuite, Sprout Social)
- Track engagement metrics per post to refine future adaptations

## Related Skills

- **[/contentforge:create-content](../../commands/create-content.md)** -- Full content production pipeline
- **[/contentforge:cf-publish](../cf-publish/SKILL.md)** -- Publish to Webflow/WordPress
- **[/contentforge:content-refresh](../content-refresh/SKILL.md)** -- Update existing content
- **[/contentforge:batch-process](../batch-process/SKILL.md)** -- Sequential, checkpointed batch production

---

**Agent:** Social Adapter (10-social-adapter)
**Config:** `config/social-platform-specs.json` (single source of truth for platform rules)
**Templates:** `templates/social-post-templates.md`
**Default:** 3 posts per platform
