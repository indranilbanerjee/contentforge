#!/usr/bin/env python3
"""
scorecard-html.py
=================
Renders a finished ContentForge run as ONE self-contained HTML page: the
decision, the score against the approve line, every dimension against its
minimum and weight, the run audit's verdict (and whether it is still current),
publication status, and the piece's own measurements.

Why this exists
---------------
A finished run leaves a verdict spread across a dozen files. A writer, an editor
or a client wants one page that says "approved, 9.0 against a 7.0 line, audit
clean" -- and wants to be able to trust it. So this page never invents a number:
every figure is read from the run's own files, the approve line and the
dimension minimums are RESOLVED from config/scoring-thresholds.json by the same
code the run auditor uses (``run-audit.py``: ``resolve_policy`` and the brand
profile's industry), and the audit's freshness is the same fingerprint
comparison ``checkpoint-manager.py finalize`` makes (``_common``).

The one thing it will not do is flatter. A run with no ``run-audit.json`` is
shown as NOT AUDITED. A run whose files changed after the audit is shown as
STALE, with the files that changed -- the old CLEAN is recorded on the page as
history, never as the current verdict. An audit written without a fingerprint
cannot prove it is fresh and is shown as UNVERIFIED.

The page is a local file: inline CSS only, no scripts, no external fonts or
images, no ``src`` or ``href`` attributes at all; light and dark through
``prefers-color-scheme``; readable at 400px wide. All text from the run is
escaped. Building it writes ONE new file (``scorecard.html``) that is not part
of the audit's fingerprint, so building the page never makes an audit stale.

Usage:
    python scorecard-html.py --run-dir <run dir> [--out <file>]

Default output: ``<run-dir>/scorecard.html``.

Result (JSON on stdout):
    path, bytes, run_id, decision, overall_score,
    verdict_shown   CLEAN | VIOLATIONS | STALE | UNVERIFIED | NOT_AUDITED | UNREADABLE
    audit_state     fresh | stale | unfingerprinted | missing | unreadable
    stale_audit     true whenever the page does NOT present a current audit
                    (anything but ``audit_state == "fresh"``)

Exit codes: 0 written - 2 unusable input (no run directory, no run.json, no
phase-7-review.json) or write failure.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import pathlib
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

SCRIPTS = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = SCRIPTS.parent / "config"

DIM_ORDER = ["content_quality", "citation_integrity", "brand_compliance",
             "seo_performance", "readability"]

# The humanizer report states its advisory scan in prose (agents/06.5-humanizer.md
# section 8). Read it back; never re-score. The negative lookahead keeps the
# unfilled template line "LOW/MODERATE/HIGH" from reading as a rating.
RATING_RE = re.compile(
    r"advisory\s+rating\s*:?\s*\**\s*(LOW|MODERATE|HIGH)\b(?!\s*/)", re.I)
SIGNAL_RE = re.compile(
    r"remaining[- ]AI[- ]signal\s+score\s*:?\s*\**\s*([01](?:\.\d+)?)", re.I)
STRUCT_RE = re.compile(
    r"structure[_ ]scan\s+overall\s*:?\s*\**\s*(OK|NOTE|ATTENTION)\b", re.I)


# ----------------------------------------------------------------- plumbing

def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _label(key: str) -> str:
    text = str(key).replace("_", " ").strip().capitalize()
    return re.sub(r"(?<![A-Za-z])Seo(?![A-Za-z])", "SEO", text)


def _read_text(path: pathlib.Path):
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            return fh.read()
    except OSError:
        return None


def _plugin_version():
    for rel in (".claude-plugin/plugin.json", "plugin.json"):
        try:
            doc = json.loads((SCRIPTS.parent / rel).read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(doc, dict) and isinstance(doc.get("version"), str):
            return doc["version"]
    return None


# --------------------------------------------------------------- derivations

def resolve_review_policy(ra, scoring, review, manifest, run_dir):
    """The approve line, dimension minimums and weights config resolves for this
    review -- the same rule ``run-audit.py`` applies: the review's industry and,
    independently, the brand profile's; the stricter binds. None when config is
    unreadable (the page then says the line was not re-derived)."""
    if scoring is None:
        return None
    ctype = manifest.get("content_type") or review.get("content_type")
    r_ind = review.get("industry")
    r_ind = r_ind.strip() if isinstance(r_ind, str) and r_ind.strip() else None
    p_ind = ra._brand_industry(run_dir)
    pol_r = ra.resolve_policy(scoring, r_ind, ctype) if r_ind else None
    pol_p = ra.resolve_policy(scoring, p_ind, ctype) if p_ind else None
    pols = [p for p in (pol_r, pol_p) if p] or [ra.resolve_policy(scoring, None, ctype)]
    own = pol_r or pol_p or pols[0]
    minimums = {}
    for p in pols:
        for k, v in p["minimums"].items():
            minimums[k] = max(minimums.get(k, v), v)
    industry = r_ind or p_ind
    overrides = scoring.get("industry_overrides", {})
    if not industry:
        basis = "default policy (no industry recorded)"
    elif ra._norm_key(industry) in overrides:
        basis = f"config override for {industry}"
    else:
        basis = f"default policy (config has no override for {industry})"
    if r_ind and p_ind and ra._norm_key(r_ind) != ra._norm_key(p_ind):
        basis += f"; the brand profile says {p_ind}, the stricter policy binds"
    return {"line": max(p["minimum_pass_score"] for p in pols),
            "minimums": minimums, "weights": own["weights"],
            "industry": industry, "basis": basis}


def read_audit(run_dir: pathlib.Path):
    """(state, record, drift). The freshness test is the one ``finalize`` makes:
    the audit's recorded fingerprint against the files as they stand now."""
    path = run_dir / "run-audit.json"
    if not path.is_file():
        return "missing", None, []
    try:
        rec = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return "unreadable", None, []
    if not isinstance(rec, dict) or "verdict" not in rec:
        return "unreadable", None, []
    fp = rec.get("fingerprint")
    if not isinstance(fp, dict) or not isinstance(fp.get("files"), dict):
        return "unfingerprinted", rec, []
    drift = _common.fingerprint_drift(fp, _common.run_artifact_fingerprint(run_dir))
    return ("stale" if drift else "fresh"), rec, drift


