#!/usr/bin/env python3
"""Collect one 60-second spark sampling profile WHILE a player is online.

Only sends spark profiler commands to the existing server console. Does not
restart Java, change world, switch JAR, spawn entities or upload private data.
"""
import json
from pathlib import Path
import re
import sys
import time
from minecraft_status import status

LIVE = Path.home() / "cuantic-live"


def send(cmd):
    with (LIVE / "cmd.in").open("a") as f:
        f.write(cmd + "\n")


def tail_since(pos):
    with (LIVE / "live.log").open("rb") as f:
        f.seek(pos)
        return f.read().decode("utf-8", "replace")


def main(out):
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {"method": "60s CPU sampling on unchanged live CatServer while a human is online",
              "limits": "diagnostic profile, NOT an A/B or faster JAR"}
    started = False
    try:
        player_count = status()["players"]["online"]
        if player_count < 1:
            raise RuntimeError("No player online; profile not started")
        result["players_at_start"] = player_count
        cursor = (LIVE / "live.log").stat().st_size
        send("spark profiler start --timeout 60")
        started = True
        time.sleep(72)
        text = tail_since(cursor)
        # spark 1.9.1 may finish automatically or require explicit stop.
        if not re.search(r"https?://(?:spark\.lucko\.me|spark\.lucko\.me/)", text):
            send("spark profiler stop")
            time.sleep(12)
            text = tail_since(cursor)
        result["players_at_end"] = status()["players"]["online"]
        result["spark_urls"] = list(dict.fromkeys(re.findall(r"https?://spark\.lucko\.me/[A-Za-z0-9/?=_-]+", text)))[:4]
        # No raw log or player names published; include diagnostic spark lines only.
        result["spark_messages"] = [line[-220:] for line in text.splitlines()
                                    if ("spark" in line.lower() or "profil" in line.lower()) and
                                    not re.search(r"password|token|secret", line, re.I)][-16:]
        result["status"] = ("PROFILE READY" if result["spark_urls"] else "PROFILE NOT EXPORTED; inspect spark messages")
    except Exception as exc:
        result["status"] = "INCOMPLETE (NO JAR/WORLD CHANGED)"
        result["reason"] = str(exc)[:200]
        if started:
            send("spark profiler stop")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0 if result["status"] == "PROFILE READY" else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: engine_player_profile.py <report.json>")
    sys.exit(main(Path(sys.argv[1])))
