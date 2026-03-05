#!/usr/bin/env python3
"""
local-tracker.py
================
Local filesystem tracker for ContentForge content pipeline.

Zero-dependency, zero-auth tracking backend that stores records
in JSON and output files in organized local directories.

Usage:
    python local-tracker.py --action init --brand "Acme"
    python local-tracker.py --action add-row --brand "Acme" --data '{"title":"AI Content","content_type":"article",...}'
    python local-tracker.py --action get-pending --brand "Acme"
    python local-tracker.py --action update-row --brand "Acme" --row-id REQ-001 --data '{"status":"in_progress"}'
    python local-tracker.py --action mark-complete --brand "Acme" --row-id REQ-001 --data '{"quality_score":9.0}' --output-file output.docx
    python local-tracker.py --action get-row --brand "Acme" --row-id REQ-001

Storage: ~/.claude-marketing/{brand}/tracking/
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────

HEADERS = [
    "requirement_id",
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
    "output_path",          # Local file path (replaces drive_url)
    "notes",
]

MONTH_NAMES = {
    1: "01-January", 2: "02-February", 3: "03-March", 4: "04-April",
    5: "05-May", 6: "06-June", 7: "07-July", 8: "08-August",
    9: "09-September", 10: "10-October", 11: "11-November", 12: "12-December",
}


# ── Helpers ─────────────────────────────────────────────────────────

def get_tracking_dir(brand):
    """Get the tracking directory for a brand."""
    return Path.home() / ".claude-marketing" / brand / "tracking"


def load_tracking(brand):
    """Load tracking records from JSON file."""
    tracking_file = get_tracking_dir(brand) / "tracking.json"
    if not tracking_file.exists():
        return None, f"No tracking file for brand '{brand}'. Run --action init first."
    data = json.loads(tracking_file.read_text(encoding="utf-8"))
    return data, None


def save_tracking(brand, records):
    """Save tracking records to JSON file."""
    tracking_file = get_tracking_dir(brand) / "tracking.json"
    tracking_file.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def slugify(text):
    """Convert text to a filesystem-safe slug."""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug[:80]


# ── Operations ──────────────────────────────────────────────────────

def init_tracking(brand):
    """Create tracking directory structure and empty tracking.json."""
    tracking_dir = get_tracking_dir(brand)
    outputs_dir = tracking_dir / "outputs"
    tracking_file = tracking_dir / "tracking.json"

    if tracking_file.exists():
        return {
            "status": "already_initialized",
            "tracking_dir": str(tracking_dir),
            "brand": brand,
        }

    tracking_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    tracking_file.write_text(
        json.dumps({"records": [], "schema_version": "1.0"}, indent=2),
        encoding="utf-8",
    )

    return {
        "status": "initialized",
        "tracking_dir": str(tracking_dir),
        "brand": brand,
    }


def add_row(brand, data):
    """Add a new content request record."""
    store, err = load_tracking(brand)
    if err:
        return {"error": err}

    # Generate requirement_id — use max existing ID to avoid collisions
    records = store["records"]
    max_num = 0
    for rec in records:
        rid = rec.get("requirement_id", "")
        if rid.startswith("REQ-"):
            try:
                num = int(rid.split("-", 1)[1])
                max_num = max(max_num, num)
            except (IndexError, ValueError):
                pass
    next_num = max_num + 1
    req_id = data.get("requirement_id", f"REQ-{next_num:03d}")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Clamp priority 1-5
    try:
        priority = min(max(int(data.get("priority", 3)), 1), 5)
    except (ValueError, TypeError):
        priority = 3

    record = {
        "requirement_id": req_id,
        "brand": data.get("brand", brand),
        "content_type": data.get("content_type", ""),
        "title": data.get("title", ""),
        "target_audience": data.get("target_audience", ""),
        "word_count_target": data.get("word_count_target", ""),
        "priority": priority,
        "status": data.get("status", "pending"),
        "created_at": now,
        "started_at": "",
        "completed_at": "",
        "quality_score": "",
        "content_quality": "",
        "citation_integrity": "",
        "brand_compliance": "",
        "seo_performance": "",
        "readability": "",
        "actual_word_count": "",
        "output_path": "",
        "notes": data.get("notes", ""),
    }

    records.append(record)
    save_tracking(brand, store)

    return {
        "status": "added",
        "requirement_id": req_id,
        "brand": data.get("brand", brand),
        "title": data.get("title", ""),
    }


def get_pending(brand):
    """Get all records with status='pending', sorted by priority."""
    store, err = load_tracking(brand)
    if err:
        return {"error": err}

    pending = [r for r in store["records"] if r.get("status", "").lower() == "pending"]

    # Sort by priority ascending — safely handle non-numeric values
    def _safe_priority(r):
        try:
            return int(r.get("priority", 5))
        except (ValueError, TypeError):
            return 5
    pending.sort(key=_safe_priority)

    return {"pending_count": len(pending), "pending": pending}


def get_row(brand, row_id):
    """Get a specific record by requirement_id."""
    store, err = load_tracking(brand)
    if err:
        return {"error": err}

    for record in store["records"]:
        if record.get("requirement_id", "") == row_id:
            return {"found": True, "record": record}

    return {"found": False, "error": f"No record with requirement_id={row_id}"}


def update_row(brand, row_id, data):
    """Update specific fields in a record identified by requirement_id."""
    store, err = load_tracking(brand)
    if err:
        return {"error": err}

    for record in store["records"]:
        if record.get("requirement_id", "") == row_id:
            fields_updated = []
            for field, value in data.items():
                if field in HEADERS:
                    record[field] = value
                    fields_updated.append(field)
            save_tracking(brand, store)
            return {
                "status": "updated",
                "requirement_id": row_id,
                "fields_updated": fields_updated,
            }

    return {"error": f"No record with requirement_id={row_id}"}


def mark_complete(brand, row_id, data, output_file=None):
    """Mark a record as completed, copy output file to organized directory."""
    store, err = load_tracking(brand)
    if err:
        return {"error": err}

    target = None
    for record in store["records"]:
        if record.get("requirement_id", "") == row_id:
            target = record
            break

    if not target:
        return {"error": f"No record with requirement_id={row_id}"}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    target["status"] = "completed"
    target["completed_at"] = now

    # Apply quality scores from --data
    score_fields = [
        "quality_score", "content_quality", "citation_integrity",
        "brand_compliance", "seo_performance", "readability",
        "actual_word_count", "notes",
    ]
    for field in score_fields:
        if field in data:
            target[field] = data[field]

    # Copy output file to organized directory
    dest_path = None
    if output_file:
        src = Path(output_file).expanduser()
        if src.exists():
            today = datetime.now(timezone.utc)
            month_dir = MONTH_NAMES[today.month]
            title_slug = slugify(target.get("title", row_id))
            ext = src.suffix

            outputs_dir = get_tracking_dir(brand) / "outputs" / str(today.year) / month_dir
            outputs_dir.mkdir(parents=True, exist_ok=True)

            dest = outputs_dir / f"{title_slug}_v1.0{ext}"
            shutil.copy2(str(src), str(dest))
            dest_path = str(dest)

            # Check for assets directory next to source file
            src_assets = src.parent / "assets"
            if src_assets.is_dir():
                dest_assets = outputs_dir / "assets"
                dest_assets.mkdir(parents=True, exist_ok=True)
                for asset in src_assets.iterdir():
                    if asset.is_file():
                        shutil.copy2(str(asset), str(dest_assets / asset.name))

            target["output_path"] = dest_path

    save_tracking(brand, store)

    return {
        "status": "completed",
        "requirement_id": row_id,
        "output_path": dest_path,
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Local Filesystem Tracker")
    parser.add_argument("--action", required=True,
                        choices=["init", "add-row", "get-pending", "get-row", "update-row", "mark-complete"])
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--row-id", help="Requirement ID for row operations")
    parser.add_argument("--data", help="JSON string with field values")
    parser.add_argument("--output-file", help="Path to output file to copy (for mark-complete)")
    args = parser.parse_args()

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
        result = init_tracking(args.brand)
    elif args.action == "add-row":
        result = add_row(args.brand, data)
    elif args.action == "get-pending":
        result = get_pending(args.brand)
    elif args.action == "get-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for get-row"}
        else:
            result = get_row(args.brand, args.row_id)
    elif args.action == "update-row":
        if not args.row_id:
            result = {"error": "Provide --row-id for update-row"}
        else:
            result = update_row(args.brand, args.row_id, data)
    elif args.action == "mark-complete":
        if not args.row_id:
            result = {"error": "Provide --row-id for mark-complete"}
        else:
            result = mark_complete(args.brand, args.row_id, data, args.output_file)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
