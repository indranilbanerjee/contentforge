---
name: cf-calendar
description: Plan content calendars with scheduling, deadlines, team assignments, and Google Calendar sync.
argument-hint: "[month or quarter]"
effort: low
---

# Content Calendar Planner

Plan and manage content production calendars with intelligent scheduling, deadline tracking, team assignments, and optional Google Calendar event creation. The calendar works backward from publish dates to calculate production start times, identifies bottlenecks, and generates a visual text-based Gantt chart timeline.

## When to Use

Use `/cf:calendar` when:
- You need a **30/60/90-day content plan** with specific dates and deadlines
- You want to **schedule production timelines** that account for ContentForge processing time + review buffers
- You need to **assign content to team members** and track who's responsible for what
- You want **Google Calendar events** with reminders for each production milestone
- You're onboarding a new client and need a **structured editorial calendar**
- You want to **identify scheduling conflicts** before they become missed deadlines

**For producing content**, use `/contentforge` or `/batch-process`.
**For auditing what needs refreshing**, use `/cf:audit` first to identify candidates.

## What This Command Does

1. **Load Content Plan** — Import topics from manual input, Google Sheets, or audit recommendations
2. **Calculate Production Timelines** — Work backward from publish dates to determine production start dates, accounting for ContentForge processing time (20-30 min per piece) and review buffer
3. **Schedule Production Windows** — Assign production start/end dates and publish dates for each piece
4. **Team Assignment** — Distribute pieces across team members with workload balancing
5. **Conflict Detection** — Identify deadline bottlenecks where multiple pieces need production on the same day
6. **Calendar Event Creation** — Create Google Calendar events (optional) with reminders for production start, review deadline, and publish date
7. **Visual Timeline** — Generate a text-based Gantt chart showing the full calendar

## Required Inputs

**Minimum Required:**
- **Time Period** — 30, 60, or 90 days (from today or from a specified start date)
- **Content Plan** — Topics to schedule (manual input, Google Sheets, or array)

**Content Plan Input Formats:**

**Manual Input (Interactive):**
```
Topic: AI in Healthcare Trends 2026
Type: article
Publish Date: 2026-03-15
Priority: 1
```

**Google Sheets:**
Sheet with columns: `title`, `content_type`, `publish_date`, `priority`, `brand`, `assigned_to` (optional)

**Array (Quick Mode):**
```
--topics="AI Healthcare Trends:article:2026-03-15:1, CRM for Startups:blog:2026-03-18:2, HIPAA Guide:whitepaper:2026-03-25:1"
```

**Optional:**
- **Team Assignments** — Team member names for workload distribution (e.g., `--team="Alice,Bob,Carol"`)
- **Publish Cadence** — Auto-distribute publish dates: `daily`, `weekly` (default), `biweekly`
- **Start Date** — Calendar start date (default: today)
- **Review Buffer** — Hours between production completion and publish date for human review (default: 24 hours)

## How to Use

### Interactive Mode
```
/cf:calendar
```
**Prompts you for:**
1. Time period (30/60/90 days)
2. Content plan source (manual / Google Sheet URL / paste topics)
3. Publish cadence
4. Team members (optional)
5. Review buffer

### Quick Mode with Google Sheet
```
/cf:calendar --period=60 --sheet=https://docs.google.com/spreadsheets/d/ABC123 --cadence=weekly --team="Alice,Bob"
```

### Quick Mode with Topics Array
```
/cf:calendar --period=30 --topics="AI Healthcare:article:2026-03-15:1, CRM Guide:blog:2026-03-20:2" --cadence=weekly
```

### Import from Audit Recommendations
```
/cf:calendar --period=90 --from-audit=latest --cadence=biweekly
```
Pulls the top refresh and new content recommendations from the most recent `/cf:audit` output and schedules them.

## What Happens

### Step 1: Load Content Plan (1-2 minutes)

Import and validate the content plan.

**Validation Checks:**
- All required fields present (title, content_type, publish_date)
- Publish dates are in the future
- Publish dates fall within the specified time period
- Content types are valid (article, blog, whitepaper, faq, research_paper)
- No duplicate titles

**If publish dates are not provided** (using cadence mode):
- Auto-assign publish dates based on the specified cadence
- Priority 1 items get earlier dates
- Distribute evenly across the time period

**Example:**
```
Content Plan Loaded
================================================================

Time Period: 2026-02-25 to 2026-04-25 (60 days)
Total Pieces: 12
Cadence: Weekly (Tuesdays and Thursdays)

Pieces by Type:
  Articles: 5
  Blogs: 4
  Whitepapers: 2
  FAQs: 1

Pieces by Priority:
  Priority 1 (Urgent): 3
  Priority 2 (High): 5
  Priority 3 (Normal): 4
================================================================
```

### Step 2: Calculate Production Timelines (1-2 minutes)

Work backward from each publish date to determine production windows.

