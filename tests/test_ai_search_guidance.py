"""Search and AI-visibility guidance agrees with what the vendors' own pages say.

Found by the 2026-10-27 trends audit of ContentForge's guidance against primary pages. The failures these tests prevent:
  * the FAQ template called FAQ schema "Critical", promised featured snippets and higher click-through, and said to
    implement it because "AI answer engines cite well-structured Q&A". Google's guide to generative AI search (updated
    2026-07-10) says structured data "isn't required for generative AI search, and there's no special schema.org markup
    you need to add"; FAQ rich results have been limited to authoritative government and health sites since August 2023;
  * the SEO/GEO optimizer quoted ChatGPT at 900M weekly users (February 2026) when OpenAI's own October 2026 post says
    more than 1.2 billion, with ads in 89 countries on the Free and Go plans only;
  * the optimizer's "market reality check" carried percentages (zero-click, AI Overview trigger rate, citation shares)
    with no primary page behind them, untagged;
  * the platform spec capped Instagram Reels at 180 seconds (Instagram now lets accounts record and edit up to 20
    minutes, and tells creators reels over 3 minutes are not recommended to new audiences);
  * SUBMISSION.md called llms.txt a "companion standard" (Google Search ignores llms.txt files) and quoted an AI
    Overview prevalence figure with no source;
  * the platform spec carried one file-level "verified July 2026" stamp, so no single number could be checked.
Also pinned, because the audit found them right and they must stay so: Instagram's five-hashtag cap; AI Overviews as
Google's default surface (AI Mode is a separate tab); nothing saying Adobe Firefly never attaches Content Credentials.
Stdlib only; works from an installed copy (no git) by walking the folder.
"""
from __future__ import annotations

import json
import re
import subprocess
import unittest
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".git", "__pycache__", "node_modules", "tests", "results"}
OPTIMIZER = REPO / "agents" / "06-seo-geo-optimizer.md"
SPECS = REPO / "config" / "social-platform-specs.json"


def prose_files() -> list:
    try:
        listed = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True,
                                check=True, timeout=60).stdout.splitlines()
        paths = [REPO / p for p in listed]
    except (OSError, subprocess.SubprocessError):
        paths = [p for p in REPO.rglob("*") if p.is_file()]
    return [p for p in paths if p.is_file() and p.suffix.lower() in {".md", ".json"} and p.name != "CHANGELOG.md"
            and not (set(p.relative_to(REPO).parts) & SKIP_PARTS)]


def day(stamp: str) -> date:
    """A verification stamp is a day, or a month ('2026-07') when only the month was recorded."""
    return date.fromisoformat(stamp if len(stamp) == 10 else stamp + "-01")


def lines_of(text: str):
    for number, line in enumerate(text.splitlines(), 1):
        yield number, line


# --- FAQ / HowTo schema is never sold as an AI-visibility or SEO lever ---------------------------------------------
SCHEMA_SUBJECT = re.compile(r"(?i)\b(FAQ(Page)?|HowTo)\b")
SCHEMA_WORD = re.compile(r"(?i)\b(schema|structured data|markup)\b")
SELLS_IT = re.compile(
    r"(?i)(\(critical\)|huge seo miss|still implement|implement (the )?(faq|howto)[^.]{0,20}(schema|structured data)"
    r"|add (the )?(faq|howto)[^.]{0,20}(schema|structured data)[^.]{0,30}(rich results|google)"
    r"|(faq|howto) schema[^.]{0,12}for (seo|ai|aeo|geo)\b|schema[^.]{0,60}ai answer engines cite"
    r"|enhanced serp display|higher click-through rates|seo focus:\*\*[^|\n]*faq schema)")
HEDGED = re.compile(r"(?i)\b(optional|structure[- ]only|no rich[- ]result|not required|isn't required|never|do not|don't"
                    r"|restricted|deprecated|no special)\b")


