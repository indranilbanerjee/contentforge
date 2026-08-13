#!/usr/bin/env python3
"""
build_review_sheet.py — render the two-tier AI-tell review sheet.

Turns a draft plus the deterministic scans (text-metrics --ai-tell-scan and
--structure-scan) into one self-contained HTML page the human reviewer opens:
Tier-1 surface tells highlighted in the prose, Tier-2 structural findings as
per-metric cards with the evidence that fired them and the human edit
direction. Emitted by the Phase 6.5 humanizer next to the humanized draft
(the reviewer generates it instead when a lane skipped the humanizer) and
referenced on the Completion Card.

Advisory only, never a publish gate. The sheet measures VISIBLE stylistic
and structural patterns; it cannot see and has no relationship to any
statistical watermark.

Usage:
    python build_review_sheet.py --draft phase-6.5-humanized.md \
        --out phase-6.5-review-sheet.html [--title "Post title"]
Exit codes: 0 written, 1 bad input.
"""
from __future__ import annotations

import argparse
import html as html_lib
import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _load_text_metrics():
    spec = importlib.util.spec_from_file_location("text_metrics", _HERE / "text-metrics.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BAND_COLORS = {"OK": "#2e7d4f", "NOTE": "#a06a00", "ATTENTION": "#b3413a",
               "LOW": "#2e7d4f", "MODERATE": "#a06a00", "HIGH": "#b3413a"}

TELL_LABELS = {
    "aphorism_candidate": "Aphorism — short ungrounded maxim",
    "connective_opener": "Connective opener (However/Moreover/...)",
    "banned_lexeme_cluster": "LLM-favored word cluster",
}


def build_sheet(draft_text: str, tier1: dict, tier2: dict, title: str) -> str:
    esc = html_lib.escape

    # Tier-1 inline highlighting: wrap flagged sentences where they appear
    # verbatim. Escape first, then substitute the escaped forms.
    body = esc(draft_text)
    for f in tier1.get("flagged_sentences", []):
        target = esc(f["text"])
        if target and target in body:
            label = TELL_LABELS.get(f["tell"], f["tell"])
            body = body.replace(
                target,
                f'<mark title="{esc(label)}">{target}</mark>', 1)

    t1_rating = tier1.get("advisory_rating", "LOW")
    t2_overall = tier2.get("overall", "OK")

    cards = ""
    for key, f in tier2.get("findings", {}).items():
        band = f.get("band", "OK")
        evidence = ""
        if f.get("spans"):
            items = "".join(f"<li>{esc(s['text'])}</li>" for s in f["spans"][:8])
            evidence = f"<ul>{items}</ul>"
        elif f.get("section_word_counts"):
            items = "".join(f"<li>{esc(t)} — {c} words</li>"
                            for t, c in f["section_word_counts"].items())
            evidence = f"<ul>{items}</ul>"
        elif f.get("headings"):
            evidence = "<ul>" + "".join(f"<li>{esc(h)}</li>" for h in f["headings"]) + "</ul>"
        cards += f"""
        <div class="card" style="border-left:4px solid {BAND_COLORS[band]}">
          <div class="card-head"><b>{esc(key.replace('_', ' ').title())}</b>
            <span class="band" style="background:{BAND_COLORS[band]}">{band}</span></div>
          <p class="meaning">{esc(f.get('meaning', ''))}</p>
          {evidence}
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Review sheet — {esc(title)}</title>
<style>
  body {{ font: 15px/1.6 -apple-system, "Segoe UI", sans-serif; color: #26221f;
         background: #f6f4f1; margin: 0; padding: 24px; }}
  .wrap {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 21px; }} h2 {{ font-size: 17px; margin-top: 28px; }}
  .advisory {{ background: #fff; border: 1px solid #ddd4c8; border-radius: 6px;
               padding: 10px 14px; font-size: 13.5px; color: #6b6257; }}
  .chips {{ display: flex; gap: 10px; margin: 14px 0; }}
  .chip {{ padding: 5px 14px; border-radius: 14px; color: #fff; font-weight: 600;
           font-size: 13px; }}
  .card {{ background: #fff; border: 1px solid #e2dacf; border-radius: 6px;
           padding: 12px 16px; margin: 10px 0; }}
  .card-head {{ display: flex; align-items: center; gap: 10px; }}
  .band {{ color: #fff; font-size: 11px; font-weight: 700; padding: 2px 9px;
           border-radius: 4px; margin-left: auto; }}
  .meaning {{ color: #6b6257; font-size: 13.5px; margin: 6px 0; }}
  .card ul {{ font-size: 13px; color: #4a443d; margin: 6px 0 2px; }}
  pre.draft {{ background: #fff; border: 1px solid #e2dacf; border-radius: 6px;
               padding: 18px 20px; white-space: pre-wrap; font: 14px/1.65 Georgia, serif; }}
  mark {{ background: #ffe2a8; border-bottom: 2px solid #d99a00; padding: 1px 2px; }}
</style></head><body><div class="wrap">
<h1>AI-tell review sheet — {esc(title)}</h1>
<p class="advisory"><b>Advisory, never a publish gate.</b> This sheet highlights visible
stylistic (Tier&nbsp;1) and structural (Tier&nbsp;2) patterns that read machine-made, so a
human editor knows where to work. It measures the text itself —
it cannot see and has no relationship to any statistical watermark.
The right response to a highlight is a genuine human edit in the brand's voice, not a synonym swap.</p>
<div class="chips">
  <span class="chip" style="background:{BAND_COLORS[t1_rating]}">Tier 1 surface: {t1_rating}</span>
  <span class="chip" style="background:{BAND_COLORS[t2_overall]}">Tier 2 structure: {t2_overall}</span>
</div>
<h2>Tier 2 — structural findings</h2>
{cards}
<h2>Draft with Tier-1 highlights ({len(tier1.get('flagged_sentences', []))} flagged spans)</h2>
<pre class="draft">{body}</pre>
</div></body></html>"""


def main():
    parser = argparse.ArgumentParser(description="Build the two-tier AI-tell review sheet")
    parser.add_argument("--draft", required=True, help="Path to the draft markdown")
    parser.add_argument("--out", required=True, help="Output HTML path")
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    draft_path = Path(args.draft).expanduser()
    if not draft_path.is_file():
        print(json.dumps({"error": f"draft not found: {draft_path}"}))
        sys.exit(1)
    text = draft_path.read_text(encoding="utf-8", errors="replace")

    tm = _load_text_metrics()
    tier1 = tm.ai_tell_scan(text)
    tier2 = tm.structure_scan(text)

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_sheet(text, tier1, tier2, args.title or draft_path.stem),
                        encoding="utf-8")
    print(json.dumps({
        "status": "success",
        "output": str(out_path),
        "tier1_rating": tier1.get("advisory_rating"),
        "tier1_flagged_spans": len(tier1.get("flagged_sentences", [])),
        "tier2_overall": tier2.get("overall"),
        "tier2_attention": [k for k, f in tier2.get("findings", {}).items()
                            if f.get("band") == "ATTENTION"],
    }, indent=2))


if __name__ == "__main__":
    main()
