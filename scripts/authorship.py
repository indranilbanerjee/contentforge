#!/usr/bin/env python3
"""Authorship provenance — keep the author's own sentences, and prove it.

ContentForge's normal mode writes from research. This script supports the other
mode: the client brings their own rough draft — a voice-note transcript, a wall
of bullets, ugly stream-of-consciousness — and the pipeline develops it AROUND
their sentences instead of paraphrasing them away.

Why it exists (the honest version): a client's own words are the one part of a
piece that is genuinely, unambiguously theirs. Paraphrasing them is the single
most common way an AI pipeline quietly launders a human voice out of a document
— the author reads the output, recognizes their idea, and no longer recognizes a
single sentence. This script measures whether that happened.

It reports three things a human editor actually needs:
  1. which sentences in the final draft are the author's, verbatim;
  2. which of the author's sentences were REWRITTEN (a broken promise);
  3. which of the author's sentences were DROPPED entirely.

Unlike the AI-tell scans, findings 2 and 3 are not advisory. A detector score is
probabilistic and deserves hedging; "the author wrote this sentence and it is no
longer here" is a fact. Those exit non-zero.

This is not a detector-evasion tool and carries no target ratio to hit. There is
no threshold at which text becomes "human enough" — the ratio is reported so the
disclosure can be accurate, never so a score can be gamed. It measures visible
text only, and has no relationship to any statistical watermark.

Usage:
    python authorship.py --source notes.md --draft phase-6.5-humanized.md
    python authorship.py --source notes.md --draft draft.md --out authorship.json
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

# A draft sentence at or above this similarity to a source sentence is the
# author's sentence, possibly edited. Below it, the sentence is new material.
NEAR_MATCH = 0.72
# Below this, "edited" becomes "rewritten past recognition" in the report.
VERBATIM = 0.995
# The author must carry at least this share of the finished words before the
# deliverable may describe itself as written by them. Guards the disclosure
# against overclaiming human authorship the record does not support.
AUTHORED_WORD_SHARE_FLOOR = 0.25

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_INLINE_MD = re.compile(r"[*_`~]+")
_WS = re.compile(r"\s+")


def split_sentences(text: str) -> list[str]:
    """Sentences from prose, ignoring markdown headings, list markers, tables
    and fenced code — the same surfaces the other scans skip."""
    out, in_code = [], False
    for raw in text.split("\n"):
        line = raw.strip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line or line.startswith("#") or line.startswith("|"):
            continue
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
        for part in _SENT_SPLIT.split(line):
            part = part.strip()
            if part:
                out.append(part)
    return out


def normalize(sentence: str) -> str:
    """Compare on meaning-bearing characters only. Deliberately forgiving about
    typography (curly vs straight quotes, dash style) and deliberately NOT
    forgiving about wording — a reworded sentence must not read as verbatim."""
    s = _INLINE_MD.sub("", sentence.lower())
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return _WS.sub(" ", s).strip()


def _ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def classify(source_text: str, draft_text: str) -> dict:
    """Match every draft sentence against the author's source draft.

    Matching is greedy best-first and one-to-one: an author sentence can account
    for at most one draft sentence, so repeating their line does not inflate the
    author's share.
    """
    src = [(i, s, normalize(s)) for i, s in enumerate(split_sentences(source_text))]
    dra = [(i, s, normalize(s)) for i, s in enumerate(split_sentences(draft_text))]

    scored = []
    for si, _, sn in src:
        if not sn:
            continue
        for di, _, dn in dra:
            if not dn:
                continue
            r = _ratio(sn, dn)
            if r >= NEAR_MATCH:
                scored.append((r, si, di))
    scored.sort(key=lambda t: (-t[0], t[1], t[2]))

    used_src, used_draft, link = set(), set(), {}
    for r, si, di in scored:
        if si in used_src or di in used_draft:
            continue
        used_src.add(si)
        used_draft.add(di)
        link[di] = (si, r)

    sentences, verbatim_words, total_words = [], 0, 0
    counts = {"author_verbatim": 0, "author_modified": 0, "ai_added": 0}
    for di, text, _ in dra:
        wc = len(text.split())
        total_words += wc
        if di in link:
            si, r = link[di]
            status = "author_verbatim" if r >= VERBATIM else "author_modified"
            if status == "author_verbatim":
                verbatim_words += wc
            rec = {"index": di, "status": status, "similarity": round(r, 3),
                   "source_index": si, "text": text[:240]}
            if status == "author_modified":
                rec["source_text"] = src[si][1][:240]
        else:
            status = "ai_added"
            rec = {"index": di, "status": status, "text": text[:240]}
        counts[status] += 1
        sentences.append(rec)

    dropped = [{"source_index": si, "text": text[:240]}
               for si, text, sn in src if sn and si not in used_src]

    # Longest stretch with none of the author's voice — editorial context, not
    # a threshold. Nothing in this pipeline requires it to be any particular size.
    longest_run, run = 0, 0
    for rec in sentences:
        run = run + 1 if rec["status"] == "ai_added" else 0
        longest_run = max(longest_run, run)

    n = max(1, len(sentences))
    word_share = round(verbatim_words / total_words, 3) if total_words else 0.0
    modified = [s for s in sentences if s["status"] == "author_modified"]

    return {
        "source_provided": bool(src),
        "draft_sentences": len(sentences),
        "source_sentences": len(src),
        "counts": counts,
        "author_sentence_share": round(counts["author_verbatim"] / n, 3),
        "author_word_share": word_share,
        "longest_ai_only_run": longest_run,
        "violations": {
            "author_sentences_rewritten": len(modified),
            "author_sentences_dropped": len(dropped),
        },
        "rewritten": modified[:25],
        "dropped": dropped[:25],
        "sentences": sentences,
        # A deliverable may describe itself as the author's only when the record
        # supports it: enough of their words survived AND none were rewritten or
        # dropped. An outstanding violation means the piece is not yet what the
        # disclosure would be claiming, so the claim waits for the repair.
        "may_claim_authored": (bool(src)
                               and word_share >= AUTHORED_WORD_SHARE_FLOOR
                               and not modified and not dropped),
        "authored_word_share_floor": AUTHORED_WORD_SHARE_FLOOR,
        "note": ("Provenance record, not a score to optimize. author_word_share exists so the "
                 "deliverable's disclosure can be accurate; there is no ratio at which text "
                 "becomes 'human enough'. Rewritten or dropped author sentences are broken "
                 "promises, not style opinions — restore them verbatim rather than improving "
                 "them. Measures visible text only; no relationship to any statistical watermark."),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Measure how much of a draft is the author's own words, verbatim.")
    parser.add_argument("--source", required=True,
                        help="The author's own rough draft / transcript / notes")
    parser.add_argument("--draft", required=True, help="The pipeline draft to check")
    parser.add_argument("--out", default=None, help="Write the record to this JSON path")
    args = parser.parse_args()

    src_path, draft_path = Path(args.source).expanduser(), Path(args.draft).expanduser()
    for label, p in (("source", src_path), ("draft", draft_path)):
        if not p.is_file():
            _common.finish({
                "error": f"{label} file not found: {p}",
                "recovery": ("Pass the author's own draft as --source and the pipeline artifact "
                             "as --draft. With no author draft, skip this script entirely — "
                             "the run simply has no authorship record."),
            })

    result = classify(src_path.read_text(encoding="utf-8"),
                      draft_path.read_text(encoding="utf-8"))
    result["source_file"] = str(src_path)
    result["draft_file"] = str(draft_path)

    if args.out:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        _common.atomic_write_json(out, result)
        result["written_to"] = str(out)

    v = result["violations"]
    if v["author_sentences_rewritten"] or v["author_sentences_dropped"]:
        _common.ensure_utf8_stdout()
        import json as _json
        print(_json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\nAUTHORSHIP VIOLATIONS: {v['author_sentences_rewritten']} of the author's "
              f"sentences were rewritten, {v['author_sentences_dropped']} were dropped. "
              f"Restore them verbatim — do not improve them.", file=sys.stderr)
        sys.exit(3)

    _common.finish(result)


if __name__ == "__main__":
    main()
