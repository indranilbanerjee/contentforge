"""The per-skill references/ contract.

v3.19.1 moved illustrative material (transcripts, worked examples, troubleshooting)
out of oversized SKILL.md bodies into `skills/<name>/references/*.md`, leaving
section-scoped "read this before step X" pointers behind. Those pointers are now the
only path to that content, so nothing may silently break them:

  - a pointer naming a file that no longer exists costs the agent a failed Read
  - a pointer naming a section heading that was renamed sends it to the wrong content
  - a reference file nobody points at is dead weight shipped to every install
  - a pointer missing "(in this skill's directory)" is ambiguous: the plugin ROOT also
    has a references/ directory, and the agent resolves the path from that phrase
  - content duplicated between a body and its reference gives the pair two sources of
    truth, which drift apart on the next edit
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"

# `references/foo.md` — the pointer as it appears in a skill body.
POINTER_RE = re.compile(r"`references/([A-Za-z0-9._-]+\.md)`")
# ...optionally followed by an explicit section citation: section "Some Heading"
SECTION_RE = re.compile(r"`references/([A-Za-z0-9._-]+\.md)`[^\n]*?section \"([^\"]+)\"")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
DISAMBIGUATOR = "(in this skill's directory)"


def skill_bodies():
    """(skill_dir, SKILL.md text) for every skill that carries a references/ dir."""
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_dir.is_dir() and skill_md.exists():
            yield skill_dir, skill_md.read_text(encoding="utf-8")


class TestReferencePointersResolve(unittest.TestCase):
    def test_every_pointer_names_an_existing_file(self):
        broken = []
        checked = 0
        for skill_dir, text in skill_bodies():
            for m in POINTER_RE.finditer(text):
                checked += 1
                if not (skill_dir / "references" / m.group(1)).exists():
                    broken.append(f"{skill_dir.name} -> references/{m.group(1)}")
        self.assertEqual(broken, [], f"Dead reference pointers: {broken}")
        self.assertGreater(checked, 0, "No reference pointers found — did the refactor regress?")

    def test_every_cited_section_exists_in_its_file(self):
        missing = []
        checked = 0
        for skill_dir, text in skill_bodies():
            for m in SECTION_RE.finditer(text):
                ref = skill_dir / "references" / m.group(1)
                if not ref.exists():
                    continue  # already reported by the pointer test
                checked += 1
                headings = [h.strip().lower()
                            for h in HEADING_RE.findall(ref.read_text(encoding="utf-8"))]
                if m.group(2).strip().lower() not in headings:
                    missing.append(f"{skill_dir.name}/{m.group(1)} :: \"{m.group(2)}\"")
        self.assertEqual(missing, [], f"Cited sections with no matching heading: {missing}")
        self.assertGreater(checked, 0, "No section-scoped pointers found")

    def test_no_orphan_reference_files(self):
        orphans = []
        for skill_dir, text in skill_bodies():
            cited = set(POINTER_RE.findall(text))
            for ref in sorted((skill_dir / "references").glob("*.md")):
                if ref.name not in cited:
                    orphans.append(f"{skill_dir.name}/references/{ref.name}")
        self.assertEqual(orphans, [], f"Reference files nothing points at: {orphans}")

    def test_pointers_carry_the_this_skill_disambiguator(self):
        """The plugin root has its own references/ — the phrase is what disambiguates."""
        undisambiguated = []
        for skill_dir, text in skill_bodies():
            for m in POINTER_RE.finditer(text):
                window = text[m.end():m.end() + 120]
                if DISAMBIGUATOR not in window:
                    undisambiguated.append(f"{skill_dir.name} -> references/{m.group(1)}")
        self.assertEqual(
            undisambiguated, [],
            "Pointers missing \"" + DISAMBIGUATOR + "\": " + str(undisambiguated))


class TestNoBodyReferenceDuplication(unittest.TestCase):
    """A block living in both the body and its reference has two sources of truth.

    v3.19.1 shipped one such block (cf-style-guide's manual-input prompt list, inlined
    back into the body for the E-E-A-T authorless opt-out while a copy stayed in the
    reference). It was deduped when this guard landed; this keeps the next one out.
    """

    RUN_LENGTH = 5  # consecutive identical content lines = copy-paste, not coincidence

    @staticmethod
    def _content_lines(text):
        """Substantive lines only — blanks, headings and fences match across any two files."""
        out = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith("```"):
                continue
            out.append(re.sub(r"\s+", " ", line))
        return out

    def test_no_shared_run_of_lines(self):
        dupes = []
        for skill_dir, text in skill_bodies():
            body = self._content_lines(text)
            body_runs = {tuple(body[i:i + self.RUN_LENGTH])
                         for i in range(len(body) - self.RUN_LENGTH + 1)}
            for ref in sorted((skill_dir / "references").glob("*.md")):
                lines = self._content_lines(ref.read_text(encoding="utf-8"))
                for i in range(len(lines) - self.RUN_LENGTH + 1):
                    run = tuple(lines[i:i + self.RUN_LENGTH])
                    if run in body_runs:
                        dupes.append(f"{skill_dir.name}/references/{ref.name}: {run[0][:60]!r}...")
                        break
        self.assertEqual(
            dupes, [],
            f"Content duplicated between skill body and its reference (pick one home): {dupes}")


if __name__ == "__main__":
    unittest.main()
