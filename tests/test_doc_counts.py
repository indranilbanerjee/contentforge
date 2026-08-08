"""Live documentation must not advertise stale skill / agent / command counts.

The repo grows faster than the prose describing it. Between v3.8.0 and v3.19.2 the
plugin went 19 -> 22 skills and 7 -> 9 commands while TESTING-GUIDE.md, SUBMISSION.md
and COWORK-GUIDE.md kept quoting the old numbers — so the testing checklist told a
reviewer to expect 19 skills and "fail" a correct install. Counts are derived from the
filesystem here, so the only way to satisfy this test is to fix the prose.

Deliberately NOT flagged:
  - CHANGELOG.md and any file banner-marked HISTORICAL DOCUMENT
  - lines carrying a bold dated version tag ("**v3.9 rebuilt ..."), which narrate a past
    release truthfully and must keep their ship-time numbers
  - ranges and thresholds ("3-5 skills", "<5 agents")
  - sentences about a sibling plugin, which has its own counts
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# "22 skills" but not "3-5 skills", "<5 agents", "v3.19.2 skills"
COUNT_RE = re.compile(r"(?<![-<>~\d])\b(\d{1,3})\s+(skills|agents|commands)\b")
DATED_LINE = re.compile(r"\*\*v\d+\.\d+")
HISTORICAL_BANNER = "HISTORICAL DOCUMENT"
SIBLINGS = ("digital-marketing-pro", "digital marketing pro", "socialforge", "social forge")


def ground_truth():
    return {
        "skills": len([d for d in (REPO / "skills").iterdir() if d.is_dir()]),
        "agents": len(list((REPO / "agents").glob("*.md"))),
        "commands": len(list((REPO / "commands").glob("*.md"))),
    }


def live_docs():
    for f in sorted(REPO.rglob("*.md")):
        if any(p in f.parts for p in (".git", "node_modules", ".pytest_cache")):
            continue
        if f.name == "CHANGELOG.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if HISTORICAL_BANNER in text[:800]:
            continue
        yield f, text


class TestLiveDocCounts(unittest.TestCase):
    def test_no_stale_counts_in_live_docs(self):
        truth = ground_truth()
        stale = []
        for f, text in live_docs():
            in_history = False
            for i, line in enumerate(text.splitlines(), 1):
                # A "## " heading ends any run of historical release entries.
                if line.startswith("## "):
                    in_history = False
                # A bold dated version tag opens one, and everything after it in this
                # section narrates past releases: the entry's body keeps its ship-time
                # numbers even though the tag sits on an earlier line.
                if DATED_LINE.search(line):
                    in_history = True
                    continue
                if in_history:
                    continue
                low = line.lower()
                if any(s in low for s in SIBLINGS):
                    continue
                for m in COUNT_RE.finditer(line):
                    n, noun = int(m.group(1)), m.group(2)
                    if n != truth[noun]:
                        stale.append(
                            "%s:%d says '%s' but the repo has %d %s"
                            % (f.relative_to(REPO).as_posix(), i, m.group(0), truth[noun], noun))
        self.assertEqual(stale, [], "Stale counts in live docs:\n  " + "\n  ".join(stale))

    def test_ground_truth_is_sane(self):
        """A miscounted truth would make the guard above vacuous."""
        truth = ground_truth()
        self.assertGreater(truth["skills"], 0)
        self.assertGreater(truth["agents"], 0)
        self.assertGreater(truth["commands"], 0)


if __name__ == "__main__":
    unittest.main()
