"""Local side-effect skills stay reachable through their gate; publishing is started by the user only.

Why this test exists. A skill with `disable-model-invocation: true` is removed
from the model's listing. A plain request such as "translate this into Spanish"
then matches nothing, and the model can still reach the same tools freehand,
with no gate in the way. Keeping a skill whose effects stay on the user's
machine model-invocable routes the request through its `## Execution gate`
block: scope or preview first, an explicit typed `yes`, anything else cancels.

Publishing is the exception (4.7.0, security review finding 6). A skill that
pushes content to an audience (a CMS) must not be startable by the model on its
own: text the model read, such as a source page or a client file, could
otherwise ask it to start one. `cf-publish` is therefore hidden like its
`/contentforge:publish` wrapper, only the user starts it, and it keeps its
gate, because hosts that ignore the flag (Codex) leave the typed `yes` as the
safety layer there. Any skill whose body drives a CMS publish (`cms-publisher`,
`push_to_cms`) or `--force`, or whose description starts with publish / send /
post / schedule / launch, must be in USER_STARTED_SKILLS.

The listing carries one entry per purpose: thin wrapper COMMANDS are hidden
(`disable-model-invocation: true`) so they do not compete with the skill they
wrap, and this test requires every hidden wrapper's target skill to be visible,
except a user-started skill, whose wrapper and skill are both hidden.

Stdlib only.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
COMMANDS = ROOT / "commands"

# Skills that change something outside the conversation but not in front of an
# audience (write files, switch backends). Each must be model-invocable AND carry a gate.
SIDE_EFFECT_SKILLS = frozenset({"cf-translate", "cf-social-adapt", "cf-switch-backend", "cf-add-integration"})

# Skills that publish, send or spend. Each must be hidden from the model
# (`disable-model-invocation: true`) AND carry a gate.
USER_STARTED_SKILLS = frozenset({"cf-publish"})

# What marks a skill as publishing, sending or spending.
PUBLISH_BODY_RE = re.compile(r"cms[-_]publisher|push_to_cms|--force\b")
PUBLISH_DESC_RE = re.compile(r"^(?:publish|send|post|schedule|launch)\b", re.I)

# Hidden wrapper command -> the visible skill it hands over to.
WRAPPER_TARGETS = {
    "audit-content": "cf-audit",
    "content-brief": "cf-brief",
    "create-content": "contentforge",
    "publish": "cf-publish",
    "social-adapt": "cf-social-adapt",
    "translate": "cf-translate",
}

# Skills allowed to stay hidden (internal steps whose commands are the visible entries).
INTERNAL_HIDDEN_SKILLS = frozenset(set())

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
GATE_RE = re.compile(r"^## Execution gate\b[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S)


def frontmatter(text: str) -> str:
    m = FM_RE.match(text)
    return m.group(1) if m else ""


def flag(text: str) -> str | None:
    m = re.search(r"^disable-model-invocation:\s*(true|false)\s*$", frontmatter(text), re.M)
    return m.group(1) if m else None


def description(text: str) -> str:
    m = re.search(r"^description:[ \t]*(.*)$", frontmatter(text), re.M)
    return m.group(1).strip().strip('"') if m else ""


def publishes(text: str) -> bool:
    """The skill drives a CMS publish or a forced write, or says it publishes, sends or posts."""
    return bool(PUBLISH_BODY_RE.search(text) or PUBLISH_DESC_RE.search(description(text)))


def gate_problems(text: str, hidden: bool = False) -> list[str]:
    out = []
    want = "true" if hidden else "false"
    if flag(text) != want:
        out.append(f"frontmatter does not say `disable-model-invocation: {want}`")
    m = GATE_RE.search(text.replace("\r\n", "\n"))
    if not m:
        out.append("no `## Execution gate` block")
    else:
        body = m.group(1)
        if "`yes`" not in body:
            out.append("gate block never asks for a typed `yes`")
        if "cancel" not in body.lower():
            out.append("gate block never says that any other reply cancels")
    return out


def wrapper_problems(commands: dict[str, str], skills: dict[str, str], targets: dict[str, str],
                     user_started=frozenset()) -> list[str]:
    """commands/skills: name -> file text. A wrapper of a user-started skill and the skill agree: both hidden."""
    out = []
    for name, text in commands.items():
        if flag(text) == "true" and name not in targets:
            out.append(f"hidden command {name} has no registered target skill")
    for cmd, skill in targets.items():
        if cmd not in commands:
            out.append(f"registered wrapper {cmd} does not exist")
        elif skill not in skills:
            out.append(f"wrapper {cmd} points at missing skill {skill}")
        elif skill in user_started:
            if flag(commands[cmd]) != "true" or flag(skills[skill]) != "true":
                out.append(f"wrapper {cmd} and its user-started skill {skill} must both be hidden")
        elif flag(skills[skill]) == "true":
            out.append(f"wrapper {cmd} is hidden and so is its target {skill}: nothing is left to route to")
    return out


def publishing_problems(skills: dict[str, str], user_started) -> list[str]:
    """Every skill that publishes, sends or spends is registered as user-started, and every registered one does."""
    found = {n for n, t in skills.items() if publishes(t)}
    out = [f"skill {n} publishes, sends or spends but is not in USER_STARTED_SKILLS"
           for n in sorted(found - set(user_started))]
    out += [f"skill {n} is in USER_STARTED_SKILLS but nothing in it publishes"
            for n in sorted(set(user_started) - found) if n in skills]
    return out


def hidden_skill_problems(skills: dict[str, str], allowed) -> list[str]:
    return [f"skill {n} is hidden but is not an allowed internal step"
            for n, t in sorted(skills.items()) if flag(t) == "true" and n not in allowed]


def _load(dirpath: Path, pattern: str, name_of) -> dict[str, str]:
    out = {}
    for p in sorted(dirpath.glob(pattern)):
        out[name_of(p)] = p.read_text(encoding="utf-8", errors="replace")
    return out


class TestExecutionGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = _load(SKILLS, "*/SKILL.md", lambda p: p.parent.name)
        cls.commands = _load(COMMANDS, "*.md", lambda p: p.stem)

    def test_side_effect_skills_exist(self):
        self.assertEqual(sorted(n for n in SIDE_EFFECT_SKILLS | USER_STARTED_SKILLS if n not in self.skills), [])

    def test_every_side_effect_skill_is_invocable_and_has_its_gate(self):
        bad = {n: p for n in sorted(SIDE_EFFECT_SKILLS) if n in self.skills
               and (p := gate_problems(self.skills[n]))}
        self.assertEqual(bad, {}, "a side-effect skill lost its gate or was hidden again "
                                  "(see this module's docstring for why)")

    def test_every_user_started_skill_is_hidden_and_has_its_gate(self):
        bad = {n: p for n in sorted(USER_STARTED_SKILLS) if n in self.skills
               and (p := gate_problems(self.skills[n], hidden=True))}
        self.assertEqual(bad, {}, "a publishing skill became model-invocable again or lost its gate")

    def test_every_skill_that_publishes_is_user_started(self):
        self.assertEqual(publishing_problems(self.skills, USER_STARTED_SKILLS), [])

    def test_every_hidden_wrapper_points_at_a_visible_skill(self):
        self.assertEqual(wrapper_problems(self.commands, self.skills, WRAPPER_TARGETS, USER_STARTED_SKILLS), [])

    def test_no_skill_is_hidden_unless_it_is_an_internal_step(self):
        self.assertEqual(hidden_skill_problems(self.skills, INTERNAL_HIDDEN_SKILLS | USER_STARTED_SKILLS), [])

    # ── planted failures ────────────────────────────────────────────────

    GOOD_SKILL = ("---\nname: x\ndisable-model-invocation: false\n---\n\n# x\n\n## Execution gate\n\n"
                  "Show the preview and wait for `yes`; any other reply cancels.\n\n## Process\n")

    def test_plant_gate_missing(self):
        t = self.GOOD_SKILL.replace("## Execution gate", "## Notes")
        self.assertIn("no `## Execution gate` block", gate_problems(t))

    def test_plant_hidden_again(self):
        t = self.GOOD_SKILL.replace("disable-model-invocation: false", "disable-model-invocation: true")
        self.assertTrue(any("disable-model-invocation: false" in p for p in gate_problems(t)))
        self.assertTrue(gate_problems(self.GOOD_SKILL.replace("disable-model-invocation: false\n", "")))

    def test_plant_gate_without_yes_or_cancel(self):
        no_yes = self.GOOD_SKILL.replace("`yes`", "a go-ahead")
        no_cancel = self.GOOD_SKILL.replace("; any other reply cancels", "")
        self.assertTrue(any("typed `yes`" in p for p in gate_problems(no_yes)))
        self.assertTrue(any("cancels" in p for p in gate_problems(no_cancel)))
        self.assertEqual(gate_problems(self.GOOD_SKILL), [])

    def test_plant_wrapper_target_hidden_or_missing(self):
        hidden = "---\nname: t\ndisable-model-invocation: true\n---\n"
        visible = "---\nname: t\ndisable-model-invocation: false\n---\n"
        cmd = "---\ndescription: d\ndisable-model-invocation: true\n---\n"
        self.assertEqual(wrapper_problems({"w": cmd}, {"t": visible}, {"w": "t"}), [])
        self.assertTrue(wrapper_problems({"w": cmd}, {"t": hidden}, {"w": "t"}))      # target hidden too
        self.assertTrue(wrapper_problems({"w": cmd}, {}, {"w": "t"}))                  # target missing
        self.assertTrue(wrapper_problems({"w": cmd}, {"t": visible}, {}))              # unregistered hidden command
        self.assertTrue(wrapper_problems({}, {"t": visible}, {"w": "t"}))              # registered wrapper missing

    def test_plant_publishing_skill_made_invocable(self):
        hidden = self.GOOD_SKILL.replace("disable-model-invocation: false", "disable-model-invocation: true")
        self.assertEqual(gate_problems(hidden, hidden=True), [])
        self.assertTrue(gate_problems(self.GOOD_SKILL, hidden=True))

    def test_plant_unregistered_publishing_skill(self):
        body = "---\nname: p\ndescription: \"Tidy a draft\"\n---\nCalls `utilities/cms-publisher.md` step 5.\n"
        desc = "---\nname: q\ndescription: \"Send the newsletter to the list\"\n---\nBody.\n"
        quiet = ("---\nname: r\ndescription: \"Repurpose an article into social posts\"\n---\n"
                 "Points at /contentforge:publish.\n")
        self.assertTrue(publishing_problems({"p": body}, frozenset()))
        self.assertTrue(publishing_problems({"q": desc}, frozenset()))
        self.assertEqual(publishing_problems({"r": quiet}, frozenset()), [])
        self.assertTrue(publishing_problems({"r": quiet}, frozenset({"r"})))   # registered but publishes nothing

    def test_plant_user_started_wrapper_disagrees(self):
        hidden = "---\nname: t\ndisable-model-invocation: true\n---\n"
        visible = "---\nname: t\ndisable-model-invocation: false\n---\n"
        cmd = "---\ndescription: d\ndisable-model-invocation: true\n---\n"
        self.assertEqual(wrapper_problems({"w": cmd}, {"t": hidden}, {"w": "t"}, frozenset({"t"})), [])
        self.assertTrue(wrapper_problems({"w": cmd}, {"t": visible}, {"w": "t"}, frozenset({"t"})))

    def test_plant_unexpected_hidden_skill(self):
        hidden = "---\nname: s\ndisable-model-invocation: true\n---\n"
        self.assertTrue(hidden_skill_problems({"s": hidden}, frozenset()))
        self.assertEqual(hidden_skill_problems({"s": hidden}, frozenset({"s"})), [])


if __name__ == "__main__":
    unittest.main()
