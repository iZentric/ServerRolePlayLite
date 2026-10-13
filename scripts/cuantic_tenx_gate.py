#!/usr/bin/env python3
"""A conservative claim gate for repeated *real Forge client* capacity tests.

No client is created here. This deliberately refuses empty, mismatched and
synthetic-only results; it is NOT a benchmark or a substitute for logs.
"""
import json
import math
from pathlib import Path
import re
import sys

FINGERPRINT = ("pack_sha256", "host_id", "jdk", "world_id", "settings_sha256", "workload_id", "duration_s")
FUNCTIONS = ("vehicles_ok", "survival_ok", "plugins_ok")
MIN_REPEATS = 3


def evaluate(data):
    arms = [data.get("baseline"), data.get("candidate")]
    if any(not isinstance(arm, list) or len(arm) < MIN_REPEATS for arm in arms):
        return {"verdict": "NEMASURAT", "reason": "minimum three real repeated trials per arm required"}
    reference = arms[0][0]
    try:
        if any(not reference.get(k) for k in FINGERPRINT):
            raise ValueError("missing comparison fingerprint")
        jars = []
        run_ids = set()
        for arm in arms:
            counts = set()
            jar_ids = set()
            for row in arm:
                if not row.get("run_id") or row["run_id"] in run_ids:
                    raise ValueError("each repeat needs a distinct run_id")
                run_ids.add(row["run_id"])
                if any(not re.fullmatch(r"[a-f0-9]{64}", str(row.get(k, "")))
                       for k in ("server_log_sha256", "client_log_sha256")):
                    raise ValueError("retain both server and Forge client log SHA-256 evidence per repeat")
                if not all(row.get(k) == reference[k] for k in FINGERPRINT):
                    raise ValueError("different host/pack/world/JDK/settings/workload/duration")
                if not all(row.get(k) is True for k in FUNCTIONS):
                    raise ValueError("modded vehicle/survival/plugin functionality not verified")
                count = row.get("players")
                if not isinstance(count, int) or isinstance(count, bool) or count < 1 or row.get("confirmed_forge_clients") != count:
                    raise ValueError("clients not confirmed in game by Forge handshake and /list")
                counts.add(count)
                jar_ids.add(row.get("jar_sha256"))
                tps, p95 = row.get("tps"), row.get("p95_ms")
                if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (tps, p95)) or tps < 19.5 or p95 <= 0 or p95 > 50:
                    raise ValueError("TPS/p95 acceptance failed or missing")
            if len(counts) != 1 or len(jar_ids) != 1 or not next(iter(jar_ids)):
                raise ValueError("each arm must repeat the same player count and exact JAR SHA")
            jars.append(next(iter(jar_ids)))
        if jars[0] == jars[1]:
            raise ValueError("candidate JAR is byte-identical to baseline")
        bcount, ccount = arms[0][0]["players"], arms[1][0]["players"]
        ratio = ccount / bcount
        return {"verdict": "10X_PRELIMINAR" if ratio >= 10 else "SUB_TINTA",
                "capacity_ratio": ratio, "baseline_players": bcount, "candidate_players": ccount,
                "reason": "same declared workload per player, host, pack and functionality; CPU/RAM ratios NOT inferred from different player counts",
                "limits": "JSON and hashes are declarations, not proof of real clients; independently inspect retained logs and repeat on competing engines before any public 10x claim"}
    except (KeyError, TypeError, ValueError) as exc:
        return {"verdict": "NEMASURAT", "reason": str(exc)}


if __name__ == "__main__":
    result = evaluate(json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) == 2 else {})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["verdict"] != "NEMASURAT" else 1)
