"""Garda parserelor de consola din FC-BENCH (TPS Spigot, `forge tps` pentru MSPT) si a legaturii
cu parserul GC comun — formatul e cel real din jurnalele publicate pe functity-out/bench-v4."""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fc_bench  # noqa: E402

SPIGOT = [
    "[06:03:13] [Server thread/INFO]: Unknown command. Type \"/help\" for help.",
    "[06:03:13] [Server thread/INFO]: TPS from last 1m, 5m, 15m: *20.0, *20.0, *20.0",
]
FORGE = [
    "[06:03:13] [Server thread/INFO]: Dim minecraft:overworld (minecraft:overworld): Mean tick time: 0.713 ms. Mean TPS: 20.000",
    "[06:03:13] [Server thread/INFO]: Dim minecraft:the_nether (minecraft:the_nether): Mean tick time: 0.021 ms. Mean TPS: 20.000",
    "[06:03:13] [Server thread/INFO]: Dim minecraft:the_end (minecraft:the_end): Mean tick time: 0.019 ms. Mean TPS: 20.000",
    "[06:03:13] [Server thread/INFO]: Overall: Mean tick time: 1.072 ms. Mean TPS: 20.000",
]


class ConsoleParseTest(unittest.TestCase):
    def test_spigot_tps_line(self):
        tps, mspt, raw = fc_bench.parse_tps_mspt(SPIGOT)
        self.assertEqual(tps, [20.0])
        self.assertEqual(mspt, [])

    def test_forge_tps_gives_overall_mspt_only(self):
        tps, mspt, raw = fc_bench.parse_tps_mspt(FORGE)
        self.assertEqual(mspt, [1.072])        # nu triplam cu liniile per dimensiune
        self.assertIn(20.0, tps)
        self.assertTrue(any("Overall" in r for r in raw))

    def test_paper_mspt_line_still_parses(self):
        tps, mspt, raw = fc_bench.parse_tps_mspt(["[INFO]: Server tick times (avg/min/max) from last 5s, 10s, 1m: mspt 2.1 ms"])
        self.assertEqual(mspt, [2.1])

    def test_gc_parser_wired(self):
        self.assertIsNotNone(fc_bench._gc, "fc_bench trebuie sa foloseasca parserul GC comun (fc_gc_reprocess)")
        p = fc_bench._gc.parse_gc_lines(["[1.0s][info][gc] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 51M->12M(1536M) 9.876ms"])
        self.assertEqual(p[0]["ms"], 9.876)


if __name__ == "__main__":
    unittest.main()
