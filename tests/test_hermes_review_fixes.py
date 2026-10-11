"""Findings from the Hermes Agent catalog review (2026-10-04), each with a planted failure.

A Hermes maintainer reviewed ContentForge 4.3.1 for catalog listing and asked for:

  S1  no package installed behind the user's back (an unpinned `pip install` ran
      from the pipeline whenever python-docx was missing)
  S2  `${CLAUDE_PLUGIN_ROOT}` is not defined on Hermes, so a skill command became
      `python /scripts/...` - every skill that uses it now says where the scripts are
  S3  names that arrive from outside must not choose a path: an Airtable
      attachment called `../../x` wrote outside its temp folder, a `--run-id` of
      `../..` named any directory, a raw `--brand` selected any existing folder
  S4  PRIVACY.md must list what really runs (the C2PA timestamp request, the
      pinned optional installs)
  S5  the throwaway C2PA dev signing key must not outlive the call
  C1  the brand-site harvester must stay on public addresses and on the site

Every check is exercised on a good input AND on the failing input it exists to
catch. Stdlib only (generate-docx's key test also needs `cryptography`, and
skips without it).
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import _common  # noqa: E402


def load(filename: str, modname: str):
    spec = importlib.util.spec_from_file_location(modname, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSafeChild(unittest.TestCase):
    BAD = ["../x", "..", ".", "a/b", "/abs/path", "C:\\win\\x", "..\\..\\x", "a\\b", "",
           "x:stream", "nul\x00byte", "C:", "//server/share"]

    def test_plain_names_pass_and_stay_inside(self):
        with tempfile.TemporaryDirectory() as d:
            for good in ("attachment.docx", "run-1", "My Brand"):
                p = _common.safe_child(d, good)
                self.assertEqual(p.parent, Path(d).resolve())

    def test_every_escaping_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in self.BAD:
                with self.subTest(name=bad), self.assertRaises(ValueError):
                    _common.safe_child(d, bad)

    def test_a_symlink_that_points_out_is_rejected(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            link = Path(d) / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks need privileges on this platform")
            with self.assertRaises(ValueError):
                _common.safe_child(d, "link")

    def test_plant_a_naive_join_would_have_escaped(self):
        with tempfile.TemporaryDirectory() as d:
            naive = (Path(d) / "../escaped.docx").resolve()
            self.assertNotEqual(naive.parent, Path(d).resolve())   # what the old code allowed
            with self.assertRaises(ValueError):
                _common.safe_child(d, "../escaped.docx")


class TestBrandDirLegacyBranch(unittest.TestCase):
    def test_raw_names_that_leave_the_home_are_ignored(self):
        with tempfile.TemporaryDirectory() as parent:
            home = Path(parent) / "home"
            outside = Path(parent) / "outside"
            home.mkdir()
            outside.mkdir()
            with mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": str(home)}):
                for raw in ("../outside", str(outside), "..\\outside", ".."):
                    with self.subTest(raw=raw):
                        got = _common.brand_dir(raw).resolve()
                        self.assertNotEqual(got, outside.resolve())
                        self.assertEqual(got.parent, home.resolve())

    def test_a_real_legacy_directory_is_still_used(self):
        with tempfile.TemporaryDirectory() as parent:
            home = Path(parent)
            (home / "Acme Corp").mkdir()
            with mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": str(home)}):
                self.assertEqual(_common.brand_dir("Acme Corp"), home / "Acme Corp")


class TestRunIdContainment(unittest.TestCase):
    GOOD = "20261010-120000-ai-in-pharma"
    BAD = ["../..", "/etc", "20261010-120000-x/../..", "..\\..", "20261010-120000-a.b", "20261010-120000-a:b",
           "20261010-120000-a/b", "", None, "x"]

    def test_validate_run_id(self):
        self.assertEqual(_common.validate_run_id(self.GOOD), self.GOOD)
        # a non-Latin topic gives a legitimate Unicode slug (the first draft of this rule rejected it)
        unicode_id = "20261010-120000-ai-in-pharma-テスト"
        self.assertEqual(_common.validate_run_id(unicode_id), unicode_id)
        for bad in self.BAD:
            with self.subTest(run_id=bad), self.assertRaises(ValueError):
                _common.validate_run_id(bad)

    def test_checkpoint_actions_refuse_a_traversal_id_and_delete_nothing(self):
        cp = load("checkpoint-manager.py", "cf_checkpoint")
        with tempfile.TemporaryDirectory() as parent:
            home = Path(parent) / "home"
            home.mkdir()
            sentinel = Path(parent) / "keep-me"
            sentinel.mkdir()
            (sentinel / "file.txt").write_text("precious", encoding="utf-8")
            with mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": str(home)}):
                made = cp.init_run("acme", "topic", None)
                self.assertTrue(Path(made["path"]).is_dir())
                for bad in ("../../keep-me", str(sentinel), "..\\..\\keep-me"):
                    with self.subTest(run_id=bad):
                        self.assertIn("error", cp.discard_run("acme", bad))
                        with self.assertRaises(ValueError):
                            cp.get_status("acme", bad)
                        with self.assertRaises(ValueError):
                            cp.save_phase("acme", bad, "1", "x", "md")
            self.assertEqual((sentinel / "file.txt").read_text(encoding="utf-8"), "precious")

    def test_drive_sync_state_turns_a_bad_id_into_a_clean_error(self):
        ds = load("drive-sync-state.py", "cf_drive_sync")
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": home}):
            out = ds._guarded(ds.add_pending_upload, "acme", "../..", "phase-1.md")
            self.assertIn("error", out)
            self.assertNotIn("Traceback", str(out))
            ok = ds._guarded(ds.add_pending_upload, "acme", "20261010-120000-topic", "phase-1.md")
            self.assertNotIn("error", ok)


class TestAirtableAttachmentDownload(unittest.TestCase):
    """Runs inside a sandbox: tempfile's base directory is a throwaway folder and every hostile name
    points at a sandbox location, so even a regression that brings the old bug back can only write
    inside the sandbox (an earlier draft of this test, run against the old code, wrote real files
    outside the temp folder)."""

    def setUp(self):
        self.bm = load("backend-migrator.py", "cf_backend_migrator")
        self._sandbox = tempfile.TemporaryDirectory()
        self.sandbox = Path(self._sandbox.name).resolve()
        self.tmp_base = self.sandbox / "tmp"
        self.outside = self.sandbox / "outside"
        self.tmp_base.mkdir()
        self.outside.mkdir()
        self._patch = mock.patch.object(tempfile, "tempdir", str(self.tmp_base))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._sandbox.cleanup()

    def _download(self, filename, url="https://v5.airtableusercontent.com/x/file"):
        record = {"output_file": [{"url": url, "filename": filename}]}

        class _Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        with mock.patch.object(self.bm, "urlopen", lambda *a, **k: _Resp(b"docx-bytes")):
            return self.bm.download_airtable_attachment(record)

    def _written_outside_the_download_folder(self, download_dir=None):
        found = [p for p in self.sandbox.rglob("*") if p.is_file()]
        return [p for p in found if download_dir is None or download_dir not in p.parents]

    def test_hostile_file_names_land_inside_the_temp_folder(self):
        bs = chr(92)   # a backslash, spelled out so no escape sequence can turn it into something else
        hostile = ["../../evil.docx", f"..{bs}..{bs}win-evil.docx", "..", "",
                   str(self.outside / "absolute.docx"),
                   str(self.outside).replace("/", bs) + bs + "backslash-abs.docx"]
        for name in hostile:
            with self.subTest(filename=name):
                path, err = self._download(name)
                self.assertIsNone(err)
                p = Path(path).resolve()
                self.assertTrue(p.parent.name.startswith("cf_migrate_"))
                self.assertEqual(p.parent.parent, self.tmp_base.resolve())
                self.assertEqual(p.read_bytes(), b"docx-bytes")
                self.assertEqual(self._written_outside_the_download_folder(p.parent), [])
                shutil.rmtree(p.parent)

    def test_a_non_https_url_is_refused(self):
        for url in ("file:///etc/passwd", "ftp://example.com/x", "http://example.com/x"):
            with self.subTest(url=url):
                path, err = self._download("x.docx", url=url)
                self.assertIsNone(path)
                self.assertIn("not https", err)
        self.assertEqual(list(self.tmp_base.iterdir()), [])

    def test_a_full_migration_leaves_no_download_folder_behind(self):
        record = {"requirement_id": "REQ-001", "title": "A Title",
                  "output_file": [{"url": "https://v5.airtableusercontent.com/x/f", "filename": "../../evil.docx"}]}

        class _Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        args = types.SimpleNamespace(brand="acme", from_backend="airtable", to_backend="local", base_id="appX",
                                     table="t", sheet_id=None, credentials=None, folder_id=None)
        with mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": str(self.sandbox / "home")}),                 mock.patch.object(self.bm, "read_airtable", lambda *a, **k: ([record], None)),                 mock.patch.object(self.bm, "urlopen", lambda *a, **k: _Resp(b"docx-bytes")):
            result = self.bm.migrate_records(args)
        self.assertEqual(result.get("records_migrated"), 1, result)
        self.assertEqual(result.get("files_migrated"), 1, result)
        self.assertEqual([p.name for p in self.tmp_base.iterdir()], [], "download folder was not removed")
        copied = [p for p in (self.sandbox / "home").rglob("*.docx")]
        self.assertEqual(len(copied), 1)
        self.assertEqual([p for p in self.sandbox.rglob("evil.docx")], [])

    def test_cleanup_removes_only_its_own_temp_folder(self):
        path, _ = self._download("report.docx")
        self.assertTrue(Path(path).exists())
        self.bm._cleanup_download(path, "airtable")
        self.assertFalse(Path(path).parent.exists())
        keep = self.outside / "f.txt"
        keep.write_text("x", encoding="utf-8")
        self.bm._cleanup_download(str(keep), "airtable")      # not a cf_migrate_ dir
        self.bm._cleanup_download(str(keep), "local")          # not an airtable download
        self.assertTrue(keep.exists())


class TestNoInstallBehindTheUsersBack(unittest.TestCase):
    def test_default_installs_nothing_and_prints_the_pinned_command(self):
        with mock.patch.dict(os.environ, {}, clear=False), mock.patch("subprocess.check_call") as call:
            os.environ.pop(_common.INSTALL_OPT_IN_ENV, None)
            err = _common.pip_install(["python-docx>=1.1.0"], label="python-docx")
        call.assert_not_called()
        self.assertIn("error", err)
        pin = f"python-docx=={_common.PINNED_DEPENDENCIES['python-docx']}"
        self.assertIn(pin, err["recovery"])
        self.assertIn("-m pip install", err["recovery"])
        self.assertNotIn(">=", err["recovery"])

    def test_explicit_opt_in_runs_exactly_the_pinned_command(self):
        with mock.patch.dict(os.environ, {_common.INSTALL_OPT_IN_ENV: "1"}), \
                mock.patch("subprocess.check_call") as call:
            self.assertIsNone(_common.pip_install(["c2pa-python>=0.32", "cryptography"]))
        args = call.call_args[0][0]
        self.assertEqual(args[1:5], ["-m", "pip", "install", "-q"])
        self.assertEqual(args[5:], [f"c2pa-python=={_common.PINNED_DEPENDENCIES['c2pa-python']}",
                                    f"cryptography=={_common.PINNED_DEPENDENCIES['cryptography']}"])

    def test_any_other_value_is_not_consent(self):
        for v in ("0", "yes", "true", ""):
            with self.subTest(value=v), mock.patch.dict(os.environ, {_common.INSTALL_OPT_IN_ENV: v}), \
                    mock.patch("subprocess.check_call") as call:
                self.assertIn("error", _common.pip_install(["gspread"]))
                call.assert_not_called()

    def test_an_unpinned_package_is_refused(self):
        with self.assertRaises(ValueError):
            _common.pip_install(["some-unpinned-package"])

    def test_every_pins_entry_is_exact(self):
        for name, ver in _common.PINNED_DEPENDENCIES.items():
            self.assertRegex(ver, r"^\d+(\.\d+)+$", name)

    def test_no_script_installs_on_its_own(self):
        offenders = []
        for p in sorted(SCRIPTS.glob("*.py")):
            if p.name == "_common.py":
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r'["\']pip["\']\s*,\s*["\']install["\']', text) or "ensurepip" in text:
                offenders.append(p.name)
            for m in re.finditer(r"pip_install\(\s*\[([^\]]*)\]", text):
                for pkg in re.findall(r'"([^"]+)"', m.group(1)):
                    try:
                        _common.pinned_specs([pkg])
                    except ValueError:
                        offenders.append(f"{p.name}: {pkg} is not pinned")
        self.assertEqual(offenders, [])

    def test_plant_the_scan_catches_a_raw_pip_call(self):
        sample = 'subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])'
        self.assertTrue(re.search(r'["\']pip["\']\s*,\s*["\']install["\']', sample))


class TestDevSigningKeyIsDeleted(unittest.TestCase):
    def test_throwaway_key_folder_is_removed(self):
        try:
            import cryptography  # noqa: F401
        except ImportError:
            self.skipTest("cryptography not installed")
        gd = load("generate-docx.py", "cf_generate_docx")

        class _Builder:
            @staticmethod
            def get_supported_mime_types():
                return []          # forces the sidecar path after the key is generated

        fake = types.ModuleType("c2pa")
        fake.Builder = _Builder
        created = []
        real_mkdtemp = tempfile.mkdtemp

        def spy(*a, **k):
            d = real_mkdtemp(*a, **k)
            created.append(d)
            return d

        with tempfile.TemporaryDirectory() as out_dir:
            out = Path(out_dir) / "piece.docx"
            out.write_bytes(b"PK")
            args = types.SimpleNamespace(c2pa_sign=True, brand="Acme", content_type="article",
                                         c2pa_signing_cert=None, c2pa_signing_key=None)
            with mock.patch.dict(sys.modules, {"c2pa": fake}), mock.patch("tempfile.mkdtemp", spy):
                result = gd._maybe_c2pa_sign_docx(out, args, "A title")
            sidecar = json.loads(out.with_suffix(".c2pa.json").read_text(encoding="utf-8"))
            created_actions = [act for a_ in sidecar["assertions"] if a_["label"].startswith("c2pa.actions")
                               for act in a_["data"]["actions"] if act["action"] == "c2pa.created"]
            # c2pa-python >= 0.38 rejects a c2pa.created action without its own digitalSourceType
            self.assertEqual(len(created_actions), 1)
            self.assertTrue(created_actions[0].get("digitalSourceType", "").startswith("http://cv.iptc.org/newscodes/digitalsourcetype/"))
        self.assertTrue(result and result.get("c2pa_signed"), result)
        dev = [d for d in created if os.path.basename(d).startswith("cf-c2pa-")]
        self.assertEqual(len(dev), 1, "the dev key folder was never created, so this test proves nothing")
        self.assertFalse(os.path.exists(dev[0]), "dev signing key folder survived the call")


class TestHarvesterStaysPublicAndOnSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = load("harvest-brand-pages.py", "cf_harvest")

    def test_non_public_and_non_http_targets_are_refused(self):
        for url in ("http://127.0.0.1/", "http://10.0.0.5/x", "http://192.168.1.1/", "http://169.254.169.254/latest/meta-data/",
                    "http://[::1]/", "http://0.0.0.0/", "file:///etc/passwd", "ftp://93.184.216.34/x", "gopher://93.184.216.34/",
                    "http:///nohost", ""):
            with self.subTest(url=url):
                self.assertFalse(self.h.url_is_fetchable(url))
                self.assertEqual(self.h.fetch(url, 1.0), (0, ""))

    def test_a_public_address_passes(self):
        self.assertTrue(self.h.url_is_fetchable("https://93.184.216.34/page"))

    def test_a_redirect_to_an_internal_address_is_refused(self):
        handler = self.h._GuardedRedirect()
        req = mock.Mock(full_url="https://93.184.216.34/start")
        for target in ("http://169.254.169.254/latest/", "file:///etc/passwd", "http://10.0.0.5/admin"):
            with self.subTest(target=target), self.assertRaisesRegex(urllib.error.URLError, "non-public or non-http"):
                handler.redirect_request(req, None, 302, "Found", {}, target)

    def test_same_site_filter_for_declared_sitemaps(self):
        root = "https://example.com"
        self.assertTrue(self.h.same_site(root, "https://www.example.com/sitemap.xml"))
        self.assertFalse(self.h.same_site(root, "https://evil.test/sitemap.xml"))
        self.assertFalse(self.h.same_site(root, "https://example.com.evil.test/sitemap.xml"))


class TestScriptRootFallback(unittest.TestCase):
    SENTENCE = ("If your host does not set `${CLAUDE_PLUGIN_ROOT}`, the scripts are in this plugin's "
                "`scripts/` folder, next to `skills/`. Run them with Python 3.10 or newer: `python`, or "
                "`python3` where `python` is not found (macOS, many Linux systems).")

    @staticmethod
    def missing(text: str, sentence: str) -> bool:
        return "CLAUDE_PLUGIN_ROOT" in text and sentence not in text

    @staticmethod
    def files():
        return (sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("commands/*.md"))
                + sorted(ROOT.glob("agents/*.md")))

    def test_every_skill_command_and_agent_that_uses_the_variable_says_where_the_scripts_are(self):
        files = self.files()
        bad = [str(p.relative_to(ROOT)) for p in files
               if self.missing(p.read_text(encoding="utf-8", errors="replace"), self.SENTENCE)]
        self.assertEqual(bad, [])

    def test_plant_a_skill_without_the_sentence_is_flagged(self):
        self.assertTrue(self.missing("run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`", self.SENTENCE))
        # the scan reaches the agents (4.5.3): the five that use the variable are in it, and an agent-shaped plant is flagged
        agents = {p.name for p in self.files() if p.parent.name == "agents" and "CLAUDE_PLUGIN_ROOT" in p.read_text(encoding="utf-8", errors="replace")}
        self.assertGreaterEqual(len(agents), 5, agents)
        self.assertTrue(self.missing("---\nname: reviewer\n---\n# Reviewer Agent\n\nRun `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`.", self.SENTENCE))
        self.assertFalse(self.missing("run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`\n" + self.SENTENCE, self.SENTENCE))
        self.assertFalse(self.missing("no variable here", self.SENTENCE))

    def test_plant_the_one_line_sentence_of_4_5_2_is_flagged(self):
        """Before 4.5.3 the line stopped at the folder and said nothing about which Python to run."""
        old = "If your host does not set `${CLAUDE_PLUGIN_ROOT}`, the scripts are in this plugin's `scripts/` folder, next to `skills/`."
        self.assertTrue(self.missing("run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`\n" + old, self.SENTENCE))
        self.assertIn("`python`", self.SENTENCE)


class TestNoPython3AsTheCommand(unittest.TestCase):
    """4.5.3: `python3` often does not resolve on Windows, so a skill, command, agent or doc that tells the host to run it
    fails there. They run Python as `python`; the script-location line says to fall back to `python3` where `python` is
    not found. (SocialForge had 28 uses until its 1.29.3.)"""
    COMMAND = re.compile(r"(?<![\w/.-])python3(?=\s+[\w\"'$./-])")

    @classmethod
    def files(cls):
        out = sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("commands/*.md")) + sorted(ROOT.glob("agents/*.md"))
        return out + [ROOT / "README.md", ROOT / "SUBMISSION.md", ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"] + sorted(ROOT.glob("docs/*.md"))

    def test_no_instruction_file_or_doc_runs_python3(self):
        files = self.files()
        self.assertGreater(len(files), 40, "the scan found too few files; the guard is vacuous")
        bad = []
        for p in files:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if self.COMMAND.search(line):
                    bad.append("%s:%d" % (p.relative_to(ROOT).as_posix(), i))
        self.assertEqual(bad, [])

    def test_plant_the_old_commands_are_flagged_and_the_fallback_sentence_is_not(self):
        self.assertTrue(self.COMMAND.search("python3 scripts/generate-docx.py --brand acme"))
        self.assertTrue(self.COMMAND.search("`python3 scripts/<script>.py --help` exits 0"))
        self.assertFalse(self.COMMAND.search("python scripts/generate-docx.py --brand acme"))
        self.assertFalse(self.COMMAND.search(TestScriptRootFallback.SENTENCE))


class TestScriptInvocationsAreRobust(unittest.TestCase):
    """A fresh-install smoke test found files that run scripts by a path that only works from one folder: `python scripts/x.py`
    resolves against the host's working directory (the user's project, not the plugin), and an unquoted
    `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py` breaks when the plugin is installed under a path with a space. This guard
    DISCOVERS every skill, command, agent and reference file that runs a script and requires (1) the script-location line,
    (2) no relative `scripts/` invocation, (3) every `${CLAUDE_PLUGIN_ROOT}` script path quoted."""

    RUN = re.compile(r"(?<![\w/.-])python\s+(?:-\w+\s+)*[\"']?(?:\./)?(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?scripts/[\w./-]+")
    RELATIVE = re.compile(r"(?<![\w/.-])python\s+(?:-\w+\s+)*[\"']?(?:\./)?scripts/")
    UNQUOTED = re.compile(r"(?<![\w/.-])python\s+(?:-\w+\s+)*\$\{CLAUDE_PLUGIN_ROOT\}/")
    EXEMPT = {}

    # Discovery is inverted: every markdown file is covered unless it is contributor documentation that runs from a repository
    # clone (where a relative `python scripts/x.py` is right). A folder added tomorrow (the way utils/ was missed) is covered by default.
    EXCLUDED_DIRS = {"docs", "tests", "research", "evals", "node_modules", "hermes", "heroes", "__pycache__"}
    EXCLUDED_FILES = {"CHANGELOG.md", "CONTRIBUTING.md", "TESTING-GUIDE.md", "TESTING.md", "SUBMISSION.md", "UPGRADE-GUIDE.md"}

    @classmethod
    def files(cls) -> dict:
        out = {}
        for dirpath, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in cls.EXCLUDED_DIRS and not d.startswith(".")]
            for name in sorted(names):
                if name.endswith(".md") and name not in cls.EXCLUDED_FILES and not name.startswith("README"):
                    p = Path(dirpath) / name
                    out[p.relative_to(ROOT).as_posix()] = p.read_text(encoding="utf-8", errors="replace")
        return out

    @classmethod
    def docs_files(cls) -> dict:
        """docs/ is excluded above (maintainer scripts run from a clone), but a command a person or a model copies from it must still
        survive a plugin folder with a space in its name."""
        return {p.relative_to(ROOT).as_posix(): p.read_text(encoding="utf-8", errors="replace") for p in sorted((ROOT / "docs").glob("**/*.md"))}

    @classmethod
    def problems(cls, files: dict, exempt: dict = None) -> list:
        exempt = cls.EXEMPT if exempt is None else exempt
        out = []
        for rel, text in files.items():
            if rel in exempt:
                continue
            lines = text.splitlines()
            if any(cls.RUN.search(l) for l in lines) and TestScriptRootFallback.SENTENCE not in text:
                out.append(rel + ": runs a script but has no script-location line")
            for n, l in enumerate(lines, 1):
                if cls.RELATIVE.search(l):
                    out.append("%s:%d: runs a script by a relative path" % (rel, n))
                if cls.UNQUOTED.search(l):
                    out.append("%s:%d: the ${CLAUDE_PLUGIN_ROOT} script path is not quoted" % (rel, n))
        return out

    def test_every_file_that_runs_a_script_invokes_it_robustly(self):
        files = self.files()
        running = [r for r, t in files.items() if any(self.RUN.search(l) for l in t.splitlines())]
        self.assertGreaterEqual(len(running), 10, "the discovery found too few files; the guard is vacuous")
        self.assertEqual(self.problems(files), [])

    def test_docs_quote_the_plugin_root_script_path(self):
        bad = ["%s:%d" % (rel, n) for rel, text in self.docs_files().items() for n, line in enumerate(text.splitlines(), 1)
               if self.UNQUOTED.search(line)]
        self.assertEqual(bad, [])
        self.assertTrue(self.UNQUOTED.search("python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py --a"))   # the plant
        self.assertFalse(self.UNQUOTED.search('python "${CLAUDE_PLUGIN_ROOT}/scripts/x.py" --a'))

    def test_every_exemption_is_a_real_file_with_a_reason(self):
        files = self.files()
        for rel, why in self.EXEMPT.items():
            with self.subTest(file=rel):
                self.assertIn(rel, files)
                self.assertGreater(len(why), 20)

    def test_plant_each_of_the_three_defects_is_flagged(self):
        line = "> **Script location.** " + TestScriptRootFallback.SENTENCE
        good = "# T\n\n" + line + "\n\n```bash\npython \"${CLAUDE_PLUGIN_ROOT}/scripts/x.py\" --a 1\n```\n"
        self.assertEqual(self.problems({"skills/t/SKILL.md": good}, exempt={}), [])
        call = 'python "${CLAUDE_PLUGIN_ROOT}/scripts/x.py"'
        planted = {
            "relative": (good.replace(call, "python scripts/x.py"), "relative path"),
            "unquoted": (good.replace(call, "python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py"), "not quoted"),
            "no line": (good.replace(line, ""), "no script-location line"),
        }
        for name, (text, needle) in planted.items():
            with self.subTest(defect=name):
                found = self.problems({"skills/t/SKILL.md": text}, exempt={})
                self.assertTrue(any(needle in f for f in found), found)

    def test_discovery_reaches_a_supporting_file_inside_a_skill_folder(self):
        """A supporting file that sits directly in a skill folder (not SKILL.md, not references/) is a file too: a SocialForge
        one ran `python scripts/install_deps.py` by a relative path with no location line and the narrower scan could not see it."""
        old_loop_tracker = ("# Loop tracker\n\n- On each loop run `python scripts/checkpoint-manager.py loop --brand {brand} --run-id {run_id}`.\n")
        found = self.problems({"utils/loop-tracker.md": old_loop_tracker}, exempt={})
        self.assertTrue(any("relative path" in f for f in found) and any("no script-location line" in f for f in found), found)
        # inverted discovery: the folders the old globs missed are scanned, and so is the repository root
        files = self.files()
        self.assertIn("utils/loop-tracker.md", files)
        self.assertIn("AGENTS.md", files)
        self.assertNotIn("CHANGELOG.md", files)
        self.assertFalse(any(rel.startswith("docs/") for rel in files))


class TestScriptsPrintAbsoluteCommands(unittest.TestCase):
    """4.5.5: checkpoint-manager.py printed "Run: python scripts/run-audit.py ...", which is relative to the host's working folder,
    not the plugin. A command a script tells someone to run comes from _common.script_command: the running interpreter and the
    script's absolute path. Docstrings (usage text) are not output and are left alone."""
    HINT = re.compile(r"\bpython3?\s+(?:\./)?scripts/")

    @classmethod
    def findings(cls, source: str, name: str = "x.py") -> list:
        import ast
        tree = ast.parse(source)
        docstrings = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
                first = node.body[0]
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                    docstrings.add(id(first.value))
        return ["%s:%d" % (name, n.lineno) for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings and cls.HINT.search(n.value)]

    def test_no_script_prints_a_relative_python_scripts_command(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        self.assertGreater(len(scripts), 20, "the scan found too few scripts; the guard is vacuous")
        bad = [f for p in scripts for f in self.findings(p.read_text(encoding="utf-8"), p.name)]
        self.assertEqual(bad, [])

    def test_plant_the_old_hints_are_flagged_and_usage_text_and_the_helper_are_not(self):
        old = 'def f():\n    return {"recovery": "Run: python scripts/run-audit.py --brand " f"{brand}"}\n'
        old_fstring = 'def g(brand):\n    return f"Re-run: python scripts/run-audit.py --brand {brand}"\n'
        usage = '"""Usage:\n    python scripts/setup.py\n"""\n\ndef h():\n    """Run python scripts/x.py"""\n    return 1\n'
        fixed = 'def f():\n    return {"recovery": "Run: " + _common.script_command("run-audit.py")}\n'
        self.assertEqual(len(self.findings(old)), 1)
        self.assertEqual(len(self.findings(old_fstring)), 1)
        self.assertEqual(self.findings(usage), [])
        self.assertEqual(self.findings(fixed), [])

    def test_script_command_is_the_running_interpreter_and_the_absolute_script(self):
        sys.path.insert(0, str(SCRIPTS))
        import _common
        cmd = _common.script_command("plugin-metadata.py", "--section", "version")
        self.assertTrue((SCRIPTS / "plugin-metadata.py").exists())
        self.assertIn('"%s"' % (SCRIPTS / "plugin-metadata.py").as_posix(), cmd)   # forward slashes, double-quoted
        self.assertNotIn("\\", cmd)                                         # bash drops a backslash
        self.assertNotIn("python scripts/", cmd)

    def test_the_command_shape_without_and_with_a_space_in_the_interpreter_path(self):
        """Pasted into Git Bash a backslash path arrived as `C:Python313python.exe` (exit 127), and a quoted first token is a string
        literal in PowerShell: forward slashes, the script always double-quoted, the interpreter quoted only when it has a space."""
        sys.path.insert(0, str(SCRIPTS))
        import _common
        from unittest import mock
        with mock.patch.object(sys, "executable", "C:\\Python313\\python.exe"):
            plain = _common.script_command("x.py", "--a", "1")
        self.assertTrue(plain.startswith('C:/Python313/python.exe "'), plain)
        self.assertTrue(plain.endswith('/scripts/x.py" --a 1'), plain)
        self.assertNotIn("PowerShell", plain)
        with mock.patch.object(sys, "executable", "C:\\Program Files\\Python313\\python.exe"):
            spaced = _common.script_command("x.py", "--a", "1")
        self.assertTrue(spaced.startswith('"C:/Program Files/Python313/python.exe" "'), spaced)
        self.assertTrue(spaced.endswith("--a 1  # in PowerShell, put & before it"), spaced)
        self.assertNotIn("\\", plain + spaced)

    def _runnable(self):
        sys.path.insert(0, str(SCRIPTS))
        import _common
        return _common.script_command("plugin-metadata.py", "--section", "version").split("  # in PowerShell")[0]

    def test_the_command_runs_pasted_into_git_bash_from_another_folder(self):
        import shutil
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("no bash on PATH")
        kernel = subprocess.run([bash, "-c", "uname -s"], capture_output=True, text=True).stdout
        if sys.platform == "win32" and not any(k in kernel for k in ("MINGW", "MSYS", "CYGWIN")):
            self.skipTest("this bash is not Git Bash (WSL cannot run a Windows interpreter path)")
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([bash, "-c", self._runnable()], capture_output=True, text=True, cwd=d, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("version", r.stdout)

    def test_the_command_runs_pasted_into_powershell_from_another_folder(self):
        import shutil
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if not ps:
            self.skipTest("no PowerShell on PATH")
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", self._runnable()], capture_output=True, text=True, cwd=d, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("version", r.stdout)

    def _spaced_line(self):
        sys.path.insert(0, str(SCRIPTS))
        import _common
        from unittest import mock
        with mock.patch.object(sys, "executable", "C:\\Program Files\\Python313\\python.exe"):
            return _common.script_command("plugin-metadata.py", "--section", "version")

    def test_the_space_case_line_parses_in_git_bash(self):
        """The note was first a parenthetical after the arguments, which bash rejects (`syntax error near unexpected token '('`).
        A trailing comment is ignored by bash and by PowerShell."""
        import shutil
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("no bash on PATH")
        kernel = subprocess.run([bash, "-c", "uname -s"], capture_output=True, text=True).stdout
        if sys.platform == "win32" and not any(k in kernel for k in ("MINGW", "MSYS", "CYGWIN")):
            self.skipTest("this bash is not Git Bash (WSL cannot parse a Windows interpreter path)")
        line = self._spaced_line()
        self.assertTrue(line.startswith('"C:/Program Files/'), line)
        ok = subprocess.run([bash, "-n", "-c", line], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, line + "\n" + ok.stderr)
        parenthetical = line.split("  # in PowerShell")[0] + " (in PowerShell, put & before it)"
        bad = subprocess.run([bash, "-n", "-c", parenthetical], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0, "the parenthetical form must fail `bash -n`, or this guard proves nothing")

    def test_the_space_case_line_runs_in_powershell_with_an_ampersand_and_not_without_one(self):
        import shutil
        ps = shutil.which("powershell") or shutil.which("pwsh")
        if not ps or sys.platform != "win32":
            self.skipTest("needs Windows PowerShell (the interpreter stand-in is a .cmd file in a folder with a space)")
        sys.path.insert(0, str(SCRIPTS))
        import _common
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            shim_dir = Path(d) / "dir with space"
            shim_dir.mkdir()
            shim = shim_dir / "pyshim.cmd"
            shim.write_text('@echo off\r\n"%s" %%*\r\n' % sys.executable, encoding="ascii")
            with mock.patch.object(sys, "executable", str(shim).replace("\\", "/")):
                line = _common.script_command("plugin-metadata.py", "--section", "version")
            self.assertTrue(line.startswith('"'), line)
            run = lambda command: subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", command],
                                                 capture_output=True, text=True, cwd=d, timeout=180)
            with_amp, without = run("& " + line), run(line)
        self.assertEqual(with_amp.returncode, 0, with_amp.stdout + with_amp.stderr)
        self.assertIn("version", with_amp.stdout)
        self.assertNotEqual(without.returncode, 0, "without `&` PowerShell reads the quoted path as a string")


class TestAgentWrittenInputsAcceptABom(unittest.TestCase):
    """4.5.5: PowerShell 5.1 writes a UTF-8 byte-order mark by default (Out-File, Set-Content -Encoding utf8), and Notepad often does.
    A BOM made `audit-ledger.py validate --file` fail with "cannot read" before it reached validation, and made `authorship.py` report
    the author's first sentence as rewritten (a false violation that blocks the run). Inputs an agent or a user writes are read with
    utf-8-sig, which reads plain UTF-8 unchanged; the shared JSON loader included. Files whose bytes are hashed on purpose
    (fix-ledger, run-audit, checkpoint content) and files the plugin writes and reads itself are not touched."""
    EXTERNAL = re.compile(r"\b(?:src_path|draft_path|content_path|MCP_JSON|mcp_path|creds_file|GOOGLE_CREDS_DEFAULT|Path\(args\.reports\))\.read_text\(encoding=\"utf-8\"")

    def test_no_script_reads_an_agent_or_user_written_input_without_allowing_a_bom(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        bad = ["%s:%d" % (p.name, n) for p in scripts for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
               if self.EXTERNAL.search(line)]
        self.assertEqual(bad, [])
        self.assertIn("utf-8-sig", (SCRIPTS / "_common.py").read_text(encoding="utf-8"))   # the shared loader

    def test_plant_the_old_reads_are_flagged_and_the_fix_is_not(self):
        self.assertTrue(self.EXTERNAL.search('result = classify(src_path.read_text(encoding="utf-8"),'))
        self.assertTrue(self.EXTERNAL.search('md_text = content_path.read_text(encoding="utf-8")'))
        self.assertFalse(self.EXTERNAL.search('md_text = content_path.read_text(encoding="utf-8-sig")'))
        self.assertFalse(self.EXTERNAL.search('text = artifact.read_text(encoding="utf-8")'))

    def test_the_shared_loader_reads_a_bom_file_like_the_plain_one(self):
        sys.path.insert(0, str(SCRIPTS))
        import _common
        body = '{"brand": "acme", "pieces": []}'
        with tempfile.TemporaryDirectory() as d:
            plain, bom = Path(d) / "plain.json", Path(d) / "bom.json"
            plain.write_text(body, encoding="utf-8")
            bom.write_bytes(b"\xef\xbb\xbf" + body.encode("utf-8"))
            self.assertNotIn("error", _common.load_json_safe(plain))
            self.assertEqual(_common.load_json_safe(bom), _common.load_json_safe(plain))

    def _run(self, *args):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home, USERPROFILE=home, CLAUDE_PLUGIN_DATA=home, CLAUDE_MARKETING_HOME=home)
            return subprocess.run([sys.executable, *args], capture_output=True, text=True, env=env, timeout=120)

    def test_audit_ledger_validate_reaches_validation_with_a_bom(self):
        with tempfile.TemporaryDirectory() as d:
            plain, bom = Path(d) / "plain.json", Path(d) / "bom.json"
            plain.write_text('{"brand": "acme"}', encoding="utf-8")
            bom.write_bytes(b"\xef\xbb\xbf" + b'{"brand": "acme"}')
            a = self._run(str(SCRIPTS / "audit-ledger.py"), "validate", "--file", str(plain))
            b = self._run(str(SCRIPTS / "audit-ledger.py"), "validate", "--file", str(bom))
        self.assertEqual(a.returncode, 1, a.stdout + a.stderr)      # the file is read and fails validation, as it should
        self.assertEqual((b.returncode, b.stdout), (a.returncode, a.stdout), b.stdout + b.stderr)

    def test_text_metrics_flags_the_same_sentences_with_a_bom(self):
        """The mark used to be echoed into the first flagged sentence, and a sentence that starts with it no longer opens with its connective."""
        text = "Moreover, the numbers improved across the board. We shipped the new flow in March.\n\nFurthermore, support tickets fell."
        with tempfile.TemporaryDirectory() as d:
            plain, bom = Path(d) / "plain.md", Path(d) / "bom.md"
            plain.write_bytes(text.encode("utf-8"))
            bom.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
            a = self._run(str(SCRIPTS / "text-metrics.py"), "--file", str(plain), "--ai-tell-scan")
            b = self._run(str(SCRIPTS / "text-metrics.py"), "--file", str(bom), "--ai-tell-scan")
        self.assertEqual((a.returncode, b.returncode), (0, 0), a.stderr + b.stderr)

        def flagged(out):
            def walk(o):
                if isinstance(o, dict):
                    if "flagged_sentences" in o:
                        return o["flagged_sentences"]
                    for v in o.values():
                        r = walk(v)
                        if r is not None:
                            return r
                return None
            return [s["text"] for s in walk(json.loads(out))]
        fa, fb = flagged(a.stdout), flagged(b.stdout)
        self.assertTrue(fa, "the sample must flag a sentence for the comparison to mean anything")
        self.assertEqual(fb, fa)
        self.assertFalse(any("\ufeff" in s for s in fb))

    def test_a_bom_on_the_authors_draft_is_not_a_rewritten_sentence(self):
        author = "We shipped the new onboarding flow in March and activation rose from 31 to 38 percent. The team credits the clearer checklist.\n\nSupport tickets fell by a fifth."
        with tempfile.TemporaryDirectory() as d:
            plain, bom, draft = Path(d) / "src-plain.md", Path(d) / "src-bom.md", Path(d) / "draft.md"
            plain.write_bytes(author.encode("utf-8"))
            bom.write_bytes(b"\xef\xbb\xbf" + author.encode("utf-8"))
            draft.write_bytes(author.encode("utf-8"))
            a = self._run(str(SCRIPTS / "authorship.py"), "--source", str(plain), "--draft", str(draft))
            b = self._run(str(SCRIPTS / "authorship.py"), "--source", str(bom), "--draft", str(draft))
        self.assertEqual(a.returncode, 0, a.stdout + a.stderr)
        self.assertEqual(b.returncode, 0, "a BOM on the author's draft was read as a rewritten sentence:\n" + b.stdout[:600] + b.stderr[:300])
        self.assertEqual(json.loads(b.stdout)["counts"], json.loads(a.stdout)["counts"])


class TestNoTmpPathsInInstructions(unittest.TestCase):
    """/tmp is not one folder on Windows: Git Bash maps it to the user's temp folder while Python resolves it elsewhere, so a
    file the shell wrote was not found by the script and the command stopped. Instructions use a folder the plugin knows."""
    TMP = re.compile(r"(?<![\w.-])/tmp/")

    def test_no_skill_command_agent_or_reference_uses_a_tmp_path(self):
        files = TestScriptInvocationsAreRobust.files()
        self.assertGreater(len(files), 20, "the scan found too few files; the guard is vacuous")
        bad = ["%s:%d" % (rel, n) for rel, text in files.items() for n, l in enumerate(text.splitlines(), 1) if self.TMP.search(l)]
        self.assertEqual(bad, [])

    def test_plant_the_old_path_is_flagged_and_the_replacement_is_not(self):
        self.assertTrue(self.TMP.search("--action quote-batch --items @/tmp/run-plan.json"))
        self.assertTrue(self.TMP.search("write the plan to /tmp/plan.json"))
        self.assertFalse(self.TMP.search("write run-plan.json in the month's output folder, not in /tmp"))
        self.assertFalse(self.TMP.search("--output {tmp}/harvest.json"))


class TestPrivacyListsWhatRuns(unittest.TestCase):
    TEXT = (ROOT / "PRIVACY.md").read_text(encoding="utf-8")

    def test_rows_for_the_timestamp_request_and_the_opt_in_install(self):
        self.assertIn("timestamp.digicert.com", self.TEXT)
        self.assertIn("CONTENTFORGE_INSTALL_DEPS=1", self.TEXT)
        self.assertNotIn("when a backend you chose needs a package and you run its setup", self.TEXT)

    def test_every_pinned_package_is_named_in_the_install_row_or_the_pin_table(self):
        row = next(ln for ln in self.TEXT.splitlines() if "`pip_install`" in ln)
        for name in ("python-docx", "c2pa-python", "cryptography"):
            self.assertIn(name, row)


# ── S3 (sweep): every --run-id and --brand is contained ────────────────

class TestEveryRunIdAndBrandArgumentIsContained(unittest.TestCase):
    # --brand reaches a local path only through _common.brand_dir(), which slugifies the name and honours a
    # raw directory only when it is one plain component (TestBrandDirLegacyBranch). Brand display names may
    # legitimately contain ':' or '/' ("AT&T / Verizon"), so --brand is NOT forced through a strict type.
    VIA_BRAND_DIR = {"audit-ledger.py", "backend-migrator.py", "checkpoint-manager.py", "drive-sync-state.py",
                     "harvest-brand-pages.py", "local-tracker.py", "pipeline-tracker.py", "run-audit.py", "telemetry.py"}
    # Scripts that use --brand but never as a local path, with the reason.
    NOT_A_PATH = {
        "airtable-tracker.py": "row filter for get-pending",
        "sheets-tracker.py": "row filter for get-pending",
        "drive-uploader.py": "name of a Google Drive folder, not a local path",
        "generate-docx.py": "text printed in the document header and the C2PA author field",
    }

    @staticmethod
    def untyped(source: str, flag: str, type_name: str) -> list[str]:
        import ast
        bad = []
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument"
                    and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == flag):
                if not any(k.arg == "type" and ast.unparse(k.value) == type_name for k in node.keywords):
                    bad.append(flag)
        return bad

    def _scripts_declaring(self, flag):
        return {p.name: p.read_text(encoding="utf-8") for p in sorted(SCRIPTS.glob("*.py"))
                if f'"{flag}"' in p.read_text(encoding="utf-8") and "add_argument" in p.read_text(encoding="utf-8")}

    def test_every_run_id_argument_uses_the_validating_type(self):
        scripts = self._scripts_declaring("--run-id")
        self.assertGreaterEqual(len(scripts), 4)
        offenders = {n: self.untyped(src, "--run-id", "_common.run_id_arg") for n, src in scripts.items()
                     if self.untyped(src, "--run-id", "_common.run_id_arg")}
        self.assertEqual(offenders, {})

    def test_every_brand_argument_is_accounted_for(self):
        declaring = set(self._scripts_declaring("--brand"))
        self.assertEqual(declaring, self.VIA_BRAND_DIR | set(self.NOT_A_PATH),
                         "a script declares --brand without being classified: decide how its value reaches a path")

    def test_brand_dir_scripts_really_use_brand_dir_and_the_others_never_build_a_path_from_it(self):
        for name in self.VIA_BRAND_DIR:
            with self.subTest(script=name):
                self.assertIn("_common.brand_dir(", (SCRIPTS / name).read_text(encoding="utf-8"))
        for name in self.NOT_A_PATH:
            src = (SCRIPTS / name).read_text(encoding="utf-8")
            with self.subTest(script=name):
                self.assertNotIn("brand_dir(", src)
                self.assertIsNone(re.search(r"Path\(\s*args\.brand|/\s*args\.brand\b|args\.brand\s*/", src))

    def test_plants(self):
        typed = 'p.add_argument("--run-id", type=_common.run_id_arg, required=True)' + chr(10)
        untyped = 'p.add_argument("--run-id", required=True)' + chr(10)
        self.assertEqual(self.untyped(typed, "--run-id", "_common.run_id_arg"), [])
        self.assertEqual(self.untyped(untyped, "--run-id", "_common.run_id_arg"), ["--run-id"])
        path_building = "dest = Path(args.brand) / 'x'" + chr(10)
        self.assertIsNotNone(re.search(r"Path\(\s*args\.brand|/\s*args\.brand\b|args\.brand\s*/", path_building))

    def test_each_run_id_script_refuses_a_path_with_a_usage_error(self):
        cases = {
            "checkpoint-manager.py": ["status", "--brand", "acme", "--run-id"],
            "drive-sync-state.py": ["--action", "list-pending-uploads", "--brand", "acme", "--run-id"],
            "pipeline-tracker.py": ["--action", "get-report", "--brand", "acme", "--run-id"],
            "run-audit.py": ["--brand", "acme", "--run-id"],
        }
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, CLAUDE_MARKETING_HOME=home)
            for name, argv in cases.items():
                for bad in ("../x", "a" + chr(92) + "b", "/abs"):
                    with self.subTest(script=name, value=bad):
                        p = subprocess.run([sys.executable, str(SCRIPTS / name)] + argv + [bad], capture_output=True,
                                           text=True, env=env, timeout=60)
                        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                        self.assertIn("single folder name", p.stderr)

    def test_pipeline_tracker_library_refuses_a_path_id(self):
        pt = load("pipeline-tracker.py", "cf_pipeline_tracker")
        with tempfile.TemporaryDirectory() as home, mock.patch.dict(os.environ, {"CLAUDE_MARKETING_HOME": home}):
            self.assertEqual(pt.get_run_file("acme", "run-A").name, "pipeline-run.json")
            for bad in ("../x", "..", "a/b"):
                with self.assertRaises(ValueError):
                    pt.get_run_file("acme", bad)


