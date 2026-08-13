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
    python text-metrics.py --file draft.md --ai-tell-scan

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
    ai_tell_scan          — with --ai-tell-scan: deterministic Tier-1
                           detector-signal proxy (banned lexemes, aphorism
                           candidates, em-dashes per 1000 words, connective/
                           participial opener rates, uniform-run detection,
                           flagged sentences, an advisory_rating of
                           LOW/MODERATE/HIGH). Reads config/humanization-
                           patterns.json (detector_lexicon) and config/
                           scoring-thresholds.json (ai_tell_scan gate).
                           Advisory only — never a publish gate. See
                           references/ai-detection-signals.md.

Robust to markdown: frontmatter, code fences, tables, images, links, and
emphasis markers are stripped/normalised before prose analysis.
"""
from __future__ import annotations

import argparse
import json
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


def split_sentences(text: str) -> list[str]:
    """Split prose into sentences on terminal punctuation. The single
    sentence-splitting implementation for this module — reused by both
    analyze() (over stripped markdown prose) and ai_tell_scan() (over raw
    text) so metrics never drift between the two callers."""
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s for s in (x.strip() for x in raw) if len(s.split()) >= 1]


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
    sentences = split_sentences(prose)
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


def _load_detector_config():
    """Load the detector lexicon (Task 10, humanization-patterns.json) and
    the ai_tell_scan thresholds (Task 10, scoring-thresholds.json). Both
    ship under config/ relative to the plugin root (one level up from
    scripts/) — the same layout every other ContentForge config consumer
    expects."""
    cfg_dir = Path(__file__).resolve().parent.parent / "config"
    with open(cfg_dir / "humanization-patterns.json", encoding="utf-8") as f:
        lex = json.load(f)["detector_lexicon"]
    with open(cfg_dir / "scoring-thresholds.json", encoding="utf-8") as f:
        thr = json.load(f)["default"]["quality_gates"]["phase_6_5_humanizer"]["ai_tell_scan"]
    return lex, thr


def is_aphorism_candidate(sentence: str) -> bool:
    """Short declarative one-liner with zero grounding: <=9 words, no digit,
    no citation marker, no question, no mid-sentence capitalized entity."""
    s = sentence.strip()
    words = s.split()
    if not s or len(words) > 9 or s.endswith("?"):
        return False
    if any(ch.isdigit() for ch in s):
        return False
    if re.search(r"\((?:[A-Z][\w.]*,?\s*\d{4}|\d+)\)|\[\d+\]", s):
        return False
    if any(w[:1].isupper() for w in words[1:]):
        return False
    return s.endswith(".")


def ai_tell_scan(text: str) -> dict:
    """Deterministic Tier-1 detector-signal proxy scan. Advisory only, never
    a publish gate — see references/ai-detection-signals.md. Consumed by the
    humanizer (Step 7.5), reviewer (5.5), and the Completion Card."""
    lex, thr = _load_detector_config()
    sentences = split_sentences(text)
    words_total = max(1, len(re.findall(r"[\w'-]+", text)))
    per_k = 1000.0 / words_total

    lset = set(lex["llm_favored_words"])
    banned = sum(1 for w in re.findall(r"[A-Za-z'-]+", text) if w.lower() in lset)
    connectives = tuple(lex["connective_openers"])
    conn = sum(1 for s in sentences if s.strip().lower().startswith(connectives))
    part = sum(1 for s in sentences
               if (s.strip().split() or [""])[0].lower().endswith("ing"))
    em_dashes = text.count("—") + text.count(" -- ")

    flagged, aph = [], 0
    for i, s in enumerate(sentences):
        st = s.strip()
        if is_aphorism_candidate(s):
            aph += 1
            flagged.append({"index": i, "text": st, "tell": "aphorism_candidate"})
        elif st.lower().startswith(connectives):
            flagged.append({"index": i, "text": st, "tell": "connective_opener"})
        elif sum(1 for w in re.findall(r"[A-Za-z'-]+", st) if w.lower() in lset) >= 2:
            flagged.append({"index": i, "text": st, "tell": "banned_lexeme_cluster"})

    runs, i = [], 0
    lens = [len(s.split()) for s in sentences]
    while i < len(lens):
        j = i
        while j + 1 < len(lens) and abs(lens[j + 1] - lens[i]) <= 3:
            j += 1
        if j - i + 1 >= 5:
            runs.append({"start_sentence": i, "length": j - i + 1,
                         "mean_words": round(sum(lens[i:j + 1]) / (j - i + 1), 1)})
        i = j + 1

    n = max(1, len(sentences))
    metrics = {
        "aphorism_candidates": round(aph * per_k, 2),
        "banned_lexemes": round(banned * per_k, 2),
        "em_dashes": round(em_dashes * per_k, 2),
    }
    conn_pct = round(100.0 * conn / n, 1)
    highs = {"aphorism_candidates": thr["aphorism_per_1000_high"],
             "banned_lexemes": thr["banned_lexemes_per_1000_high"]}
    over_high = any(metrics[k] > v for k, v in highs.items()) or conn_pct > thr["connective_openers_pct_high"]
    over_mod = any(metrics[k] > v * thr["moderate_fraction"] for k, v in highs.items()) \
        or conn_pct > thr["connective_openers_pct_high"] * thr["moderate_fraction"]
    rating = "HIGH" if over_high else ("MODERATE" if over_mod else "LOW")

    return {"words_analyzed": words_total,
            "per_1000_words": metrics,
            "connective_openers_pct": conn_pct,
            "participial_openers_pct": round(100.0 * part / n, 1),
            "uniform_runs": runs,
            "flagged_sentences": flagged[:25],
            "advisory_rating": rating,
            "advisory_note": "Deterministic proxy scan — advisory only, never a publish gate. See references/ai-detection-signals.md."}


# ---------------------------------------------------------------------------
# Tier-2 structural scan — deterministic proxies for the narrative-structure
# tells identified in StoryScope (arXiv 2604.03136): AI text stays detectable
# on STRUCTURE even after surface-style editing (93.9% F1 after stylistic
# stripping, only -1.6 points). Surface humanization is necessary, not
# sufficient — these proxies show the human reviewer WHERE the piece is still
# structurally machine-shaped. Advisory only, never a publish gate; thresholds
# live HERE, deliberately never in scoring-thresholds.json.
# ---------------------------------------------------------------------------

_MORALIZING_PHRASES = (
    "in conclusion", "ultimately", "the key takeaway", "the bottom line",
    "it's important to remember", "it is important to remember",
    "this matters because", "at the end of the day", "in short", "simply put",
    "what this means for you", "the lesson here", "in today's world",
    "it's crucial to", "it is crucial to", "remember that", "the takeaway is",
)
_HEDGING_WORDS = frozenset((
    "may", "might", "can", "could", "often", "typically", "generally",
    "usually", "tends", "potentially", "possibly", "somewhat", "relatively",
))
_STANCE_RE = re.compile(r"\b(?:I|we|our|my|us)\b|\bin my experience\b", re.I)
_CITATION_RE = re.compile(r"\[\d+\]|\((?:[A-Z][\w.]*,?\s*)?\d{4}\)|https?://")
_QUOTE_RE = re.compile(r"[\"“][^\"”]{6,}[\"”]")

# Advisory bands (value thresholds). Order: (attention, note) unless noted.
_BANDS = {
    "moralizing_per_1000": (6.0, 3.0),          # higher is worse
    "section_symmetry_cv": (0.20, 0.35),        # LOWER is worse (too uniform)
    "parallel_heading_share": (0.75, 0.55),     # higher is worse
    "specificity_per_1000": (5.0, 10.0),        # LOWER is worse (generic)
    "hedging_per_1000": (18.0, 12.0),           # higher is worse
    "paragraph_evenness_cv": (0.25, 0.40),      # LOWER is worse (uniform voice)
}


def _band(metric, value):
    att, note = _BANDS[metric]
    lower_is_worse = metric in ("section_symmetry_cv", "specificity_per_1000",
                                "paragraph_evenness_cv")
    if lower_is_worse:
        return "ATTENTION" if value <= att else ("NOTE" if value <= note else "OK")
    return "ATTENTION" if value >= att else ("NOTE" if value >= note else "OK")


def _cv(values):
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return None
    return round(statistics.pstdev(values) / mean, 3)


def structure_scan(md_text: str) -> dict:
    """Deterministic Tier-2 structural-tell proxies. Each finding carries the
    spans (sections / sentences) that drove it, so the review sheet can show
    the human editor exactly where to work. This scan has no relationship to
    any statistical watermark — it measures visible structure only."""
    md_text, _ = _strip_frontmatter(md_text)

    # --- sectioning by H2 ---------------------------------------------------
    sections = []  # (title, [prose lines])
    current = ["(before first heading)", []]
    in_code = False
    paragraphs, para = [], []
    for raw in md_text.split("\n"):
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = _HEADING_RE.match(line.strip())
        if m and len(m.group(1)) == 2:
            sections.append(current)
            current = [_inline_to_plain(m.group(2)).strip(), []]
            if para:
                paragraphs.append(" ".join(para)); para = []
            continue
        if m or line.strip().startswith("|"):
            continue
        if not line.strip():
            if para:
                paragraphs.append(" ".join(para)); para = []
            continue
        cleaned = _inline_to_plain(re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)).strip()
        if cleaned:
            current[1].append(cleaned)
            para.append(cleaned)
    sections.append(current)
    if para:
        paragraphs.append(" ".join(para))
    sections = [(t, " ".join(ls)) for t, ls in sections if ls]

    prose = " ".join(text for _, text in sections)
    words_total = max(1, len(re.findall(r"[\w'-]+", prose)))
    per_k = 1000.0 / words_total
    sentences = split_sentences(prose)

    findings = {}

    # 1. Over-explanation / moralizing
    moral_hits = []
    for i, s in enumerate(sentences):
        low = s.lower()
        for ph in _MORALIZING_PHRASES:
            if ph in low:
                moral_hits.append({"index": i, "text": s.strip()[:160], "phrase": ph})
                break
    val = round(len(moral_hits) * per_k, 2)
    findings["moralizing"] = {
        "per_1000_words": val, "band": _band("moralizing_per_1000", val),
        "spans": moral_hits[:15],
        "meaning": "Spelling the takeaway out instead of trusting the reader — AI states the theme far more often than human writers do.",
    }

    # 2. Template symmetry (H2 section word counts too uniform)
    counts = [len(re.findall(r"[\w'-]+", text)) for _, text in sections]
    cv = _cv(counts) if len(counts) >= 4 else None
    findings["section_symmetry"] = {
        "section_word_counts": {t[:60]: c for (t, _), c in zip(sections, counts)},
        "coefficient_of_variation": cv,
        "band": _band("section_symmetry_cv", cv) if cv is not None else "OK",
        "meaning": "Near-identical section lengths read as a filled template; human structure is asymmetric — sections take the length their content earns.",
    }

    # 3. Parallel heading syntax
    h2s = [t for t, _ in sections if t != "(before first heading)"]
    share = None
    if len(h2s) >= 4:
        first_words = [t.split()[0].lower() for t in h2s if t.split()]
        gerund_share = sum(1 for w in first_words if w.endswith("ing")) / len(first_words)
        top_share = max(first_words.count(w) for w in set(first_words)) / len(first_words)
        share = round(max(gerund_share, top_share), 2)
    findings["parallel_headings"] = {
        "headings": h2s, "max_identical_pattern_share": share,
        "band": _band("parallel_heading_share", share) if share is not None else "OK",
        "meaning": "Every heading cut to the same grammatical shape is a template tell; vary the syntax where the content allows.",
    }

    # 4. Specificity density (numbers, proper nouns, quotes, citations)
    numbers = len(re.findall(r"\b\d[\d,.%]*\b", prose))
    proper = sum(1 for s in sentences
                 for w in s.split()[1:] if w[:1].isupper() and w[1:2].islower())
    cites = len(_CITATION_RE.findall(prose))
    quotes = len(_QUOTE_RE.findall(prose))
    val = round((numbers + proper + cites + quotes) * per_k, 2)
    findings["specificity"] = {
        "per_1000_words": val, "band": _band("specificity_per_1000", val),
        "components_per_1000": {"numbers": round(numbers * per_k, 2),
                                "proper_nouns": round(proper * per_k, 2),
                                "citations_urls": round(cites * per_k, 2),
                                "quoted_strings": round(quotes * per_k, 2)},
        "meaning": "Generic prose is the AI center-of-mass; human expert writing names specific, checkable things — sources, numbers, products, people.",
    }

    # 5. Stance absence (hedging up, first-person/stance down)
    hedges = sum(1 for w in re.findall(r"[A-Za-z'-]+", prose) if w.lower() in _HEDGING_WORDS)
    stance = len(_STANCE_RE.findall(prose))
    hval = round(hedges * per_k, 2)
    findings["stance"] = {
        "hedging_per_1000_words": hval,
        "stance_markers_per_1000_words": round(stance * per_k, 2),
        "band": _band("hedging_per_1000", hval),
        "meaning": "Hedged, positionless prose reads machine-made; a human expert takes a stance and owns a judgment somewhere in the piece.",
    }

    # 6. Structural evenness (paragraph lengths too uniform)
    plens = [len(p.split()) for p in paragraphs if len(p.split()) >= 10]
    pcv = _cv(plens) if len(plens) >= 6 else None
    findings["paragraph_evenness"] = {
        "paragraphs_measured": len(plens), "coefficient_of_variation": pcv,
        "band": _band("paragraph_evenness_cv", pcv) if pcv is not None else "OK",
        "meaning": "Uniform paragraph rhythm is a machine fingerprint; human writing has short punches and long developments.",
    }

    order = {"OK": 0, "NOTE": 1, "ATTENTION": 2}
    overall = max((f["band"] for f in findings.values()), key=order.get, default="OK")
    return {
        "words_analyzed": words_total,
        "sections": len(sections),
        "findings": findings,
        "overall": overall,
        "advisory_note": ("Structural-tell proxies (StoryScope-derived) — advisory only, never a "
                          "publish gate. These measure visible structure; they cannot see and have "
                          "no relationship to any statistical watermark."),
    }


def main():
    parser = argparse.ArgumentParser(description="ContentForge text metrics (burstiness, FK grade, keyword placement, structure)")
    parser.add_argument("--file", required=True, help="Markdown (or plain text) file to analyze")
    parser.add_argument("--keyword", default=None, help="Primary keyword for placement/density checks")
    parser.add_argument("--ai-tell-scan", action="store_true",
                         help="Add the deterministic AI-tell detector-signal proxy scan (advisory only)")
    parser.add_argument("--structure-scan", action="store_true",
                         help="Add the Tier-2 structural-tell proxy scan (StoryScope-derived; advisory only)")
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
    if args.ai_tell_scan:
        result["ai_tell_scan"] = ai_tell_scan(text)
    if args.structure_scan:
        result["structure_scan"] = structure_scan(text)
    result["file"] = str(path)
    _common.finish(result)


if __name__ == "__main__":
    main()
