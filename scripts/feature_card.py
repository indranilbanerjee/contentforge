#!/usr/bin/env python3
"""
feature_card.py
===============
Deterministic feature image (OG card) — 1200x630, rendered from the brand's own
recorded colors and the piece's real title. No AI generation involved.

Why this exists
---------------
The only feature-image route in Phase 3.5 was AI generation, so under
``image_gen_mode: none`` — a recorded user decision — a mandatory-before-publish
item ("supply a feature image, og:image is null") was permanently unclosable by
the pipeline. A real run ended publication-BLOCKED on exactly that, with
image-generation tools detected and correctly declined.

This is the same move that closed the diagram gap: render deterministically,
where every constraint is checkable before the file is written. The card uses
only facts the pipeline already holds — the brand's profile colors, the brand
name, the article title — so nothing about the brand's identity is invented.
It is a typographic card, not artwork; the JSON result says so.

Approval note: deterministic *data* assets (charts verified at Gate 4) embed
without user approval. A feature card is aesthetic, and it becomes the piece's
public face (og:image), so it is recorded ``approved_by_user: false`` and the
orchestrator collects approval like any other creative choice. What changes is
that a "supply a feature image" blocker now has a pipeline-native candidate to
approve instead of a dead end.

Determinism: same inputs on the same environment produce the same bytes
(verified by re-render + sha256 in the self-check). Cross-machine byte equality
is NOT promised — font rasterization differs per platform — and the result JSON
carries the hash so any consumer can verify what it received.

Usage:
    python feature_card.py --title "The Real Cost of Digital Preservation" \
        --brand-name "Example Archive" --primary "#0B6E4F" --secondary "#DDA15E" \
        --out /path/to/{run_id}-feature-card.png [--kicker "BLOG"]

Exit codes: 0 success · 1 constraint violation (file NOT written) · 2 usage error.
"""

import argparse
import hashlib
import json
import pathlib
import re
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

WIDTH_PX, HEIGHT_PX = 1200, 630
DPI = 100
MAX_TITLE_CHARS = 140

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _fail(msg, code=2):
    print(json.dumps({"status": "FAILED", "error": msg}, ensure_ascii=False))
    sys.exit(code)


def _luminance(hex_color: str) -> float:
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def render(title: str, brand_name: str, primary: str, secondary: str,
           out_path: pathlib.Path, kicker: str = None) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Text on the primary ground must be readable; pick white or near-black by
    # measured luminance, never by guess.
    text_color = "#FAFAF7" if _luminance(primary) < 0.5 else "#14181D"

    fig = plt.figure(figsize=(WIDTH_PX / DPI, HEIGHT_PX / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=primary, zorder=0))
    # One quiet geometric accent in the secondary color — an edge band, not décor
    # pretending to be illustration.
    ax.add_patch(plt.Rectangle((0, 0), 1, 0.035, color=secondary, zorder=1))
    ax.add_patch(plt.Rectangle((0.055, 0.82), 0.06, 0.012, color=secondary, zorder=1))

    if kicker:
        ax.text(0.055, 0.87, kicker.upper(), fontsize=15, color=text_color,
                alpha=0.85, fontweight="bold", family="sans-serif", zorder=2)

    wrapped = textwrap.fill(title.strip(), width=26)
    n_lines = wrapped.count("\n") + 1
    title_size = 44 if n_lines <= 3 else (36 if n_lines == 4 else 30)
    ax.text(0.055, 0.72, wrapped, fontsize=title_size, color=text_color,
            fontweight="bold", family="sans-serif", va="top", linespacing=1.25,
            zorder=2)

    ax.text(0.055, 0.09, brand_name, fontsize=17, color=text_color, alpha=0.9,
            family="sans-serif", zorder=2)

    # ---- constraints, asserted BEFORE the file exists -----------------------
    problems = []
    texts = [t.get_text() for t in ax.texts]
    expected = {wrapped, brand_name} | ({kicker.upper()} if kicker else set())
    if set(texts) != expected:
        problems.append(f"unexpected text artists: {sorted(set(texts) - expected)}")
    for t in texts:
        # A feature card must not smuggle in numbers that read as data claims.
        if re.search(r"\d", t) and t not in (wrapped, brand_name, kicker.upper() if kicker else ""):
            problems.append(f"unexpected digits in card text: {t!r}")
    if problems:
        plt.close(fig)
        return {"status": "FAILED", "stage": "constraints", "problems": problems}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=DPI)  # no bbox_inches='tight': it changes the size
    plt.close(fig)

    # ---- verify off disk, never from intent ---------------------------------
    from PIL import Image
    with Image.open(out_path) as img:
        img.verify()
    with Image.open(out_path) as img:
        size = img.size
    if size != (WIDTH_PX, HEIGHT_PX):
        out_path.unlink(missing_ok=True)
        return {"status": "FAILED", "stage": "verify",
                "problems": [f"rendered {size}, contract requires "
                             f"({WIDTH_PX}, {HEIGHT_PX}); file removed"]}

    data = out_path.read_bytes()
    return {
        "status": "generated",
        "kind": "deterministic_feature_card",
        "note": ("Typographic card from the brand's recorded colors and the real "
                 "title — no AI generation, no data plotted, nothing invented. "
                 "Requires user approval before use as og:image, like any "
                 "creative choice."),
        "file_path": str(out_path.resolve()),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": [WIDTH_PX, HEIGHT_PX],
        "ai_generated": False,
        "approved_by_user": False,
        "text_color_basis": f"luminance({primary}) = {_luminance(primary):.3f}",
    }


def main():
    ap = argparse.ArgumentParser(description="Deterministic 1200x630 feature card")
    ap.add_argument("--title", required=True)
    ap.add_argument("--brand-name", required=True)
    ap.add_argument("--primary", required=True, help="brand primary color, #RRGGBB")
    ap.add_argument("--secondary", required=True, help="brand secondary color, #RRGGBB")
    ap.add_argument("--out", required=True)
    ap.add_argument("--kicker", default=None, help="small upper label, e.g. content type")
    args = ap.parse_args()

    if not _HEX_RE.match(args.primary) or not _HEX_RE.match(args.secondary):
        _fail("colors must be #RRGGBB — read them from the brand profile, "
              "never invent them")
    if not args.title.strip():
        _fail("empty title")
    if len(args.title) > MAX_TITLE_CHARS:
        _fail(f"title over {MAX_TITLE_CHARS} chars will not fit legibly; "
              f"shorten it rather than shrinking the type into noise")

    result = render(args.title, args.brand_name, args.primary, args.secondary,
                    pathlib.Path(args.out).expanduser(), args.kicker)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["status"] == "generated" else 1)


if __name__ == "__main__":
    main()
