#!/usr/bin/env python3
"""audit-ledger.py — the canonical, durable output of /contentforge:cf-audit.

Why this exists (v4.0)
----------------------
The content lifecycle loop existed and broke at this exact joint: cf-audit
produced a ranked refresh report, cf-calendar's contract said it "pulls the top
refresh recommendations from the most recent cf-audit output" — and no canonical
file existed, so the handoff only worked when both skills ran in one session.
That is the defect class the pipeline itself cured in v3.16 (file-based phase
handoff) and v3.27 (corrections with no destination), applied here at the
between-skills level: the audit's findings now land at a stated path, validated,
atomically, where cf-calendar and content-refresh read them by contract.

Storage: ``{brand_dir}/audits/audit-<UTC-stamp>.json``. On Cowork the audits/
directory rides the same brand-directory Drive sync as profiles and checkpoints.

Actions
-------
  record   --brand <slug> --file <report.json>   validate + write canonical file
  latest   --brand <slug>                        print the newest audit record
  validate --file <report.json>                  schema-check only, write nothing
  list     --brand <slug>                        one line per stored audit

Schema (record/validate enforce this; extra keys are allowed and preserved):
  generated_at   ISO date/datetime string        (required)
  brand          slug                            (required)
  pieces         list of objects, each with:     (required, may be empty)
      title            non-empty string          (required)
      freshness_score  number 0-100              (required)
      refresh_priority integer >= 1              (required; 1 = most urgent)
      recommended_scope one of light|medium|heavy|retire|none   (required)
      reasons          list of strings           (required, may be empty)
  gap_topics     list of strings                 (required, may be empty)
  retire_candidates list of strings              (required, may be empty)
  aeo_history_considered  true | false | "n/a — no aeo/checks.json for brand"
                                                 (required — "not consulted" and
                                                  "consulted" must be distinguishable;
                                                  a bare omission is how hollow
                                                  inputs are born)

Exit codes: 0 ok · 1 validation failure · 2 usage/IO error.
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

SCOPES = {"light", "medium", "heavy", "retire", "none"}


def _load_json(path):
    """_common.load_json_safe returns an 'error'-keyed dict for missing/corrupt
    files, never None (ContentForge payloads never carry a top-level 'error').
    Normalize so 'unreadable' has one spelling here."""
    doc = _common.load_json_safe(path)
    if isinstance(doc, dict) and "error" in doc:
        return None
    return doc


def validate_record(doc) -> list:
    """Return a list of problems; empty list means valid."""
    problems = []
    if not isinstance(doc, dict):
        return ["record must be a JSON object"]
    if not isinstance(doc.get("generated_at"), str) or not doc.get("generated_at").strip():
        problems.append("generated_at: required non-empty string")
    if not isinstance(doc.get("brand"), str) or not doc.get("brand").strip():
        problems.append("brand: required non-empty string")
    for key in ("gap_topics", "retire_candidates"):
        if not isinstance(doc.get(key), list):
            problems.append(f"{key}: required list (may be empty)")
    aeo = doc.get("aeo_history_considered", "__missing__")
    if aeo == "__missing__":
        problems.append("aeo_history_considered: required — true, false, or an "
                        "explicit 'n/a — <reason>' string; silence is not an answer")
    elif not (aeo is True or aeo is False or
              (isinstance(aeo, str) and aeo.strip().lower().startswith("n/a"))):
        problems.append("aeo_history_considered: must be true, false, or an "
                        "'n/a — <reason>' string")
    pieces = doc.get("pieces")
    if not isinstance(pieces, list):
        problems.append("pieces: required list (may be empty)")
        return problems
    for i, p in enumerate(pieces):
        where = f"pieces[{i}]"
        if not isinstance(p, dict):
            problems.append(f"{where}: must be an object")
            continue
        if not isinstance(p.get("title"), str) or not p.get("title").strip():
            problems.append(f"{where}.title: required non-empty string")
        score = p.get("freshness_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not (0 <= score <= 100):
            problems.append(f"{where}.freshness_score: required number 0-100")
        pri = p.get("refresh_priority")
        if not isinstance(pri, int) or isinstance(pri, bool) or pri < 1:
            problems.append(f"{where}.refresh_priority: required integer >= 1")
        if p.get("recommended_scope") not in SCOPES:
            problems.append(f"{where}.recommended_scope: must be one of "
                            + "|".join(sorted(SCOPES)))
        if not isinstance(p.get("reasons"), list):
            problems.append(f"{where}.reasons: required list (may be empty)")
    return problems


def audits_dir(brand: str) -> Path:
    return _common.brand_dir(brand) / "audits"


def stored_audits(brand: str) -> list:
    """Newest first, by filename stamp (UTC stamps sort lexically)."""
    d = audits_dir(brand)
    if not d.is_dir():
        return []
    return sorted(d.glob("audit-*.json"), reverse=True)


def cmd_record(args) -> int:
    doc = _load_json(Path(args.file))
    if doc is None:
        print(json.dumps({"ok": False, "error": f"cannot read {args.file}"}))
        return 2
    doc.setdefault("brand", args.brand)
    problems = validate_record(doc)
    if problems:
        print(json.dumps({"ok": False, "problems": problems}, indent=2))
        return 1
    if doc["brand"] != args.brand:
        print(json.dumps({"ok": False, "problems": [
            f"record says brand {doc['brand']!r} but --brand is {args.brand!r}"]}))
        return 1
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = audits_dir(args.brand) / f"audit-{stamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    doc["recorded_at"] = datetime.now(timezone.utc).isoformat()
    _common.atomic_write_json(path, doc)
    print(json.dumps({"ok": True, "path": str(path),
                      "pieces": len(doc["pieces"]),
                      "gap_topics": len(doc["gap_topics"])}, indent=2))
    return 0


def cmd_latest(args) -> int:
    stored = stored_audits(args.brand)
    if not stored:
        print(json.dumps({"ok": False,
                          "error": f"no stored audits for brand {args.brand!r} — "
                                   "run /contentforge:cf-audit first",
                          "audits_dir": str(audits_dir(args.brand))}))
        return 1
    doc = _load_json(stored[0])
    if doc is None:
        print(json.dumps({"ok": False, "error": f"newest audit {stored[0]} unreadable"}))
        return 1
    print(json.dumps({"ok": True, "path": str(stored[0]), "record": doc}, indent=2))
    return 0


def cmd_validate(args) -> int:
    doc = _load_json(Path(args.file))
    if doc is None:
        print(json.dumps({"ok": False, "error": f"cannot read {args.file}"}))
        return 2
    problems = validate_record(doc)
    print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    return 1 if problems else 0


def cmd_list(args) -> int:
    rows = []
    for p in stored_audits(args.brand):
        doc = _load_json(p) or {}
        rows.append({"path": str(p), "generated_at": doc.get("generated_at"),
                     "pieces": len(doc.get("pieces", [])),
                     "readable": bool(doc)})
    print(json.dumps({"ok": True, "count": len(rows), "audits": rows}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Canonical store for cf-audit reports")
    sub = ap.add_subparsers(dest="action", required=True)
    p = sub.add_parser("record"); p.add_argument("--brand", required=True); p.add_argument("--file", required=True)
    p = sub.add_parser("latest"); p.add_argument("--brand", required=True)
    p = sub.add_parser("validate"); p.add_argument("--file", required=True)
    p = sub.add_parser("list"); p.add_argument("--brand", required=True)
    args = ap.parse_args()
    return {"record": cmd_record, "latest": cmd_latest,
            "validate": cmd_validate, "list": cmd_list}[args.action](args)


if __name__ == "__main__":
    sys.exit(main())
