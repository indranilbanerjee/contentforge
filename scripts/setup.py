#!/usr/bin/env python3
"""
setup.py
========
ContentForge session startup script.

Validates the plugin environment on session start:
- Checks Python version (3.8+ required)
- Reports plugin root and scripts directory paths
- Validates .mcp.json exists and is valid JSON
- Reports connector count
- Checks Google integration status (credentials, pip packages)

Called by hooks/hooks.json SessionStart hook.
"""

import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
GOOGLE_CREDS_DEFAULT = Path.home() / ".claude-marketing" / "google-credentials.json"


def check_google_integration():
    """Check Google Sheets/Drive integration status."""
    status = {"credentials": False, "packages": False}

    # Check credentials file
    if GOOGLE_CREDS_DEFAULT.exists():
        try:
            data = json.loads(GOOGLE_CREDS_DEFAULT.read_text(encoding="utf-8"))
            if "client_email" in data:
                status["credentials"] = True
                status["service_account_email"] = data["client_email"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Check pip packages
    try:
        import gspread  # noqa: F401
        from google.oauth2.service_account import Credentials  # noqa: F401
        from googleapiclient.discovery import build  # noqa: F401
        status["packages"] = True
    except ImportError:
        pass

    return status


def main():
    errors = []

    # Check Python version
    if sys.version_info < (3, 8):
        errors.append(f"Python 3.8+ required (found {sys.version})")

    # Report paths
    print(f"PLUGIN_ROOT={PLUGIN_ROOT}")
    print(f"SCRIPTS_DIR={SCRIPTS_DIR}")

    # Validate .mcp.json
    if MCP_JSON.exists():
        try:
            data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
            servers = data.get("mcpServers", {})
            print(f"CONNECTORS={len(servers)} HTTP connectors loaded")
        except json.JSONDecodeError as e:
            errors.append(f".mcp.json is invalid JSON: {e}")
    else:
        print("CONNECTORS=0 (no .mcp.json found)")

    # Check Google integration
    google = check_google_integration()
    if google["credentials"]:
        print(f"GOOGLE_CREDENTIALS=configured ({google.get('service_account_email', 'found')})")
    else:
        print("GOOGLE_CREDENTIALS=not_configured (sheets/drive scripts will prompt for setup)")

    if google["packages"]:
        print("GOOGLE_PACKAGES=installed")
    else:
        print("GOOGLE_PACKAGES=not_installed (will auto-install on first script run)")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
