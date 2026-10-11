"""The suite stays out of the user's real folders (4.5.7), and the guard that says so is itself tested.

The SocialForge suite was found appending to the customer's real failure log on every run (516 entries over 129 runs) because one
test isolated a folder and forgot another that the same code falls back to through `Path.home()`. The ContentForge suite writes
nothing outside its temporary folders today (every test file was run alone against a temporary home to check); this keeps it so.
The fix has two layers (see `_isolation.py`) and each one is proved here: the redirect keeps a forgetful test out of the real
folder, and the guard fails the session when something still gets in. The plants run the real `checkpoint-manager.py init` in a
child process against a FAKE home, with the redirect on, with only the guard on, and with neither, because a guard nobody has seen
fail has not been tested.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TESTS = Path(__file__).resolve().parent
SCRIPTS = TESTS.parent / "scripts"
sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(SCRIPTS))

import _isolation  # noqa: E402

_isolation.start()    # a direct run of this file is protected too; a no-op when the runner already started it

LEAK = r'''
import json, os, runpy, sys
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[2])
mode = sys.argv[3]
import _isolation
if mode in ("guard-only", "exit-hook"):
    _isolation.start(redirect=False)
elif mode == "full":
    _isolation.start()
script = os.path.join(sys.argv[2], "checkpoint-manager.py")
sys.argv = [script, "init", "--brand", "Plant Co", "--topic", "A plant", "--content-type", "article"]
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit:
    pass
if mode != "exit-hook":
    print(json.dumps({"problems": _isolation.finish()}))
'''


class TestTheSessionIsRedirected(unittest.TestCase):
    def test_home_points_into_the_temporary_folder_and_the_folder_variables_are_gone(self):
        """Judged from what start() did, not from os.environ now: a test may set or unset a folder variable of its own."""
        tmp = _isolation._state["tmp"]
        self.assertEqual(sorted(_isolation._state["redirected"]), sorted(_isolation.HOME_VARS))
        for name, value in _isolation._state["redirected"].items():
            with self.subTest(var=name):
                self.assertEqual(Path(value).parent, tmp)
        self.assertEqual(Path.home().parent, tmp)
        self.assertTrue(set(_isolation._state["removed"]) <= set(_isolation.DATA_VARS))

    def test_the_marketing_home_default_resolves_inside_it(self):
        import _common
        tmp = _isolation._state["tmp"]
        with mock.patch.dict(os.environ):
            for name in _isolation.DATA_VARS:
                os.environ.pop(name, None)
            self.assertEqual(_common.marketing_home(), Path.home() / ".claude-marketing")
            self.assertTrue(str(_common.marketing_home()).startswith(str(tmp)), _common.marketing_home())

    def test_the_guard_watches_both_default_folders_whatever_a_test_sets(self):
        """The redirect is the first layer, not the only one: the guard's list was taken before the redirect and names the defaults."""
        roots = [str(r) for r in _isolation._state["roots"]]
        self.assertTrue(any(r.endswith(".claude-marketing") for r in roots), roots)
        self.assertTrue(any(r.endswith(os.path.join("Documents", "ContentForge")) for r in roots), roots)

    def test_the_real_folders_named_by_the_guard_are_not_the_redirected_ones(self):
        tmp = _isolation._state["tmp"]
        self.assertTrue(_isolation._state["roots"], "the guard watches nothing")
        for root in _isolation._state["roots"]:
            self.assertFalse(str(root).startswith(str(tmp)), "the guard is watching the temporary folder, not the real one: %s" % root)
        self.assertFalse(str(_isolation.real_home()).startswith(str(tmp)), "real_home() must name the real home, not the temporary one")
        self.assertNotEqual(_isolation.real_home(), Path.home())


class TestTheSnapshotSeesEveryKindOfChange(unittest.TestCase):
    def test_added_changed_removed_new_folder_and_a_root_that_appears(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "workspace"
            root.mkdir()
            (root / "keep.txt").write_text("one", encoding="utf-8")
            (root / "edit.txt").write_text("one", encoding="utf-8")
            (root / "drop.txt").write_text("one", encoding="utf-8")
            missing = Path(d) / "not-there-yet"
            before = _isolation.snapshot([root, missing])
            self.assertEqual(_isolation.changes(before, _isolation.snapshot([root, missing])), [])
            (root / "edit.txt").write_text("one and more", encoding="utf-8")
            (root / "drop.txt").unlink()
            (root / "new.txt").write_text("x", encoding="utf-8")
            (root / "sub").mkdir()
            missing.mkdir()
            found = _isolation.changes(before, _isolation.snapshot([root, missing]))
            self.assertEqual(sorted(entry.split(":")[0] for entry in found), ["added", "added", "added", "changed", "removed"], found)
            self.assertTrue(any(entry.startswith("added: ") and entry.endswith("not-there-yet") for entry in found), found)
            self.assertFalse(any("keep.txt" in entry for entry in found), found)


class TestThePlantsTheGuardMustCatch(unittest.TestCase):
    """The real run-start script, run in a child process against a FAKE home so nothing real is at risk."""

    def _run(self, mode):
        with tempfile.TemporaryDirectory() as fake_home:
            env = {k: v for k, v in os.environ.items() if k not in _isolation.DATA_VARS}
            env.update(HOME=fake_home, USERPROFILE=fake_home, PYTHONIOENCODING="utf-8")
            r = subprocess.run([sys.executable, "-c", LEAK, str(TESTS), str(SCRIPTS), mode],
                               capture_output=True, text=True, env=env, timeout=120)
            home_data = Path(fake_home) / ".claude-marketing"
            leaked = home_data.is_dir() and any(home_data.rglob("*.json"))
            lines = r.stdout.strip().splitlines()
            out = json.loads(lines[-1]) if lines and lines[-1].startswith('{"problems"') else None
            return r, leaked, out

    def test_without_the_fixture_the_run_start_does_reach_the_home_folder(self):
        """The victim can be hit: this is the behaviour a forgetful test would have, and the reason the other plants mean anything."""
        r, leaked, _ = self._run("off")
        self.assertTrue(leaked, "the plant did not reproduce a leak, so the next tests prove nothing:\n" + r.stdout + r.stderr)

    def test_the_guard_alone_catches_the_leak(self):
        r, leaked, out = self._run("guard-only")
        self.assertTrue(leaked, r.stdout + r.stderr)
        self.assertTrue(any(p.startswith("added: ") and ".claude-marketing" in p for p in out["problems"]), out)
        self.assertIn("TEST SUITE TOUCHED THE USER'S REAL FOLDERS", _isolation.report(out["problems"]))

    def test_the_redirect_alone_keeps_the_same_run_out_of_the_home_folder(self):
        r, leaked, out = self._run("full")
        self.assertFalse(leaked, "the redirect did not hold:\n" + r.stdout + r.stderr)
        self.assertEqual(out["problems"], [])

    def test_a_run_nobody_wraps_still_exits_nonzero_when_the_guard_trips(self):
        """`python tests/test_x.py` has no runner hook; the exit hook turns a leak into exit status 1."""
        r, leaked, _ = self._run("exit-hook")
        self.assertTrue(leaked, r.stdout + r.stderr)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("TEST SUITE TOUCHED THE USER'S REAL FOLDERS", r.stderr)


if __name__ == "__main__":
    unittest.main()