**Production Time Estimates:**
```
Content Type    Production Time    Review Buffer    Total Lead Time
─────────────────────────────────────────────────────────────────
Article         25 min             24 hours         ~1.5 days
Blog            18 min             24 hours         ~1.5 days
Whitepaper      35 min             48 hours         ~2.5 days
FAQ             15 min             24 hours         ~1.5 days
Research Paper  60 min             72 hours         ~3.5 days
```

**Timeline Calculation:**
```
For each piece:
  Publish Date:      [specified or auto-assigned]
  Review Deadline:   Publish Date - Review Buffer
  Production End:    Review Deadline - 1 hour (buffer for output generation)
  Production Start:  Production End - Production Time
  Brief Due:         Production Start - 24 hours (if brief needed)
```

**Example Timeline for One Piece:**
```
"AI Healthcare Trends 2026" (Article, Priority 1)
  Brief Due:         2026-03-13 09:00 AM
  Production Start:  2026-03-14 09:00 AM
  Production End:    2026-03-14 09:30 AM
  Review Deadline:   2026-03-15 09:00 AM
  Publish Date:      2026-03-15 10:00 AM
```

### Step 3: Team Assignment (1 minute)

If team members are specified, distribute pieces across the team with workload balancing.

**Assignment Logic:**
1. Sort pieces by priority (highest first)
2. Assign each piece to the team member with the lightest workload that week
3. Ensure no team member has more than 2 production pieces on the same day
4. Respect any pre-assigned team members from the content plan

**Example:**
```
Team Assignments
================================================================

Alice (5 pieces):
  Week 1: AI Healthcare Trends (article), CRM Guide (blog)
  Week 2: HIPAA Compliance (whitepaper)
  Week 3: Patient Engagement (article)
  Week 4: Data Security FAQ (faq)

Bob (4 pieces):
  Week 1: Telemedicine ROI (article)
  Week 2: Remote Monitoring (blog), Digital Health (blog)
  Week 3: EHR Integration (article)

Carol (3 pieces):
  Week 1: Value-Based Care (whitepaper)
  Week 2: Clinical AI (article)
  Week 3: API Integration (blog)

Workload Balance: Alice 5 | Bob 4 | Carol 3 (balanced within 2)
================================================================
```

### Step 4: Conflict Detection (1 minute)

Identify scheduling bottlenecks.

**Conflicts Detected:**
- **Same-day overload:** More than 3 pieces scheduled for production on the same day
- **Review pile-up:** More than 2 pieces need review on the same day
- **Team overload:** One team member has >2 pieces in the same week
- **Publish cluster:** More than 2 pieces publishing on the same day (audience fatigue risk)

**Example Conflicts:**
```
Scheduling Conflicts Detected
================================================================

WARNING: March 14 — 3 pieces scheduled for production
  AI Healthcare Trends (Alice), Telemedicine ROI (Bob), Value-Based Care (Carol)
  Risk: All 3 need review on March 15 (review pile-up)
  Suggestion: Move "Value-Based Care" production to March 12
              (whitepaper needs 48h review buffer anyway)

WARNING: March 25 — 2 pieces publishing same day
  HIPAA Compliance (whitepaper) and EHR Integration (article)
  Risk: Audience email fatigue if both go to same list
  Suggestion: Move EHR Integration to March 27

Auto-resolved: 1 conflict
  Moved "Value-Based Care" production to March 12 (accepted suggestion)

Remaining: 1 conflict requires manual decision
  March 25 publish cluster — choose which piece to move
================================================================
```

### Step 5: Google Calendar Events (1-2 minutes, optional)

If Google Calendar MCP is connected, create calendar events for each milestone.

**Events Created Per Piece:**
1. **Brief Due** — "CF Brief Due: [Title]" (1 day before production)
2. **Production Start** — "CF Production: [Title]" with description containing content type, brand, word count target
3. **Review Deadline** — "CF Review: [Title]" with link to output file
4. **Publish Date** — "CF Publish: [Title]" with publish instructions

**Event Details:**
- Calendar: Uses default calendar (or specify with `--calendar="Content Team"`)
- Reminders: 1 hour before and 15 minutes before each event
- Color coding: Priority 1 = red, Priority 2 = orange, Priority 3 = blue
- Description: Content type, brand, assigned team member, word count target

**Without Google Calendar MCP:**
Calendar events are skipped. The visual timeline is still generated.

### Step 6: Visual Timeline (Gantt Chart)

Generate a text-based Gantt chart showing the complete calendar.

