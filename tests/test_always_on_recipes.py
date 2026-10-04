"""docs/ALWAYS-ON-RECIPES.md must only ask the plugin for things the plugin does.

The recipes are copy-paste prompts that run unattended, which is the worst place
for a stale flag: nobody is watching when `--from-audit` has been renamed, the job
fails silently, and the loop the recipe exists to keep turning stops without a
sound. So the ContentForge side of every recipe is checked against the shipped
files:

  * every /contentforge:<name> is a real skill or command
  * every --flag written on a /contentforge: line exists in that skill's text (or in
    the skill a thin command wraps)
  * every script named exists, every audit-ledger.py subcommand is a real one, every
    environment variable and store path the recipes lean on appears in shipped code
  * every `--skill <name>` handed to a scheduler is a real skill directory
  * the schedules keep the loop's order: the AEO sweep before the audit, the audit
    before the quarterly calendar
  * the safety rails in the prompts (stop on a missing brand directory, never run
    brand-setup, report RECORDED / NOT RECORDED) cannot be edited out unnoticed
  * the documented sources, the retrieval date and the "unverified" labels on the
    platforms whose documentation is thin stay in place

The platform side (what Claude Tag, Grok Bot, Gemini Spark, Hermes and Claude Code
routines actually do) comes from their documentation and cannot be proven offline;
the document says so, and this file does not pretend otherwise.

Every guard has a planted failure in TestGuardFires. Stdlib only.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC_PATH = REPO / "docs" / "ALWAYS-ON-RECIPES.md"

REQUIRED_SOURCES = (
    "https://code.claude.com/docs/en/routines",
    "https://x.ai/news/grok-bot-more-plans",
    "https://support.google.com/gemini/answer/17171264",
)

REQUIRED_RAILS = (
    "Nobody can answer questions",
    "BRAND DIRECTORY NOT FOUND",
    "Do not run brand-setup",
    "Do not create a blank brand",
    "RECORDED",
    "NOT RECORDED",
)

PLATFORM_HEADINGS = ("### Claude Code", "### Claude Tag in Slack", "### Grok Bot",
                     "### Gemini Spark", "### Hermes cron")

# Where the loop's file-contract stores must be documented in shipped text.
STORE_TOKENS = ("aeo/checks.json", "audits/", "Brand-Guidelines/")

ENV_VARS = ("CLAUDE_MARKETING_HOME", "CLAUDE_PLUGIN_DATA", "PLUGIN_DATA")


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def shipped_text() -> str:
    """Every skill, command and script: the surface a recipe may lean on."""
    parts = []
    for base, pattern in (("skills", "*/SKILL.md"), ("commands", "*.md"), ("scripts", "*.py")):
        for f in sorted((REPO / base).glob(pattern)):
            parts.append(read(f))
    return "\n".join(parts)


def flag_surface(name: str) -> str | None:
    """Text in which a /contentforge:<name> flag must appear: the skill, the command,
    and any skill the command links to (commands are thin wrappers)."""
    parts, found = [], False
    skill = REPO / "skills" / name / "SKILL.md"
    cmd = REPO / "commands" / f"{name}.md"
    if skill.is_file():
        parts.append(read(skill))
        found = True
    if cmd.is_file():
        ctext = read(cmd)
        parts.append(ctext)
        found = True
        for linked in set(re.findall(r"skills/([\w-]+)/SKILL\.md", ctext)):
            f = REPO / "skills" / linked / "SKILL.md"
            if f.is_file():
                parts.append(read(f))
    return "\n".join(parts) if found else None


def cron_fields(expr: str) -> list[str]:
    return expr.split()


def check_slash_commands_and_flags(text: str) -> list[str]:
    problems = []
    for name in sorted(set(re.findall(r"/contentforge:([\w-]+)", text))):
        if flag_surface(name) is None:
            problems.append(f"names /contentforge:{name}, which is neither a skill nor a command")
    for i, line in enumerate(text.splitlines(), 1):
        names = re.findall(r"/contentforge:([\w-]+)", line)
        if not names:
            continue
        surface = "\n".join(s for s in (flag_surface(n) for n in names) if s)
        for flag in re.findall(r"(?<![\w-])(--[a-z][a-z-]*)", line):
            # whole-token match: '--thresh' must not be satisfied by '--threshold'
            if not re.search(rf"(?<![\w-]){re.escape(flag)}(?![\w-])", surface):
                problems.append(f"line {i}: {flag} is written beside /contentforge:"
                                f"{'/'.join(names)} but is not in that skill or command")
    return problems


def check_scripts_and_subcommands(text: str) -> list[str]:
    problems = []
    for name in sorted(set(re.findall(r"scripts/([\w-]+\.py)", text))):
        if not (REPO / "scripts" / name).is_file():
            problems.append(f"names scripts/{name}, which does not exist")
    ledger = read(REPO / "scripts" / "audit-ledger.py")
    for sub in sorted(set(re.findall(r"audit-ledger\.py\s+([a-z]+)\b", text))):
        if f'add_parser("{sub}")' not in ledger:
            problems.append(f"audit-ledger.py has no subcommand {sub!r}")
    meta = read(REPO / "scripts" / "plugin-metadata.py")
    for sect in sorted(set(re.findall(r"plugin-metadata\.py --section ([\w-]+)", text))):
        if f'"{sect}"' not in meta and f"'{sect}'" not in meta:
            problems.append(f"plugin-metadata.py has no --section {sect!r}")
    return problems


def check_env_and_stores(text: str) -> list[str]:
    problems = []
    shipped = shipped_text()
    # Every environment variable written with a $ prefix must be one the plugin
    # itself reads or documents; a renamed variable fails silently in a scheduled run.
    for var in sorted(set(re.findall(r"\$\{?([A-Z][A-Z0-9_]{4,})\}?", text))):
        if var not in shipped:
            problems.append(f"names ${var}, which no shipped skill, command or script mentions")
    common = read(REPO / "scripts" / "_common.py")
    for var in ENV_VARS:
        if var not in common:
            problems.append(f"scripts/_common.py no longer reads {var}, which the recipes depend on")
    for token in STORE_TOKENS:
        if token in text and token not in shipped:
            problems.append(f"names {token!r}, which no shipped skill or script mentions")
    return problems


def check_scheduler_skill_names(text: str) -> list[str]:
    problems = []
    for name in sorted(set(re.findall(r"--skill\s+([\w-]+)", text))):
        if not (REPO / "skills" / name / "SKILL.md").is_file():
            problems.append(f"hands the scheduler --skill {name}, which is not a skill directory")
    return problems


def check_schedule_order(text: str) -> list[str]:
    """Hermes examples are the machine-readable schedules. Invariant: AEO sweep first,
    audit later the same day, quarterly calendar on a later day, quarter months only."""
    rows = {}
    for expr, skill in re.findall(r'hermes cron create "([^"]+)"\s+"[^"]*"\s+--skill\s+([\w-]+)', text):
        rows[skill] = cron_fields(expr)
    problems = []
    for skill in ("cf-aeo-check", "cf-audit", "cf-calendar"):
        if skill not in rows or len(rows[skill]) != 5:
            return [f"no 5-field cron schedule found for the {skill} job in the Hermes examples"]
    sweep, audit, cal = rows["cf-aeo-check"], rows["cf-audit"], rows["cf-calendar"]
    try:
        if sweep[2] != audit[2]:
            problems.append("the audit must run on the same day as the sweep it follows")
        if not int(audit[1]) > int(sweep[1]):
            problems.append("the audit must be scheduled after the AEO sweep (it reads the sweep's history)")
        if not int(cal[2]) > int(audit[2]):
            problems.append("the quarterly calendar must run on a later day than the monthly audit "
                            "(it reads the audit's record)")
        if cal[3] != "1,4,7,10":
            problems.append(f"the quarterly job runs in months {cal[3]!r}, not 1,4,7,10")
        if sweep[3] != "*" or audit[3] != "*":
            problems.append("the sweep and the audit are monthly jobs (month field must be *)")
    except ValueError:
        problems.append("a cron field that must be numeric is not")
    # the /schedule update examples in prose must repeat the same expressions
    for label, fields in (("monthly", sweep), ("quarterly", cal)):
        expr = " ".join(fields)
        if label == "monthly" and f"`{expr}`" not in text:
            problems.append(f"the Claude Code section no longer shows the monthly cron `{expr}`")
        if label == "quarterly" and f"`{expr}`" not in text:
            problems.append(f"the Claude Code section no longer shows the quarterly cron `{expr}`")
    return problems


def check_rails(text: str) -> list[str]:
    return [f"safety rail missing from the prompts: {r!r}" for r in REQUIRED_RAILS if r not in text]


def check_sources_and_honesty(text: str) -> list[str]:
    problems = [f"required source URL missing: {u}" for u in REQUIRED_SOURCES if u not in text]
    if not re.search(r"Retrieved \d{4}-\d{2}-\d{2}", text):
        problems.append("the Sources section lost its 'Retrieved YYYY-MM-DD' line")
    for head in PLATFORM_HEADINGS:
        if head not in text:
            problems.append(f"platform section missing: {head}")
    for head in ("### Grok Bot", "### Gemini Spark"):
        m = re.search(rf"^{re.escape(head)}\s*\n(.*?)(?=^#{{2,3}} )", text, re.M | re.S)
        if m and "unverified" not in m.group(1).casefold():
            problems.append(f"{head} no longer labels itself unverified")
    for needle in ("## Before you schedule anything", "brand directory", "## What these recipes do not promise"):
        if needle not in text:
            problems.append(f"missing required content: {needle!r}")
    return problems


def check_recipes(text: str) -> list[str]:
    problems = []
    for fn in (check_slash_commands_and_flags, check_scripts_and_subcommands, check_env_and_stores,
               check_scheduler_skill_names, check_schedule_order, check_rails,
               check_sources_and_honesty):
        problems += fn(text)
    return problems


DOC = read(DOC_PATH) if DOC_PATH.is_file() else ""


class TestAlwaysOnRecipes(unittest.TestCase):
    def test_document_exists(self):
        self.assertTrue(DOC_PATH.is_file(), "docs/ALWAYS-ON-RECIPES.md is missing")

    def test_recipes_only_use_what_the_plugin_ships(self):
        problems = check_recipes(DOC)
        self.assertEqual(problems, [], "docs/ALWAYS-ON-RECIPES.md has drifted from the plugin:\n  "
                         + "\n  ".join(problems))

    def test_guards_are_not_vacuous(self):
        """A scanner that finds nothing to check passes everything."""
        self.assertGreaterEqual(len(set(re.findall(r"/contentforge:([\w-]+)", DOC))), 4)
        self.assertTrue(re.findall(r"(?<![\w-])--(?:from-audit|period|cadence|scope|threshold)", DOC))
        self.assertEqual(len(re.findall(r'hermes cron create "\d', DOC)), 3)
        self.assertGreaterEqual(len(re.findall(r"audit-ledger\.py\s+[a-z]+", DOC)), 2)

    def test_the_recipes_cover_the_three_lifecycle_jobs(self):
        for needle in ("/contentforge:cf-aeo-check", "/contentforge:audit-content",
                       "/contentforge:cf-calendar --period=90 --from-audit=latest"):
            self.assertIn(needle, DOC)

    def test_aeo_runs_before_audit_in_the_monthly_prompt(self):
        sweep = DOC.index("/contentforge:cf-aeo-check <url>")
        audit = DOC.index("/contentforge:audit-content <content source>")
        self.assertLess(sweep, audit, "the audit reads the sweep's history, so the sweep goes first")


class TestGuardFires(unittest.TestCase):
    """Plant a wrong flag, name, schedule or rail; the checker must object."""

    @classmethod
    def setUpClass(cls):
        cls.baseline = check_recipes(DOC)
        assert cls.baseline == [], "plant tests need a clean baseline: " + str(cls.baseline)

    def plant(self, old: str, new: str):
        self.assertIn(old, DOC, f"plant anchor {old!r} not found — the doc moved; update this plant")
        problems = check_recipes(DOC.replace(old, new, 1))
        self.assertTrue(problems, f"planted drift went unnoticed: {old!r} -> {new!r}")
        return problems

    def test_misspelled_command_is_caught(self):
        self.plant("/contentforge:cf-aeo-check <url>", "/contentforge:cf-aeo-chek <url>")

    def test_renamed_flag_is_caught(self):
        self.plant("--from-audit=latest --cadence=biweekly", "--from-audt=latest --cadence=biweekly")

    def test_invented_flag_is_caught(self):
        self.plant("--scope=both --threshold=12", "--scope=both --thresh=12")

    def test_unknown_script_is_caught(self):
        self.plant("scripts/audit-ledger.py list", "scripts/audit-ledgr.py list")

    def test_unknown_audit_ledger_subcommand_is_caught(self):
        self.plant("audit-ledger.py list --brand", "audit-ledger.py enumerate --brand")

    def test_unread_environment_variable_is_caught(self):
        self.plant("`$CLAUDE_MARKETING_HOME` if set", "`$CLAUDE_MARKETING_ROOT` if set")

    def test_unknown_scheduler_skill_is_caught(self):
        self.plant("--skill cf-aeo-check", "--skill cf-aeo-chek")

    def test_audit_scheduled_before_the_sweep_is_caught(self):
        self.plant('hermes cron create "7 7 1 * *"', 'hermes cron create "7 5 1 * *"')

    def test_calendar_on_the_same_day_as_the_audit_is_caught(self):
        self.plant('hermes cron create "13 6 2 1,4,7,10 *"', 'hermes cron create "13 6 1 1,4,7,10 *"')

    def test_quarterly_months_drift_is_caught(self):
        self.plant('hermes cron create "13 6 2 1,4,7,10 *"', 'hermes cron create "13 6 2 1,3,5,7 *"')

    def test_removed_safety_rail_is_caught(self):
        self.plant("BRAND DIRECTORY NOT FOUND", "brand directory missing")

    def test_removed_brand_setup_rail_is_caught(self):
        self.plant("Do not run brand-setup.", "Run brand-setup if needed.")

    def test_dropped_required_source_is_caught(self):
        self.plant("https://x.ai/news/grok-bot-more-plans", "https://example.invalid/grok")

    def test_dropped_retrieval_date_is_caught(self):
        self.plant("Retrieved 2026-10-04.", "Accessed recently.")

    def test_grok_section_losing_its_unverified_label_is_caught(self):
        self.plant("Unverified, and the cited page is thin.", "Works well.")

    def test_removed_platform_section_is_caught(self):
        self.plant("### Gemini Spark", "### Gemini")


if __name__ == "__main__":
    unittest.main()
