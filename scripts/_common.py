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

import hashlib
import json
import os
import re
import sys
import unicodedata
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


# Windows device names: no file or folder can carry one, with or without an extension.
WINDOWS_RESERVED = frozenset({"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                              *(f"lpt{i}" for i in range(1, 10))})


def _ascii_slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return re.sub(r"-+", "-", s).strip("-")[:60].rstrip("-")


def legacy_slug(name: str) -> str:
    """The slug before 4.6.0, which dropped every non-ASCII letter ("Café" -> "caf", any Devanagari or
    CJK name -> "brand"). Used only to find folders created under it."""
    return _ascii_slug(name or "") or "brand"


def safe_slug(text: str, fallback: str = "brand") -> str:
    """A file-name-safe ASCII slug that keeps different names apart (the same function as Digital Marketing
    Pro's _common.safe_slug; tests/test_brand_slugs.py pins the same vectors in both).

    ASCII text gives exactly the old slug. Accents fold ("Café" -> "cafe"). When letters, digits or emoji
    from another script remain (Devanagari, CJK, Arabic, Cyrillic), the ASCII part gets a six-character tag from
    a hash of the name, so two such names never share a slug. A Windows device name gets "-<fallback>" appended."""
    name = unicodedata.normalize("NFKC", text or "").strip()
    folded = "".join(c for c in unicodedata.normalize("NFKD", name) if not unicodedata.combining(c))
    slug = _ascii_slug(folded)
    if any(not c.isascii() and unicodedata.category(c)[0] in "LNM" or unicodedata.category(c) == "So"
           for c in folded):
        tag = hashlib.sha256(name.casefold().encode("utf-8")).hexdigest()[:6]
        slug = f"{slug[:53].rstrip('-') or fallback}-{tag}"
    slug = slug or fallback
    return f"{slug}-{fallback}" if slug in WINDOWS_RESERVED else slug


def slugify_brand(name: str) -> str:
    """Canonical brand slug (safe_slug with the fallback "brand"). One slugifier for every script."""
    return safe_slug(name, "brand")


def same_brand_name(a, b) -> bool:
    """True when two brand names are the same name (case and Unicode normal form aside)."""
    norm = lambda s: unicodedata.normalize("NFKC", str(s or "")).strip().casefold()  # noqa: E731
    return norm(a) == norm(b)


BRAND_RECORD = "brand.json"


def read_brand_record(directory: Path):
    """The brand name a folder says it belongs to, or None (no record, or an unreadable one)."""
    try:
        doc = json.loads((Path(directory) / BRAND_RECORD).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None
    name = doc.get("brand_name") if isinstance(doc, dict) else None
    return name if isinstance(name, str) and name.strip() else None


def claim_brand_dir(brand: str):
    """(directory, None), or (None, error) when a different brand already holds this folder.

    A folder remembers whose it is in brand.json. Two brands whose slugs coincide must never share a folder
    (4.5.12 gave every Japanese, Arabic or Cyrillic brand the folder "brand"): the second one is refused, by
    name, instead of reading the first one's rows. A folder with no record (made before 4.6.0) is claimed by
    the first brand that names it. Creating a record never changes an existing one."""
    directory = brand_dir(brand)
    held = read_brand_record(directory)
    name = (brand or "").strip()
    if held is not None and name and not same_brand_name(held, name):
        return None, (f"the folder {directory.name!r} already belongs to the brand {held!r}, not {name!r}: "
                      f"use the exact name {held!r}, or give this brand its own name")
    if held is None and name and directory.is_dir():
        try:
            atomic_write_json(directory / BRAND_RECORD, {"brand_name": name, "slug": directory.name})
        except OSError:
            pass  # a read-only folder keeps working; it just stays unlabelled
    return directory, None


def documents_dir(shell=None, windows=None) -> Path:
    """The user's Documents folder. On Windows it is often redirected (OneDrive "Known Folder Move" makes it
    %USERPROFILE%\\OneDrive\\Documents), and ~/Documents is then a second, un-synced folder that Explorer's Documents page never
    shows. It is asked of the shell only when HOME is still the real profile folder: a sandbox or a test that points HOME elsewhere
    must not be sent to the real user's Documents. Anywhere else, or without an answer, it is ~/Documents."""
    home = Path.home()
    if windows is None:
        windows = os.name == "nt"
    if windows:
        if shell is None:
            def shell(csidl):
                try:
                    import ctypes
                    from ctypes import wintypes
                    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
                    if ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf) == 0 and buf.value:
                        return Path(buf.value)
                except (AttributeError, ImportError, OSError):
                    pass
                return None
        profile, documents = shell(40), shell(5)  # CSIDL_PROFILE, CSIDL_PERSONAL
        if profile and documents and os.path.normcase(str(profile)) == os.path.normcase(str(home)):
            return Path(documents)
    return home / "Documents"


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
    slug = slugify_brand(brand)
    # A folder made under the pre-4.6.0 slug ("Café" -> "caf"): reachable while no folder exists under the new slug,
    # when its brand.json names this brand. An unlabelled one is taken only if its slug is not the old catch-all "brand",
    # which held every non-Latin brand at once.
    old = legacy_slug(brand)
    if raw and old != slug and not (home / slug).exists() and (home / old).is_dir():
        held = read_brand_record(home / old)
        if (held is not None and same_brand_name(held, raw)) or (held is None and old != "brand"):
            return home / old
    return home / slug


# ── Path containment ────────────────────────────────────────────────

# A run id is always generated as {YYYYMMDD}-{HHMMSS}-{topic-slug}; anything else
# is rejected before it can be turned into a filesystem path. The slug is built from
# word characters (so a Japanese or Arabic topic gives a legitimate Unicode slug) and
# hyphens; no separator, dot or colon can appear in it.
class _RunIdShape:
    """`RUN_ID_RE.match(value)`: truthy for {YYYYMMDD}-{HHMMSS}-{slug}, where the slug is letters, digits, combining marks,
    "-" and "_" of any script. (A `\\w` class drops the vowel signs and the virama of Devanagari, Tamil and Thai, so a
    correctly spelled topic produced an id the validator refused.)"""

    HEAD = re.compile(r"^\d{8}-\d{6}-")

    def match(self, value):
        if not isinstance(value, str) or not self.HEAD.match(value) or len(value) == 16:
            return None
        ok = all(c in "-_" or unicodedata.category(c)[0] in "LNM" for c in value[16:])
        return value if ok else None


RUN_ID_RE = _RunIdShape()


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
        # utf-8-sig: PowerShell 5.1 writes a BOM by default (Out-File, Set-Content -Encoding utf8); plain UTF-8 reads the same
        return json.loads(path.read_text(encoding="utf-8-sig"))
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
    "matplotlib": "3.10.9",
    "pillow": "12.3.0",
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


PYTHON_PREFERRED = (3, 11)


def python_floor_warning(version=None):
    """A warning when this interpreter is older than 3.11, else None.

    Python 3.10 reached end of life on 2026-10-01 (PEP 619), but Claude's Cowork environment ran 3.10.12 when last checked,
    so NO release is promised for the move: ContentForge still runs on 3.10 and will move to 3.11 once Cowork does. The warning says that,
    conditionally, and asks for 3.11 or newer where the user can."""
    found = tuple((version or sys.version_info)[:2])
    if found < PYTHON_PREFERRED:
        return ("Python 3.10 reached end of life on 2026-10-01. ContentForge still runs on it, and will move to 3.11 once Claude's Cowork "
                "environment does (it ran 3.10.12 when last checked). Use 3.11 or newer where you can.")
    return None


def printed_command(*tokens: str) -> str:
    """A command to PRINT, ready to paste into Git Bash or PowerShell: the interpreter that is running now, then `tokens`. The
    interpreter path uses FORWARD slashes (bash drops a backslash, so `C:\\Python313\\python.exe` arrives as `C:Python313python.exe`)
    and is quoted only when it has a space, because a quoted first token is a string literal in PowerShell; then the line ends with
    a trailing comment (bash and PowerShell both ignore it) saying to put `&` before it. A parenthetical there is a syntax error in
    bash, and anything appended after the line lands inside the comment, so a caller puts prose BEFORE the command and passes every
    argument as a token. Code that RUNS something passes an argv list to subprocess instead and never uses this."""
    exe = sys.executable.replace("\\", "/")
    spaced = " " in exe
    line = " ".join(['"%s"' % exe if spaced else exe, *tokens])
    return line + "  # in PowerShell, put & before it" if spaced else line


def _quote_arg(arg: str) -> str:
    return '"%s"' % arg if any(c.isspace() for c in arg) and '"' not in arg else arg


def script_command(script: str, *args: str) -> str:
    """The exact command that runs one of this plugin's scripts (see printed_command): the script's absolute path with forward
    slashes, always double-quoted, then the arguments (quoted when they contain a space). A printed `python scripts/x.py` is relative
    to the host's working folder (the user's project), which is the wrong place, so every command a script tells someone to run
    comes from here."""
    path = str(Path(__file__).resolve().parent / script).replace("\\", "/")
    return printed_command('"%s"' % path, *[_quote_arg(a) for a in args])


def install_command(packages) -> str:
    """The exact, pinned command a user would run to install `packages`, in the printed shape (see printed_command). It is only
    ever PRINTED: pip_install runs an argv list."""
    return printed_command("-m", "pip", "install", *pinned_specs(packages))


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
                f"On externally-managed Pythons add --user or use a virtualenv. "
                f"To let ContentForge run exactly that command once, set "
                f"{INSTALL_OPT_IN_ENV}=1 for that run. "
                f"Or install it yourself, then re-run this command: {command}"
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
                f"On externally-managed Pythons add --user or use a virtualenv, then re-run this command. "
                f"Install manually: {command}"
            ),
        }
