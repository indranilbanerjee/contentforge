---
name: cf-video-script
description: Produce platform-optimized video scripts with hooks, scenes, B-roll directions, and on-screen text for YouTube, TikTok, Instagram Reels, and explainer videos
---

# Video Script Production

Transform a topic or existing article into a production-ready video script with timestamps, scene directions, B-roll shot lists, on-screen text, and music recommendations -- optimized for YouTube, TikTok, Instagram Reels, or explainer video formats.

## When to Use

Use `/cf-video-script` when you need:
- **YouTube scripts** (3-10 min) with SEO-optimized titles, descriptions, and chapter timestamps
- **TikTok scripts** (30-60s) with fast-cut pacing and trending audio hooks
- **Instagram Reels scripts** (30-60s) with vertical format and caption-driven storytelling
- **Explainer videos** (3-5 min) with clear visual directions and professional pacing
- **Video adaptations** of existing ContentForge articles, blogs, or whitepapers

**Not for:** Raw creative brainstorming (use `/contentforge` first for research), live stream outlines, podcast scripts.

## Supported Platforms & Lengths

| Platform | Supported Lengths | Aspect Ratio | Key Characteristics |
|----------|------------------|--------------|-------------------|
| **YouTube** | 3min, 5min, 10min | 16:9 landscape | SEO titles, end screens, mid-roll breaks |
| **TikTok** | 30s, 60s | 9:16 vertical | Hook in 1s, fast cuts, trending audio |
| **Instagram Reels** | 30s, 60s | 9:16 vertical | Captions required, visual-first storytelling |
| **Explainer** | 3min, 5min | 16:9 landscape | Slower pace, professional graphics, clear narration |

## Required Inputs

**Minimum Required:**
- **Topic or Source** -- Either a topic string ("AI in Healthcare 2026") or a ContentForge article URL/path
- **Platform** -- `youtube`, `tiktok`, `instagram`, or `explainer`
- **Video Length** -- `30s`, `60s`, `3min`, `5min`, or `10min`

**Optional:**
- **Tone** -- `educational`, `entertaining`, `promotional`, or `storytelling` (defaults to platform standard)
- **Brand** -- Brand profile for voice consistency (recommended)
- **Target Audience** -- Who this video is for (e.g., "Marketing managers, 25-45")
- **Primary Keyword** -- For YouTube SEO optimization
- **CTA** -- Specific call-to-action (defaults to platform-appropriate CTA)
- **Speaker** -- On-camera host name, or "voiceover only"

## How to Use

### Interactive Mode
```
/cf-video-script
```
**Prompts you for:**
1. Topic or source article URL
2. Platform (YouTube / TikTok / Instagram / Explainer)
3. Video length
4. Tone
5. Brand profile (optional)

### Quick Mode
```
/cf-video-script "AI in Healthcare: 2026 Trends" --platform=youtube --length=5min --tone=educational --brand=AcmeMed
```

### From Existing Article
```
/cf-video-script --source="https://drive.google.com/file/d/ABC123" --platform=tiktok --length=60s --tone=entertaining
```
Extracts key points from the article and restructures for video format.

## What Happens

### Phase 1: Content Research & Extraction (2-4 minutes)
- If topic provided: Research Agent gathers video-friendly data points, statistics, examples, and competitor video analysis
- If source article provided: Extracts key messages, data points, quotes, and visual opportunities
- Identifies the single strongest hook (statistic, question, or bold claim)
- Maps content to target video length (word count budget based on 120-150 words/minute dialogue)
- **Quality Gate:** Hook identified, word budget calculated, key points mapped to scenes

### Phase 2: Script Structure (2-3 minutes)
- Content Drafter builds script following `templates/content-types/video-script-structure.md`
- Allocates time to each section:
  - **HOOK:** First 3 seconds (TikTok: 1 second)
  - **INTRO:** 10-15% of total length
  - **MAIN CONTENT:** 60-70% split across scenes
  - **CTA:** 10-15% of total length
  - **OUTRO:** 5-10% (YouTube only)
- Creates scene breakdown with timestamps
- **Quality Gate:** All sections allocated, timestamps continuous, word count within budget

