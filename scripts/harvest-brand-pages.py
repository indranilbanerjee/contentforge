#!/usr/bin/env python3
"""harvest-brand-pages.py — crawl a brand's own website to build the internal-link
inventory and page classification that brand-setup saves into `brand_pages`,
and (v4.0) merge a pipeline run's verified link inventory back into the profile.

Design rules:
- stdlib only; respects robots.txt; identifies itself honestly.
- NEVER invents URLs: every page in the output was fetched live during this run
  (crawl mode) or was live-verified by the phase that produced it (merge mode).
- Polite: capped page count, per-request delay, single-threaded.

Usage:
  python harvest-brand-pages.py --url https://example.com [--max-pages 75]
      [--output harvest.json] [--timeout 15] [--delay 0.3]
  python harvest-brand-pages.py --merge-inventory phase-1-link-inventory.json --brand <slug>

Merge mode (v4.0 — closes the loop Phase 7 used to hand to the owner as a to-do):
Phase 1's Client Site Reconnaissance verifies real brand URLs every run, and that
knowledge used to evaporate with the run. ``--merge-inventory`` upserts the run's
verified rows into the profile's ``brand_pages``:

- ``service_or_product`` rows -> ``product_or_service_pages`` (upsert by URL)
- ``authority`` rows          -> ``authority_pages``          (upsert by URL)
- ``conversion`` rows         -> STAGED into ``brand_pages.recon_candidates`` —
  never auto-activated, because a conversion CTA is a commercial decision a
  human makes; staging collects the evidence without faking the decision.
- ``informational`` / ``other`` rows are skipped (they serve topical linking via
  the run inventory, not brand_pages) and counted in the result.

A row whose URL already exists only gets its ``verified_live`` stamp refreshed —
manually curated ``topic`` / ``anchor_text_hints`` are never overwritten. Writes
are atomic via _common.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser

UA = "ContentForge-BrandHarvester/1.0 (+https://github.com/indranilbanerjee/contentforge)"
SKIP_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".zip", ".doc",
                   ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp4", ".webp", ".ico",
                   ".css", ".js", ".xml", ".rss")
STOPWORDS = {"and", "or", "the", "a", "an", "of", "for", "to", "in", "on", "with", "our", "your", "us"}

# Order matters: first match wins. (category, url_regex, title_regex)
CATEGORY_RULES = [
    ("conversion", r"/(contact|demo|quote|get-started|book|request|subscribe|sign-?up|trial|enquir|inquir)",
     r"\b(contact|demo|quote|request|enquiry|inquiry|get started)\b"),
    ("authority", r"/(about|leadership|team|our-story|company|management|who-we-are)",
     r"\b(about|leadership|team|our story|management)\b"),
    ("service_or_product", r"/(services?|products?|solutions?|platform|capabilit|offerings?|formulation|manufactur|development|technolog)",
     r"\b(services?|products?|solutions?|platform|capabilities|offerings)\b"),
    ("informational", r"/(blog|news|insights?|resources?|articles?|knowledge|case-stud|white-?paper|publication|events?)",
     r"\b(blog|news|insights?|resources?|articles?|case stud)\b"),
]


def classify_page(url: str, title: str) -> tuple[str, str]:
    """Classify a page. Returns (category, evidence)."""
    path = urllib.parse.urlparse(url).path.lower()
    for cat, url_re, _ in CATEGORY_RULES:
        m = re.search(url_re, path)
        if m:
            return cat, f"url matched {m.group(0)!r}"
    for cat, _, title_re in CATEGORY_RULES:
        m = re.search(title_re, (title or "").lower())
        if m:
            return cat, f"title matched {m.group(0)!r}"
    return "other", "no rule matched"


def parse_sitemap_locs(xml_text: str) -> list[str]:
    return [m.strip() for m in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml_text)]


def is_sitemap_index(xml_text: str) -> bool:
    return "<sitemapindex" in xml_text


def _strip_www(netloc: str) -> str:
    """Remove 'www.' prefix from netloc (Python 3.8+ safe)."""
    netloc = netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def filter_candidates(root: str, urls: list[str]) -> list[str]:
    """Same-host http(s) pages only, fragments stripped, binary/file URLs dropped, deduped in order."""
    host = _strip_www(urllib.parse.urlparse(root).netloc)
    seen, kept = set(), []
    for u in urls:
        if not isinstance(u, str) or not u.startswith(("http://", "https://")):
            continue
        u = u.split("#", 1)[0]
        p = urllib.parse.urlparse(u)
        if _strip_www(p.netloc) != host:
            continue
        if p.path.lower().endswith(SKIP_EXTENSIONS):
            continue
        if u not in seen:
            seen.add(u)
            kept.append(u)
    return kept


def topic_keywords(url: str) -> list[str]:
    segs = [s for s in urllib.parse.urlparse(url).path.split("/") if s]
    if not segs:
        return []
    tokens = re.split(r"[-_]+", segs[-1].lower())
    return [t for t in tokens if t and t not in STOPWORDS and not t.isdigit()]


class _PageParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base = base_url
        self.title = ""
        self.h1 = ""
        self.meta_description = ""
        self.links: list[str] = []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(urllib.parse.urljoin(self.base, a["href"]))
        elif tag == "meta" and a.get("name", "").lower() == "description":
            self.meta_description = self.meta_description or (a.get("content") or "").strip()
        elif tag in ("title", "h1"):
            self._in = tag

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        if self._in == "title" and not self.title:
            self.title = data.strip()
        elif self._in == "h1" and not self.h1:
            self.h1 = data.strip()


def parse_page(html_text: str, base_url: str) -> dict:
    p = _PageParser(base_url)
    try:
        p.feed(html_text)
    except Exception:
        pass
    return {"title": p.title, "h1": p.h1, "meta_description": p.meta_description, "links": p.links}


def fetch(url: str, timeout: float) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(1_500_000)
            return r.status, body.decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def _norm_url(u: str) -> str:
    """URL identity for upserts: scheme-insensitive host (www stripped), path
    without trailing slash. Query strings are kept — they can be distinct pages."""
    p = urllib.parse.urlparse((u or "").strip())
    host = _strip_www(p.netloc)
    path = p.path.rstrip("/") or "/"
    q = ("?" + p.query) if p.query else ""
    return f"{host}{path}{q}".lower()


def _load_json_or_none(common_mod, path):
    """common_mod.load_json_safe returns an 'error'-keyed dict for missing or
    corrupt files, never None (ContentForge payloads never carry a top-level
    'error'). Normalize so 'unreadable' has one spelling here."""
    doc = common_mod.load_json_safe(path)
    if isinstance(doc, dict) and "error" in doc:
        return None
    return doc


# Which brand_pages list each recon category upserts into. Conversion is
# deliberately absent: those rows STAGE for human confirmation instead.
MERGE_TARGETS = {
    "service_or_product": "product_or_service_pages",
    "authority": "authority_pages",
}


def merge_inventory(profile: dict, rows: list, today: str) -> dict:
    """Upsert verified recon rows into profile['brand_pages']. Returns a result
    dict; mutates profile in place. Never overwrites manual curation — an
    existing entry only gets its verified_live stamp refreshed."""
    bp = profile.setdefault("brand_pages", {})
    result = {"added": [], "refreshed": [], "staged_conversion": [],
              "skipped_informational": 0, "skipped_invalid": 0}
    for row in rows:
        url = (row.get("url") or "").strip()
        if not url.startswith(("http://", "https://")):
            result["skipped_invalid"] += 1
            continue
        cat = (row.get("category") or "").strip().lower()
        if cat == "conversion":
            staged = bp.setdefault("recon_candidates", {}).setdefault("conversion", [])
            if not any(_norm_url(e.get("url", "")) == _norm_url(url) for e in staged):
                staged.append({"url": url, "title": row.get("title") or "",
                               "verified_live": today, "source": "phase1_recon",
                               "needs_review": True})
                result["staged_conversion"].append(url)
            continue
        target = MERGE_TARGETS.get(cat)
        if target is None:
            result["skipped_informational"] += 1
            continue
        entries = bp.setdefault(target, [])
        existing = next((e for e in entries
                         if _norm_url(e.get("url", "")) == _norm_url(url)), None)
        if existing is not None:
            existing["verified_live"] = today
            result["refreshed"].append(url)
        else:
            entries.append({
                "url": url,
                "topic": row.get("title") or " ".join(topic_keywords(url)) or "",
                "category": "service" if target == "product_or_service_pages" else "authority",
                "anchor_text_hints": [],
                "source": "phase1_recon",
                "verified_live": today,
            })
            result["added"].append(url)
    bp["last_recon_merge"] = today
    return result


def run_merge(args) -> int:
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    import _common
    from datetime import datetime, timezone
    inv_path = __import__("pathlib").Path(args.merge_inventory)
    inv = _load_json_or_none(_common, inv_path)
    if inv is None:
        print(json.dumps({"ok": False, "error": f"cannot read inventory {inv_path}"}))
        return 2
    rows = inv.get("rows") if isinstance(inv, dict) else inv
    if not isinstance(rows, list):
        print(json.dumps({"ok": False, "error": "inventory must be a list of rows "
                          "or an object with a 'rows' list"}))
        return 2
    profile_path = _common.brand_dir(args.brand) / "brand-profile.json"
    profile = _load_json_or_none(_common, profile_path)
    if profile is None:
        print(json.dumps({"ok": False, "error": f"no brand profile at {profile_path}"}))
        return 2
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = merge_inventory(profile, rows, today)
    _common.atomic_write_json(profile_path, profile)
    result.update({"ok": True, "profile": str(profile_path),
                   "counts": {k: (len(v) if isinstance(v, list) else v)
                              for k, v in result.items() if k != "ok"}})
    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawl a brand website into a brand_pages inventory (stdlib, robots-respecting), or merge a run's verified link inventory into the brand profile")
    ap.add_argument("--url", help="Site root, e.g. https://example.com (crawl mode)")
    ap.add_argument("--merge-inventory", help="Path to a phase-1-link-inventory.json to merge into the brand profile (merge mode)")
    ap.add_argument("--brand", help="Brand slug (required with --merge-inventory)")
    ap.add_argument("--max-pages", type=int, default=75)
    ap.add_argument("--output", help="Also write the JSON result to this path")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--delay", type=float, default=0.3)
    args = ap.parse_args()

    if args.merge_inventory:
        if not args.brand:
            ap.error("--merge-inventory requires --brand")
        return run_merge(args)
    if not args.url:
        ap.error("either --url (crawl) or --merge-inventory (merge) is required")

    root = args.url.rstrip("/")
    if not root.startswith(("http://", "https://")):
        root = "https://" + root
    result = {"domain": root, "harvested_at": datetime.now(timezone.utc).isoformat(),
              "method": None, "robots": {"fetched": False, "sitemaps_declared": [], "disallowed_skipped": 0},
              "pages_discovered": 0, "pages_verified": 0, "page_cap": args.max_pages,
              "pages": [], "categorized": {}, "errors": []}

    rp = urllib.robotparser.RobotFileParser()
    status, robots_txt = fetch(root + "/robots.txt", args.timeout)
    if status == 200 and robots_txt:
        rp.parse(robots_txt.splitlines())
        result["robots"]["fetched"] = True
        result["robots"]["sitemaps_declared"] = [
            ln.split(":", 1)[1].strip() for ln in robots_txt.splitlines()
            if ln.lower().startswith("sitemap:")]
    else:
        rp.parse([])  # no robots -> everything allowed

    candidates: list[str] = []
    sitemap_urls = result["robots"]["sitemaps_declared"] or [root + "/sitemap.xml"]
    for sm in sitemap_urls[:5]:
        s_status, s_body = fetch(sm, args.timeout)
        if s_status != 200 or "<" not in s_body:
            continue
        locs = parse_sitemap_locs(s_body)
        if is_sitemap_index(s_body):
            for child in locs[:10]:
                c_status, c_body = fetch(child, args.timeout)
                if c_status == 200:
                    candidates.extend(parse_sitemap_locs(c_body))
                time.sleep(args.delay)
        else:
            candidates.extend(locs)
    if candidates:
        result["method"] = "sitemap"
    else:
        h_status, h_body = fetch(root + "/", args.timeout)
        if h_status == 200:
            candidates = parse_page(h_body, root + "/")["links"]
            result["method"] = "nav_fallback"
        else:
            result["errors"].append(f"homepage fetch failed with status {h_status}")

    candidates = filter_candidates(root, candidates)
    result["pages_discovered"] = len(candidates)
    allowed = [u for u in candidates if rp.can_fetch(UA, u)]
    result["robots"]["disallowed_skipped"] = len(candidates) - len(allowed)

    for u in allowed[: args.max_pages]:
        p_status, p_body = fetch(u, args.timeout)
        if p_status != 200:
            result["errors"].append(f"{u} -> HTTP {p_status or 'error'}")
            continue
        meta = parse_page(p_body, u)
        cat, ev = classify_page(u, meta["title"] or meta["h1"])
        result["pages"].append({"url": u, "status": p_status, "title": meta["title"],
                                "h1": meta["h1"], "meta_description": meta["meta_description"],
                                "category": cat, "category_evidence": ev,
                                "topic_keywords": topic_keywords(u)})
        time.sleep(args.delay)

    result["pages_verified"] = len(result["pages"])
    cats: dict[str, int] = {}
    for pg in result["pages"]:
        cats[pg["category"]] = cats.get(pg["category"], 0) + 1
    result["categorized"] = cats

    out = json.dumps(result, indent=2)
    print(out)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
