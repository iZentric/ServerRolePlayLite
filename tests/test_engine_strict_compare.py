"""Never promote an engine because one selected minimum looks favorable."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from engine_strict_compare import (EXPECTED_BRANDED, EXPECTED_OFFICIAL,
                                   EXPECTED_CANDIDATE, EXPECTED_PACK, ARMS, strict_screen)


class EngineStrictScreenTest(unittest.TestCase):
    def sample(self, value, sha):
        return {"valid": True, "jar_sha256": sha,
                "rss_steady_median_mb": value,
                "cpu_seconds_steady_after_55s": value,
                "spark_tick_min_median_p95_max_ms_1m": [0, 0, value, value],
                "boot_done_s": value, "boot_wall_seconds": value}

    def report(self, patched=8):
        data = {"pack_sha256": EXPECTED_PACK, "candidate_sha256": EXPECTED_CANDIDATE}
        for arm, sha, value in (("branded", EXPECTED_BRANDED, 10),
                                ("official", EXPECTED_OFFICIAL, 11),
                                ("patched", data["candidate_sha256"], patched)):
            for label in ARMS[arm]:
                data[label] = self.sample(value, sha)
        return data

    def test_only_strict_worst_below_best_for_all_metrics_passes_synthetic_screen(self):
        result = strict_screen(self.report())
        self.assertTrue(result["synthetic_screen_pass"])
        self.assertEqual(len(result["checks"]), 5)
        self.assertIn("NEVER auto-release", result["reason"])

    def test_equal_startup_or_worse_ram_rejects_candidate(self):
        report = self.report()
        report["patched-C2"]["boot_wall_seconds"] = 10
        self.assertFalse(strict_screen(report)["synthetic_screen_pass"])
        report = self.report()
        report["patched-C1"]["rss_steady_median_mb"] = 12
        self.assertFalse(strict_screen(report)["synthetic_screen_pass"])

    def test_incomplete_or_wrong_sha_never_promotes(self):
        report = self.report()
        report["patched-C1"]["valid"] = False
        self.assertFalse(strict_screen(report)["synthetic_screen_pass"])
        report = self.report()
        report["branded-A1"]["jar_sha256"] = "wrong"
        self.assertFalse(strict_screen(report)["synthetic_screen_pass"])
        report = self.report()
        report["candidate_sha256"] = EXPECTED_BRANDED
        self.assertFalse(strict_screen(report)["synthetic_screen_pass"])


if __name__ == "__main__":
    unittest.main()
