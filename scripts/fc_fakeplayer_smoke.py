#!/usr/bin/env python3
"""Isolated FunCity smoke using Curtain server-side fake players.

The caller must prepare a throwaway server (including bootstrap libraries) and
provide the original, checksum-pinned Curtain JAR. This cannot validate a Forge
client handshake or measure real-player capacity. Never point at a live server.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sys
import time
import zipfile

from fc_bench import JvmRun, matched_world, read_props

CURTAIN_SHA = "c9234d2c5ca43c337abac25a05022fe2f226c884855aa6941b6130c60777819d"
COREPROTECT_SHA = "04f31b609d1e3e1c53e99aaa06ca10ea6bdf5172c94bf5af8ccf108b0bc4b977"
BOTS = ("benchA01", "benchA02", "benchA03")
LIST = re.compile(r"There are (\d+) (?:of a max of|out of maximum) (\d+) players online[^\n]*", re.I)


def test_only_curtain(source, dest):
    """Remove only the upstream NaturalSpawnerMixin that failed on CatServer.

    The modified, unsigned Curtain is strictly an isolated test dependency; the
    other Curtain mixins, including /player, remain. Fail on unexpected input.
    """
    if hashlib.sha256(source.read_bytes()).hexdigest() != CURTAIN_SHA:
        raise ValueError("Curtain checksum changed")
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(dest, "w") as zout:
        info = zin.getinfo("curtain.mixins.json")
        config = json.loads(zin.read(info))
        mixins = config["mixins"]
        if mixins.count("NaturalSpawnerMixin") != 1 or not all(
            name in mixins for name in ("rules.command_player.PlayerListMixin",
                                       "rules.command_player.ServerPlayerEntityMixin")):
            raise ValueError("Curtain mixin layout changed")
        mixins.remove("NaturalSpawnerMixin")
        for item in zin.infolist():
            if item.filename.startswith("META-INF/") and item.filename.lower().endswith((".sf", ".rsa", ".dsa")):
                continue  # signing no longer valid after modifying the mixin config
            data = json.dumps(config, indent=2).encode() + b"\n" if item.filename == info.filename else zin.read(item)
            zout.writestr(item, data)


def wait_reply(path, offset, pattern, process, timeout=40):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with path.open("rb") as f:
            f.seek(offset)
            text = f.read().decode("utf-8", "replace")
        match = pattern.search(text)
        if match:
            return match.group(0)
        if process.poll() is not None:
            raise RuntimeError(f"server exited ({process.returncode}) while waiting for {pattern.pattern}")
        time.sleep(0.25)
    raise RuntimeError(f"timeout waiting for {pattern.pattern}; log tail: {text[-650:]}")


def proc_sample(pid):
    """Linux runner: RSS in MiB and accumulated JVM CPU seconds (not client FPS)."""
    stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    ticks = int(stat[11]) + int(stat[12])  # utime + stime; field 3 starts at index 0
    status = Path(f"/proc/{pid}/status").read_text()
    rss = re.search(r"^VmRSS:\s*(\d+) kB", status, re.M)
    return round(int(rss.group(1)) / 1024, 1) if rss else None, ticks / os.sysconf("SC_CLK_TCK")


def main(stage, engine, curtain, output):
    output.mkdir(parents=True, exist_ok=True)
    report = {"valid": False, "names": list(BOTS), "method": "3 server-side Curtain fake players, pinned CoreProtect and no ClaimChunk on disposable runner; /list at spawn and after 40 seconds", "limitations": "Not a Forge client login, a modded-event audit or a gameplay/capacity benchmark. Test-only derived Curtain removes NaturalSpawnerMixin. Never publish this JAR.", "production_changes": False}
    jar = stage / engine
    log = output / "fakeplayers.log"
    server = None
    try:
        # Refuse use outside the dedicated disposable CI stage or against public IPs.
        if not stage.resolve().is_relative_to(Path("/tmp/fc-smoke").resolve()):
            raise ValueError("not the disposable /tmp/fc-smoke stage")
        props = (stage / "server.properties").read_text(encoding="latin-1")
        if not re.search(r"^server-ip=127\.0\.0\.1\s*$", props, re.M):
            raise ValueError("server must bind only to 127.0.0.1")
        if not jar.is_file() or not (stage / "libraries").is_dir():
            raise ValueError("engine/bootstrap missing; cannot start isolated smoke")
        plugins = stage / "plugins"
        cp = [p for p in plugins.glob("*.jar") if p.name.lower().startswith("coreprotect")]
        if len(cp) != 1 or hashlib.sha256(cp[0].read_bytes()).hexdigest() != COREPROTECT_SHA:
            raise ValueError("pinned CoreProtect v21.2 missing or duplicated")
        # Open city: disable territorial claims ONLY in this temporary copy.
        claim_jars = [p for p in plugins.glob("*.jar") if p.name.lower().startswith("claimchunk")]
        report["claims_disabled_in_test"] = [p.name for p in claim_jars]
        disabled = stage / "plugins-disabled-test-only"
        for p in claim_jars:
            disabled.mkdir(exist_ok=True)
            p.rename(disabled / (p.name + ".disabled"))
        mods = stage / "mods"
        if len(list(mods.glob("*.jar"))) != 36:
            raise ValueError("reference pack mods changed (expected 36)")
        mod = mods / "curtain-mc1.16.5-1.3.2-test-only.jar"
        test_only_curtain(curtain, mod)
        report["curtain_test_sha256"] = hashlib.sha256(mod.read_bytes()).hexdigest()
        report["engine_sha256"] = hashlib.sha256(jar.read_bytes()).hexdigest()
        report["mods_on_disk"] = len(list(mods.glob("*.jar")))
        reference = os.environ.get('FC_WORLD_SNAPSHOT')
        if reference:
            world = read_props(stage / 'server.properties')[0].get('level-name', 'world')
            report['world_snapshot_sha256'] = matched_world(stage, reference, world, 'restore')
        server = JvmRun(str(stage), engine, ["-Xms1G", "-Xmx3G"], str(log))
        server.port = 25565
        server.start()
        if not server.wait_done(360):
            raise RuntimeError(f"server did not finish boot (exit={getattr(server, 'exit_early', 'timeout')})")
        report["boot_wall_s"] = server.done_wall_s
        boot_log = log.read_text(errors="replace")
        report["plugins_enabled"] = sorted(set(re.findall(r"\bEnabling ([A-Za-z0-9_.-]+) v", boot_log)))
        enabled = {p.lower() for p in report["plugins_enabled"]}
        if "coreprotect" not in enabled or "claimchunk" in enabled:
            raise RuntimeError("expected CoreProtect enabled, ClaimChunk disabled (open-city test)")
        if len(enabled) < 14:
            raise RuntimeError("fewer than 14 plugins enabled in open-city + CoreProtect test")
        # A line announcing a player is not proof the player is still connected.
        for i, name in enumerate(BOTS):
            offset = log.stat().st_size
            server.send(f"player {name} spawn at {i * 8} 90 0")
            wait_reply(log, offset, re.compile(rf"\b{re.escape(name)}\b.*joined the game|joined the game.*\b{re.escape(name)}\b", re.I), server.p)
            server.send(f"player {name} move forward")
        offset = log.stat().st_size
        server.send("list")
        line = wait_reply(log, offset, LIST, server.p)
        report["initial_list"] = line
        if int(LIST.search(line).group(1)) < 3 or any(name not in line for name in BOTS):
            raise RuntimeError(f"fake players absent from fresh initial /list: {line}")
        rss0, cpu0 = proc_sample(server.p.pid)
        t0 = time.monotonic()
        rss_samples = [rss0]
        while time.monotonic() - t0 < 40 and server.p.poll() is None:
            time.sleep(5)
            if server.p.poll() is None:
                rss_samples.append(proc_sample(server.p.pid)[0])
        rss1, cpu1 = proc_sample(server.p.pid) if server.p.poll() is None else (None, None)
        report["active_40s_rss_max_mib"] = max((r for r in rss_samples if r is not None), default=None)
        report["active_40s_cpu_seconds"] = round(cpu1 - cpu0, 2) if cpu1 is not None else None
        report["active_40s_elapsed_s"] = round(time.monotonic() - t0, 1)
        if server.p.poll() is not None or report["active_40s_elapsed_s"] < 40:
            raise RuntimeError("server exited before completing 40s with bots")
        offset = log.stat().st_size
        server.send("list")
        line = wait_reply(log, offset, LIST, server.p)
        report["after_40s_list"] = line
        if int(LIST.search(line).group(1)) < 3 or any(name not in line for name in BOTS):
            raise RuntimeError(f"fake players absent from fresh after_40s /list: {line}")
        report["valid"] = server.p.poll() is None
        report["clean_stop"] = server.stop(45) == "CLEAN" and server.p.returncode == 0
        report["valid"] &= report["clean_stop"]
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"[:1000]
    finally:
        if server:
            if server.p and server.p.poll() is None:
                try:
                    os.killpg(os.getpgid(server.p.pid), signal.SIGKILL)
                    server.p.wait(timeout=10)
                except ProcessLookupError:
                    pass
            server.close()
        if log.exists():
            text = log.read_text(errors="replace")
            report["critical_lines"] = [line[-500:] for line in text.splitlines() if re.search(
                r"Mixin apply failed|FATAL|Exception in server tick loop|OutOfMemoryError|Could not enable plugin", line, re.I)][:20]
            report["log_tail"] = text[-2500:]
            if report["critical_lines"]:
                report["valid"] = False
        (output / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        if not report["valid"] and os.environ.get("GITHUB_ACTIONS") == "true":
            reason = report.get("error", "critical server log: " + "; ".join(report.get("critical_lines", [])[:2]))
            # Actions log archives are not always retrievable; publish a bounded,
            # sanitized crash excerpt as an annotation (test stage has no secrets).
            if "server did not finish boot" in reason and log.exists():
                suspects = [line.strip() for line in text.splitlines() if re.search(
                    r"Caused by:|Exception|Mixin|FATAL|\bERROR\b|Failed to|Crash report", line, re.I)]
                reason += " | crash clues: " + " | ".join(suspects[:3] + suspects[-3:])
                reason += " | log end: " + text[-500:]
            reason = re.sub(r"\s+", " ", reason)
            print("::error::fake-player gate failed: " + reason[:1400], flush=True)
        print(json.dumps({k: v for k, v in report.items() if k != "log_tail"}, ensure_ascii=False, indent=2), flush=True)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit("usage: fc_fakeplayer_smoke.py <isolated-stage> <engine-jar-basename> <curtain.jar> <output-dir>")
    sys.exit(main(Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve(), Path(sys.argv[4]).resolve()))
