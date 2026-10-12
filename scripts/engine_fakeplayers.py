#!/usr/bin/env python3
"""Isolated Forge 1.16.5/CatServer fake-player smoke: NOT a modded-client login.

Uses upstream Curtain only in a temporary copy of the released pack. Verifies
that fake players actually appear in fresh server `list` and status replies;
never sends commands to the live server or changes the public release.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import zipfile

from engine_ab import BOOT_LIMIT, JAR, prepare, rss_mb, cpu_time_seconds, metrics_from_log
from minecraft_status import status

PACK_SHA = "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15"
JAR_SHA = "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
BOTS = ("benchA01", "benchA02", "benchA03")
# Both variants must later use the SAME verified extra test mod. 1.16.5 release:
# https://github.com/Gu-ZT/Curtain/releases/tag/1.3.2
CURTAIN = "curtain-mc1.16.5-1.3.2.jar"
CURTAIN_SHA = "c9234d2c5ca43c337abac25a05022fe2f226c884855aa6941b6130c60777819d"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_catserver_test_mod(source, dest):
    """Disable ONLY Curtain's incompatible, non-player spawning redirect.

    Fail closed on unexpected jar/mixin JSON. This derived jar is test-only,
    neither released nor installed on the public server.
    """
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(dest, "w") as zout:
        info = zin.getinfo("curtain.mixins.json")
        config = json.loads(zin.read(info).decode("utf-8"))
        mixins = config["mixins"]
        if mixins.count("NaturalSpawnerMixin") != 1 or not all(
            name in mixins for name in ("rules.command_player.PlayerListMixin",
                                       "rules.command_player.ServerPlayerEntityMixin")):
            raise ValueError("Curtain mixin layout changed; refusing test patch")
        mixins.remove("NaturalSpawnerMixin")
        for item in zin.infolist():
            data = zin.read(item)
            if item.filename == info.filename:
                data = (json.dumps(config, indent=2) + "\n").encode("utf-8")
            # Modified JAR cannot keep original zip signatures; LGPL attribution
            # and original source/release identity stay in the benchmark report.
            if item.filename.startswith("META-INF/") and item.filename.lower().endswith((".sf", ".rsa", ".dsa")):
                continue
            zout.writestr(item, data)


def write_command(proc, text):
    if proc.poll() is not None:
        raise RuntimeError("server exited before command: " + text)
    proc.stdin.write(text + "\n")
    proc.stdin.flush()


def log_since(path, offset):
    with path.open("rb") as inp:
        inp.seek(offset)
        return inp.read().decode("utf-8", "replace")


def wait_for(path, pattern, start, seconds=40, proc=None):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        text = log_since(path, start)
        match = re.search(pattern, text, re.I)
        if match:
            return match, text
        if proc and proc.poll() is not None:
            break
        time.sleep(.25)
    raise RuntimeError("No fresh response matching " + pattern + " (last log: " + log_since(path, start)[-500:] + ")")


def main(pack, curtain, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {"method": "temporary GH runner, Java17, released 36/14 pack plus ONE isolated Curtain 1.16.5 test mod; 3 server-side fake players via /player; verify fresh list + local status, 40s ticking",
              "limits": "Fake players are not network clients: no Forge FML login, resource pack, client FPS or vehicle-driver validation. Added Curtain changes the test pack; the test-only derived jar disables one incompatible non-player NaturalSpawnerMixin. Feasibility/smoke, NOT performance A/B or production recommendation.",
              "pack_sha256": sha(pack), "curtain_sha256": sha(curtain), "curtain_release": "Gu-ZT/Curtain 1.3.2/mc1.16.5",
              "expected_names": list(BOTS), "valid": False, "production_changes": False}
    logfile = output / "server.log"
    proc = None
    try:
        if (pack.resolve() == curtain.resolve() or report["pack_sha256"] != PACK_SHA or
            curtain.name != CURTAIN or report["curtain_sha256"] != CURTAIN_SHA):
            raise ValueError("wrong release pack or Curtain filename; abort")
        server = output / "isolated-server"
        server.mkdir()
        prepare(pack, server)
        if sha(server / JAR) != JAR_SHA:
            raise ValueError("live JAR SHA mismatch")
        make_catserver_test_mod(curtain, server / "mods" / CURTAIN)
        report["test_mod_sha256"] = sha(server / "mods" / CURTAIN)
        report["test_only_disabled_mixin"] = "NaturalSpawnerMixin (CatServer target mismatch; NOT a player mixin)"
        # Avoid competing with any public/local Minecraft service.
        props = server / "server.properties"
        with props.open("a", encoding="latin-1") as file:
            file.write("\nserver-ip=127.0.0.1\nserver-port=25565\nonline-mode=false\n")
        with logfile.open("w") as out:
            start = time.monotonic()
            proc = subprocess.Popen(["java", "-Xms1G", "-Xmx3G", "-jar", JAR, "nogui"],
                                    cwd=server, stdin=subprocess.PIPE, stdout=out,
                                    stderr=subprocess.STDOUT, text=True)
            match, boot_log = wait_for(logfile, r"Done \(([\d.]+)s\)", 0, BOOT_LIMIT, proc)
            report["boot_done_s"] = float(match.group(1))
            report["boot_wall_s"] = round(time.monotonic() - start, 2)
            report["mods_on_disk"] = len(list((server / "mods").glob("*.jar")))
            report["plugins_enabled"] = len(re.findall(r"\bEnabling ([A-Za-z0-9_.-]+) v", boot_log))
            if report["mods_on_disk"] != 37 or report["plugins_enabled"] < 14:
                raise RuntimeError("not all 36 original mods + Curtain / 14 plugins loaded")
            write_command(proc, "gamerule doMobSpawning false")
            # Deliberately not a real-world city; forced chunks and simple player motion.
            write_command(proc, "forceload add 0 0")
            for i, name in enumerate(BOTS):
                offset = logfile.stat().st_size
                write_command(proc, f"player {name} spawn at {i * 8} 90 0")
                _, response = wait_for(logfile, re.escape(name) + r".*(?:joined the game|logged in)|(?:joined the game|logged in).*" + re.escape(name), offset, 45, proc)
                report.setdefault("join_log_tails", []).append(response[-350:])
                write_command(proc, f"player {name} move forward")
            offset = logfile.stat().st_size
            write_command(proc, "list")
            _, response = wait_for(logfile, r"There are (\d+) (?:of a max of|out of maximum) (\d+) players online[^\n]*", offset, 30, proc)
            line = re.search(r"There are (\d+) (?:of a max of|out of maximum) (\d+) players online[^\n]*", response, re.I).group(0)
            report["list_reply"] = line
            report["list_count"] = int(re.search(r"There are (\d+)", line).group(1))
            report["local_status"] = status("127.0.0.1", 25565)
            if report["list_count"] < len(BOTS) or not all(name in line for name in BOTS):
                raise RuntimeError("fresh list does not contain all three fake players")
            if report["local_status"]["players"]["online"] < len(BOTS):
                raise RuntimeError("local protocol status does not count all fake players")
            cpu0 = cpu_time_seconds(proc.pid)
            rss = []
            deadline = time.monotonic() + 40
            while time.monotonic() < deadline and proc.poll() is None:
                rss.append(rss_mb(proc.pid))
                time.sleep(1)
            report["steady_rss_mib"] = [v for v in rss if v is not None]
            cpu1 = cpu_time_seconds(proc.pid)
            report["cpu_seconds_40s"] = round(cpu1 - cpu0, 2) if cpu1 and cpu0 else None
            offset = logfile.stat().st_size
            write_command(proc, "spark health")
            _, response = wait_for(logfile, r"Tick durations \(min/med/95%ile/max ms\) from last 10s, 1m:", offset, 20, proc)
            report["mspt_1m"] = metrics_from_log(response)
            offset = logfile.stat().st_size
            write_command(proc, "list")
            _, response = wait_for(logfile, r"There are (\d+) (?:of a max of|out of maximum) (\d+) players online[^\n]*", offset, 20, proc)
            report["final_list_reply"] = re.search(r"There are (\d+) (?:of a max of|out of maximum) (\d+) players online[^\n]*", response, re.I).group(0)
            report["valid"] = (proc.poll() is None and report["mspt_1m"] is not None and
                               all(name in report["final_list_reply"] for name in BOTS) and
                               len(report["steady_rss_mib"]) >= 30)
            write_command(proc, "stop")
            try:
                proc.wait(timeout=45)
            except subprocess.TimeoutExpired:
                raise RuntimeError("server did not stop cleanly")
            report["clean_stop"] = proc.returncode == 0
            report["valid"] &= report["clean_stop"]
    except Exception as exc:
        report["error"] = str(exc)[:650]
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        if logfile.exists():
            lines = logfile.read_text(errors="replace")
            report["critical_lines"] = [line[-550:] for line in lines.splitlines() if re.search(
                r"Mixin apply failed|FATAL|Exception in server tick loop|OutOfMemoryError|Could not enable plugin", line, re.I)][:20]
            # The tail of a Forge crash is mostly CompletableFuture frames; keep
            # the actual first cause, mixin target and exception type for triage.
            report["root_causes"] = [line[-600:] for line in lines.splitlines() if re.search(
                r"Caused by:|Exception:|Error:|InjectionError|InvalidMixinException|MixinTransformerError", line, re.I)][:35]
            report["log_tail"] = lines[-1800:]
            report["command_error_context"] = [lines[max(0, m.start() - 500):m.start() + 2400]
                                               for m in list(re.finditer(r"An unexpected error occurred trying to execute that command|benchA\d+.*(?:left the game|disconnected)", lines))[:5]]
            report["valid"] &= not report["critical_lines"]
        (output / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({k: v for k, v in report.items() if k != "steady_rss_mib"}, indent=2, ensure_ascii=False), flush=True)
    return int(not report["valid"])


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: engine_fakeplayers.py <released-server-pack.zip> <curtain.jar> <output-dir>")
    sys.exit(main(*(Path(x).resolve() for x in sys.argv[1:])))
