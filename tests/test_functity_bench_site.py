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

    def test_unmeasured_stays_declared(self):
        page = engine_results.functity_panel()
        self.assertIn("NEMĂSURAT", page)
        self.assertIn("join", page.lower())
        for forbidden in ("cel mai rapid server", "zero lag", "1000×"):
            self.assertNotIn(forbidden.lower(), page.lower())

    def test_degrades_honestly_without_data(self):
        with patch.object(engine_results, "functity_data", return_value={}):
            page = engine_results.functity_panel()
        self.assertIn("Nicio măsurătoare", page)
        self.assertNotIn("<td>", page)


if __name__ == "__main__":
    unittest.main()