**Example:**
```
Content Calendar: 2026-02-25 to 2026-04-25 (60 Days)
================================================================

Week 1 (Feb 25 - Mar 3)
  Mon  Tue  Wed  Thu  Fri  Sat  Sun
  25   26   27   28   1    2    3
  ──── ──── ──── ──── ──── ──── ────
       [B]            [P]
       AI Healthcare  AI Healthcare
       >>>>>>>>>>>>>>>>[R][PUBLISH]

       [B] = Brief Due  [P] = Production  [R] = Review

Week 2 (Mar 4 - Mar 10)
  Mon  Tue  Wed  Thu  Fri  Sat  Sun
  4    5    6    7    8    9    10
  ──── ──── ──── ──── ──── ──── ────
  [B]       [P]  [R]  [PUB]
  CRM Guide >>>>>>>>>[PUBLISH]

       [P]  [R]       [PUB]
       Tele ROI >>>>>>[PUBLISH]

... (continues for all weeks)

================================================================
Summary:
  Total Pieces: 12
  Publishing Dates: 12 dates across 8 weeks
  Production Days: 14 unique days with scheduled work
  Team Coverage: Alice (5), Bob (4), Carol (3)
  Calendar Events Created: 48 (4 per piece x 12 pieces)
  Conflicts Resolved: 1 auto, 1 manual pending
================================================================
```

## Output

The complete content calendar includes:

| Section | Description |
|---------|------------|
| **Plan Summary** | Total pieces, time period, cadence, team members |
| **Production Timeline** | Start/end/review/publish dates per piece |
| **Team Assignments** | Workload distribution with weekly breakdown |
| **Conflict Report** | Identified bottlenecks with resolution suggestions |
| **Gantt Chart** | Visual text-based timeline of all production activity |
| **Calendar Events** | Status of Google Calendar event creation (if connected) |
| **Deadline Alerts** | Upcoming deadlines for the next 7 days |

## Output Example

```
Content Calendar Created
================================================================

Period: 60 days (2026-02-25 to 2026-04-25)
Pieces: 12 pieces across 8 weeks
Cadence: Weekly (Tuesdays and Thursdays)
Team: Alice (5), Bob (4), Carol (3)

Production Schedule:
  This Week: 2 pieces starting production
  Next Week: 3 pieces starting production
  Week 3-4: 4 pieces
  Week 5-8: 3 pieces

Calendar Events: 48 events created in "Content Team" calendar
Conflicts: 1 auto-resolved, 1 pending manual decision

Next Deadline: "AI Healthcare Trends" brief due Feb 27, 9:00 AM (Alice)
================================================================
```

## MCP Integrations

### Optional (HTTP)
- **Google Calendar** — Create calendar events with reminders for production milestones. Events are color-coded by priority. Without it, the calendar is still fully functional as a text-based timeline.

### Optional (npx)
- **Google Sheets** — Import content plan from a shared Google Sheet. Export the generated calendar back to a Sheet for team access. Without it, use manual input or CSV.

### Fallback (No MCP)
Without MCP connections, the calendar provides a complete text-based timeline with production dates, team assignments, and conflict detection. Events can be manually added to any calendar application using the dates from the timeline.

## Troubleshooting

### "Publish dates conflict with weekends"
**Solution:** By default, publish dates are assigned to weekdays only. Use `--include-weekends` to allow weekend publishing.

### "Team member overloaded"
**Cause:** More pieces than team members can handle in the time period.
**Solution:** Extend the time period, add team members, or reduce the number of pieces. The calendar will warn you during conflict detection.

### "Calendar events not created"
**Cause:** Google Calendar MCP not connected or authorization not granted.
**Solution:** Run `/cf:integrations` to check Google Calendar status. Run `/cf:connect google-calendar` for setup instructions.

### "Production timeline too tight"
**Cause:** Publish dates are too close together for the number of pieces.
**Solution:** Increase the review buffer (`--review-buffer=48`) or spread publish dates further apart. Whitepapers and research papers need longer lead times.

## Limitations

- **Time zones** — Calendar events use the system's default time zone. Multi-timezone team support planned for v2.2.
- **Auto-rescheduling** — Calendar does not automatically reschedule when a piece is delayed. Manual update required.
- **Google Calendar only** — No Outlook, Apple Calendar, or iCal export yet (planned for v2.2).
- **Cadence patterns** — Supports daily, weekly, and biweekly. Custom cadence patterns (e.g., "Mon/Wed/Fri") planned for v2.2.
- **Maximum pieces** — Tested with up to 50 pieces per calendar. Larger calendars may have slower conflict detection.

## Agent Used

None. This skill uses deterministic scheduling logic (backward timeline calculation, workload balancing, conflict detection) without agent-based reasoning.

## Related Skills

- **[/cf:audit](../cf-audit/SKILL.md)** — Audit content library to identify what needs refreshing (feeds into calendar)
- **[/cf:brief](../cf-brief/SKILL.md)** — Generate briefs for calendar topics before production
- **[/contentforge](../contentforge/SKILL.md)** — Produce content for scheduled pieces
- **[/batch-process](../batch-process/SKILL.md)** — Process multiple calendar pieces in parallel
- **[/content-refresh](../content-refresh/SKILL.md)** — Refresh content identified in the calendar

---

**Version:** 3.4.0
**Agent:** None (deterministic scheduling)
**MCP:** Google Calendar (optional, HTTP), Google Sheets (optional, npx)
**Processing Time:** 3-8 minutes (varies by plan size)
**Output:** Content calendar with timeline, assignments, conflict report, and optional calendar events
