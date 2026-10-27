"""Brands whose names share no ASCII letters must not share a folder.

4.5.12 slugged every brand with no ASCII letters to "brand", so 東京ブランド and 大阪商事 shared ~/.claude-marketing/brand: the
second brand's `init` reported "already_initialized" and `get-pending` returned the first brand's rows, and every later write
(runs, audits, profile, publish folder) landed in the shared folder. A Latin name with an accent was only lossy ("Café" ->
"caf"). Mixed names collided too ("भारत Foods" and "चीन Foods" both -> "foods").

The slug function is a copy of Digital Marketing Pro's safe_slug, and the vectors below are pinned in both plugins so the two
cannot drift apart. A folder also remembers whose it is (brand.json): the second brand to name a held slug is refused, by
name, and a create never overwrites. A folder made under the old slug stays reachable while it is unambiguous.
Everything runs against a temp workspace.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402

VECTORS = [
    ("Acme", "acme"),
    ("Café Noir", "cafe-noir"),
    ("भारत चाय", "brand-d08c85"),
    ("भारत Foods", "foods-bb073d"),
    ("चीन Foods", "foods-3a10f7"),
    ("東京ブランド", "brand-fa1e53"),
    ("大阪商事", "brand-462a02"),
    ("ñandú", "nandu"),
    ("Nul", "nul-brand"),
    ("CON", "con-brand"),
    ("", "brand"),
]


class TestSlugVectors(unittest.TestCase):

    def test_the_pinned_vectors(self):
        for name, slug in VECTORS:
            with self.subTest(name=name):
                self.assertEqual(_common.slugify_brand(name), slug)

    def test_ascii_names_keep_the_slug_they_always_had(self):
        for name, slug in (("Acme Corp", "acme-corp"), ("AT&T", "at-t"), ("  Spaced   Out  ", "spaced-out"),
                           ("a" * 200, "a" * 60)):
            self.assertEqual(_common.slugify_brand(name), slug)

    def test_every_windows_device_name_gets_a_suffix(self):
        for name in ("con", "PRN", "Aux", "nul", "COM1", "lpt9"):
            self.assertEqual(_common.slugify_brand(name), name.lower() + "-brand")

    def test_distinct_non_latin_names_get_distinct_slugs(self):
        names = ["東京ブランド", "大阪商事", "भारत चाय", "चीन चाय", "شركة النور", "Компания Ромашка", "삼성", "บริษัท"]
        slugs = [_common.slugify_brand(n) for n in names]
        self.assertEqual(len(set(slugs)), len(names), slugs)

    def test_the_same_name_in_a_different_unicode_form_is_one_slug(self):
        self.assertEqual(_common.slugify_brand("Café Noir"), _common.slugify_brand("Café Noir"))
        self.assertEqual(_common.slugify_brand("東京ブランド"), _common.slugify_brand("東京ブランド".upper()))

    def test_a_slug_is_always_a_safe_single_component(self):
        for name, _ in VECTORS:
            self.assertTrue(_common.is_single_component(_common.slugify_brand(name)), name)


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.home = Path(self._tmp.name)
        self.ws = self.home / "ws"
        self.env = {**os.environ, "CLAUDE_MARKETING_HOME": str(self.ws), "HOME": str(self.home),
                    "USERPROFILE": str(self.home)}
        for name in ("CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "CLAUDE_PLUGIN_DATA_DIR", "PYTHONUTF8", "PYTHONIOENCODING"):
            self.env.pop(name, None)

    def tracker(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "local-tracker.py"), *args], capture_output=True,
                              env=self.env, timeout=120)
        out = proc.stdout.decode("utf-8", "replace").strip()
        try:
            payload = json.loads(out) if out else {}
        except ValueError:
            payload = {"_unparseable": out, "_stderr": proc.stderr.decode("utf-8", "replace")[-400:]}
        return proc.returncode, payload

    def folders(self):
        return sorted(p.name for p in self.ws.iterdir() if p.is_dir()) if self.ws.is_dir() else []


class TestTwoBrandsTwoFolders(Workspace):

    def test_the_second_non_latin_brand_does_not_see_the_first_ones_rows(self):
        rc, first = self.tracker("--action", "init", "--brand", "東京ブランド")
        self.assertEqual((rc, first.get("status")), (0, "initialized"), first)
        rc, row = self.tracker("--action", "add-row", "--brand", "東京ブランド",
                               "--data", json.dumps({"title": "Tokyo post", "content_type": "article"}))
        self.assertEqual(rc, 0, row)
        rc, second = self.tracker("--action", "init", "--brand", "大阪商事")
        self.assertEqual((rc, second.get("status")), (0, "initialized"), second)
        rc, pending = self.tracker("--action", "get-pending", "--brand", "大阪商事")
        self.assertEqual(rc, 0, pending)
        self.assertEqual(pending.get("pending_count", 0), 0, pending)
        self.assertEqual(len(self.folders()), 2, self.folders())

    def test_a_folder_held_by_another_name_is_refused_by_name_and_left_alone(self):
        held = self.ws / _common.slugify_brand("Acme")
        (held / "tracking").mkdir(parents=True)
        (held / "brand.json").write_text(json.dumps({"brand_name": "Acme!"}), encoding="utf-8")
        before = (held / "brand.json").read_bytes()
        rc, got = self.tracker("--action", "init", "--brand", "Acme?")
        self.assertEqual(rc, 1, got)
        self.assertIn("already belongs to the brand 'Acme!'", got["error"])
        self.assertEqual((held / "brand.json").read_bytes(), before)

    def test_init_labels_the_folder_and_a_second_init_changes_nothing(self):
        rc, first = self.tracker("--action", "init", "--brand", "Acme Corp")
        self.assertEqual(rc, 0, first)
        record = self.ws / "acme-corp" / "brand.json"
        self.assertEqual(json.loads(record.read_text(encoding="utf-8"))["brand_name"], "Acme Corp")
        tracking = self.ws / "acme-corp" / "tracking" / "tracking.json"
        before = (record.read_bytes(), tracking.read_bytes())
        rc, again = self.tracker("--action", "init", "--brand", "ACME CORP")  # same brand, other case
        self.assertEqual((rc, again.get("status")), (0, "already_initialized"), again)
        self.assertEqual((record.read_bytes(), tracking.read_bytes()), before)


class TestFoldersMadeUnderTheOldSlug(Workspace):

    def setUp(self):
        super().setUp()
        os.environ["CLAUDE_MARKETING_HOME"] = str(self.ws)
        self.addCleanup(os.environ.pop, "CLAUDE_MARKETING_HOME", None)

    def test_a_labelled_old_folder_is_found_for_the_brand_it_names(self):
        old = self.ws / "caf"
        old.mkdir(parents=True)
        (old / "brand.json").write_text(json.dumps({"brand_name": "Café"}), encoding="utf-8")
        self.assertEqual(_common.brand_dir("Café"), old)
        self.assertEqual(_common.brand_dir("CAFÉ"), old)
        self.assertEqual(_common.brand_dir("Café Noir"), self.ws / "cafe-noir")

    def test_a_labelled_old_folder_is_not_taken_by_a_different_brand(self):
        old = self.ws / "caf"
        old.mkdir(parents=True)
        (old / "brand.json").write_text(json.dumps({"brand_name": "Caf"}), encoding="utf-8")
        self.assertEqual(_common.brand_dir("Café"), self.ws / "cafe")

    def test_an_unlabelled_old_folder_under_an_accent_stripped_slug_is_still_reachable(self):
        old = self.ws / "caf"
        old.mkdir(parents=True)
        self.assertEqual(_common.brand_dir("Café"), old)

    def test_the_old_catch_all_folder_is_never_assumed_to_be_one_brands(self):
        (self.ws / "brand").mkdir(parents=True)
        self.assertEqual(_common.brand_dir("東京ブランド"), self.ws / "brand-fa1e53")

    def test_a_new_folder_wins_once_it_exists(self):
        (self.ws / "caf").mkdir(parents=True)
        (self.ws / "cafe").mkdir(parents=True)
        self.assertEqual(_common.brand_dir("Café"), self.ws / "cafe")


if __name__ == "__main__":
    unittest.main()
