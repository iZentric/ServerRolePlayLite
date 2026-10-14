"""Garda parserului FC-GC: formatul real `-Xlog:gc*:file=...:time,uptime,level,tags` (JDK 11, G1).
Ce nu e pauza (gc,start / gc,phases / Concurrent Cycle) nu se numara; fara date => NEMASURAT, nu 0."""
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fc_gc_reprocess as gc  # noqa: E402

SAMPLE = """\
[2026-10-14T06:02:20.456+0000][0.012s][info][gc,heap] Heap region size: 1M
[2026-10-14T06:02:20.460+0000][0.016s][info][gc     ] Using G1
[2026-10-14T06:02:20.460+0000][0.016s][info][gc,heap,coops] Heap address: 0x00000000a0000000, size: 1536 MB, Compressed Oops mode: 32-bit
[2026-10-14T06:02:21.000+0000][0.556s][info][gc,start     ] GC(0) Pause Young (Normal) (G1 Evacuation Pause)
[2026-10-14T06:02:21.000+0000][0.556s][info][gc,task      ] GC(0) Using 4 workers of 4 for evacuation
[2026-10-14T06:02:21.010+0000][0.566s][info][gc,phases    ] GC(0)   Evacuate Collection Set: 8.9ms
[2026-10-14T06:02:21.010+0000][0.566s][info][gc,heap      ] GC(0) Eden regions: 51->0(44)
[2026-10-14T06:02:21.010+0000][0.566s][info][gc,metaspace ] GC(0) Metaspace: 12345K->12345K(1234567K)
[2026-10-14T06:02:21.010+0000][0.566s][info][gc           ] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 51M->12M(1536M) 9.876ms
[2026-10-14T06:02:21.010+0000][0.566s][info][gc,cpu       ] GC(0) User=0.03s Sys=0.00s Real=0.01s
[2026-10-14T06:02:30.000+0000][9.500s][info][gc           ] GC(1) Pause Young (Concurrent Start) (Metadata GC Threshold) 300M->120M(1536M) 31.250ms
[2026-10-14T06:02:30.100+0000][9.600s][info][gc           ] GC(2) Concurrent Cycle
[2026-10-14T06:02:30.200+0000][9.700s][info][gc           ] GC(2) Pause Remark 130M->130M(1536M) 4.321ms
[2026-10-14T06:02:30.300+0000][9.800s][info][gc           ] GC(2) Pause Cleanup 130M->129M(1536M) 0.123ms
[2026-10-14T06:02:30.400+0000][9.900s][info][gc           ] GC(2) Concurrent Cycle 45.678ms
[2026-10-14T06:03:40.000+0000][80.000s][info][gc           ] GC(3) Pause Young (Normal) (G1 Evacuation Pause) 400M->200M(1536M) 12.000ms
[2026-10-14T06:04:40.000+0000][140.000s][info][gc           ] GC(4) Pause Full (System.gc()) 500M->200M(1536M) 456.789ms
[2026-10-14T06:05:40.000+0000][200.000s][info][gc,heap,exit ] Heap
"""


class ParserTest(unittest.TestCase):
    def test_counts_only_stw_pauses(self):
        p = gc.parse_gc_lines(SAMPLE.splitlines())
        self.assertEqual([x["kind"] for x in p], ["Young", "Young", "Remark", "Cleanup", "Young", "Full"])
        self.assertEqual(p[0]["ms"], 9.876)
        self.assertEqual(p[0]["uptime_s"], 0.566)
        self.assertEqual(p[0]["heap_before_mb"], 51.0)
        self.assertEqual(p[0]["heap_after_mb"], 12.0)
        self.assertEqual(p[0]["heap_cap_mb"], 1536.0)
        self.assertEqual(p[1]["detail"], "(Concurrent Start) (Metadata GC Threshold)")

    def test_no_decorators_still_parses(self):
        p = gc.parse_gc_lines(["[gc] GC(7) Pause Young (Normal) (G1 Evacuation Pause) 51M->12M(1536M) 9.5ms"])
        self.assertEqual(len(p), 1)
        self.assertIsNone(p[0]["uptime_s"])

    def test_units_kb_gb(self):
        p = gc.parse_gc_lines(["[1.0s][info][gc] GC(1) Pause Young (Normal) (G1 Evacuation Pause) 512K->1G(2G) 1.0ms"])
        self.assertEqual(p[0]["heap_before_mb"], 0.5)
        self.assertEqual(p[0]["heap_after_mb"], 1024.0)
        self.assertEqual(p[0]["heap_cap_mb"], 2048.0)

    def test_percentile_nearest_rank(self):
        self.assertEqual(gc.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95), 10)
        self.assertEqual(gc.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50), 5)
        self.assertIsNone(gc.percentile([], 95))


