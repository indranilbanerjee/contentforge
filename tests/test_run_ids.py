"""A run id keeps the topic's own letters, and two runs never share one.

Found by the installed-copy journeys of 4.5.12:
  * the run id's topic part kept only `\\w` characters, and Python's `\\w` does not match the vowel signs and the virama of
    Devanagari (or of Thai, Tamil, Arabic with marks), so a topic like "भारत में AI" was mangled into a run id that no longer
    read as the topic; the id validator used the same class, so a correct id would have been refused;
  * two `init` calls for the same topic in the same second produced the same run id, and the second silently reused the first
    run's folder and replaced its run.json.
Runs in a temp workspace; no network.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402


def load_checkpoint():
    spec = importlib.util.spec_from_file_location("_cf_checkpoint_run_ids", SCRIPTS / "checkpoint-manager.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        os.environ["CLAUDE_MARKETING_HOME"] = str(Path(self._tmp.name) / "ws")
        self.addCleanup(os.environ.pop, "CLAUDE_MARKETING_HOME", None)
        self.cm = load_checkpoint()


class TestTopicLettersSurvive(Workspace):

    def test_a_devanagari_topic_keeps_its_vowel_signs(self):
        slug = self.cm._slug("भारत में AI")
        self.assertEqual(slug, "भारत-में-ai")

    def test_other_scripts_with_combining_marks_survive(self):
        self.assertEqual(self.cm._slug("தமிழ் செய்தி"), "தமிழ்-செய்தி")
        self.assertEqual(self.cm._slug("Café Müller"), "café-müller")

    def test_punctuation_and_separators_still_go(self):
        self.assertEqual(self.cm._slug("a/b\\c:d..e?"), "abcde")
        self.assertEqual(self.cm._slug("   "), "untitled")

    def test_the_generated_id_is_accepted_by_the_validator(self):
        run_id = f"20261028-031500-{self.cm._slug('भारत में AI')}"
        self.assertEqual(_common.validate_run_id(run_id), run_id)
        self.assertTrue(self.cm.RUN_ID_RE.match(run_id))

    def test_the_validator_still_refuses_paths(self):
        for bad in ("../x", "20261028-031500-a/b", "20261028-031500-a\\b", "20261028-031500-a:b",
                    "20261028-031500-a.b", "20261028-031500-", "run-A", "20261028-031500-..", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    _common.validate_run_id(bad)
                self.assertFalse(self.cm.RUN_ID_RE.match(bad))


class TestTwoInitsInOneSecond(Workspace):

    def init(self, topic="Same topic"):
        frozen = datetime(2026, 10, 28, 3, 15, 0, tzinfo=timezone.utc)
        with mock.patch.object(self.cm, "datetime") as fake:
            fake.now.return_value = frozen
            fake.side_effect = lambda *a, **k: datetime(*a, **k)
            return self.cm.init_run("Acme", topic, "article")

    def test_the_second_init_gets_its_own_id_and_the_first_run_is_untouched(self):
        first = self.init()
        self.assertIn("run_id", first, first)
        first_dir = self.cm._run_dir("Acme", first["run_id"])
        before = (first_dir / "run.json").read_bytes()
        second = self.init()
        self.assertIn("run_id", second, second)
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertTrue(second["run_id"].startswith(first["run_id"]))
        self.assertEqual((first_dir / "run.json").read_bytes(), before)
        self.assertTrue((self.cm._run_dir("Acme", second["run_id"]) / "run.json").is_file())

    def test_a_third_init_counts_on(self):
        ids = [self.init()["run_id"] for _ in range(3)]
        self.assertEqual(len(set(ids)), 3, ids)
        for run_id in ids:
            self.assertEqual(_common.validate_run_id(run_id), run_id)


if __name__ == "__main__":
    unittest.main()
