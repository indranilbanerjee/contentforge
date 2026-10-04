# ContentForge always-on recipes

Recurring jobs that keep a brand's content lifecycle loop turning without anyone remembering to run it: measure what you published, audit the library, plan the next quarter. Written for Claude Code routines and scheduled tasks, Claude Tag in Slack, Grok Bot, Gemini Spark and Hermes cron.

The loop is already built from files, not conversation memory. `/contentforge:cf-aeo-check` appends to `aeo/checks.json`, `/contentforge:audit-content` records `audits/audit-<stamp>.json`, and `/contentforge:cf-calendar --from-audit=latest` reads that record back, all under the brand directory. That is what makes it schedulable: a job that runs next month finds what this month's job left behind. It is also why the one non-negotiable prerequisite below is the brand directory.

## What to schedule, and what not to

| Job | Cadence | What it does | Durable output |
|---|---|---|---|
| AEO sweep | Monthly | `/contentforge:cf-aeo-check` on each published piece that is due | Appends to `aeo/checks.json` |
| Library audit and record | Monthly, after the sweep | `/contentforge:audit-content`, then the audit record is stored | `audits/audit-<stamp>.json` |
| Quarterly calendar | Quarterly, after that month's audit | `/contentforge:cf-calendar --period=90 --from-audit=latest` | None: the calendar is the run's final message |

Order matters. The audit's freshness model reads `aeo/checks.json`, and a piece whose recorded AI citations were lost since the previous check is scored as decaying whatever its age says, so the sweep goes first. The calendar reads the newest audit record by file contract; with no record it must say so and stop rather than reconstruct recommendations from memory, so the calendar runs after a monthly audit has succeeded (the examples below put it on the second of the month).

Deliberately not scheduled: `/contentforge:create-content`, `/contentforge:content-refresh` and `/contentforge:publish`. Production has human stops by design: the title is confirmed by a person (or passed with `--title`), generated images wait for approval, and a finished piece goes to review. These recipes schedule the half of the loop that reads and records, and they end with a report a person acts on.

## Before you schedule anything

### 1. The brand directory must exist in the scheduled session

Everything above lives under one directory per brand. ContentForge resolves it in this order: `$CLAUDE_MARKETING_HOME` if set, else `$CLAUDE_PLUGIN_DATA` (or `$PLUGIN_DATA`) if set and the directory exists, else `~/.claude-marketing`. The brand's own folder inside it is named by its slug, and holds the brand profile (`Brand-Guidelines/`), `aeo/`, `audits/`, `tracking/` and `runs/`.

