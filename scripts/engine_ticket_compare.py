#!/usr/bin/env python3
"""ABBA isolated 64-forced-chunk CatServer comparison. Never touches live server."""
import hashlib
import json
from pathlib import Path
import statistics
import sys
from engine_ab import JAR, prepare, run


def main(pack, candidate, out):
    out.mkdir(parents=True, exist_ok=True)
    result = {"method": "ABBA same machine: original CatServer, optimized SortedArraySet, optimized, original; isolated 64 forced chunks + 40 zombies; no players",
              "limits": "2 runs/arm on fresh worlds, no modded player login, driving, production world, or real traffic; experimental JAR NEVER promoted automatically"}
    for label, jar in (("live-A1", None), ("patched-B1", candidate),
                       ("patched-B2", candidate), ("live-A2", None)):
        dest = out / label
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        arm = run(label, dest, out, ticket_workload=True)
        arm["jar_sha256"] = hashlib.sha256((dest / JAR).read_bytes()).hexdigest()
        result[label] = arm
        print(json.dumps(arm, indent=2), flush=True)
        if not arm["valid"]:
            result["verdict"] = "INCOMPLETE: boot/workload/metric not verified; no promotion"
            break
    if "verdict" not in result:
        def med(arms, fn):
            return round(statistics.median(fn(result[arm]) for arm in arms), 3)
        summary = {}
        for key, arms in (("live", ("live-A1", "live-A2")), ("patched", ("patched-B1", "patched-B2"))):
            summary[key] = {
                "p95_ms_median_of_2": med(arms, lambda x: x["spark_tick_min_median_p95_max_ms_1m"][2]),
                "cpu_seconds_median_of_2": med(arms, lambda x: x["cpu_seconds_during_command_and_warmup"]),
                "rss_mb_median_of_2": med(arms, lambda x: x["rss_median_mb"]),
            }
        result["summary"] = summary
        result["verdict"] = ("better p95 AND CPU for this synthetic workload only; still not ready for live" if
            summary["patched"]["p95_ms_median_of_2"] < summary["live"]["p95_ms_median_of_2"] and
            summary["patched"]["cpu_seconds_median_of_2"] < summary["live"]["cpu_seconds_median_of_2"] else
            "NOT PROVEN BETTER than live JAR; no promotion")
    (out / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return int(not all(result.get(x, {}).get("valid") for x in ("live-A1", "patched-B1", "patched-B2", "live-A2")))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: engine_ticket_compare.py <server-pack.zip> <patched.jar> <report-dir>")
    sys.exit(main(*(Path(x).resolve() for x in sys.argv[1:])))