def sells_faq_schema(text: str) -> list:
    out = []
    for n, line in lines_of(text):
        if SCHEMA_SUBJECT.search(line) and SCHEMA_WORD.search(line) and SELLS_IT.search(line) and not HEDGED.search(line):
            out.append((n, line.strip()[:120]))
    return out


# --- Google's default AI surface -----------------------------------------------------------------------------------
AI_MODE_AND_DEFAULT = re.compile(r"(?i)AI Mode[^.;\n]{0,70}\bdefault\b|\bdefault\b[^.;\n]{0,40}\bis (now )?AI Mode")
NEGATED = re.compile(r"(?i)\b(not|isn't|remain|remains|separate)\b")


def says_ai_mode_is_default(line: str) -> bool:
    return bool(AI_MODE_AND_DEFAULT.search(line)) and not NEGATED.search(line)


# --- C2PA / Firefly ------------------------------------------------------------------------------------------------
FIREFLY = re.compile(r"(?i)firefly")
WITHHOLDS = re.compile(r"(?i)\b(none of|does not|doesn't|never|no)\b[^.\n]{0,90}(auto-?embed|embed C2PA|attach)|(auto-?embed|attach)[^.\n]{0,30}\b(not|never)\b")


def says_firefly_withholds_credentials(line: str) -> bool:
    return bool(FIREFLY.search(line) and WITHHOLDS.search(line))


# --- the optimizer's statistics block ------------------------------------------------------------------------------
TAGGED = re.compile(r"(?i)(vendor stud|\(openai|openai's|\(google|google's|source:)")


def untagged_percentages(block: str) -> list:
    return [(n, line.strip()[:110]) for n, line in lines_of(block) if "%" in line and not TAGGED.search(line)]


def market_block(text: str) -> str:
    start = text.index("**Market reality check**")
    return text[start:text.index("#### 6.1", start)]


# The figures the optimizer stated as fact before 4.6.0 and no primary page backed: they stay out of every shipped file, in
# whichever wording and with or without the tilde.
RETIRED_STATISTICS = {
    "the Similarweb zero-click share": re.compile(r"(?i)~?\b68%[^.\n]{0,60}(without a click|zero-click)|zero-click[^.\n]{0,60}~?\b68%"),
    "the zero-click share on AI Overview queries": re.compile(r"(?i)zero-click rate is ~?83%|~?\b83%[^.\n]{0,40}zero-click"),
    "the AI Overview trigger-rate range": re.compile(r"(?i)~?\b20% to ~?48%"),
    "a Wikipedia or Reddit citation share": re.compile(r"(?i)\b(wikipedia|reddit)\b\W{0,5}4\d(\.\d)?%"),
    "the Facebook and Yelp over-indexing claim": re.compile(r"(?i)over-index\w* on Facebook"),
}


def retired_statistics(text: str) -> list:
    return [(n, label) for n, line in lines_of(text) for label, pattern in RETIRED_STATISTICS.items() if pattern.search(line)]


class TestFaqSchemaIsNotSold(unittest.TestCase):

    def test_no_shipped_file_sells_faq_or_howto_schema(self):
        found = []
        for p in prose_files():
            for n, line in sells_faq_schema(p.read_text(encoding="utf-8-sig")):
                found.append(f"{p.relative_to(REPO).as_posix()}:{n}: {line}")
        self.assertEqual(found, [], "\n  " + "\n  ".join(found))

    def test_plants(self):
        for sold in ("### FAQ Schema Markup (Critical)",
                     "- Skip FAQ schema markup (huge SEO miss) for the FAQ page",
                     "Google restricts FAQ rich results. Still implement the FAQ schema: AI answer engines cite well-structured Q&A",
                     "- Implement FAQ schema for SEO",
                     "**SEO Focus:** Very High (FAQ schema, long-tail keywords, featured snippets)",
                     "Add the FAQ structured data so Google shows rich results"):
            self.assertTrue(sells_faq_schema(sold), sold)
        for fine in ("FAQPage is optional, structure-only markup; Google restricts FAQ rich results to government and health sites",
                     "Google says there is no special schema.org markup you need for generative AI search",
                     "Never add FAQ schema to get into AI answers", "Article + Organization JSON-LD is the baseline",
                     "HowTo rich results were deprecated in September 2023"):
            self.assertEqual(sells_faq_schema(fine), [], fine)

    def test_the_optimizer_quotes_googles_july_2026_guide(self):
        text = OPTIMIZER.read_text(encoding="utf-8-sig")
        self.assertIn("no special schema.org markup", text)
        self.assertIn("2026-07-10", text)


