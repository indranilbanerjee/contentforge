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

Storage: <brand-dir>/tracking/  (brand dir resolved via _common.brand_dir)
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

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

MONTH_NAMES = _common.MONTH_NAMES


# ── Helpers ─────────────────────────────────────────────────────────

def get_tracking_dir(brand):
    """Get the tracking directory for a brand (internal — hidden dotfolder)."""
    return _common.brand_dir(brand) / "tracking"


def get_publish_dir(brand, content_type=None, override=None):
    """Resolve the user-visible 'published output' directory.

    Resolution order (first non-empty wins):
      1. ``override`` argument (CLI --publish-dir)
      2. ``CONTENTFORGE_PUBLISH_DIR`` env var (workspace default)
      3. ``~/Documents/ContentForge/{brand}/[{content_type}/]``

    The published copy is in addition to the tracking copy under the brand's
    ``tracking/outputs/...`` directory — internal tracking stays where the
    rest of the plugin expects it; this is the copy the user actually opens.
    """
    base = override or os.environ.get("CONTENTFORGE_PUBLISH_DIR")
    if base:
        base = Path(base).expanduser()
    else:
        base = Path.home() / "Documents" / "ContentForge" / brand
    if content_type:
        base = base / content_type
    return base


def load_tracking(brand):
    """Load tracking records from JSON file. Returns (data, error)."""
    tracking_file = get_tracking_dir(brand) / "tracking.json"
    if not tracking_file.exists():
        return None, f"No tracking file for brand '{brand}'. Run --action init first."
    data = _common.load_json_safe(tracking_file)
    if isinstance(data, dict) and data.get("corrupt"):
        return None, (f"{data['error']} — {data['recovery']}")
    return data, None


def save_tracking(brand, records):
    """Atomically save tracking records to JSON file."""
    _common.atomic_write_json(get_tracking_dir(brand) / "tracking.json", records)


def slugify(text):
    """Convert text to a filesystem-safe slug (titles, not brands)."""
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
    _common.atomic_write_json(tracking_file, {"records": [], "schema_version": "1.0"})

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

    records = store["records"]
    req_id = data.get("requirement_id") or _common.next_req_id(records)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    priority = _common.clamp_priority(data.get("priority", 3))

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


def mark_complete(brand, row_id, data, output_file=None, publish_dir_override=None, skip_publish=False):
    """Mark a record as completed and copy output to two locations:

    1. Internal tracking copy under ``<brand-dir>/tracking/outputs/...``
       (machine-readable, used by /contentforge:analytics, /contentforge:audit, etc.)
    2. **User-visible published copy** under ``~/Documents/ContentForge/{brand}/...``
       (the path end users actually open — fixes the "file isn't saving on local
       drive" report from the v3.12.2 user feedback).

    Both copies are returned in the result so the orchestrator can quote the
    visible path to the user.
    """
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
    tracking_path = None
    published_path = None
    if output_file:
        src = Path(output_file).expanduser()
        if src.exists():
            today = datetime.now(timezone.utc)
            month_dir = MONTH_NAMES[today.month]
            title_slug = slugify(target.get("title", row_id))
            ext = src.suffix
            content_type = target.get("content_type", "") or None

            # --- 1. Internal tracking copy ---
            try:
                tracking_outputs_dir = get_tracking_dir(brand) / "outputs" / str(today.year) / month_dir
                tracking_outputs_dir.mkdir(parents=True, exist_ok=True)
                tracking_dest = tracking_outputs_dir / f"{title_slug}_v1.0{ext}"
                shutil.copy2(str(src), str(tracking_dest))
                tracking_path = str(tracking_dest)
            except (OSError, PermissionError) as exc:
                save_tracking(brand, store)
                return {"error": f"Could not write internal tracking copy: {exc}",
                        "recovery": "Check disk space / permissions on the brand tracking directory."}

            src_assets = src.parent / "assets"
            if src_assets.is_dir():
                dest_assets = tracking_outputs_dir / "assets"
                dest_assets.mkdir(parents=True, exist_ok=True)
                for asset in src_assets.iterdir():
                    if asset.is_file():
                        shutil.copy2(str(asset), str(dest_assets / asset.name))

            # --- 2. User-visible published copy (under ~/Documents/...) ---
            if not skip_publish:
                month_short = today.strftime("%Y-%m")
                publish_outputs_dir = get_publish_dir(brand, content_type, publish_dir_override) / month_short
                try:
                    publish_outputs_dir.mkdir(parents=True, exist_ok=True)
                    publish_dest = publish_outputs_dir / f"{title_slug}{ext}"
                    shutil.copy2(str(src), str(publish_dest))
                    published_path = str(publish_dest)

                    # Also publish assets alongside the .docx so charts/images are visible
                    if src_assets.is_dir():
                        publish_assets = publish_outputs_dir / f"{title_slug}-assets"
                        publish_assets.mkdir(parents=True, exist_ok=True)
                        for asset in src_assets.iterdir():
                            if asset.is_file():
                                shutil.copy2(str(asset), str(publish_assets / asset.name))
                except (OSError, PermissionError) as exc:
                    # Non-fatal — tracking copy is the system-of-record.
                    # User-visible copy can be re-published with /contentforge:output-folder.
                    published_path = None
                    target.setdefault("notes", "")
                    target["notes"] = (str(target["notes"]) + f" | publish failed: {exc}").strip(" |")

            target["output_path"] = tracking_path
            target["published_path"] = published_path

    save_tracking(brand, store)

    return {
        "status": "completed",
        "requirement_id": row_id,
        "output_path": tracking_path,
        "published_path": published_path,
        "published_path_note": (
            "This is the user-visible copy under ~/Documents/ContentForge/. "
            "Open this folder, not the internal tracking copy."
        ) if published_path else None,
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
    parser.add_argument("--publish-dir", default=None,
                        help="Override the user-visible publish directory (default: "
                             "$CONTENTFORGE_PUBLISH_DIR if set, else ~/Documents/ContentForge/{brand}/)")
    parser.add_argument("--skip-publish", action="store_true",
                        help="Skip the user-visible copy and only write the internal tracking copy")
    args = parser.parse_args()

    # Parse data JSON
    data = {}
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            _common.finish({"error": f"Invalid JSON in --data: {e}"})

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
            result = mark_complete(args.brand, args.row_id, data, args.output_file,
                                   publish_dir_override=args.publish_dir,
                                   skip_publish=args.skip_publish)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    _common.finish(result)


if __name__ == "__main__":
    main()
