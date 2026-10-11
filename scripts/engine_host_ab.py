#!/usr/bin/env python3
"""A/B on the live HOST, not the live WORLD/process: private :25566 copies only.

Never replaces a running jar or opens a public port. Refuses to start if players
are online, RAM/disk are insufficient or the read-only world snapshot fails.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

from engine_ab import JAR, run


def command(live, text, pattern, seconds=35):
    log = live / "live.log"
    pos = log.stat().st_size
    with (live / "cmd.in").open("a") as f:
        f.write(text + "\n")
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        with log.open("rb") as f:
            f.seek(pos)
            chunk = f.read().decode("utf-8", errors="replace")
        lines = re.findall(pattern, chunk, flags=re.I)
        if lines:
            return lines[-1]
        time.sleep(2)
    raise RuntimeError(f"No fresh console response to {text!r}; refusing to touch world")


def check_players(live):
    count = command(live, "list", r"There are (\d+) out of maximum \d+ players online")
    if int(count) != 0:
        raise RuntimeError(f"{count} player(s) online; stage test skipped (no disruption)")


def available_mb():
    text = Path("/proc/meminfo").read_text()
    return int(re.search(r"MemAvailable:\s*(\d+) kB", text).group(1)) / 1024


def snapshot(live, base):
    props = (live / "server.properties").read_text(encoding="latin-1")
    world = re.findall(r"^level-name=(.*)$", props, re.M)
    world = world[-1] if world else "world"
    if "/" in world or ".." in world or not (live / world).is_dir():
        raise RuntimeError("Unrecognized/missing world; aborting without touching live")
    # Do not copy a concurrently-written world; request flush and keep production up.
    command(live, "save-all flush", r"Saved the game|Saved the world|Saving is already turned off", seconds=50)
    base.mkdir(parents=True, exist_ok=True)
    for directory in ("mods", "plugins", "config", "defaultconfigs", "libraries",
                      world, world + "_nether", world + "_the_end"):
        if (live / directory).is_dir():
            shutil.copytree(live / directory, base / directory)
    for name in (JAR, "spigot.yml", "bukkit.yml", "catserver.yml", "commands.yml",
                 "server.properties", "eula.txt", "ops.json", "whitelist.json"):
        if (live / name).is_file():
            shutil.copy2(live / name, base / name)
    if not (base / JAR).is_file() or not (base / "mods").is_dir():
        raise RuntimeError("Incomplete staging snapshot")
    return world


def main(candidate, report_dir):
    live = Path.home() / "cuantic-live"
    report_dir.mkdir(parents=True, exist_ok=True)
    verdict = {
        "method": "two PRIVATE copies on the actual live host; live JVM stays up; no real players",
        "disclaimer": "Synthetic workload only. Does NOT establish client handshake or universal superiority.",
    }
    try:
        if not (live / "live.log").is_file() or not (live / "cmd.in").is_file():
            raise RuntimeError("Missing live console/log; skip")
        if not Path("/proc/net/tcp").exists():
            raise RuntimeError("No process metrics; skip")
        java = Path.home() / ".local/jdk17/bin/java"
        if not java.is_file():
            raise RuntimeError("Java 17 absent; skip")
        os.environ["PATH"] = str(java.parent) + os.pathsep + os.environ.get("PATH", "")
        check_players(live)
        if available_mb() < 4000:
            raise RuntimeError(f"Not enough headroom for second JVM: {available_mb():.0f} MB")
        if shutil.disk_usage("/tmp").free < 1_300_000_000:
            raise RuntimeError("Insufficient temp disk for staging; skip")
        # Crash / action cancellation: TemporaryDirectory only contains copies and is auto-cleaned.
        with tempfile.TemporaryDirectory(prefix="cuantic-engine-ab-", dir="/tmp") as temp:
            root = Path(temp)
            world = snapshot(live, root / "snapshot")
            verdict["world_copied"] = world
            verdict["live_jar_sha256"] = subprocess.check_output(
                ["sha256sum", str(live / JAR)], text=True).split()[0]
            for label, jar in (("baseline-2023", None), ("candidate-2024", candidate)):
                check_players(live)
                if available_mb() < 4000:
                    raise RuntimeError("Live host RAM headroom fell below 4G; abort")
                dest = root / label
                shutil.copytree(root / "snapshot", dest)
                if jar:
                    shutil.copyfile(jar, dest / JAR)
                props = dest / "server.properties"
                text = props.read_text(encoding="latin-1")
                text += "\nserver-ip=127.0.0.1\nserver-port=25566\n"
                props.write_text(text, encoding="latin-1")
                voice = dest / "config/voicechat/voicechat-server.properties"
                if voice.exists():
                    vc = voice.read_text()
                    voice.write_text(re.sub(r"(?m)^port=\d+", "port=24455", vc))
                verdict[label] = run(label, dest, report_dir)
                print(json.dumps(verdict[label], indent=2), flush=True)
                if not verdict[label]["valid"]:
                    raise RuntimeError(f"{label} failed isolated boot/spark; no other test run")
                check_players(live)
            verdict["status"] = "both stages valid; no live jar replaced"
    except Exception as exc:
        verdict["status"] = "ABORTED / NO LIVE JAR CHANGED"
        verdict["reason"] = str(exc)[:300]
    (report_dir / "result.json").write_text(json.dumps(verdict, indent=2, ensure_ascii=False) + "\n")
    return 0 if verdict.get("status", "").startswith("both stages valid") else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: engine_host_ab.py <compiled-candidate.jar> <report-dir>")
    sys.exit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))