class TestOptimizerStatistics(unittest.TestCase):

    def setUp(self):
        self.text = OPTIMIZER.read_text(encoding="utf-8-sig")

    def test_chatgpt_scale_is_openais_october_2026_figure(self):
        self.assertNotIn("900M", self.text)
        self.assertNotIn("weekly active users (Feb", self.text)
        block = market_block(self.text)
        self.assertIn("1.2 billion", block)
        self.assertIn("89 countries", block)
        self.assertRegex(block, r"Free and Go")

    def test_every_percentage_in_the_market_block_names_its_source(self):
        found = untagged_percentages(market_block(self.text))
        self.assertEqual(found, [], "\n  " + "\n  ".join(f"{n}: {line}" for n, line in found))

    def test_plants(self):
        self.assertTrue(untagged_percentages("- **~68% of Google searches now end without a click** (early 2026)"))
        self.assertTrue(untagged_percentages("- Wikipedia = 47.9% of ChatGPT factual cites"))
        self.assertEqual(untagged_percentages("- Zero-click estimates differ (vendor study, 2026): ~60%"), [])

    def test_no_shipped_file_states_a_retired_statistic(self):
        found = []
        for path in prose_files():
            found += [f"{path.relative_to(REPO)}:{n}: {label}" for n, label in retired_statistics(path.read_text(encoding="utf-8-sig"))]
        self.assertEqual(found, [], "\n  " + "\n  ".join(found))

    def test_retired_statistics_plants(self):
        old = (
            "- **~68% of Google searches now end without a click** (Similarweb study reported by Search Engine Land, early 2026)",
            "On queries that trigger an AI Overview the zero-click rate is ~83%, versus ~60% on queries without one",
            "2026 trackers report anywhere from ~20% to ~48% of tracked queries",
            "Wikipedia = 47.9% of ChatGPT factual cites; Reddit = 46.7% of Perplexity cites",
            "Reddit 47% / Wikipedia 48%",
            "Google AIO over-indexes on Facebook/Yelp",
        )
        for line in old:
            self.assertTrue(retired_statistics(line), line)
        for line in ("Zero-click estimates differ (vendor study, 2026): ~60%", "Wikipedia is the most-cited source in ChatGPT's factual answers",
                     "Reddit leads in Perplexity's; never quote a share"):
            self.assertEqual(retired_statistics(line), [], line)


class TestGoogleAndAdobeFacts(unittest.TestCase):

    def test_no_file_says_ai_mode_is_the_default(self):
        found = [f"{p.relative_to(REPO).as_posix()}:{n}" for p in prose_files()
                 for n, line in lines_of(p.read_text(encoding="utf-8-sig")) if says_ai_mode_is_default(line)]
        self.assertEqual(found, [])
        self.assertTrue(says_ai_mode_is_default("AI Mode became the default search experience at I/O 2026"))
        self.assertTrue(says_ai_mode_is_default("the default surface is now AI Mode"))
        self.assertFalse(says_ai_mode_is_default("AI Overviews remain Google's default surface; AI Mode is a separate tab"))
        self.assertFalse(says_ai_mode_is_default("AI Mode is not the default experience"))

    def test_no_file_says_firefly_withholds_content_credentials(self):
        found = [f"{p.relative_to(REPO).as_posix()}:{n}" for p in prose_files()
                 for n, line in lines_of(p.read_text(encoding="utf-8-sig")) if says_firefly_withholds_credentials(line)]
        self.assertEqual(found, [])
        self.assertTrue(says_firefly_withholds_credentials("None of these (gpt-image-2, Midjourney v7, Firefly) auto-embed C2PA"))
        self.assertTrue(says_firefly_withholds_credentials("Firefly does not attach Content Credentials"))
        self.assertFalse(says_firefly_withholds_credentials("Adobe applies Content Credentials to Firefly output automatically"))

    def test_submission_does_not_call_llms_txt_a_standard(self):
        text = (REPO / "SUBMISSION.md").read_text(encoding="utf-8-sig")
        self.assertNotRegex(text, r"(?i)llms\.txt companion standard")
        self.assertNotRegex(text, r"(?i)AI Overviews? 55%")


