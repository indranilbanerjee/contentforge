"""The AI-assistance disclosure: honest by default, fail-safe by design.

Pins the v3.22.0 disclosure contract: the surface classifier only skips the
disclosure on an AFFIRMATIVE non-Claude fingerprint (uncertain ⇒ disclose —
over-disclosure is harmless, under-disclosure is the compliance risk), the
default wording names no vendor and claims only the review the pipeline
actually performs, the author field is genuinely optional, and the decision
is recorded in run.json either way.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ds = _load("detect_surface", "detect_surface.py")
OUTPUT_MANAGER = (REPO / "agents" / "08-output-manager.md").read_text(encoding="utf-8")
STYLE_GUIDE = (REPO / "skills" / "cf-style-guide" / "SKILL.md").read_text(encoding="utf-8")


class TestSurfaceClassifier(unittest.TestCase):
    def test_claude_env_classifies_claude(self):
        r = ds.classify_surface({"CLAUDECODE": "1"})
        self.assertEqual(r["surface"], "claude")
        self.assertIn("CLAUDECODE", r["basis"])

    def test_non_claude_fingerprint_classifies_non_claude(self):
        r = ds.classify_surface({"CODEX_SESSION_ID": "x"})
        self.assertEqual(r["surface"], "non-claude")

    def test_no_evidence_is_uncertain(self):
        self.assertEqual(ds.classify_surface({})["surface"], "uncertain")

    def test_conflicting_evidence_is_uncertain(self):
        r = ds.classify_surface({"CLAUDECODE": "1", "CODEX_SESSION_ID": "x"})
        self.assertEqual(r["surface"], "uncertain")


class TestDisclosureDecision(unittest.TestCase):
    def test_the_full_mode_by_surface_matrix(self):
        cases = {
            ("always", "claude"): True, ("always", "non-claude"): True,
            ("always", "uncertain"): True,
            ("off", "claude"): False, ("off", "non-claude"): False,
            ("off", "uncertain"): False,
            ("claude-surfaces", "claude"): True,
            ("claude-surfaces", "non-claude"): False,
            ("claude-surfaces", "uncertain"): True,  # THE fail-safe pin
        }
        for (mode, surface), expected in cases.items():
            with self.subTest(mode=mode, surface=surface):
                self.assertEqual(ds.disclosure_applies(mode, surface), expected)

    def test_uncertain_discloses_because_underdisclosure_is_the_risk(self):
        """The load-bearing design decision, pinned on its own: skipping the
        disclosure requires an AFFIRMATIVE non-Claude fingerprint, never mere
        absence of a Claude one."""
        self.assertTrue(ds.disclosure_applies("claude-surfaces", "uncertain"))

    def test_missing_mode_defaults_to_claude_surfaces(self):
        self.assertTrue(ds.disclosure_applies(None, "uncertain"))
        self.assertFalse(ds.disclosure_applies(None, "non-claude"))


class TestDefaultWordingHonesty(unittest.TestCase):
    def _default_texts(self):
        # The two default disclosure strings live in the output manager Step 1.5
        texts = re.findall(r"`\*Created with AI assistance[^`]*\*`", OUTPUT_MANAGER)
        self.assertEqual(len(texts), 2, "expected exactly two default disclosure strings")
        return texts

    def test_default_text_names_no_vendor_or_model(self):
        """Hard rule + keeps the wording valid on every surface. Brands may
        name models in CUSTOM text — their words, their choice."""
        vendor_re = re.compile(
            r"\b(claude|anthropic|gpt|openai|gemini|google|copilot|codex)\b", re.I)
        for t in self._default_texts():
            self.assertIsNone(vendor_re.search(t),
                              f"default disclosure text names a vendor: {t}")

    def test_author_is_optional_and_never_invented(self):
        self.assertIn("An empty author is fully supported", OUTPUT_MANAGER)
        self.assertIn("never invent a name", OUTPUT_MANAGER)

    def test_decision_is_recorded_either_way(self):
        self.assertIn('"disclosure": {"applied"', OUTPUT_MANAGER)
        self.assertIn("a recorded choice, not an omission", OUTPUT_MANAGER)

    def test_disclosure_lands_inside_the_body_so_it_survives_publish(self):
        self.assertIn("survives `/contentforge:publish`", OUTPUT_MANAGER)

    def test_output_manager_delegates_the_decision_to_the_script(self):
        self.assertIn("detect_surface.py", OUTPUT_MANAGER)
        self.assertIn("Never override the script's answer", OUTPUT_MANAGER)


class TestBrandSetupWiring(unittest.TestCase):
    def test_style_guide_configures_all_three_modes(self):
        for token in ('"claude-surfaces"', "`always`", "`off`", "ai_disclosure"):
            self.assertIn(token, STYLE_GUIDE,
                          f"cf-style-guide no longer documents {token}")

    def test_style_guide_says_author_may_stay_null(self):
        self.assertIn("may stay null", STYLE_GUIDE)


if __name__ == "__main__":
    unittest.main()
