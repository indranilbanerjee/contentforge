"""local-tracker.py mark-complete must always publish a named, non-colliding file.

add_row always writes a "title" key (defaulting to ""), so the old
`slugify(target.get("title", row_id))` fallback could never fire. An untitled
record slugified to "" and published the deliverable as a bare ".md" — a hidden
dotfile on macOS/Linux — and every subsequent untitled record overwrote it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SCRIPT = TESTS_DIR.parent / "scripts" / "local-tracker.py"


class TestPublishFilenames(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.home = Path(self._tmp.name)
        self.publish = self.home / "publish"
        self.env = os.environ.copy()
        self.env["CLAUDE_MARKETING_HOME"] = str(self.home)
        self.env["PYTHONIOENCODING"] = "utf-8"
        self.draft = self.home / "draft.md"
        self.draft.write_text("# Draft\n\nBody.\n", encoding="utf-8")
        self.run_lt("--action", "init", "--brand", "Acme")

    def tearDown(self):
        self._tmp.cleanup()

    def run_lt(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, env=self.env)
        out = proc.stdout.decode("utf-8", errors="replace").strip()
        try:
            payload = json.loads(out) if out else {}
        except json.JSONDecodeError:
            payload = {"_stdout": out,
                       "_stderr": proc.stderr.decode("utf-8", errors="replace")}
        return proc.returncode, payload

    def _complete(self, req_id, data):
        self.run_lt("--action", "add-row", "--brand", "Acme", "--data", json.dumps(data))
        rc, payload = self.run_lt("--action", "mark-complete", "--brand", "Acme",
                                  "--row-id", req_id, "--output-file", str(self.draft),
                                  "--publish-dir", str(self.publish))
        self.assertEqual(rc, 0, payload)
        self.assertNotIn("error", payload, payload)
        return payload

    def test_untitled_record_does_not_publish_a_dotfile(self):
        payload = self._complete("REQ-001", {"requirement_id": "REQ-001",
                                             "content_type": "article"})
        published = Path(payload["published_path"])
        self.assertNotEqual(published.name, ".md",
                            "an untitled record published a hidden dotfile")
        self.assertFalse(published.name.startswith("."),
                         f"published file is hidden: {published.name}")
        self.assertIn("req-001", published.name.lower())
        self.assertTrue(published.exists())

    def test_untitled_records_do_not_overwrite_each_other(self):
        first = self._complete("REQ-001", {"requirement_id": "REQ-001",
                                           "content_type": "article"})
        second = self._complete("REQ-002", {"requirement_id": "REQ-002",
                                            "content_type": "article"})
        self.assertNotEqual(first["published_path"], second["published_path"],
                            "two untitled records collided on one filename")
        self.assertNotEqual(first["output_path"], second["output_path"],
                            "two untitled records collided in the tracking copy")
        self.assertTrue(Path(first["published_path"]).exists())
        self.assertTrue(Path(second["published_path"]).exists())

    def test_titled_record_still_uses_its_title(self):
        payload = self._complete("REQ-003", {"requirement_id": "REQ-003",
                                             "title": "Email Deliverability in 2026",
                                             "content_type": "article"})
        self.assertIn("email-deliverability-in-2026",
                      Path(payload["published_path"]).name)

    def test_title_of_only_punctuation_falls_back_to_req_id(self):
        payload = self._complete("REQ-004", {"requirement_id": "REQ-004",
                                             "title": "!!! ??? ***",
                                             "content_type": "article"})
        name = Path(payload["published_path"]).name
        self.assertFalse(name.startswith("."), f"published file is hidden: {name}")
        self.assertIn("req-004", name.lower())


if __name__ == "__main__":
    unittest.main()
