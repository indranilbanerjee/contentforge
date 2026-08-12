"""The instruction surface must not depend on, or instruct installing,
commercial products.

Suite-wide policy: capability first, product never. A workflow may USE
connectors the user already chose (the graceful-degradation pattern — "Ahrefs
when connected, web-search fallback when not"), and the connector CATALOG may
name what exists; but no skill or agent may make a commercial product a
required step, and nothing may instruct signing up for one. The 2026-08 audit
found this plugin already clean — these tests PIN that state so it cannot
silently regress.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
AGENTS = REPO / "agents"

# Commercial products the content/SEO domain reaches for. Recognition list for
# the SCANNER only — naming them here is what lets the guard find them.
VENDOR = (r"(ahrefs|semrush|similarweb|grammarly|jasper|surfer ?seo|copyscape|"
          r"originality\.ai|gptzero|deepl|sarvam|midjourney|frase|clearscope|"
          r"marketmuse)")

SIGNUP_RE = re.compile(
    r"(?i)(sign up|create an account|subscribe|purchase a plan|buy a license|"
    r"install)[^.\n]{0,60}\b" + VENDOR + r"\b")

# A vendor mention on the instruction surface is fine ONLY in conditional,
# already-connected framing. Lines matching VENDOR must carry one of these
# markers (or live in an exempt catalog file).
CONDITIONAL_MARKERS = ("when connected", "if connected", "falls back",
                       "fallback", "if such a connector", "when available",
                       "if available", "already connected", "connected",
                       "connector", "mcp", "e.g.", "optional",
                       # citing a named study is attribution, not tool dependence
                       "study", "reported by", "according to")

# Catalog surfaces where naming connectors IS the job.
EXEMPT = {
    "skills/cf-connect/SKILL.md",
    "skills/cf-add-integration/SKILL.md",
    "skills/cf-integrations/SKILL.md",
}


def instruction_files():
    for base in (SKILLS, AGENTS):
        for f in sorted(base.rglob("*.md")):
            yield f.relative_to(REPO).as_posix(), f.read_text(
                encoding="utf-8", errors="replace")


class TestVendorNeutrality(unittest.TestCase):
    def test_no_signup_or_install_instructions(self):
        hits = []
        for rel, text in instruction_files():
            m = SIGNUP_RE.search(text)
            if m:
                hits.append(f"{rel}: {m.group(0)[:100]}")
        self.assertEqual(hits, [], "Sign-up/install instructions for commercial "
                                   "products on the instruction surface:\n  "
                                   + "\n  ".join(hits))

    def test_vendor_mentions_stay_conditional(self):
        """Every vendor mention outside the catalog must carry connected-tools
        framing — the pattern that made the 2026-08 audit pass."""
        vendor_re = re.compile(r"(?i)\b" + VENDOR + r"\b")
        bare = []
        for rel, text in instruction_files():
            if rel in EXEMPT:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if vendor_re.search(line):
                    low = line.lower()
                    if not any(mk in low for mk in CONDITIONAL_MARKERS):
                        bare.append(f"{rel}:{i}: {line.strip()[:100]}")
        self.assertEqual(bare, [],
                         "Vendor named without conditional/connected framing "
                         "(add 'when connected' framing or route by capability):\n  "
                         + "\n  ".join(bare))

    def test_no_bare_current_model_ids_on_instruction_surface(self):
        """Model ids belong in the registry and resolver, not in skill/agent
        prose — the resolver's alias layer exists so docs never carry ids."""
        model_re = re.compile(r"\b(claude-(?:opus|sonnet|haiku|fable)-[0-9][\w.-]*|"
                              r"gpt-[45][\w.-]*|gemini-[0-9][\w.-]*)\b")
        hits = []
        for rel, text in instruction_files():
            for i, line in enumerate(text.splitlines(), 1):
                if model_re.search(line) and "resolve_model" not in line:
                    hits.append(f"{rel}:{i}: {line.strip()[:100]}")
        self.assertEqual(hits, [], "Bare model ids on the instruction surface:\n  "
                                   + "\n  ".join(hits))

    # ── plant checks ────────────────────────────────────────────────

    def test_scanner_fires_on_planted_violations(self):
        self.assertTrue(SIGNUP_RE.search("First, sign up for an Ahrefs account."))
        vendor_re = re.compile(r"(?i)\b" + VENDOR + r"\b")
        self.assertTrue(vendor_re.search("Use Semrush to pull the keyword list."))

    def test_scanner_accepts_conditional_framing(self):
        line = "Uses MCP tools (Ahrefs, Similarweb) when connected, falls back to web search"
        self.assertIsNone(SIGNUP_RE.search(line))
        self.assertTrue(any(mk in line.lower() for mk in CONDITIONAL_MARKERS))


if __name__ == "__main__":
    unittest.main()
