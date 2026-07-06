"""Tests for scripts/_common.py — the shared helper module."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import _common  # noqa: E402


class EnvHomeMixin(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self._saved = os.environ.get("CLAUDE_MARKETING_HOME")
        os.environ["CLAUDE_MARKETING_HOME"] = str(self.home)

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("CLAUDE_MARKETING_HOME", None)
        else:
            os.environ["CLAUDE_MARKETING_HOME"] = self._saved
        self._tmp.cleanup()


class TestSlugifyBrand(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(_common.slugify_brand("Acme Corp"), "acme-corp")

    def test_punctuation_collapses(self):
        self.assertEqual(_common.slugify_brand("O'Reilly  Media!!"), "o-reilly-media")

    def test_max_60_chars(self):
        self.assertLessEqual(len(_common.slugify_brand("x" * 200)), 60)

    def test_empty_yields_brand(self):
        self.assertEqual(_common.slugify_brand(""), "brand")
        self.assertEqual(_common.slugify_brand("!!!"), "brand")

    def test_already_slug_unchanged(self):
        self.assertEqual(_common.slugify_brand("acme-corp"), "acme-corp")


class TestClampPriority(unittest.TestCase):
    def test_in_range(self):
        self.assertEqual(_common.clamp_priority(2), 2)

    def test_clamps_high_and_low(self):
        self.assertEqual(_common.clamp_priority(99), 5)
        self.assertEqual(_common.clamp_priority(0), 1)

    def test_string_number(self):
        self.assertEqual(_common.clamp_priority("4"), 4)

    def test_garbage_returns_default(self):
        self.assertEqual(_common.clamp_priority("high"), 3)
        self.assertEqual(_common.clamp_priority(None), 3)


class TestNextReqId(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(_common.next_req_id([]), "REQ-001")
        self.assertEqual(_common.next_req_id(None), "REQ-001")

    def test_dicts(self):
        records = [{"requirement_id": "REQ-007"}, {"requirement_id": "junk"}, {}]
        self.assertEqual(_common.next_req_id(records), "REQ-008")

    def test_strings(self):
        self.assertEqual(_common.next_req_id(["REQ-002", "REQ-010"]), "REQ-011")

    def test_gap_tolerant(self):
        # After deletions, next id must exceed the MAX, not the count.
        records = [{"requirement_id": "REQ-005"}]
        self.assertEqual(_common.next_req_id(records), "REQ-006")


class TestAtomicWriteAndLoad(EnvHomeMixin):
    def test_roundtrip(self):
        p = self.home / "sub" / "data.json"
        _common.atomic_write_json(p, {"a": 1, "s": "ünïcode — em"})
        data = _common.load_json_safe(p)
        self.assertEqual(data["a"], 1)
        self.assertEqual(data["s"], "ünïcode — em")

    def test_no_tmp_left_behind(self):
        p = self.home / "data.json"
        _common.atomic_write_json(p, {"x": True})
        self.assertFalse((self.home / "data.json.tmp").exists())

    def test_load_missing_returns_error_dict(self):
        result = _common.load_json_safe(self.home / "nope.json")
        self.assertIn("error", result)
        self.assertTrue(result.get("missing"))
        self.assertIn("recovery", result)

    def test_load_corrupt_returns_error_dict(self):
        p = self.home / "bad.json"
        p.write_text('{"truncated": ', encoding="utf-8")
        result = _common.load_json_safe(p)
        self.assertIn("error", result)
        self.assertTrue(result.get("corrupt"))
        self.assertIn("recovery", result)


class TestMarketingHomeAndBrandDir(EnvHomeMixin):
    def test_env_override_wins(self):
        self.assertEqual(_common.marketing_home(), self.home)

    def test_brand_dir_uses_slug_when_no_legacy(self):
        self.assertEqual(_common.brand_dir("Acme Corp"), self.home / "acme-corp")

    def test_brand_dir_prefers_existing_legacy_raw_dir(self):
        legacy = self.home / "Acme Corp"
        legacy.mkdir(parents=True)
        self.assertEqual(_common.brand_dir("Acme Corp"), legacy)

    def test_plugin_data_empty_string_does_not_resolve_to_cwd(self):
        # Regression: setup.py used Path(os.environ.get("CLAUDE_PLUGIN_DATA", ""))
        # which normalises to Path(".") and always exists.
        os.environ.pop("CLAUDE_MARKETING_HOME", None)
        saved = os.environ.get("CLAUDE_PLUGIN_DATA")
        os.environ["CLAUDE_PLUGIN_DATA"] = ""
        try:
            home = _common.marketing_home()
            self.assertNotEqual(str(home), ".")
            self.assertEqual(home, Path.home() / ".claude-marketing")
        finally:
            if saved is None:
                os.environ.pop("CLAUDE_PLUGIN_DATA", None)
            else:
                os.environ["CLAUDE_PLUGIN_DATA"] = saved
            os.environ["CLAUDE_MARKETING_HOME"] = str(self.home)


if __name__ == "__main__":
    unittest.main()
