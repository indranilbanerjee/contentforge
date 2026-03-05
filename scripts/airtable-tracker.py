#!/usr/bin/env python3
"""
airtable-tracker.py
===================
Airtable tracker for ContentForge content pipeline.

Alternative to Google Sheets tracking with simpler auth setup.
Handles tracking AND file delivery via Airtable attachment fields.

Usage:
    python airtable-tracker.py --action init --base-id appXXXXXXXXXXXXXX
    python airtable-tracker.py --action add-row --base-id appXXX --data '{"brand":"Acme","title":"AI Content",...}'
    python airtable-tracker.py --action get-pending --base-id appXXX
    python airtable-tracker.py --action get-pending --base-id appXXX --brand "Acme Corp"
    python airtable-tracker.py --action update-row --base-id appXXX --row-id REQ-001 --data '{"status":"in_progress"}'
    python airtable-tracker.py --action mark-complete --base-id appXXX --row-id REQ-001 --data '{"quality_score":9.0}' --attach-file output.docx
    python airtable-tracker.py --action get-row --base-id appXXX --row-id REQ-001

Auth: Set AIRTABLE_TOKEN environment variable with your Personal Access Token
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Auto-install dependencies ───────────────────────────────────────
try:
    from pyairtable import Api
    from pyairtable.formulas import match
except ImportError:
    import subprocess
    print("Installing required packages (first run only)...", file=sys.stderr)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "pyairtable"],
        stdout=subprocess.DEVNULL,
    )
    from pyairtable import Api
    from pyairtable.formulas import match

# ── Constants ───────────────────────────────────────────────────────

# Tracking table column headers (20 fields, mirrors sheets-tracker.py schema)
HEADERS = [
    "requirement_id",       # Primary field
    "brand",
    "content_type",
    "title",
    "target_audience",
    "word_count_target",
    "priority",             # 1=highest, 5=lowest
    "status",               # pending/in_progress/completed/failed/review_required
    "created_at",
    "started_at",
    "completed_at",
    "quality_score",
    "content_quality",
    "citation_integrity",
    "brand_compliance",
    "seo_performance",
    "readability",
    "actual_word_count",
    "output_file",          # Attachment field (replaces drive_url)
    "notes",
]

# Airtable field types for documentation / manual table creation guidance
FIELD_TYPES = {
    "requirement_id": "singleLineText",
    "brand": "singleLineText",
    "content_type": "singleSelect",
    "title": "singleLineText",
    "target_audience": "singleLineText",
    "word_count_target": "number",
    "priority": "number",
    "status": "singleSelect",
    "created_at": "singleLineText",
    "started_at": "singleLineText",
    "completed_at": "singleLineText",
    "quality_score": "number",
    "content_quality": "number",
    "citation_integrity": "number",
    "brand_compliance": "number",
    "seo_performance": "number",
    "readability": "number",
    "actual_word_count": "number",
    "output_file": "multipleAttachments",
    "notes": "multilineText",
}

DEFAULT_TABLE = "ContentForge Tracking"

SETUP_HELP = (
    "To set up Airtable:\n"
    "1. Go to airtable.com/create/tokens\n"
    "2. Create a Personal Access Token with 'data.records:read' and 'data.records:write' scopes\n"
    "3. Set the environment variable: export AIRTABLE_TOKEN=pat...\n"
    "4. Create a base with a table named 'ContentForge Tracking'"
)

# Numeric fields that should be stored as numbers, not strings
NUMERIC_FIELDS = {
    "word_count_target", "priority", "quality_score", "content_quality",
    "citation_integrity", "brand_compliance", "seo_performance",
    "readability", "actual_word_count",
}


# ── Auth ────────────────────────────────────────────────────────────

def get_api():
    """Create authenticated Airtable API client."""
    token = os.environ.get("AIRTABLE_TOKEN")
    if not token:
        return None, "AIRTABLE_TOKEN environment variable not set."
    try:
        api = Api(token)
        return api, None
    except Exception as e:
        return None, f"Airtable authentication failed: {e}"


def get_table(api, base_id, table_name):
    """Get a table reference from the API client."""
    try:
        table = api.table(base_id, table_name)
        return table, None
    except Exception as e:
        return None, f"Error accessing table '{table_name}' in base {base_id}: {e}"


# ── Helpers ─────────────────────────────────────────────────────────

def record_to_dict(record):
    """Flatten an Airtable record into a simple dict with all HEADERS fields."""
    fields = record.get("fields", {})
    result = {"_record_id": record["id"]}
    for h in HEADERS:
        if h == "output_file":
            # Attachments come as a list of objects; extract URLs
            attachments = fields.get(h, [])
            if attachments:
                result[h] = [{"filename": a.get("filename", ""), "url": a.get("url", "")} for a in attachments]
            else:
                result[h] = []
        else:
            result[h] = fields.get(h, "")
    return result


def next_requirement_id(table):
    """Generate the next REQ-NNN id by finding the max existing number."""
    records = table.all(fields=["requirement_id"])
    max_num = 0
    for rec in records:
        rid = rec.get("fields", {}).get("requirement_id", "")
        if rid.startswith("REQ-"):
            try:
                num = int(rid.split("-", 1)[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
    return f"REQ-{max_num + 1:03d}"


def coerce_numeric(data):
    """Convert numeric field values from strings to numbers where appropriate."""
    coerced = {}
    for key, value in data.items():
        if key in NUMERIC_FIELDS and value != "" and value is not None:
            try:
                coerced[key] = float(value)
                # Use int if the value is whole
                if coerced[key] == int(coerced[key]):
                    coerced[key] = int(coerced[key])
            except (ValueError, TypeError):
                coerced[key] = value
        else:
            coerced[key] = value
    return coerced


# ── Operations ──────────────────────────────────────────────────────

def init_table(api, base_id, table_name):
    """Verify the table exists and is accessible."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    try:
        # Try to read one record to verify access
        records = table.all(max_records=1)
        field_count = len(HEADERS)
        return {
            "status": "ready",
            "base_id": base_id,
            "table": table_name,
            "fields": field_count,
            "existing_records": len(records),
            "field_schema": FIELD_TYPES,
        }
    except Exception as e:
        error_msg = str(e)
        if "NOT_FOUND" in error_msg or "404" in error_msg:
            return {
                "error": f"Table '{table_name}' not found in base {base_id}.",
                "help": (
                    "Airtable API (Personal Access Token) cannot create tables on free tier.\n"
                    "Please create the table manually:\n"
                    f"1. Open your base at https://airtable.com/{base_id}\n"
                    f"2. Create a table named '{table_name}'\n"
                    "3. Add fields with these types:\n"
                    + "\n".join(f"   - {f}: {t}" for f, t in FIELD_TYPES.items())
                ),
            }
        return {"error": f"Cannot access table: {error_msg}"}


