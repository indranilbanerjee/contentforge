"""4.5.8: the always-on listing cost, the Instagram hashtag cap, the Python floor warning and the one-command install.

`claude plugin details contentforge` measured ~2,112 tokens added to every session; Anthropic's directory highlights an "every turn" cost of
2,000 or more. Two agent descriptions (268 and 216 characters) accounted for most of the excess, and the rest were wordier than routing needs.
They are now 60-150 characters and the measure is ~1,958. The real measure needs the CLI, so this file pins a character proxy that stops the
agent descriptions growing back, plus the other 4.5.8 facts.
"""
from __future__ import annotations

import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402

AGENT_CHAR_BUDGET = 1300      # the 13 descriptions total ~1,110 today; the proxy leaves room for wording, not for a 268-character one


def agent_descriptions():
    out = {}
    for p in sorted((ROOT / "agents").glob("*.md")):
        m = re.search(r'(?m)^description:\s*(.*)$', p.read_text(encoding="utf-8"))
        out[p.name] = m.group(1).strip().strip('"') if m else ""
    return out


class TestAgentDescriptionsStayInTheBudget(unittest.TestCase):
    def test_every_agent_description_is_60_to_150_characters(self):
        descriptions = agent_descriptions()
        self.assertEqual(len(descriptions), 13)
        for name, text in descriptions.items():
            with self.subTest(agent=name):
                self.assertTrue(60 <= len(text) <= 150, "%s is %d characters; the rule is 60-150" % (name, len(text)))

    def test_all_agent_descriptions_together_stay_under_the_character_proxy(self):
        self.assertLessEqual(sum(len(t) for t in agent_descriptions().values()), AGENT_CHAR_BUDGET)

    def test_plant_the_4_5_7_descriptions_would_fail_both_checks(self):
        old = [137, 113, 115, 268, 216, 113, 135, 108, 104, 90, 109, 71, 85]      # lengths read from the 4.5.7 files
        self.assertEqual([n for n in old if not 60 <= n <= 150], [268, 216])
        self.assertGreater(sum(old), AGENT_CHAR_BUDGET)


class TestInstagramHashtagCap(unittest.TestCase):
    """Instagram's verified @creators account announced on Threads on 2025-12-18: "Starting today, Instagram will allow up to 5 hashtags in a
    reel or post". ContentForge's spec said 8-12 and Instagram would not accept them."""

    @staticmethod
    def problems(tags):
        out = []
        if tags["count_max"] > 5:
            out.append("count_max %d is over Instagram's cap of 5" % tags["count_max"])
        if sum(tags.get("tier_mix", {}).values()) > tags["count_max"]:
            out.append("tier_mix adds up to more than count_max")
        if tags["count_min"] > tags["count_max"]:
            out.append("count_min is above count_max")
        return out

    def test_the_shipped_spec_respects_the_cap_and_names_its_source(self):
        spec = json.loads((ROOT / "config" / "social-platform-specs.json").read_text(encoding="utf-8-sig"))
        tags = spec["instagram"]["hashtags"]
        self.assertEqual(self.problems(tags), [])
        self.assertIn("@creators", tags["notes"])
        self.assertIn("2025-12-18", tags["notes"])

    def test_plant_the_4_5_7_spec_is_flagged(self):
        old = {"count_min": 8, "count_max": 12, "tier_mix": {"broad": 2, "specific": 4, "niche": 4, "branded": 2}}
        self.assertEqual(len(self.problems(old)), 1)
        self.assertTrue(self.problems(dict(old, count_max=5)))


class TestPythonFloorWarning(unittest.TestCase):
    def test_python_3_10_is_warned_and_3_11_is_not(self):
        warning = _common.python_floor_warning((3, 10, 12))
        self.assertIn("3.11", warning)
        self.assertIn("end of life", warning)
        self.assertIsNone(_common.python_floor_warning((3, 11, 0)))
        self.assertIsNone(_common.python_floor_warning((3, 13, 1)))

    def test_setup_prints_the_warning_line(self):
        import setup as cf_setup
        out = io.StringIO()
        with mock.patch.object(_common, "python_floor_warning", return_value="WARN-TEXT"), mock.patch("sys.stdout", out):
            with self.assertRaises(SystemExit):
                cf_setup.main()
        self.assertIn("PYTHON_WARNING=WARN-TEXT", out.getvalue())
        out = io.StringIO()
        with mock.patch.object(_common, "python_floor_warning", return_value=None), mock.patch("sys.stdout", out):
            with self.assertRaises(SystemExit):
                cf_setup.main()
        self.assertNotIn("PYTHON_WARNING", out.getvalue())


class TestOneCommandInstall(unittest.TestCase):
    LINE = "claude plugin install contentforge --marketplace indranilbanerjee/neels-plugins"

    def test_the_readme_and_user_guide_show_it_and_keep_the_two_step_route(self):
        for rel in ("README.md", "docs/USER-GUIDE.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertIn(self.LINE, text)
                self.assertIn("claude plugin marketplace add indranilbanerjee/neels-plugins" if rel.startswith("docs") else "/plugin marketplace add indranilbanerjee/neels-plugins", text)


class TestNoPromisedPythonFloor(unittest.TestCase):
    """Claude's Cowork environment ran Python 3.10.12 when last checked, so promising "3.11 from the next minor release" would break every
    Cowork user. The wording is conditional everywhere: the plugin moves to 3.11 once Cowork does, and no release is named."""
    PROMISE = re.compile(r"(?is)(?:will\s+(?:be\s+)?requires?d?|requires?d?)[^.]{0,60}\b3\.11\b[^.]{0,60}\bnext\s+(?:minor|release)"
                         r"|\b3\.11\b[^.]{0,60}\bfrom\s+the\s+next\s+(?:minor|release)")

    def test_no_shipped_text_promises_python_3_11_from_a_release(self):
        skip_dirs = {".git", "node_modules", ".pytest_cache", "tests", "research", "heroes", ".superpowers"}
        scanned, bad = 0, []
        for path in ROOT.rglob("*"):
            if not path.is_file() or skip_dirs & set(path.relative_to(ROOT).parts):
                continue
            if path.suffix.lower() not in {".md", ".py", ".json", ".yml", ".yaml", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            if self.PROMISE.search(text):
                bad.append(path.relative_to(ROOT).as_posix())
        self.assertGreater(scanned, 100, "the scan saw too few files; the guard is vacuous")
        self.assertEqual(bad, [])

    def test_plant_the_old_wordings_are_caught_and_the_conditional_one_is_not(self):
        for old in ("ContentForge will require Python 3.11 from the next minor release.",
                    "ContentForge will require Python 3.11 or newer from the next minor release: install a newer Python.",
                    "Scripts require Python 3.10+ today (3.11 will be required from the next minor release, and setup warns on 3.10)",
                    "(3.11 from the next minor release; setup warns on 3.10)",
                    "will require\n  Python 3.11 from the next release"):
            with self.subTest(old=old):
                self.assertTrue(self.PROMISE.search(old), old)
        new = ("Python 3.10 reached end of life on 2026-10-01. ContentForge still runs on it, and will move to 3.11 once Claude's Cowork "
               "environment does (it ran 3.10.12 when last checked). Use 3.11 or newer where you can.")
        self.assertFalse(self.PROMISE.search(new))

    def test_the_warning_is_conditional_and_names_cowork(self):
        import _common
        warning = _common.python_floor_warning((3, 10, 12))
        self.assertIn("once Claude's Cowork environment does", warning)
        self.assertIn("3.10.12", warning)
        self.assertNotIn("next minor", warning)


if __name__ == "__main__":
    unittest.main()