def stale_platform_values(specs: dict) -> list:
    """Values the platforms' own pages contradicted when they were read again on 2026-10-28 (the report listed five corrections
    and two unsourced numbers). Each stays out of the file: one line per value that has come back."""
    out = []
    if specs["bluesky"]["image_specs"]["feed"].get("max_size_mb") != 2:
        out.append("bluesky: an image may be 2 MB (2,000,000 bytes since atproto PR #4823), not 1 MB")
    linkedin = specs["linkedin"]["image_specs"]
    if linkedin["feed"].get("max_size_mb") != 5:
        out.append("linkedin: a photo is 5 MB on LinkedIn's photo page, not 10 MB")
    if "carousel" in linkedin or any("max_slides" in v for v in linkedin.values() if isinstance(v, dict)):
        out.append("linkedin: no page gives 20 slides; a document is 300 pages and a multi-photo post is 20 photos (two products)")
    document = linkedin.get("document", {})
    if (document.get("max_pages"), document.get("max_size_mb")) != (300, 100) or set(document.get("formats", [])) != {"PDF", "PPT", "PPTX", "DOC", "DOCX"}:
        out.append("linkedin: a document post is PDF/PPT/PPTX/DOC/DOCX, 300 pages, 100 MB (no PNG or JPG)")
    multi = linkedin.get("multi_photo", {})
    if (multi.get("max_photos"), multi.get("max_size_mb_each")) != (20, 5):
        out.append("linkedin: a multi-photo post is 20 photos at 5 MB each")
    if "C2PA" not in specs["linkedin"]["ai_disclosure"]["mechanism"] or "none native" in specs["linkedin"]["ai_disclosure"]["mechanism"]:
        out.append("linkedin: LinkedIn shows a C2PA icon on signed media automatically; it is not 'none native'")
    if "WebP" in specs["twitter"]["image_specs"]["feed"]["formats"]:
        out.append("twitter: X accepts GIF, JPEG and PNG only, not WebP")
    if "35%" in specs["twitter"]["algorithm_notes"]:
        out.append("twitter: no X page gives an engagement figure for images")
    if "deprioritized" in specs["twitter"]["hashtags"].get("_note", ""):
        out.append("twitter: X does not say it deprioritizes hashtags; it recommends no more than 2")
    story = specs["facebook"]["image_specs"]["story"]
    if story.get("max_size_mb") == 250 or "max_size_mb" in story:
        out.append("facebook: Meta states no story file size; photos are 10 MB and video is 3 to 90 seconds")
    return out


