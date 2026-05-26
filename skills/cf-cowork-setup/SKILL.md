---
name: cf-cowork-setup
description: "One-shot setup that wires ContentForge for team usage in Anthropic Cowork. Verifies Cowork environment, checks for a Google Drive integration, creates the canonical Drive folder layout, and confirms the team-ready output routing. Use this the first time a Cowork user installs ContentForge OR when files aren't landing in Drive."
argument-hint: "[--brand <name>] [--drive-root <folder-name>]"
effort: low
---

# /contentforge:cf-cowork-setup

The one-time setup that makes ContentForge usable in Cowork by a team. Wires up the Cowork → Drive routing so generated `.docx` files, brand profiles, and run records actually persist somewhere the team can reach.

## Why this skill exists

Cowork is the most user-friendly Anthropic surface for non-CLI users — marketers, content teams, agency staff. The natural team workflow is "everyone uses Cowork; outputs live in our shared Google Drive". But ContentForge's filesystem layer was originally designed for local Claude Code (writes to `~/Documents/ContentForge/` on the host). In Cowork that path is the Linux sandbox — gone at session end, invisible to the team.

v3.12.9 fixed this with environment-aware routing: when Cowork is detected AND a Drive MCP is configured, the output-manager agent uploads to Drive instead. This skill is the one-shot setup that ensures both conditions are true before you start producing real content.

## Behavior

### Step 1 — Verify Cowork environment

```bash
python scripts/plugin-metadata.py --section environment
```

Parse the JSON. Three branches:

**`environment == "cowork-sandbox"`** — Proceed to Step 2.

**`environment == "claude-code-windows"` / `"-mac"` / `"-linux"`** — Tell the user:

> "You're running in local Claude Code, not Cowork. The Cowork-specific Drive routing isn't needed here — your files will land in `~/Documents/ContentForge/<brand>/` on your host as designed. If you ALSO want Drive backups for team sharing, run `/contentforge:brand-setup` and pick the Google Sheets + Drive backend."

Don't run the rest of this skill.

**`environment == "unknown"`** — Show the indicators from the JSON and ask the user where they're running, then proceed assuming Cowork (since unknown-from-Cowork is most likely).

### Step 2 — Verify a Drive MCP is connected

Scan your available tools for any Google Drive MCP. Common signatures:

- `mcp__<id>__create_file`, `mcp__<id>__read_file_content`, `mcp__<id>__search_files`, `mcp__<id>__list_folder_items` — Anthropic-platform Drive integration (Settings → Integrations → Google Drive in Cowork)
- `mcp__pipedream-google-drive__*` — Pipedream aggregator
- `mcp__composio-google-drive__*` — Composio
- `mcp__zapier-google-drive__*` — Zapier
- Any tool whose name combines "drive" with "create" / "upload" / "search"

**If a Drive MCP is found:** confirm to the user which one ("Found: Anthropic platform Google Drive integration. I'll use this.") and proceed to Step 3.

**If NO Drive MCP is found:** stop the wizard with a clear message:

> "Cowork-mode ContentForge needs a Google Drive integration before it can save files anywhere your team can reach. Easiest setup (60 seconds):
>
> 1. In Cowork, click your profile menu → **Settings** → **Integrations**
> 2. Find **Google Drive** in the list → click **Connect**
> 3. Sign in with the Google account that owns your team's shared Drive
> 4. Come back here and re-run `/contentforge:cf-cowork-setup`
>
> Alternative for teams that prefer Pipedream / Composio / Zapier: add the relevant connector via `/contentforge:cf-add-integration` and re-run."

### Step 3 — Verify or create the canonical Drive folder

Default folder name: `ContentForge` (under "My Drive" or wherever the user prefers). If `--drive-root <name>` was passed, use that instead.

Use the Drive MCP to:

