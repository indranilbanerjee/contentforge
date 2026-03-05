#!/usr/bin/env python3
"""
backend-migrator.py
===================
Cross-backend data migrator for ContentForge tracking.

Migrates tracking records and output files between local, Airtable,
and Google Sheets/Drive backends. Migration is additive (source data
is never deleted), idempotent (no duplicates), and resumable.

Usage:
    python backend-migrator.py --action status --brand "Acme" --from local
    python backend-migrator.py --action migrate --brand "Acme" --from local --to airtable --base-id appXXX
    python backend-migrator.py --action migrate --brand "Acme" --from local --to google_sheets --sheet-id XXX --folder-id YYY
    python backend-migrator.py --action migrate --brand "Acme" --from airtable --to local --base-id appXXX
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlretrieve

# ── Constants ───────────────────────────────────────────────────────

BASE_DIR = Path.home() / ".claude-marketing"
DEFAULT_CREDENTIALS = BASE_DIR / "google-credentials.json"
DEFAULT_TABLE = "ContentForge Tracking"

GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# ── Lazy dependency installers ─────────────────────────────────────

def _ensure_pyairtable():
    """Auto-install pyairtable on first use."""
    try:
        from pyairtable import Api
        return Api
    except ImportError:
        import subprocess
        print("Installing pyairtable (first run only)...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "pyairtable"],
            stdout=subprocess.DEVNULL,
        )
        from pyairtable import Api
        return Api


def _ensure_google():
    """Auto-install gspread + google-auth + google-api-python-client on first use."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        return gspread, Credentials
    except ImportError:
        import subprocess
        print("Installing Google packages (first run only)...", file=sys.stderr)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q",
             "gspread", "google-auth", "google-api-python-client"],
            stdout=subprocess.DEVNULL,
        )
        import gspread
        from google.oauth2.service_account import Credentials
        return gspread, Credentials


# ── Local backend ──────────────────────────────────────────────────

def read_local(brand):
    """Read records from local tracking.json."""
    tracking_file = BASE_DIR / brand / "tracking" / "tracking.json"
    if not tracking_file.exists():
        return [], f"No local tracking for brand '{brand}'"
    data = json.loads(tracking_file.read_text(encoding="utf-8"))
    return data.get("records", []), None


def write_local_record(brand, record):
    """Write a single record to local tracking.json."""
    tracking_dir = BASE_DIR / brand / "tracking"
    tracking_file = tracking_dir / "tracking.json"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    if tracking_file.exists():
        data = json.loads(tracking_file.read_text(encoding="utf-8"))
    else:
        data = {"records": [], "schema_version": "1.0"}
    data["records"].append(record)
    tracking_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def count_local_files(brand):
    """Count output files in the local outputs directory."""
    outputs_dir = BASE_DIR / brand / "outputs"
    if not outputs_dir.exists():
        return 0
    return sum(1 for f in outputs_dir.rglob("*") if f.is_file())


def copy_file_local(source_path, brand, record):
    """Copy a file to the local tracking outputs directory."""
    source = Path(source_path).expanduser()
    if not source.exists():
        return None, f"Source file not found: {source}"

    now = datetime.now(timezone.utc)
    year = str(now.year)
    month = f"{now.month:02d}"

    # Build slug from record title or requirement_id
    slug = record.get("title", record.get("requirement_id", "output"))
    slug = slug.lower().replace(" ", "-")[:60]

    dest_dir = BASE_DIR / brand / "outputs" / year / month
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / f"{slug}{source.suffix}"

    shutil.copy2(str(source), str(dest_file))
    return str(dest_file), None


# ── Airtable backend ──────────────────────────────────────────────

def _get_airtable_api():
    """Create authenticated Airtable API client."""
    token = os.environ.get("AIRTABLE_TOKEN")
    if not token:
        return None, "AIRTABLE_TOKEN environment variable not set."
    Api = _ensure_pyairtable()
    return Api(token), None


def read_airtable(base_id, table_name):
    """Read all records from Airtable."""
    api, err = _get_airtable_api()
    if err:
        return [], err
    try:
        table = api.table(base_id, table_name)
        records = table.all()
        return [r["fields"] for r in records], None
    except Exception as e:
        return [], f"Airtable read failed: {e}"