class SummaryTest(unittest.TestCase):
    def test_boot_idle_split(self):
        s = gc.summarize(gc.parse_gc_lines(SAMPLE.splitlines()), boot_s=10.0)
        self.assertEqual(s["stare"], "MASURAT")
        self.assertEqual(s["total"]["n"], 6)
        self.assertEqual(s["full_gc"], 1)
        self.assertEqual(s["boot"]["n"], 4)
        self.assertEqual(s["idle"]["n"], 2)
        self.assertEqual(s["idle"]["max_ms"], 456.8)
        self.assertEqual(s["total"]["max_ms"], 456.8)
        self.assertEqual(s["young_max_ms"], 31.2)
        self.assertEqual(s["heap_dupa_ultimul_young_mb"], 200.0)
        self.assertEqual(s["durata_jurnal_s"], 140.0)
        self.assertAlmostEqual(s["idle"]["pauze_pe_minut"], 2 / 130.0 * 60, places=2)

    def test_empty_is_unmeasured_not_zero(self):
        s = gc.summarize([])
        self.assertEqual(s["stare"], "NEMASURAT")
        self.assertIsNone(s["total"]["max_ms"])
        self.assertIsNone(s["young_max_ms"])

    def test_unknown_format_file(self):
        with tempfile.TemporaryDirectory() as td:
            f = pathlib.Path(td) / "gc-trial1.log"
            f.write_text("GC(0) something TotalTime: 12ms\n", encoding="utf-8")
            s = gc.summarize_file(f)
        self.assertEqual(s["stare"], "NEMASURAT")
        self.assertIn("motiv", s)


class ArtifactTreeTest(unittest.TestCase):
    def _tree(self, td):
        art = pathlib.Path(td) / "38519665645" / "fcbench-functity_b1"
        art.mkdir(parents=True)
        (art / "gc-trial1.log").write_text(SAMPLE, encoding="utf-8")
        (art / "gc-trial2.log").write_text(SAMPLE.replace("456.789ms", "40.000ms").replace("Pause Full (System.gc())", "Pause Young (Mixed) (G1 Evacuation Pause)"), encoding="utf-8")
        (art / "functity_b1.json").write_text(json.dumps({
            "arm": "functity_b1", "eticheta": "FunCity b1.2256", "java": "temurin-11",
            "probe": [{"trial": 1, "boot_timp_real_s": 10.0}, {"trial": 2, "boot_timp_real_s": 10.0}]}), encoding="utf-8")
        gol = pathlib.Path(td) / "38519665645" / "fcbench-catserver"
        gol.mkdir()
        (gol / "catserver.json").write_text(json.dumps({"arm": "catserver", "eticheta": "CatServer", "probe": []}), encoding="utf-8")
        return pathlib.Path(td)

    def test_aggregate_and_markdown(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._tree(td)
            data = gc.process_root(root)
            arms = data["runs"]["38519665645"]["arms"]
            b1 = arms["functity_b1"]
            self.assertEqual(b1["stare"], "MASURAT")
            self.assertEqual(b1["probe_masurate"], 2)
            self.assertEqual(b1["toate_pauzele"]["n"], 12)
            self.assertEqual(b1["full_gc_total"], 1)
            self.assertEqual(b1["idle_max_ms_pe_proba"], [456.8, 40.0])
            self.assertEqual(arms["catserver"]["stare"], "NEMASURAT")
            self.assertIn("motiv", arms["catserver"])
            md = gc.render_markdown(data)
            self.assertIn("FunCity b1.2256", md)
            self.assertIn("456.8", md)
            self.assertIn("| CatServer | 0 | NEMASURAT |", md)
            out = root / "out"
            self.assertEqual(gc.main(["--in", str(root), "--out", str(out)]), 0)
            self.assertTrue((out / "gc.json").is_file() and (out / "GC.md").is_file())

    def test_main_exit_2_without_measurements(self):
        with tempfile.TemporaryDirectory() as td:
            (pathlib.Path(td) / "1" / "fcbench-x").mkdir(parents=True)
            (pathlib.Path(td) / "1" / "fcbench-x" / "x.json").write_text(json.dumps({"arm": "x", "probe": []}), encoding="utf-8")
            self.assertEqual(gc.main(["--in", td, "--out", td + "/o"]), 2)


if __name__ == "__main__":
    unittest.main()
