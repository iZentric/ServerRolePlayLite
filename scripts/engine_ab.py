#!/usr/bin/env python3
"""Isolated A/B of the CURRENT and CANDIDATE CatServer using the same CUANTIC pack.

This is a synthetic, no-player benchmark, NOT evidence of real client compatibility or
performance with players. No existing world, live host or release is touched.
"""
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time
import zipfile

JAR = "CatServer-1.16.5-1d8d6313-server.jar"
BOOT_LIMIT = 240
WARMUP = 50


def rss_mb(pid):
    try:
        text = Path(f"/proc/{pid}/status").read_text()
        return int(re.search(r"^VmRSS:\s*(\d+)\s*kB", text, re.M).group(1)) / 1024
    except (OSError, AttributeError):
        return None


def cpu_time_seconds(pid):
    try:
        # Linux /proc stat: fields 14/15 utime/stime, after the executable's ')'.
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(") ", 1)[1].split()
        return (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")
    except (OSError, IndexError, ValueError):
        return None


def metrics_from_log(text):
    # spark health: "... last 10s, 1m: min/med/p95/max; min/med/p95/max"
    clean = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)
    hits = re.findall(r"Tick durations \(min/med/95%ile/max ms\) from last 10s, 1m:\s*"
                      r"([\d.]+/[\d.]+/[\d.]+/[\d.]+);\s*"
                      r"([\d.]+/[\d.]+/[\d.]+/[\d.]+)", clean)
    return [float(x) for x in hits[-1][1].split("/")] if hits else None


def prepare(pack, dest, candidate=None):
    with zipfile.ZipFile(pack) as z:
        z.extractall(dest)
    if candidate:
        shutil.copyfile(candidate, dest / JAR)
    props = dest / "server.properties"
    text = props.read_text(encoding="latin-1")
    text += "\nlevel-seed=20261011\nserver-ip=127.0.0.1\nserver-port=25565\n"
    props.write_text(text, encoding="latin-1")
    (dest / "eula.txt").write_text("eula=true\n")


