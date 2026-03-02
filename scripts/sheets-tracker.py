#!/usr/bin/env python3
"""
sheets-tracker.py
=================
Google Sheets tracker for ContentForge content pipeline.

Handles all tracking sheet operations: adding content requests,
updating status, reading pending items, and marking completions.
Works in Cowork VM (auto-installs dependencies on first run).

Usage:
    python sheets-tracker.py --action init --sheet-id SHEET_ID
    python sheets-tracker.py --action add-row --sheet-id SHEET_ID --data '{"brand":"Acme","title":"AI Content",...}'
    python sheets-tracker.py --action get-pending --sheet-id SHEET_ID
    python sheets-tracker.py --action get-pending --sheet-id SHEET_ID --brand "Acme Corp"
    python sheets-tracker.py --action update-row --sheet-id SHEET_ID --row-id REQ-001 --data '{"status":"in_progress"}'
    python sheets-tracker.py --action mark-complete --sheet-id SHEET_ID --row-id REQ-001 --data '{"quality_score":9.0,...}'
    python sheets-tracker.py --action get-row --sheet-id SHEET_ID --row-id REQ-001

Credentials: Reads service account JSON from --credentials flag
             (default: ~/.claude-marketing/google-credentials.json)
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Auto-install dependencies ───────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    import subprocess
    print("Installing required packages (first run only)...", file=sys.stderr)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "gspread", "google-auth"],
        stdout=subprocess.DEVNULL,
    )
    import gspread
    from google.oauth2.service_account import Credentials

# ── Constants ───────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

DEFAULT_CREDENTIALS = Path.home() / ".claude-marketing" / "google-credentials.json"

# Tracking sheet column headers (A-T, 20 columns)
HEADERS = [
    "requirement_id",       # A
    "brand",                # B
    "content_type",         # C
    "title",                # D
    "target_audience",      # E
    "word_count_target",    # F
    "priority",             # G — 1=highest, 5=lowest
    "status",               # H — pending/in_progress/completed/failed/review_required
    "created_at",           # I
    "started_at",           # J
    "completed_at",         # K
    "quality_score",        # L
    "content_quality",      # M
    "citation_integrity",   # N
    "brand_compliance",     # O
    "seo_performance",      # P
    "readability",          # Q
    "actual_word_count",    # R
    "drive_url",            # S
    "notes",                # T
]

DEFAULT_TAB = "ContentForge Tracking"


# ── Auth ────────────────────────────────────────────────────────────

def get_client(credentials_path):
    """Create authenticated gspread client."""
    creds_path = Path(credentials_path).expanduser()
    if not creds_path.exists():
        return None, f"Credentials file not found: {creds_path}"
    try:
        creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
        client = gspread.authorize(creds)
        return client, None
    except Exception as e:
        return None, f"Authentication failed: {e}"


def get_worksheet(client, sheet_id, tab_name=DEFAULT_TAB):
    """Get or create the tracking worksheet."""
    try:
        spreadsheet = client.open_by_key(sheet_id)
    except gspread.SpreadsheetNotFound:
        return None, f"Spreadsheet not found: {sheet_id}. Share it with the service account email."
    except Exception as e:
        return None, f"Error opening spreadsheet: {e}"

    try:
        worksheet = spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        # Create the tab if it doesn't exist
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(HEADERS))
        worksheet.update("A1", [HEADERS])
        # Bold the header row
        worksheet.format("A1:T1", {"textFormat": {"bold": True}})

    return worksheet, None


# ── Operations ──────────────────────────────────────────────────────

def init_sheet(client, sheet_id, tab_name):
    """Initialize the tracking sheet with headers and formatting."""
    ws, err = get_worksheet(client, sheet_id, tab_name)
    if err:
        return {"error": err}

    # Check if headers already exist
    existing = ws.row_values(1)
    if existing == HEADERS:
        return {"status": "already_initialized", "sheet_id": sheet_id, "tab": tab_name, "columns": len(HEADERS)}

    # Write headers
    ws.update("A1", [HEADERS])
    ws.format("A1:T1", {"textFormat": {"bold": True}})

    return {"status": "initialized", "sheet_id": sheet_id, "tab": tab_name, "columns": len(HEADERS)}


def add_row(client, sheet_id, tab_name, data):
    """Add a new content request row."""
    ws, err = get_worksheet(client, sheet_id, tab_name)
    if err:
        return {"error": err}

    # Generate requirement ID
    all_values = ws.col_values(1)  # Column A
    existing_ids = [v for v in all_values[1:] if v]  # Skip header
    next_num = len(existing_ids) + 1
    req_id = data.get("requirement_id", f"REQ-{next_num:03d}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    row = [
        req_id,
        data.get("brand", ""),
        data.get("content_type", ""),
        data.get("title", ""),
        data.get("target_audience", ""),
        str(data.get("word_count_target", "")),
        str(data.get("priority", 3)),
        data.get("status", "pending"),
        now,                                    # created_at
        "",                                     # started_at
        "",                                     # completed_at
        "",                                     # quality_score
        "",                                     # content_quality
        "",                                     # citation_integrity
        "",                                     # brand_compliance
        "",                                     # seo_performance
        "",                                     # readability
        "",                                     # actual_word_count
        "",                                     # drive_url
        data.get("notes", ""),
    ]

    ws.append_row(row, value_input_option="USER_ENTERED")

    return {
        "status": "added",
        "requirement_id": req_id,
        "row_number": len(all_values) + 1,
        "brand": data.get("brand", ""),
        "title": data.get("title", ""),
    }


def get_pending(client, sheet_id, tab_name, brand_filter=None):
    """Get all rows with status='pending'."""
    ws, err = get_worksheet(client, sheet_id, tab_name)
    if err:
        return {"error": err}

    all_records = ws.get_all_records()
    pending = []

    for i, record in enumerate(all_records):
        if record.get("status", "").lower() == "pending":
            if brand_filter and record.get("brand", "").lower() != brand_filter.lower():
                continue
            record["_row_number"] = i + 2  # +2 for header row + 0-index
            pending.append(record)

    # Sort by priority (1=highest)
    pending.sort(key=lambda r: int(r.get("priority", 5)))

    return {"pending_count": len(pending), "pending": pending}


def get_row(client, sheet_id, tab_name, row_id):
    """Get a specific row by requirement_id."""
    ws, err = get_worksheet(client, sheet_id, tab_name)
    if err:
        return {"error": err}

    all_records = ws.get_all_records()
    for i, record in enumerate(all_records):
        if record.get("requirement_id", "") == row_id:
            record["_row_number"] = i + 2
            return {"found": True, "record": record}

    return {"found": False, "error": f"No row with requirement_id={row_id}"}


def update_row(client, sheet_id, tab_name, row_id, data):
    """Update specific fields in a row identified by requirement_id."""
    ws, err = get_worksheet(client, sheet_id, tab_name)
    if err:
        return {"error": err}

    # Find the row
    all_records = ws.get_all_records()
    target_row = None
    for i, record in enumerate(all_records):
        if record.get("requirement_id", "") == row_id:
            target_row = i + 2  # +2 for header + 0-index
            break

    if not target_row:
        return {"error": f"No row with requirement_id={row_id}"}

    # Map field names to column letters
    col_map = {h: chr(65 + i) for i, h in enumerate(HEADERS)}  # A=65

    updates = []
    for field, value in data.items():
        if field in col_map:
            cell = f"{col_map[field]}{target_row}"
            updates.append({"range": cell, "values": [[str(value)]]})

    if updates:
        ws.batch_update(updates, value_input_option="USER_ENTERED")

    return {
        "status": "updated",
        "requirement_id": row_id,
        "row_number": target_row,
        "fields_updated": list(data.keys()),
    }


def mark_complete(client, sheet_id, tab_name, row_id, data):
    """Mark a row as completed with quality scores and Drive URL."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    completion_data = {
        "status": "completed",
        "completed_at": now,
    }

    # Map common fields from agent output
    field_map = {
        "quality_score": "quality_score",
        "content_quality": "content_quality",
        "citation_integrity": "citation_integrity",
        "brand_compliance": "brand_compliance",
        "seo_performance": "seo_performance",
        "readability": "readability",
        "actual_word_count": "actual_word_count",
        "drive_url": "drive_url",
        "notes": "notes",
    }

    for key, col in field_map.items():
        if key in data:
            completion_data[col] = data[key]

    return update_row(client, sheet_id, tab_name, row_id, completion_data)


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Google Sheets Tracker")
    parser.add_argument("--action", required=True,
                        choices=["init", "add-row", "get-pending", "get-row", "update-row", "mark-complete"])
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID (from the URL)")
    parser.add_argument("--tab", default=DEFAULT_TAB, help=f"Sheet tab name (default: {DEFAULT_TAB})")
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS),
                        help=f"Path to service account JSON (default: {DEFAULT_CREDENTIALS})")
    parser.add_argument("--row-id", help="Requirement ID for row operations")
    parser.add_argument("--brand", help="Brand filter for get-pending")
    parser.add_argument("--data", help="JSON string with field values")
    args = parser.parse_args()

    # Authenticate
    client, err = get_client(args.credentials)
    if err:
        print(json.dumps({"error": err, "help": (
            "To set up Google credentials:\n"
            "1. Go to Google Cloud Console > IAM & Admin > Service Accounts\n"
            "2. Create a service account and download the JSON key\n"
            "3. Save it to: ~/.claude-marketing/google-credentials.json\n"
            "4. Share your Google Sheet with the service account email (Editor access)"
        )}))
        sys.exit(1)

    # Parse data JSON
    data = {}
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON in --data: {e}"}))
            sys.exit(1)

    # Dispatch
    if args.action == "init":
        result = init_sheet(client, args.sheet_id, args.tab)
    elif args.action == "add-row":
        result = add_row(client, args.sheet_id, args.tab, data)
    elif args.action == "get-pending":
        result = get_pending(client, args.sheet_id, args.tab, args.brand)
    elif args.action == "get-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for get-row"}
        else:
            result = get_row(client, args.sheet_id, args.tab, args.row_id)
    elif args.action == "update-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for update-row"}
        else:
            result = update_row(client, args.sheet_id, args.tab, args.row_id, data)
    elif args.action == "mark-complete":
        if not args.row_id:
            result = {"error": "Provide --row-id for mark-complete"}
        else:
            result = mark_complete(client, args.sheet_id, args.tab, args.row_id, data)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
