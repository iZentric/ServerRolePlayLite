"""Gardă pentru scara CUANTIC (candidat → SHA → smoke → A/B) și pentru panoul de pe site.

Scara e singura cale prin care un motor trece din „NEAVĂGAT” în „măsurat”. Testele
se asigură că nu poate minți: fără descărcare nu e fum, fără fum nu e A/B, fără
3 probe valide pe braț nu e verdict, iar site-ul afișează eșecul exact așa cum e.
"""
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "site"))
import cuantic_ladder as ladder  # noqa: E402
import jar_delta  # noqa: E402


def arm(*trials):
    """trials = (rss, cpu, p95, boot) pentru fiecare pornire validă."""
    return [{"rss_steady_median_mb": r, "cpu_seconds_steady_after_55s": c,
             "p95_ms": p, "boot_done_s": b} for r, c, p, b in trials]


BASE = arm((2300, 3.10, 1.20, 10.1), (2540, 3.30, 1.30, 10.5), (2328, 3.09, 1.25, 10.2))


class LadderLogicTest(unittest.TestCase):
    def test_spec_parsing_never_invents_a_url(self):
        items = ladder.candidates_from_spec("Mohist 1.16.5|https://repo1.maven.org/x.jar|AB|GPL-3.0, LoliServer")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["url"], "https://repo1.maven.org/x.jar")
        self.assertEqual(items[0]["licence"], "GPL-3.0")
        self.assertEqual(items[1]["url"], "")
        self.assertIsNone(items[1]["sha256"])

    def test_missing_candidate_or_pack_is_a_hard_stop_not_a_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = None
            try:
                rc = ladder.main(["--pack", str(Path(tmp) / "lipsa.zip"), "--out", tmp,
                                  "--spec", "Mohist|https://invalid.invalid/x.jar"])
            except SystemExit as exc:
                rc = str(exc)
        self.assertIn("pack inexcesibil", str(rc))

    def test_no_spec_does_not_run_anything(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = ladder.main(["--pack", str(Path(tmp)), "--out", tmp, "--spec", ""])
        self.assertEqual(code, 2)

    def test_fewer_than_three_trials_cannot_produce_a_verdict(self):
        state = ladder.summarise(BASE[:2], arm((2290, 3.0, 1.10, 10.0), (2295, 3.1, 1.2, 10.1), (2300, 3.2, 1.3, 10.2)))
        self.assertEqual(state["verdict"], "NEMĂSURAT")
        self.assertIn("minimum 3", state["reason"])

    def test_candidate_worse_than_noise_floor_is_rejected(self):
        state = ladder.summarise(BASE, arm((2585, 4.5, 3.0, 13.0), (2600, 4.6, 3.1, 13.2), (2605, 4.7, 3.2, 13.4)))
        self.assertEqual(state["verdict"], "RESPINS")
        self.assertIn("rss_steady_mib", state["reason"])

    def test_parity_is_not_marketed_as_a_win(self):
        state = ladder.summarise(BASE, arm((2305, 3.00, 1.19, 10.0), (2545, 3.20, 1.30, 10.4), (2330, 3.05, 1.24, 10.1)))
        self.assertEqual(state["verdict"], "PARITATE_OBSERVATĂ")
        self.assertIn("nu e dovadă de câștig", state["reason"])
        self.assertNotIn("câștigător", state["reason"])

    def test_claim_gate_stays_the_authority(self):
        result = ladder.run_gate(Path(__file__).with_name("_inexistent_gate.json"))
        self.assertNotEqual(result.get("exit"), 0)
        self.assertIn("verdict", result)

    def test_download_verifies_sha_before_trusting_a_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            jar = Path(tmp) / "x.jar"
            jar.write_bytes(b"cuantic")
            sha = ladder.download(jar.as_uri(), Path(tmp) / "copy.jar")
            self.assertEqual(len(sha), 64)
            with self.assertRaises(ValueError):
                ladder.download(jar.as_uri(), Path(tmp) / "copy2.jar", "0" * 64)

    def test_baseline_guard_refuses_a_tampered_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "pack.zip"
            import zipfile
            with zipfile.ZipFile(pack, "w") as z:
                z.writestr("mods/only-one.jar", "x")
            with self.assertRaises(ValueError):
                ladder.assert_baseline(pack)

    def test_engine_ab_is_the_only_boot_harness(self):
        with patch.dict(sys.modules, {"engine_ab": None}):
            with tempfile.TemporaryDirectory() as tmp:
                row = ladder.boot_one(Path(tmp), "x", Path(tmp))
        self.assertEqual(row["valid"], False)
        self.assertIn("engine_ab", row["error"])


class LadderOnSiteTest(unittest.TestCase):
    def test_absent_ladder_report_keeps_rows_unmeasured(self):
        self.assertEqual(jar_delta.ladder_rows(), [])
        html = jar_delta.panel()
        self.assertIn("NEAVĂGAT", html)

    def test_ladder_failure_is_rendered_as_a_failure(self):
        payload = {"candidates": {
            "Mohist 1.16.5": {"licence_declared": "GPL-3.0", "smoke_passed": True,
                              "boot_done_s": 11.2, "plugins_enabled": 14,
                              "sha256_actual": "a" * 64,
                              "ab": {"verdict": "NEMĂSURAT",
                                     "reason": "brațele au 0 / 0 probe valide"}},
            "Magma 1.16.5": {"licence_declared": "neverificată",
                             "error": "URLError: nod negăsit"},
        }}
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "CUANTIC-LADDER-RESULT.md"
            doc.write_text("```json\n" + json.dumps(payload) + "\n```\n", encoding="utf-8")
            with patch.object(jar_delta, "LADDER", doc):
                rows = jar_delta.ladder_rows()
                self.assertEqual(len(rows), 2)
                html = jar_delta.panel()
        self.assertIn("a pornit 36/14", html)
        self.assertIn("ESUAT", html)
        self.assertIn("nod negăsit", html)
        # un candidat care arefum dar nu are 3 probe tot nu urcă în clasament
        self.assertIn("NEMĂSURAT", html)

    def test_site_is_still_generable_after_the_ladder_panel(self):
        page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="diferente"', page)
        self.assertIn("Date brute:", page)
        self.assertEqual(page.count("<style>"), 1)


if __name__ == "__main__":
    unittest.main()
