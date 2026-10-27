"""Every script a workflow tells an agent to run takes the arguments the workflow gives it.

Found in 4.5.12: workflows/audit-library.js told the agent to run `audit-ledger.py --action record`. The script takes
subcommands (`record --brand B --file F`), so the command exits 2 ("unrecognized arguments: --action") and the library audit
could not be recorded. The prose looked right and nothing parsed it. This test parses each invocation against the script's own
--help: the first word must be a subcommand when the script has subcommands, and every --flag must exist.
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
MENTION = re.compile(r"scripts/([A-Za-z0-9_\-]+\.py)[\"']?\s*([^)'`\"\\,\n]*)")
HELP_CACHE: dict = {}


def help_of(script: str, *sub: str) -> str:
    key = (script, sub)
    if key not in HELP_CACHE:
        proc = subprocess.run([sys.executable, str(SCRIPTS / script), *sub, "--help"], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120)
        HELP_CACHE[key] = proc.stdout + proc.stderr
    return HELP_CACHE[key]


def problems_in(script: str, args_text: str) -> list:
    """What is wrong with `script args_text` according to the script's own --help (empty = parses)."""
    if not (SCRIPTS / script).is_file():
        return [f"{script} does not exist"]
    words = args_text.split()
    top = help_of(script)
    out = []
    groups = re.findall(r"\{([a-z0-9_,\-]+)\}", top)
    sub = ()
    if groups:
        subcommands = set(groups[0].split(","))
        first = next((w for w in words if not w.startswith("-")), None)
        if first not in subcommands:
            out.append(f"{script}: the first word must be one of {sorted(subcommands)}, not {first!r}")
        else:
            sub = (first,)
    # options before the subcommand belong to the script itself, options after it to the subcommand
    position = words.index(sub[0]) if sub else len(words)
    for index, word in enumerate(words):
        if word.startswith("--"):
            text = help_of(script, *sub) if sub and index > position else top
            if word.split("=")[0] not in text:
                out.append(f"{script}: unknown option {word}")
    return out


def workflow_invocations(source: str) -> list:
    found = []
    for match in MENTION.finditer(source):
        found.append((match.group(1), match.group(2).replace("<", "").replace(">", "").strip()))
    return found


class TestWorkflowInvocations(unittest.TestCase):

    def test_every_script_a_workflow_names_parses(self):
        checked = 0
        for path in sorted((REPO / "workflows").glob("*.js")):
            for script, args_text in workflow_invocations(path.read_text(encoding="utf-8-sig")):
                with self.subTest(workflow=path.name, script=script):
                    self.assertEqual(problems_in(script, args_text), [], f"{path.name}: {script} {args_text}")
                    checked += 1
        self.assertGreater(checked, 0, "no workflow names a script, so this test checked nothing")

    def test_the_4_5_12_form_is_caught(self):
        got = problems_in("audit-ledger.py", "--action record")
        self.assertTrue(got, "the form that exits 2 must be reported")
        self.assertTrue(any("--action" in line for line in got), got)
        self.assertTrue(problems_in("audit-ledger.py", "export --brand B"), "an unknown subcommand is caught too")

    def test_the_real_form_passes(self):
        self.assertEqual(problems_in("audit-ledger.py", "record --brand B --file F"), [])
        self.assertEqual(problems_in("audit-ledger.py", "validate --file F"), [])

    def test_an_unknown_option_on_a_real_subcommand_is_caught(self):
        self.assertTrue(problems_in("audit-ledger.py", "record --nonsense x"))

    def test_the_workflow_names_the_absolute_script_path_form(self):
        text = (REPO / "workflows" / "audit-library.js").read_text(encoding="utf-8-sig")
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/scripts/audit-ledger.py" record', text)


if __name__ == "__main__":
    unittest.main()
