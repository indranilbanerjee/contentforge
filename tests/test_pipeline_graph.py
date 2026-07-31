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


class TestContentTypeRegistryIsConsistent(unittest.TestCase):
    """A content type that ships a template but is missing from a validator's
    enumeration is silently rejected by that part of the system. video_script
    shipped for months while batch, calendar, analytics and the brand profile
    all listed only five types."""

    # The three token spellings a type appears under across the repo.
    TYPES = {
        # stem on disk: (underscore, hyphen, Title)
        "video-script": ("video_script", "video-script", "Video Script"),
        "case-study": ("case_study", "case-study", "Case Study"),
        "newsletter": ("newsletter", "newsletter", "Newsletter"),
    }

    # files that enumerate the supported content types, and the token style each uses
    ENUMERATIONS = {
        "skills/contentforge/SKILL.md": 0,
        "agents/09-batch-orchestrator.md": 0,
        "skills/cf-analytics/SKILL.md": 0,
        "skills/cf-calendar/SKILL.md": 0,
        "skills/cf-style-guide/SKILL.md": 0,
        "commands/create-content.md": 0,
        "commands/output-folder.md": 0,
        "scripts/pipeline-tracker.py": 0,
        "config/brand-registry-template.json": 0,
        "skills/cf-template/SKILL.md": 1,
        "skills/cf-brief/SKILL.md": 1,
        "agents/03-content-drafter.md": 2,
        "agents/08-output-manager.md": 2,
    }

    def test_shipped_templates_match_the_orchestrator_table(self):
        shipped = {p.stem.replace("-structure", "")
                   for p in (REPO / "templates" / "content-types").glob("*-structure.md")}
        self.assertEqual(len(shipped), 8, f"expected 8 shipped templates, found {sorted(shipped)}")
        for stem in self.TYPES:
            self.assertIn(stem, shipped, f"{stem}-structure.md is asserted below but not shipped")

    def test_every_enumeration_includes_every_registered_type(self):
        for rel, style in self.ENUMERATIONS.items():
            text = read(REPO / rel)
            for stem, tokens in self.TYPES.items():
                with self.subTest(file=rel, type=stem):
                    self.assertIn(tokens[style], text,
                                  f"{rel} enumerates content types but omits {tokens[style]!r} — "
                                  f"that type ships a template and would be rejected here")

    def test_orchestrator_spec_table_has_a_row_per_shipped_type(self):
        orch = read(REPO / "skills" / "contentforge" / "SKILL.md")
        for label in ("Article", "Blog", "Whitepaper", "FAQ", "Research Paper",
                      "Video Script", "Case Study", "Newsletter"):
            with self.subTest(type=label):
                self.assertIn(f"**{label}**", orch,
                              f"Content Types & Specifications has no row for {label}, so "
                              f"Gate 3/Gate 5 have no target to check it against")

    def test_pipeline_tracker_has_benchmarks_for_every_type(self):
        text = read(REPO / "scripts" / "pipeline-tracker.py")
        for t in ("article", "blog", "whitepaper", "research_paper", "faq",
                  "video_script", "case_study", "newsletter"):
            with self.subTest(type=t):
                self.assertIn(f'"{t}": {{"0.5"', text,
                              f"PHASE_BENCHMARKS has no entry for {t}")


class TestAuthorEEATLayer(unittest.TestCase):
    """v3.18.0: the byline layer must stay wired end-to-end — profile schema →
    drafter byline → Person schema → capture path. A break anywhere reverts the
    pipeline to authorless output silently."""

    def test_brand_registry_defines_author_profiles(self):
        cfg = json.loads(read(REPO / "config" / "brand-registry-template.json"))
        ap = cfg.get("author_profiles")
        self.assertIsInstance(ap, dict, "brand-registry-template lost author_profiles")
        self.assertIn("default_author", ap)
        self.assertTrue(ap.get("authors"), "author_profiles.authors must ship a sample entry")
        sample = ap["authors"][0]
        for field in ("slug", "name", "title", "credentials", "bio", "expertise", "content_types"):
            self.assertIn(field, sample, f"sample author entry lost {field!r}")

    def test_drafter_applies_the_byline(self):
        text = read(REPO / "agents" / "03-content-drafter.md")
        self.assertIn("author_profiles", text)
        self.assertIn("Author selection (E-E-A-T)", text)
        self.assertIn("*By {author.name}, {author.title}*", text,
                      "the skeleton lost the byline line")

    def test_phase6_emits_person_schema_and_flags_authorless(self):
        text = read(REPO / "agents" / "06-seo-geo-optimizer.md")
        self.assertIn("**Person**", text)
        self.assertIn("author_profiles", text)
        self.assertIn("Authorless content", text,
                      "Phase 6 must flag the authorless E-E-A-T handicap")

    def test_style_guide_captures_authors(self):
        text = read(REPO / "skills" / "cf-style-guide" / "SKILL.md")
        self.assertIn("Capture Author Profiles", text)


class TestAeoCheckSkill(unittest.TestCase):
    """cf-aeo-check closes the brief's pre-production loop. It must stay honest
    about engine coverage and keep its cross-skill routing intact."""

    SKILL = REPO / "skills" / "cf-aeo-check" / "SKILL.md"

    def test_skill_ships_with_correct_frontmatter(self):
        self.assertTrue(self.SKILL.exists(), "cf-aeo-check skill missing")
        text = read(self.SKILL)
        m = re.search(r"^name:\s*(.+?)\s*$", text, re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), "cf-aeo-check")
        self.assertIn("description:", text)

    def test_skill_is_honest_about_engine_coverage(self):
        text = read(self.SKILL)
        self.assertIn("cannot measure directly", text,
                      "the honest-scope section is the skill's contract — keep it")
        self.assertIn("google-only", text)
        self.assertIn("Never present an estimate as a measurement", text)

    def test_routing_targets_exist(self):
        text = read(self.SKILL)
        for target in ("cf-brief", "content-refresh", "cf-audit", "cf-publish"):
            with self.subTest(target=target):
                self.assertIn(f"/contentforge:{target}", text,
                              f"cf-aeo-check lost its routing to {target}")
        # every relative link must resolve on disk
        for m in re.finditer(r"\]\((\.\./[^)#]+)", text):
            link = (self.SKILL.parent / m.group(1)).resolve()
            self.assertTrue(link.exists(), f"broken link in cf-aeo-check: {m.group(1)}")


class TestNoParallelBatchClaims(unittest.TestCase):
    """batch-process is sequential and checkpointed by design (09-batch-orchestrator:
    "No concurrency"). Twelve skills advertised it as parallel, which is a promise
    the system cannot keep."""

    ALLOWED = (
        "parallel structure", "parallel h2", "parallelism", "parallel construction",
        "no concurrency", "do not claim or attempt parallel",
        "does not run them concurrently", '"parallel" batch',
    )

    def test_no_skill_or_agent_advertises_parallel_batch(self):
        offenders = []
        for p in list(SKILLS.glob("*/SKILL.md")) + list(AGENTS.glob("*.md")):
            for i, line in enumerate(read(p).splitlines(), 1):
                low = line.lower()
                if "parallel" not in low and "concurrent" not in low:
                    continue
                if any(a in low for a in self.ALLOWED):
                    continue
                offenders.append(f"{p.parent.name}/{p.name}:{i}: {line.strip()[:90]}")
        self.assertEqual(offenders, [],
                         "batch processing is sequential by design; these claim otherwise:\n"
                         + "\n".join(offenders))


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