VERDICT_FOR_STATE = {"missing": "NOT_AUDITED", "unreadable": "UNREADABLE",
                     "unfingerprinted": "UNVERIFIED", "stale": "STALE"}


def body_artifact(manifest: dict, run_dir: pathlib.Path):
    arts = manifest.get("phase_artifacts") or {}
    for phase, default in (("6.5", "phase-6.5-humanized.md"),
                           ("6", "phase-6-seo.md"), ("5", "phase-5-structured.md"),
                           ("3", "phase-3-draft.md")):
        name = arts.get(phase, default)
        if isinstance(name, str) and (run_dir / name).is_file():
            return name
    return None


def humanizer_scan(run_dir: pathlib.Path) -> dict:
    text = _read_text(run_dir / "phase-6.5-report.md")
    if text is None:
        return {}
    out = {}
    for key, rx in (("rating", RATING_RE), ("signal", SIGNAL_RE), ("structure", STRUCT_RE)):
        m = rx.search(text)
        if m:
            out[key] = m.group(1).upper() if key != "signal" else float(m.group(1))
    return out


def fix_ledger_view(run_dir: pathlib.Path, review: dict):
    """The ledger verification as recorded: Phase 7's own output file first, the
    review's embedded copy second. Returns (source, ledger dict) or (None, None)."""
    try:
        doc = json.loads((run_dir / "phase-7-fix-ledger.json").read_text(encoding="utf-8-sig"))
        if isinstance(doc, dict):
            return "phase-7-fix-ledger.json", doc
    except (OSError, json.JSONDecodeError):
        pass
    fl = review.get("fix_ledger")
    if isinstance(fl, dict) and fl:
        return "phase-7-review.json", fl
    return None, None


# ----------------------------------------------------------------- rendering

