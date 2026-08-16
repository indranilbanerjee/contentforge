"""The pipeline DAG as data — and the drift guard that makes it load-bearing.

config/pipeline-graph.json is authoritative for the pipeline's shape. Before it
existed, the contract lived as prose in four places at once (the SKILL.md table,
the agent files, checkpoint-manager's PHASE_ORDER, run-audit's expectations) and
they drifted: v3.28 shipped "Phase 4 was asked to verify outline adherence
against an artifact its own INPUTS never gave it", and the 2026-07-30
interconnection audit found three agents no phase ever dispatched — both classes
invisible to every unit test because no machine-readable contract existed to
check against. These tests are that contract check, permanent.

Stdlib only.
"""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GRAPH = json.loads((REPO / "config" / "pipeline-graph.json").read_text(encoding="utf-8"))

AGENT_FILES = {
    "1": "01-researcher.md",
    "2": "02-fact-checker.md",
    "3": "03-content-drafter.md",
    "3.5": "03.5-visual-asset-annotator.md",
    "4": "04-scientific-validator.md",
    "5": "05-structurer-proofreader.md",
    "6": "06-seo-geo-optimizer.md",
    "6.5": "06.5-humanizer.md",
    "7": "07-reviewer.md",
    "8": "08-output-manager.md",
}

ARTIFACT_RE = re.compile(r"\bphase-[\d.]+-[a-z-]+\.(?:md|json|txt|html)\b")


def _load_script(name, filename):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def node_files(node, key):
    """Filenames (not tokens) in a node's reads or writes."""
    out = []
    for item in node.get(key, []):
        if isinstance(item, dict):
            out.append(item["file"])
        elif isinstance(item, str) and ":" in item:
            continue  # token (config:X) — handled by the caller, not a filename
        elif isinstance(item, str) and item.startswith("phase-"):
            out.append(item)
        elif isinstance(item, str) and item.endswith((".md", ".json", ".txt", ".html")):
            out.append(item)
    return out


class TestGraphShape(unittest.TestCase):
    def test_phase_order_matches_nodes(self):
        self.assertEqual(GRAPH["phase_order"], list(GRAPH["nodes"].keys()))

    def test_phase_order_matches_checkpoint_manager(self):
        cm = _load_script("cf_cm_graph", "checkpoint-manager.py")
        self.assertEqual(GRAPH["phase_order"], cm.PHASE_ORDER,
                         "pipeline-graph.json and checkpoint-manager.py disagree "
                         "on the phase order — one of them shipped a phase the "
                         "other has never heard of")

    def test_phase_order_matches_run_audit(self):
        ra = _load_script("cf_ra_graph", "run-audit.py")
        self.assertEqual(GRAPH["phase_order"], ra.PHASE_ORDER)

    def test_loop_budgets_match_skill_prose(self):
        skill = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        b = GRAPH["loop_budgets"]
        self.assertIn(f"max {b['per_edge']} loops per edge", skill)
        self.assertIn(f"max {b['total_per_run']} loops total", skill)

    def test_every_pipeline_agent_exists_and_is_reachable(self):
        """The 2026-07-30 finding, inverted: every graph node names an agent
        file that exists, and every NN-prefixed pipeline agent file is a graph
        node — no orphan phases, no ghost agents."""
        for phase, fname in AGENT_FILES.items():
            self.assertTrue((REPO / "agents" / fname).is_file(),
                            f"graph phase {phase} maps to missing agents/{fname}")
        pipeline_named = {f.name for f in (REPO / "agents").glob("[0-9]*.md")}
        extra = pipeline_named - set(AGENT_FILES.values())
        # 09/10/11 are post-pipeline by contract (batch, social, translator).
        allowed_post = {"09-batch-orchestrator.md", "10-social-adapter.md",
                        "11-translator.md"}
        self.assertEqual(extra - allowed_post, set(),
                         f"numbered agent files outside the graph: {extra - allowed_post}")


