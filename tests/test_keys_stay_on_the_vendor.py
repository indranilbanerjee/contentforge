"""4.6.0: an API key never follows a redirect off the vendor it was sent to.

urllib's redirect handler builds the follow-up request from the first one's ordinary headers (everything except Content-Length and
Content-Type), so a key set with `Request(url, headers=...)` or `req.add_header(...)` is sent, as it stands, to whatever host a 30x
answer names. `add_unredirected_header` keeps a header on the first request only. Two tests keep it that way:

  * a stub-redirect run: the script's own code asks a vendor host for a model list, the stub answers 302 to another host, and that
    host is shown every header it receives. No network, no real key. The harness is checked first with a request that sets the key
    the old way, because a test of a leak that cannot see a leak proves nothing.
  * a static guard over every shipped Python file: a urllib Request that carries a credential header, or an `add_header` call that
    names one (or whose header name cannot be read from the source), is a failure. Planted cases show the guard fires.
"""
from __future__ import annotations

import ast
import email.message
import io
import json
import os
import re
import sys
import unittest
import urllib.parse
import urllib.request
import urllib.response
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import refresh_models  # noqa: E402

SKIP_PARTS = {".git", "__pycache__", "node_modules", "tests", "results", "dist"}
ELSEWHERE = "elsewhere.example"

# ---------------------------------------------------------------------------------------------------------------------------
# The static guard
# ---------------------------------------------------------------------------------------------------------------------------

# Authorization, Proxy-Authorization and Cookie, anything ending in -key / -token / -secret (x-api-key, x-goog-api-key, api-key,
# xi-api-key, api-subscription-key ...), or a bare key / token / secret.
CREDENTIAL_NAME = re.compile(r"(?i)^(authorization|proxy-authorization|cookie)$|[-_](key|token|secret)$|^(api)?(key|token|secret)$")
CREDENTIAL_SCHEME = re.compile(r"(?i)^\s*(bearer|basic|key|token)\s")


def leading_text(node) -> str:
    """The literal text a string expression starts with ('Bearer ' for 'Bearer ' + key and for f'Bearer {key}'), else ''."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values:
        return leading_text(node.values[0])
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return leading_text(node.left)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format":
        return leading_text(node.func.value)
    return ""


def is_credential(name_node, value_node) -> bool:
    if isinstance(name_node, ast.Constant) and isinstance(name_node.value, str) and CREDENTIAL_NAME.search(name_node.value):
        return True
    return bool(CREDENTIAL_SCHEME.match(leading_text(value_node)))


def callee(node: ast.Call) -> str:
    f = node.func
    return f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""


def credential_leaks(source: str, where: str = "<source>") -> list[str]:
    """One line per place a credential header would be copied to a redirect target."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = callee(node)
        if name == "add_header":
            head = node.args[0] if node.args else None
            tail = node.args[1] if len(node.args) > 1 else None
            if head is None or not (isinstance(head, ast.Constant) and isinstance(head.value, str)):
                found.append(f"{where}:{node.lineno}: add_header with a header name that cannot be read from the source")
            elif is_credential(head, tail):
                found.append(f"{where}:{node.lineno}: add_header sets {head.value!r}; use add_unredirected_header")
        elif name == "Request":
            headers = next((k.value for k in node.keywords if k.arg == "headers"), node.args[2] if len(node.args) > 2 else None)
            if headers is None or (isinstance(headers, ast.Constant) and headers.value is None):
                continue
            if not isinstance(headers, ast.Dict):
                found.append(f"{where}:{node.lineno}: Request(headers=...) is built elsewhere; add each header with add_unredirected_header")
                continue
            for key, value in zip(headers.keys, headers.values):
                if key is None or not isinstance(key, ast.Constant):
                    found.append(f"{where}:{node.lineno}: Request(headers=...) has a header name that cannot be read from the source")
                elif is_credential(key, value):
                    found.append(f"{where}:{node.lineno}: Request(headers=...) carries {key.value!r}; use add_unredirected_header")
    return found


def shipped_python() -> list[Path]:
    return sorted(p for p in REPO.rglob("*.py") if p.is_file() and not (set(p.relative_to(REPO).parts) & SKIP_PARTS))


class TestStaticGuard(unittest.TestCase):

    def test_no_shipped_script_copies_a_credential_header_to_a_redirect(self):
        found = []
        for path in shipped_python():
            found += credential_leaks(path.read_text(encoding="utf-8-sig"), str(path.relative_to(REPO)))
        self.assertEqual(found, [], "\n  " + "\n  ".join(found))

    def test_the_scan_reads_the_scripts_that_send_keys(self):
        names = {p.name for p in shipped_python()}
        self.assertIn("refresh_models.py", names)
        self.assertGreater(len(names), 20)

    def test_plants(self):
        planted = {
            "add_header, the usual way": 'req = urllib.request.Request(u)\nreq.add_header("Authorization", "Bearer " + key)\n',
            "add_header, the x-api-key header": 'req.add_header("x-api-key", key)\n',
            "add_header, the Gemini header": 'req.add_header("X-Goog-Api-Key", key)\n',
            "add_header, a header name in a variable": "for k, v in headers.items():\n    req.add_header(k, v)\n",
            "add_header, a Bearer value under any name": 'req.add_header("X-Auth", f"Bearer {key}")\n',
            "Request headers literal": 'urllib.request.Request(u, headers={"xi-api-key": key})\n',
            "Request headers literal, Sarvam": 'urllib.request.Request(u, data=b, headers={"api-subscription-key": key})\n',
            "Request headers literal, Bearer value": 'Request(u, headers={"X-Auth": "Bearer " + key})\n',
            "Request headers positional": 'Request(u, None, {"Authorization": token})\n',
            "Request headers from a variable": "urllib.request.Request(u, headers=hdr)\n",
            "Request headers unpacked": "urllib.request.Request(u, headers={**base, 'a': 'b'})\n",
        }
        for label, source in planted.items():
            self.assertTrue(credential_leaks(source), label)

    def test_what_is_allowed_stays_allowed(self):
        fine = (
            'req = urllib.request.Request(u)\nreq.add_unredirected_header("Authorization", "Bearer " + key)\n',
            'req.add_unredirected_header("x-api-key", key)\n',
            'for k, v in headers.items():\n    req.add_unredirected_header(k, v)\n',
            'urllib.request.Request(u, headers={"User-Agent": UA, "Accept": "text/html"})\n',
            'urllib.request.Request(u, data=b, headers={"Content-Type": ct})\n',
            'urllib.request.Request(u, headers={})\n',
            'urllib.request.Request(u)\nreq.add_header("Accept", "application/json")\n',
        )
        for source in fine:
            self.assertEqual(credential_leaks(source), [], source)