CSS = """
:root{
  --bg:#f6f5f1;--surface:#ffffff;--ink:#1b1f24;--muted:#58616c;--line:#dcd9d0;--track:#e6e3da;
  --ok:#17663a;--ok-bg:#e1f2e6;--warn:#835400;--warn-bg:#fbefd0;--bad:#a3262a;--bad-bg:#fbe3e3;
  --neutral:#3b4452;--neutral-bg:#ecebe5;
  color-scheme:light dark;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#121417;--surface:#1b1e23;--ink:#ecebe6;--muted:#a4abb4;--line:#2f353d;--track:#2b3037;
    --ok:#7bd6a0;--ok-bg:#16301f;--warn:#f0c46e;--warn-bg:#352a0e;--bad:#ff9fa1;--bad-bg:#3c1a1c;
    --neutral:#c4cad3;--neutral-bg:#252a31;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
main{max-width:46rem;margin:0 auto;padding:20px 16px 36px}
h1{font-size:1.55rem;line-height:1.25;margin:.15rem 0 .35rem;overflow-wrap:anywhere}
h2{font-size:1.02rem;line-height:1.3;margin:0 0 .65rem;letter-spacing:.01em}
p{margin:.25rem 0}
.eyebrow{font-size:.78rem;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:0}
.sub{color:var(--muted);font-size:.92rem;overflow-wrap:anywhere}
.chips{list-style:none;display:flex;flex-wrap:wrap;gap:6px;margin:.7rem 0 0;padding:0}
.chips li{border:1px solid var(--line);background:var(--surface);border-radius:999px;
  padding:2px 10px;font-size:.82rem;color:var(--muted);overflow-wrap:anywhere}
.chips b{color:var(--ink);font-weight:600}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;
  padding:16px;margin:14px 0;overflow-wrap:anywhere}
.t-ok{--tone:var(--ok);--tone-bg:var(--ok-bg)}
.t-warn{--tone:var(--warn);--tone-bg:var(--warn-bg)}
.t-bad{--tone:var(--bad);--tone-bg:var(--bad-bg)}
.t-neutral{--tone:var(--neutral);--tone-bg:var(--neutral-bg)}
.hero{border-left:6px solid var(--tone)}
.hero-top{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap}
.big{font-size:3.1rem;line-height:1;font-weight:700;color:var(--tone);font-variant-numeric:tabular-nums}
.of{color:var(--muted);font-size:1rem}
.decision{font-size:1.15rem;font-weight:700;letter-spacing:.04em;color:var(--tone);margin:0}
.pill{display:inline-block;background:var(--tone-bg);color:var(--tone);border-radius:6px;
  padding:1px 8px;font-weight:600;font-size:.82rem;letter-spacing:.03em}
.bar{position:relative;height:10px;border-radius:5px;background:var(--track);margin:.8rem 0 .3rem}
.bar .fill{position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:var(--tone)}
.bar .mark{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--ink);opacity:.75}
.legend{font-size:.8rem;color:var(--muted)}
.flags{margin:.7rem 0 0;padding:0;list-style:none}
.flags li{background:var(--warn-bg);color:var(--warn);border-radius:8px;padding:6px 10px;
  margin:.35rem 0;font-size:.9rem}
.banner{background:var(--tone-bg);color:var(--tone);border-radius:8px;padding:10px 12px;
  font-weight:600;margin:.1rem 0 .6rem}
.dims{list-style:none;margin:0;padding:0}
.dim{padding:.7rem 0;border-top:1px solid var(--line)}
.dim:first-child{border-top:0;padding-top:0}
.dim-head{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.dim-name{font-weight:600}
.dim-score{font-weight:700;font-size:1.2rem;color:var(--tone);font-variant-numeric:tabular-nums}
.dim-meta{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:.84rem;color:var(--muted)}
.dim-meta .st{color:var(--tone);font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0;padding:0;list-style:none}
.stats li{border:1px solid var(--line);border-radius:10px;padding:8px 10px}
.stats .k{display:block;font-size:.76rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.stats .v{display:block;font-weight:600;font-variant-numeric:tabular-nums}
.stats .n{display:block;font-size:.8rem;color:var(--muted)}
.checks{margin:.4rem 0 0;padding-left:1.1rem}
.checks li{margin:.3rem 0}
.checks .d{display:block;color:var(--muted);font-size:.88rem}
details{margin-top:.6rem}
summary{cursor:pointer;color:var(--muted);font-size:.9rem}
.small{font-size:.86rem;color:var(--muted)}
footer{margin-top:22px;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:.82rem}
footer p{margin:.3rem 0}
@media print{
  body{background:#fff}
  main{max-width:none;padding:0}
  .card{break-inside:avoid}
}
"""