class TestArtifactDrift(unittest.TestCase):
    """Every artifact an agent file mentions must be in its node's edges, and
    every non-optional read must be mentioned — the v3.28 class, both ways."""

    def test_agent_mentions_every_required_read(self):
        missing = []
        for phase, fname in AGENT_FILES.items():
            text = (REPO / "agents" / fname).read_text(encoding="utf-8")
            node = GRAPH["nodes"][phase]
            wanted = node_files(node, "reads")
            # config:X tokens resolve to the config/X path form agents use.
            wanted += [t.split(":", 1)[1] for t in node.get("reads", [])
                       if isinstance(t, str) and t.startswith("config:")]
            for f in wanted:
                if f not in text:
                    missing.append(f"agents/{fname} never mentions its contracted "
                                   f"input {f}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_agent_mentions_every_write(self):
        missing = []
        for phase, fname in AGENT_FILES.items():
            text = (REPO / "agents" / fname).read_text(encoding="utf-8")
            for item in GRAPH["nodes"][phase].get("writes", []):
                f = item["file"] if isinstance(item, dict) else item
                if f.startswith("*"):
                    continue
                if isinstance(item, dict) and item.get("optional"):
                    continue
                if f not in text:
                    missing.append(f"agents/{fname} never mentions its contracted "
                                   f"output {f}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_no_agent_mentions_an_artifact_outside_its_edges(self):
        """An artifact named in an agent file that is neither read nor written
        by that phase is contract drift — the exact v3.28 shape. The reviewer
        (ALL_PRIOR_ARTIFACTS) and the orchestrator SKILL are exempt by design."""
        drift = []
        for phase, fname in AGENT_FILES.items():
            node = GRAPH["nodes"][phase]
            if "ALL_PRIOR_ARTIFACTS" in node.get("reads", []):
                continue
            allowed = set(node_files(node, "reads")) | set(
                item["file"] if isinstance(item, dict) else item
                for item in node.get("writes", []))
            allowed |= {i["file"] for i in node.get("reads", [])
                        if isinstance(i, dict)}
            text = (REPO / "agents" / fname).read_text(encoding="utf-8")
            for m in set(ARTIFACT_RE.findall(text)):
                if m not in allowed:
                    drift.append(f"agents/{fname} mentions {m}, which its graph "
                                 f"node neither reads nor writes")
        self.assertEqual(drift, [], "\n".join(sorted(drift)))

    def test_skill_contract_table_names_every_write(self):
        skill = (REPO / "skills" / "contentforge" / "SKILL.md").read_text(encoding="utf-8")
        missing = []
        for phase, node in GRAPH["nodes"].items():
            for item in node.get("writes", []):
                f = item["file"] if isinstance(item, dict) else item
                if f.startswith("*"):
                    continue
                if f not in skill:
                    missing.append(f"SKILL.md contract never names phase {phase} "
                                   f"output {f}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_run_audit_artifacts_exist_in_graph(self):
        """Every artifact filename run-audit.py hardcodes must be a graph edge —
        the auditor may not expect a file no phase is contracted to write."""
        src = (REPO / "scripts" / "run-audit.py").read_text(encoding="utf-8")
        graph_files = set()
        for node in GRAPH["nodes"].values():
            graph_files |= set(node_files(node, "reads"))
            for item in node.get("writes", []):
                graph_files.add(item["file"] if isinstance(item, dict) else item)
        missing = [m for m in set(ARTIFACT_RE.findall(src)) if m not in graph_files]
        self.assertEqual(sorted(missing), [],
                         f"run-audit.py expects artifacts the graph never grants: {missing}")


class TestGuardCanFail(unittest.TestCase):
    def test_artifact_regex_matches_the_real_names(self):
        for name in ("phase-3.5-visual-manifest.json", "phase-6.5-humanized.md",
                     "phase-0.5-title.txt", "phase-6.5-review-sheet.html"):
            self.assertTrue(ARTIFACT_RE.search(f"reads {name} early"), name)

    def test_node_files_reads_both_shapes(self):
        node = {"reads": ["phase-1-research.md", "brand_profile",
                          {"file": "source-draft.md", "optional": True}],
                "writes": [{"file": "phase-2-factcheck.md"}]}
        self.assertEqual(node_files(node, "reads"),
                         ["phase-1-research.md", "source-draft.md"])


if __name__ == "__main__":
    unittest.main()
