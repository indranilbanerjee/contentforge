---
description: Print the absolute path to the user-visible ContentForge output folder and open it in the OS file manager
argument-hint: "[brand] (omit to use the active brand)"
---

# Output Folder

Show the user where ContentForge actually saves the finished `.docx` files, and (when supported) open that folder in the OS file manager. This is the answer to "where did my file go?" — a real question from the v3.12.2 user-feedback cycle.

## Trigger

User runs `/contentforge:output-folder`, or asks any variant of "where did my file save", "I can't find the output", "open output folder".

## Background

ContentForge writes two copies of every finished `.docx`:

1. **Internal tracking copy** at `~/.claude-marketing/{brand}/tracking/outputs/{year}/{month}/{slug}_v1.0.docx`. This is the system-of-record for `/contentforge:cf-analytics`, `/contentforge:cf-audit`, etc. It lives inside a dotfolder that Windows hides by default — users rarely find it.
2. **User-visible published copy** at `~/Documents/ContentForge/{brand}/{content_type}/{YYYY-MM}/{slug}.docx` (or wherever `$CONTENTFORGE_PUBLISH_DIR` points). This is the one to surface.

The published copy was added in v3.12.3 specifically because end users reported "the file isn't saving on local drive" — it was saving, just somewhere they couldn't see.

## Process

### Step 1: Resolve the path

The published-output directory is:

- `$CONTENTFORGE_PUBLISH_DIR/{brand}/` if the env var is set, or
- `~/Documents/ContentForge/{brand}/` otherwise.

Default to the active brand if no argument was provided. If neither is available, prompt: "Which brand's output folder? Run `/contentforge:output-folder <brand>` or set up a brand with `/contentforge:brand-setup`."

### Step 2: Print the absolute path

Always show the path explicitly in the conversation so the user can copy/paste it even if the OS open step fails:

```
📂 ContentForge output folder for {brand}:
   {absolute_path}

   Subfolders are organized by content type (article / blog / whitepaper / faq / research_paper)
   and by month (YYYY-MM). The newest run is in the latest month folder.
```

### Step 3: Open the folder in the OS file manager

Pick the platform-appropriate command. The plugin runs on Windows (most users), macOS, and Linux:

```bash
# Windows
start "" "{absolute_path}"

# macOS
open "{absolute_path}"

# Linux
xdg-open "{absolute_path}"
```

If the open step fails (no display, headless environment, no associated handler), don't error — the user already has the path from Step 2.

### Step 4: If the folder doesn't exist yet

`~/Documents/ContentForge/{brand}/` is created the first time a pipeline run finishes Phase 8. If the folder is missing, say:

```
The output folder doesn't exist yet — that means no `/contentforge:create-content` run
has completed for "{brand}" yet. Run a pipeline first, then come back here.

Expected location after the first successful run:
   {absolute_path}
```

Do NOT create the folder pre-emptively — empty folders are noise.

## Configuration

End users (or admins setting up a shared workstation) can redirect the visible-copy location with the `CONTENTFORGE_PUBLISH_DIR` env var:

```bash
# Persistent — add to your shell profile
export CONTENTFORGE_PUBLISH_DIR="$HOME/Dropbox/Marketing/ContentForge"

# Per-run
CONTENTFORGE_PUBLISH_DIR="/mnt/team-share/ContentForge" /contentforge:create-content ...
```

The internal tracking copy (under `~/.claude-marketing/`) is unchanged — that stays as the plugin's system-of-record. The env var only affects the published copy.

## Related

- [`commands/create-content.md`](create-content.md) — the pipeline that produces the files this command reveals.
- [`scripts/local-tracker.py`](../scripts/local-tracker.py) — implements the dual-copy save (`mark_complete` writes both paths and returns them in its JSON output).
