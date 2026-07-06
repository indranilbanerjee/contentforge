"""generate-docx.py parser tests (pure functions — no python-docx needed),
plus an optional end-to-end render test when python-docx is installed."""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

spec = importlib.util.spec_from_file_location("cf_generate_docx", SCRIPTS_DIR / "generate-docx.py")
gd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gd)

try:
    import docx  # noqa: F401
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# 1x1 red pixel PNG
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


class TestParseBlocks(unittest.TestCase):
    def _kinds(self, md):
        return [k for k, _ in gd.parse_markdown_to_blocks(md)]

    def test_frontmatter_stripped(self):
        md = "---\ntitle: X\n---\n# Real Title\n\nBody."
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertEqual(blocks[0], ("h1", "Real Title"))

    def test_table_block(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertEqual(blocks[0][0], "table")
        self.assertEqual(len(blocks[0][1]), 3)

    def test_nested_bullets_carry_levels(self):
        md = "- top\n  - child\n    - grandchild\n- top2"
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertEqual(blocks[0][0], "bullet")
        self.assertEqual(blocks[0][1],
                         [(0, "top"), (1, "child"), (2, "grandchild"), (0, "top2")])

    def test_plus_bullets_supported(self):
        blocks = gd.parse_markdown_to_blocks("+ one\n+ two")
        self.assertEqual(blocks[0][0], "bullet")
        self.assertEqual(len(blocks[0][1]), 2)

    def test_ordered_with_paren_and_nesting(self):
        md = "1. first\n2) second\n   1. sub"
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertEqual(blocks[0][0], "ordered")
        levels = [lvl for lvl, _ in blocks[0][1]]
        self.assertEqual(levels, [0, 0, 1])

    def test_indented_bullet_not_absorbed_into_paragraph(self):
        md = "Intro paragraph line.\n  - indented item\n  - second item"
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertEqual(blocks[0], ("para", "Intro paragraph line."))
        self.assertEqual(blocks[1][0], "bullet")

    def test_image_block(self):
        blocks = gd.parse_markdown_to_blocks("![Chart 1: growth](assets/chart1.png)")
        self.assertEqual(blocks[0], ("image", ("Chart 1: growth", "assets/chart1.png")))

    def test_hr_variants(self):
        for hr in ("---", "***", "___", "- - -"):
            kinds = self._kinds(f"para\n\n{hr}\n\npara2")
            self.assertIn("hr", kinds, f"{hr!r} should parse as hr")

    def test_code_fence(self):
        blocks = gd.parse_markdown_to_blocks("```python\nx = 1\n```")
        self.assertEqual(blocks[0], ("code", "x = 1"))

    def test_completion_card_stripped(self):
        md = "# T\n\nBody.\n\n## CONTENTFORGE — COMPLETION CARD\n\nsecret"
        blocks = gd.parse_markdown_to_blocks(md)
        self.assertNotIn("secret", json.dumps(blocks))


class TestInlinePattern(unittest.TestCase):
    def _first_match_groups(self, text):
        m = gd.INLINE_PATTERN.search(text)
        return m.groups() if m else None

    def test_underscore_bold(self):
        groups = self._first_match_groups("__bold text__")
        self.assertEqual(groups[5], "bold text")

    def test_underscore_italic(self):
        groups = self._first_match_groups("an _italic_ word")
        self.assertEqual(groups[7], "italic")

    def test_snake_case_not_italicized(self):
        self.assertIsNone(gd.INLINE_PATTERN.search("use snake_case_name here"))

    def test_triple_star_bold_italic(self):
        groups = self._first_match_groups("***both***")
        self.assertEqual(groups[2], "both")

    def test_inline_image_captured(self):
        groups = self._first_match_groups("see ![alt](img.png) inline")
        self.assertEqual(groups[0], "alt")
        self.assertEqual(groups[1], "img.png")

    def test_link_still_captured(self):
        groups = self._first_match_groups("[Anthropic](https://anthropic.com)")
        self.assertEqual(groups[9], "Anthropic")
        self.assertEqual(groups[10], "https://anthropic.com")


class TestInternalLinkMarkers(unittest.TestCase):
    MARKER = ('Before <!-- INTERNAL-LINK: type=commercial | anchor="ENHERTU" | '
              'url=https://x.example/p | priority=1 | reason="product" | section=Intro --> after')

    def test_split_produces_link_segment(self):
        segments = gd.split_text_with_links(self.MARKER)
        kinds = [k for k, _ in segments]
        self.assertEqual(kinds, ["text", "link", "text"])
        link = segments[1][1]
        self.assertEqual(link["anchor"], "ENHERTU")
        self.assertFalse(link["placeholder"])

    def test_tbd_url_is_placeholder(self):
        text = '<!-- INTERNAL-LINK: type=topical | anchor="anchor text" | url=TBD -->'
        link = gd.split_text_with_links(text)[0][1]
        self.assertTrue(link["placeholder"])


@unittest.skipUnless(HAS_DOCX, "python-docx not installed")
class TestEndToEndRender(unittest.TestCase):
    def test_render_with_image_toc_footer(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "chart.png").write_bytes(TINY_PNG)
            md = (
                "# Render Test Title\n\n"
                "Intro paragraph with **bold**, __also bold__, _italic_, and `code`.\n\n"
                "![Chart caption](" + (tmpdir / "chart.png").as_posix() + ")\n\n"
                "![missing image](" + (tmpdir / "nope.png").as_posix() + ")\n\n"
                "## Section\n\n- top\n  - nested\n\n"
                "| A | B |\n|---|---|\n| 1 | 2 |\n"
            )
            content = tmpdir / "article.md"
            content.write_text(md, encoding="utf-8")
            out = tmpdir / "out.docx"

            env = os.environ.copy()
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "generate-docx.py"),
                 "--content", str(content), "--output", str(out),
                 "--brand", "TestBrand", "--content-type", "article"],
                capture_output=True, env=env,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout.decode("utf-8", "replace")
                             + proc.stderr.decode("utf-8", "replace"))
            payload = json.loads(proc.stdout.decode("utf-8", "replace"))
            self.assertEqual(payload["status"], "success")
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 2000)

            with zipfile.ZipFile(out) as z:
                document_xml = z.read("word/document.xml").decode("utf-8")
                footer_names = [n for n in z.namelist() if n.startswith("word/footer")]
            self.assertIn("TOC", document_xml)          # TOC field present
            self.assertIn("Render Test Title", document_xml)
            self.assertIn("Image not found", document_xml)  # missing-image placeholder
            self.assertTrue(footer_names, "expected a footer part for Page X of Y")


if __name__ == "__main__":
    unittest.main()
