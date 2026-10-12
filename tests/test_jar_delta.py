"""Paza pentru panoul „diferența măsurată” și pentru forma simplificată a site-ului.

Aceste teste nu verifică gustul designer-ului, ci doua lucruri care pot minciuni:
 1. ca panoul de diferente afiseaza DOAR numere scrise in rapoartele commit-uite
    si refuza sa inventeze scor pentru un motor nemasurat;
 2. ca pagina ramane un singur flux (o sectiune de intrare, un singur <style>,
    arhiva marcata explicit ca istoric) dupa rearanjare.
"""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
import jar_delta  # noqa: E402


class DeltaPanelTest(unittest.TestCase):
    def test_only_same_run_pairs_are_compared(self):
        pairs = jar_delta.same_run_pairs()
        titles = [p["title"] for p in pairs]
        self.assertIn("CUANTIC live vs CatServer oficial", titles)
        self.assertIn("CUANTIC live vs CUANTIC patch (cod scris de noi)", titles)
        # un motor care nu a pornit nu are voie sa apara ca pereche de diferenta
        for pair in pairs:
            self.assertNotIn("Arclight", pair["title"])
            self.assertNotIn("Mist", pair["title"])

    def test_native_numbers_are_verbatim_from_the_committed_report(self):
        pair = next(p for p in jar_delta.same_run_pairs()
                    if p["title"].startswith("CUANTIC live vs CatServer oficial"))
        rows = {r["label"]: r for r in pair["rows"]}
        self.assertAlmostEqual(rows["RAM stabilă"]["a"], 2328.55, places=2)
        self.assertAlmostEqual(rows["RAM stabilă"]["b"], 2330.6, places=2)
        self.assertAlmostEqual(rows["RAM stabilă"]["delta"], 2.05, places=2)
        self.assertAlmostEqual(rows["p95 MSPT"]["delta"], 0.0, places=6)
        self.assertEqual(pair["state"], "NECONCLUDENT")

    def test_patch_candidate_is_reported_as_rejected_not_as_winner(self):
        pair = next(p for p in jar_delta.same_run_pairs() if "patch" in p["title"])
        self.assertEqual(pair["state"], "RESPINS")
        html = jar_delta._pair_table(pair)
        self.assertIn("jd-chip respins", html)
        self.assertNotIn("câștigător", html)
        self.assertNotIn("🏆", html)

    def test_unmeasured_candidates_have_no_score(self):
        with patch.object(jar_delta, "ladder_rows", return_value=[]):
            html = jar_delta.panel()
        for name in ("Mohist", "LoliServer", "Magma"):
            self.assertIn(name, html)
        unmeasured = [row for row in html.split('data-delta-row')[1:] if 'jd-badge none' in row]
        self.assertGreaterEqual(len(unmeasured), 3)
        for row in unmeasured:
            self.assertIn('<td>—</td><td>—</td>', row)
            self.assertIn('<td class="jd-num"><b>—</b></td>', row)
        self.assertNotIn("câștigător", html)

    def test_family_parse_refuses_to_invent_boot_times(self):
        smokes = jar_delta.family_smokes()
        self.assertTrue(smokes["live-CatServer"]["passed"])
        self.assertFalse(smokes["Arclight"]["passed"])
        self.assertIsNone(smokes["Arclight"]["boot_s"])
        html = jar_delta._matrix_rows(jar_delta.same_run_pairs())
        self.assertIn("nu a pornit cu pack-ul nostru", html)
        self.assertIn("fără scor: nu a ajuns la <code>Done</code>", html)
        # un alt ecosistem care share-a numele nu are voie să fie numit candidat neavăgat
        self.assertNotIn('data-engine="ketting', html)

    def test_missing_reports_render_no_numbers(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp)
            with patch.object(jar_delta, "DOCS", empty), \
                 patch.object(jar_delta, "FAMILY", empty / "ENGINE-FAMILY-RESULT.md"), \
                 patch.object(jar_delta, "ATLAS", empty / "atlas.md"), \
                 patch.object(jar_delta, "BENCH", empty / "BENCH-LIVE.md"):
                html = jar_delta.panel()
        self.assertIn("pagina nu afișează numere", html)
        self.assertNotIn("jd-a\">", html)

    def test_html_is_escaped_and_links_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp)
            (docs / "ENGINE-FAMILY-RESULT.md").write_text(
                '```json\n{"candidates":{"X":{"smoke":{"done_seconds":"1.0",'
                '"passed_smoke":true},"candidate_pack_inventory":{"mods":36},'
                '"jar_sha256":"aa"}}}\n```\n', encoding="utf-8")
            with patch.object(jar_delta, "DOCS", docs), \
                 patch.object(jar_delta, "FAMILY", docs / "ENGINE-FAMILY-RESULT.md"):
                html = jar_delta._matrix_rows([])
        self.assertNotIn("<script", html)

    def test_delta_bar_shows_noise_band_only_when_reported(self):
        pairs = jar_delta.same_run_pairs()
        native = next(p for p in pairs if p["noise_reported"])
        patched = next(p for p in pairs if not p["noise_reported"])
        self.assertIn("jd-noise", jar_delta._delta_bar(native["rows"][0]))
        self.assertNotIn("jd-noise", jar_delta._delta_bar(patched["rows"][0]))
        self.assertIn("fără plajă de zgomot raportată", jar_delta._pair_table(patched))

    def test_archive_is_labeled_history_not_benchmark(self):
        html = jar_delta.panel()
        self.assertIn("Arhiva „cum era înainte”", html)
        self.assertIn("nu</b> ca benchmark", html)
        deltas = {a["label"]: a["pct"] for a in jar_delta.archive_deltas()}
        self.assertLess(deltas["p95 MSPT (ms)"], 0)
        self.assertGreater(deltas["RAM vârf (MiB)"], 0)


class SimplifiedPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")

    def test_entry_instructions_appear_once(self):
        self.assertEqual(self.page.count("Cum intri"), 1)
        self.assertEqual(self.page.count('id="cum-intri"'), 1)

    def test_one_style_block_and_its_guard(self):
        self.assertEqual(self.page.count("<style>"), 1)
        self.assertEqual(self.page.count("</style>"), 1)
        self.assertIn(".jd-section{", self.page.split("<style>", 1)[1].split("</style>", 1)[0])

    def test_no_duplicate_anchor_ids(self):
        import re
        ids = re.findall(r'id="([^"]+)"', self.page)
        dupes = {i for i in ids if ids.count(i) > 1}
        self.assertEqual(dupes, set(), "id-uri duplicate: " + str(sorted(dupes)))
        self.assertIn('id="cifre"', self.page)
        self.assertEqual(ids.count("cifre"), 1)

    def test_measured_sections_are_linked_from_the_hero(self):
        for anchor in ('href="#diferente"', 'href="#tier"', 'href="#atlas"', 'href="#viziune"'):
            self.assertIn(anchor, self.page)

    def test_strategy_voice_keeps_honest_labels(self):
        self.assertIn("Răspunsul onest azi: NEDECIS", self.page)
        self.assertIn("Nu există un câștigător demonstrat", self.page)
        self.assertIn("nu este o listă de viteză", self.page)
        # negatiile („fara zero lag inventat”) sunt permise; sloganul gol, nu
        for banned in ("S = cel mai performant", "10× demonstrat", "merge și pe cartof, fără lag",
                       "cel mai rapid motor este", "câștigătorul este", "🏆"):
            self.assertNotIn(banned, self.page)


if __name__ == "__main__":
    unittest.main()
