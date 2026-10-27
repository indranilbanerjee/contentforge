"""The npx allowlist scanner sees every way a package gets run, not only `npx -y NAME`.

Found in 4.5.12 by probing the scanner (no live defect: none of these forms is in the repo today): `npx deepl-mcp-server@latest`
without -y, `npx -y --package=evil-pkg@1.0.0 deepl-mcp-server` (which runs evil-pkg and reported the allowlisted name),
`npm exec`, `pnpm dlx`, `yarn dlx`, and configs that wrap the runner (`cmd /c npx ...`, `sh -c "npx ..."`) were all invisible to
the guard the weekly workflow relies on. Each form is planted below.
"""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "npm_allowlist.py"
spec = importlib.util.spec_from_file_location("_cf_npm_allowlist_forms", SCRIPT)
na = importlib.util.module_from_spec(spec)
spec.loader.exec_module(na)

ALLOW = {"deepl-mcp-server": {"version": "1.3.14"}}


class TestProseForms(unittest.TestCase):

    def runnables(self, text):
        return na.mentioned_runnables(text)

    def test_npx_without_the_yes_flag(self):
        self.assertEqual(self.runnables("Run `npx deepl-mcp-server@latest` to start it."), ["deepl-mcp-server"])
        self.assertEqual(na.unpinned_mentions("Run `npx deepl-mcp-server@latest`", ALLOW), ["deepl-mcp-server@latest"])

    def test_the_package_flag_names_what_runs_not_the_binary_after_it(self):
        text = "npx -y --package=evil-pkg@1.0.0 deepl-mcp-server"
        self.assertEqual(self.runnables(text), ["evil-pkg"])
        self.assertEqual(self.runnables("npx --package evil-pkg@1.0.0 deepl-mcp-server"), ["evil-pkg"])
        self.assertEqual(self.runnables("npx -p evil-pkg@1.0.0 deepl-mcp-server"), ["evil-pkg"])

    def test_npm_exec_and_the_dlx_runners(self):
        self.assertEqual(self.runnables("npm exec -y evil-pkg@1.0.0"), ["evil-pkg"])
        self.assertEqual(self.runnables("pnpm dlx evil-pkg"), ["evil-pkg"])
        self.assertEqual(self.runnables("yarn dlx @evil/scoped-pkg@2.0.0"), ["@evil/scoped-pkg"])

    def test_the_old_forms_still_work(self):
        self.assertEqual(self.runnables("`npx -y mcp-semrush` and bunx -y @acme/mcp-x@1.2.3"), ["mcp-semrush", "@acme/mcp-x"])
        self.assertEqual(self.runnables('{"args": ["-y", "mcp-twitter"]}'), ["mcp-twitter"])

    def test_prose_that_merely_mentions_the_command_is_ignored(self):
        for text in ("`npx -y` downloads whatever is published under a name.", "Use npx to run a package.",
                     "npx <package-name> is the shape of the command", "an npm exec call can be slow"):
            with self.subTest(text=text):
                self.assertEqual(self.runnables(text), [], text)

    def test_the_args_array_form_with_the_package_flag(self):
        text = '{"command": "npx", "args": ["-y", "--package=evil-pkg@1.0.0", "deepl-mcp-server"]}'
        self.assertEqual(self.runnables(text), ["evil-pkg"])


class TestConfigForms(unittest.TestCase):

    def specs(self, command, args):
        return na.runnable_specs({"mcpServers": {"deepl": {"command": command, "args": args}}})

    def test_package_flag_in_a_config(self):
        self.assertEqual(self.specs("npx", ["-y", "--package=evil-pkg@1.0.0", "deepl-mcp-server"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])
        self.assertEqual(self.specs("npx", ["-y", "-p", "evil-pkg@1.0.0", "deepl-mcp-server"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])

    def test_npm_exec_and_pnpm_dlx_in_a_config(self):
        self.assertEqual(self.specs("npm", ["exec", "-y", "evil-pkg@1.0.0"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])
        self.assertEqual(self.specs("pnpm", ["dlx", "evil-pkg@1.0.0"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])

    def test_a_shell_wrapper_is_unwrapped(self):
        self.assertEqual(self.specs("cmd", ["/c", "npx", "-y", "evil-pkg@1.0.0"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])
        self.assertEqual(self.specs("sh", ["-c", "npx -y evil-pkg@1.0.0"]), [("mcpServers/deepl", "evil-pkg@1.0.0")])

    def test_a_plain_npx_config_is_unchanged(self):
        self.assertEqual(self.specs("npx", ["-y", "deepl-mcp-server@1.3.14"]), [("mcpServers/deepl", "deepl-mcp-server@1.3.14")])
        self.assertEqual(self.specs("python", ["-m", "something"]), [])

    def test_lookalikes_are_still_not_verified(self):
        real = na.load()
        for name in ("deepl-mcp-serverx", "deepl_mcp_server", "DEEPL-MCP-SERVER", "@deepl/deepl-mcp-server"):
            self.assertFalse(na.is_verified(name, real), name)


if __name__ == "__main__":
    unittest.main()
