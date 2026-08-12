#!/usr/bin/env python3
"""
rename_readiness.py — Make renaming this plugin a day's mechanical work, not a
week's archaeology.

WHY THIS EXISTS
---------------
The plugin's name appears ~1,500 times across ~130 files, in materially
different ROLES: manifest identity fields that platforms read, `contentforge:`
namespace references that agent dispatch resolves at runtime, `cf-` skill
directory names users type, repository URLs, and plain prose. A rename that
treats those as one find/replace breaks dispatch; a rename that misses a class
ships a plugin that half-answers to its old name. This script inventories
every occurrence BY ROLE, checks the invariants that keep a future rename
mechanical, and emits an ordered rename plan when given a new name.

It deliberately suggests no names. Choosing the name is the maintainer's;
keeping the rename cheap is this script's.

Usage:
    python scripts/rename_readiness.py --report
    python scripts/rename_readiness.py --check          # invariants only; exit 1 on violation
    python scripts/rename_readiness.py --plan --new-name acmeforge [--new-prefix af]

Stdlib only. Read-only: this script never edits a file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NAME = "contentforge"
PREFIX = "cf-"

SCAN_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".js", ".ts", ".txt", ".toml"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".pytest_cache"}

# Identity fields platforms actually read — the highest-stakes class.
MANIFEST_FILES = (
    ".claude-plugin/plugin.json", "package.json", "plugin.yaml",
    "gemini-extension.json", "openclaw.plugin.json",
    ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json",
    ".github/plugin/plugin.json",
)

NAMESPACE_RE = re.compile(rf"\b{NAME}:[a-z0-9][a-z0-9-]*")
REPO_URL_RE = re.compile(rf"github\.com/[A-Za-z0-9-]+/{NAME}", re.I)
PREFIX_RE = re.compile(rf"\b{re.escape(PREFIX)}[a-z][a-z0-9-]*")
NAME_RE = re.compile(NAME, re.I)
# A rename with variant spellings in the tree cannot be mechanical: the name
# split by a space, hyphen, or underscore must never appear anywhere. The
# pattern is assembled at runtime so this file stays clean under its own scan
# (same needle discipline as the source-anonymity guard).
_HALVES = ("content", "forge")
VARIANT_RE = re.compile(_HALVES[0] + r"[ _-]" + _HALVES[1], re.I)


def scan_files():
    for f in sorted(REPO.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in SCAN_SUFFIXES:
            continue
        if any(p in f.parts for p in SKIP_PARTS):
            continue
        yield f.relative_to(REPO).as_posix(), f.read_text(encoding="utf-8", errors="replace")


def classify():
    """Count occurrences of the plugin identity by ROLE."""
    counts = defaultdict(int)
    files = defaultdict(set)
    variants = []
    for rel, text in scan_files():
        for m in VARIANT_RE.finditer(text):
            # URLs to the real repo are canonical, not variants
            variants.append(f"{rel}: ...{text[max(0, m.start()-30):m.end()+30]!r}...")
        ns = len(NAMESPACE_RE.findall(text))
        urls = len(REPO_URL_RE.findall(text))
        prefix = len(PREFIX_RE.findall(text))
        total = len(NAME_RE.findall(text))
        if rel in MANIFEST_FILES and total:
            counts["manifest-identity"] += total
            files["manifest-identity"].add(rel)
            continue
        if ns:
            counts["namespace-refs"] += ns
            files["namespace-refs"].add(rel)
        if urls:
            counts["repo-urls"] += urls
            files["repo-urls"].add(rel)
        if prefix:
            counts["skill-prefix-refs"] += prefix
            files["skill-prefix-refs"].add(rel)
        prose = total - ns - urls
        if prose > 0:
            counts["prose"] += prose
            files["prose"].add(rel)
    skill_dirs = sorted(d.name for d in (REPO / "skills").iterdir()
                        if d.is_dir() and d.name.startswith(PREFIX))
    return counts, files, variants, skill_dirs


def invariant_violations():
    """Conditions that would make a future rename NON-mechanical."""
    _, _, variants, _ = classify()
    violations = [f"variant spelling (breaks find/replace): {v}" for v in variants]
    for rel in MANIFEST_FILES:
        p = REPO / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if rel.endswith(".json"):
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                violations.append(f"{rel}: unparseable manifest")
                continue
            name = data.get("name", "")
            if NAME not in name.lower():
                violations.append(f"{rel}: name field {name!r} does not carry the canonical name")
    return violations


def build_plan(new_name, new_prefix):
    counts, files, _, skill_dirs = classify()
    steps = [
        {"step": 1, "class": "manifest-identity",
         "action": f"Set every manifest name field to '{new_name}' "
                   f"({counts['manifest-identity']} occurrences in {len(files['manifest-identity'])} files). "
                   "Platforms read these — do them first and atomically."},
        {"step": 2, "class": "namespace-refs",
         "action": f"Replace '{NAME}:' dispatch/slash namespace with '{new_name}:' "
                   f"({counts['namespace-refs']} occurrences in {len(files['namespace-refs'])} files). "
                   "Agent dispatch resolves these at runtime — the pipeline-graph tests "
                   "verify every agent is still dispatched after the sweep."},
        {"step": 3, "class": "skill-dirs",
         "action": (f"git mv the {len(skill_dirs)} '{PREFIX}*' skill directories to the "
                    f"'{new_prefix}' prefix and sweep '{PREFIX}' references "
                    f"({counts['skill-prefix-refs']} occurrences)."
                    if new_prefix else
                    f"Keeping the '{PREFIX}' prefix (no --new-prefix given) — "
                    f"{len(skill_dirs)} skill dirs untouched.")},
        {"step": 4, "class": "repo-urls",
         "action": f"Update repository URLs after the GitHub rename "
                   f"({counts['repo-urls']} occurrences in {len(files['repo-urls'])} files). "
                   "GitHub redirects the old URL, so this can trail by a release."},
        {"step": 5, "class": "prose",
         "action": f"Sweep prose mentions ({counts['prose']} occurrences in "
                   f"{len(files['prose'])} files). CHANGELOG historical entries keep the "
                   "old name — history is history."},
        {"step": 6, "class": "external",
         "action": "Marketplace repo: rename the listing in all 4 marketplace.json files "
                   "same-day; users must uninstall + purge cache + reinstall (uninstall "
                   "does not purge cache). GitHub About/description and pinned repos are "
                   "UI-only. Announce the old->new mapping in both READMEs."},
        {"step": 7, "class": "verify",
         "action": "Run the full suite (pipeline-graph catches dispatch breaks, "
                   "release-consistency catches manifest drift, rename_readiness --check "
                   "must report zero variants of BOTH names), then the install-verify ritual."},
    ]
    return {"current_name": NAME, "new_name": new_name,
            "new_prefix": new_prefix or PREFIX, "steps": steps}


def main() -> int:
    ap = argparse.ArgumentParser(description="Inventory, check, and plan a plugin rename.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--report", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--plan", action="store_true")
    ap.add_argument("--new-name")
    ap.add_argument("--new-prefix")
    args = ap.parse_args()

    if args.report:
        counts, files, variants, skill_dirs = classify()
        print(json.dumps({
            "canonical_name": NAME,
            "skill_prefix": PREFIX,
            "classes": {k: {"occurrences": counts[k], "files": len(files[k])}
                        for k in sorted(counts)},
            "prefixed_skill_dirs": len(skill_dirs),
            "variant_spellings": variants,
        }, indent=2))
        return 0
    if args.check:
        violations = invariant_violations()
        if violations:
            print("RENAME-READINESS VIOLATIONS:", file=sys.stderr)
            for v in violations:
                print(f"  {v}", file=sys.stderr)
            return 1
        print("rename-ready: no variant spellings, manifests canonical")
        return 0
    if args.plan:
        if not args.new_name or not re.fullmatch(r"[a-z][a-z0-9-]{2,30}", args.new_name):
            print("ERROR: --plan requires --new-name (lowercase slug, 3-31 chars).",
                  file=sys.stderr)
            return 2
        print(json.dumps(build_plan(args.new_name, args.new_prefix), indent=2))
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