### Phase 3: Scene Writing (3-5 minutes)
- Writes each scene with:
  - **Dialogue/Narration:** What the speaker says (timed to 120-150 words/min)
  - **On-Screen Text:** Key phrases, statistics, bullet points viewers see
  - **B-Roll Directions:** Specific visual descriptions for each segment
  - **Music/SFX:** Mood, tempo, and transition sound suggestions
- Applies platform-specific style:
  - YouTube: Conversational, direct address, pattern interrupts every 30-60s
  - TikTok: Punchy, fast-paced, text-heavy, trending audio references
  - Instagram: Visual-first, caption storytelling, aesthetic emphasis
  - Explainer: Clear, measured pace, professional graphics focus
- **Quality Gate:** Every scene has all 4 elements, dialogue word count matches timestamps

### Phase 4: Structuring & Optimization (1-2 minutes)
- Structurer Agent reviews flow, pacing, and transitions between scenes
- Verifies hook strength (would you stop scrolling for this?)
- Checks CTA clarity and placement
- Platform-specific optimization:
  - YouTube: End screen directions, mid-roll break points (for 8+ min), chapter timestamps
  - TikTok: Ensures hook in first 1 second, audio sync points, loop potential
  - Instagram: Caption overlay timing, visual consistency
  - Explainer: Pacing check (not too fast for complex topics)
- **Quality Gate:** Pacing feels natural when read aloud, transitions smooth, CTA actionable

### Phase 5: Output Assembly (1 minute)
- Compiles final script document
- Generates supplementary materials:
  - B-roll shot list (consolidated)
  - On-screen text list (for graphic designer)
  - Music recommendations with mood/tempo
  - YouTube metadata (title, description, tags, chapters) if applicable
- Uploads to Google Drive

## Output Example

**YouTube 5-Minute Script: "AI in Healthcare: 2026 Trends"**

```
Video Script Complete: "AI in Healthcare: 2026 Trends"

Platform: YouTube
Length: 5:00 (target) / 4:52 (actual)
Tone: Educational
Dialogue Word Count: 682 words (136 words/min)

Script Sections:
- HOOK (0:00-0:03): Bold statistic opener
- INTRO (0:03-0:30): Topic framing + what viewers will learn
- SCENE 1 (0:30-1:30): Current state of AI in healthcare
- SCENE 2 (1:30-2:45): 3 breakthrough applications
- SCENE 3 (2:45-3:45): Real-world case study
- SCENE 4 (3:45-4:20): What this means for the industry
- CTA (4:20-4:40): Subscribe + resource link
- OUTRO (4:40-4:52): End screen directions

Supplementary Materials:
- B-Roll Shot List: 14 shots
- On-Screen Text: 9 text overlays
- Music Recommendations: 3 tracks (upbeat electronic, 120 BPM)
- YouTube SEO: Title, description (with timestamps), 15 tags

Output Location:
Google Drive: ContentForge Output/AcmeMed/video/AI-Healthcare-2026_youtube-5min_v1.0.docx
```

## Platform-Specific Guidelines

### YouTube (3min / 5min / 10min)

**Pacing:**
- Hook in first 3 seconds (bold claim, surprising stat, or question)
- Pattern interrupt every 30-60 seconds (new visual, topic shift, question)
- Mid-roll break point at ~8:00 for 10-minute videos
- End screen: 20 seconds with subscribe CTA and related video

**SEO Requirements:**
- Title: <= 60 characters, includes primary keyword, triggers curiosity
- Description: 200-300 words, timestamps (chapters), links, keywords
- Tags: 10-15 relevant tags
- Thumbnail suggestion (text overlay + visual concept)

**Dialogue Style:**
- Direct address ("you") throughout
- Conversational but authoritative
- Questions to maintain engagement ("But here's what most people miss...")
- Data points with context, not just numbers

### TikTok (30s / 60s)

**Pacing:**
- Hook in first 1 second (text overlay + audio hook)
- New visual or text every 2-3 seconds
- Fast cuts between points (no lingering shots)
- End with loop potential (last frame connects to first)