def run(label, dest, report_dir, hopper_workload=False, ticket_workload=False):
    logfile = report_dir / f"{label}.log"
    rss = []
    cpu_workload = None
    done_at = None
    proc = None
    commands = None
    stopped = False
    started = time.monotonic()
    try:
        with logfile.open("w") as out:
            proc = subprocess.Popen(["java", "-Xms1G", "-Xmx3G", "-jar", JAR, "nogui"],
                                    cwd=dest, stdin=subprocess.PIPE, stdout=out,
                                    stderr=subprocess.STDOUT, text=True)
            while time.monotonic() - started < BOOT_LIMIT:
                if proc.poll() is not None:
                    break
                text = logfile.read_text(errors="replace")
                if "Done (" in text:
                    done_at = time.monotonic()
                    break
                time.sleep(2)
            if done_at is not None:
                cpu_start = cpu_time_seconds(proc.pid)
                # Ensure an identical, ticking chunk without human accounts.
                block = "minecraft:hopper[facing=east]" if hopper_workload else "minecraft:hopper"
                commands = (["gamerule doMobSpawning false", "forceload add -64 -64 63 63"]
                            if ticket_workload else
                            ["gamerule doMobSpawning false", "forceload add 0 0", f"fill 0 75 0 15 75 15 {block}"])
                if hopper_workload:
                    # Every hopper receives items, not just an empty container: this
                    # exercises the engine's actual InventoryMoveItemEvent hot path.
                    commands += [f'data merge block {x} 75 {z} {{Items:[{{Slot:0b,id:"minecraft:stone",Count:64b}}]}}'
                                 for x in range(16) for z in range(16)]
                commands += ["summon minecraft:zombie 8 76 8"] * 40
                for cmd in commands:
                    proc.stdin.write(cmd + "\n")
                proc.stdin.flush()
                until = time.monotonic() + (85 if hopper_workload else 55 if ticket_workload else WARMUP)
                while time.monotonic() < until and proc.poll() is None:
                    sample = rss_mb(proc.pid)
                    if sample is not None:
                        rss.append(sample)
                    time.sleep(2)
                if ticket_workload and proc.poll() is None:
                    # Isolate the steady ticket-expiry scan: world generation and
                    # force-load startup dwarf the cost of the method being patched.
                    cpu_start = cpu_time_seconds(proc.pid)
                    until = time.monotonic() + 75
                    while time.monotonic() < until and proc.poll() is None:
                        sample = rss_mb(proc.pid)
                        if sample is not None:
                            rss.append(sample)
                        time.sleep(2)
                cpu_end = cpu_time_seconds(proc.pid)
                if cpu_start is not None and cpu_end is not None:
                    cpu_workload = round(max(0, cpu_end - cpu_start), 2)
                if proc.poll() is None:
                    proc.stdin.write("spark health\nlist\n")
                    proc.stdin.flush()
                    time.sleep(15)
                    proc.stdin.write("stop\n")
                    proc.stdin.flush()
                    try:
                        proc.wait(timeout=40)
                        stopped = True
                    except subprocess.TimeoutExpired:
                        pass
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    text = logfile.read_text(errors="replace")
    plugins = re.findall(r"\bEnabling ([A-Za-z0-9_.-]+) v", text)
    critical = re.findall(r"Mixin apply failed|Could not (?:load|enable) plugin|"
                          r"Error occurred while enabling|Exception in server tick loop|OutOfMemoryError", text, re.I)
    boot = re.findall(r"Done \(([\d.]+)s\)", text)
    mspt = metrics_from_log(text)
    feedback = [line[-170:] for line in text.splitlines() if re.search(
        r"forceload|force.load|filled [0-9]+ blocks|modified block data|summoned new zombie|unable to|unknown command|error executing", line, re.I)]
    merged = len(re.findall(r"Modified block data of", text, re.I))
    filled = bool(re.search(r"Successfully filled 256 blocks", text, re.I))
    ticket_confirmed = bool(re.search(r"(?:marked|force.loaded|force loaded).*64 chunks", text, re.I))
    workload_ok = ticket_confirmed if ticket_workload else filled and (not hopper_workload or merged == 256)
    return {
        "label": label,
        "boot_done_s": float(boot[-1]) if boot else None,
        "plugins_enabled": len(plugins),
        "mods_on_disk": len(list((dest / "mods").glob("*.jar"))),
        "rss_median_mb": round(statistics.median(rss), 1) if rss else None,
        "rss_peak_mb": round(max(rss), 1) if rss else None,
        "cpu_seconds_during_command_and_warmup": cpu_workload if not ticket_workload else None,
        "cpu_seconds_steady_after_55s": cpu_workload if ticket_workload else None,
        "spark_tick_min_median_p95_max_ms_1m": mspt,
        "critical_errors": critical[:10],
        "exit_code": proc.returncode if proc else None,
        "clean_stop": stopped,
        "synthetic_workload_requested": ("64 forced chunks + 40 zombies, no players" if ticket_workload else
                                         "one forced chunk + 256 filled hoppers + 40 zombies, no players" if hopper_workload else
                                         "one forced chunk + 256 empty hoppers + 40 zombies, no players"),
        "ticket_64_confirmed": ticket_confirmed if ticket_workload else None,
        "hopper_data_merge_responses": merged if hopper_workload else None,
        "hopper_fill_256_confirmed": filled if hopper_workload else None,
        "command_feedback_last": feedback[-8:],
        "valid": bool(boot and len(plugins) >= 14 and not critical and stopped and mspt and workload_ok),
    }


def main(pack, candidate, output):
    output.mkdir(parents=True, exist_ok=True)
    result = {"method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
              "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment"}
    for label, jar in (("baseline-2023", None), ("candidate-2024", candidate)):
        dest = output / label
        dest.mkdir(parents=True, exist_ok=True)
        prepare(pack, dest, jar)
        result[label] = run(label, dest, output)
        print(json.dumps(result[label], indent=2), flush=True)
        # Do not run further experiments on a host with failed startup.
        if not result[label]["valid"]:
            break
    (output / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return int(not all(result.get(x, {}).get("valid") for x in ("baseline-2023", "candidate-2024")))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: engine_ab.py <server-pack.zip> <candidate.jar> <out-dir>")
    sys.exit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()))
