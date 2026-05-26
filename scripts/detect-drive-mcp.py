#!/usr/bin/env python3
"""
detect-drive-mcp.py
===================
Probe .mcp.json for Google Drive connectivity BEFORE walking a user
through the legacy service-account setup flow.

ContentForge has two ways to reach Google Drive:

  A) Service-account JSON path  — scripts/drive-uploader.py uses the
     google-api-python-client SDK with credentials at
     ~/.claude-marketing/google-credentials.json. Required for fully
     automated, programmatic Drive uploads (no MCP needed).

  B) MCP path — when a Drive-capable MCP server is in .mcp.json, Claude
     can read/list/upload via MCP tool calls. Works in Cowork (no
     service account, no Node.js). Known Drive-capable MCPs:
       - google-drive (Anthropic-platform-level via Settings -> Integrations)
       - pipedream-google-drive
       - composio-google-drive
       - zapier-google-drive
       - make-google-drive

Before v3.12.7, brand-setup assumed (A) was the only path. If a user
came in having already added (B), brand-setup would walk them through
the service-account flow anyway — which felt redundant and ignored
their existing config. This script lets brand-setup ask once: "I see
you have <connector_name> connected — want me to use that for the
input/output folder structure?"

Usage:
    python detect-drive-mcp.py                # prints JSON status
    python detect-drive-mcp.py --quiet        # exit code only
    python detect-drive-mcp.py --plugin-root /path/to/contentforge

Exit codes:
    0 = a Drive-capable MCP is configured
    1 = no Drive MCP detected
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# Drive-capable MCP server names. Order = display priority.
KNOWN_DRIVE_MCPS = [
    ("google-drive",
     "Anthropic platform Google Drive (set up in Cowork Settings -> Integrations, "
     "or Claude.com platform integrations)"),
    ("pipedream-google-drive",
     "Pipedream aggregator -- works in both Cowork and Claude Code"),
    ("composio-google-drive",
     "Composio aggregator -- works in both Cowork and Claude Code"),
    ("zapier-google-drive",
     "Zapier aggregator -- works in both Cowork and Claude Code"),
    ("make-google-drive",
     "Make.com aggregator -- works in both Cowork and Claude Code"),
    ("drive-mcp",
     "Generic Drive MCP server"),
    ("mcp-google-drive",
     "npx-style Google Drive MCP (Claude Code only)"),
]

# Service-account credentials file (legacy / non-MCP path)
DEFAULT_CREDS_FILE = Path.home() / ".claude-marketing" / "google-credentials.json"


def probe_mcp_json(plugin_root: Path) -> dict:
    """Read .mcp.json and identify configured Drive connectors."""
    mcp_path = plugin_root / ".mcp.json"
    if not mcp_path.exists():
        return {"present": False, "configured_drive_mcps": [], "raw_servers": []}
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"present": True, "error": f"{type(e).__name__}: {e}",
                "configured_drive_mcps": [], "raw_servers": []}

    servers = data.get("mcpServers", {}) or {}
    server_names = list(servers.keys())
    found = []
    for known, description in KNOWN_DRIVE_MCPS:
        if known in servers:
            found.append({
                "name": known,
                "description": description,
                "transport": servers[known].get("type", servers[known].get("command", "unknown")),
            })

    # Also flag any server whose name matches a heuristic — catches generic /
    # user-renamed Drive connectors that aren't in the well-known list.
    heuristic_matches = []
    for name in server_names:
        if name in {f["name"] for f in found}:
            continue
        nl = name.lower()
        if "drive" in nl and "google" in nl:
            heuristic_matches.append({
                "name": name,
                "description": "Heuristic match (name contains 'google' + 'drive')",
                "transport": servers[name].get("type", servers[name].get("command", "unknown")),
            })

    return {
        "present": True,
        "configured_drive_mcps": found,
        "heuristic_drive_mcps": heuristic_matches,
        "raw_servers": server_names,
    }


def probe_service_account() -> dict:
    """Check if the legacy service-account credentials file exists."""
    exists = DEFAULT_CREDS_FILE.exists()
    result = {"path": str(DEFAULT_CREDS_FILE), "exists": exists}
    if exists:
        try:
            data = json.loads(DEFAULT_CREDS_FILE.read_text(encoding="utf-8"))
            result["client_email"] = data.get("client_email", "unknown")
            result["project_id"] = data.get("project_id", "unknown")
        except (json.JSONDecodeError, OSError):
            result["error"] = "credentials file exists but is unreadable or malformed"
    return result


def synthesize_recommendation(mcp_probe: dict, sa_probe: dict) -> dict:
    """Decide which path brand-setup should take."""
    has_mcp = bool(mcp_probe.get("configured_drive_mcps") or
                   mcp_probe.get("heuristic_drive_mcps"))
    has_sa = sa_probe.get("exists", False) and "error" not in sa_probe

    if has_mcp and has_sa:
        return {
            "recommended_path": "mcp_or_service_account",
            "message": "Both a Google Drive MCP AND a service-account credentials "
                       "file are configured. The MCP path is preferred when both "
                       "are present (works in Cowork, simpler auth). Use the "
                       "service account only if you need fully unattended uploads "
                       "(e.g. cron jobs).",
        }
    if has_mcp:
        primary = (mcp_probe.get("configured_drive_mcps") or
                   mcp_probe.get("heuristic_drive_mcps"))[0]
        return {
            "recommended_path": "mcp",
            "primary_connector": primary["name"],
            "message": (
                f"A Google Drive MCP is configured ('{primary['name']}'). "
                f"brand-setup will offer this as the input/output folder route "
                f"BEFORE asking for service-account credentials. Drive folders "
                f"are read/listed/uploaded via MCP tool calls — no Python SDK "
                f"or service-account JSON needed."),
        }
    if has_sa:
        return {
            "recommended_path": "service_account",
            "message": f"Service-account credentials found at {sa_probe['path']} "
                       f"(client_email: {sa_probe.get('client_email')}). "
                       f"brand-setup will use the service-account upload path.",
        }
    return {
        "recommended_path": "none",
        "message": "No Google Drive route configured. brand-setup will default to "
                   "local-only tracking (~/.claude-marketing/{brand}/) and offer "
                   "the user the choice between (a) adding a Drive MCP via "
                   "/contentforge:cf-add-integration, (b) setting up a service "
                   "account via the Step A flow, or (c) keeping local-only.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", default=None,
                        help="path to plugin root (default: parent of this script)")
    parser.add_argument("--quiet", action="store_true",
                        help="exit code only; no JSON output")
    args = parser.parse_args()

    if args.plugin_root:
        plugin_root = Path(args.plugin_root).resolve()
    else:
        plugin_root = Path(__file__).resolve().parent.parent

    mcp_probe = probe_mcp_json(plugin_root)
    sa_probe = probe_service_account()
    recommendation = synthesize_recommendation(mcp_probe, sa_probe)

    has_any_drive = (recommendation["recommended_path"] != "none")

    result = {
        "plugin_root": str(plugin_root),
        "mcp_probe": mcp_probe,
        "service_account_probe": sa_probe,
        "recommendation": recommendation,
        "has_any_drive_route": has_any_drive,
    }

    if not args.quiet:
        print(json.dumps(result, indent=2))
    sys.exit(0 if has_any_drive else 1)


if __name__ == "__main__":
    main()
