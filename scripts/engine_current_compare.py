#!/usr/bin/env python3
"""ABBA same-source JAR A/B on one runner (never deploys)."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
from engine_ab import JAR, prepare, run


def main(pack, candidate, out):
    out.mkdir(parents=True, exist_ok=True)
    result = {"method": "ABBA: live-2023, patched-2023, patched-2023, live-2023; same runner, same pack/seed and filled-hopper commands (256/256 validated), no players",
              "limits": "two independent samples per arm, synthetic forced chunk; no modded login, real traffic, vehicles or weak laptop; NEVER deploy automatically"}
    for label, jar in (("live-A1", None), ("patched-B1", candidate),
                       ("patched-B2", candidate), ("live-A2", None)):
        dest = out / label
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        arm = run(label, dest, out, hopper_workload=True)
        arm["jar_sha256"] = hashlib.sha256((dest / JAR).read_bytes()).hexdigest()
        result[label] = arm
        print(json.dumps(arm, indent=2), flush=True)
        if not arm["valid"]:
            result["verdict"] = "INCOMPLETE: failed startup, workload or metric; no promotion"
            break
    if "verdict" not in result:
        a = [result[x] for x in ("live-A1", "live-A2")]
        b = [result[x] for x in ("patched-B1", "patched-B2")]
        def med(items, key):
            return round(statistics.median(x[key] for x in items), 2)
        summary = {}
        for name, items in (("live", a), ("patched", b)):
            summary[name] = {
                "p95_ms_median_of_2": med([{"v": x["spark_tick_min_median_p95_max_ms_1m"][2]} for x in items], "v"),
                "cpu_seconds_workload_median_of_2": med(items, "cpu_seconds_during_command_and_warmup"),
                "rss_median_mb_of_2": med(items, "rss_median_mb"),
            }
        result["summary"] = summary
        winner = (summary["patched"]["p95_ms_median_of_2"] < summary["live"]["p95_ms_median_of_2"] and
                  summary["patched"]["cpu_seconds_workload_median_of_2"] < summary["live"]["cpu_seconds_workload_median_of_2"])
        result["verdict"] = ("better p95 AND CPU only for THIS synthetic workload, still not ready for live" if winner
                             else "NOT PROVEN BETTER than current CatServer: no live promotion")
    (out / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return int(not all(result.get(x, {}).get("valid") for x in ("live-A1", "patched-B1", "patched-B2", "live-A2")))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: engine_current_compare.py <current-pack.zip> <patched-current.jar> <report-dir>")
    sys.exit(main(*(Path(p).resolve() for p in sys.argv[1:])))
