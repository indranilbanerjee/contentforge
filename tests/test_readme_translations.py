"""Guards for the 11 README translations (v4.1.1).

The contract: every translation is a real, curated document that names the
English README as source of truth and carries a "Synced with English README
vX.Y.Z" stamp. The stamp must equal the CURRENT canonical version — when a
release changes the English README, the translations must be consciously
re-synced (or consciously re-stamped after verifying nothing user-facing
changed). A translation that silently falls behind the shipping version is
the same defect as a stale count, and it fails the suite the same way.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TRANSLATIONS = [
    "README.hi.md", "README.zh-CN.md", "README.ja.md", "README.ko.md",
    "README.es.md", "README.pt-BR.md", "README.ar.md", "README.ur.md",
    "README.ta.md", "README.bn.md", "README.ru.md",
]

# A stub or truncated upload is not a translation. The smallest real file
# (Urdu, dense script) ships at ~18 KB; half that is a generous floor.
MIN_BYTES = 9_000


def _canonical() -> str:
    data = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    return data["version"]


def _switcher_line() -> str:
    """The 🌐 line in the English README is the canonical switcher."""
    for line in (REPO / "README.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("🌐"):
            return line.strip()
    raise AssertionError("English README lost its 🌐 language-switcher line")


def _has_stamp(text: str, version: str) -> bool:
    """True iff the text carries the literal current-version token."""
    return f"v{version}" in text


class TestTranslationFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = _canonical()
        cls.switcher = _switcher_line()

    def test_every_translation_exists_and_is_substantial(self):
        for name in TRANSLATIONS:
            p = REPO / name
            with self.subTest(file=name):
                self.assertTrue(p.exists(), f"{name} is missing")
                size = p.stat().st_size
                self.assertGreaterEqual(
                    size, MIN_BYTES,
                    f"{name} is {size} bytes — a stub, not a translation")

    def test_switcher_line_is_byte_identical_everywhere(self):
        for name in TRANSLATIONS:
            text = (REPO / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                self.assertIn(self.switcher, text,
                              f"{name} does not carry the English README's "
                              "🌐 switcher line byte-identically")

    def test_sync_stamp_matches_canonical_version(self):
        for name in TRANSLATIONS:
            text = (REPO / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                self.assertTrue(
                    _has_stamp(text, self.canonical),
                    f"{name} is not stamped v{self.canonical} — the plugin "
                    "shipped a release this translation was never synced "
                    "against. Re-sync the translation (or re-stamp it after "
                    "verifying nothing user-facing changed).")

    def test_every_translation_links_back_to_english(self):
        for name in TRANSLATIONS:
            text = (REPO / name).read_text(encoding="utf-8")
            with self.subTest(file=name):
                self.assertIn("(README.md)", text,
                              f"{name} lost its source-of-truth link to the "
                              "English README")

    def test_english_readme_names_every_translation(self):
        text = (REPO / "README.md").read_text(encoding="utf-8")
        for name in TRANSLATIONS:
            with self.subTest(file=name):
                self.assertIn(f"({name})", text,
                              f"English README's switcher does not link {name}")

    def test_guard_can_fail(self):
        """Plant-check: the stamp check must actually reject a stale stamp."""
        self.assertTrue(_has_stamp("Synced with English README v4.1.1.", "4.1.1"))
        self.assertFalse(_has_stamp("Synced with English README v4.1.0.", "4.1.1"))
        self.assertFalse(_has_stamp("no stamp here at all", "4.1.1"))


if __name__ == "__main__":
    unittest.main()
