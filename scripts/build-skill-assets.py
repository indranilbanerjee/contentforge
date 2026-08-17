#!/usr/bin/env python3
"""build-skill-assets.py — package hero skills as claude.ai-uploadable .skill files.

Usage (from repo root):
    python scripts/build-skill-assets.py            # build every skill in the manifest
    python scripts/build-skill-assets.py --skill cf-brief
    python scripts/build-skill-assets.py --check    # portability scan only, build nothing

Reads config/skill-assets.json. For each listed skill, produces
dist/<skill>.skill — a zip with a single top-level <skill>/ directory
containing the skill's own files plus each declared extra file at its
repo-relative path, so references like `templates/content-brief-template.md`
in the SKILL.md prose resolve against the skill root after upload.

Refuses to build when a SKILL.md references ${CLAUDE_PLUGIN_ROOT} (there is
no plugin root on claude.ai) or a repo-level path that is neither in-skill
nor declared in the manifest. claude.ai caps uploads at 200 files per skill;
the cap is enforced from the manifest, not hardcoded here.

Zips are deterministic: fixed timestamps, sorted entries — rebuilding the
same tree yields byte-identical assets.

Exit codes: 0 = built/clean, 1 = portability or structure violation, 2 = usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "config" / "skill-assets.json"
DIST = REPO / "dist"

# Repo-relative path tokens that SKILL.md prose can reference. Trailing
# punctuation from sentences is stripped before resolution.
PATH_TOKEN_RE = re.compile(r"\b((?:config|templates|scripts|references)/[A-Za-z0-9_./-]+)")
FORBIDDEN_TOKEN = "CLAUDE_PLUGIN_ROOT"

# Never package editor/OS litter even if it appears in a skill dir.
SKIP_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db", "desktop.ini"}

ZIP_EPOCH = (2020, 1, 1, 0, 0, 0)


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _skill_files(skill_dir: Path) -> list[Path]:
    return sorted(
        p for p in skill_dir.rglob("*")
        if p.is_file() and not (set(p.relative_to(skill_dir).parts) & SKIP_NAMES)
    )


def scan_portability(skill: str, extra_files: list[str]) -> list[str]:
    """Return a list of violations (empty = portable)."""
    skill_dir = REPO / "skills" / skill
    skill_md = skill_dir / "SKILL.md"
    problems: list[str] = []
    if not skill_md.exists():
        return [f"{skill}: skills/{skill}/SKILL.md does not exist"]

    text = skill_md.read_text(encoding="utf-8")
    if FORBIDDEN_TOKEN in text:
        problems.append(
            f"{skill}: SKILL.md references ${{{FORBIDDEN_TOKEN}}} — there is no "
            "plugin root on claude.ai; this skill cannot ship as a .skill asset"
        )

    declared = set(extra_files)
    for raw in set(PATH_TOKEN_RE.findall(text)):
        token = raw.rstrip(".,;:)")
        if token in declared:
            continue
        if token.endswith("/"):
            if any(d.startswith(token) for d in declared) or (skill_dir / token).is_dir():
                continue
            problems.append(f"{skill}: SKILL.md references directory '{token}' "
                            "with no declared or in-skill match")
            continue
        if (skill_dir / token).exists():
            continue  # in-skill reference (references/ contract) — ships with the dir
        problems.append(f"{skill}: SKILL.md references '{token}' which is neither "
                        "inside the skill dir nor declared in config/skill-assets.json")

    for extra in extra_files:
        if not (REPO / extra).exists():
            problems.append(f"{skill}: declared extra file '{extra}' does not exist in the repo")
    return problems


def build_skill(skill: str, extra_files: list[str], cap: int) -> Path:
    skill_dir = REPO / "skills" / skill
    entries: list[tuple[str, Path]] = []
    for f in _skill_files(skill_dir):
        entries.append((f"{skill}/{f.relative_to(skill_dir).as_posix()}", f))
    for extra in sorted(extra_files):
        entries.append((f"{skill}/{extra}", REPO / extra))

    md_count = sum(1 for arc, _ in entries if Path(arc).name == "SKILL.md")
    if md_count != 1:
        raise SystemExit(f"error: {skill}: expected exactly one SKILL.md in bundle, found {md_count}")
    if len(entries) > cap:
        raise SystemExit(f"error: {skill}: {len(entries)} files exceeds claude.ai's cap of {cap}")

    DIST.mkdir(exist_ok=True)
    out = DIST / f"{skill}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, src in sorted(entries):
            info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, src.read_bytes())
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", help="build only this skill (default: all in manifest)")
    parser.add_argument("--check", action="store_true",
                        help="run the portability scan only; build nothing")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    skills: dict = manifest["skills"]
    cap = manifest["claude_ai_upload_cap_files"]
    if args.skill:
        if args.skill not in skills:
            print(f"error: '{args.skill}' is not in config/skill-assets.json", file=sys.stderr)
            return 2
        skills = {args.skill: skills[args.skill]}

    all_problems: list[str] = []
    for name, spec in skills.items():
        all_problems.extend(scan_portability(name, spec.get("extra_files", [])))
    if all_problems:
        print("portability violations — nothing built:", file=sys.stderr)
        for p in all_problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    if args.check:
        print(f"portability scan clean for {len(skills)} skill(s)")
        return 0

    for name, spec in skills.items():
        out = build_skill(name, spec.get("extra_files", []), cap)
        with zipfile.ZipFile(out) as zf:
            n = len(zf.namelist())
        print(f"built {out.relative_to(REPO)} ({n} files, {out.stat().st_size:,} bytes)")
    print("upload via claude.ai > Settings > Capabilities (enable Code execution) "
          "> Customize > Skills > Upload skill")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
