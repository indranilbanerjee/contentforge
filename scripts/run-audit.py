#!/usr/bin/env python3
"""
run-audit.py
============
Re-derives every claim a finished run makes from the artifacts on disk, using
the plugin's own scripts — so "the pipeline says it finished" and "the artifacts
prove it finished" can never drift apart silently.

Why this exists
---------------
This instrument found most of the thirty-eight defects of the August 2026
self-run campaign — but it lived in a session scratchpad, so customers ran the
pipeline without the thing that catches what the pipeline misses. Every failure
class it checks for was observed in a real run at least once: phases recorded
complete without their artifact, an artifact on disk the manifest never heard
of, a delivered body carrying production scaffolding, a valid chart with no
anchor to embed at, corrections silently lost or silently undone, an APPROVED
review beside an unpublishable piece with nothing saying so, a DRAFT deliverable
published under a clean filename.

The auditor holds two disciplines learned the hard way:

1. **It re-derives; it never trusts.** The approve line, the dimension weights
   and the dimension minimums are RESOLVED from config/scoring-thresholds.json
   for the review's industry (and the brand profile's, whichever is stricter) and
   held against what the review recorded; the review's composite is recomputed
   from its own dimension scores; fix-ledger fields are compared against fresh
   script output; loop counts are held to the SMALLER of the caps config sets;
   statuses are checked against the files they describe. An agent's report is a
   claim; the artifact is the evidence.
2. **A missing input downgrades a check to reported-N/A, never to silent-pass.**
   "Not checked" and "checked and fine" are different results, and conflating
   them is how every hollow gate in the campaign was born.

What it does NOT do: it does not re-score the piece's quality (the dimension
scores themselves are the reviewer's judgment), and it does not demand that
every phase ran (the express lane skips phases by recorded choice).

Freshness: the result records a sha256 fingerprint of the files it read (see
``_common.run_artifact_fingerprint``). ``checkpoint-manager.py finalize --status
completed`` recomputes it and refuses when any of those files changed after the
audit, so "a fresh CLEAN verdict" is a comparison, not a promise.

Usage:
    python run-audit.py --brand <slug> --run-id <run_id> [--strict] [--out FILE]
    python run-audit.py --run-dir <path>                 [--strict] [--out FILE]

Writes ``run-audit.json`` into the run directory by default (``--out`` to
override). ``checkpoint-manager.py finalize --status completed`` refuses unless
that record exists with a clean verdict — the audit is the price of the word
"completed".

``--strict`` also fails on N/A checks, for CI-style use.

Exit codes: 0 clean · 1 violations (or, with --strict, N/A) · 2 usage/IO error.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

SCRIPTS = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = SCRIPTS.parent / "config"

PHASE_ORDER = ["0.5", "1", "2", "3", "3.5", "4", "5", "6", "6.5", "7", "8"]

# Composite recomputation tolerance: each dimension is reported to one decimal
# and the composite is rounded to one decimal, so two honest paths to the same
# number can differ by up to 0.1 — plus a hair for float noise.
COMPOSITE_TOLERANCE = 0.15


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read(path: pathlib.Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def _json(path: pathlib.Path):
    try:
        return json.loads(_read(path))
    except (OSError, json.JSONDecodeError):
        return None


# --------------------------------------------------- config-derived policy

def _norm_key(value) -> str:
    """'Real Estate' / 'real-estate' / 'REAL_ESTATE' all become 'real_estate'."""
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")


def resolve_policy(scoring: dict, industry=None, content_type=None) -> dict:
    """The approve line, weights and dimension minimums that config resolves for
    an industry and content type.

    Layers, later wins: ``default`` < ``content_type_overrides.<type>`` <
    ``industry_overrides.<industry>`` — the order the config's own description
    states. An industry that has no override resolves to the default.
    """
    d = scoring["default"]
    policy = {
        "minimum_pass_score": d["minimum_pass_score"],
        "weights": dict(d["dimension_weights"]),
        "minimums": dict(d["quality_gates"]["phase_7_review"]),
    }
    layers = (
        scoring.get("content_type_overrides", {}).get(_norm_key(content_type)),
        scoring.get("industry_overrides", {}).get(_norm_key(industry)),
    )
    for layer in layers:
        if not isinstance(layer, dict):
            continue
        policy["minimum_pass_score"] = layer.get("minimum_pass_score",
                                                 policy["minimum_pass_score"])
        policy["weights"] = dict(layer.get("dimension_weights", policy["weights"]))
        policy["minimums"].update(
            layer.get("quality_gates", {}).get("phase_7_review", {}))
    return policy


def _brand_industry(run_dir: pathlib.Path):
    """The brand profile's industry, when the run sits in the canonical layout
    ``<brand dir>/runs/<run id>`` and a profile can be found — an independent
    source to hold the review's own ``industry`` claim against."""
    if run_dir.parent.name != "runs":
        return None
    brand = run_dir.parent.parent
    candidates = [brand / "brand-profile.json"]
    guidelines = brand / "Brand-Guidelines"
    if guidelines.is_dir():
        candidates += sorted(guidelines.glob("*-brand-profile.json"))
    for path in candidates:
        doc = _json(path) if path.is_file() else None
        if isinstance(doc, dict) and isinstance(doc.get("industry"), str) \
                and doc["industry"].strip():
            return doc["industry"].strip()
    return None


