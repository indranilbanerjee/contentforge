"""Cross-file contract tests for the client-site intelligence chain (v3.19.0).
Defects live in edges: brand-setup -> profile schema -> researcher -> SEO -> reviewer -> card."""
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
read = lambda rel: (REPO / rel).read_text(encoding="utf-8")


class TestHarvestChain(unittest.TestCase):
    def test_brand_setup_runs_harvest_script(self):
        t = read("commands/brand-setup.md")
        self.assertIn("harvest-brand-pages.py", t)
        self.assertIn("harvest_status", t)

    def test_profile_template_has_harvest_and_facts(self):
        d = json.loads(read("config/brand-registry-template.json"))
        self.assertIn("harvest_status", d["seo_preferences"]["brand_pages"])
        self.assertIn("brand_facts", d)

    def test_researcher_has_recon_step_and_gate(self):
        t = read("agents/01-researcher.md")
        self.assertIn("Client Site Reconnaissance", t)
        self.assertIn("Internal-Link Inventory", t)
        self.assertIn("NEEDS-PRIMARY-SOURCE", t)

    def test_seo_agent_has_thin_guard_and_live_rule(self):
        t = read("agents/06-seo-geo-optimizer.md")
        self.assertIn("Thin-brand_pages guard", t)
        self.assertIn("Deep-link", t)
        self.assertTrue(("verified live" in t.lower()) or ("fetched live" in t.lower()))

    def test_reviewer_has_no_free_pass(self):
        t = read("agents/07-reviewer.md")
        self.assertIn("HOMEPAGE-ONLY INTERNAL LINKING", t)
        self.assertIn("do NOT exclude it from the average", t)
        self.assertNotIn("(informational-only brand) → score N/A and exclude from average (do NOT penalize)", t)

    def test_orchestrator_card_surfaces_link_deficiency(self):
        t = read("skills/contentforge/SKILL.md")
        self.assertIn("HOMEPAGE-ONLY INTERNAL LINKING", t)

    def test_research_brief_template_has_recon_section(self):
        self.assertIn("Client Site Reconnaissance", read("templates/research-brief.md"))

    def test_ai_detectability_surfacing_pinned(self):
        # v3.19.0's AI-detectability advisory rating must stay wired end to
        # end: reviewer scorecard -> Completion Card directive -> Phase 6.5
        # tell-scan that produces it.
        self.assertIn("AI-detectability (advisory)", read("agents/07-reviewer.md"))
        skill_text = read("skills/contentforge/SKILL.md")
        self.assertIn("AI-detectability", skill_text)
        self.assertIn("MUST append", skill_text)
        self.assertIn("AI-TELL SCAN", read("agents/06.5-humanizer.md"))


if __name__ == "__main__":
    unittest.main()
