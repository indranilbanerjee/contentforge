"""resolve_model.py semantics — retired/deprecated rewrites and CLI exit codes."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import resolve_model  # noqa: E402

REGISTRY = json.loads((SCRIPTS_DIR / "model_registry.json").read_text(encoding="utf-8"))
MODELS = REGISTRY.get("models", [])


def _first(status, with_replacement=True):
    for m in MODELS:
        if m.get("status") == status and (not with_replacement or m.get("replacement_id")):
            return m
    return None


def run_cli(*args):
    proc = subprocess.run([sys.executable, str(SCRIPTS_DIR / "resolve_model.py"), *args],
                          capture_output=True, env=os.environ.copy())
    return proc.returncode, proc.stdout.decode("utf-8", "replace").strip()


class TestResolveSemantics(unittest.TestCase):
    def test_retired_resolves_to_replacement(self):
        m = _first("retired")
        self.assertIsNotNone(m, "registry should contain a retired model with replacement_id")
        self.assertEqual(resolve_model.resolve(m["id"]), m["replacement_id"])

    def test_retired_rewritten_even_with_allow_deprecated(self):
        m = _first("retired")
        self.assertEqual(resolve_model.resolve(m["id"], allow_deprecated=True),
                         m["replacement_id"])

    def test_deprecated_resolves_to_replacement(self):
        m = _first("deprecated")
        self.assertIsNotNone(m)
        self.assertEqual(resolve_model.resolve(m["id"]), m["replacement_id"])

    def test_current_passes_through(self):
        m = _first("current", with_replacement=False)
        self.assertEqual(resolve_model.resolve(m["id"]), m["id"])

    def test_check_reports_status(self):
        m = _first("retired")
        status, repl = resolve_model.check(m["id"])
        self.assertEqual(status, "retired")
        self.assertEqual(repl, m["replacement_id"])

    def test_unknown_raises(self):
        with self.assertRaises(KeyError):
            resolve_model.resolve("model-that-does-not-exist-xyz")


class TestCliExitCodes(unittest.TestCase):
    def test_check_current_exits_0(self):
        m = _first("current", with_replacement=False)
        rc, _ = run_cli("--check", m["id"])
        self.assertEqual(rc, 0)

    def test_check_deprecated_exits_1(self):
        m = _first("deprecated")
        rc, out = run_cli("--check", m["id"])
        self.assertEqual(rc, 1, out)

    def test_check_retired_exits_1(self):
        # Regression: retired used to exit 0 despite being worse than deprecated.
        m = _first("retired")
        rc, out = run_cli("--check", m["id"])
        self.assertEqual(rc, 1, out)

    def test_check_unknown_exits_1(self):
        rc, _ = run_cli("--check", "model-that-does-not-exist-xyz")
        self.assertEqual(rc, 1)

    def test_alias_resolves_exit_0(self):
        aliases = REGISTRY.get("aliases", {})
        self.assertTrue(aliases, "registry should define aliases")
        alias = next(iter(aliases))
        rc, out = run_cli("--alias", alias)
        self.assertEqual(rc, 0)
        self.assertTrue(out)


if __name__ == "__main__":
    unittest.main()
