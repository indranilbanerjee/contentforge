"""Rendered-link counting in generate-docx.py must count BOTH pathways:
INTERNAL-LINK markers AND plain markdown [text](url) links, split internal/outbound."""
import importlib.util
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
spec = importlib.util.spec_from_file_location("gdocx", SCRIPTS / "generate-docx.py")
gdocx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gdocx)

MD = """# Title
Intro referencing [our analytics service](https://brand.example/services/analytics)
and an outbound source [FDA guidance](https://www.fda.gov/guidance-x).
<!-- INTERNAL-LINK: type=commercial | anchor="analytics platform" | url=https://brand.example/platform | priority=high | reason="r" | section=2 -->
Body text with [another page](https://brand.example/services/dev/) inline.
"""


class TestRenderedLinkCounts(unittest.TestCase):
    def test_counts_both_pathways_split_by_domain(self):
        counts = gdocx.count_rendered_links(MD, brand_domain="brand.example")
        self.assertEqual(counts["marker_links_total"], 1)
        self.assertEqual(counts["inline_links_internal"], 2)
        self.assertEqual(counts["inline_links_outbound"], 1)
        self.assertEqual(counts["internal_links_total"], 3)  # 1 marker + 2 internal inline

    def test_no_domain_known(self):
        counts = gdocx.count_rendered_links(MD, brand_domain=None)
        self.assertEqual(counts["marker_links_total"], 1)
        self.assertEqual(counts["inline_links_internal"], 0)
        self.assertEqual(counts["inline_links_outbound"], 3)
        self.assertEqual(counts["internal_links_total"], 1)

    def test_full_url_brand_domain_accepted(self):
        # brand_domain may be a bare host ("brand.example") or a full URL
        # ("https://www.brand.example") — both must normalize identically.
        counts = gdocx.count_rendered_links(MD, brand_domain="https://www.brand.example")
        self.assertEqual(counts["inline_links_internal"], 2)
        self.assertEqual(counts["inline_links_outbound"], 1)
        self.assertEqual(counts["internal_links_total"], 3)


if __name__ == "__main__":
    unittest.main()
