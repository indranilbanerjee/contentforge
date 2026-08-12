"""The plugin must stay one mechanical find/replace away from a rename.

The maintainer plans to rename this plugin; the name's ~1,500 occurrences are
only safe if they stay CANONICAL — one spelling, classified by role, with the
manifests parseable and the namespace uniform. These tests keep that true
release after release, so the eventual rename is a day of scripted work
instead of a week of archaeology. (No name is suggested anywhere — choosing it
is the maintainer's; keeping it cheap is ours.)
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "rename_readiness.py"

sys.path.insert(0, str(REPO / "scripts"))
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("rename_readiness", SCRIPT)
rename_readiness = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(rename_readiness)


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, timeout=120)


class TestRenameReadiness(unittest.TestCase):
    def test_check_passes_on_the_live_tree(self):
        proc = run("--check")
        self.assertEqual(proc.returncode, 0,
                         "rename-readiness invariants violated:\n" + proc.stderr)

    def test_report_classifies_the_identity_surface(self):
        proc = run("--report")
        self.assertEqual(proc.returncode, 0)
        report = json.loads(proc.stdout)
        classes = report["classes"]
        # The high-stakes classes must be present and non-trivial: if these
        # counts collapse, the scanner regressed, not the repo.
        self.assertGreaterEqual(classes["manifest-identity"]["occurrences"], 8)
        self.assertGreaterEqual(classes["namespace-refs"]["occurrences"], 100)
        self.assertEqual(report["variant_spellings"], [])
        self.assertGreater(report["prefixed_skill_dirs"], 10)

    def test_plan_orders_manifests_before_prose(self):
        proc = run("--plan", "--new-name", "example-name")
        self.assertEqual(proc.returncode, 0)
        plan = json.loads(proc.stdout)
        classes_in_order = [s["class"] for s in plan["steps"]]
        self.assertLess(classes_in_order.index("manifest-identity"),
                        classes_in_order.index("prose"))
        blob = json.dumps(plan)
        self.assertIn("purge cache", blob, "plan must carry the cache-purge step")
        self.assertIn("pipeline-graph", blob, "plan must route verification through the suite")

    def test_plan_rejects_bad_names(self):
        self.assertEqual(run("--plan", "--new-name", "Bad Name!").returncode, 2)
        self.assertEqual(run("--plan").returncode, 2)

    def test_script_is_read_only(self):
        """The kit inventories and plans; it must never edit. If write calls
        appear in it, the design changed without changing this contract."""
        text = SCRIPT.read_text(encoding="utf-8")
        for needle in ("write_text", "open(", "shutil", "os.rename", "unlink"):
            self.assertNotIn(needle, text,
                             f"rename_readiness.py contains {needle!r} — it must stay read-only")

    # ── plant check ─────────────────────────────────────────────────

    def test_variant_detector_fires_on_planted_spelling(self):
        planted = "the " + "content" + " " + "forge" + " plugin"
        self.assertTrue(rename_readiness.VARIANT_RE.search(planted))
        self.assertIsNone(rename_readiness.VARIANT_RE.search("the contentforge plugin"))


if __name__ == "__main__":
    unittest.main()
