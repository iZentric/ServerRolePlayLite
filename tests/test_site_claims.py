import unittest, os, re
P = os.path.join(os.path.dirname(__file__), "..", "site", "index.html")
class TestFunCitySite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = open(P, encoding="utf-8").read()
    def test_brand(self):
        self.assertIn("FunCity RP Lite", self.html)
    def test_upstream_atribuit(self):
        self.assertIn("Mohist", self.html); self.assertIn("GPL-3.0", self.html)
    def test_sha_legat(self):
        self.assertIn("d6ffa35c", self.html)
    def test_tabelul_cu_date_masurate(self):
        for x in ("33.34", "43.35", "FC-BENCH v4"): self.assertIn(x, self.html)
    def test_fara_promisiuni_golase(self):
        for interzis in ("cel mai rapid server", "garantat", "fara lag", "nu pica"):
            self.assertNotIn(interzis, self.html.lower())
    def test_adresa_jucatorilor(self):
        self.assertIn("92.5.171.150:25565", self.html)
if __name__ == "__main__":
    unittest.main()
