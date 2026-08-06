"""Unit tests for scripts/harvest-brand-pages.py (network-free)."""
import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("harvest", SCRIPTS / "harvest-brand-pages.py")
harvest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harvest)


class TestClassifyUrl(unittest.TestCase):
    def test_service_url(self):
        cat, ev = harvest.classify_page("https://x.com/services/small-molecule-cdmo/", "Small Molecule CDMO")
        self.assertEqual(cat, "service_or_product")

    def test_conversion_url(self):
        cat, _ = harvest.classify_page("https://x.com/contact-us/", "Contact Us")
        self.assertEqual(cat, "conversion")

    def test_authority_url(self):
        cat, _ = harvest.classify_page("https://x.com/about/leadership/", "Leadership")
        self.assertEqual(cat, "authority")

    def test_blog_url(self):
        cat, _ = harvest.classify_page("https://x.com/blog/why-quality-matters/", "Why Quality Matters")
        self.assertEqual(cat, "informational")

    def test_title_fallback_when_url_opaque(self):
        cat, ev = harvest.classify_page("https://x.com/p/12345", "Our Services — Formulation")
        self.assertEqual(cat, "service_or_product")
        self.assertIn("title", ev)

    def test_unknown_is_other(self):
        cat, _ = harvest.classify_page("https://x.com/xyzzy", "Xyzzy")
        self.assertEqual(cat, "other")


class TestSitemapParsing(unittest.TestCase):
    def test_extracts_locs(self):
        xml = "<urlset><url><loc>https://x.com/a</loc></url><url><loc>https://x.com/b</loc></url></urlset>"
        self.assertEqual(harvest.parse_sitemap_locs(xml), ["https://x.com/a", "https://x.com/b"])

    def test_detects_sitemap_index(self):
        xml = "<sitemapindex><sitemap><loc>https://x.com/s1.xml</loc></sitemap></sitemapindex>"
        self.assertTrue(harvest.is_sitemap_index(xml))
        self.assertEqual(harvest.parse_sitemap_locs(xml), ["https://x.com/s1.xml"])


class TestUrlFiltering(unittest.TestCase):
    def test_same_host_only(self):
        kept = harvest.filter_candidates("https://x.com", [
            "https://x.com/a", "https://other.com/b", "https://x.com/a#frag",
            "https://x.com/file.pdf", "mailto:a@x.com", "https://x.com/a?utm_source=t"])
        self.assertEqual(kept, ["https://x.com/a", "https://x.com/a?utm_source=t"])

    def test_dedup_preserves_order(self):
        kept = harvest.filter_candidates("https://x.com", ["https://x.com/a", "https://x.com/a", "https://x.com/b"])
        self.assertEqual(kept, ["https://x.com/a", "https://x.com/b"])


class TestPageMetaParser(unittest.TestCase):
    def test_extracts_title_h1_meta_links(self):
        html = ('<html><head><title>T1</title>'
                '<meta name="description" content="D1"></head>'
                '<body><h1>H One</h1><a href="/x">x</a><a href="https://x.com/y">y</a></body></html>')
        meta = harvest.parse_page(html, base_url="https://x.com/")
        self.assertEqual(meta["title"], "T1")
        self.assertEqual(meta["h1"], "H One")
        self.assertEqual(meta["meta_description"], "D1")
        self.assertIn("https://x.com/x", meta["links"])
        self.assertIn("https://x.com/y", meta["links"])


class TestTopicKeywords(unittest.TestCase):
    def test_slug_tokens(self):
        self.assertEqual(
            harvest.topic_keywords("https://x.com/services/analytical-development-and-validation/"),
            ["analytical", "development", "validation"])


if __name__ == "__main__":
    unittest.main()
