#!/usr/bin/env python3
"""
_common.py
==========
Shared helpers for every ContentForge Python script. Stdlib only.

Why this exists: the tracker/checkpoint scripts each carried private copies of
brand-path building, slugification, REQ-id generation, priority clamping, JSON
persistence, and stdout encoding guards — and the copies drifted (three
different slugifiers produced three different directories for the same brand,
which broke the Cowork Drive-sync roundtrip). This module is now the single
source of truth. Scripts hard-require it: `import _common` works because
sys.path[0] is scripts/ when a script is invoked as `python scripts/x.py`;
each script also inserts its own directory into sys.path defensively.

Path policy (canon):
  * marketing_home() — $CLAUDE_MARKETING_HOME if set; else $CLAUDE_PLUGIN_DATA
    if set AND the directory exists; else ~/.claude-marketing
  * brand_dir(brand) — backward compatible: if a legacy directory named with
    the RAW brand string already exists under marketing_home(), keep using it;
    otherwise use the canonical slug directory (slugify_brand()).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────

MONTH_NAMES = {
    1: "01-January", 2: "02-February", 3: "03-March", 4: "04-April",
    5: "05-May", 6: "06-June", 7: "07-July", 8: "08-August",
    9: "09-September", 10: "10-October", 11: "11-November", 12: "12-December",
}


# ── Encoding ────────────────────────────────────────────────────────

def ensure_utf8_stdout() -> None:
    """Force UTF-8 (errors=replace) on stdout/stderr.

    Windows consoles default to cp1252; printing JSON containing em dashes or
    non-Latin content would otherwise raise UnicodeEncodeError mid-pipeline.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


# ── Paths ───────────────────────────────────────────────────────────

def marketing_home() -> Path:
    """Root of ContentForge persistent data.

    Resolution order:
      1. $CLAUDE_MARKETING_HOME (explicit override; used by tests)
      2. $CLAUDE_PLUGIN_DATA if set (non-empty) AND the directory exists
      3. ~/.claude-marketing
    """
    override = os.environ.get("CLAUDE_MARKETING_HOME")
    if override:
        return Path(override).expanduser()
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:  # empty string must NOT resolve to Path(".")
        p = Path(plugin_data).expanduser()
        if p.exists():
            return p
    return Path.home() / ".claude-marketing"


def slugify_brand(name: str) -> str:
    """Canonical brand slug: lowercase, non-alphanumeric runs → single hyphen,
    trimmed, max 60 chars. Empty input yields 'brand'."""
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60].rstrip("-") or "brand"


def brand_dir(brand: str) -> Path:
    """Per-brand data directory under marketing_home().

    Backward compatibility: if a directory named with the raw brand string
    already exists (created by pre-v3.16 scripts), keep using it so existing
    tracking/checkpoint data stays reachable. Otherwise use the slug directory.
    """
    home = marketing_home()
    raw = (brand or "").strip()
    if raw:
        try:
            legacy = home / raw
            if legacy.is_dir():
                return legacy
        except (OSError, ValueError):
            pass  # raw name not representable as a path component on this OS
    return home / slugify_brand(brand)


# ── JSON persistence ────────────────────────────────────────────────

def atomic_write_json(path: Path, data) -> None:
    """Write JSON atomically: tmp file in the same directory + os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    tmp.replace(path)


def load_json_safe(path: Path):
    """Load JSON, never raise. On failure returns a dict with 'error' and
    'recovery' keys instead of the payload; callers check `"error" in result`
    (payloads produced by ContentForge never carry a top-level 'error' key)."""
    path = Path(path)
    if not path.exists():
        return {
            "error": f"file not found: {path}",
            "missing": True,
            "recovery": "Initialise it first (e.g. --action init) or check the brand name.",
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "error": f"corrupt or unreadable JSON at {path}: {type(exc).__name__}: {exc}",
            "corrupt": True,
            "recovery": (
                f"The file may have been truncated by an interrupted write. "
                f"Inspect {path} manually; a sibling '{path.name}.tmp' file (if present) "
                f"may hold the last attempted write. Re-run init to start fresh."
            ),
        }


# ── CLI result handling ─────────────────────────────────────────────

def finish(result) -> "None":
    """Print the result JSON and exit: 1 when the result carries an error,
    0 otherwise. Every ContentForge CLI script funnels through this so shell
    callers can trust $?."""
    ensure_utf8_stdout()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    is_error = isinstance(result, dict) and "error" in result
    sys.exit(1 if is_error else 0)


# ── Small shared utilities ──────────────────────────────────────────

def clamp_priority(value, default: int = 3) -> int:
    """Coerce a priority to int and clamp into 1..5. Bad input → default."""
    try:
        return min(max(int(value), 1), 5)
    except (ValueError, TypeError):
        return default


def next_req_id(records) -> str:
    """Next REQ-NNN id from existing records.

    Accepts an iterable of dicts (with a 'requirement_id' key) or of raw
    id strings. Scans for the max numeric suffix to avoid collisions after
    deletions."""
    max_num = 0
    for rec in records or []:
        rid = rec.get("requirement_id", "") if isinstance(rec, dict) else str(rec or "")
        if rid.startswith("REQ-"):
            try:
                max_num = max(max_num, int(rid.split("-", 1)[1]))
            except (IndexError, ValueError):
                pass
    return f"REQ-{max_num + 1:03d}"


def pip_install(packages, label: str = None):
    """Run `pip install -q <packages>`. Returns None on success, or an
    error dict (with a manual-install hint) the caller should finish() with."""
    import subprocess
    pkgs = list(packages)
    print(f"Installing {label or ' '.join(pkgs)} (first run only)...", file=sys.stderr)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", *pkgs],
            stdout=subprocess.DEVNULL,
        )
        return None
    except Exception as exc:
        return {
            "error": f"automatic dependency install failed: {type(exc).__name__}: {exc}",
            "recovery": (
                f"Install manually: {sys.executable} -m pip install {' '.join(pkgs)} "
                f"(on externally-managed Pythons add --user or use a virtualenv), "
                f"then re-run this command."
            ),
        }
