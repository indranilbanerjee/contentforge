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

Called by hooks/hooks.json SessionStart hook.
"""

import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
SCRIPTS_DIR = PLUGIN_ROOT / "scripts"


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

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
