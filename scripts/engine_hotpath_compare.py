#!/usr/bin/env python3
"""Matched filled-hopper A/B; candidate is never deployed from here."""
import hashlib
import json
from pathlib import Path
import sys
from engine_ab import JAR, prepare, run


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main(pack, upstream, candidate, output):
    output.mkdir(parents=True, exist_ok=True)
    result = {"method": "A/B/C same GitHub runner + exact pack, 256 hoppers with 64 stone items each, 40 zombies, zero players, one sample each",
              "limits": "one synthetic run per arm in order A/B/C, not a modded client handshake or performance with players/vehicles; no deployment"}
    for label, jar in (("live-CatServer-2023", None), ("upstream-CatServer-2024", upstream), ("cuantic-hotpath-2024", candidate)):
        dest = output / label
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        result[label] = run(label, dest, output, hopper_workload=True)
        result[label]["jar_sha256"] = digest(dest / JAR)
        print(json.dumps(result[label], indent=2), flush=True)
        if not result[label]["valid"]:
            result["verdict"] = "INCOMPLETE: one arm did not finish/validate 256 transfers; no comparison"
            break
    if "verdict" not in result:
        a = result["live-CatServer-2023"]["spark_tick_min_median_p95_max_ms_1m"][2]
        u = result["upstream-CatServer-2024"]["spark_tick_min_median_p95_max_ms_1m"][2]
        b = result["cuantic-hotpath-2024"]["spark_tick_min_median_p95_max_ms_1m"][2]
        result["verdict"] = ("patch had lower p95 than BOTH alternatives IN THIS ONE RUN" if b < a and b < u else
                             "no demonstrated p95 win versus BOTH alternatives in this run")
        result["p95_delta_vs_live_ms"] = round(b - a, 3)
        result["p95_delta_vs_upstream_ms"] = round(b - u, 3)
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return int(not all(result.get(x, {}).get("valid") for x in ("live-CatServer-2023", "upstream-CatServer-2024", "cuantic-hotpath-2024")))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: engine_hotpath_compare.py <release-pack.zip> <unpatched-upstream.jar> <patched.jar> <report-dir>")
    sys.exit(main(*(Path(p).resolve() for p in sys.argv[1:])))