# ── the credentials the scripts read are declared in plugin.yaml ───────

class TestCredentialsAreDeclared(unittest.TestCase):
    """Hermes shows `optional_env` / `requires_env` to users; `requires_env: []` while the scripts read six
    third-party credentials under-declared them (non-blocking review note). They are all optional, so they
    are listed under optional_env."""

    READ = re.compile(r"""(?:environ\.get\(|environ\[|getenv\()\s*["']([A-Z][A-Z0-9_]+)["']""")
    CREDENTIAL = re.compile(r"(_KEY|_TOKEN|_SECRET|_PROJECT|_LOCATION|_CREDENTIALS)$")

    @classmethod
    def read_by_scripts(cls) -> set[str]:
        names = set()
        for p in SCRIPTS.glob("*.py"):
            names.update(cls.READ.findall(p.read_text(encoding="utf-8", errors="replace")))
        return {n for n in names if cls.CREDENTIAL.search(n)}

    @staticmethod
    def declared(yaml_text: str) -> set[str]:
        return set(re.findall(r"(?m)^\s*-\s*name:\s*([A-Z][A-Z0-9_]+)\s*$", yaml_text))

    def test_every_credential_a_script_reads_is_listed(self):
        text = (ROOT / "plugin.yaml").read_text(encoding="utf-8")
        missing = sorted(self.read_by_scripts() - self.declared(text))
        self.assertEqual(missing, [], "scripts read these credentials but plugin.yaml does not list them")
        self.assertGreaterEqual(len(self.read_by_scripts()), 3, "the scan found suspiciously few credentials")

    def test_nothing_is_required_to_install(self):
        self.assertIn("requires_env: []", (ROOT / "plugin.yaml").read_text(encoding="utf-8"))

    def test_plant_an_undeclared_credential_is_flagged(self):
        sample = 'key = os.environ.get("NEW_VENDOR_API_KEY")'
        found = {n for n in self.READ.findall(sample) if self.CREDENTIAL.search(n)}
        self.assertEqual(found, {"NEW_VENDOR_API_KEY"})
        self.assertEqual(found - self.declared("optional_env:\n  - name: OTHER_API_KEY\n"), {"NEW_VENDOR_API_KEY"})


if __name__ == "__main__":
    unittest.main()