def loop_caps(graph: dict, scoring: dict) -> dict:
    """Every loop cap config sets, reduced to the rule config states once
    (``default.feedback_loop_limits._precedence``): where they disagree, the
    SMALLER cap governs.

      per_edge / total   generic budgets (pipeline-graph.json) vs
                         max_total_loops (scoring-thresholds.json) -> smaller
      named              phase_A_to_B edge caps; the effective cap on an edge is
                         min(per_edge, its named cap)
      groups             caps on a SUM of edges: phase_N_to_any (every
                         phase_N_to_* edge), max_validation_loops (edges leaving
                         phase 4), max_seo_loops (edges leaving phase 6)
    """
    d = scoring["default"]
    limits = {k: v for k, v in d["feedback_loop_limits"].items()
              if not k.startswith("_")}
    budgets = graph["loop_budgets"]
    named, groups = {}, []
    for key, cap in limits.items():
        m = re.fullmatch(r"phase_(.+)_to_any", key)
        if m:
            groups.append((f"edges leaving phase {m.group(1).replace('_', '.')} ({key})",
                           f"phase_{m.group(1)}_to_", cap))
        elif re.fullmatch(r"phase_.+_to_.+", key):
            named[key] = cap
    gates = d["quality_gates"]
    groups.append(("edges leaving phase 4 (max_validation_loops)", "phase_4_to_",
                   gates["phase_4_validation"]["max_validation_loops"]))
    groups.append(("edges leaving phase 6 (max_seo_loops)", "phase_6_to_",
                   gates["phase_6_seo"]["max_seo_loops"]))
    return {
        "per_edge": budgets["per_edge"],
        "total": min(budgets["total_per_run"], limits.get("max_total_loops",
                                                          budgets["total_per_run"])),
        "named": named,
        "groups": groups,
    }


def loop_violations(counts: dict, caps: dict):
    """(per-run violations, per-edge violations) for a manifest's loop_counts."""
    total = sum(counts.values())
    total_v = ([f"{total} loops recorded, per-run cap {caps['total']}"]
               if total > caps["total"] else [])
    edge_v = []
    for edge, n in sorted(counts.items()):
        cap = min(caps["per_edge"], caps["named"].get(edge, caps["per_edge"]))
        if n > cap:
            edge_v.append(f"{edge}: {n} loops, cap {cap}")
    for label, prefix, cap in caps["groups"]:
        n = sum(v for e, v in counts.items() if e.startswith(prefix))
        if n > cap:
            edge_v.append(f"{label}: {n} loops, cap {cap}")
    return total_v, edge_v


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


class Audit:
    def __init__(self):
        self.checks = []

    def check(self, section, name, ok, detail=""):
        self.checks.append({"section": section, "name": name,
                            "result": "PASS" if ok else "FAIL",
                            "detail": detail or None})

    def na(self, section, name, reason):
        self.checks.append({"section": section, "name": name,
                            "result": "N/A", "detail": reason})

    def summary(self, strict=False):
        p = sum(1 for c in self.checks if c["result"] == "PASS")
        f = sum(1 for c in self.checks if c["result"] == "FAIL")
        n = sum(1 for c in self.checks if c["result"] == "N/A")
        verdict = "CLEAN" if f == 0 and (not strict or n == 0) else "VIOLATIONS"
        return {"pass": p, "fail": f, "na": n, "verdict": verdict}


