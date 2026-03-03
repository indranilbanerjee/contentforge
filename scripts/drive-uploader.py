#!/usr/bin/env python3
"""
drive-uploader.py
=================
Google Drive file uploader for ContentForge output delivery.

Uploads .docx files (and chart PNGs) to organized Google Drive folders,
creates folder hierarchies automatically, and returns shareable URLs.

Usage:
    python drive-uploader.py --action upload --folder-id ROOT_ID --file path/to/file.docx --brand "Acme Corp" --content-type article
    python drive-uploader.py --action ensure-folders --folder-id ROOT_ID --brand "Acme Corp" --content-type article
    python drive-uploader.py --action list --folder-id FOLDER_ID
    python drive-uploader.py --action upload-assets --folder-id ROOT_ID --brand "Acme Corp" --assets-dir ~/.claude-marketing/acme-corp/assets/

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
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.service_account import Credentials
except ImportError:
    import subprocess
    print("Installing required packages (first run only)...", file=sys.stderr)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q",
         "google-api-python-client", "google-auth"],
        stdout=subprocess.DEVNULL,
    )
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.oauth2.service_account import Credentials

# ── Constants ───────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DEFAULT_CREDENTIALS = Path.home() / ".claude-marketing" / "google-credentials.json"

MONTH_NAMES = {
    1: "01-January", 2: "02-February", 3: "03-March", 4: "04-April",
    5: "05-May", 6: "06-June", 7: "07-July", 8: "08-August",
    9: "09-September", 10: "10-October", 11: "11-November", 12: "12-December",
}

MIME_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".json": "application/json",
    ".csv": "text/csv",
    ".md": "text/markdown",
}


# ── Auth ────────────────────────────────────────────────────────────

def get_service(credentials_path):
    """Create authenticated Google Drive service."""
    creds_path = Path(credentials_path).expanduser()
    if not creds_path.exists():
        return None, f"Credentials file not found: {creds_path}"
    try:
        creds = Credentials.from_service_account_file(str(creds_path), scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        return service, None
    except Exception as e:
        return None, f"Authentication failed: {e}"


# ── Folder Operations ──────────────────────────────────────────────

def find_folder(service, parent_id, folder_name):
    """Find a folder by name within a parent folder.

    Uses client-side name matching to avoid query injection from
    folder names containing apostrophes (e.g., "O'Reilly Media").
    """
    query = (
        f"'{parent_id}' in parents and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    for f in results.get("files", []):
        if f["name"] == folder_name:
            return f["id"]
    return None


def create_folder(service, parent_id, folder_name):
    """Create a folder within a parent folder."""
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def ensure_folder_path(service, root_folder_id, path_parts):
    """Create folder hierarchy, returning the deepest folder ID.

    path_parts example: ["Acme Corp", "Articles", "2026", "03-March"]
    """
    current_id = root_folder_id
    created = []

    for part in path_parts:
        existing = find_folder(service, current_id, part)
        if existing:
            current_id = existing
        else:
            current_id = create_folder(service, current_id, part)
            created.append(part)

    return current_id, created


def build_folder_path(brand, content_type):
    """Build the folder path parts for a content piece.

    Structure: ContentForge/{Brand}/{Content Type}/{Year}/{Month}
    """
    now = datetime.now(timezone.utc)
    content_type_folder = content_type.replace("_", " ").title() + "s"
    # article -> Articles, blog -> Blogs, whitepaper -> Whitepapers

    return [
        brand,
        content_type_folder,
        str(now.year),
        MONTH_NAMES.get(now.month, f"{now.month:02d}"),
    ]


# ── Upload Operations ──────────────────────────────────────────────

def upload_file(service, folder_id, file_path):
    """Upload a single file to a Drive folder.

    If the service account lacks storage quota (personal Google accounts),
    returns a structured error with the local file path as fallback.
    """
    file_path = Path(file_path).expanduser()
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    mime_type = MIME_TYPES.get(file_path.suffix.lower(), "application/octet-stream")

    metadata = {
        "name": file_path.name,
        "parents": [folder_id],
    }

    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)

    try:
        uploaded = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, webViewLink, size",
        ).execute()
    except Exception as e:
        error_str = str(e)
        if "storageQuotaExceeded" in error_str or "do not have storage quota" in error_str.lower():
            return {
                "error": "storage_quota",
                "message": (
                    "Service account cannot upload files to personal Google Drive "
                    "(no storage quota). The file has been saved locally."
                ),
                "local_path": str(file_path),
                "file_name": file_path.name,
                "fix_options": [
                    "Use a Google Workspace Shared Drive instead of personal Drive",
                    "Download the file directly from the conversation",
                ],
            }
        return {"error": f"Upload failed: {error_str}"}

    return {
        "file_id": uploaded["id"],
        "name": uploaded["name"],
        "url": uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view"),
        "size": uploaded.get("size", "unknown"),
    }


def list_files(service, folder_id):
    """List files in a Drive folder."""
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
        orderBy="modifiedTime desc",
    ).execute()

    files = results.get("files", [])
    return {"folder_id": folder_id, "file_count": len(files), "files": files}


# ── High-Level Operations ──────────────────────────────────────────

def upload_content(service, root_folder_id, file_path, brand, content_type):
    """Upload a content file to the organized folder structure."""
    path_parts = build_folder_path(brand, content_type)
    target_folder_id, created_folders = ensure_folder_path(service, root_folder_id, path_parts)

    result = upload_file(service, target_folder_id, file_path)
    if "error" in result:
        return result

    result["folder_path"] = "/".join(path_parts)
    result["folders_created"] = created_folders
    return result


def upload_assets(service, root_folder_id, brand, assets_dir):
    """Upload all visual assets from the assets directory."""
    assets_path = Path(assets_dir).expanduser()
    if not assets_path.exists():
        return {"error": f"Assets directory not found: {assets_path}"}

    # Create assets subfolder under brand
    path_parts = [brand, "Assets"]
    target_folder_id, created = ensure_folder_path(service, root_folder_id, path_parts)

    uploaded = []
    errors = []

    for file in sorted(assets_path.iterdir()):
        if file.is_file() and file.suffix.lower() in MIME_TYPES:
            result = upload_file(service, target_folder_id, file)
            if "error" in result:
                errors.append({"file": file.name, "error": result["error"]})
            else:
                uploaded.append(result)

    return {
        "assets_uploaded": len(uploaded),
        "errors": len(errors),
        "folder_path": "/".join(path_parts),
        "files": uploaded,
        "upload_errors": errors,
    }


# ── Main ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ContentForge Google Drive Uploader")
    parser.add_argument("--action", required=True,
                        choices=["upload", "ensure-folders", "list", "upload-assets"])
    parser.add_argument("--folder-id", required=True,
                        help="Root Google Drive folder ID (the ContentForge output folder)")
    parser.add_argument("--credentials", default=str(DEFAULT_CREDENTIALS),
                        help=f"Path to service account JSON (default: {DEFAULT_CREDENTIALS})")
    parser.add_argument("--file", help="Path to file to upload")
    parser.add_argument("--brand", help="Brand name for folder organization")
    parser.add_argument("--content-type", help="Content type (article, blog, whitepaper, faq, research_paper)")
    parser.add_argument("--assets-dir", help="Directory containing visual assets to upload")
    args = parser.parse_args()

    # Authenticate
    service, err = get_service(args.credentials)
    if err:
        print(json.dumps({"error": err, "help": (
            "To set up Google credentials:\n"
            "1. Go to Google Cloud Console > IAM & Admin > Service Accounts\n"
            "2. Create a service account and download the JSON key\n"
            "3. Save it to: ~/.claude-marketing/google-credentials.json\n"
            "4. Share your Google Drive folder with the service account email (Editor access)"
        )}))
        sys.exit(1)

    # Dispatch
    if args.action == "upload":
        if not args.file:
            result = {"error": "Provide --file for upload"}
        elif not args.brand or not args.content_type:
            result = {"error": "Provide --brand and --content-type for upload"}
        else:
            result = upload_content(service, args.folder_id, args.file, args.brand, args.content_type)

    elif args.action == "ensure-folders":
        if not args.brand or not args.content_type:
            result = {"error": "Provide --brand and --content-type for ensure-folders"}
        else:
            path_parts = build_folder_path(args.brand, args.content_type)
            folder_id, created = ensure_folder_path(service, args.folder_id, path_parts)
            result = {
                "folder_id": folder_id,
                "folder_path": "/".join(path_parts),
                "folders_created": created,
            }

    elif args.action == "list":
        result = list_files(service, args.folder_id)

    elif args.action == "upload-assets":
        if not args.brand or not args.assets_dir:
            result = {"error": "Provide --brand and --assets-dir for upload-assets"}
        else:
            result = upload_assets(service, args.folder_id, args.brand, args.assets_dir)

    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