A scheduled session is a fresh session. If it cannot see that directory it will not find your brand profile, will have no AEO history to compare against, and will find no audit for the calendar to read. To print the directory a session will actually use:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/plugin-metadata.py --section environment
python -c "import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts'); import _common; print(_common.brand_dir('<slug>'))"
```

Where each platform's scheduled session runs decides whether it sees your files. Taken from each platform's own documentation (retrieved 2026-10-04; sources at the end):

| Platform | Where the scheduled run executes | Sees your local brand directory? |
|---|---|---|
| Claude Code Desktop scheduled task | Your machine | Yes. It only fires while the app is open and the computer is awake. |
| Claude Code routine (cloud) | Anthropic-managed cloud, a fresh clone of the repositories you select | No. The documented comparison table says "Access to local files: No (fresh clone)". |
| Claude Code `/loop` | Your machine, inside an open session | Yes, but recurring tasks expire after seven days, so it is not a monthly mechanism. |
| Claude Tag (Slack) | An ephemeral cloud sandbox per thread | No. "Files that exist only in the sandbox" do not survive between replies. |
| Hermes cron | The machine running the Hermes gateway daemon | Yes. |
| Grok Bot | "Their own computer in the cloud" | Not documented. |
| Gemini Spark | Not documented on the cited page | Not documented. |

So for a plugin that keeps its state in files, the reliable homes are a Desktop scheduled task or Hermes cron on a machine that holds the brand directory. The cloud options can work only if you make the brand directory reachable, and that is your design decision, not something ContentForge does for you. Two ways, both untested here: keep the brand directory in a private repository the session clones and point `CLAUDE_MARKETING_HOME` at it (a routine's environment can carry variables, and a run pushes to a `claude/` branch unless told otherwise, so the new `audits/` and `aeo/` files need merging back), or use the Drive routing that `/contentforge:cf-cowork-setup` configures for Cowork (see the persistence section of `COWORK-GUIDE.md`, which says teams that want the lifecycle loop should treat Drive routing as required). Brand profiles can hold client details; a repository that carries one must be private.

### 2. Write the prompt so nothing has to be asked

A scheduled run cannot answer questions. `/contentforge:audit-content` asks for its content source when it is not given one, and `/contentforge:cf-calendar` has an interactive mode, so every input goes into the prompt: the brand slug, the content source, the period, the cadence. The Claude Code routines and Hermes cron documentation say the same thing in their own words: a routine's prompt "must be self-contained and explicit about what to do and what success looks like", and a Hermes cron job's prompt "must contain everything the agent needs".

Start every prompt with the brand-directory check and an instruction to stop, not improvise, when it fails. Never let a scheduled run fall back to `/contentforge:brand-setup`: that would quietly create a blank brand next to the real one.

### 3. Keep the job read-and-record

Attach no connector the job does not need. A cloud routine includes all your connectors by default and, per its documentation, can use every tool from an included connector, writes included, without asking. `/contentforge:cf-calendar` creates Google Calendar events when that connector is present, and the audit can export to a Sheet; for an unattended job, leave those connectors off unless creating the events is exactly what you want.

### 4. A green run is not a finished run

The routines documentation says it plainly: a green status "does not mean the task in your prompt succeeded". So every prompt below ends by printing one line per outcome, `RECORDED` or `NOT RECORDED` with a reason, and you check the stores after the first run and after each cycle:

```bash
# A new audit-<stamp>.json with this run's stamp should be listed (count rises by one)
python ${CLAUDE_PLUGIN_ROOT}/scripts/audit-ledger.py list --brand <slug>

# Exit 1 means no audit is recorded yet, which is what the quarterly calendar would also see
python ${CLAUDE_PLUGIN_ROOT}/scripts/audit-ledger.py latest --brand <slug>
```

Open `aeo/checks.json` in the brand directory and look for today's `checked_at` entries.

## The prompts

Replace `<slug>`, `<Brand Name>`, the URL list and the content source. Keep the step order.

### Monthly: AEO sweep, then audit and record

```text
Unattended monthly measurement job for ContentForge brand "<slug>" (display name "<Brand Name>").
Nobody can answer questions. If you cannot complete a step, stop and say which step and why. Never guess.

1. Brand directory check. Print the brand directory this session uses and confirm it exists and
   contains the brand profile under Brand-Guidelines/. If not, reply "BRAND DIRECTORY NOT FOUND" and
   stop. Do not run brand-setup. Do not create a blank brand.

2. AEO sweep. For each published URL listed below, run
   /contentforge:cf-aeo-check <url> --brand=<Brand Name>
   Check only the pieces that are due under that skill's own cadence (published at least two weeks
   ago; about 2, 6 and 12 weeks after publication, then quarterly), and no more than 10 pieces in
   this run. Every check must be appended to aeo/checks.json. Published URLs:
   <url 1>
   <url 2>