def _audit_review_scores(a: "Audit", review: dict, manifest: dict,
                         run_dir: pathlib.Path, scoring) -> None:
    """Section E, the score half: hold the review's decision against the policy
    config RESOLVES for its industry — not against a number the script (or the
    reviewer) carries in its head.

    The industry is the review's own claim (``industry``) and, independently,
    the brand profile's. When both exist the stricter approve line and the
    stricter minimums bind, and a review that recorded a laxer industry than
    the profile's is itself a failure: a reviewer must not be able to move a
    pharma piece to the default approve line by writing a different word.
    """
    score = review.get("overall_score")
    decision = review.get("decision", "")
    approved = "APPROVED" in str(decision)
    if scoring is None:
        a.na("E review", "approve line",
             "config/scoring-thresholds.json is unreadable — the approve "
             "line, weights and minimums cannot be re-derived")
        return

    ctype = manifest.get("content_type")
    r_ind = review.get("industry")
    r_ind = r_ind.strip() if isinstance(r_ind, str) and r_ind.strip() else None
    p_ind = _brand_industry(run_dir)
    pol_r = resolve_policy(scoring, r_ind, ctype) if r_ind else None
    pol_p = resolve_policy(scoring, p_ind, ctype) if p_ind else None
    pols = [p for p in (pol_r, pol_p) if p] or [resolve_policy(scoring, None, ctype)]
    own = pol_r or pol_p or pols[0]
    line = max(p["minimum_pass_score"] for p in pols)
    if r_ind and p_ind and _norm_key(r_ind) != _norm_key(p_ind):
        who = f"industry {r_ind!r} (brand profile says {p_ind!r}; the stricter binds)"
    elif r_ind or p_ind:
        who = f"industry {r_ind or p_ind!r}"
    else:
        who = "the default (no industry recorded)"
        a.na("E review", "review industry",
             "neither the review nor a brand profile records an industry — "
             "only the default approve line could be applied; a regulated "
             "brand would be held to a higher one")

    if _num(score) and approved:
        a.check("E review", "APPROVED decision is backed by its own score",
                score >= line,
                f"decision {decision} at score {score}; config's approve line "
                f"for {who} is {line}")

    applied = review.get("minimum_pass_score_applied")
    if applied is None:
        a.na("E review", "approve line applied",
             "the review does not record minimum_pass_score_applied "
             "(a review from before the field existed)")
    else:
        a.check("E review", "review applied the approve line its industry resolves to",
                _num(applied) and abs(applied - own["minimum_pass_score"]) < 1e-9,
                f"review applied {applied!r}; config resolves "
                f"{own['minimum_pass_score']} for {who}")

    if pol_r and pol_p:
        a.check("E review", "review industry is not laxer than the brand profile's",
                pol_r["minimum_pass_score"] >= pol_p["minimum_pass_score"],
                f"review industry {r_ind!r} resolves to approve line "
                f"{pol_r['minimum_pass_score']}; brand profile industry {p_ind!r} "
                f"resolves to {pol_p['minimum_pass_score']}")
    elif r_ind and not p_ind:
        a.na("E review", "review industry cross-check",
             "no brand profile industry was found to hold the review's industry against")

    dims = review.get("dimensions")
    have_dims = isinstance(dims, dict) and any(_num(v) for v in dims.values())
    if approved:
        if have_dims:
            mins = {}
            for p in pols:
                for k, v in p["minimums"].items():
                    mins[k] = max(mins.get(k, v), v)
            below = [f"{k} {v} < {mins['min_' + k]}" for k, v in sorted(dims.items())
                     if _num(v) and f"min_{k}" in mins and v < mins[f"min_{k}"]]
            a.check("E review",
                    "APPROVED decision has every dimension at or above its minimum",
                    not below, f"below the minimum config resolves for {who}: {below}")
        else:
            a.na("E review", "dimension minimums",
                 "an APPROVED review records no numeric dimension scores to hold "
                 "against the minimums")

    if review.get("lane") == "express" or manifest.get("mode") == "express":
        a.na("E review", "weights and composite",
             "express lane renormalizes the weights when a phase is skipped; "
             "they are not re-derived")
        return
    wa = review.get("weights_applied")
    if isinstance(wa, dict) and wa:
        as_fraction = all(_num(v) and v <= 1.0 for v in wa.values())
        got = {k: (v * 100 if as_fraction else v) for k, v in wa.items() if _num(v)}
        want = {k: v * 100 for k, v in own["weights"].items()}
        a.check("E review",
                "review weights match the configured weights for its industry",
                set(got) == set(want) and all(abs(got[k] - want[k]) < 1e-6 for k in want),
                f"review applied {wa}; config resolves {want} for {who}")
    else:
        a.na("E review", "review weights", "the review records no weights_applied")
    if _num(score) and isinstance(dims, dict) \
            and all(_num(dims.get(k)) for k in own["weights"]):
        recomputed = sum(dims[k] * own["weights"][k] for k in own["weights"])
        a.check("E review", "overall score matches the weighted dimension scores",
                abs(recomputed - score) <= COMPOSITE_TOLERANCE,
                f"the review's own dimension scores weighted by config give "
                f"{recomputed:.2f}; the review says {score}")
    else:
        a.na("E review", "composite",
             "the review has no complete numeric dimension scores to recompute from")


