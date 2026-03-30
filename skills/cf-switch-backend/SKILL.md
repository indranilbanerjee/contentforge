---
name: cf-switch-backend
description: Switch tracking backend (local/airtable/google) with optional data migration
disable-model-invocation: true
argument-hint: "[local | airtable | google] [--migrate]"
effort: high
---

# Switch Tracking Backend

Switch ContentForge's tracking and delivery backend between **Google Sheets + Drive**, **Airtable**, or **Local filesystem**. Optionally migrate existing tracking data and output files to the new backend.

## When to Use

- Switching from local (default) to a cloud backend for collaboration
- Migrating from Google to Airtable (or vice versa) for simpler auth
- Downgrading to local when cloud access isn't needed
- Checking current backend status before switching

## How to Use

```
/cf:switch-backend airtable
/cf:switch-backend google
/cf:switch-backend local
/cf:switch-backend --status
```

## What This Command Does

### Step 1: Identify Current Backend

Read the active brand profile's `tracking.backend` field.

Report current state:
```
Current backend: local
Records: 47 tracking records
Output files: 42 files in ~/.claude-marketing/{brand}/tracking/outputs/
```

### Step 2: Validate Target Backend

**If switching to Airtable:**
1. Check `AIRTABLE_TOKEN` environment variable exists
2. If missing, guide through setup:
   - Go to [airtable.com/create/tokens](https://airtable.com/create/tokens)
   - Create a Personal Access Token with `data.records:read` and `data.records:write` scopes
   - Select the base that will hold tracking data
   - Set the environment variable: `export AIRTABLE_TOKEN=patXXXXXXXX`
3. Ask for the Airtable Base ID (from the base URL: `airtable.com/appXXXXXXXXX/...`)
4. Verify access by running:
   ```
   python3 {scripts_dir}/airtable-tracker.py --action init --base-id {base_id}
   ```

**If switching to Google Sheets + Drive:**
1. Check Google credentials at `~/.claude-marketing/google-credentials.json`
2. If missing, guide through setup:
   - Go to Google Cloud Console > IAM & Admin > Service Accounts
   - Create a project (or use existing)
   - Enable Google Sheets API and Google Drive API
   - Create a Service Account and download the JSON key
   - Save to `~/.claude-marketing/google-credentials.json`
   - Create a Google Sheet and share it with the service account email (Editor)
   - Create a Google Drive folder and share it with the service account email (Editor)
3. Ask for the Google Sheet ID and Drive folder ID
4. Verify access by running:
   ```
   python3 {scripts_dir}/sheets-tracker.py --action init --sheet-id {sheet_id}
   ```

**If switching to Local:**
- No setup needed — works immediately
- Run init to ensure directory exists:
  ```
  python3 {scripts_dir}/local-tracker.py --action init --brand "{brand}"
  ```

### Step 3: Offer Migration

If the current backend has existing records:

```
You have 47 tracking records and 42 output files on 'local'.
Would you like to migrate this data to Airtable?
  1. Yes — Copy all records and files to the new backend
  2. No — Start fresh (existing data preserved but not synced)
  3. Skip — Just switch, decide on migration later
```

**If yes**, run:
```
python3 {scripts_dir}/backend-migrator.py --action migrate --brand "{brand}" --from {current} --to {target} [backend-specific args]
```

Report migration results:
```
Migration complete:
  Records migrated: 47
  Files migrated: 42
  Files failed: 0
  Source data preserved at: ~/.claude-marketing/{brand}/tracking/
```

### Step 4: Update Brand Profile

Update the brand profile JSON:
- Set `tracking.backend` to the new backend value
- Fill in backend-specific config (base_id, sheet_id, folder_id, etc.)

### Step 5: Confirm

```
Backend switched to Airtable.
  New tracking records → Airtable base appXXXXXX
  Output files → Airtable attachment fields
  Previous data preserved at: ~/.claude-marketing/{brand}/tracking/

Run /cf:switch-backend --status to verify anytime.
```

## Backend Comparison

| Factor | Google Sheets + Drive | Airtable | Local |
|--------|----------------------|----------|-------|
| Auth setup | Service account (~5 min) | Personal token (~2 min) | None |
| Tracking | Google Sheets | Airtable records | JSON file |
| File delivery | Google Drive | Attachment field | Local filesystem |
| Collaboration | Share via Google | Share via Airtable | Single user |
| Free tier | 15GB Drive | 1,000 records + 10GB | Unlimited |
| Offline | No | No | Yes |

## Check Status

Run with `--status` flag to check current backend health:

```
/cf:switch-backend --status
```

This runs:
```
python3 {scripts_dir}/backend-migrator.py --action status --brand "{brand}" --from {current_backend}
```

## Important Notes

- **Migration is additive** — source data is never deleted
- **Migration is idempotent** — running twice won't create duplicates
- **Migration is resumable** — if interrupted, re-run picks up where it left off
- **You can switch back anytime** — data is preserved on all backends you've used
- **The pipeline uses whichever backend is set** in `tracking.backend` — switching takes effect immediately for the next content run

## Related Skills

- **[/cf:style-guide](../cf-style-guide/SKILL.md)** — Brand setup (Step G sets initial backend)
- **[/cf:integrations](../cf-integrations/SKILL.md)** — Check all connector status
- **[/cf:connect](../cf-connect/SKILL.md)** — Set up individual connectors
