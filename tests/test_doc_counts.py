"""Live documentation must not advertise stale skill / agent / command / script counts.

The repo grows faster than the prose describing it. Between v3.8.0 and v3.19.2 the
plugin went 19 -> 22 skills and 7 -> 9 commands while TESTING-GUIDE.md, SUBMISSION.md
and COWORK-GUIDE.md kept quoting the old numbers — so the testing checklist told a
reviewer to expect 19 skills and "fail" a correct install. Counts are derived from the
filesystem here, so the only way to satisfy this test is to fix the prose.

The 2026-08-16 documentation audit found the original guard was pattern-blind: "All 21
SKILL.md files", "all 21 ContentForge skills" and "8 scripts" all rotted in live docs
while the guard passed, because the number was not directly followed by one of its three
nouns. The guard now also covers scripts, "N SKILL.md files", "N ContentForge skills",
and comparison-table "Skills count" rows — and AGENTS.md (auto-loaded by every
non-Claude runtime) must carry the current release version on its surfaces line.

Deliberately NOT flagged:
  - CHANGELOG.md, research/ (dated internal design docs), and any file banner-marked
    HISTORICAL DOCUMENT
  - lines carrying a bold dated version tag ("**v3.9 rebuilt ..."), which narrate a past
    release truthfully and must keep their ship-time numbers
  - sections whose heading names a release ("### Release v1.2.0", "## What's new ... v3.1"),
    for the same reason
  - ranges and thresholds ("3-5 skills", "<5 agents", "~86 scripts")
  - sentences about a sibling plugin, which has its own counts
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# "22 skills" / "25 Python scripts" but not "3-5 skills", "<5 agents", "v3.19.2 skills"
# 2026-10-04: one optional qualifier let "18 top-level commands" and "24 specialist
# agents" escape in a sibling plugin after a command fold; qualifiers now chain.
# 2026-10-10 (Hermes docs sweep): the pattern above could not see "16 Agent Skills", "25 Claude
# Code slash commands", "22 Python helpers", "10 opt-in HTTP MCP connectors", the heading
# "All 25 Commands" (capital C) or "the 10-connector catalog" (hyphen), and AGENTS.md carried
# all of them, 3 to 10 releases stale. Nouns are now case-insensitive, singular or plural, the
# separator may be a hyphen, and the qualifier list covers those phrasings. A '#' before the
# number is a markdown anchor (#14-commands), not a claim.
COUNT_RE = re.compile(
    r"(?<![-<>~#\d])\b([1-9]\d{0,2})\s+"
    r"(?:(?:Python|top-level|slash|specialist|Claude\s+Code|opt-in|HTTP|MCP|executable)\s+)*"
    r"(?:Agent\s+(?=skills))?"
    r"(skills|agents|commands|scripts|helpers|connectors)\b", re.I)
# "the 10-connector catalog" — the singular only counts in this hyphenated form ("a 3-agent
# workflow" and "0 connectors configured" are not inventory claims).
HYPHEN_RE = re.compile(r"(?<![-<>~#\d])\b([1-9]\d{0,2})-connector catalog", re.I)
NOUNS = {"skills": "skills", "agents": "agents", "commands": "commands", "scripts": "scripts",
         "helpers": "scripts", "connectors": "connectors"}
# "passes | 55 tests" — a suite size, counted only when the line carries a suite marker
# (in a marketing repo "tests" also means A/B tests).
TESTS_RE = re.compile(r"(?<![-<>~\d])\b(\d{2,4})\s+(?:stdlib-unittest\s+|unit\s+)?tests\b", re.I)
TEST_MARKER = re.compile(r"\b(?:passes|passing|test suite|unittest|run_all|pytest)\b", re.I)
# "All 21 SKILL.md files" — the phrasing the original guard could not see
SKILL_MD_RE = re.compile(r"(?<![-<>~\d])\b(\d{1,3})\s+SKILL\.md files?\b")
# "all 21 ContentForge skills" — plugin name between number and noun
NAMED_SKILLS_RE = re.compile(r"(?<![-<>~\d])\b(\d{1,3})\s+ContentForge skills\b", re.I)
# "| Skills count | **158** |" — comparison-table row form
TABLE_ROW_RE = re.compile(r"Skills count\s*\|\s*\*\*(\d{1,3})\*\*")
DATED_LINE = re.compile(r"\*\*v\d+\.\d+")
# A heading that narrates a release keeps its ship-time numbers.
RELEASE_HEADING = re.compile(r"^#{1,6}\s.*\bv\d+\.\d+.*", re.I)
RELEASE_HEADING_WORDS = ("release", "earlier", "previous", "what's new", "whats-new",
                         "shipped", "upgrad", "history", "changelog")
HISTORICAL_BANNER = "HISTORICAL DOCUMENT"
SIBLINGS = ("digital-marketing-pro", "digital marketing pro", "socialforge", "social forge")


def ground_truth():
    return {
        "skills": len([d for d in (REPO / "skills").iterdir() if d.is_dir()]),
        "agents": len(list((REPO / "agents").glob("*.md"))),
        "commands": len(list((REPO / "commands").glob("*.md"))),
        "scripts": len(list((REPO / "scripts").glob("*.py"))),
        "connectors": _catalog_connectors(),
        "tests": _badge_tests(),
    }


def _badge_tests():
    """The suite size the README badge states (release_consistency keeps it honest)."""
    m = re.search(r"badge/tests-(\d+)%2F(\d+)", (REPO / "README.md").read_text(encoding="utf-8"))
    return int(m.group(2))


def _catalog_connectors():
    """Entries in the opt-in catalog (.mcp.json.connectors-reference), section markers excluded."""
    data = json.loads((REPO / ".mcp.json.connectors-reference").read_text(encoding="utf-8"))
    return len([k for k in data["mcpServers_reference"] if not k.startswith("_")])


def _registry_connectors():
    """Total connectors in scripts/connector-status.py CONNECTOR_REGISTRY (29 across 14 categories)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("cf_connector_status", REPO / "scripts" / "connector-status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return sum(len(v["connectors"]) for v in mod.CONNECTOR_REGISTRY.values())


def extra_ok(noun):
    """Counts that are right under another definition and so are allowed next to the main one:
    the 9 first-party HTTP connectors connector-status.py reports, and the registry total."""
    return {9, _registry_connectors()} if noun == "connectors" else set()


def claims_in(line):
    """Every (number, noun, matched text) count claim on one line."""
    found = [(int(m.group(1)), NOUNS[m.group(2).lower()], m.group(0))
             for m in COUNT_RE.finditer(line)]
    found += [(int(m.group(1)), "skills", m.group(0))
              for pat in (SKILL_MD_RE, NAMED_SKILLS_RE, TABLE_ROW_RE)
              for m in pat.finditer(line)]
    found += [(int(m.group(1)), "connectors", m.group(0)) for m in HYPHEN_RE.finditer(line)]
    if TEST_MARKER.search(line):
        found += [(int(m.group(1)), "tests", m.group(0)) for m in TESTS_RE.finditer(line)]
    return found


def stale_claims(line, truth):
    """The claims on a line that disagree with the repo."""
    return [(n, noun, shown) for n, noun, shown in claims_in(line)
            if n != truth[noun] and n not in extra_ok(noun)]


def live_docs():
    for f in sorted(REPO.rglob("*.md")):
        if any(p in f.parts for p in (".git", "node_modules", ".pytest_cache", "research")):
            continue
        if f.name == "CHANGELOG.md":
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if HISTORICAL_BANNER in text[:800]:
            continue
        yield f, text


def _is_release_heading(line):
    if not RELEASE_HEADING.match(line):
        return False
    # A heading that IS a version number labels a release entry outright.
    if re.match(r'#{1,6}\s+v\d+\.\d+', line):
        return True
    low = line.lower()
    return any(w in low for w in RELEASE_HEADING_WORDS)


class TestLiveDocCounts(unittest.TestCase):
    def test_no_stale_counts_in_live_docs(self):
        truth = ground_truth()
        stale = []
        for f, text in live_docs():
            in_history = False
            for i, line in enumerate(text.splitlines(), 1):
                # Headings reset the state: a release-narrative heading opens a
                # historical run, any other heading closes one.
                if line.lstrip().startswith("#"):
                    in_history = _is_release_heading(line.lstrip())
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
                for n, noun, shown in stale_claims(line, truth):
                    stale.append(
                        "%s:%d says '%s' but the repo has %d %s"
                        % (f.relative_to(REPO).as_posix(), i, shown, truth[noun], noun))
        self.assertEqual(stale, [], "Stale counts in live docs:\n  " + "\n  ".join(stale))

    def test_ground_truth_is_sane(self):
        """A miscounted truth would make the guard above vacuous."""
        truth = ground_truth()
        self.assertGreater(truth["skills"], 0)
        self.assertGreater(truth["agents"], 0)
        self.assertGreater(truth["commands"], 0)
        self.assertGreater(truth["scripts"], 0)
        self.assertGreater(truth["connectors"], 0)
        self.assertGreater(truth["tests"], 0)

    def test_guard_can_fail(self):
        """Plant-check: each new pattern must actually match its rot form."""
        self.assertTrue(SKILL_MD_RE.search("All 21 SKILL.md files in ContentForge"))
        self.assertTrue(NAMED_SKILLS_RE.search("all 21 ContentForge skills are discoverable"))
        self.assertTrue(TABLE_ROW_RE.search("| Skills count | **158** |"))
        self.assertTrue(COUNT_RE.search("86 Python scripts"))
        self.assertFalse(COUNT_RE.search("~86 scripts"))  # approx stays exempt
        self.assertTrue(COUNT_RE.search("12 top-level slash commands"))
        self.assertTrue(COUNT_RE.search("13 specialist agents"))
        # 2026-10-10 phrasings (each was invisible to the old pattern)
        self.assertTrue(COUNT_RE.search("16 Agent Skills"))
        self.assertTrue(COUNT_RE.search("25 Claude Code slash commands"))
        self.assertTrue(COUNT_RE.search("22 Python helpers"))
        self.assertTrue(COUNT_RE.search("10 opt-in HTTP MCP connectors"))
        self.assertTrue(COUNT_RE.search("## 14. All 25 Commands"))
        self.assertTrue(HYPHEN_RE.search("The 10-connector catalog"))
        self.assertFalse(COUNT_RE.search("3-5 skills"))      # ranges stay exempt
        self.assertFalse(COUNT_RE.search("10-15 scripts"))
        self.assertFalse(COUNT_RE.search("expect 0 connectors configured"))   # zero is a state
        self.assertFalse(COUNT_RE.search("Phase 2 Agent output"))              # not an inventory claim
        self.assertFalse(COUNT_RE.search("a 3-agent workflow"))

    def test_guard_flags_planted_numbers(self):
        """Plant a wrong number in each phrasing and confirm the guard reports it; the
        right number must pass. A pattern that matches but never reports proves nothing."""
        truth = ground_truth()
        plants = [("%d Agent Skills", "skills"),
                  ("%d Claude Code slash commands", "commands"),
                  ("%d Python helpers", "scripts"),
                  ("%d opt-in HTTP MCP connectors", "connectors"),
                  ("## 14. All %d Commands", "commands"),
                  ("The %d-connector catalog", "connectors"),
                  ("`python tests/run_all.py` passes | %d tests", "tests"),
                  ("%d specialist agents", "agents")]
        for template, noun in plants:
            wrong = template % (truth[noun] + 7)
            right = template % truth[noun]
            self.assertTrue(stale_claims(wrong, truth), "guard missed a planted '%s'" % wrong)
            self.assertEqual(stale_claims(right, truth), [], "guard rejected '%s'" % right)
        # a test count on a line with no suite marker is an A/B-testing sentence, not a claim
        self.assertEqual(stale_claims("a team running 8 tests per quarter", truth), [])


class TestPythonMinimum(unittest.TestCase):
    """One Python minimum, stated the same way everywhere.

    Before 2026-10-10 the docs disagreed (3.8+ in guides, 3.10+ in the submission bundle)
    while the pinned c2pa-python 0.38.0 needs 3.10. The floor is the highest requires_python
    among the pinned packages (scripts/_common.py PINNED_DEPENDENCIES); raise FLOOR_MINOR here and in every doc when a pin
    moves. This test cannot reach PyPI, so it keeps the prose consistent, not the pins.
    """
    FLOOR_MINOR = 10
    OPTIONAL_EXTRA_MINOR = None
    OPTIONAL_EXTRA_LINE = None
    STATEMENT = re.compile(r"Python\s+3\.(\d{1,2})\s*(?:\+|or newer)|\b3\.(\d{1,2})\+")

    def statements(self):
        for f, text in live_docs():
            for i, line in enumerate(text.splitlines(), 1):
                if "python" not in line.lower():
                    continue
                for m in self.STATEMENT.finditer(line):
                    yield f, i, int(m.group(1) or m.group(2)), line

    def allowed(self, minor, line):
        if minor == self.FLOOR_MINOR:
            return True
        return bool(self.OPTIONAL_EXTRA_MINOR and minor == self.OPTIONAL_EXTRA_MINOR
                    and self.OPTIONAL_EXTRA_LINE.search(line))

    def test_every_statement_names_the_same_minimum(self):
        seen, wrong = 0, []
        for f, i, minor, line in self.statements():
            seen += 1
            if not self.allowed(minor, line):
                wrong.append("%s:%d says Python 3.%d but the minimum is 3.%d"
                             % (f.relative_to(REPO).as_posix(), i, minor, self.FLOOR_MINOR))
        self.assertGreater(seen, 0, "no Python-minimum statement found; the guard is vacuous")
        self.assertEqual(wrong, [], "Python minimum disagrees:\n  " + "\n  ".join(wrong))

    # scripts/setup.py is the one place the floor is enforced in code (`MIN_PYTHON = (3, N)`).
    SETUP_FLOOR_RE = re.compile(r"^MIN_PYTHON\s*=\s*\(3,\s*(\d+)\)", re.M)

    def test_setup_script_enforces_the_documented_minimum(self):
        src = (REPO / "scripts" / "setup.py").read_text(encoding="utf-8")
        m = self.SETUP_FLOOR_RE.search(src)
        self.assertIsNotNone(m, "scripts/setup.py lost its MIN_PYTHON constant")
        self.assertEqual(int(m.group(1)), self.FLOOR_MINOR,
                         "scripts/setup.py enforces Python 3.%s but the docs say 3.%d"
                         % (m.group(1), self.FLOOR_MINOR))

    def test_setup_script_refuses_an_older_python(self):
        """Behavioural: one minor below the floor, setup.py exits 1 and says 3.N+ required."""
        import contextlib
        import importlib.util
        import io
        import sys
        from unittest import mock
        spec = importlib.util.spec_from_file_location("cf_setup_floor_check", REPO / "scripts" / "setup.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        import collections
        version_info = collections.namedtuple("version_info", "major minor micro releaselevel serial")
        older = version_info(3, self.FLOOR_MINOR - 1, 0, "final", 0)
        out, err = io.StringIO(), io.StringIO()
        # The Google probe imports google.auth, which reads sys.version_info.major; stub it out so
        # the test exercises the version check and nothing else.
        stub = {"credentials": False, "packages": False}
        with mock.patch.object(sys, "version_info", older), \
                mock.patch.object(mod, "check_google_integration", return_value=stub), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                mod.main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Python 3.%d+ required" % self.FLOOR_MINOR, err.getvalue())

    def test_setup_floor_guard_can_fail(self):
        """Plant-check: a script still saying 3.8 must read as a different floor."""
        planted = self.SETUP_FLOOR_RE.search("MIN_PYTHON = (3, 8)\n")
        self.assertIsNotNone(planted)
        self.assertNotEqual(int(planted.group(1)), self.FLOOR_MINOR)

    def test_guard_can_fail(self):
        """Plant-check: the old wrong forms must be seen and rejected."""
        for planted in ("Requires Python 3.8+ with optional dependencies",
                        "- **Python 3.9 or newer** unlocks scoring",
                        "Python version: must be 3.8+"):
            hits = [int(m.group(1) or m.group(2)) for m in self.STATEMENT.finditer(planted)]
            self.assertTrue(hits and not all(self.allowed(h, planted) for h in hits), planted)
        self.assertTrue(all(self.allowed(int(m.group(1) or m.group(2)), "Python 3.%d+" % self.FLOOR_MINOR)
                            for m in self.STATEMENT.finditer("Python 3.%d+" % self.FLOOR_MINOR)))


class TestAgentsContextCurrent(unittest.TestCase):
    """AGENTS.md is auto-loaded by Codex / Cursor / Copilot / Antigravity. Before this
    guard it pinned 'Supported surfaces (v3.22.0)' and listed only 4 of the 8 surfaces
    — telling every non-Claude runtime the plugin was 11 releases older and half as
    portable as it is."""

    def setUp(self):
        self.text = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        self.version = json.loads(
            (REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]

    def test_supported_surfaces_version_is_current(self):
        m = re.search(r"Supported surfaces \(v([\d.]+)\)", self.text)
        self.assertIsNotNone(m, "AGENTS.md lost its 'Supported surfaces (vX.Y.Z)' line")
        self.assertEqual(m.group(1), self.version,
                         "AGENTS.md surfaces line pins v%s but the plugin is v%s"
                         % (m.group(1), self.version))

    def test_supported_surfaces_lists_all_native_surfaces(self):
        m = re.search(r"^.*Supported surfaces.*$", self.text, re.M)
        line = m.group(0) if m else ""
        for name in ("Claude Code", "Cowork", "Codex", "Cursor", "Copilot",
                     "Antigravity", "Hermes", "OpenClaw", "Grok"):
            self.assertIn(name, line, "AGENTS.md surfaces line is missing %s" % name)


class TestPhaseCountConsistent(unittest.TestCase):
    """The canonical claim is 10 phases (established v3.16.0's truth pass). The 2026-08-16
    audit found the new submission bundle saying '11-phase' while every other doc said 10
    — the number a directory reviewer would check first."""

    def test_live_docs_agree_on_ten_phases(self):
        drift = []
        for f, text in live_docs():
            in_history = False
            for i, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("#"):
                    in_history = _is_release_heading(line.lstrip())
                if DATED_LINE.search(line):
                    in_history = True
                    continue
                if in_history:
                    continue
                for m in re.finditer(r"\b(\d+)-phase\b", line):
                    if int(m.group(1)) != 10:
                        drift.append("%s:%d says '%s'"
                                     % (f.relative_to(REPO).as_posix(), i, m.group(0)))
        self.assertEqual(drift, [], "Docs disagree on the phase count:\n  " + "\n  ".join(drift))


if __name__ == "__main__":
    unittest.main()
