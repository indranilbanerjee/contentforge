"""Every script prints UTF-8, whatever the console's code page.

On Windows a pipe defaults to the ANSI code page (cp1252), so a script that prints a brand name, a topic or a model note outside it
(Devanagari, Japanese, an arrow, an emoji) ends in UnicodeEncodeError and a traceback. Digital Marketing Pro's audit found it in the
status and setup scripts; ContentForge's own audit found five scripts, plus two whose --help printed a cp1252 em dash. The guard is
static, as in DMP: a script must call `_common.ensure_utf8_stdout()` or reconfigure its own streams before it prints.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
GUARDED = re.compile(r"ensure_utf8_stdout\s*\(|\.reconfigure\s*\(\s*encoding\s*=\s*[\"']utf-8[\"']")


def unguarded(source: str) -> bool:
    return not GUARDED.search(source)


class TestEveryScriptPrintsUtf8(unittest.TestCase):

    def test_no_script_is_left_on_the_console_code_page(self):
        bare = [p.name for p in sorted(SCRIPTS.glob("*.py")) if unguarded(p.read_text(encoding="utf-8-sig"))]
        self.assertEqual(bare, [], "these scripts neither call ensure_utf8_stdout() nor reconfigure their streams: " + ", ".join(bare))

    def test_plants(self):
        self.assertTrue(unguarded("import json\nprint(json.dumps({'a': 1}))\n"))
        self.assertTrue(unguarded("import sys\nsys.stdout.write('x')\n"))
        self.assertFalse(unguarded("import _common\n_common.ensure_utf8_stdout()\n"))
        self.assertFalse(unguarded("sys.stdout.reconfigure(encoding='utf-8', errors='replace')\n"))
        self.assertFalse(unguarded("    _stream.reconfigure(encoding=\"utf-8\", errors=\"replace\")\n"))

    def test_the_scripts_directory_was_actually_read(self):
        self.assertGreater(len(list(SCRIPTS.glob("*.py"))), 20)


if __name__ == "__main__":
    unittest.main()
