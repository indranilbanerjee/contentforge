#!/usr/bin/env python3
"""
refresh_models.py — Poll provider APIs and report drift against the registry.

Reads model_registry.json, calls the provider list endpoints where available,
and prints:
  • Models in the provider catalog that are NOT in the registry (additions to triage)
  • Models the registry still treats as live (current / supported / preview) that
    the provider no longer lists — the real alarm
  • Models the registry already marks deprecated / retired that the provider has
    stopped serving — expected, no action
  • Models the registry marks deprecated / retired that the provider STILL serves
    — the shutdown has not landed yet
  • A simple summary + next_review_due reminder

By default this is REPORT-ONLY. Pass --bump-timestamp to update last_updated
to today after a manual review pass. The script never silently rewrites model
entries; curation is a human decision.

Requires (per provider) one or more of:
  ANTHROPIC_API_KEY   — calls https://api.anthropic.com/v1/models
  OPENAI_API_KEY      — calls https://api.openai.com/v1/models
  GEMINI_API_KEY      — calls https://generativelanguage.googleapis.com/v1beta/models

Usage:
    python refresh_models.py            # report drift
    python refresh_models.py --json     # machine-readable
    python refresh_models.py --bump-timestamp  # set last_updated to today
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from resolve_model import _find_registry, get_registry  # noqa: E402


def _http_get(url: str, headers: dict[str, str], timeout: int = 15) -> dict | None:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def list_anthropic() -> set[str] | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    data = _http_get(
        "https://api.anthropic.com/v1/models",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
    )
    if not data:
        return None
    return {m.get("id") for m in data.get("data", []) if m.get("id")}


def list_openai() -> set[str] | None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    data = _http_get(
        "https://api.openai.com/v1/models",
        {"Authorization": f"Bearer {key}"},
    )
    if not data:
        return None
    return {m.get("id") for m in data.get("data", []) if m.get("id")}


def list_gemini() -> set[str] | None:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    data = _http_get(
        f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
        {},
    )
    if not data:
        return None
    return {
        m.get("name", "").replace("models/", "")
        for m in data.get("models", [])
        if m.get("name")
    }


# Registry statuses the provider is still expected to serve.
LIVE_STATUSES = {"current", "supported", "preview"}

# Fallback review cadence — the quarterly floor from stewardship_policy.
DEFAULT_REVIEW_INTERVAL_DAYS = 90


def _review_interval_days(last_updated: str | None, next_review_due: str | None) -> int:
    """Days between the registry's last_updated and next_review_due.

    Used to carry the existing cadence forward on --bump-timestamp. Falls back
    to the quarterly floor if either date is missing or unparseable."""
    try:
        gap = (date.fromisoformat(next_review_due) - date.fromisoformat(last_updated)).days
    except (TypeError, ValueError):
        return DEFAULT_REVIEW_INTERVAL_DAYS
    return gap if gap > 0 else DEFAULT_REVIEW_INTERVAL_DAYS


def diff(registry_statuses: dict[str, str], live_ids: set[str]) -> dict[str, list[str]]:
    """Partition drift by registry status.

    Comparing bare id sets reports every deprecated/retired entry as STALE, which
    buries the one bucket that matters. `registry_statuses` maps model id ->
    status so each absence can be judged: a live-status model the provider no
    longer lists is an alarm; a deprecated/retired one is the expected outcome.
    """
    registry_ids = set(registry_statuses)
    gone = registry_ids - live_ids
    live_status = {i for i in registry_ids if registry_statuses.get(i, "current") in LIVE_STATUSES}
    sunset = registry_ids - live_status
    return {
        "missing_from_registry": sorted(live_ids - registry_ids),
        "current_but_unlisted": sorted(gone & live_status),
        "deprecated_and_unlisted": sorted(gone & sunset),
        "deprecated_but_still_served": sorted(sunset & live_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report model-registry drift")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--bump-timestamp",
        action="store_true",
        help="Set last_updated to today (use after a manual curation pass)",
    )
    args = parser.parse_args()

    reg = get_registry()
    reg_path = _find_registry()
    by_vendor: dict[str, dict[str, str]] = {}
    for m in reg.get("models", []):
        by_vendor.setdefault(m.get("vendor", ""), {})[m.get("id")] = m.get("status", "current")

    report: dict[str, object] = {
        "registry_path": str(reg_path),
        "registry_last_updated": reg.get("last_updated"),
        "registry_next_review_due": reg.get("next_review_due"),
    }

    for vendor, fetcher in (
        ("anthropic", list_anthropic),
        ("openai", list_openai),
        ("google", list_gemini),
    ):
        live = fetcher()
        if live is None:
            report[vendor] = {"status": "skipped (no API key or fetch failed)"}
            continue
        registry_statuses = by_vendor.get(vendor, {})
        d = diff(registry_statuses, live)
        report[vendor] = {
            "status": "checked",
            "live_count": len(live),
            "registry_count": len(registry_statuses),
            **d,
        }

    if args.bump_timestamp:
        previous_updated = reg.get("last_updated")
        previous_due = reg.get("next_review_due")
        reg["last_updated"] = date.today().isoformat()
        # Carry the existing review cadence forward instead of leaving
        # next_review_due stuck in the past after every bump.
        reg["next_review_due"] = (
            date.today() + timedelta(days=_review_interval_days(previous_updated, previous_due))
        ).isoformat()
        reg_path.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
        report["timestamp_bumped"] = reg["last_updated"]
        report["next_review_due_bumped"] = reg["next_review_due"]

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Registry: {report['registry_path']}")
        print(f"Last updated: {report['registry_last_updated']}  "
              f"(next review due: {report['registry_next_review_due']})")
        if "timestamp_bumped" in report:
            print(f"  -> timestamp bumped to {report['timestamp_bumped']} "
                  f"(next review due {report['next_review_due_bumped']})")
        buckets = (
            ("missing_from_registry", "NEW (served by provider, not in registry — triage)", "+"),
            ("current_but_unlisted", "ALARM (registry says live, provider no longer lists it)", "!"),
            ("deprecated_but_still_served", "PENDING (registry says deprecated/retired, provider still serves it)", "~"),
            ("deprecated_and_unlisted", "EXPECTED (deprecated/retired and gone — no action)", "-"),
        )
        for v in ("anthropic", "openai", "google"):
            r = report.get(v, {})
            print(f"\n{v.upper()}: {r.get('status')}")
            if r.get("status") == "checked":
                drift = False
                for key, label, marker in buckets:
                    if r.get(key):
                        drift = True
                        print(f"  {label}:")
                        for m in r[key]:
                            print(f"    {marker} {m}")
                if not drift:
                    print("  no drift")
    return 0


if __name__ == "__main__":
    sys.exit(main())