1. Search for a top-level folder named `ContentForge` (or the user's `--drive-root`)
2. If it exists, confirm the user wants to use it. Show its URL.
3. If it doesn't exist, create it. Show the URL of the new folder.

Then create the subfolder skeleton:

```
ContentForge/
├── _brands/                  <-- brand-profile JSONs persist here per brand
├── _runs/                    <-- per-run checkpoints (resume across sessions)
└── (brand folders created on first content run)
    └── <brand name>/
        └── <content type>/
            └── <YYYY-MM>/
                └── <slug>.docx
```

Don't create empty brand subfolders yet — those are auto-created by the output-manager agent during the first content run for that brand. Just `_brands/` and `_runs/` need to exist.

### Step 4 — Store the Drive root reference + team namespace (v3.12.10)

**Multi-team isolation**: ask the user "what's your team's Drive root folder name?" (default: `ContentForge`). Different teams use different folder names → automatic namespace isolation. Examples:
- Solo / small team: `ContentForge` (default)
- Agency named "ACME": `ACME ContentForge`
- Two distinct teams sharing one Drive: each picks their own name

Then write the config via the canonical script (NOT a hand-written JSON file — use the script so the format stays in sync with the rest of the toolchain):

```bash
python scripts/drive-sync-state.py --action write-config --data '{
  "environment": "cowork-sandbox",
  "drive_root_folder_name": "<team folder name chosen>",
  "drive_root_folder_id": "<id from Step 3>",
  "drive_root_folder_url": "<webViewLink from Step 3>",
  "drive_mcp_tool_prefix": "<prefix detected in Step 2, e.g. mcp__abc123__>"
}'
```

The script writes to `~/.claude-marketing/_cowork-config.json` and adds a `configured_at` timestamp automatically.

Future Cowork sessions: every ContentForge operation (`brand-setup`, `create-content`, `resume`, etc.) reads this config first. If it exists AND the Drive folder still exists, all I/O routes to that root. If a different team picked a different folder name, their config lives at the same path but points elsewhere — no collision.

To verify it was written correctly:
```bash
python scripts/drive-sync-state.py --action read-config
```

### Step 5 — Set the user's expectations

Show a clean summary:

```
ContentForge is now wired for Cowork team usage:

Environment:           Cowork sandbox (Linux)
Drive integration:     <name>
Output root in Drive:  My Drive/<folder name> (link)
Config saved at:       ~/.claude-marketing/_cowork-config.json

What this means in practice:

- /contentforge:create-content -> final .docx lands in
  Drive/<folder>/{brand}/{content_type}/{YYYY-MM}/{slug}.docx
- /contentforge:brand-setup -> brand profile JSON lands in
  Drive/<folder>/_brands/{brand-slug}/profile.json (persists across sessions)
- /contentforge:resume -> checkpoint files in
  Drive/<folder>/_runs/{run-id}/ (works across sessions / browser tabs)
- Your team accesses everything via Google Drive directly -- no
  Cowork-specific paths to remember.

Next step:
  /contentforge:brand-setup "Your Brand Name"
```

### Step 6 — Optional: kick off a brand setup

If `--brand <name>` was passed, automatically launch `/contentforge:brand-setup "<name>"` after the summary. This makes the very first run "one command, fully set up."

## What this skill does NOT do

- It does not change ContentForge's behavior in local Claude Code (where host filesystem is fine).
- It does not migrate existing local-mode brands to Drive. To do that after the fact: re-run `/contentforge:brand-setup "<brand>"` in Cowork after this skill finishes.
- It does not create a service-account JSON. Cowork-mode uses the MCP path exclusively (simpler, no Google Cloud setup).
- It does not check whether your Drive has enough space. (Cowork-typical content runs produce 50KB-2MB per .docx, so this is rarely a concern, but flag it if you hit a quota error during a real run.)

## See also

- `/contentforge:cf-environment` — runtime capability matrix (use to confirm Cowork+Drive is detected after setup)
- `/contentforge:brand-setup` — actual brand setup (now Drive-default in Cowork)
- `scripts/plugin-metadata.py --section environment` — the underlying probe
- README "Cross-platform compatibility" section — canonical doc for which surface to use
