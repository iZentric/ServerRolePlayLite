"""The tier list must rank evidence only, never invent a performance winner."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
import jar_atlas  # noqa: E402
import jar_tier  # noqa: E402


class TierClassificationTest(unittest.TestCase):
    def setUp(self):
        self.text = jar_atlas.ATLAS.read_text(encoding="utf-8")
        self.buckets, self.hybrids, self.alternatives = jar_tier.classify(self.text)
        self.total = sum(len(entries) for entries in self.buckets.values())

    def test_every_atlas_row_lands_in_exactly_one_tier(self):
        self.assertEqual((self.hybrids, self.alternatives), (8, 26))
        self.assertEqual(self.total, 34)
        self.assertEqual([len(self.buckets[letter]) for letter, _, _ in jar_tier.TIERS],
                         [2, 1, 2, 3, 26])

    def test_tiers_are_derived_from_the_atlas_not_hardcoded(self):
        names = {letter: [entry["name"] for entry in self.buckets[letter]]
                 for letter, _, _ in jar_tier.TIERS}
        self.assertIn("**CUANTIC live**", names["S"][0])
        self.assertIn("CatServer oficial", names["S"][1])
        self.assertIn("SortedArraySet", names["A"][0])
        self.assertEqual(len(names["B"]), 2)
        self.assertTrue(all("Arclight" in n or "Mist" in n for n in names["B"]))

    def test_unmeasured_jars_can_never_reach_a_measured_tier(self):
        measured = [entry["name"] for letter in ("S", "A", "B")
                    for entry in self.buckets[letter]]
        for unmeasured in ("Mohist", "LoliServer", "Magma"):
            self.assertFalse(any(unmeasured in name for name in measured),
                             f"{unmeasured} has no 36/14 smoke and must stay out of S/A/B")
            self.assertTrue(any(unmeasured in entry["name"]
                                for entry in self.buckets["C"]))

    def test_non_equivalent_ecosystems_are_not_counted_as_defeated_engines(self):
        self.assertEqual(len(self.buckets["D"]), self.alternatives)
        for name in ("**Folia**", "**Paper**", "**Fabric / Quilt**"):
            self.assertTrue(any(name in entry["name"] for entry in self.buckets["D"]))

    def test_incomplete_atlas_refuses_to_publish_a_partial_tier_list(self):
        truncated = self.text.split("## B. Celelalte JAR-uri")[0] + "## Ce înseamnă 10×\n"
        with self.assertRaises(ValueError):
            jar_tier.classify(truncated)

    def test_missing_atlas_degrades_instead_of_guessing(self):
        original = jar_tier.ATLAS
        jar_tier.ATLAS = original.parent / "NU-EXISTA.md"
        try:
            panel = jar_tier.panel()
        finally:
            jar_tier.ATLAS = original
        self.assertIn("indisponibil", panel)
        self.assertNotIn("data-tier-row", panel)


class ConsumptionVerdictTest(unittest.TestCase):
    def setUp(self):
        self.entries = jar_tier.measured()

    def test_all_five_measures_are_read_from_the_raw_report(self):
        self.assertEqual(len(self.entries), 5)
        raw = jar_tier.NATIVE.read_text(encoding="utf-8")
        for entry in self.entries:
            self.assertIn(entry["cuantic_raw"], raw)
            self.assertIn(entry["official_raw"], raw)

    def test_raw_cells_are_shown_verbatim_without_float_drift(self):
        by_label = {entry["label"]: entry for entry in self.entries}
        self.assertEqual(by_label["RAM RSS în fereastra stabilă"]["cuantic_raw"],
                         "2205,1 / 2452,0")
        self.assertEqual(by_label["Boot intern până la `Done`"]["cuantic_raw"],
                         "9,770 / 10,509")

    def test_two_trials_per_arm_never_produce_a_winner(self):
        for entry in self.entries:
            label, _ = jar_tier.verdict(entry)
            self.assertTrue(label.startswith("NECONCLUDENT"), label)
            self.assertIn("2 probe/braț", label)

    def test_medians_use_romanian_decimal_comma(self):
        self.assertEqual(jar_tier._ro(2328.55), "2328,55")
        self.assertEqual(jar_tier._ro(2330.6), "2330,60")

    def test_missing_raw_report_hides_every_number(self):
        block = jar_tier._consumption_block([])
        self.assertIn("nu este disponibil", block)
        self.assertNotIn("MiB", block.replace("niciun număr", ""))


class TierPanelClaimsTest(unittest.TestCase):
    def setUp(self):
        self.panel = jar_tier.panel()

    def test_panel_ranks_evidence_and_never_crowns_a_champion(self):
        self.assertIn('id="tier"', self.panel)
        self.assertIn("Răspunsul onest azi: NEDECIS", self.panel)
        self.assertIn("Nu există un câștigător demonstrat", self.panel)
        self.assertIn("nu este o listă de viteză", self.panel)
        for forbidden in ("cel mai rapid motor este", "câștigătorul este",
                          "10× demonstrat", "S = cel mai performant",
                          "zero lag", "🏆"):
            self.assertNotIn(forbidden, self.panel)

    def test_panel_states_the_measured_gap_is_inside_the_noise(self):
        self.assertIn("~2 MiB la RSS", self.panel)
        self.assertIn("247–290 MiB", self.panel)

    def test_panel_names_the_rule_that_would_change_the_ranking(self):
        self.assertIn("minimum <b>3 repetări reale pe braț</b>", self.panel)
        self.assertIn("scripts/cuantic_tenx_gate.py", self.panel.replace("<code>", "").replace("</code>", ""))
        self.assertIn("NEMASURAT", self.panel)

    def test_panel_covers_every_row_and_links_to_the_atlas(self):
        self.assertEqual(self.panel.count('data-tier="D"'), 26)
        self.assertEqual(self.panel.count('data-tier="C"'), 3)
        self.assertIn('href="#atlas"', self.panel)

    def test_tier_rows_do_not_collide_with_atlas_row_counters(self):
        self.assertEqual(jar_atlas.panel().count("data-atlas-row"), 34)
        self.assertEqual(self.panel.count("data-tier-band"), 5)


class BuiltPageTest(unittest.TestCase):
    def setUp(self):
        self.page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")

    def test_generated_homepage_contains_the_tier_list_and_the_atlas(self):
        self.assertIn('id="tier"', self.page)
        self.assertIn('href="#tier"', self.page)
        self.assertIn("document.getElementById('tier')", self.page)
        self.assertEqual(self.page.count('data-tier="D"'), 26)
        # the atlas must survive next to it
        self.assertIn('id="atlas"', self.page)
        self.assertIn("Se afișează 34 din 34 rânduri", self.page)

    def test_tier_list_does_not_introduce_banned_marketing_claims(self):
        for forbidden in ("merge și pe cartof, fără lag", "32 de moduri si 15 pluginuri",
                          "2643 MB · boot 11.521s", "2814 MB · boot 11.062s", "(0 MB)"):
            self.assertNotIn(forbidden, self.page)

    def test_tier_css_block_is_closed_inside_the_single_style_tag(self):
        self.assertEqual(self.page.count("<style>"), 1)
        self.assertEqual(self.page.count("</style>"), 1)
        style = self.page.split("<style>", 1)[1].split("</style>", 1)[0]
        self.assertIn(".tier-section{", style)
        self.assertIn(".tier-band[data-tier-band=\"S\"]", style)
        self.assertEqual(style.count("<style"), 0)


if __name__ == "__main__":
    unittest.main()