def write_airtable_record(base_id, table_name, record, attach_file=None):
    """Write a single record to Airtable, optionally with file attachment."""
    api, err = _get_airtable_api()
    if err:
        return err

    try:
        table = api.table(base_id, table_name)

        # Exclude file-related fields from the record dict
        fields = {k: v for k, v in record.items()
                  if k not in ("output_file", "output_path", "drive_url", "_record_id")
                  and v not in (None, "")}

        created = table.create(fields)

        # Upload attachment if provided
        if attach_file:
            file_path = Path(attach_file).expanduser()
            if file_path.exists():
                try:
                    table.upload_attachment(created["id"], "output_file", str(file_path))
                except Exception as e:
                    return f"Record created but attachment failed: {e}"

        return None
    except Exception as e:
        return f"Airtable write failed: {e}"


def download_airtable_attachment(record, brand):
    """Download attachment from Airtable record to local temp."""
    attachments = record.get("output_file", [])
    if not attachments or not isinstance(attachments, list):
        return None, "No attachment"

    first = attachments[0]
    url = first.get("url") if isinstance(first, dict) else None
    if not url:
        return None, "No attachment URL"

    filename = first.get("filename", "attachment.docx") if isinstance(first, dict) else "attachment.docx"
    tmp_dir = Path(tempfile.mkdtemp(prefix="cf_migrate_"))
    dest = tmp_dir / filename

    try:
        urlretrieve(url, str(dest))
        return str(dest), None
    except Exception as e:
        return None, f"Download failed: {e}"


# ── Google Sheets/Drive backend ───────────────────────────────────

def _get_google_client(credentials_path):
    """Create authenticated gspread client."""
    gspread, Credentials = _ensure_google()
    creds_path = Path(credentials_path).expanduser()
    if not creds_path.exists():
        return None, None, f"Credentials not found: {creds_path}"
    try:
        creds = Credentials.from_service_account_file(str(creds_path), scopes=GOOGLE_SCOPES)
        client = gspread.authorize(creds)
        return client, creds, None
    except Exception as e:
        return None, None, f"Google auth failed: {e}"


def read_google(sheet_id, credentials_path):
    """Read all records from Google Sheets."""
    client, _, err = _get_google_client(credentials_path)
    if err:
        return [], err
    try:
        sheet = client.open_by_key(sheet_id)
        ws = sheet.worksheet(DEFAULT_TABLE)
        records = ws.get_all_records()
        return records, None
    except Exception as e:
        return [], f"Google Sheets read failed: {e}"


def write_google_record(sheet_id, credentials_path, record, folder_id=None, file_path=None):
    """Write record to Google Sheet, optionally upload file to Drive."""
    client, creds, err = _get_google_client(credentials_path)
    if err:
        return err

    try:
        sheet = client.open_by_key(sheet_id)
        ws = sheet.worksheet(DEFAULT_TABLE)
        headers = ws.row_values(1)

        # Build row matching header order
        row = []
        for h in headers:
            val = record.get(h, "")
            # Skip complex types (lists, dicts)
            if isinstance(val, (list, dict)):
                val = ""
            row.append(str(val) if val is not None else "")

        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception as e:
        return f"Google Sheets write failed: {e}"

    # Upload file to Drive if requested
    if file_path and folder_id:
        upload_err = _upload_to_drive(file_path, folder_id, creds)
        if upload_err:
            return f"Record created but Drive upload failed: {upload_err}"

    return None


def _upload_to_drive(file_path, folder_id, creds):
    """Upload file to Google Drive folder."""
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return "google-api-python-client not available"

    fp = Path(file_path).expanduser()
    if not fp.exists():
        return f"File not found: {fp}"

    try:
        service = build("drive", "v3", credentials=creds)
        metadata = {"name": fp.name, "parents": [folder_id]}
        media = MediaFileUpload(str(fp), resumable=True)
        service.files().create(body=metadata, media_body=media, fields="id").execute()
        return None
    except Exception as e:
        return f"Drive upload failed: {e}"


# ── Migration engine ──────────────────────────────────────────────

def get_requirement_ids(records):
    """Extract the set of requirement_ids from a list of records."""
    ids = set()
    for r in records:
        rid = r.get("requirement_id", "")
        if rid:
            ids.add(rid)
    return ids


