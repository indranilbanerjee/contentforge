"""4.5.8: connector setup only offers vendor-verified npm packages.

`npx -y <name>` downloads and runs whatever is published under that name, with the user's API keys in its environment. Four of
the package names ContentForge's connector catalog used to hand out did not exist on npm (anyone could have registered them
and received the keys), and most of the rest were community packages rather than the vendor's. The rule now:

1. a runnable command exists only for a package listed in config/verified-npx-packages.json (name, expected npm publisher,
   the vendor's repository);
2. every other connector is "no verified connector": the setup guide prints the options and no command or credentials;
3. an offline guard checks that nothing runnable is outside the list, and a weekly workflow asks npm whether each listed
   package still exists, still has versions and still has the expected publisher.

Each guard is planted below: a non-allowlisted name, the four missing names, a 404, a changed publisher.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import npm_allowlist as na  # noqa: E402

# Connectors that used to be given `npx -y <package>` and are now "no verified connector", with the package each had.
CONVERTED = {
    "confluence": "mcp-confluence", "wordpress": "mcp-wordpress", "hubspot-cms": "mcp-hubspot-cms", "semrush": "mcp-semrush",
    "sarvam-ai": "sarvam-mcp-server", "twitter-x": "mcp-twitter", "linkedin-publishing": "mcp-linkedin-publishing",
    "instagram": "mcp-instagram",
}
# The four of those that are not registered on npm at all (read from registry.npmjs.org, 2026-10-27).
UNREGISTERED = ("mcp-hubspot-cms", "mcp-semrush", "mcp-twitter", "mcp-linkedin-publishing")
# Community image-generation packages that .mcp.json.example used to run.
REMOVED_EXAMPLE_PACKAGES = ("mcp-server-stability-ai", "gemini-nanobanana-mcp", "mcp-imagenate")


def load_connector_status():
    spec = importlib.util.spec_from_file_location("cf_connector_status_under_test", SCRIPTS / "connector-status.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CS = load_connector_status()


def healthy_doc(name="deepl-mcp-server", maintainer="deepl-com", repo="git+https://github.com/DeepL/deepl-mcp-server.git"):
    return {"dist-tags": {"latest": "1.0.0"}, "maintainers": [{"name": maintainer}],
            "versions": {"1.0.0": {"repository": {"url": repo}}}}


class TestTheAllowlistFile(unittest.TestCase):
    def test_every_entry_names_a_publisher_a_vendor_and_the_vendors_repository(self):
        allow = na.load()
        self.assertIn("deepl-mcp-server", allow)
        for name, entry in allow.items():
            with self.subTest(package=name):
                self.assertTrue(entry["npm_publishers"], "no expected publisher")
                self.assertTrue(entry["vendor"])
                self.assertRegex(entry["repository"], r"^https://github\.com/[^/]+/[^/]+$")
                self.assertRegex(entry["verified_on"], r"^\d{4}-\d\d-\d\d$")

    def test_only_one_package_is_listed_today(self):
        self.assertEqual(sorted(na.load()), ["deepl-mcp-server"])


class TestNothingRunnableIsOutsideTheAllowlist(unittest.TestCase):
    def test_the_shipped_configs_and_the_registry_are_clean(self):
        self.assertEqual(na.offline_problems(), [])

    def test_plant_the_example_file_as_it_was_in_4_5_7(self):
        old = {"mcpServers": {name: {"command": "npx", "args": ["-y", pkg], "env": {"K": "${K}"}}
                              for name, pkg in (("stability-ai", "mcp-server-stability-ai"), ("nanobanana", "gemini-nanobanana-mcp"),
                                                ("imagenate", "mcp-imagenate"))}}
        problems = na.offline_problems(config_texts={".mcp.json.example": json.dumps(old)}, registry={})
        self.assertEqual(len(problems), 3, problems)
        for pkg in REMOVED_EXAMPLE_PACKAGES:
            self.assertTrue(any(pkg in p for p in problems), pkg)

    def test_plant_a_registry_that_still_hands_out_the_four_missing_names(self):
        registry = {"cat": {"connectors": {name: {"transport": "npx", "package": pkg} for name, pkg in CONVERTED.items()}}}
        problems = na.offline_problems(config_texts={}, registry=registry)
        self.assertEqual(len(problems), len(CONVERTED))
        for pkg in UNREGISTERED:
            self.assertTrue(any(pkg in p for p in problems), pkg)

    def test_plant_a_scoped_and_a_versioned_name_and_other_runners_are_all_recognised(self):
        config = {"mcpServers": {"a": {"command": "npx", "args": ["-y", "@evil/mcp-x@1.2.3"]},
                                 "b": {"command": "bunx", "args": ["some-mcp"]},
                                 "c": {"command": "pnpm", "args": ["dlx", "other-mcp"]},
                                 "d": {"command": "python", "args": ["server.py"]}}}
        self.assertEqual(sorted(p for _s, p in na.runnable_packages(config)), ["@evil/mcp-x", "other-mcp", "some-mcp"])

    def test_every_connector_the_registry_offers_as_npx_is_listed_and_its_command_names_that_package(self):
        offered = [(name, conn) for cat in CS.CONNECTOR_REGISTRY.values() for name, conn in cat["connectors"].items()
                   if CS._tx(conn) == "npx"]
        self.assertEqual([n for n, _c in offered], ["deepl"])
        for name, conn in offered:
            guide = CS.setup_guide(name)
            entry = guide["mcp_json_entry"][name]
            self.assertEqual(entry["command"], "npx")
            self.assertIn(entry["args"][1], na.load())

    def test_no_shipped_text_tells_anyone_to_run_a_package_that_is_not_listed(self):
        """Discovery: every text file in the repo (skills, docs, scripts, configs, READMEs) except history and tests."""
        allow = na.load()
        skip_dirs = {".git", "node_modules", ".pytest_cache", "tests", "evals", "research", "heroes", ".superpowers"}
        skip_files = {"CHANGELOG.md", "UPGRADE-GUIDE.md"}
        scanned, bad = 0, []
        for path in ROOT.rglob("*"):
            if not path.is_file() or skip_dirs & set(path.relative_to(ROOT).parts) or path.name in skip_files:
                continue
            if path.suffix.lower() not in {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".example", ".toml"} and not path.name.startswith(".mcp.json"):
                continue
            try:
                text = path.read_text(encoding="utf-8-sig")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            for name in na.mentioned_runnables(text):
                if name not in allow:
                    bad.append(f"{path.relative_to(ROOT).as_posix()}: {name}")
        self.assertGreater(scanned, 100, "the scan saw too few files; the guard is vacuous")
        self.assertEqual(bad, [])

    def test_plant_the_scanner_flags_a_command_in_prose_and_in_json_and_ignores_placeholders_and_plain_prose(self):
        found = na.mentioned_runnables('Run `npx -y mcp-semrush` now. {"args": ["-y", "mcp-twitter"]} `npx -y` downloads code. '
                                       'npx -y <package-name> and "-y", "<verified-package-name>"')
        self.assertEqual(found, ["mcp-semrush", "mcp-twitter"])


class TestUnverifiedConnectorsGetNoCommandAndNoCredentials(unittest.TestCase):
    def test_the_eight_converted_connectors_are_manual_with_no_package_and_no_env_vars(self):
        index = {name: conn for cat in CS.CONNECTOR_REGISTRY.values() for name, conn in cat["connectors"].items()}
        for name, package in CONVERTED.items():
            with self.subTest(connector=name):
                conn = index[name]
                self.assertEqual(conn["transport"], "manual")
                self.assertNotIn("package", conn)
                self.assertEqual(conn["env_vars"], [])
                self.assertIn("No verified connector", conn["note"])
                guide = CS.setup_guide(name)
                self.assertEqual(guide["transport"], "manual")
                self.assertNotIn("mcp_json_entry", guide)
                self.assertNotIn("package", guide)
                self.assertEqual(guide["env_vars"], [])
                self.assertNotIn(package, json.dumps(guide))
                self.assertNotIn("npx", json.dumps(guide).replace("npx -y", "").lower().replace("no npm", ""))   # no command
                checked = CS.check_connector(name)
                self.assertEqual(checked["transport"], "manual")
                self.assertNotIn(package, json.dumps(checked))
                self.assertEqual(checked["env_vars"], [])

    def test_the_options_are_printed_instead(self):
        guide = CS.setup_guide("semrush")
        text = json.dumps(guide)
        self.assertIn("vendor", text)
        self.assertIn("aggregator", text)
        self.assertIn("unverified third part", text)

    def test_the_dashboard_and_the_list_report_them_as_manual_not_npx(self):
        dash = CS.status_dashboard()
        transports = {c["name"]: c["transport"] for cat in dash["categories"] for c in cat["connected"] + cat["available"]}
        for name in CONVERTED:
            self.assertEqual(transports[name], "manual", name)
        self.assertEqual(transports["deepl"], "npx")
        listed = {c["name"]: c for c in CS.list_available()["available_connectors"]}
        for name in CONVERTED:
            self.assertNotIn("env_vars_needed", listed[name], name)

    def test_plant_an_npx_entry_for_an_unlisted_package_is_still_treated_as_manual(self):
        """Defence in depth: editing the registry back to npx does not bring the command back."""
        for name, package in (("semrush", "mcp-semrush"), ("wordpress", "mcp-wordpress")):
            with self.subTest(connector=name):
                conn = next(c["connectors"][name] for c in CS.CONNECTOR_REGISTRY.values() if name in c["connectors"])
                patched = dict(conn, transport="npx", package=package, env_vars=["SECRET_KEY"])
                with mock.patch.dict(conn, patched):
                    guide = CS.setup_guide(name)
                    checked = CS.check_connector(name)
                self.assertEqual(guide["transport"], "manual")
                self.assertNotIn("mcp_json_entry", guide)
                self.assertNotIn(package, json.dumps(guide))
                self.assertEqual(checked["transport"], "manual")

    def test_the_script_source_names_no_community_package(self):
        text = (SCRIPTS / "connector-status.py").read_text(encoding="utf-8")
        for package in list(CONVERTED.values()) + list(REMOVED_EXAMPLE_PACKAGES):
            self.assertNotIn(package, text, package)

    def test_the_example_file_ships_only_the_vendor_package(self):
        data = json.loads((ROOT / ".mcp.json.example").read_text(encoding="utf-8-sig"))
        self.assertEqual(sorted(data["mcpServers"]), ["deepl"])
        self.assertEqual(data["mcpServers"]["deepl"]["args"], ["-y", "deepl-mcp-server"])


class TestTheWeeklyOnlineCheck(unittest.TestCase):
    ENTRY = na.load()["deepl-mcp-server"]

    def run_check(self, doc):
        return na.online_problems(allow={"deepl-mcp-server": self.ENTRY}, fetch=lambda _name: doc)

    def test_a_healthy_package_passes(self):
        self.assertEqual(self.run_check(healthy_doc()), [])

    def test_plant_a_404_name(self):
        problems = self.run_check(None)
        self.assertEqual(len(problems), 1)
        self.assertIn("not on npm (404)", problems[0])
        self.assertIn("free for anyone to register", problems[0])

    def test_plant_a_package_with_no_versions(self):
        self.assertIn("no published versions", self.run_check({"dist-tags": {}, "maintainers": [], "versions": {}})[0])

    def test_plant_a_changed_publisher(self):
        problems = self.run_check(healthy_doc(maintainer="someone-else"))
        self.assertEqual(len(problems), 1)
        self.assertIn("publisher changed", problems[0])
        self.assertIn("someone-else", problems[0])

    def test_plant_a_changed_repository(self):
        problems = self.run_check(healthy_doc(repo="git+https://github.com/not-deepl/deepl-mcp-server.git"))
        self.assertIn("repository changed", problems[0])

    def test_repository_spellings_that_mean_the_same_repo_pass(self):
        for url in ("https://github.com/DeepL/deepl-mcp-server", "git://github.com/DeepL/deepl-mcp-server.git",
                    "git+https://github.com/deepl/deepl-mcp-server.git/"):
            with self.subTest(url=url):
                self.assertEqual(self.run_check(healthy_doc(repo=url)), [])

    def test_plant_a_deprecated_latest_version(self):
        doc = healthy_doc()
        doc["versions"]["1.0.0"]["deprecated"] = "use something else"
        self.assertIn("marked deprecated", self.run_check(doc)[0])

    def test_an_unreachable_registry_is_reported_not_hidden(self):
        def boom(_name):
            raise OSError("network down")
        problems = na.online_problems(allow={"deepl-mcp-server": self.ENTRY}, fetch=boom)
        self.assertIn("could not read npm", problems[0])

    def test_the_cli_writes_the_report_and_exits_1(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(na, "online_problems", return_value=["x: not on npm (404)"]):
            report = str(Path(d) / "report")
            self.assertEqual(na.main(["--online", "--report", report]), 1)
            self.assertIn("not on npm (404)", Path(report + ".md").read_text(encoding="utf-8"))
            self.assertFalse(json.loads(Path(report + ".json").read_text(encoding="utf-8"))["ok"])
        with mock.patch.object(na, "online_problems", return_value=[]):
            self.assertEqual(na.main(["--online"]), 0)

    def test_the_workflow_runs_weekly_checks_both_ways_and_opens_an_issue_with_least_privilege(self):
        text = (ROOT / ".github" / "workflows" / "npm-allowlist.yml").read_text(encoding="utf-8")
        self.assertRegex(text, r'cron:\s*"[^"]+ \* \* [0-7]"')
        self.assertIn("scripts/npm_allowlist.py --check", text)
        self.assertIn("scripts/npm_allowlist.py --online", text)
        self.assertIn("gh issue create", text)
        self.assertIn("if: failure()", text)
        self.assertIn("issues: write", text)
        self.assertNotIn("contents: write", text)
        self.assertNotIn("pull_request_target", text)


if __name__ == "__main__":
    unittest.main()