def add_row(api, base_id, table_name, data):
    """Add a new content request record."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    # Generate requirement ID using max existing ID to avoid collisions
    req_id = data.get("requirement_id") or next_requirement_id(table)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Clamp priority 1-5
    try:
        priority = min(max(int(data.get("priority", 3)), 1), 5)
    except (ValueError, TypeError):
        priority = 3

    fields = {
        "requirement_id": req_id,
        "brand": data.get("brand", ""),
        "content_type": data.get("content_type", ""),
        "title": data.get("title", ""),
        "target_audience": data.get("target_audience", ""),
        "priority": priority,
        "status": data.get("status", "pending"),
        "created_at": now,
        "notes": data.get("notes", ""),
    }

    # Add optional numeric fields if provided
    if data.get("word_count_target"):
        try:
            fields["word_count_target"] = int(data["word_count_target"])
        except (ValueError, TypeError):
            pass

    try:
        record = table.create(fields)
        return {
            "status": "added",
            "requirement_id": req_id,
            "record_id": record["id"],
            "brand": fields["brand"],
            "title": fields["title"],
        }
    except Exception as e:
        return {"error": f"Failed to create record: {e}"}


def get_pending(api, base_id, table_name, brand_filter=None):
    """Get all records with status='pending', sorted by priority."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    try:
        # Build formula filter
        if brand_filter:
            formula = f"AND({{status}} = 'pending', {{brand}} = '{brand_filter}')"
        else:
            formula = "{status} = 'pending'"

        records = table.all(formula=formula, sort=["priority"])
        pending = [record_to_dict(r) for r in records]

        return {"pending_count": len(pending), "pending": pending}
    except Exception as e:
        return {"error": f"Failed to fetch pending records: {e}"}