def _tone_for_decision(decision: str) -> str:
    d = str(decision or "").upper()
    if "APPROVED" in d:
        return "ok"
    if "LOOP" in d:
        return "warn"
    return "bad"


def _pill(text, tone):
    return f'<span class="pill t-{tone}">{esc(text)}</span>'


def render(run_dir: pathlib.Path, manifest: dict, review: dict, ra, tm) -> tuple:
    """Build the page. ``ra`` is the run-audit module (policy, brand industry), ``tm``
    the text-metrics module (the body word count Gate 3 means). Returns
    (html text, summary dict for the JSON result)."""
    scoring = ra._json(CONFIG_DIR / "scoring-thresholds.json")
    policy = resolve_review_policy(ra, scoring, review, manifest, run_dir)

    run_id = manifest.get("run_id") or review.get("run_id") or run_dir.name
    title_txt = _read_text(run_dir / "phase-0.5-title.txt")
    title = next((ln.strip() for ln in (title_txt or "").splitlines() if ln.strip()), None)
    topic = manifest.get("topic")
    title = title or topic or run_id
    brand = review.get("brand") or manifest.get("brand") or "not recorded"
    ctype = manifest.get("content_type") or review.get("content_type")
    industry = (policy or {}).get("industry") or review.get("industry")
    lane = review.get("lane") or manifest.get("mode") or "full"

    # ---- decision + score vs approve line ---------------------------------
    score = review.get("overall_score")
    decision = str(review.get("decision") or "not recorded")
    approved = "APPROVED" in decision.upper()
    line = policy["line"] if policy else review.get("minimum_pass_score_applied")
    line_src = policy["basis"] if policy else "as recorded by the reviewer; config could not be read"
    dims = review.get("dimensions") if isinstance(review.get("dimensions"), dict) else {}
    minimums = (policy or {}).get("minimums", {})

    below = [k for k, v in dims.items() if _num(v) and _num(minimums.get(f"min_{k}"))
             and v < minimums[f"min_{k}"]]
    flags = []
    if _num(score) and _num(line) and approved and score < line:
        flags.append(f"The decision says APPROVED but the score {score:.1f} is below the "
                     f"approve line {line:.1f} that config resolves. Do not rely on this decision.")
    if approved and below:
        flags.append("The decision says APPROVED but these dimensions are below their "
                     "minimum: " + ", ".join(_label(k) for k in below) + ".")
    applied = review.get("minimum_pass_score_applied")
    if policy and _num(applied) and _num(line) and abs(applied - line) > 1e-9:
        flags.append(f"The reviewer recorded an approve line of {applied:.1f}; config "
                     f"resolves {line:.1f} for this industry.")
    tone = "bad" if (flags and approved) else _tone_for_decision(decision)

    pct = max(0.0, min(100.0, (score if _num(score) else 0) * 10))
    mark = max(0.0, min(100.0, (line if _num(line) else 0) * 10))
    grade = review.get("grade")
    margin = (f" &middot; margin {score - line:+.1f}"
              if _num(score) and _num(line) else "")
    loop_to = review.get("loop_target_phase")
    decision_show = decision.replace("_", " ").upper()
    if loop_to not in (None, "", "null") and "LOOP" in decision.upper():
        decision_show += f" TO PHASE {loop_to}"

    hero = [
        f'<section class="card hero t-{tone}" id="verdict" data-decision="{esc(decision)}">',
        '<div class="hero-top">',
        f'<span class="big">{esc(f"{score:.1f}") if _num(score) else "n/a"}</span>',
        '<span class="of">/ 10</span>',
        f'<div><p class="decision">{esc(decision_show)}</p>',
        f'<p class="small">{("Grade " + esc(grade) + " &middot; ") if grade else ""}'
        f'approve line {esc(f"{line:.1f}") if _num(line) else "not recorded"}{margin}</p></div>',
        '</div>',
        f'<div class="bar" role="img" aria-label="Score {esc(score)} out of 10; '
        f'approve line {esc(line)}"><span class="fill" style="width:{pct:.1f}%"></span>'
        f'<span class="mark" style="left:{mark:.1f}%"></span></div>',
        f'<p class="legend">The dark tick is the approve line. Basis: {esc(line_src)}.</p>',
    ]
    if flags:
        hero.append('<ul class="flags">' + "".join(f"<li>{esc(f)}</li>" for f in flags) + "</ul>")
    hero.append("</section>")

    # ---- dimensions ---------------------------------------------------------
    weights = review.get("weights_applied")
    w_src = "reviewer"
    if not (isinstance(weights, dict) and weights):
        weights, w_src = {k: v for k, v in (policy or {}).get("weights", {}).items()}, "config"
    as_fraction = all(_num(v) and v <= 1.0 for v in weights.values()) if weights else False
    wpct = {k: (v * 100 if as_fraction else v) for k, v in weights.items() if _num(v)}
    keys = [k for k in DIM_ORDER if k in dims or k in wpct]
    keys += [k for k in dims if k not in keys]
    rows = []
    for k in keys:
        v = dims.get(k)
        mn = minimums.get(f"min_{k}")
        if _num(v):
            ok = (not _num(mn)) or v >= mn
            t = "ok" if ok else "bad"
            status = ("Meets minimum" if ok else "Below minimum") if _num(mn) else "No minimum set"
            shown = f"{v:.1f}"
            fillw = max(0.0, min(100.0, v * 10))
        else:
            t, status, shown, fillw = "neutral", "Not scored" + (f" ({v})" if v else ""), "n/a", 0.0
        meta = []
        if k in wpct:
            meta.append(f"Weight {wpct[k]:g}%")
        meta.append(f"Minimum {mn:.1f}" if _num(mn) else "Minimum not set")
        mk = (f'<span class="mark" style="left:{max(0.0, min(100.0, mn * 10)):.1f}%"></span>'
              if _num(mn) else "")
        rows.append(
            f'<li class="dim t-{t}" data-dimension="{esc(k)}">'
            f'<div class="dim-head"><span class="dim-name">{esc(_label(k))}</span>'
            f'<span class="dim-score">{esc(shown)}</span></div>'
            f'<div class="bar" role="img" aria-label="{esc(_label(k))} {esc(shown)} out of 10"'
            f'><span class="fill" style="width:{fillw:.1f}%"></span>{mk}</div>'
            f'<div class="dim-meta">{"".join(f"<span>{esc(m)}</span>" for m in meta)}'
            f'<span class="st">{esc(status)}</span></div></li>')
    wnote = ("Weights are the ones the reviewer applied"
             if w_src == "reviewer" else "Weights are config's (the review recorded none)")
    if lane == "express":
        wnote += "; the express lane renormalizes them when a phase is skipped"
    dim_html = ['<section class="card" id="dimensions"><h2>Dimensions against their minimums</h2>',
                '<ul class="dims">' + "".join(rows) + "</ul>" if rows else
                '<p class="small">The review records no dimension scores.</p>',
                f'<p class="small">The dark tick on each bar is that dimension&rsquo;s minimum. '
                f'{esc(wnote)}. Dimension scores are the reviewer&rsquo;s rubric judgments.</p>',
                "</section>"]

    # ---- audit --------------------------------------------------------------
    state, rec, drift = read_audit(run_dir)
    verdict_shown = (rec or {}).get("verdict", "") if state == "fresh" \
        else VERDICT_FOR_STATE[state]
    checks = list((rec or {}).get("checks") or [])
    n_pass = sum(1 for c in checks if c.get("result") == "PASS")
    n_fail = sum(1 for c in checks if c.get("result") == "FAIL")
    n_na = sum(1 for c in checks if c.get("result") == "N/A")
    if state == "fresh":
        a_tone = "ok" if rec.get("verdict") == "CLEAN" else "bad"
        head = (f"Audit {rec.get('verdict')}: re-derived from the files as they stand now"
                if rec.get("verdict") == "CLEAN" else
                f"Audit {rec.get('verdict')}: {n_fail} check(s) failed")
    elif state == "stale":
        a_tone = "bad"
        head = (f"AUDIT IS STALE: {len(drift)} file(s) changed after it ran. Its recorded "
                f"verdict ({str(rec.get('verdict')).lower()}) describes an earlier version "
                f"of this run and is not current")
    elif state == "unfingerprinted":
        a_tone = "warn"
        head = ("AUDIT CANNOT BE SHOWN TO BE CURRENT: it carries no file fingerprint "
                f"(recorded verdict: {str(rec.get('verdict')).lower()}). Re-run run-audit.py")
    elif state == "unreadable":
        a_tone = "bad"
        head = "AUDIT RECORD UNREADABLE: run-audit.json exists but cannot be parsed"
    else:
        a_tone = "bad"
        head = ("NOT AUDITED: there is no run-audit.json, so nothing has re-derived this "
                "run's claims from its files")
    audit_html = [f'<section class="card t-{a_tone}" id="audit" data-audit-state="{state}" '
                  f'data-verdict="{esc(verdict_shown)}"><h2>Run audit</h2>',
                  f'<p class="banner">{esc(head)}</p>']
    if manifest.get("audit_skipped"):
        audit_html.append('<p class="banner t-warn">This run was finalized with the audit '
                          'skipped (audit_skipped is stamped in run.json).</p>')
    if state == "stale":
        shown = drift[:10]
        extra = f" and {len(drift) - 10} more" if len(drift) > 10 else ""
        audit_html.append("<p>Changed since the audit: " + esc("; ".join(shown) + extra) + ".</p>")
    if rec is not None:
        when = rec.get("audited_at")
        prefix = "" if state == "fresh" else "As recorded at audit time (not current): "
        audit_html.append(
            f'<p class="small">{esc(prefix)}{n_pass} passed &middot; {n_fail} failed &middot; '
            f'{n_na} not applicable (not checked)'
            f'{(" &middot; audited " + esc(when)) if when else ""}.</p>')
        failing = [c for c in checks if c.get("result") == "FAIL"]
        if failing:
            audit_html.append('<ul class="checks">' + "".join(
                f'<li><b>{esc(c.get("section"))} &middot; {esc(c.get("name"))}</b>'
                f'<span class="d">{esc(c.get("detail") or "")}</span></li>'
                for c in failing) + "</ul>")
        nas = [c for c in checks if c.get("result") == "N/A"]
        if nas:
            audit_html.append(
                f'<details><summary>{len(nas)} check(s) not applicable: not checked, '
                f'not passed</summary><ul class="checks">' + "".join(
                    f'<li>{esc(c.get("section"))} &middot; {esc(c.get("name"))}'
                    f'<span class="d">{esc(c.get("detail") or "")}</span></li>'
                    for c in nas) + "</ul></details>")
        if checks and state == "fresh":
            audit_html.append(
                f'<details><summary>All {len(checks)} checks</summary><ul class="checks">'
                + "".join(f'<li>{esc(c.get("result"))} &middot; {esc(c.get("section"))} '
                          f'&middot; {esc(c.get("name"))}</li>' for c in checks)
                + "</ul></details>")
    audit_html.append("</section>")

    # ---- publication --------------------------------------------------------
    pub = review.get("publication_status")
    src, ledger = fix_ledger_view(run_dir, review)
    out8 = ra._json(run_dir / "phase-8-output.json") or {}
    pub8 = out8.get("publication_status") if isinstance(out8, dict) else None
    docx = sorted(p.name for p in run_dir.glob("*.docx")
                  if "pre-remediation" not in p.name.lower())
    p_tone = {"CLEAR": "ok", "BLOCKED": "bad"}.get(str(pub), "neutral")
    pub_html = [f'<section class="card t-{p_tone}" id="publication" '
                f'data-publication="{esc(pub or "not recorded")}"><h2>Publication status</h2>',
                f'<p><span class="pill t-{p_tone}">{esc(pub or "not recorded")}</span> '
                f'<span class="small">as recorded by the reviewer; the decision and the '
                f'publication status are independent</span></p>']
    if ledger:
        unresolved = ledger.get("unresolved_blocking") or []
        regressed = ledger.get("regressed") or []
        total = ledger.get("total")
        survived = ledger.get("survived")
        pub_html.append(
            f'<p class="small">Fix ledger ({esc(src)}): '
            f'{esc(total if total is not None else "?")} correction(s), '
            f'{esc(survived if survived is not None else "?")} survived, '
            f'{len(unresolved)} unresolved blocking, {len(regressed)} undone downstream.</p>')
        if unresolved or regressed:
            pub_html.append('<ul class="checks">' + "".join(
                f'<li><b>{esc(i)}</b><span class="d">unresolved blocking correction</span></li>'
                for i in unresolved) + "".join(
                f'<li><b>{esc(i)}</b><span class="d">applied, then undone by a later phase</span></li>'
                for i in regressed) + "</ul>")
    else:
        pub_html.append('<p class="small">No fix ledger in this run (it predates the ledger, '
                        'or Phase 4 carried no corrections).</p>')
    if pub8:
        pub_html.append(f'<p class="small">Phase 8 recorded publication status '
                        f'{esc(pub8)}'
                        f'{(" and delivered " + esc(", ".join(docx))) if docx else ""}.</p>')
        if pub and pub8 != pub:
            pub_html.append(f'<p class="banner t-warn">The review says {esc(pub)} but Phase 8 '
                            f'says {esc(pub8)}.</p>')
    elif docx:
        pub_html.append(f'<p class="small">Delivered: {esc(", ".join(docx))}.</p>')
    pub_html.append(f'<p class="small">Run status: {esc(manifest.get("status") or "not recorded")}.'
                    f'</p></section>')

    # ---- the piece ----------------------------------------------------------
    stats = []
    body_name = body_artifact(manifest, run_dir)
    target = (manifest.get("meta") or {}).get("word_count")
    if body_name:
        wc = tm._body_word_count(_read_text(run_dir / body_name) or "")
        note = ""
        if _num(target) and target and scoring:
            tol = scoring["default"]["quality_gates"]["phase_3_draft"]["word_count_tolerance_percent"]
            lo, hi = int(target * (100 - tol) / 100), int(target * (100 + tol) / 100)
            note = (f"target {target:,}, band {lo:,}-{hi:,}: "
                    + ("inside" if lo <= wc <= hi else "OUTSIDE"))
        stats.append(("Body words", f"{wc:,}", note or f"measured from {body_name}"))
    else:
        stats.append(("Body words", "not measured", "no draft artifact in the run"))
    loops = manifest.get("total_loops")
    stats.append(("Loops", str(loops) if loops is not None else "not recorded",
                  "feedback loops recorded in run.json"))
    scan = humanizer_scan(run_dir)
    if scan.get("rating"):
        stats.append(("AI-tell scan", scan["rating"], "advisory, never a gate"))
    else:
        stats.append(("AI-tell scan", "not recorded", "no Phase 6.5 report, or no scan in it"))
    if "signal" in scan:
        ceiling = None
        try:
            ceiling = scoring["default"]["quality_gates"]["phase_6_5_humanizer"]["max_ai_signal_score"]
        except (TypeError, KeyError):
            pass
        stats.append(("Remaining AI signal", f"{scan['signal']:.2f}",
                      f"ceiling {ceiling}" if ceiling is not None else "Phase 6.5 report"))
    if "structure" in scan:
        stats.append(("Structural tells", scan["structure"], "advisory, never a gate"))
    cv = review.get("critical_violations")
    if isinstance(cv, dict) and cv:
        stats.append(("Critical violations",
                      str(sum(v for v in cv.values() if _num(v))),
                      ", ".join(f"{_label(k).lower()} {v}" for k, v in cv.items())))
    piece = ['<section class="card" id="piece"><h2>The piece</h2><ul class="stats">']
    for k, v, n in stats:
        piece.append(f'<li><span class="k">{esc(k)}</span><span class="v">{esc(v)}</span>'
                     f'<span class="n">{esc(n)}</span></li>')
    piece.append("</ul></section>")

    # ---- header + footer ----------------------------------------------------
    chips = [("Brand", brand), ("Type", _label(ctype) if ctype else "not recorded"),
             ("Industry", industry or "not recorded"), ("Lane", lane)]
    head_html = [
        '<header><p class="eyebrow">ContentForge scorecard</p>',
        f"<h1>{esc(title)}</h1>",
    ]
    if topic and topic != title:
        head_html.append(f'<p class="sub">Topic: {esc(topic)}</p>')
    head_html.append('<ul class="chips">' + "".join(
        f"<li>{esc(k)} <b>{esc(v)}</b></li>" for k, v in chips) + "</ul></header>")

    version = _plugin_version()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    foot = [
        "<footer>",
        f"<p>Generated by ContentForge{(' v' + esc(version)) if version else ''} "
        f"&middot; run {esc(run_id)} &middot; built {esc(stamp)}.</p>",
        "<p>Every figure on this page is read from the run&rsquo;s own files; the approve line "
        "and minimums are resolved from the plugin&rsquo;s config. Scores are a reviewer&rsquo;s "
        "rubric judgments. The audit re-derives the policy and the arithmetic, not whether "
        "the writing earned the score. This file is a local copy; nothing here has been "
        "shared.</p>",
        "</footer>",
    ]

    doc = "\n".join([
        "<!doctype html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        '<meta name="color-scheme" content="light dark">',
        f"<title>{esc(title)} &middot; ContentForge scorecard</title>",
        f"<style>{CSS}</style>", "</head>",
        f'<body data-run-id="{esc(run_id)}" data-audit-state="{state}">', "<main>",
        *head_html, *hero, *audit_html, *dim_html, *pub_html, *piece, *foot,
        "</main>", "</body>", "</html>", ""])

    return doc, {
        "run_id": run_id, "decision": decision,
        "overall_score": score if _num(score) else None,
        "verdict_shown": verdict_shown, "audit_state": state,
        "stale_audit": state != "fresh",
    }


def _fail(msg: str):
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(
        description="Render a finished run as one self-contained HTML scorecard.")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default=None,
                    help="output file (default: <run-dir>/scorecard.html)")
    args = ap.parse_args()

    run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    if not run_dir.is_dir():
        _fail(f"no run directory at {run_dir}")

    ra = _load("cf_ra_scorecard", "run-audit.py")
    tm = _load("cf_tm_scorecard", "text-metrics.py")
    manifest = ra._json(run_dir / "run.json")
    if not isinstance(manifest, dict):
        _fail(f"no usable run.json in {run_dir} (missing or corrupt)")
    review = ra._json(run_dir / "phase-7-review.json")
    if not isinstance(review, dict):
        _fail(f"no usable phase-7-review.json in {run_dir}: a scorecard needs a "
              f"reviewed run (Phase 7)")

    doc, summary = render(run_dir, manifest, review, ra, tm)
    out = pathlib.Path(args.out).expanduser().resolve() if args.out \
        else run_dir / "scorecard.html"
    data = doc.encode("utf-8")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, out)
    except OSError as exc:
        _fail(f"could not write {out}: {exc}")

    print(json.dumps({"path": str(out), "bytes": len(data), **summary},
                     indent=2, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
