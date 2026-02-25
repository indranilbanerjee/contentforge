---
description: Repurpose articles into platform-specific social media posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads
argument-hint: "<article source> [platforms: all|linkedin|twitter|instagram|facebook|threads]"
---

# Social Adapt

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Repurpose any ContentForge article into ready-to-publish social media posts for LinkedIn, Twitter/X, Instagram, Facebook, and Threads. Each post is tailored to platform character limits, audience expectations, hashtag conventions, and optimal posting times — producing 15-25 social posts from a single article.

## Trigger

User runs `/social-adapt` or asks to repurpose content for social media, create social posts from an article, or promote content on social platforms.

## Inputs

Gather the following from the user. If not provided, ask before proceeding:

1. **Source content** — the article to repurpose, provided as:
   - Google Drive URL
   - Local file path
   - Requirement ID (e.g., `REQ-001`)
   - Pasted article text

2. **Platforms** — which platforms to create posts for:
   - `all` (default) — LinkedIn, Twitter/X, Instagram, Facebook, Threads
   - Or specify: `linkedin`, `twitter`, `instagram`, `facebook`, `threads`

3. **Additional context** (optional):
   - Posts per platform (default: 3, max: 10)
   - Brand profile for voice alignment (auto-detected from content metadata if not specified)
   - Campaign hashtag (e.g., `#AcmeMedInsights`)
   - Published URL for link-sharing posts
   - Image assets available for social use
   - Tone override (casual, professional, provocative)

## Process

### 1. Content Analysis
- Read the full article and identify 10-15 shareworthy moments:
  - Compelling statistics and data points
  - Key insights and takeaways
  - Quotable sentences
  - Actionable tips
  - Surprising findings or contrarian points

### 2. Platform Adaptation

Apply platform-specific rules from `config/social-platform-specs.json`:

| Platform | Character Limit | Hashtags | Tone | Best For |
|----------|----------------|----------|------|----------|
| LinkedIn | 3,000 chars | 3-5 | Professional, thought leadership | B2B, industry insights |
| Twitter/X | 280 chars | 1-3 | Punchy, conversational | Quick takes, data points |
| Instagram | 2,200 caption | 10-15 | Visual-first, storytelling | Behind-the-scenes, tips |
| Facebook | 63,206 chars | 1-2 | Conversational, community | Discussions, longer reads |
| Threads | 500 chars | 0-2 | Casual, authentic | Hot takes, opinions |

### 3. Post Generation

For each post:
- **Hook** — scroll-stopping first line (question, bold statement, surprising stat)
- **Body** — platform-appropriate content that stands alone (doesn't require reading the article)
- **CTA** — engagement prompt or link to full article
- **Hashtags** — platform-appropriate number and relevance
- **Image spec** — recommended image dimensions, style, and content
- **Posting time** — optimal day and time for the platform

### 4. Quality Check

Each post verified against:
- Character count within platform limit
- Self-contained (makes sense without the article)
- Has a clear CTA (read more, share, comment, save)
- Brand voice consistency
- No duplicate content across posts

## Output Format

### Social Package Summary

| Platform | Posts Created | Total Characters | Hashtag Strategy |
|----------|-------------|-----------------|------------------|

### Posts by Platform

For each platform, each post includes:

**Post [#] — [Platform]**
- Content (with character count)
- Hashtags
- Image recommendation (dimensions, content description, style)
- Best posting time
- Engagement prediction (high/medium/low based on content type)

### Posting Schedule

| Day | Time | Platform | Post # | Hook Preview |
|-----|------|----------|--------|--------------|

Spread posts across 1-2 weeks for sustained engagement.

## After Adaptation

Ask: "Would you like me to:
- Schedule these posts? (requires ~~chat or social connector)
- Create the recommended images in Canva? (requires ~~design connector)
- Generate more posts for specific platforms?
- Adapt another article?
- Create A/B variants for the top-performing hooks? (`/variants`)
- Translate these posts for other markets? (`/translate`)"
