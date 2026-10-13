#!/usr/bin/env python3
"""Porțile de migrare: gazda nouă nu primește serverul pe încredere."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import cuantic_migrate as M  # noqa: E402

LIVE = {"pack_sha256": "a" * 64, "micro_ops_s": 1_000, "boot_done_s": 11.8,
        "rss_mib": 2330.0, "mods": 36, "plugins_enabled": 14}


def new(**over):
    base = {"pack_sha256": "a" * 64, "micro_ops_s": 1_050, "boot_done_s": 12.0,
            "rss_peak_mib": 2340.0, "steal_pct": 0.2, "steal_hidden": False,
            "plugins_enabled": 14, "mods": 36, "root_cause": None}
    base.update(over)
    return base


class VerdictTest(unittest.TestCase):
    def test_all_gates_green_is_the_only_way_to_migrate(self):
        out = M.verdict(LIVE, new())
        self.assertEqual(out["verdict"], "MIGREAZĂ")
        self.assertTrue(all(g["ok"] for g in out["gates"]))
        self.assertEqual(len(out["gates"]), 6)

    def test_slower_cpu_blocks_the_move(self):
        out = M.verdict(LIVE, new(micro_ops_s=800))
        self.assertNotEqual(out["verdict"], "MIGREAZĂ")
        self.assertIn("CPU", " ".join(out["notes"]))

    def test_missing_reference_is_not_a_pass(self):
        out = M.verdict({}, new())
        self.assertIn("identitate", " ".join(out["notes"]))
        self.assertIn("CPU", " ".join(out["notes"]))
        self.assertIn("pornire", " ".join(out["notes"]))

    def test_hidden_steal_counter_is_treated_as_unknown_not_zero(self):
        out = M.verdict(LIVE, new(steal_pct=0.0, steal_hidden=True))
        self.assertIn("vecini", " ".join(out["notes"]))

    def test_incompatible_pack_blocks_move_even_when_cpu_is_fast(self):
        out = M.verdict(LIVE, new(plugins_enabled=0, boot_done_s=None, root_cause="NoSuchMethodError"))
        self.assertIn("pornire", " ".join(out["notes"]))
        self.assertIn("pack intact", " ".join(out["notes"]))

    def test_report_names_the_untouched_live_host(self):
        out = M.verdict(LIVE, new())
        self.assertIn("25599", out["limit"])
        self.assertIn("nu a fost atins", out["limit"])


class MeasurementTest(unittest.TestCase):
    def test_live_baseline_reads_only_and_never_boots(self):
        src = (ROOT / "scripts" / "cuantic_migrate.py").read_text(encoding="utf-8")
        start = src.index("def live_baseline")
        end = src.index("\n\ndef main(", start)
        body = src[start:end]
        self.assertNotIn("Popen", body)
        self.assertNotIn("killpg", body)
        self.assertNotIn("systemctl", body)

    def test_baseline_is_json_serialisable_on_a_box_without_the_server(self):
        data = M.live_baseline(None)
        self.assertIsInstance(data, dict)
        json.dumps(data)
        self.assertIn("micro_ops_s", data)

    def test_shadow_uses_a_port_nobody_else_listens_on(self):
        self.assertEqual(M.SHADOW_PORT, 25599)
        self.assertNotEqual(M.SHADOW_PORT, 25565)


if __name__ == "__main__":
    unittest.main()
