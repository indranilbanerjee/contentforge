"""The feature card never draws empty boxes where a script's letters should be, and its libraries are pinned.

Found in 4.5.12 by the installed-copy journeys: a card with a Devanagari title was drawn in matplotlib's default sans-serif, which has
no Devanagari glyphs, so the PNG showed empty boxes and the script reported success. The card now looks for an installed font that
covers every character of its text (and keeps the default font whenever that covers it), and refuses with a clear message, drawing
nothing, when no font does. matplotlib and pillow were also missing from PINNED_DEPENDENCIES, so the dependency error carried no
install command.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402

spec = importlib.util.spec_from_file_location("_cf_feature_card_fonts", SCRIPTS / "feature_card.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)

HAVE_LIBRARIES = not fc._missing_libraries()
HINDI = "भारत में AI का भविष्य"


class TestPickFont(unittest.TestCase):

    def test_the_first_family_that_covers_the_text_wins(self):
        installed = [("DejaVu Sans", "a.ttf"), ("Nirmala UI", "b.ttf"), ("Mangal", "c.ttf")]
        covers = lambda path, text: path in ("b.ttf", "c.ttf")  # noqa: E731
        self.assertEqual(fc.pick_font(HINDI, installed, covers), "Nirmala UI")

    def test_a_family_outside_the_preferred_list_is_used_when_nothing_preferred_covers(self):
        installed = [("DejaVu Sans", "a.ttf"), ("Zz Devanagari Display", "z.ttf")]
        covers = lambda path, text: path == "z.ttf"  # noqa: E731
        self.assertEqual(fc.pick_font(HINDI, installed, covers), "Zz Devanagari Display")

    def test_no_covering_font_gives_none(self):
        self.assertIsNone(fc.pick_font(HINDI, [("DejaVu Sans", "a.ttf")], lambda path, text: False))
        self.assertIsNone(fc.pick_font(HINDI, [], lambda path, text: True))


@unittest.skipUnless(HAVE_LIBRARIES, "matplotlib and pillow are not installed here")
class TestRender(unittest.TestCase):

    def render(self, title, out):
        return fc.render(title, "Example Archive", "#0B6E4F", "#DDA15E", Path(out))

    def test_a_latin_title_keeps_the_default_font(self):
        self.assertEqual(fc._card_family("Plain Latin title — with a dash"), "sans-serif")

    def test_a_title_no_installed_font_can_draw_is_refused_and_nothing_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "card.png"
            real_default, real_pick = fc._covers, fc.pick_font
            fc._covers = lambda path, text: False      # even the default font has no glyph
            fc.pick_font = lambda text, installed=None, covers=None: None
            try:
                result = self.render(HINDI, out)
            finally:
                fc._covers, fc.pick_font = real_default, real_pick
            self.assertEqual(result["status"], "FAILED")
            self.assertEqual(result["stage"], "fonts")
            self.assertIn("Nothing was drawn or written", result["error"])
            self.assertFalse(out.exists())

    def test_a_devanagari_title_is_drawn_when_a_covering_font_is_installed(self):
        family = fc._card_family(HINDI)
        if family is None:
            self.skipTest("no installed font covers Devanagari on this machine; the refusal test covers it")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "card.png"
            result = self.render(HINDI, out)
            self.assertEqual(result["status"], "generated", result)
            self.assertTrue(out.is_file())


class TestPinned(unittest.TestCase):

    def test_the_drawing_libraries_have_pins_and_the_message_carries_the_command(self):
        for name in ("matplotlib", "pillow"):
            self.assertIn(name, _common.PINNED_DEPENDENCIES)
        command = _common.install_command(["matplotlib", "pillow"])
        self.assertIn("matplotlib==", command)
        self.assertIn("pillow==", command)
        original = fc._missing_libraries
        fc._missing_libraries = lambda: ["matplotlib"]
        try:
            result = fc.render("t", "b", "#112233", "#445566", Path("unused.png"))
        finally:
            fc._missing_libraries = original
        self.assertEqual(result["stage"], "dependencies")
        self.assertIn("pip install", result["error"])
        self.assertIn("matplotlib==", result["error"])


if __name__ == "__main__":
    unittest.main()
