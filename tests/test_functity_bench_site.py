"""Garda sectiunii FunCity: cifrele de pe site trebuie sa fie cele din snapshot, iar
ceea ce n-a fost masurat trebuie sa apara scris ca NEMĂSURAT, nu umplut."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
import engine_results  # noqa: E402


class FunctityPanelTest(unittest.TestCase):
    def test_measured_numbers_match_snapshot(self):
        d = engine_results.functity_data()
        self.assertTrue(d, "snapshot lipsa din analysis/FUNCTITY-BENCH.md")
        page = engine_results.functity_panel()
        for run in d["runde"].values():
            for arm in run["arms"].values():
                v = arm.get("done_s") or []
                if v:
                    self.assertIn("%.2f s" % (sum(v) / len(v)), page)
        c = d["runde"].get("C", {})
        self.assertTrue(c.get("arms"), "runda C lipsa din snapshot")
        for arm in c["arms"].values():
            boot = "%.2f s" % arm["boot_medie_wall_s"]
            mspt = "%.2f ms" % arm["mspt_medie_ms"]
            self.assertIn(boot.replace(".", ","), page)
            self.assertIn(mspt.replace(".", ","), page)

    def test_unmeasured_stays_declared(self):
        page = engine_results.functity_panel()
        self.assertIn("NEMĂSURAT", page)
        self.assertIn("join", page.lower())
        for forbidden in ("cel mai rapid server", "zero lag", "1000×"):
            self.assertNotIn(forbidden.lower(), page.lower())

    def test_gc_paragraph_follows_snapshot(self):
        d = engine_results.functity_data()
        page = engine_results.functity_panel()
        gc = d.get("gc", {}).get("runde", {})
        if not gc:
            self.assertIn("Pauze GC: NEMĂSURAT", page)
            return
        self.assertIn("Pauze GC: MĂSURATE", page)
        c = gc.get("C", {})
        self.assertTrue(c, "reprocesarea rundei C lipseste din snapshot")
        for arm in d["brate"]:
            a = c.get(arm)
            if a:
                self.assertIn("boot max/p95 %.0f/%.0f ms" % (a["boot_max_ms"], a["boot_p95_ms"]), page)
        self.assertIn("Runda C", page)
        self.assertIn("trei probe nu justifică", page)
        self.assertIn("sub sarcină cu jucători: NEMĂSURAT", page)

    def test_degrades_honestly_without_data(self):
        with patch.object(engine_results, "functity_data", return_value={}):
            page = engine_results.functity_panel()
        self.assertIn("Nicio măsurătoare", page)
        self.assertNotIn("<td>", page)


if __name__ == "__main__":
    unittest.main()
