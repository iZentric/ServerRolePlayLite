#!/usr/bin/env python3
"""Fail-closed, offline verifier for an attested FunCity real-client ABBA ramp.

This tool cannot collect measurements or prove that submitted observations are
truthful. It consumes *private, anonymized* aggregate observations; do not feed
it world files, player identities, credentials, or server logs. Its synthetic
unit tests are not a performance result. Exit 0 ONLY for a validated increase
in the tested player rung, 2 for insufficient evidence/regression.
"""

import json
import math
import re
import sys
from pathlib import Path

SHA = re.compile(r"[0-9a-f]{64}\Z")
ORDER = ("baseline", "candidate", "candidate", "baseline")


class InvalidEvidence(ValueError):
    pass


def require(test, message):
    if not test:
        raise InvalidEvidence(message)


def number(obj, key, low, high):
    value = obj.get(key)
    require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high,
            "invalid metric: " + key)
    return value


def sha(value, name):
    require(isinstance(value, str) and SHA.fullmatch(value) is not None,
            "missing/invalid fingerprint: " + name)


def verify(data):
    require(isinstance(data, dict) and data.get("schema") == 1, "unsupported schema")
    env = data.get("environment")
    require(isinstance(env, dict), "missing environment")
    require(env.get("java_major") == 11 and env.get("ram_limit_mib") == 3072
            and env.get("mod_jars") == 34 and env.get("plugin_jars") == 13,
            "not the pinned FunCity Java 11 / 3 GiB / 34+13 pack")
    require(env.get("world_kind") == "private-rp-copy"
            and env.get("clients") == "real-forge-1.16.5"
            and env.get("hardware_kind") == "isolated-host-equivalent",
            "not the real-client private RP test environment")
    for key in ("pack_sha256", "world_sha256", "scenario_sha256", "hardware_sha256"):
        sha(env.get(key), key)
    engines = data.get("engines")
    require(isinstance(engines, dict) and set(engines) == set(ORDER), "two engine arms required")
    for arm in ("baseline", "candidate"):
        sha(engines[arm], arm + " engine")
    require(engines["baseline"] != engines["candidate"], "no engine change to compare")

    levels = data.get("levels")
    require(isinstance(levels, list) and levels, "no tested player rungs")
    seen = set()
    baseline_high = candidate_high = 0
    baseline_stopped = candidate_stopped = False
    baseline_failure_at_candidate = False
    for level in levels:
        require(isinstance(level, dict), "invalid player rung")
        players = level.get("players")
        require(type(players) is int and 1 <= players <= 64 and players not in seen
                and (not seen or players > max(seen)), "rungs must be distinct and ascending")
        seen.add(players)
        trials = level.get("trials")
        require(isinstance(trials, list) and len(trials) == 4
                and tuple(t.get("arm") if isinstance(t, dict) else None for t in trials) == ORDER,
                "each rung requires chronological A/B/B/A trials")
        outcomes = {"baseline": [], "candidate": []}
        for trial in trials:
            arm = trial["arm"]
            require(trial.get("engine_sha256") == engines[arm], "trial engine hash mismatch")
            require(trial.get("logged_in_players") == players, "incomplete real-client joins")
            measured = number(trial, "measured_seconds", 1200, 86400)
            warmup = number(trial, "warmup_seconds", 300, 3600)
            require(measured >= 4 * warmup, "warm-up dominates measured window")
            for key in ("auth_ok", "voice_ok", "vehicles_ok", "rp_ok", "memory_stable",
                        "gc_stable", "clean_restart_ok", "backup_restore_ok"):
                require(type(trial.get(key)) is bool, "missing compatibility check: " + key)
            require(type(trial.get("critical_errors")) is int
                    and trial["critical_errors"] >= 0, "missing critical error count")
            tps = number(trial, "tps", 0, 20)
            p95 = number(trial, "mspt_p95", 0, 100000)
            p99 = number(trial, "mspt_p99", 0, 100000)
            require(p99 >= p95, "p99 cannot be below p95")
            rss = number(trial, "rss_peak_mib", 1, 1048576)
            cpu = number(trial, "cpu_total_percent", 0, 100)
            uplink = number(trial, "uplink_percent", 0, 100)
            # A measured failure is evidence of a failed rung, not malformed input.
            outcomes[arm].append(tps >= 19.5 and p95 <= 35 and p99 <= 45
                                 and rss <= env["ram_limit_mib"] - 128
                                 and cpu <= 75 and uplink <= 70
                                 and trial["critical_errors"] == 0
                                 and all(trial[key] for key in ("auth_ok", "voice_ok", "vehicles_ok",
                                         "rp_ok", "memory_stable", "gc_stable", "clean_restart_ok",
                                         "backup_restore_ok")))
        passing = {arm: all(values) for arm, values in outcomes.items()}
        if not baseline_stopped and passing["baseline"]:
            baseline_high = players
        else:
            baseline_stopped = True
        if not candidate_stopped and passing["candidate"]:
            candidate_high = players
            if not any(outcomes["baseline"]):
                baseline_failure_at_candidate = True
        else:
            candidate_stopped = True
    require(baseline_high > 0, "baseline never passed a real-client rung")
    require(candidate_high > baseline_high and baseline_failure_at_candidate,
            "no demonstrated higher passing rung after measured baseline failure")
    return baseline_high, candidate_high


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def main(path):
    try:
        result = verify(json.loads(Path(path).read_text(encoding="utf-8"),
                                   object_pairs_hook=unique_keys))
    except (OSError, json.JSONDecodeError, InvalidEvidence) as exc:
        print("NOT_VALIDATED: " + str(exc), file=sys.stderr)
        return 2
    print("TESTED_CAPACITY_GAIN: baseline_rung=%d candidate_rung=%d; "
          "not a production promotion or a max-players recommendation" % result)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: fc_funcity_capacity_verdict.py private-aggregate.json", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