def get_file_path_from_record(record, backend):
    """Extract the output file path/reference from a record based on backend."""
    if backend == "local":
        return record.get("output_path") or record.get("output_file") or None
    elif backend == "google_sheets":
        return record.get("drive_url") or None
    elif backend == "airtable":
        # Airtable attachments are lists
        att = record.get("output_file", [])
        if isinstance(att, list) and att:
            first = att[0]
            return first.get("url") if isinstance(first, dict) else None
        return None
    return None


def migrate_records(args):
    """Core migration logic: read source, deduplicate, write to target."""
    brand = args.brand
    src = args.from_backend
    tgt = args.to_backend
    errors = []

    # ── Read source records ────────────────────────────────────────
    if src == "local":
        source_records, err = read_local(brand)
    elif src == "airtable":
        if not args.base_id:
            return {"error": "--base-id required for airtable source"}
        source_records, err = read_airtable(args.base_id, args.table)
    elif src == "google_sheets":
        if not args.sheet_id:
            return {"error": "--sheet-id required for google_sheets source"}
        source_records, err = read_google(args.sheet_id, args.credentials)
    else:
        return {"error": f"Unknown source backend: {src}"}

    if err:
        return {"error": f"Source read failed: {err}"}

    if not source_records:
        return {
            "status": "completed",
            "records_migrated": 0, "records_skipped": 0,
            "files_migrated": 0, "files_failed": 0,
            "source": src, "target": tgt, "source_preserved": True,
            "errors": [], "note": "Source has no records to migrate.",
        }

    # ── Read target records (for dedup) ────────────────────────────
    if tgt == "local":
        target_records, _ = read_local(brand)
    elif tgt == "airtable":
        if not args.base_id:
            return {"error": "--base-id required for airtable target"}
        target_records, _ = read_airtable(args.base_id, args.table)
    elif tgt == "google_sheets":
        if not args.sheet_id:
            return {"error": "--sheet-id required for google_sheets target"}
        target_records, _ = read_google(args.sheet_id, args.credentials)
    else:
        return {"error": f"Unknown target backend: {tgt}"}

    existing_ids = get_requirement_ids(target_records)

    # ── Migrate each record ────────────────────────────────────────
    migrated = 0
    skipped = 0
    files_migrated = 0
    files_failed = 0

    for record in source_records:
        rid = record.get("requirement_id", "")

        # Skip duplicates
        if rid and rid in existing_ids:
            skipped += 1
            continue

        # ── Attempt file transfer ──────────────────────────────────
        local_file = None  # path to a local copy of the file for upload

        file_ref = get_file_path_from_record(record, src)
        if file_ref:
            local_file, file_err = _resolve_file_to_local(file_ref, src, record, brand)
            if file_err:
                errors.append(f"{rid}: file download — {file_err}")

        # ── Write record to target ─────────────────────────────────
        write_err = None
        if tgt == "local":
            # Strip remote-only fields before local write
            clean = {k: v for k, v in record.items()
                     if k != "_record_id" and not isinstance(v, list)}
            write_local_record(brand, clean)
            if local_file:
                dest, copy_err = copy_file_local(local_file, brand, record)
                if copy_err:
                    errors.append(f"{rid}: local file copy — {copy_err}")
                    files_failed += 1
                else:
                    files_migrated += 1

        elif tgt == "airtable":
            if not args.base_id:
                return {"error": "--base-id required for airtable target"}
            write_err = write_airtable_record(
                args.base_id, args.table, record,
                attach_file=local_file,
            )
            if local_file and not write_err:
                files_migrated += 1
            elif local_file and write_err and "attachment" in str(write_err).lower():
                files_failed += 1

        elif tgt == "google_sheets":
            if not args.sheet_id:
                return {"error": "--sheet-id required for google_sheets target"}
            write_err = write_google_record(
                args.sheet_id, args.credentials, record,
                folder_id=args.folder_id,
                file_path=local_file,
            )
            if local_file and not write_err:
                files_migrated += 1
            elif local_file and write_err and "upload" in str(write_err).lower():
                files_failed += 1

        if write_err:
            errors.append(f"{rid}: write — {write_err}")
        else:
            migrated += 1
            if rid:
                existing_ids.add(rid)

    return {
        "status": "completed",
        "records_migrated": migrated,
        "records_skipped": skipped,
        "files_migrated": files_migrated,
        "files_failed": files_failed,
        "source": src,
        "target": tgt,
        "source_preserved": True,
        "errors": errors,
    }


