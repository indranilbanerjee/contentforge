"""Skill descriptions must carry enough signal to route on.

For a model-invoked skill, the frontmatter description is the entire routing
layer — the only thing the model reads when deciding whether a skill applies.
Before this guard, 20 of the 22 descriptions were one-liners under 161
characters. The house pattern (proven suite-wide): what the skill does and
produces, then "Triggers on" with the quoted phrases a user would actually
type (slash alias first), then what it reads or pairs with.

Stdlib only.
"""
from __future__ import annotations

import re
import statistics
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "skills"

MIN_LENGTH = 300
MAX_LENGTH = 900
MIN_TRIGGER_PHRASES = 4
SLASH_PREFIX = "/contentforge:"

DESC_RE = re.compile(r'^description:\s*"(.*)"\s*$', re.M)
PHRASE_RE = re.compile(r'\\"([^"]+?)\\"')


def description_line(skill_dir: Path) -> str | None:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    m = DESC_RE.search(text)
    return m.group(1) if m else None


def analyze(desc: str) -> dict:
    phrases = PHRASE_RE.findall(desc)
    return {
        "length": len(desc),
        "has_triggers": "Triggers on" in desc,
        "phrases": phrases,
        "has_slash": any(p.startswith(SLASH_PREFIX) for p in phrases),
    }


def all_skills():
    for d in sorted(SKILLS.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            yield d


class TestDescriptionDensity(unittest.TestCase):
    def test_every_description_is_single_line_double_quoted(self):
        bad = [d.name for d in all_skills() if description_line(d) is None]
        self.assertEqual(bad, [],
                         "Skills whose description is not a single-line double-quoted "
                         "string:\n  " + "\n  ".join(bad))

    def test_every_description_meets_the_floor(self):
        failures = []
        for d in all_skills():
            desc = description_line(d)
            if desc is None:
                continue
            a = analyze(desc)
            problems = []
            if a["length"] < MIN_LENGTH:
                problems.append(f"{a['length']} chars < {MIN_LENGTH}")
            if a["length"] > MAX_LENGTH:
                problems.append(f"{a['length']} chars > {MAX_LENGTH}")
            if not a["has_triggers"]:
                problems.append("no 'Triggers on'")
            if len(a["phrases"]) < MIN_TRIGGER_PHRASES:
                problems.append(f"{len(a['phrases'])} quoted trigger phrases < {MIN_TRIGGER_PHRASES}")
            if not a["has_slash"]:
                problems.append(f"no quoted {SLASH_PREFIX}<name> alias")
            if problems:
                failures.append(f"{d.name}: " + "; ".join(problems))
        self.assertEqual(failures, [],
                         "Descriptions below the routing floor:\n  " + "\n  ".join(failures))

    def test_median_stays_dense(self):
        lengths = [len(description_line(d) or "") for d in all_skills()]
        self.assertGreaterEqual(statistics.median(lengths), 350,
                                f"median description length {statistics.median(lengths)} — "
                                "the routing layer is thinning out")

    # ── plant checks ────────────────────────────────────────────────

    def test_analyzer_accepts_the_house_pattern(self):
        good = ('Does a real thing and produces a real artifact. '
                'Triggers on \\"/contentforge:example\\", \\"do the thing\\", '
                '\\"why is it broken\\", \\"make a thing plan\\". '
                'Reads the brand profile; pairs with /contentforge:cf-brief.')
        a = analyze(good)
        self.assertTrue(a["has_triggers"] and a["has_slash"])
        self.assertGreaterEqual(len(a["phrases"]), 4)

    def test_analyzer_rejects_a_one_liner(self):
        a = analyze("Audit existing content for issues")
        self.assertFalse(a["has_triggers"])
        self.assertEqual(a["phrases"], [])


if __name__ == "__main__":
    unittest.main()
