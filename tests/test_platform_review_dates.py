"""A platform limit is re-read before its review date, not after.

config/social-platform-specs.json carries a verified_on and a review_by for every platform in `_provenance`. The test in
test_ai_search_guidance.py keeps each stamp to about five months, but nothing failed when a review_by came or went, so a limit
could age past its date without anyone being told. This test fails from 30 days before the earliest review_by (and for any
review_by that has passed), which leaves a month to read the platform's page again, correct the number and move the date.

CF_TODAY=YYYY-MM-DD freezes today. Stdlib only; works from an installed copy.
"""
from __future__ import annotations

import json
import os
import unittest
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPECS = REPO / "config" / "social-platform-specs.json"
WARN_DAYS = 30


def today() -> date:
    frozen = os.environ.get("CF_TODAY")
    return date.fromisoformat(frozen) if frozen else date.today()


def platforms(specs: dict) -> dict:
    return {k: v for k, v in (specs.get("_provenance") or {}).items() if not k.startswith("_") and isinstance(v, dict)}


def reviews_due(specs: dict, on: date, warn_days: int = WARN_DAYS) -> list[str]:
    """One line per platform whose review_by is within warn_days of `on`, or already past, or not a full date."""
    out = []
    for name, stamp in sorted(platforms(specs).items()):
        try:
            due = date.fromisoformat(stamp["review_by"])
        except (KeyError, TypeError, ValueError):
            out.append(f"{name}: review_by must be a full date (YYYY-MM-DD), found {stamp.get('review_by')!r}")
            continue
        left = (due - on).days
        if left <= warn_days:
            days = lambda n: f"{n} day" if n == 1 else f"{n} days"
            when = f"passed {days(-left)} ago" if left < 0 else "is today" if left == 0 else f"is {days(left)} away"
            out.append(f"{name}: review_by {due} {when}; read {', '.join(stamp.get('sources') or ['its page'])} again, "
                       f"then correct the limits and move verified_on, status and review_by")
    return out


class TestPlatformReviewDates(unittest.TestCase):

    def setUp(self):
        self.specs = json.loads(SPECS.read_text(encoding="utf-8-sig"))

    def test_no_platform_review_is_due_within_30_days(self):
        problems = reviews_due(self.specs, today())
        self.assertEqual(problems, [], "\n  " + "\n  ".join(problems))

    def test_every_platform_is_read(self):
        """A scan that found nothing would pass for the wrong reason."""
        found = platforms(self.specs)
        for name in ("linkedin", "twitter", "instagram", "facebook", "threads", "tiktok", "bluesky", "youtube_shorts"):
            self.assertIn(name, found)

    def test_plants(self):
        specs = {"_provenance": {"_description": "x", "demo": {"verified_on": "2026-07", "review_by": "2026-12-31", "sources": ["https://example.com"]}}}
        self.assertEqual(reviews_due(specs, date(2026, 11, 30)), [])                      # 31 days ahead
        self.assertIn("30 days away", reviews_due(specs, date(2026, 12, 1))[0])            # the first day it fails
        self.assertIn("is today", reviews_due(specs, date(2026, 12, 31))[0])
        past = reviews_due(specs, date(2027, 1, 5))                                       # a review date that has passed
        self.assertEqual(len(past), 1)
        self.assertIn("passed 5 days ago", past[0])
        self.assertIn("https://example.com", past[0])

    def test_a_missing_or_partial_date_fails(self):
        for stamp in ({}, {"review_by": "2026-12"}, {"review_by": None}, {"review_by": "soon"}):
            specs = {"_provenance": {"demo": dict(stamp)}}
            self.assertIn("full date", reviews_due(specs, date(2026, 1, 1))[0], stamp)

    def test_the_planted_past_date_in_a_whole_file(self):
        """The same check against a copy of the real file with one platform's review date moved into the past."""
        specs = json.loads(json.dumps(self.specs))
        specs["_provenance"]["instagram"]["review_by"] = (today() - timedelta(days=1)).isoformat()
        got = reviews_due(specs, today())
        self.assertTrue(any(line.startswith("instagram:") and "passed 1 day ago" in line for line in got), got)


WORKFLOW = REPO / ".github" / "workflows" / "dated-checks.yml"


def workflow_problems(text: str) -> list[str]:
    """What the weekly job must do for an expiring date to reach someone: run weekly, run on demand, run this test, report it."""
    live = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))      # a commented-out line does nothing
    problems = []
    if "schedule:" not in live or "cron:" not in live:
        problems.append("it has no weekly schedule")
    if "workflow_dispatch" not in live:
        problems.append("it cannot be started by hand")
    if "tests.test_platform_review_dates" not in live:
        problems.append("it does not run tests.test_platform_review_dates")
    if "gh issue" not in live or "dated-check" not in live:
        problems.append("it does not open or update a dated-check issue on failure")
    return problems


class TestTheWeeklyJob(unittest.TestCase):
    """The date test fails only when someone runs it, and a quiet repo is not run. The weekly job runs it."""

    def test_the_weekly_job_runs_this_test_and_reports_a_failure(self):
        self.assertEqual(workflow_problems(WORKFLOW.read_text(encoding="utf-8-sig")), [])

    def test_plants(self):
        real = WORKFLOW.read_text(encoding="utf-8-sig")
        self.assertTrue(workflow_problems(real.replace("schedule:", "# schedule:").replace("cron:", "# cron:")))
        self.assertTrue(workflow_problems(real.replace("workflow_dispatch", "")))
        self.assertTrue(workflow_problems(real.replace("tests.test_platform_review_dates", "tests.test_something_else")))
        self.assertTrue(workflow_problems(real.replace("gh issue", "echo")))
        self.assertTrue(workflow_problems(""))


if __name__ == "__main__":
    unittest.main()