def _resolve_file_to_local(file_ref, backend, record, brand):
    """Ensure we have a local file path for transfer.

    For local backend, the reference is already a path.
    For remote backends, download to a temp directory first.
    """
    if backend == "local":
        fp = Path(file_ref).expanduser()
        if fp.exists():
            return str(fp), None
        return None, f"Local file not found: {fp}"

    elif backend == "airtable":
        return download_airtable_attachment(record, brand)

    elif backend == "google_sheets":
        # Google Drive download requires the Drive API and file ID extraction
        # from the URL — stub with a warning for now
        return None, "Google Drive file download not yet supported; record migrated without file"

    return None, f"Unknown backend for file resolution: {backend}"


# ── Status check ──────────────────────────────────────────────────

def check_status(args):
    """Report current state of a backend for a given brand."""
    brand = args.brand
    backend = args.from_backend

    if backend == "local":
        records, err = read_local(brand)
        file_count = count_local_files(brand)
        tracking_file = BASE_DIR / brand / "tracking" / "tracking.json"

        if err:
            return {
                "backend": "local",
                "brand": brand,
                "record_count": 0,
                "file_count": file_count,
                "status": "empty",
                "details": err,
            }

        return {
            "backend": "local",
            "brand": brand,
            "record_count": len(records),
            "file_count": file_count,
            "status": "healthy",
            "details": f"Tracking file: {tracking_file}",
        }

    elif backend == "airtable":
        if not args.base_id:
            return {"error": "--base-id required for airtable status"}
        records, err = read_airtable(args.base_id, args.table)
        if err:
            return {
                "backend": "airtable",
                "brand": brand,
                "record_count": 0,
                "file_count": 0,
                "status": "error",
                "details": err,
            }
        # Count records with attachments
        files = sum(1 for r in records if r.get("output_file"))
        return {
            "backend": "airtable",
            "brand": brand,
            "record_count": len(records),
            "file_count": files,
            "status": "healthy",
            "details": f"Base: {args.base_id}, Table: {args.table}",
        }

    elif backend == "google_sheets":
        if not args.sheet_id:
            return {"error": "--sheet-id required for google_sheets status"}
        records, err = read_google(args.sheet_id, args.credentials)
        if err:
            return {
                "backend": "google_sheets",
                "brand": brand,
                "record_count": 0,
                "file_count": 0,
                "status": "error",
                "details": err,
            }
        # Count records with drive_url
        files = sum(1 for r in records if r.get("drive_url"))
        return {
            "backend": "google_sheets",
            "brand": brand,
            "record_count": len(records),
            "file_count": files,
            "status": "healthy",
            "details": f"Sheet: {args.sheet_id}",
        }

    else:
        return {"error": f"Unknown backend: {backend}"}


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Backend Migrator")
    parser.add_argument("--action", required=True, choices=["migrate", "status"])
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--from", dest="from_backend",
                        help="Source backend: local|airtable|google_sheets")
    parser.add_argument("--to", dest="to_backend",
                        help="Target backend: local|airtable|google_sheets")
    parser.add_argument("--base-id", help="Airtable Base ID (if airtable involved)")
    parser.add_argument("--sheet-id", help="Google Sheet ID (if google involved)")
    parser.add_argument("--folder-id", help="Google Drive folder ID (if google involved)")
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS),
                        help="Path to Google credentials JSON")
    parser.add_argument("--table", default=DEFAULT_TABLE,
                        help="Airtable table name")
    args = parser.parse_args()

    # ── Validate ───────────────────────────────────────────────────
    if not args.from_backend:
        print(json.dumps({"error": "Provide --from (source backend)"}))
        sys.exit(1)

    if args.action == "migrate" and not args.to_backend:
        print(json.dumps({"error": "Provide --to (target backend) for migrate"}))
        sys.exit(1)

    if args.action == "migrate" and args.from_backend == args.to_backend:
        print(json.dumps({"error": "Source and target backends must be different"}))
        sys.exit(1)

    # ── Dispatch ───────────────────────────────────────────────────
    if args.action == "status":
        result = check_status(args)
    elif args.action == "migrate":
        result = migrate_records(args)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
