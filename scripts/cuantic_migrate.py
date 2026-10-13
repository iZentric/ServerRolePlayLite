#!/usr/bin/env python3
"""MIGRATE — compara gazda noua cu cea de pe care ruleaza ACUM serverul.

Citeste, nu scrie: pe gazda tinta ridica un server-umbra pe port 25599, intr-un
director din /tmp, cu pack-ul extras din release-ul `lite` verificat ca sha256.
Serverul live (92.5.171.150:25565, ~/cuantic-live, frpc) nu e atins: niciun kill,
niciun fișier scris în el, nicio schimbare de port.

Verdictul e al porților, nu al dorinței:
  PORTA 1  identitate   pack-ul umbrei are același sha256 ca cel care rulează
  PORTA 2  CPU          micro-benchmark similar sau mai bun decât gazda live
  PORTA 3  pornire      `Done` sub 1,25x timpul live, cu 36 moduri + 14 pluginuri
  PORTA 4  RAM          RSS sub 105% din live (altfel „mai mult consum” nu e upgrade)
  PORTA 5  vecini       steal de la hipervizor < 3% în fereașa de măsurătoare
Oricare poartă căzută => RĂMII, cu motivul scris în raport.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LITE_RELEASE_API = "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite"
PACK_NAME = "CUANTIC-Server-CatServer-1.7.7.zip"
LIVE_DIR = Path.home() / "cuantic-live"
SHADOW_PORT = 25599
EXPECTED = {"mods": 36, "plugins": 14}
BOOT_FACTOR = 1.25
RSS_FACTOR = 1.05
STEAL_MAX_PCT = 3.0
MICRO_TOLERANCE = 0.95      # gazda noua trebuie sa stea in 5% din live sau mai bine
MICRO_SECONDS = 3.0


# ------------------------------------------------------------------ masuratori
def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def micro(seconds=MICRO_SECONDS):
    """Micro-benchmark determinist, aceeasi expresie pe amandoua gazdele.

    Limbaj de masurare, nu de reclamă: un singur numar (cicli aproximativi/secunda
    printr-un sieve de prime), rulat identic oriunde exista python3.
    """
    code = ("import time,sys\n"
            "L=2_000_000; s=time.perf_counter(); n=0\n"
            "while time.perf_counter()-s < %r:\n"
            "    f=[True]*L; c=0\n"
            "    for i in range(2,L):\n"
            "        if f[i]:\n"
            "            c+=1\n"
            "            for j in range(i*i,L,i): f[j]=False\n"
            "    n+=c\n"
            "print(int(n/max(time.perf_counter()-s,1e-9)))\n" % seconds)
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                          timeout=seconds * 4)
    out = (proc.stdout or "").strip()
    return int(out) if out.isdigit() else None


def steal_pct(sample_seconds=2.0):
    """% din timp pierdut din cauza vecinilor de hipervizor.

    Pe OpenVZ/Virtuozzo, /proc/stat raporta steal 0 fals; de-aia intoarcem si
    `hidden=True` ca sa nu tragem concluzia „nu fură nimeni” dintr-un zero orb.
    """
    def read():
        try:
            line = Path("/proc/stat").read_text().splitlines()[0]
        except OSError:
            return None
        return [int(x) for x in line.split()[1:]]

    def fields(v):
        user, nice, system, idle, iowait, irq, softirq, steal = (list(v) + [0] * 8)[:8]
        busy = user + nice + system + irq + softirq + steal
        return busy, user + nice + system + idle + iowait + irq + softirq + steal, steal

    a, b = read(), None
    if a is None:
        return None, True
    time.sleep(sample_seconds)
    b = read()
    if b is None:
        return None, True
    busy_a, total_a, steal_a = fields(a)
    busy_b, total_b, steal_b = fields(b)
    dt, ds = total_b - total_a, steal_b - steal_a
    if dt <= 0:
        return None, True
    return 100.0 * ds / dt, ds == 0 and "vz" in Path("/proc/cpuinfo").read_text(errors="replace").lower()


def rss_mib(pid):
    try:
        text = Path(f"/proc/{pid}/status").read_text(errors="replace")
    except OSError:
        return None
    m = re.search(r"VmRSS:\s+(\d+)\s+kB", text)
    return int(m.group(1)) / 1024 if m else None


def cpuinfo():
    info = {"model": None, "cores": os.cpu_count(), "mhz": None, "avx2": False}
    try:
        text = Path("/proc/cpuinfo").read_text(errors="replace")
    except OSError:
        return info
    m = re.search(r"^model name\s*:\s*(.+)$", text, re.M)
    info["model"] = m.group(1).strip() if m else None
    m = re.search(r"^cpu MHz\s*:\s*([0-9.]+)", text, re.M)
    info["mhz"] = float(m.group(1)) if m else None
    info["avx2"] = "avx2" in text
    return info


def disk(path):
    st = shutil.disk_usage(path)
    return {"free_gib": round(st.free / 1024 ** 3, 1), "total_gib": round(st.total / 1024 ** 3, 1),
            "used_pct": round(100 * st.used / st.total, 1) if st.total else None}


# ------------------------------------------------------------------ server-umbra
def fetch_pack(dest):
    api = json.load(urllib.request.urlopen(urllib.request.Request(
        LITE_RELEASE_API, headers={"User-Agent": "cuantic-migrate/1.0"}), timeout=30))
    url = next((a["browser_download_url"] for a in api["assets"] if a["name"] == PACK_NAME), None)
    if not url:
        raise SystemExit(f"n-am gasit {PACK_NAME} in release-ul lite")
    with urllib.request.urlopen(url, timeout=180) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return api.get("tag_name"), sha256(dest)


def shadow_boot(workdir, log_path, boot_timeout=300, watch=20):
    """Ridica serverul-umbra si intoarce (done_s, rss_mib, pluginuri, keep_up, root_cause)."""
    args = workdir / "unix_args.txt"
    if not args.is_file():
        return {"error": "unix_args.txt lipseste dupa extragere"}
    heap = "4G"
    with open(log_path, "w") as log:
        proc = subprocess.Popen([os.environ.get("JAVA_HOME_BIN", "java"), f"@{args}"],
                                cwd=workdir, stdout=log, stderr=subprocess.STDOUT,
                                stdin=subprocess.PIPE, start_new_session=True)
        started = time.time()
        done = None
        try:
            while time.time() - started < boot_timeout:
                text = log_path.read_text(errors="replace")
                m = re.search(r"Done \(([0-9.]+)s\)", text)
                if m:
                    done = float(m.group(1))
                    break
                if proc.poll() is not None:
                    break
                time.sleep(1)
            time.sleep(watch)
            peak = max(filter(None, [rss_mib(proc.pid)]), default=None)
            text = log_path.read_text(errors="replace")
        finally:
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    return {"boot_done_s": done,
            "rss_peak_mib": round(peak, 1) if peak else None,
            "plugins_enabled": len(re.findall(r"Enabling ", text)),
            "mods": len((workdir / "mods").glob("*.jar")) if (workdir / "mods").is_dir() else None,
            "cant_keep_up": len(re.findall(r"Can't keep up!", text)),
            "root_cause": (re.search(r"([\w.$]+(?:Exception|Error)): ?(.{4,160})", text) or [None, None, None])[0]}


def measure(out_dir, use_live_pack=False, boot_timeout=300):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = {"when": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": os.uname().nodename,
              "cpu": cpuinfo(), "disk": disk(out), "micro_ops_s": micro(), "shadow_port": SHADOW_PORT}
    steal, hidden = steal_pct()
    report["steal_pct"] = steal
    report["steal_hidden"] = hidden
    if use_live_pack:
        src = LIVE_DIR / PACK_NAME
        if not src.is_file():
            zips = sorted(LIVE_DIR.glob("*.zip"))
            if not zips:
                raise SystemExit(f"nu gasesc pack-ul in {LIVE_DIR}")
            src = zips[0]
        pack, tag = src, "live"
    else:
        pack = out / PACK_NAME
        tag, _ = fetch_pack(pack)
    report["release_tag"] = tag
    report["pack_sha256"] = sha256(pack)
    report["pack_bytes"] = pack.stat().st_size
    stage = out / "shadow"
    stage.mkdir(exist_ok=True)
    import zipfile
    with zipfile.ZipFile(pack) as z:
        z.extractall(stage)
    (stage / "eula.txt").write_text("eula=true\n", encoding="utf-8")
    props = stage / "server.properties"
    text = props.read_text(errors="replace") if props.is_file() else ""
    text = re.sub(r"^server-port=.*$", f"server-port={SHADOW_PORT}", text, flags=re.M)
    if "server-port=" not in text:
        text += f"\nserver-port={SHADOW_PORT}\n"
    props.write_text(text, encoding="utf-8")
    report.update(shadow_boot(stage, out / "shadow.log", boot_timeout=boot_timeout))
    (out / "measure.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    return report


def live_baseline(out_dir):
    """Referinta de pe gazda live: citim ce exista deja, nu pornim nimic al doilea.

    Nu atingem serverul: /proc/<pid>/status, live.log si fisierele din ~/cuantic-live.
    """
    out = Path(out_dir) if out_dir else None
    b = {"when": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "host": os.uname().nodename,
         "cpu": cpuinfo(), "disk": disk(LIVE_DIR if LIVE_DIR.is_dir() else Path.home()),
         "micro_ops_s": micro(), "source": str(LIVE_DIR)}
    steal, hidden = steal_pct()
    b["steal_pct"], b["steal_hidden"] = steal, hidden
    pid = None
    try:
        for entry in Path("/proc").iterdir():
            if not entry.name.isdigit():
                continue
            try:
                cmd = (entry / "cmdline").read_bytes().decode(errors="replace")
            except OSError:
                continue
            if "java" in cmd and "unix_args" in cmd:
                pid = int(entry.name)
                break
    except OSError:
        pid = None
    b["java_pid"] = pid
    b["rss_mib"] = round(rss_mib(pid), 1) if pid else None   # instantaneu, nu varf: live nu are monitor de varf
    log = LIVE_DIR / "live.log"
    if log.is_file():
        text = log.read_text(errors="replace")
        dones = re.findall(r"Done \(([0-9.]+)s\)", text)
        b["boot_done_s"] = float(dones[-1]) if dones else None
        tail = text[-400_000:]
        b["plugins_enabled"] = len(re.findall(r"Enabling ", tail))
        b["cant_keep_up"] = len(re.findall(r"Can't keep up!", tail))
    mods = LIVE_DIR / "mods"
    b["mods"] = len(list(mods.glob("*.jar"))) if mods.is_dir() else None
    jars = sorted(LIVE_DIR.glob("CatServer-*.jar"))
    if jars:
        b["pack_sha256"] = sha256(jars[0])
        b["jar"] = jars[0].name
    pack = LIVE_DIR / PACK_NAME
    if pack.is_file():
        b["pack_sha256"] = sha256(pack)
    addr = LIVE_DIR / "ADRESA"
    if addr.is_file():
        b["address"] = addr.read_text(errors="replace").strip()
    if out:
        out.mkdir(parents=True, exist_ok=True)
        (out / "live.json").write_text(json.dumps(b, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    return b


# ------------------------------------------------------------------ verdict
def verdict(live, new):
    """Doar porti trecute sau un motiv care ramane scris in raport."""
    gates, notes = [], []

    def gate(name, ok, detail):
        gates.append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok:
            notes.append(f"{name}: {detail}")

    ident = bool(live.get("pack_sha256")) and live.get("pack_sha256") == new.get("pack_sha256")
    gate("identitate", ident, f"sha256 live {str(live.get('pack_sha256'))[:12]} vs nou {str(new.get('pack_sha256'))[:12]}"
         if not ident else "același pack, verificat byte cu byte")
    lm, nm = live.get("micro_ops_s"), new.get("micro_ops_s")
    if lm and nm:
        ratio = nm / lm
        gate("CPU", ratio >= MICRO_TOLERANCE,
             f"{nm:,} vs live {lm:,} ops/s".replace(",", ".") + f" ({ratio * 100:.0f}% din gazda actuală)")
    else:
        gate("CPU", False, "micro-benchmark lipsă pe una din gazde — fără comparare, nu presupunem")
    lb, nb = live.get("boot_done_s"), new.get("boot_done_s")
    if nb is None:
        gate("pornire", False, "umbra nu a ajuns la `Done`: " + str(new.get("root_cause") or "vezi log"))
    elif lb:
        gate("pornire", nb <= lb * BOOT_FACTOR, f"boot {nb:.3f} s vs live {lb:.3f} s (prag ×{BOOT_FACTOR})")
    else:
        gate("pornire", False, f"umbra a pornit ({nb:.3f} s) dar măsurarea live n-are boot de referință")
    lr, nr = live.get("rss_mib") or live.get("rss_peak_mib"), new.get("rss_peak_mib")
    if lr and nr:
        gate("RAM", nr <= lr * RSS_FACTOR, f"RSS umbră {nr:.1f} vs live {lr:.1f} MiB (instantaneu pe live, prag +5%)")
    else:
        gate("RAM", False, "RSS incomplet pe una din gazde")
    st = new.get("steal_pct")
    if st is None:
        gate("vecini", False, "steal nelizibil — pe OpenVZ 0-ul nu înseamnă nimic")
    else:
        gate("vecini", st < STEAL_MAX_PCT and not new.get("steal_hidden"),
             f"steal {st:.2f}%" + (" (-contor ascuns de container)" if new.get("steal_hidden") else ""))
    plugins = new.get("plugins_enabled")
    gate("pack intact", plugins == EXPECTED["plugins"] and new.get("mods") == EXPECTED["mods"],
         f"pluginuri {plugins}/{EXPECTED['plugins']} · moduri {new.get('mods')}/{EXPECTED['mods']}")
    ok = all(g["ok"] for g in gates)
    return {"verdict": "MIGREAZĂ" if ok else "STAI PE GAZDA ACTUALĂ",
            "gates": gates, "notes": notes,
            "limit": "umbra a mers pe port " + str(SHADOW_PORT) + ", în /tmp, fără frpc și fără "
                     "date de jucători; live-ul nu a fost atins"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure", help="măsoară gazda curentă")
    m.add_argument("--out", required=True)
    m.add_argument("--use-live-pack", action="store_true",
                   help="folosește pack-ul din ~/cuantic-live (de pe gazda live, fără download)")
    m.add_argument("--boot-timeout", type=int, default=300)
    c = sub.add_parser("compare", help="verdict din două măsurători JSON")
    c.add_argument("--live", required=True)
    c.add_argument("--new", required=True)
    c.add_argument("--out")
    b = sub.add_parser("baseline", help="referinta citita de pe gazda live, fara niciun pornit nou")
    b.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "baseline":
        print(json.dumps(live_baseline(a.out), ensure_ascii=False, indent=2))
        return 0
    if a.cmd == "measure":
        print(json.dumps(measure(a.out, a.use_live_pack, a.boot_timeout), ensure_ascii=False, indent=2))
        return 0
    live = json.loads(Path(a.live).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    out = verdict(live, new)
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0 if out["verdict"].startswith("MIGREAZĂ") else 3


if __name__ == "__main__":
    sys.exit(main())
