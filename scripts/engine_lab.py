#!/usr/bin/env python3
"""Smoke-test an isolated CUANTIC server pack with an experimental engine.

Never touches ~/cuantic-live, never opens a public tunnel. A successful result is
NOT a player-load benchmark, modded-client handshake or proof of better TPS.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


BOOT_TIMEOUT = 300
POST_BOOT_SECONDS = 15


def summarize(log: str, jar_name: str, exit_code: int, timeout: bool) -> dict:
    dones = re.findall(r"\bDone \(([0-9.]+)s\)", log)
    # Bukkit/Spigot prefix: [Server thread/INFO]: [ClaimChunk] Enabling ClaimChunk v0.0.21
    enabled = re.findall(r"\bEnabling ([A-Za-z0-9_.-]+) v", log)
    failures = [line[:250] for line in log.splitlines() if re.search(
        r"Mixin apply failed|Could not (load|enable) plugin|Error occurred while enabling|"
        r"Exception in server tick loop|Failed to start the minecraft server|OutOfMemoryError", line, re.I)]
    return {
        "jar": jar_name,
        "done_seconds": dones[-1] if dones else None,
        "enabled_plugins": len(enabled),
        "plugin_names": enabled,
        "critical_lines": failures[:30],
        "timed_out": timeout,
        "exit_code_after_stop": exit_code,
        "handshake_with_real_client": "NOT TESTED",
        "performance_under_players": "NOT TESTED",
        "passed_smoke": bool(dones and len(enabled) >= 14 and not failures and not timeout),
    }


def smoke(stage: Path, output: Path) -> bool:
    stage, output = stage.resolve(), output.resolve()
    jar = "CatServer-1.16.5-1d8d6313-server.jar"  # stable start-script filename; contents = candidate
    if not (stage / jar).is_file():
        raise FileNotFoundError(stage / jar)
    output.parent.mkdir(parents=True, exist_ok=True)
    proc = None
    timed_out = False
    boot_at = None
    started = time.monotonic()
    try:
        with output.open("w", encoding="utf-8") as out:
            proc = subprocess.Popen(
                ["java", "-Xms1G", "-Xmx3G", "-jar", jar, "nogui"],
                cwd=stage, stdin=subprocess.PIPE, stdout=out, stderr=subprocess.STDOUT,
                text=True,
            )
            while proc.poll() is None:
                now = time.monotonic()
                if now - started > BOOT_TIMEOUT:
                    timed_out = True
                    break
                out.flush()
                log = output.read_text(encoding="utf-8", errors="replace")
                if "Done (" in log and boot_at is None:
                    boot_at = now
                if boot_at is not None and now - boot_at >= POST_BOOT_SECONDS:
                    break
                time.sleep(2)
            if proc.poll() is None and not timed_out and boot_at is not None:
                try:
                    proc.stdin.write("stop\n")
                    proc.stdin.flush()
                    proc.wait(timeout=45)
                except (BrokenPipeError, subprocess.TimeoutExpired):
                    pass
    finally:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    log = output.read_text(encoding="utf-8", errors="replace")
    result = summarize(log, jar, proc.returncode if proc else -1, timed_out)
    (output.parent / "smoke-result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result["passed_smoke"]


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: engine_lab.py <isolated-pack-dir> <boot-log>")
    sys.exit(0 if smoke(Path(sys.argv[1]), Path(sys.argv[2])) else 1)
