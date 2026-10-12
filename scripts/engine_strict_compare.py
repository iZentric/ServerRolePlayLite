#!/usr/bin/env python3
"""Fail-closed synthetic screen for an actual source-patched engine JAR.

Six fresh worlds, one GitHub runner, same pack/seed/JVM and workload. It cannot
certify real client FPS or that a JAR beats every engine on every possible load.
No release, deployment, or live machine is touched by this script.
"""
import hashlib
import json
from pathlib import Path
import sys
from engine_ab import JAR, prepare, run

EXPECTED_BRANDED = "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
EXPECTED_OFFICIAL = "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
EXPECTED_CANDIDATE = "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
EXPECTED_PACK = "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
# Threshold 0: "the same" or worse in any metric fails, not an average score.
# Two samples cannot prove statistical separation or real-world performance.
METRICS = {
    "rss_steady_median_mb": lambda x: x["rss_steady_median_mb"],
    "cpu_steady_s": lambda x: x["cpu_seconds_steady_after_55s"],
    "p95_ms": lambda x: x["spark_tick_min_median_p95_max_ms_1m"][2],
    "boot_internal_done_s": lambda x: x["boot_done_s"],
    "boot_wall_s": lambda x: x["boot_wall_seconds"],
}
ORDER = (("branded-A1", None), ("official-B1", "official"),
         ("patched-C1", "candidate"), ("patched-C2", "candidate"),
         ("official-B2", "official"), ("branded-A2", None))
ARMS = {"branded": ("branded-A1", "branded-A2"),
        "official": ("official-B1", "official-B2"),
        "patched": ("patched-C1", "patched-C2")}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_screen(result):
    """Candidate's *worst* run must beat *both* baselines' *best* run.

    Returns false for missing/invalid data, matching SHA or exact ties, and
    makes no claim that a passing synthetic screen qualifies for production.
    """
    all_labels = [label for labels in ARMS.values() for label in labels]
    if not all(result.get(label, {}).get("valid") for label in all_labels):
        return {"synthetic_screen_pass": False, "reason": "INCOMPLETE: not all six trials validated"}
    if (result.get("pack_sha256") != EXPECTED_PACK or
        result["branded-A1"].get("jar_sha256") != EXPECTED_BRANDED or
        result["branded-A2"].get("jar_sha256") != EXPECTED_BRANDED or
        any(result[label].get("jar_sha256") != EXPECTED_OFFICIAL for label in ARMS["official"]) or
        result.get("candidate_sha256") != EXPECTED_CANDIDATE or
        any(result[label].get("jar_sha256") != result["candidate_sha256"] for label in ARMS["patched"])):
        return {"synthetic_screen_pass": False, "reason": "INCOMPLETE: SHA provenance mismatch"}
    checks = {}
    for metric, get in METRICS.items():
        try:
            samples = {name: [float(get(result[label])) for label in labels]
                       for name, labels in ARMS.items()}
            checks[metric] = {
                "samples": samples,
                "candidate_worst": max(samples["patched"]),
                "best_baseline": min(samples["branded"] + samples["official"]),
                "pass": max(samples["patched"]) < min(samples["branded"] + samples["official"]),
            }
        except (KeyError, ValueError, TypeError, IndexError):
            return {"synthetic_screen_pass": False, "reason": "INCOMPLETE: metric missing: " + metric}
    passed = all(item["pass"] for item in checks.values())
    return {
        "synthetic_screen_pass": passed,
        "checks": checks,
        "reason": ("SYNTHETIC SCREEN ONLY; further repeated workloads and modded player + vehicle validation REQUIRED; NEVER auto-release" if passed else
                   "REJECT: at least one metric tied or regressed against at least one baseline; do not promote"),
    }


def main(pack, official, candidate, output):
    output.mkdir(parents=True, exist_ok=True)
    result = {
        "method": "A/B/C/C/B/A; same runner Java17, same release pack, -Xms1G -Xmx3G, seed and 64 forced chunks + 40 zombies; 55s warmup/75s steady, fresh world per run",
        "limits": "two samples per arm; zero players/vehicles; synthetic *screen* not proof of universal superiority, stability or FPS; production release forbidden without real modded player + vehicles",
        "pack_sha256": digest(pack), "official_sha256": digest(official),
        "candidate_sha256": digest(candidate),
    }
    try:
        if result["pack_sha256"] != EXPECTED_PACK or result["official_sha256"] != EXPECTED_OFFICIAL or result["candidate_sha256"] != EXPECTED_CANDIDATE:
            result["screen"] = {"synthetic_screen_pass": False, "reason": "INCOMPLETE: wrong pack/official/candidate SHA"}
            return 1
        for label, jar in ORDER:
            dest = output / label
            dest.mkdir(parents=True, exist_ok=True)
            prepare(pack, dest, official if jar == "official" else candidate if jar == "candidate" else None)
            arm = run(label, dest, output, ticket_workload=True)
            arm["jar_sha256"] = digest(dest / JAR)
            result[label] = arm
            print(json.dumps(arm, indent=2), flush=True)
            if not arm["valid"]:
                break
        result["screen"] = strict_screen(result)
        return int(not all(result.get(label, {}).get("valid") for label, _ in ORDER))
    finally:
        (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: engine_strict_compare.py <pack.zip> <official.jar> <candidate.jar> <output-dir>")
    sys.exit(main(*(Path(x).resolve() for x in sys.argv[1:])))