3. Library audit. Run
   /contentforge:audit-content <content source> --scope=both --threshold=12
   where the content source is <Drive folder URL | site URL | CSV path>. The audit is not finished
   until its record is stored under audits/ (the skill's audit-ledger.py record step exits 0).

4. Report. For each URL: "AEO <url>: RECORDED" or "AEO <url>: NOT RECORDED - <reason>", or
   "AEO <url>: not due". Then "AUDIT RECORDED: <path>" or "AUDIT NOT RECORDED - <reason>".
   Add the top refresh candidates from the audit and each recommended scope. Do not start any refresh.
```

`cf-aeo-check` measures Google-observable signals only, unless an AEO-tracking connector is present, and then it labels the data's source. Do not ask the job for more than that.

### Quarterly: calendar from the latest audit

```text
Unattended quarterly planning job for ContentForge brand "<slug>" (display name "<Brand Name>").
Nobody can answer questions. If you cannot complete a step, stop and say which step and why. Never guess.

1. Brand directory check, exactly as in the monthly job. Stop if it fails.

2. Run /contentforge:cf-calendar --period=90 --from-audit=latest --cadence=biweekly
   Where the skill offers a choice, use its documented default. If it reports that no audit is
   recorded for this brand, say exactly that and stop: do not rebuild recommendations from memory.

3. Do not create calendar events and do not start any production. Post the finished calendar,
   including its conflict report, as your final message.
```

The calendar is not written to a ContentForge store. It lives in the run's transcript, so point the job at somewhere a person will read it: the Slack channel, the Hermes delivery target, or the routine's run page.

## Platform recipes

### Claude Code

**Desktop scheduled task (local, recommended when the brand directory lives on that machine).** In the Desktop app's Code tab: Routines, New routine, then choose Local. Paste a prompt as the Instructions and pick the working folder. The schedule picker offers Manual, Hourly, Daily, Weekdays and Weekly; for "the first of each month" the documentation says to ask Claude in any Desktop session to set the schedule in plain language. Things the documentation says to plan around: tasks run only while the app is running and the computer is awake, a missed run gets one catch-up when the app next starts (within seven days), and a task in Manual permission mode stalls on any tool it was never allowed, so click Run now once after creating it and choose always allow for each prompt.

**Routine (cloud).** Run `/schedule` in a Claude Code session to create one conversationally, then `/schedule update` to set a custom cron such as `7 6 1 * *` for the monthly job and `13 6 2 1,4,7,10 *` for the quarterly one. The minimum interval is one hour, and a few minutes past the hour (`:07`) starts closer to time than exactly on it. The documentation does not say which timezone a custom cron expression is read in, so state the timezone to Claude and confirm the next-run time it reports. Two prerequisites you must satisfy yourself, because the routines documentation describes a fresh clone with skills "committed to the cloned repository": ContentForge's skills and scripts have to be reachable from the repository the routine clones, and the brand directory has to be reachable as described above. Routines are in research preview and the documentation says behavior and limits may change.

**`/loop`.** Not for these jobs: session-scoped, and recurring tasks expire after seven days.

### Claude Tag in Slack

Set a routine from the channel it should report in, by describing schedule and work in one message and naming the timezone, because schedules run in UTC:

```text
@Claude on the 1st of every month at 06:07 UTC, run the ContentForge monthly measurement job
for brand "<slug>": <paste the monthly prompt>. Post the report in this channel.
```

Send `@Claude !routines` afterwards to confirm the time Claude set (it lists schedules in UTC). Claude Tag is in public beta for Team and Enterprise plans. Two things from the documentation shape the recipe. A thread locks in the skills and plugins its scope had when it started, so ContentForge has to be among what your admin configured for that scope before you start a fresh top-level thread; the documentation does not say how a third-party plugin gets added, so ask your admin. And the sandbox is ephemeral: work that must outlive a run has to be pushed or posted somewhere durable, so Tag is the weakest home for the file-contract stores. Use it for the human-facing half, posting the monthly report and the quarterly calendar where the team reads them, and keep the stores on a machine that persists. Whether ContentForge's Drive routing activates inside a Tag sandbox is untested.

### Grok Bot

Unverified, and the cited page is thin. It describes Bots as "digital teammates" with "their own computer in the cloud" and "easy-to-set-up routines": you ask a Bot to follow along the next time you do the job, "so it can run on its own after that". It does not document a schedule syntax, whether a Bot can load a plugin such as ContentForge's Grok plugin, or what survives between runs. A cautious recipe: do the monthly job once with the Bot watching, using the monthly prompt above, then check what it kept. If the brand directory is not in the Bot's own computer after the run, it did not persist, and the quarterly calendar will have no audit to read.

### Gemini Spark

Unverified. The cited support page lists Schedules and Skills for Gemini Spark and says connected apps work through their MCP server URLs, with availability limited to Google AI Pro and Ultra subscribers in the regions it names. It does not say how a schedule is created, where it runs, or whether files persist between runs, and it does not say whether Spark can load a ContentForge skill. Use it for the human-facing prompt only: paste the monthly or quarterly prompt as the scheduled instruction, and check the output yourself before trusting it to keep state.

### Hermes cron

Hermes runs each cron job in a fresh agent session inside its gateway daemon, so the job sees the machine's files and the prompt has to carry everything. Per the Hermes documentation, jobs are created with `hermes cron create "<schedule>" "<prompt>" --skill <name>`, a schedule can be a cron expression, results save under `~/.hermes/cron/output/` and job definitions persist in `~/.hermes/cron/jobs.json`. ContentForge's Hermes adapter registers its skills, so attach the one the job needs; confirm the exact registered name in your install. Split the monthly job in two, an hour apart, so each prompt stays short and a failure in one is visible on its own:

```bash
# 06:07 on the 1st: AEO sweep (use the monthly prompt's steps 1, 2 and 4)
hermes cron create "7 6 1 * *" "<AEO sweep prompt>" --skill cf-aeo-check --workdir <brand work dir>

# 07:07 on the 1st: audit and record (steps 1, 3 and 4)
hermes cron create "7 7 1 * *" "<audit prompt>" --skill cf-audit --workdir <brand work dir>

# 06:13 on the 2nd of Jan/Apr/Jul/Oct: calendar from the latest audit
hermes cron create "13 6 2 1,4,7,10 *" "<quarterly prompt>" --skill cf-calendar --workdir <brand work dir>
```

Set `CLAUDE_MARKETING_HOME` in the gateway daemon's environment so these jobs and your interactive sessions use the same brand directory. Choose the delivery target (the documentation lists `local` for files only and messaging platforms such as `slack`) so the quarterly calendar reaches a person.

## What these recipes do not promise

- **They have not been run unattended on every platform.** The ContentForge side, the commands, flags, scripts and stores named here, is checked by `tests/test_always_on_recipes.py`. The platform side comes from the cited documentation, retrieved 2026-10-04, and several of these products are in preview or beta.
- **They do not produce or publish content.** Everything that changes the page itself stays behind a human stop.
- **They do not measure every AI engine.** `cf-aeo-check` is Google-observable unless an AEO-tracking connector is present.
- **They do not guarantee the run happened.** A scheduled platform can skip a run (a sleeping computer, an expired connection, a usage limit). The `RECORDED` lines and the store checks above are how you find out.

## Sources

Retrieved 2026-10-04. Platform behavior changes; re-check before relying on a detail.

- Claude Code routines: https://code.claude.com/docs/en/routines
- Claude Code Desktop scheduled tasks: https://code.claude.com/docs/en/desktop-scheduled-tasks
- Claude Code `/loop` and in-session scheduling: https://code.claude.com/docs/en/scheduled-tasks
- Claude Tag, how it works: https://claude.com/docs/claude-tag/concepts/how-it-works
- Claude Tag, set up routines: https://claude.com/docs/claude-tag/users/proactivity
- Grok Bot: https://x.ai/news/grok-bot-more-plans
- Gemini Spark: https://support.google.com/gemini/answer/17171264
- Hermes scheduled tasks (cron): https://hermes-agent.nousresearch.com/docs/user-guide/features/cron
