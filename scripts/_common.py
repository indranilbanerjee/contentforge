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
      2. $CLAUDE_PLUGIN_DATA, else $PLUGIN_DATA (the Agent Plugins 1.0 standard
         name — Codex/ChatGPT/Cursor-hosted installs set only this one), if set
         (non-empty) AND the directory exists
      3. ~/.claude-marketing
    """
    override = os.environ.get("CLAUDE_MARKETING_HOME")
    if override:
        return Path(override).expanduser()
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA") or os.environ.get("PLUGIN_DATA")
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
    # The legacy branch is honoured only for a plain single-component name. A raw
    # "--brand ../.." or an absolute path must never select a directory outside
    # marketing_home() (Hermes review of 2026-10-04).
    if raw and is_single_component(raw):
        try:
            legacy = home / raw
            if legacy.is_dir():
                return legacy
        except (OSError, ValueError):
            pass  # raw name not representable as a path component on this OS
    return home / slugify_brand(brand)


# ── Path containment ────────────────────────────────────────────────

# A run id is always generated as {YYYYMMDD}-{HHMMSS}-{topic-slug}; anything else
# is rejected before it can be turned into a filesystem path. The slug is built from
# word characters (so a Japanese or Arabic topic gives a legitimate Unicode slug) and
# hyphens; no separator, dot or colon can appear in it.
RUN_ID_RE = re.compile(r"^\d{8}-\d{6}-[\w-]+$")


def is_single_component(name) -> bool:
    """True iff `name` is one plain path component: not empty, not '.' or '..',
    no separators (either kind), no drive or stream colon, no NUL, not absolute."""
    s = str(name if name is not None else "")
    if not s or s in (".", "..") or "\x00" in s:
        return False
    if "/" in s or "\\" in s or ":" in s:
        return False
    return Path(s).name == s and not Path(s).is_absolute()


def safe_child(base, name) -> Path:
    """`base / name`, resolved, guaranteed to stay directly inside `base`.

    Raises ValueError for a name with separators, '..', an absolute path or a
    drive/stream colon, or if the resolved result escapes `base` (a symlink
    inside `base` pointing out of it counts as escaping). Use it for every path
    built from a model-supplied or remote-supplied name before a read, write,
    unlink or rmtree."""
    if not is_single_component(name):
        raise ValueError(f"unsafe path component: {name!r}")
    base_resolved = Path(base).resolve()
    child = (base_resolved / str(name)).resolve()
    if child.parent != base_resolved:
        raise ValueError(f"path escapes its directory: {name!r}")
    return child


def run_id_arg(value):
    """argparse `type` for --run-id: one plain path component, or a clear usage error.

    Containment only: pipeline-tracker keeps accepting free-form ids ("run-A"), so the strict generated
    shape (YYYYMMDD-HHMMSS-slug) is enforced where ids are always generated - checkpoint-manager's
    `_run_dir` and drive-sync-state call `validate_run_id`."""
    import argparse
    if not is_single_component(value):
        raise argparse.ArgumentTypeError(
            f"run id must be a single folder name, not a path (no '/', backslash, '..' or ':'): {value!r}")
    return value


def validate_run_id(run_id) -> str:
    """Return `run_id` if it has the generated shape; raise ValueError otherwise."""
    if not isinstance(run_id, str) or not RUN_ID_RE.match(run_id) or not is_single_component(run_id):
        raise ValueError(f"invalid run id: {run_id!r} (expected YYYYMMDD-HHMMSS-topic-slug)")
    return run_id


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


# ── Run-directory fingerprint (audit freshness) ─────────────────────

def run_artifact_fingerprint(run_dir) -> dict:
    """Content hashes of the files a run audit reads, so "this audit is fresh"
    is a comparison and not a promise.

    Audited set — top level of the run directory only: ``run.json``, every
    ``phase-*`` artifact, ``source-draft.md`` and every ``*.docx``. The audit's
    own ``run-audit.json`` is excluded (it is the record being compared), as is
    ``_sync-pending.json`` (Drive-sync bookkeeping, rewritten after every save)
    and ``*.tmp`` files.

    Hashes, not mtimes: a Drive sync, a copy or a restore rewrites mtimes
    without changing a byte, and a hand edit inside the same second can leave
    an mtime ordering ambiguous. The bytes are the evidence.

    Returns ``{"algorithm": "sha256", "digest": <hex over the whole set>,
    "files": {name: sha256}}``.
    """
    import hashlib

    root = Path(run_dir)
    files = {}
    if root.is_dir():
        for p in sorted(root.iterdir()):
            name = p.name
            if not p.is_file() or name.endswith(".tmp"):
                continue
            if not (name == "run.json" or name.startswith("phase-")
                    or name == "source-draft.md" or name.lower().endswith(".docx")):
                continue
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            files[name] = h.hexdigest()
    whole = hashlib.sha256()
    for name in sorted(files):
        whole.update(f"{name}\t{files[name]}\n".encode("utf-8"))
    return {"algorithm": "sha256", "digest": whole.hexdigest(), "files": files}


def fingerprint_drift(recorded: dict, current: dict) -> list:
    """Human-readable differences between two fingerprints (empty = identical)."""
    rec = (recorded or {}).get("files", {}) or {}
    cur = (current or {}).get("files", {}) or {}
    drift = [f"{n} changed" for n in sorted(rec) if n in cur and rec[n] != cur[n]]
    drift += [f"{n} was added" for n in sorted(set(cur) - set(rec))]
    drift += [f"{n} was removed" for n in sorted(set(rec) - set(cur))]
    return drift


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


# Exact versions of every optional package a ContentForge script may ask for.
# These are the versions the scripts were tested against. A new version reaches a
# user only when this table is changed on purpose (and the tests are re-run), the
# same exact-pin discipline Hermes asks of catalog plugins.
PINNED_DEPENDENCIES = {
    "python-docx": "1.2.0",
    "c2pa-python": "0.38.0",
    "cryptography": "46.0.6",
    "pyairtable": "3.3.0",
    "google-api-python-client": "2.192.0",
    "google-auth": "2.49.1",
    "gspread": "6.2.1",
}

# Setting this to "1" for a single run is the user's explicit consent to let
# ContentForge run the pinned install command itself. Without it nothing is
# ever installed: the script prints the exact command and exits non-zero.
INSTALL_OPT_IN_ENV = "CONTENTFORGE_INSTALL_DEPS"


def pinned_specs(packages):
    """Map package names (any version specifier is ignored) to exact `name==x.y.z`
    pins from PINNED_DEPENDENCIES. Raises ValueError for an unpinned package."""
    out = []
    for p in packages:
        name = re.split(r"[<>=!~;\[ ]", str(p), maxsplit=1)[0].strip().lower().replace("_", "-")
        if name not in PINNED_DEPENDENCIES:
            raise ValueError(f"no pinned version for package {name!r}; add it to PINNED_DEPENDENCIES")
        out.append(f"{name}=={PINNED_DEPENDENCIES[name]}")
    return out


def install_command(packages) -> str:
    """The exact, pinned command a user would run to install `packages`."""
    exe = sys.executable
    if " " in exe:
        exe = f'"{exe}"'
    return f"{exe} -m pip install {' '.join(pinned_specs(packages))}"


def pip_install(packages, label: str = None):
    """Install `packages` at their pinned versions ONLY when the user opted in.

    Default (no opt-in): installs nothing and returns an error dict that carries
    the exact pinned command, which the caller finish()es with (exit 1).
    With CONTENTFORGE_INSTALL_DEPS=1 in the environment: runs that same command.
    Returns None on success, or the error dict."""
    import subprocess
    specs = pinned_specs(packages)
    command = install_command(packages)
    what = label or ", ".join(specs)
    if os.environ.get(INSTALL_OPT_IN_ENV) != "1":
        return {
            "error": f"{what} is not installed, and ContentForge never installs packages on its own",
            "recovery": (
                f"Install it yourself, then re-run this command: {command}  "
                f"(on externally-managed Pythons add --user or use a virtualenv). "
                f"To let ContentForge run exactly that command once, set "
                f"{INSTALL_OPT_IN_ENV}=1 for that run."
            ),
        }
    print(f"Installing {what} ({INSTALL_OPT_IN_ENV}=1 was set)...", file=sys.stderr)
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", *specs],
            stdout=subprocess.DEVNULL,
        )
        return None
    except Exception as exc:
        return {
            "error": f"dependency install failed: {type(exc).__name__}: {exc}",
            "recovery": (
                f"Install manually: {command} "
                f"(on externally-managed Pythons add --user or use a virtualenv), "
                f"then re-run this command."
            ),
        }