def get_row(api, base_id, table_name, row_id):
    """Get a specific record by requirement_id."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    try:
        formula = match({"requirement_id": row_id})
        records = table.all(formula=formula, max_records=1)

        if not records:
            return {"found": False, "error": f"No record with requirement_id={row_id}"}

        return {"found": True, "record": record_to_dict(records[0])}
    except Exception as e:
        return {"error": f"Failed to fetch record: {e}"}


def update_row(api, base_id, table_name, row_id, data):
    """Update specific fields in a record identified by requirement_id."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    try:
        # Find the record
        formula = match({"requirement_id": row_id})
        records = table.all(formula=formula, max_records=1)

        if not records:
            return {"error": f"No record with requirement_id={row_id}"}

        record_id = records[0]["id"]

        # Filter to valid fields only (exclude attachment field from simple updates)
        update_fields = {}
        for field, value in data.items():
            if field in HEADERS and field != "output_file" and field != "requirement_id":
                update_fields[field] = value

        # Coerce numeric fields
        update_fields = coerce_numeric(update_fields)

        if not update_fields:
            return {"error": "No valid fields to update"}

        table.update(record_id, update_fields)

        return {
            "status": "updated",
            "requirement_id": row_id,
            "record_id": record_id,
            "fields_updated": list(update_fields.keys()),
        }
    except Exception as e:
        return {"error": f"Failed to update record: {e}"}


def mark_complete(api, base_id, table_name, row_id, data, attach_file=None):
    """Mark a record as completed with quality scores and optional file attachment."""
    table, err = get_table(api, base_id, table_name)
    if err:
        return {"error": err}

    try:
        # Find the record
        formula = match({"requirement_id": row_id})
        records = table.all(formula=formula, max_records=1)

        if not records:
            return {"error": f"No record with requirement_id={row_id}"}

        record_id = records[0]["id"]
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Build completion fields
        completion_fields = {
            "status": "completed",
            "completed_at": now,
        }

        # Map quality score fields from data
        score_fields = [
            "quality_score", "content_quality", "citation_integrity",
            "brand_compliance", "seo_performance", "readability",
            "actual_word_count", "notes",
        ]
        for field in score_fields:
            if field in data:
                completion_fields[field] = data[field]

        # Coerce numeric fields
        completion_fields = coerce_numeric(completion_fields)

        # Update the record
        table.update(record_id, completion_fields)

        # Handle file attachment
        attachment_info = None
        if attach_file:
            file_path = Path(attach_file).expanduser()
            if file_path.exists():
                try:
                    table.upload_attachment(record_id, "output_file", str(file_path))
                    attachment_info = {
                        "filename": file_path.name,
                        "size_bytes": file_path.stat().st_size,
                    }
                except Exception as e:
                    attachment_info = {"error": f"Attachment upload failed: {e}"}
            else:
                attachment_info = {"error": f"File not found: {file_path}"}

        return {
            "status": "completed",
            "requirement_id": row_id,
            "record_id": record_id,
            "fields_updated": list(completion_fields.keys()),
            "attachment": attachment_info,
        }
    except Exception as e:
        return {"error": f"Failed to mark complete: {e}"}


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Airtable Tracker")
    parser.add_argument("--action", required=True,
                        choices=["init", "add-row", "get-pending", "get-row", "update-row", "mark-complete"])
    parser.add_argument("--base-id", required=True, help="Airtable Base ID (from base URL)")
    parser.add_argument("--table", default=DEFAULT_TABLE, help=f"Table name (default: {DEFAULT_TABLE})")
    parser.add_argument("--row-id", help="Requirement ID for row operations")
    parser.add_argument("--brand", help="Brand filter for get-pending")
    parser.add_argument("--data", help="JSON string with field values")
    parser.add_argument("--attach-file", help="Path to file to attach (for mark-complete)")
    args = parser.parse_args()

    # Authenticate
    api, err = get_api()
    if err:
        print(json.dumps({"error": err, "help": SETUP_HELP}))
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
        result = init_table(api, args.base_id, args.table)
    elif args.action == "add-row":
        result = add_row(api, args.base_id, args.table, data)
    elif args.action == "get-pending":
        result = get_pending(api, args.base_id, args.table, args.brand)
    elif args.action == "get-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for get-row"}
        else:
            result = get_row(api, args.base_id, args.table, args.row_id)
    elif args.action == "update-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for update-row"}
        else:
            result = update_row(api, args.base_id, args.table, args.row_id, data)
    elif args.action == "mark-complete":
        if not args.row_id:
            result = {"error": "Provide --row-id for mark-complete"}
        else:
            result = mark_complete(api, args.base_id, args.table, args.row_id, data, args.attach_file)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
