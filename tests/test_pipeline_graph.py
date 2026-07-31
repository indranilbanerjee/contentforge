"""Whole-system contract checks across every skill and agent.

ContentForge is a graph, not a pile of files: phases hand artifacts to each
other, skills dispatch agents, and every gate number lives in config. The
defects that matter live in those edges, so these tests assert the edges
rather than the contents of any single file.

Covers the breaks found on 2026-07-30:
  * agents shipped but never dispatched by the skill that documents them
  * built-in template count in cf-template drifting from templates/ on disk
  * an agent reading a run artifact no phase ever writes
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / "agents"
SKILLS = REPO / "skills"
ORCHESTRATOR = SKILLS / "contentforge" / "SKILL.md"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def agent_names() -> dict[str, Path]:
    names = {}
    for p in AGENTS.glob("*.md"):
        m = re.search(r"^name:\s*(.+?)\s*$", read(p), re.M)
        if m:
            names[m.group(1)] = p
    return names


class TestEveryAgentIsDispatched(unittest.TestCase):
    """An agent nobody calls is dead weight that silently diverges from the
    skill that duplicates its logic."""

    # agent name -> the skill file responsible for dispatching it
    DISPATCHERS = {
        "researcher": "contentforge", "fact-checker": "contentforge",
        "content-drafter": "contentforge", "visual-asset-annotator": "contentforge",
        "scientific-validator": "contentforge", "structurer-proofreader": "contentforge",
        "seo-geo-optimizer": "contentforge", "humanizer": "contentforge",
        "reviewer": "contentforge", "output-manager": "contentforge",
        "social-adapter": "cf-social-adapt",
        "translator": "cf-translate",
        "batch-orchestrator": "batch-process",
    }

    def test_every_shipped_agent_has_a_declared_dispatcher(self):
        shipped = set(agent_names())
        self.assertEqual(shipped, set(self.DISPATCHERS),
                         "agents/ and the dispatcher map disagree — a new agent needs "
                         "a skill that dispatches it, or removal")

    def test_dispatcher_skill_invokes_the_agent_by_subagent_type(self):
        for agent, skill in self.DISPATCHERS.items():
            with self.subTest(agent=agent):
                path = SKILLS / skill / "SKILL.md"
                self.assertTrue(path.exists(), f"dispatcher skill {skill} missing")
                text = read(path)
                self.assertIn(f"contentforge:{agent}", text,
                              f"{skill} documents {agent} but never names it as a "
                              f"subagent_type — the agent would never run")

    def test_non_orchestrator_dispatchers_say_task_and_subagent_type(self):
        """Prose like 'the X Agent does Y' is not a dispatch instruction."""
        for skill in {"cf-social-adapt", "cf-translate", "batch-process"}:
            with self.subTest(skill=skill):
                text = read(SKILLS / skill / "SKILL.md")
                self.assertIn("subagent_type", text,
                              f"{skill} must dispatch its agent via Task/subagent_type")
                self.assertIn("Task", text)


class TestRunArtifactGraph(unittest.TestCase):
    """Every phase artifact an agent reads must be written by some phase."""

    ARTIFACT = re.compile(r"phase-[0-9.]+[a-z-]*\.(?:md|json|txt)")

    def test_every_read_artifact_is_produced_by_the_pipeline_contract(self):
        orch = read(ORCHESTRATOR)
        produced = set(self.ARTIFACT.findall(orch))
        consumed = set()
        for p in AGENTS.glob("*.md"):
            consumed |= set(self.ARTIFACT.findall(read(p)))
        orphans = sorted(consumed - produced)
        self.assertEqual(orphans, [],
                         f"agents read run artifacts the orchestrator's Pipeline "
                         f"Contract never lists as produced: {orphans}")


class TestBuiltinTemplateCount(unittest.TestCase):
    """cf-template advertises the built-ins; drift means users are told a
    shipped template does not exist."""

    def test_cf_template_count_matches_disk(self):
        on_disk = sorted(p.stem.replace("-structure", "")
                         for p in (REPO / "templates" / "content-types").glob("*-structure.md"))
        text = read(SKILLS / "cf-template" / "SKILL.md")
        counts = set(re.findall(r"(\d+) built-in", text))
        self.assertEqual(counts, {str(len(on_disk))},
                         f"cf-template claims {counts} built-in templates but "
                         f"templates/content-types/ ships {len(on_disk)}: {on_disk}")

    def test_every_shipped_template_is_named_in_cf_template(self):
        text = read(SKILLS / "cf-template" / "SKILL.md")
        for p in (REPO / "templates" / "content-types").glob("*-structure.md"):
            name = p.stem.replace("-structure", "")
            with self.subTest(template=name):
                self.assertIn(name, text,
                              f"{name} ships in templates/content-types/ but "
                              f"cf-template never mentions it")


class TestConfigKeysCitedByAgentsExist(unittest.TestCase):
    """Agents defer gate numbers to config; a renamed key silently disables a gate."""

    def test_cited_scoring_keys_resolve(self):
        cfg = json.loads(read(REPO / "config" / "scoring-thresholds.json"))
        default = cfg["default"]
        self.assertIn("feedback_loop_limits", default)
        limits = default["feedback_loop_limits"]
        for key in ("phase_4_to_3", "phase_4_to_3_5", "phase_7_to_any", "max_total_loops"):
            self.assertIn(key, limits, f"{key} is cited by an agent but absent from config")
        gates = default["quality_gates"]["phase_7_review"]
        for key in ("min_content_quality", "min_citation_integrity", "min_brand_compliance",
                    "min_seo_performance", "min_readability"):
            self.assertIn(key, gates)
        self.assertIn("human_review_threshold", default)

    def test_every_industry_pack_referenced_by_overrides_exists(self):
        cfg = json.loads(read(REPO / "config" / "scoring-thresholds.json"))
        for industry in cfg.get("industry_overrides", {}):
            with self.subTest(industry=industry):
                self.assertTrue((REPO / "config" / "industries" / f"{industry}.json").exists(),
                                f"scoring-thresholds overrides {industry} but no "
                                f"config/industries/{industry}.json ships")

    def test_social_platform_specs_cover_every_platform_the_agent_claims(self):
        specs = json.loads(read(REPO / "config" / "social-platform-specs.json"))
        agent = read(AGENTS / "10-social-adapter.md")
        claimed = re.search(r"\((linkedin,[^)]+)\)", agent)
        self.assertIsNotNone(claimed, "social-adapter no longer lists its platforms")
        for platform in [p.strip() for p in claimed.group(1).split(",")]:
            with self.subTest(platform=platform):
                self.assertIn(platform, specs)
                self.assertIn("ai_disclosure", specs[platform],
                              f"{platform} lacks ai_disclosure, which the agent reads")


if __name__ == "__main__":
    unittest.main()
