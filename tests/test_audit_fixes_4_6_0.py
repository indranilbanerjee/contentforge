"""The 4.5.12 audits' smaller findings, each planted.

  * `--help` and a mistyped option work on every script, with or without its optional package, and the help text is valid UTF-8
    when PYTHONUTF8 is unset (setup.py had no parser at all; three scripts imported their package before parsing; two printed a
    cp1252 em dash into a UTF-8 reader);
  * `local-tracker add-row` refuses a requirement_id that already exists (it created an unreachable duplicate);
  * `refresh_models` tells "no key" from "fetch failed" and exits 1 when no provider could be read (a dead network read as
    "no drift");
  * `harvest-brand-pages` exits 1, naming the reason, when the homepage was refused or unreachable, and exits 2 for a scheme it
    will never fetch (it prefixed https:// to file:// and ftp://);
  * the user-visible publish folder is the user's real Documents folder (a OneDrive-redirected one on Windows), not
    ~/Documents next to it.
Everything runs in a temp HOME with a dead proxy; nothing touches the network.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import _common  # noqa: E402


def clean_env(root, **extra):
    env = {k: v for k, v in os.environ.items()
           if k not in ("PYTHONUTF8", "PYTHONIOENCODING", "CLAUDE_PLUGIN_DATA", "PLUGIN_DATA", "CLAUDE_MARKETING_HOME",
                        "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "CONTENTFORGE_PUBLISH_DIR")}
    env.update({"HOME": str(root), "USERPROFILE": str(root), "CLAUDE_MARKETING_HOME": str(Path(root) / "ws"),
                "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
                "http_proxy": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9"})
    env.update(extra)
    return env


def run(script, *args, env, timeout=180):
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, env=env, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


class Temp(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)


class TestHelpAndTypos(Temp):
    SCRIPTS_UNDER_TEST = ("setup.py", "airtable-tracker.py", "drive-uploader.py", "sheets-tracker.py",
                          "build-skill-assets.py", "detect_surface.py")

    def test_help_exits_zero_with_usage_and_valid_utf8(self):
        for name in self.SCRIPTS_UNDER_TEST:
            with self.subTest(script=name):
                rc, out, err = run(name, "--help", env=clean_env(self.root))
                self.assertEqual(rc, 0, (out + err).decode("utf-8", "replace")[-300:])
                text = out.decode("utf-8")  # strict: a cp1252 byte fails here
                self.assertIn("usage:", text.lower())
                self.assertNotIn("\ufffd", text)

    def test_a_mistyped_option_exits_two_with_usage(self):
        for name in self.SCRIPTS_UNDER_TEST:
            with self.subTest(script=name):
                rc, out, err = run(name, "--no-such-option-xyz", env=clean_env(self.root))
                self.assertEqual(rc, 2, (out + err).decode("utf-8", "replace")[-300:])
                self.assertIn("usage", err.decode("utf-8", "replace").lower())


class TestDuplicateRequirementId(Temp):

    def test_the_second_add_row_with_an_existing_id_is_refused(self):
        env = clean_env(self.root)
        run("local-tracker.py", "--action", "init", "--brand", "Acme", env=env)
        data = json.dumps({"requirement_id": "REQ-001", "title": "first"})
        rc, out, _ = run("local-tracker.py", "--action", "add-row", "--brand", "Acme", "--data", data, env=env)
        self.assertEqual(rc, 0, out)
        rc, out, _ = run("local-tracker.py", "--action", "add-row", "--brand", "Acme", "--data",
                         json.dumps({"requirement_id": "REQ-001", "title": "duplicate id"}), env=env)
        self.assertEqual(rc, 1, out)
        self.assertIn("already exists", json.loads(out)["error"])
        tracking = next((self.root / "ws").rglob("tracking.json"))
        records = json.loads(tracking.read_text(encoding="utf-8"))["records"]
        self.assertEqual([r["title"] for r in records], ["first"])

    def test_generated_ids_still_advance(self):
        env = clean_env(self.root)
        run("local-tracker.py", "--action", "init", "--brand", "Acme", env=env)
        ids = []
        for n in range(3):
            rc, out, _ = run("local-tracker.py", "--action", "add-row", "--brand", "Acme", "--data", json.dumps({"title": f"t{n}"}), env=env)
            self.assertEqual(rc, 0, out)
            ids.append(json.loads(out)["requirement_id"])
        self.assertEqual(ids, ["REQ-001", "REQ-002", "REQ-003"])


class TestRefreshModelsStatuses(Temp):

    def test_no_keys_at_all_is_reported_as_no_key_and_exits_one(self):
        rc, out, _ = run("refresh_models.py", "--json", env=clean_env(self.root))
        report = json.loads(out)
        self.assertEqual(rc, 1, report)
        for vendor in ("anthropic", "openai", "google"):
            self.assertEqual(report[vendor]["status"], "skipped (no key)", report)

    def test_keys_present_but_the_network_dead_is_reported_as_fetch_failed_and_exits_one(self):
        env = clean_env(self.root, ANTHROPIC_API_KEY="sk-test-FAKE0000", OPENAI_API_KEY="sk-test-FAKE0001",
                        GEMINI_API_KEY="AIzaFAKE0002")
        rc, out, err = run("refresh_models.py", "--json", env=env, timeout=240)
        report = json.loads(out)
        self.assertEqual(rc, 1, report)
        for vendor in ("anthropic", "openai", "google"):
            self.assertEqual(report[vendor]["status"], "skipped (fetch failed)", report)
        self.assertNotIn(b"FAKE000", out + err)  # a key never reaches the output


class TestHarvestExitsAndSchemes(Temp):

    def test_a_non_public_homepage_is_refused_with_a_reason_and_exit_one(self):
        rc, out, _ = run("harvest-brand-pages.py", "--url", "http://169.254.169.254/", "--max-pages", "1", "--timeout", "3",
                         env=clean_env(self.root))
        report = json.loads(out)
        self.assertEqual(rc, 1, report)
        self.assertTrue(any("refused" in e and "non-public" in e for e in report["errors"]), report["errors"])
        self.assertFalse(any("status 0" in e for e in report["errors"]), report["errors"])

    def test_an_unreachable_site_names_the_network(self):
        rc, out, _ = run("harvest-brand-pages.py", "--url", "https://example.com/", "--max-pages", "1", "--timeout", "3",
                         env=clean_env(self.root), timeout=240)
        report = json.loads(out)
        self.assertEqual(rc, 1, report)
        self.assertTrue(any("network" in e for e in report["errors"]), report["errors"])

    def test_a_scheme_it_will_never_fetch_exits_two(self):
        for url in ("file:///D:/README.md", "ftp://example.com/", "gopher://example.com/"):
            with self.subTest(url=url):
                rc, out, err = run("harvest-brand-pages.py", "--url", url, env=clean_env(self.root))
                self.assertEqual(rc, 2, (out + err).decode("utf-8", "replace")[-300:])
                self.assertIn("http", err.decode("utf-8", "replace"))

    def test_a_bare_domain_still_gets_https(self):
        rc, out, _ = run("harvest-brand-pages.py", "--url", "example.com", "--max-pages", "1", "--timeout", "3",
                         env=clean_env(self.root), timeout=240)
        self.assertEqual(json.loads(out)["domain"], "https://example.com")


class TestDocumentsFolder(unittest.TestCase):

    def test_a_redirected_documents_folder_is_used_when_the_profile_matches(self):
        home = Path.home()
        redirected = home / "OneDrive" / "Documents"
        shell = {40: home, 5: redirected}.get
        self.assertEqual(_common.documents_dir(shell=shell, windows=True), redirected)

    def test_a_redirected_home_falls_back_to_documents_beside_it(self):
        # tests and sandboxes point HOME at a temp folder; the real user's Documents must not be written to then
        elsewhere = Path.home().parent / "someone-else"
        shell = {40: elsewhere, 5: elsewhere / "OneDrive" / "Documents"}.get
        self.assertEqual(_common.documents_dir(shell=shell, windows=True), Path.home() / "Documents")

    def test_off_windows_or_without_an_answer_it_is_documents_in_home(self):
        self.assertEqual(_common.documents_dir(windows=False), Path.home() / "Documents")
        self.assertEqual(_common.documents_dir(shell=lambda csidl: None, windows=True), Path.home() / "Documents")

    def test_the_tracker_publishes_under_it_and_says_which_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            sys.path.insert(0, str(SCRIPTS))
            import importlib.util
            spec = importlib.util.spec_from_file_location("_cf_local_tracker_docs", SCRIPTS / "local-tracker.py")
            lt = importlib.util.module_from_spec(spec)
            old = os.environ.get("CONTENTFORGE_PUBLISH_DIR")
            os.environ.pop("CONTENTFORGE_PUBLISH_DIR", None)
            try:
                spec.loader.exec_module(lt)
                got = lt.get_publish_dir("Acme")
            finally:
                if old is not None:
                    os.environ["CONTENTFORGE_PUBLISH_DIR"] = old
            self.assertEqual(got, _common.documents_dir() / "ContentForge" / "acme")


if __name__ == "__main__":
    unittest.main()
