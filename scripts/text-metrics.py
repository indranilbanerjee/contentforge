#!/usr/bin/env python3
"""
text-metrics.py
===============
Deterministic text metrics for the ContentForge pipeline quality gates.
Stdlib only. Used by the orchestrator (SKILL.md) at the Phase 5 / 6 / 6.5
gates so burstiness, Flesch-Kincaid, keyword placement, and answer-first
structure checks are measured, not guessed.

Usage:
    python text-metrics.py --file draft.md
    python text-metrics.py --file draft.md --keyword "ai in healthcare"

Output (JSON):
    word_count, sentence_count, avg_sentence_len, sentence_len_stdev,
    burstiness           — stdev/mean of sentence lengths, capped at 1.0
                           (>=0.7 is the humanizer target)
    fk_grade             — Flesch-Kincaid grade level (syllable heuristic)
    keyword_count, keyword_density_pct,
    keyword_placements   — {in_title, in_first_100_words,
                            h2_count_with_keyword, in_conclusion}
    structured_elements  — {qa_headers, numbered_lists, bullet_lists,
                            tables, definition_patterns}
                           (consumed by the Phase 6 → 6.5 structure-manifest
                            preservation check)

Robust to markdown: frontmatter, code fences, tables, images, links, and
emphasis markers are stripped/normalised before prose analysis.
"""
from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

_BULLET_RE = re.compile(r"^\s*[-*+]\s+\S")
_ORDERED_RE = re.compile(r"^\s*\d+[.)]\s+\S")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_TABLE_SEP_RE = re.compile(r"^\|[-: |]+\|\s*$")
_DEF_BOLD_RE = re.compile(r"^\s*\*\*[^*\n]{2,80}\*\*\s*[:—–-]\s+\S")
_DEF_SENT_RE = re.compile(r"\b(?:is defined as|refers to|means|is a|is an|is the|are the|are a)\b", re.I)


def _strip_frontmatter(text: str):
    title = None
    if text.lstrip().startswith("---"):
        stripped = text.lstrip()
        end = stripped.find("\n---", 3)
        if end > 0:
            fm = stripped[3:end]
            m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
            if m:
                title = m.group(1).strip()
            text = stripped[end + 4:]
    return text, title


def _inline_to_plain(s: str) -> str:
    """Reduce inline markdown to plain prose text."""
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", s)               # images
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)            # links -> anchor
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.DOTALL)        # html comments
    s = re.sub(r"`([^`]*)`", r"\1", s)                        # inline code
    s = re.sub(r"(\*\*\*|___|\*\*|__|\*|_)(?=\S)", "", s)     # opening emphasis
    s = re.sub(r"(?<=\S)(\*\*\*|___|\*\*|__|\*|_)", "", s)    # closing emphasis
    return s


def _syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    count = len(groups)
    if w.endswith("e") and count > 1 and not w.endswith(("le", "ee", "ye")):
        count -= 1
    return max(count, 1)


