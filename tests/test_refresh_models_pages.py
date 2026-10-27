"""4.5.12: refresh_models.py keeps every API key out of the URL, and reads every page of every provider's model list.

Before 4.5.12 the Gemini call was `https://generativelanguage.googleapis.com/v1beta/models?key=<key>`: a key in a URL is kept by
proxies and server logs, and Google's own header (`x-goog-api-key`) exists so it does not have to be. The three list calls also
read ONE page each, which is 20 models for Anthropic and 50 for Google unless asked for more. A drift check that sees a partial
list reports every model on the missing pages as gone ("current but unlisted"), which is the alarm the script exists to raise,
so the report was wrong exactly when the catalogue was long.

These tests drive the script's own code through a recording stand-in for urllib's opener. Nothing touches the network, and no
key in them is a real one.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import refresh_models  # noqa: E402

A_KEY = "ant-test-0000-not-a-real-anthropic-key"
O_KEY = "oai-test-0000-not-a-real-openai-key"
G_KEY = "g-test-0000-not-a-real-google-key"
KEYS = (A_KEY, O_KEY, G_KEY)
ENV = {"ANTHROPIC_API_KEY": A_KEY, "OPENAI_API_KEY": O_KEY, "GEMINI_API_KEY": G_KEY}


class Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def body(obj) -> Resp:
    return Resp(json.dumps(obj).encode("utf-8"))


def anthropic_page(req):
    after = urllib.parse.parse_qs(urllib.parse.urlsplit(req.full_url).query).get("after_id", [None])[0]
    if after is None:
        return body({"data": [{"id": "claude-one"}, {"id": "claude-two"}], "has_more": True, "last_id": "claude-two"})
    assert after == "claude-two", after
    return body({"data": [{"id": "claude-three"}], "has_more": False, "last_id": "claude-three"})


def openai_page(req):
    after = urllib.parse.parse_qs(urllib.parse.urlsplit(req.full_url).query).get("after", [None])[0]
    if after is None:
        return body({"object": "list", "data": [{"id": "gpt-one"}, {"id": "gpt-two"}], "has_more": True, "last_id": "gpt-two"})
    assert after == "gpt-two", after
    return body({"object": "list", "data": [{"id": "gpt-three"}], "has_more": False})


def google_page(req):
    token = urllib.parse.parse_qs(urllib.parse.urlsplit(req.full_url).query).get("pageToken", [None])[0]
    if token is None:
        return body({"models": [{"name": "models/gem-one"}, {"name": "models/gem-two"}], "nextPageToken": "tok-1"})
    assert token == "tok-1", token
    return body({"models": [{"name": "models/gem-three"}]})


PAGES = {"api.anthropic.com": anthropic_page, "api.openai.com": openai_page, "generativelanguage.googleapis.com": google_page}


class Recorder:
    """Stands in for urllib.request.urlopen: records every request, answers from the page functions or fails on cue."""

    def __init__(self, pages=None, fail=None):
        self.pages = dict(PAGES if pages is None else pages)
        self.fail = fail or {}      # host -> callable(request, call_number) that raises, or returns None to answer normally
        self.requests = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        host = urllib.parse.urlsplit(req.full_url).netloc
        n = sum(1 for r in self.requests if urllib.parse.urlsplit(r.full_url).netloc == host)
        if host in self.fail:
            self.fail[host](req, n)
        return self.pages[host](req)

    def to(self, host):
        return [r for r in self.requests if urllib.parse.urlsplit(r.full_url).netloc == host]

    def headers(self, req) -> str:
        return " ".join(f"{k}: {v}" for k, v in req.header_items())


def run_main(rec, *args):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, ENV), mock.patch.object(urllib.request, "urlopen", rec), \
            mock.patch.object(sys, "argv", ["refresh_models.py", *args]), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = refresh_models.main()
    return code, out.getvalue(), err.getvalue()


def list_with(fn, rec, key_env):
    with mock.patch.dict(os.environ, {key_env: ENV[key_env]}), mock.patch.object(urllib.request, "urlopen", rec):
        return fn()


class TestEveryPageIsRead(unittest.TestCase):

    def test_anthropic_follows_has_more_and_last_id(self):
        rec = Recorder()
        got = list_with(refresh_models.list_anthropic, rec, "ANTHROPIC_API_KEY")
        self.assertEqual(got, {"claude-one", "claude-two", "claude-three"})
        self.assertEqual(len(rec.requests), 2)

    def test_anthropic_asks_for_the_largest_page_instead_of_the_default_20(self):
        rec = Recorder()
        list_with(refresh_models.list_anthropic, rec, "ANTHROPIC_API_KEY")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(rec.requests[0].full_url).query)
        self.assertEqual(query.get("limit"), ["1000"])

    def test_google_follows_next_page_token(self):
        rec = Recorder()
        got = list_with(refresh_models.list_gemini, rec, "GEMINI_API_KEY")
        self.assertEqual(got, {"gem-one", "gem-two", "gem-three"})
        self.assertEqual(len(rec.requests), 2)

    def test_google_asks_for_the_largest_page_instead_of_the_default_50(self):
        rec = Recorder()
        list_with(refresh_models.list_gemini, rec, "GEMINI_API_KEY")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(rec.requests[0].full_url).query)
        self.assertEqual(query.get("pageSize"), ["1000"])

    def test_openai_follows_a_cursor_when_the_list_offers_one(self):
        rec = Recorder()
        got = list_with(refresh_models.list_openai, rec, "OPENAI_API_KEY")
        self.assertEqual(got, {"gpt-one", "gpt-two", "gpt-three"})

    def test_a_single_page_list_is_read_once(self):
        single = {"api.openai.com": lambda req: body({"object": "list", "data": [{"id": "gpt-only"}]})}
        rec = Recorder(single)
        self.assertEqual(list_with(refresh_models.list_openai, rec, "OPENAI_API_KEY"), {"gpt-only"})
        self.assertEqual(len(rec.requests), 1)

    def test_the_report_counts_models_across_pages(self):
        code, out, _ = run_main(Recorder(), "--json")
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual((report["anthropic"]["live_count"], report["openai"]["live_count"], report["google"]["live_count"]),
                         (3, 3, 3))


class TestAFailedOrEndlessListIsSkippedNotTruncated(unittest.TestCase):
    """A partial list would report every model on the missing pages as gone, the one alarm this script exists to raise."""

    def test_a_failing_second_page_skips_the_provider(self):
        def second_page_fails(req, n):
            if n == 2:
                raise urllib.error.URLError("connection reset")

        for host, fn, env in (("api.anthropic.com", refresh_models.list_anthropic, "ANTHROPIC_API_KEY"),
                              ("generativelanguage.googleapis.com", refresh_models.list_gemini, "GEMINI_API_KEY")):
            with self.subTest(host=host):
                rec = Recorder(fail={host: second_page_fails})
                self.assertIsNone(list_with(fn, rec, env))
                self.assertEqual(len(rec.requests), 2)

    def test_a_rejected_key_skips_the_provider(self):
        def reject(req, n):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)

        rec = Recorder(fail={"generativelanguage.googleapis.com": reject})
        self.assertIsNone(list_with(refresh_models.list_gemini, rec, "GEMINI_API_KEY"))

    def test_a_body_that_is_not_a_list_object_skips_the_provider_instead_of_crashing(self):
        for host, fn, env in (("api.anthropic.com", refresh_models.list_anthropic, "ANTHROPIC_API_KEY"),
                              ("generativelanguage.googleapis.com", refresh_models.list_gemini, "GEMINI_API_KEY")):
            for odd in ([], "oops", 7, {"data": None, "models": None}):
                with self.subTest(host=host, body=odd):
                    rec = Recorder({host: lambda req, odd=odd: body(odd)})
                    got = list_with(fn, rec, env)
                    self.assertTrue(got is None or got == set(), got)

    def test_a_timeout_mid_read_skips_the_provider(self):
        def stall(req, n):
            raise TimeoutError("timed out")

        rec = Recorder(fail={"api.anthropic.com": stall})
        self.assertIsNone(list_with(refresh_models.list_anthropic, rec, "ANTHROPIC_API_KEY"))

    def test_a_list_that_never_ends_is_skipped_after_a_bounded_number_of_requests(self):
        endless = {"generativelanguage.googleapis.com":
                   lambda req: body({"models": [{"name": "models/x"}], "nextPageToken": "again"})}
        rec = Recorder(endless)
        self.assertIsNone(list_with(refresh_models.list_gemini, rec, "GEMINI_API_KEY"))
        self.assertLessEqual(len(rec.requests), refresh_models.MAX_PAGES)

    def test_the_report_says_skipped_for_the_provider_that_failed_and_still_checks_the_others(self):
        def second_page_fails(req, n):
            if n == 2:
                raise urllib.error.URLError("connection reset")

        code, out, _ = run_main(Recorder(fail={"api.anthropic.com": second_page_fails}), "--json")
        report = json.loads(out)
        self.assertEqual(report["anthropic"]["status"], "skipped (no API key or fetch failed)")
        self.assertEqual(report["google"]["status"], "checked")
        self.assertEqual(report["openai"]["status"], "checked")


class TestNoKeyIsEverInAUrlAnErrorOrTheOutput(unittest.TestCase):

    def test_no_url_the_script_requests_carries_any_key(self):
        rec = Recorder()
        run_main(rec, "--json")
        self.assertEqual(len(rec.requests), 6, "three providers, two pages each")
        for req in rec.requests:
            for key in KEYS:
                self.assertNotIn(key, req.full_url)
            self.assertNotIn("key=", req.full_url.lower())

    def test_the_gemini_key_travels_in_the_x_goog_api_key_header_on_every_page(self):
        rec = Recorder()
        run_main(rec, "--json")
        for req in rec.to("generativelanguage.googleapis.com"):
            self.assertEqual(req.get_header("X-goog-api-key"), G_KEY)
            self.assertIsNone(req.get_header("Authorization"))

    def test_the_other_keys_keep_their_own_headers_on_every_page(self):
        rec = Recorder()
        run_main(rec, "--json")
        for req in rec.to("api.anthropic.com"):
            self.assertEqual(req.get_header("X-api-key"), A_KEY)
            self.assertEqual(req.get_header("Anthropic-version"), "2023-06-01")
        for req in rec.to("api.openai.com"):
            self.assertEqual(req.get_header("Authorization"), f"Bearer {O_KEY}")

    def test_each_key_goes_only_to_its_own_vendor(self):
        rec = Recorder()
        run_main(rec, "--json")
        own = {"api.anthropic.com": A_KEY, "api.openai.com": O_KEY, "generativelanguage.googleapis.com": G_KEY}
        for req in rec.requests:
            host = urllib.parse.urlsplit(req.full_url).netloc
            sent = self.sent_text(req)
            for vendor, key in own.items():
                if vendor == host:
                    self.assertIn(key, sent)
                else:
                    self.assertNotIn(key, sent, f"{vendor}'s key went to {host}")

    @staticmethod
    def sent_text(req) -> str:
        return req.full_url + " " + " ".join(f"{k}: {v}" for k, v in req.header_items())

    def test_a_failure_that_echoes_the_key_leaks_nothing_into_the_output(self):
        """Providers echo part of a rejected key in their error text; the script must not print any error text."""
        def echo(req, n):
            raise urllib.error.HTTPError(req.full_url, 401, f"invalid key {G_KEY} {A_KEY} {O_KEY}", {}, None)

        for args in (("--json",), ()):
            with self.subTest(args=args):
                rec = Recorder(fail={host: echo for host in PAGES})
                code, out, err = run_main(rec, *args)
                for key in KEYS:
                    self.assertNotIn(key, out)
                    self.assertNotIn(key, err)

    def test_a_successful_run_prints_no_key_either(self):
        for args in (("--json",), ()):
            with self.subTest(args=args):
                _, out, err = run_main(Recorder(), *args)
                for key in KEYS:
                    self.assertNotIn(key, out)
                    self.assertNotIn(key, err)

    def test_the_source_has_no_key_in_a_url_template(self):
        source = (SCRIPTS_DIR / "refresh_models.py").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"[?&]key=", "an API key is placed in a URL")


class TestDocsMatchTheScript(unittest.TestCase):
    """The privacy table and the curator doc say how refresh_models.py sends keys and what its report shows."""

    ROOT = SCRIPTS_DIR.parent

    def text(self, rel):
        return " ".join((self.ROOT / rel).read_text(encoding="utf-8").split())

    def test_privacy_says_where_each_key_goes_and_that_every_page_is_read(self):
        row = next(line for line in self.text("PRIVACY.md").split("| `") if line.startswith("scripts/refresh_models.py"))
        for fact in ("every page", "request header", "x-goog-api-key", "never in a URL"):
            self.assertIn(fact, row)

    def test_the_curator_doc_says_how_keys_travel_and_what_a_failed_page_means(self):
        doc = self.text("docs/MODEL-CURATOR.md")
        for fact in ("never in a URL", "1000", "skipped"):
            self.assertIn(fact, doc)

    def test_the_curator_doc_names_every_bucket_the_report_prints(self):
        source = (SCRIPTS_DIR / "refresh_models.py").read_text(encoding="utf-8")
        labels = __import__("re").findall(r'\("\w+", "([A-Z]+) \(', source)
        self.assertEqual(sorted(labels), ["ALARM", "EXPECTED", "NEW", "PENDING"])
        doc = self.text("docs/MODEL-CURATOR.md")
        for label in labels:
            self.assertIn(f"**{label}**", doc, f"the curator doc does not describe the {label} bucket")


if __name__ == "__main__":
    unittest.main()