class TestPlatformSpecs(unittest.TestCase):

    def setUp(self):
        self.specs = json.loads(SPECS.read_text(encoding="utf-8-sig"))

    def test_no_value_the_platform_pages_contradicted_has_come_back(self):
        self.assertEqual(stale_platform_values(self.specs), [])

    def test_the_stale_value_check_fires_on_each_old_value(self):
        old = json.loads(json.dumps(self.specs))
        old["bluesky"]["image_specs"]["feed"]["max_size_mb"] = 1
        old["linkedin"]["image_specs"]["feed"]["max_size_mb"] = 10
        old["linkedin"]["image_specs"]["carousel"] = {"max_slides": 20, "formats": ["PDF", "PNG", "JPG"]}
        del old["linkedin"]["image_specs"]["document"]
        del old["linkedin"]["image_specs"]["multi_photo"]
        old["linkedin"]["ai_disclosure"]["mechanism"] = "none native — disclose manually in post copy"
        old["twitter"]["image_specs"]["feed"]["formats"] = ["PNG", "JPG", "GIF", "WebP"]
        old["twitter"]["algorithm_notes"] += " Images increase engagement by ~35%."
        old["twitter"]["hashtags"]["_note"] = "X has algorithmically deprioritized hashtags through 2025-26"
        old["facebook"]["image_specs"]["story"]["max_size_mb"] = 250
        got = stale_platform_values(old)
        self.assertEqual(len(got), 10, got)
        for platform in ("bluesky", "linkedin", "twitter", "facebook"):
            self.assertTrue([line for line in got if line.startswith(platform + ":")], platform)

    def test_every_stamp_has_a_known_status_and_says_what_is_not_read(self):
        provenance = {k: v for k, v in self.specs["_provenance"].items() if not k.startswith("_")}
        for name, stamp in provenance.items():
            with self.subTest(platform=name):
                self.assertIn(stamp["status"], {"read", "reported", "carried"})
                self.assertTrue(stamp["sources"] and all(s.startswith("https://") for s in stamp["sources"]))
                for key in ("reported", "practice"):
                    self.assertTrue(all(isinstance(x, str) and x for x in stamp.get(key, [])), key)
        for name in ("linkedin", "twitter", "facebook", "bluesky"):
            self.assertEqual(provenance[name]["verified_on"], "2026-10-28", name)

    def test_facebook_says_its_headline_figure_is_reported(self):
        stamp = self.specs["_provenance"]["facebook"]
        self.assertEqual(stamp["status"], "reported")
        self.assertTrue([line for line in stamp["reported"] if "63,206" in line])
        self.assertIn("Reported, not read", self.specs["facebook"]["_limit_note"])

    def test_instagram_hashtag_cap_stays_five(self):
        tags = self.specs["instagram"]["hashtags"]
        self.assertEqual(tags["count_max"], 5)
        self.assertLessEqual(tags["count_min"], tags["count_max"])

    def test_instagram_reels_allow_twenty_minutes_but_recommend_three(self):
        reel = self.specs["instagram"]["image_specs"]["reel"]
        self.assertEqual(reel["max_duration_seconds"], 1200)
        self.assertEqual(reel["recommended_max_duration_seconds"], 180)
        self.assertIn("20 minutes", reel["_note"])

    def test_every_platform_carries_its_own_provenance(self):
        provenance = {k: v for k, v in self.specs["_provenance"].items() if not k.startswith("_")}
        platforms = [k for k, v in self.specs.items() if isinstance(v, dict) and "character_limit" in v or k == "youtube_shorts"]
        self.assertEqual(sorted(provenance), sorted(platforms))
        for name, stamp in provenance.items():
            with self.subTest(platform=name):
                verified, review_by = day(stamp["verified_on"]), day(stamp["review_by"])
                self.assertLess(verified, review_by)
                self.assertLessEqual((review_by - verified).days, 160, "a stamp must expire within about five months")
                self.assertTrue(stamp["sources"], "name at least one page that was read")
                self.assertIn(stamp["status"], {"read", "reported", "carried"})
                for url in stamp["sources"]:
                    self.assertTrue(url.startswith("https://"), url)

    def test_the_file_level_stamp_no_longer_stands_in_for_the_fields(self):
        self.assertNotIn("verified July 2026", self.specs["_description"])

    def test_tiktok_caption_limit_admits_the_sources_split(self):
        note = self.specs["tiktok"]["_limit_note"]
        self.assertIn("2,200", note)
        self.assertIn("4,000", note)


if __name__ == "__main__":
    unittest.main()
