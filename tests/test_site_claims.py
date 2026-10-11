"""Guard against marketing a benchmark loser as a new engine or RP plans as live."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))
import engine_results  # noqa: E402


class SiteClaimsTest(unittest.TestCase):
    def test_winner_requires_matching_player_and_release_provenance(self):
        page = engine_results.panel()
        self.assertIn(engine_results.JAR_URL, page)
        self.assertIn("96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c", page)
        self.assertIn("identic byte-cu-byte", page)
        self.assertIn("nu este upgrade demonstrat", page)
        self.assertIn("Arclight cu pack-ul complet", page)
        self.assertIn("Mist pe Java 11", page)

    def test_missing_proof_cannot_advertise_direct_jar(self):
        with patch.object(engine_results, "result", return_value={}):
            page = engine_results.panel()
        self.assertNotIn(engine_results.JAR_URL, page)
        self.assertIn("nu afișăm un câștigător nou neverificat", page)

    def test_strategy_is_labeled_future_work(self):
        page = engine_results.strategy_panel()
        self.assertIn('id="viziune"', page)
        self.assertIn("survival + mafii", page)
        self.assertIn("nu funcții declarate deja lansate", page)
        self.assertIn("STRATEGIE-ROLEPLAY-SURVIVAL.md", page)
        self.assertIn("OptiFine + modurile normale", page)
        self.assertIn("INCIDENT-2026-10-11-STATUS.md", page)

    def test_tunnel_config_requires_external_credential(self):
        import re
        for name in ("cuantic-live.sh", "ensure-up.sh", "frps-install.sh", "up.sh"):
            source = (ROOT / "scripts" / name).read_text()
            self.assertNotRegex(source, r'auth\.token = \\?"(?!%s)[^"\\]+\\?"', name)
        self.assertIn("FRP_AUTH_TOKEN", (ROOT / "scripts" / "frps-install.sh").read_text())

    def test_built_page_contains_benchmark_download_and_strategy(self):
        page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn(engine_results.JAR_URL, page)
        self.assertIn("BENCHMARK-MOTOARE-CUANTIC-2026-10-12.md", page)
        self.assertIn('id="viziune"', page)
        self.assertNotIn("merge și pe cartof, fără lag", page)
        self.assertNotIn("32 de moduri si 15 pluginuri", page)


if __name__ == "__main__":
    unittest.main()
