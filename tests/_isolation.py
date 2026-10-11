"""The test suite never touches the user's real folders, and fails the session if it ever does.

4.5.7: the SocialForge suite was found appending four entries to the customer's real failure log on every run (516 over 129 runs):
a test isolated one folder and forgot another that the same code falls back to through `Path.home()`. The ContentForge suite was
checked the same way (every test file run alone against a temporary home) and writes nothing outside it, so this is prevention.

Two layers, because one test forgetting to isolate must not be enough to reach a real folder:

1. `start()` points HOME and USERPROFILE at a temporary folder and removes every folder variable the scripts read
   (CLAUDE_MARKETING_HOME, CLAUDE_PLUGIN_DATA, PLUGIN_DATA, CONTENTFORGE_PUBLISH_DIR), before any test module is imported. A
   test that sets nothing therefore falls back to a default, and every default (`~/.claude-marketing`, `~/Documents/ContentForge`)
   now lives inside the temporary folder.
2. `start()` also snapshots the REAL folders (path, size, mtime of every file) and `finish()` compares at the end. Any added,
   removed or changed file is a failure of the whole session, so the next leak is loud instead of months old.

`tests/__init__.py` starts it for pytest and `python -m unittest`, `run_all.py` starts it for the stdlib runner, and an exit hook
covers direct runs of one test file. `start(redirect=False)` is the guard alone, used to prove the guard catches a leak.
"""
from __future__ import annotations

import atexit
import os
import shutil
import sys
import tempfile
from pathlib import Path

HOME_VARS = ("HOME", "USERPROFILE")
DATA_VARS = ("CLAUDE_MARKETING_HOME", "CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "CONTENTFORGE_PUBLISH_DIR")

_state: dict = {"started": False, "finished": False}


def real_folders() -> list:
    """The folders a ContentForge run really writes to for this user, as the environment names them at this moment."""
    roots = [Path.home() / ".claude-marketing", Path.home() / "Documents" / "ContentForge"]
    roots += [Path(os.environ[name]) for name in DATA_VARS if os.environ.get(name)]
    unique, seen = [], set()
    for root in roots:
        key = os.path.normcase(os.path.abspath(root))
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def real_home() -> Path:
    """The user's real home, for the one test that READS a preserved real run from it. Reads are safe: the guard proves nothing changed."""
    return _state.get("real_home") or Path.home()


def snapshot(roots) -> dict:
    """path -> "dir" | "absent" | (size, mtime_ns) for every folder and file under each root."""
    seen: dict = {}
    for root in roots:
        root = str(root)
        if not os.path.isdir(root):
            seen[root] = "absent"
            continue
        seen[root] = "dir"
        for dirpath, dirnames, filenames in os.walk(root, onerror=lambda error: None):
            for name in dirnames:
                seen[os.path.join(dirpath, name)] = "dir"
            for name in filenames:
                path = os.path.join(dirpath, name)
                try:
                    stat = os.stat(path)
                except OSError:
                    continue
                seen[path] = (stat.st_size, stat.st_mtime_ns)
    return seen


def changes(before: dict, after: dict) -> list:
    out = []
    for path in sorted(set(before) | set(after)):
        was, now = before.get(path), after.get(path)
        if was == now:
            continue
        if was in (None, "absent"):
            out.append("added: " + path)
        elif now in (None, "absent"):
            out.append("removed: " + path)
        else:
            out.append("changed: " + path)
    return out


def start(redirect: bool = True) -> None:
    """Idempotent. Call before any test module is imported."""
    if _state["started"]:
        return
    _state.update(started=True, finished=False, roots=real_folders(), real_home=Path.home())
    _state["before"] = snapshot(_state["roots"])
    if redirect:
        tmp = Path(tempfile.mkdtemp(prefix="cf-tests-"))
        home = tmp / "home"
        home.mkdir()
        for name in HOME_VARS:
            os.environ[name] = str(home)
        # The folder variables are REMOVED rather than pointed somewhere: a test of a fallback ("CLAUDE_PLUGIN_DATA is empty, so
        # ~/.claude-marketing") must see the defaults a fresh machine has, and with HOME redirected every default resolves inside
        # the temporary home. The guard above already recorded where the real values point.
        _state["removed"] = [name for name in DATA_VARS if os.environ.pop(name, None) is not None]
        _state["tmp"] = tmp
        _state["redirected"] = {name: os.environ[name] for name in HOME_VARS}
    atexit.register(_at_exit)


def finish() -> list:
    """Compare the real folders with their snapshot and remove the temporary folder. Returns the changes (empty is good)."""
    if not _state["started"] or _state["finished"]:
        return []
    _state["finished"] = True
    problems = changes(_state["before"], snapshot(_state["roots"]))
    if _state.get("tmp"):
        shutil.rmtree(_state["tmp"], ignore_errors=True)
    return problems


def report(problems: list) -> str:
    shown = problems[:12]
    more = "" if len(problems) <= 12 else "\n  ... and %d more" % (len(problems) - 12)
    return ("\nTEST SUITE TOUCHED THE USER'S REAL FOLDERS (%d change%s):\n  %s%s\n"
            "A test wrote there instead of into its temporary folder, or a live ContentForge run wrote there while the suite ran: "
            "run the suite again to tell which. A test that leaks is a bug: it pollutes the customer's own brand data and run history."
            % (len(problems), "" if len(problems) == 1 else "s", "\n  ".join(shown), more))


def _at_exit() -> None:
    """Direct runs (`python tests/test_x.py`) have no runner hook, so the exit hook enforces the guard."""
    problems = finish()
    if problems:
        sys.stderr.write(report(problems))
        sys.stderr.flush()
        os._exit(1)
