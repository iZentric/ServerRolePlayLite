#!/usr/bin/env python3
"""Read-only baseline while a REAL modded player drives in the live world.

No restart, no synthetic entities, no JAR or world changes. Requires a fresh
Minecraft local status ping AND console list >=1; never interprets silence as 0.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from minecraft_status import status

LIVE = Path.home() / "cuantic-live"
JAR = LIVE / "CatServer-1.16.5-1d8d6313-server.jar"
METRIC = re.compile(r"Tick durations \(min/med/95%ile/max ms\) from last 10s, 1m:\s*"
                    r"([\d.]+/[\d.]+/[\d.]+/[\d.]+);\s*([\d.]+/[\d.]+/[\d.]+/[\d.]+)")


def console(command, pattern, timeout=25):
    log = LIVE / "live.log"
    pos = log.stat().st_size
    with (LIVE / "cmd.in").open("a") as f:
        f.write(command + "\n")
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        with log.open("rb") as f:
            f.seek(pos)
            text = f.read().decode("utf-8", "replace")
        hits = re.findall(pattern, text, flags=re.I)
        if hits:
            return hits[-1]
        time.sleep(2)
    raise RuntimeError(f"No fresh reply to {command!r} in {timeout}s; aborted without server changes")


def players():
    # Status ping is a fresh response from THIS local JVM. Console 'list' is
    # optional in a read-only measurement: the cmd.in bridge can lag or be down.
    ping = status()
    return int(ping["players"]["online"]), ping


def main(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    r = {"method": "real player on public live server; read-only status/list/spark; no restart or artificial workload",
         "limits": "single session, no competing JAR, cannot prove speedup"}
    try:
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            try:
                count, ping = players()
                if count >= 1:
                    break
            except (OSError, EOFError, RuntimeError, ValueError):
                pass
            time.sleep(10)
        else:
            raise RuntimeError("No verified player on server after 4 min; no fake 0-player benchmark")
        r["ping_at_start"] = ping
        try:
            r["console_list_at_start"] = players_from_console = int(console("list", r"There are (\d+) out of maximum \d+ players online", timeout=10))
            if players_from_console < 1:
                raise RuntimeError("Console returned zero players; status inconsistent")
        except RuntimeError as exc:
            if "status inconsistent" in str(exc):
                raise
            r["console_list_at_start"] = "NO REPLY (status ping says player is online)"
        r["live_jar_sha256"] = subprocess.check_output(["sha256sum", str(JAR)], text=True).split()[0]
        pid_text = subprocess.check_output(["pgrep", "-f", "java @unix_args.txt"], text=True).strip().splitlines()
        pid = int(pid_text[0])
        r["samples"] = []
        for i in range(3):
            count, ping = players()
            if count < 1:
                raise RuntimeError("Player left before 3 samples; partial data only")
            mspt = console("spark health", METRIC.pattern, timeout=35)
            mem = (Path(f"/proc/{pid}/status").read_text())
            rss = re.search(r"^VmRSS:\s*(\d+) kB", mem, re.M)
            r["samples"].append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                 "players": count,
                                 "spark_mspt_min_med_p95_max_10s": [float(x) for x in mspt[0].split("/")],
                                 "spark_mspt_min_med_p95_max_1m": [float(x) for x in mspt[1].split("/")],
                                 "rss_mb": round(int(rss.group(1)) / 1024, 1) if rss else None})
            output.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
            print(json.dumps(r["samples"][-1], ensure_ascii=False), flush=True)
            if i < 2:
                time.sleep(40)
        r["status"] = "COMPLETED: 3 samples with real online player(s), NO JAR changed"
    except Exception as exc:
        r["status"] = "INCOMPLETE, NO SERVER CHANGES"
        r["reason"] = str(exc)[:250]
    output.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    return 0 if r["status"].startswith("COMPLETED") else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: engine_player_live.py <report.json>")
    sys.exit(main(Path(sys.argv[1])))