def audit_run(run_dir: pathlib.Path, strict: bool = False) -> dict:
    a = Audit()
    # Fingerprint FIRST: it describes the bytes this audit is about to read, so
    # a file that changes mid-audit shows up as drift at finalize, not as luck.
    stamp = {"audited_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "fingerprint": _common.run_artifact_fingerprint(run_dir)}
    graph = _json(CONFIG_DIR / "pipeline-graph.json")
    scoring = _json(CONFIG_DIR / "scoring-thresholds.json")

    # ---------------------------------------------------------- A. manifest
    manifest = _json(run_dir / "run.json")
    a.check("A manifest", "run.json parses", manifest is not None)
    if manifest is None:
        return {"run_dir": str(run_dir), "checks": a.checks,
                **a.summary(strict), **stamp}

    completed = [str(x) for x in manifest.get("completed_phases", [])]
    artifacts = manifest.get("phase_artifacts", {})
    a.check("A manifest", "completed phases are known phases",
            set(completed) <= set(PHASE_ORDER),
            f"unknown: {sorted(set(completed) - set(PHASE_ORDER))}")

    missing = [ph for ph in completed
               if not (run_dir / artifacts.get(ph, f"__absent__{ph}")).is_file()]
    a.check("A manifest", "every completed phase has its artifact on disk",
            not missing, f"missing artifacts for phases: {missing}")

    # The invisible-crash window: artifacts present for phases the manifest
    # does not record. Not an error by itself — it is the reconciliation signal
    # resume exists for — but a run FINALIZED with orphans is lying about scope.
    cm = _load("cf_cm_audit", "checkpoint-manager.py")
    orphaned = []
    for ph in PHASE_ORDER:
        if ph in completed:
            continue
        for ext in ("md", "json", "txt"):
            fname, key = cm._artifact_name(ph, ext)
            if key == ph and (run_dir / fname).is_file():
                orphaned.append({"phase": ph, "artifact": fname})
                break
    if manifest.get("status") in ("completed", "blocked"):
        a.check("A manifest", "no orphaned artifacts in a finalized run",
                not orphaned, str(orphaned))
    elif orphaned:
        a.na("A manifest", "orphaned artifacts present (run not finalized)",
             f"reconcile via resume: {orphaned}")

    lc = manifest.get("loop_counts", {})
    a.check("A manifest", "total_loops equals the sum of loop_counts",
            manifest.get("total_loops", 0) == sum(lc.values()),
            f"total_loops={manifest.get('total_loops')} sum={sum(lc.values())}")
    if "loop_history" in manifest:
        hist = manifest["loop_history"]
        a.check("A manifest", "loop history arithmetic matches the counts",
                len(hist) == sum(lc.values()),
                f"history rows={len(hist)} vs count sum={sum(lc.values())}")
    elif lc:
        # Runs created before loop_history existed (pre-3.28) cannot carry it;
        # absence of the KEY dates the run, absence of ROWS would be the defect.
        a.na("A manifest", "loop history",
             "pre-3.28 run: loop_counts exist but the manifest has no "
             "loop_history key — the reasons for these loops were never "
             "persisted and cannot be recovered")

    # Budgets are protocol — checkpoint-manager records a loop, it never refuses
    # one — so the only place a blown budget can be caught is here, from the
    # counts the run itself recorded. The cap rule is the one config states
    # (scoring-thresholds.json feedback_loop_limits._precedence): the SMALLER of
    # the generic and the named caps governs.
    if graph is not None and scoring is not None:
        caps = loop_caps(graph, scoring)
        total_v, edge_v = loop_violations(lc, caps)
        a.check("A manifest", "total loops within the per-run budget",
                not total_v, "; ".join(total_v))
        a.check("A manifest", "every loop edge within its cap",
                not edge_v, "; ".join(edge_v))
    else:
        a.na("A manifest", "loop budgets",
             "config/pipeline-graph.json or config/scoring-thresholds.json is "
             "unreadable — the caps cannot be re-derived")

    # ------------------------------------------------------------- B. body
    body_name = artifacts.get("6.5", "phase-6.5-humanized.md")
    body_path = run_dir / body_name
    body = _read(body_path) if body_path.is_file() else None
    if body is None:
        a.na("B body", "body measurements", f"{body_name} absent")
    else:
        tm = _load("cf_tm_audit", "text-metrics.py")
        scaff = tm._residual_scaffolding(body)
        a.check("B body", "no production scaffolding in the delivered body",
                scaff["clean"], f"{scaff['count']} item(s), first at line "
                f"{scaff['items'][0]['line'] if scaff['items'] else '?'}")

        target = (manifest.get("meta") or {}).get("word_count")
        if target:
            wc = tm._body_word_count(body)
            lo, hi = int(target * 0.9), int(target * 1.1)
            a.check("B body", f"body word count inside the gate ({lo}-{hi})",
                    lo <= wc <= hi, f"{wc} words")
        else:
            a.na("B body", "word count gate", "no word_count in run meta")

        mani = _json(run_dir / "phase-3.5-visual-manifest.json")
        if mani:
            vis = mani if isinstance(mani, list) else mani.get("visuals", [])
            generated = [v for v in vis if v.get("status") == "generated"]
            anchors = set(tm._visual_markers(body)["ids"])
            unanchored = [v.get("id") for v in generated
                          if v.get("placement") != "feature-image"
                          and v.get("id") not in anchors]
            a.check("B body", "every generated inline asset has a body anchor",
                    not unanchored, f"no anchor for: {unanchored}")
            ghosts = [v.get("id") for v in vis
                      if v.get("file_path")
                      and not pathlib.Path(v["file_path"]).is_file()]
            a.check("B body", "no manifest path points at a missing file",
                    not ghosts, f"ghost files: {ghosts}")
        else:
            a.na("B body", "visual anchors", "no visual manifest")

    # -------------------------------------------------------- C. authorship
    src = run_dir / "source-draft.md"
    if src.is_file() and body is not None:
        au = _load("cf_au_audit", "authorship.py")
        rec = au.classify(_read(src), body)
        v = rec["violations"]
        a.check("C authorship", "zero author sentences rewritten",
                v["author_sentences_rewritten"] == 0, str(v))
        a.check("C authorship", "zero author sentences dropped",
                v["author_sentences_dropped"] == 0, str(v))
        stored = _json(run_dir / "phase-6.5-authorship.json")
        if stored is not None:
            a.check("C authorship",
                    "stored authorship record matches a fresh measurement",
                    stored.get("author_word_share") == rec["author_word_share"],
                    f"stored {stored.get('author_word_share')} vs fresh "
                    f"{rec['author_word_share']} — the stored record predates "
                    f"a body change")
    elif src.is_file():
        a.na("C authorship", "authorship", "source draft present but no body")
    else:
        a.na("C authorship", "authorship", "no source draft in this run")

    # -------------------------------------------------------- D. fix ledger
    ledger_path = run_dir / "phase-4-fixes.json"
    ledger_verify = None
    if ledger_path.is_file() and body is not None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "fix-ledger.py"), "verify",
             "--run-dir", str(run_dir), "--target", body_name],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        try:
            ledger_verify = json.loads(proc.stdout)
        except json.JSONDecodeError:
            ledger_verify = None
        a.check("D ledger", "fix-ledger verify produced a readable result",
                ledger_verify is not None, proc.stdout[:200])
        if ledger_verify:
            a.check("D ledger", "no correction was undone downstream",
                    ledger_verify.get("regressed") == [],
                    f"regressed: {ledger_verify.get('regressed')}")
    elif ledger_path.is_file():
        a.na("D ledger", "ledger verification", "ledger present but no body")
    else:
        a.na("D ledger", "fix ledger", "no phase-4-fixes.json (pre-3.27 run, "
             "or Phase 4 carried no corrections)")

    # ------------------------------------------------------------ E. review
    review = _json(run_dir / "phase-7-review.json")
    if review:
        _audit_review_scores(a, review, manifest, run_dir, scoring)
        pub = review.get("publication_status")
        if ledger_verify and pub:
            a.check("E review",
                    "review publication_status agrees with the ledger",
                    pub == ledger_verify.get("publication_status"),
                    f"review says {pub}, ledger verify says "
                    f"{ledger_verify.get('publication_status')}")
        elif ledger_verify and not pub:
            a.check("E review", "review records a publication_status",
                    False, "a run with a fix ledger needs the review to say "
                           "whether the piece is publishable")
    else:
        a.na("E review", "review checks", "no phase-7-review.json")

    # ------------------------------------------------------ F. deliverable
    out8 = _json(run_dir / "phase-8-output.json")
    docx = [p for p in run_dir.glob("*.docx")
            if "pre-remediation" not in p.name.lower()]
    if out8:
        pub8 = out8.get("publication_status")
        if ledger_verify and pub8:
            a.check("F deliverable", "phase-8 status agrees with the ledger",
                    pub8 == ledger_verify.get("publication_status"),
                    f"phase-8 says {pub8}, ledger says "
                    f"{ledger_verify.get('publication_status')}")
        if pub8 == "BLOCKED" and docx:
            a.check("F deliverable", "blocked deliverable is marked DRAFT",
                    all(d.name.upper().startswith("DRAFT-") for d in docx),
                    f"{[d.name for d in docx]}")
        if docx:
            bad = []
            for d in docx:
                try:
                    with zipfile.ZipFile(d) as z:
                        if z.testzip() is not None or \
                                "word/document.xml" not in z.namelist():
                            bad.append(d.name)
                except zipfile.BadZipFile:
                    bad.append(d.name)
            a.check("F deliverable", "every .docx is valid OOXML",
                    not bad, f"invalid: {bad}")
    else:
        a.na("F deliverable", "deliverable checks", "no phase-8-output.json")

    # ----------------------------------------------------- G. status honesty
    status = manifest.get("status")
    if status == "completed":
        problems = []
        if ledger_verify and ledger_verify.get("publication_status") == "BLOCKED":
            problems.append("fix ledger holds unresolved blocking corrections")
        if review and review.get("publication_status") == "BLOCKED":
            problems.append("review says BLOCKED")
        a.check("G honesty", "'completed' is not hiding a blocked publication",
                not problems, "; ".join(problems))
    elif status and str(status).startswith("blocked"):
        a.check("G honesty", "'blocked' names at least one open blocker",
                bool(ledger_verify and ledger_verify.get("unresolved_blocking"))
                or bool(review and review.get("publication_status") == "BLOCKED"),
                "status is blocked but no artifact records an open blocker")

    return {"run_dir": str(run_dir), "run_id": manifest.get("run_id"),
            "status": status, "checks": a.checks, **a.summary(strict), **stamp}


def main():
    ap = argparse.ArgumentParser(
        description="Re-derive every gate of a run from its artifacts.")
    ap.add_argument("--brand")
    ap.add_argument("--run-id", type=_common.run_id_arg)
    ap.add_argument("--run-dir")
    ap.add_argument("--strict", action="store_true",
                    help="N/A checks also fail the verdict")
    ap.add_argument("--out", default=None,
                    help="result path (default: <run-dir>/run-audit.json)")
    args = ap.parse_args()

    if args.run_dir:
        run_dir = pathlib.Path(args.run_dir).expanduser().resolve()
    elif args.brand and args.run_id:
        run_dir = (_common.brand_dir(args.brand) / "runs" / args.run_id).resolve()
    else:
        print(json.dumps({"error": "need --run-dir, or --brand and --run-id"}))
        sys.exit(2)

    if not run_dir.is_dir():
        print(json.dumps({"error": f"no run directory at {run_dir}"}))
        sys.exit(2)

    result = audit_run(run_dir, strict=args.strict)
    out = pathlib.Path(args.out).expanduser() if args.out \
        else run_dir / "run-audit.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    result["written_to"] = str(out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["verdict"] == "CLEAN" else 1)


if __name__ == "__main__":
    main()