# ---------------------------------------------------------------------------------------------------------------------------
# The stub redirect
# ---------------------------------------------------------------------------------------------------------------------------

A_KEY = "ant-test-0000-not-a-real-anthropic-key"
O_KEY = "oai-test-0000-not-a-real-openai-key"
G_KEY = "g-test-0000-not-a-real-google-key"
ENV = {"ANTHROPIC_API_KEY": A_KEY, "OPENAI_API_KEY": O_KEY, "GEMINI_API_KEY": G_KEY}


def answer(url: str, code: int, msg: str, headers: dict, payload: bytes) -> urllib.response.addinfourl:
    head = email.message.Message()
    for name, value in headers.items():
        head[name] = value
    response = urllib.response.addinfourl(io.BytesIO(payload), head, url, code)
    response.msg = msg
    return response


class RedirectingHost(urllib.request.BaseHandler):
    """Stands in for the network: every host except ELSEWHERE answers 302 to ELSEWHERE, and ELSEWHERE answers an empty list.
    It records the headers each host was shown, which is all a redirect target could ever read."""

    handler_order = 100          # ahead of the real HTTPSHandler

    def __init__(self):
        self.shown = []          # (host, [(header, value), ...]) in the order the requests arrived

    def https_open(self, req):
        host = urllib.parse.urlsplit(req.full_url).netloc
        self.shown.append((host, list(req.header_items())))
        if host != ELSEWHERE:
            return answer(req.full_url, 302, "Found", {"Location": f"https://{ELSEWHERE}/leak"}, b"")
        return answer(req.full_url, 200, "OK", {"Content-Type": "application/json"},
                      json.dumps({"data": [], "has_more": False, "models": []}).encode())

    def seen_by_elsewhere(self) -> str:
        return " ".join(f"{k}: {v}" for host, items in self.shown if host == ELSEWHERE for k, v in items)

    def reached_elsewhere(self) -> bool:
        return any(host == ELSEWHERE for host, _ in self.shown)


def through(handler: RedirectingHost, fn, env: dict):
    """Run fn with urllib's own opener chain (redirect handler included) and the stub as the network."""
    opener = urllib.request.build_opener(handler)
    with mock.patch.dict(os.environ, env), mock.patch.object(urllib.request, "_opener", opener):
        return fn()


class TestAKeyDoesNotFollowARedirect(unittest.TestCase):

    def test_the_stub_sees_a_key_set_the_old_way(self):
        """Plant: the old code, `add_header`, leaks. If this passes, the stub can see a leak; if it fails, the tests below prove nothing."""
        def old_way():
            req = urllib.request.Request("https://api.vendor.example/v1/models")
            req.add_header("x-api-key", A_KEY)
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.read()
        handler = RedirectingHost()
        through(handler, old_way, {})
        self.assertTrue(handler.reached_elsewhere(), "the stub did not follow its own redirect")
        self.assertIn(A_KEY, handler.seen_by_elsewhere())

    def test_the_stub_sees_a_key_given_in_the_headers_argument(self):
        def old_way():
            req = urllib.request.Request("https://api.vendor.example/v1/models", headers={"Authorization": f"Bearer {O_KEY}"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.read()
        handler = RedirectingHost()
        through(handler, old_way, {})
        self.assertIn(O_KEY, handler.seen_by_elsewhere())

    def check(self, fn, key, header_name):
        handler = RedirectingHost()
        through(handler, fn, ENV)
        first_host, first_headers = handler.shown[0]
        self.assertNotEqual(first_host, ELSEWHERE)
        sent = {k.lower(): v for k, v in first_headers}
        self.assertIn(header_name.lower(), sent, "the vendor must still receive the key")
        self.assertIn(key, sent[header_name.lower()])
        self.assertTrue(handler.reached_elsewhere(), "the stub did not follow its own redirect")
        leaked = handler.seen_by_elsewhere()
        self.assertNotIn(key, leaked)
        self.assertNotIn(header_name.lower(), leaked.lower())

    def test_anthropic_key_stays_with_anthropic(self):
        self.check(refresh_models.list_anthropic, A_KEY, "x-api-key")

    def test_openai_key_stays_with_openai(self):
        self.check(refresh_models.list_openai, O_KEY, "Authorization")

    def test_gemini_key_stays_with_google(self):
        self.check(refresh_models.list_gemini, G_KEY, "x-goog-api-key")

    def test_no_header_the_vendor_was_sent_reaches_the_redirect_target(self):
        """Nothing the vendor was sent needs to reach the redirect target, the harmless headers included."""
        handler = RedirectingHost()
        through(handler, refresh_models.list_anthropic, ENV)
        self.assertNotIn("anthropic-version", handler.seen_by_elsewhere().lower())


if __name__ == "__main__":
    unittest.main()
