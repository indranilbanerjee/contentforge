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
                "`scripts/` folder, next to `skills/`.")

    @staticmethod
    def missing(text: str, sentence: str) -> bool:
        return "CLAUDE_PLUGIN_ROOT" in text and sentence not in text

    def test_every_skill_and_command_that_uses_the_variable_says_where_the_scripts_are(self):
        files = sorted(ROOT.glob("skills/*/SKILL.md")) + sorted(ROOT.glob("commands/*.md"))
        bad = [str(p.relative_to(ROOT)) for p in files
               if self.missing(p.read_text(encoding="utf-8", errors="replace"), self.SENTENCE)]
        self.assertEqual(bad, [])

    def test_plant_a_skill_without_the_sentence_is_flagged(self):
        self.assertTrue(self.missing("run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`", self.SENTENCE))
        self.assertFalse(self.missing("run `python ${CLAUDE_PLUGIN_ROOT}/scripts/x.py`\n" + self.SENTENCE, self.SENTENCE))
        self.assertFalse(self.missing("no variable here", self.SENTENCE))


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
