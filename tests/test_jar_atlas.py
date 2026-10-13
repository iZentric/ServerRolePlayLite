"""The published atlas must contain every researched row without fictional rankings."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'site'))
import jar_atlas  # noqa: E402


class AtlasTest(unittest.TestCase):
    def test_all_researched_rows_are_visible_and_filterable(self):
        content = jar_atlas.ATLAS.read_text(encoding='utf-8')
        same = jar_atlas.rows(content, '## A. Duel echivalent posibil', '## B. Celelalte JAR-uri', 4)
        other = jar_atlas.rows(content, '## B. Celelalte JAR-uri', '## Ce înseamnă 10×', 3)
        panel = jar_atlas.panel()
        self.assertEqual((len(same), len(other)), (8, 26))
        self.assertEqual(panel.count('data-atlas-row'), 34)
        self.assertEqual(panel.count('data-kind="same"'), 8)
        self.assertEqual(panel.count('data-kind="other"'), 26)
        self.assertIn('aria-live="polite"', panel)
        self.assertIn('data-atlas-filter="same"', panel)
        self.assertIn('Nu pornește cu 36/14', panel)
        self.assertIn('probe care confirmă 10×', panel)
        self.assertNotIn('10× demonstrat</strong>', panel)

    def test_escape_untrusted_html_and_allow_only_known_link_types(self):
        html = jar_atlas.inline('**test** <script>alert(1)</script> [safe](https://example.org/x) [bad](javascript:evil)')
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<script>', html)
        self.assertIn('href="https://example.org/x"', html)
        self.assertNotIn('href="javascript:', html)

    def test_generated_homepage_contains_atlas_and_script(self):
        page = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        self.assertIn('id="atlas"', page)
        self.assertIn('Se afișează 34 din 34 rânduri', page)
        self.assertIn("document.getElementById('atlas')", page)
        self.assertIn('href="#atlas"', page)
        self.assertNotIn('site/CUANTIC-JAR-ATLAS-2026-10-12.md', page)


if __name__ == '__main__':
    unittest.main()