def analyze(md_text: str, keyword: str | None = None) -> dict:
    md_text, fm_title = _strip_frontmatter(md_text)
    lines = md_text.split("\n")

    headings: list[tuple[int, str]] = []      # (level, plain text)
    prose_parts: list[str] = []               # paragraph/quote/list-item text
    structured = {"qa_headers": 0, "numbered_lists": 0, "bullet_lists": 0,
                  "tables": 0, "definition_patterns": 0}
    section_first_sentences: list[str] = []   # first sentence after each heading

    in_code = False
    in_bullet = in_ordered = in_table = False
    awaiting_first_sentence = False

    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()
        if not stripped:
            in_bullet = in_ordered = in_table = False
            continue

        m = _HEADING_RE.match(stripped)
        if m:
            level = len(m.group(1))
            htext = _inline_to_plain(m.group(2)).strip()
            headings.append((level, htext))
            if level in (2, 3) and htext.endswith("?"):
                structured["qa_headers"] += 1
            in_bullet = in_ordered = in_table = False
            awaiting_first_sentence = True
            continue

        if stripped.startswith("|"):
            if not in_table and not _TABLE_SEP_RE.match(stripped):
                structured["tables"] += 1
            in_table = True
            in_bullet = in_ordered = False
            continue
        in_table = False

        if _BULLET_RE.match(line):
            if not in_bullet:
                structured["bullet_lists"] += 1
            in_bullet, in_ordered = True, False
            item = _inline_to_plain(re.sub(r"^\s*[-*+]\s+", "", line)).strip()
            if item:
                prose_parts.append(item)
            continue
        if _ORDERED_RE.match(line):
            if not in_ordered:
                structured["numbered_lists"] += 1
            in_ordered, in_bullet = True, False
            item = _inline_to_plain(re.sub(r"^\s*\d+[.)]\s+", "", line)).strip()
            if item:
                prose_parts.append(item)
            continue
        in_bullet = in_ordered = False

        if re.match(r"^\s*([-*_])\1{2,}\s*$", stripped):
            continue  # horizontal rule

        if _DEF_BOLD_RE.match(line):
            structured["definition_patterns"] += 1

        text = _inline_to_plain(stripped.lstrip("> ")).strip()
        if text:
            prose_parts.append(text)
            if awaiting_first_sentence:
                first = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
                section_first_sentences.append(first)
                awaiting_first_sentence = False

    prose = " ".join(prose_parts)
    heading_words = sum(len(h[1].split()) for h in headings)

    # Sentences: split prose on terminal punctuation.
    raw_sentences = re.split(r"(?<=[.!?])\s+", prose)
    sentences = [s for s in (x.strip() for x in raw_sentences) if len(s.split()) >= 1]
    sent_lens = [len(s.split()) for s in sentences]

    words = prose.split()
    word_count = len(words) + heading_words
    sentence_count = len(sentences)
    avg_len = (sum(sent_lens) / sentence_count) if sentence_count else 0.0
    stdev = statistics.pstdev(sent_lens) if sentence_count > 1 else 0.0
    burstiness = min(1.0, round(stdev / avg_len, 3)) if avg_len else 0.0

    # Flesch-Kincaid grade
    syllable_total = sum(_syllables(w) for w in words)
    if sentence_count and words:
        fk = (0.39 * (len(words) / sentence_count)
              + 11.8 * (syllable_total / len(words)) - 15.59)
        fk_grade = round(max(fk, 0.0), 1)
    else:
        fk_grade = 0.0

    # Definition patterns: also count section-opening sentences that define.
    for first in section_first_sentences:
        if _DEF_SENT_RE.search(first):
            structured["definition_patterns"] += 1

    result = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_len": round(avg_len, 2),
        "sentence_len_stdev": round(stdev, 2),
        "burstiness": burstiness,
        "fk_grade": fk_grade,
        "structured_elements": structured,
    }

    if keyword:
        kw = keyword.strip().lower()
        kw_re = re.compile(r"(?<!\w)" + re.escape(kw).replace(r"\ ", r"\s+") + r"(?!\w)", re.I)
        full_plain = (prose + " " + " ".join(h[1] for h in headings)).lower()
        kw_count = len(kw_re.findall(full_plain))
        density = round((kw_count / word_count * 100), 2) if word_count else 0.0

        title_text = next((h[1] for h in headings if h[0] == 1), None) or fm_title or ""
        first_100 = " ".join(words[:100]).lower()
        h2s = [h[1] for h in headings if h[0] == 2]
        conclusion_zone = " ".join(words[-200:]).lower() if words else ""
        # Prefer an explicit conclusion-ish section when present
        for i, (lvl, htext) in enumerate(headings):
            if lvl == 2 and re.search(r"\b(conclusion|final thoughts|takeaway|summary|bottom line)\b",
                                      htext, re.I):
                conclusion_zone = (htext + " " + conclusion_zone).lower()
                break

        result.update({
            "keyword": keyword,
            "keyword_count": kw_count,
            "keyword_density_pct": density,
            "keyword_placements": {
                "in_title": bool(kw_re.search(title_text.lower())),
                "in_first_100_words": bool(kw_re.search(first_100)),
                "h2_count_with_keyword": sum(1 for h in h2s if kw_re.search(h.lower())),
                "in_conclusion": bool(kw_re.search(conclusion_zone)),
            },
        })

    return result


def main():
    parser = argparse.ArgumentParser(description="ContentForge text metrics (burstiness, FK grade, keyword placement, structure)")
    parser.add_argument("--file", required=True, help="Markdown (or plain text) file to analyze")
    parser.add_argument("--keyword", default=None, help="Primary keyword for placement/density checks")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    if not path.is_file():
        _common.finish({"error": f"file not found: {path}",
                        "recovery": "Pass the path to the phase artifact, e.g. the Phase 6.5 humanized draft."})
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        _common.finish({"error": f"could not read {path}: {exc}"})

    result = analyze(text, keyword=args.keyword)
    result["file"] = str(path)
    _common.finish(result)


if __name__ == "__main__":
    main()
