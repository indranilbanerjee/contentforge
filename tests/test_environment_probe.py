"""Layered Cowork detection: strong signals classify, weak signals warn."""
import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("pmeta", SCRIPTS / "plugin-metadata.py")
pmeta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pmeta)


def classify(**kw):
    base = dict(env={}, existing_paths=set(), platform_name="Linux",
                cwd="/home/user/work", home="/home/user", username="user")
    base.update(kw)
    return pmeta.classify_environment(**base)


class TestStrongSignals(unittest.TestCase):
    def test_cowork_session_env(self):
        r = classify(env={"ANTHROPIC_COWORK_SESSION_ID": "x"})
        self.assertEqual(r["environment"], "cowork-sandbox")

    def test_host_proxy_env(self):
        r = classify(env={"CLAUDE_CODE_HOST_HTTP_PROXY_PORT": "3128"})
        self.assertEqual(r["environment"], "cowork-sandbox")

    def test_mitm_socket(self):
        r = classify(existing_paths={"/var/run/mitm-proxy.sock"})
        self.assertEqual(r["environment"], "cowork-sandbox")

    def test_sessions_root(self):
        r = classify(existing_paths={"/sessions"})
        self.assertEqual(r["environment"], "cowork-sandbox")

    def test_warning_fires(self):
        r = classify(env={"ANTHROPIC_COWORK_SESSION_ID": "x"})
        self.assertIn("sandbox", r["cowork_warning"])


class TestWeakSignals(unittest.TestCase):
    def test_two_weak_signals_mean_uncertain(self):
        r = classify(env={"ALL_PROXY": "socks5h://localhost:1080"},
                     existing_paths={"/.dockerenv"},
                     username="serene-vibrant-newton")
        self.assertEqual(r["environment"], "linux-sandbox-uncertain")
        self.assertIsNotNone(r["cowork_warning"])

    def test_one_weak_signal_stays_linux(self):
        r = classify(existing_paths={"/.dockerenv"})
        self.assertEqual(r["environment"], "claude-code-linux")
        self.assertIsNone(r["cowork_warning"])

    def test_plain_windows(self):
        r = classify(platform_name="Windows", home="C:/Users/x", cwd="C:/Users/x/w", username="x")
        self.assertEqual(r["environment"], "claude-code-windows")
        self.assertIsNone(r["cowork_warning"])


if __name__ == "__main__":
    unittest.main()