**Style:**
- Text-heavy: Every key point has on-screen text
- Audio: Reference trending sounds or use voiceover with background music
- Casual, high-energy tone (even for educational content)
- Bold, simple language (no complex sentences)

**Format:**
- 9:16 vertical
- Captions auto-generated but script should assume sound-off viewing
- Green screen / talking head + B-roll intercuts

### Instagram Reels (30s / 60s)

**Pacing:**
- Hook in first 2 seconds (visual + caption)
- Caption-driven storytelling (assume sound-off for 60% of viewers)
- Smooth transitions (no hard cuts like TikTok)
- Aesthetic consistency with brand visual identity

**Style:**
- Visual-first: Every scene needs a strong visual concept
- Captions: Required, styled to brand fonts/colors
- Music: Background mood music, lower energy than TikTok
- Professional but approachable

### Explainer Video (3min / 5min)

**Pacing:**
- Hook in first 5 seconds (problem statement)
- Slower, measured delivery (120 words/min max)
- Pause after key points for viewer absorption
- Clear section transitions with visual markers

**Style:**
- Professional voiceover (no on-camera unless specified)
- Motion graphics and animated diagrams as primary visuals
- Data visualizations for statistics
- Clean, branded color palette throughout

## Dialogue Word Count Targets

| Length | Target Words | Words/Min | Notes |
|--------|-------------|-----------|-------|
| 30s | 60-75 | 120-150 | Tight, every word counts |
| 60s | 120-150 | 120-150 | Room for one key point + CTA |
| 3min | 360-450 | 120-150 | 3-4 main scenes |
| 5min | 600-750 | 120-150 | 4-5 main scenes |
| 10min | 1,200-1,500 | 120-150 | 6-8 main scenes + mid-roll break |

## MCP Integrations

### Required
- **Google Drive** -- Output storage, source article retrieval

### Optional
- **Google Sheets** -- Tracking sheet updates with video script metadata
- **Notion** -- Alternative output destination for video production teams

## Processing Times

| Video Length | Processing Time | Notes |
|-------------|----------------|-------|
| 30s | 6-10 min | Short format, tight optimization |
| 60s | 8-12 min | Slightly more scene work |
| 3min | 12-18 min | Multiple scenes, B-roll planning |
| 5min | 15-22 min | Full production script |
| 10min | 22-30 min | Extended script with chapter markers |

## Limitations

- **No video production** -- This produces scripts, not finished videos
- **Music is suggestive** -- Recommendations for mood/tempo, not licensed track names
- **B-roll is descriptive** -- Shot list describes what to film/source, not actual footage
- **Platform algorithms change** -- SEO and pacing recommendations based on current best practices
- **Branded visuals** -- Script describes visual concepts but does not produce graphics

## Troubleshooting

### "Source article too long for target video length"
**Cause:** Article has more content than the video length can accommodate.
**Solution:** Script automatically selects the highest-impact points. Override with `--focus="section 2, section 4"` to prioritize specific sections.

### "Hook score below threshold"
**Cause:** Opening 3 seconds lack a strong enough attention grabber.
**Solution:** Script loops back and regenerates hooks (up to 3 attempts). If persistent, provide a specific hook with `--hook="Did you know 73% of..."`.

### "Word count exceeds time budget"
**Cause:** Dialogue written at > 150 words/minute pace.
**Solution:** Structurer Agent trims sections to fit. Review trimmed content in the script notes.

## Related Skills

- **[/contentforge](../contentforge/SKILL.md)** -- Research and produce source content first
- **[/cf-social-adapt](../cf-social-adapt/SKILL.md)** -- Adapt video descriptions for social platforms
- **[/batch-process](../batch-process/SKILL.md)** -- Batch produce scripts for a content series
- **[/cf-translate](../cf-translate/SKILL.md)** -- Translate scripts for international markets

---

**Version:** 2.1.0
**Agents:** Researcher (01-researcher), Content Drafter (03-content-drafter), Structurer (05-structurer-proofreader)
**Processing Time:** 6-30 minutes depending on video length
**Quality Guarantee:** Hook in first 3s, dialogue paced at 120-150 wpm, B-roll for every major point, platform-specific optimization
