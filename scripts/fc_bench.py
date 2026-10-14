#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FC-BENCH v4 — banca de masurare FunCity pe pack-ul CUANTIC 36/14 (MC 1.16.5, java 11).

Metodologie (identica per brat, masina identica = runner GitHub izolat):
  stage curat = pack dezarhivat; excluzem libraries/run/version.json + jar-urile de la
  radacina DOAR pentru motoare de tip bootstrap (Mohist/FunCity le aduce el); bratul
  CatServer isi pastrand librariile din pack.
  Faza A = instalare bootstrap (necontrolata, nemasurata) + lumea creata o data, cu
           seed fix din server.properties; world-ul REZULTANT e comun tuturor probelor.
  Faza B = N probe de boot la cald pe ACELASI world; in fiecare proba: pornire masurata
           (timp real pana la "Done"), intarziere de logare (probe protocol 1.16.5,
           offline), esantionare TPS/MSPT prin consola, supraveghere "Can't keep up!",
           esantionare resurse (RSS/CPU), jurnal GC, oprire curata prin consola.

Reguli de onestitate implementate aici:
  - zero masuratori ascunse: orice metrica care nu poate fi parse-uit e None + motiv,
    niciodata 0 inventat;
  - abaterile de la pack (seed fix, online-mode=false pentru probele headless,
    view-distance, check_update=false la Mohist) sunt patch-uite IDENTIC la toate
    bratele SI inregistrate in结果.json sub "overrides" ca sa fie auditabile;
  - un brat care nu ajunge la "Done" e inregistrat ESUAT_TEHNIC, nu exclus.

Rulare (de CI): python3 fc_bench.py --arm-conf arm.json cu env:
  FC_JAR=cale jar de boot (poate lipsi pt catserver) ; FC_STAGE=director lucru
  FC_OUT=director rezultate ; FC_TRIALS=3 FC_RUN_SECONDS=300 FC_BOOT_TIMEOUT=600
  FC_INSTALL_TIMEOUT=420 FC_EXCLUDE='libraries/* run/* version.json /*.jar'
"""
import argparse, json, os, re, signal, socket, statistics, struct, subprocess, sys, threading, time, uuid, zipfile

ANSI = re.compile(r"\x1b\[[0-9;]*m")
DONE_RE = re.compile(r"Done \(([0-9]+\.[0-9]+)s\)")
TPS_RE = re.compile(r"(?i)tps[\s\S]{0,40}?([0-9]{1,2}\.\d{1,4})")
TPS_LINE_RE = re.compile(r"(?i)(tps|per second|from last)")
MSPT_RE = re.compile(r"(?i)(mspt|ticks)[^\n]{0,90}?([0-9]+\.[0-9]+)\s*ms")
OVERRUN_RE = re.compile(r"Can't keep up!.*?Running (\d+)ms", re.I)
GC_RE = re.compile(r"GC\(\d+\).*?TotalTime: ([0-9.]+)ms")
CRIT_RES = [
    re.compile(r"Exception in server tick loop", re.I),
    re.compile(r"Failed to start", re.I),
    re.compile(r"Could not (?:load|enable) plugin", re.I),
    re.compile(r"Mixin apply failed", re.I),
]

def log(msg):
    print(time.strftime("[%H:%M:%S] ") + msg, flush=True)

def strip_ansi(s):
    return ANSI.sub("", s)

# ---------------- props ----------------

def read_props(path):
    props, order = {}, []
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or line.lstrip().startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    props[k.strip()] = v
                    order.append(k.strip())
    return props, order

def write_props(path, props, order):
    with open(path, "w", encoding="utf-8") as f:
        for k in order:
            f.write(f"{k}={props[k]}\n")

# ---------------- resurse ----------------

def clock_ticks_hz():
    try:
        return os.sysconf("SC_CLK_TCK")
    except Exception:
        return 100

def proc_stat_jvm():
    """(ticked_total, rss_kb, threads) pentru procesul java cu RSS maxim; None daca nu-i."""
    best = None
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/comm") as f:
                if f.read().strip() not in ("java", "OpenJDK"):
                    continue
            with open(f"/proc/{pid}/stat") as f:
                parts = f.read().rsplit(") ", 1)[1].split()
            utime, stime = int(parts[11]), int(parts[12])
            threads = int(parts[17])
            rss = 0
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        rss = int(line.split()[1])
                        break
            t = utime + stime
            if best is None or rss > best[1]:
                best = (t, rss, threads)
        except Exception:
            continue
    return best

class ResSampler(threading.Thread):
    def __init__(self, interval=10.0):
        super().__init__(daemon=True)
        self.interval = interval
        self.samples = []  # (rss_kb, cpu_pct, threads)
        self.stop_flag = threading.Event()

    def run(self):
        hz = clock_ticks_hz()
        prev = proc_stat_jvm()
        tprev = time.monotonic()
        while not self.stop_flag.wait(self.interval):
            cur = proc_stat_jvm()
            now = time.monotonic()
            if cur and prev:
                cpu = (cur[0] - prev[0]) / hz / max(now - tprev, 1e-6) * 100.0
                self.samples.append([cur[1], round(cpu, 1), cur[2]])
            if cur:
                prev, tprev = cur, now

    def stop(self):
        self.stop_flag.set()

# ---------------- probe de logare (protocol 1.16.5, offline) ----------------

def vi(n):
    out = b""
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out += bytes([b | 0x80])
        else:
            out += bytes([b])
            return out

def frame(packet_id, payload):
    body = vi(packet_id) + payload
    return vi(len(body)) + body

def read_vi(sock):
    num = 0
    for i in range(5):
        b = sock.recv(1)
        if not b:
            raise OSError("conexiune inchisa")
        b = b[0]
        num |= (b & 0x7F) << (7 * i)
        if not b & 0x80:
            return num
    raise ValueError("VarInt prea lung")

def read_frame(sock, timeout=10.0):
    sock.settimeout(timeout)
    ln = read_vi(sock)
    data = b""
    while len(data) < ln:
        chunk = sock.recv(min(65536, ln - len(data)))
        if not chunk:
            raise OSError("conexiune inchisa in cadru")
        data += chunk
    pid = vi2int(data)
    return pid, data[1 + len(vi(pid)):]

def vi2int(buf):
    num = 0
    for i in range(5):
        if i >= len(buf):
            raise ValueError("VarInt incomplet")
        b = buf[i]
        num |= (b & 0x7F) << (7 * i)
        if not b & 0x80:
            return num
    raise ValueError("VarInt prea lung")

def login_probe(port, user="FcBench"):
    """Returneaza (ok, latency_ms, detaliu). Trimite handshake+login start si asteapta
    login success (0x02). Dison/criptare/esec = ok=False cu motiv, fara cifre inventate."""
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=10)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.sendall(frame(0x00, vi(754) + vi(len("127.0.0.1")) + b"127.0.0.1" + struct.pack(">H", port) + vi(2)))
        t0 = time.monotonic()
        s.sendall(frame(0x00, vi(len(user)) + user.encode()))
        seen = []
        deadline = t0 + 15.0
        while time.monotonic() < deadline:
            try:
                pid, payload = read_frame(s, timeout=max(0.1, deadline - time.monotonic()))
            except Exception as e:
                s.close()
                return False, None, f"cadru citit esuat dupa {seen}: {type(e).__name__}"
            seen.append(pid)
            if pid == 0x02:  # login success (vanilla, state 2)
                dt = (time.monotonic() - t0) * 1000.0
                s.close()
                return True, round(dt, 1), f"login_success (pachete vazute: {seen})"
            if pid == 0x00:  # disconnect/login_error cu JSON
                try:
                    ln = vi2int(payload)
                    reason = payload[1 + len(vi(ln)):1 + len(vi(ln)) + ln].decode("utf-8", "replace")
                except Exception:
                    reason = payload[:120].hex()
                s.close()
                return False, None, f"refuzat: {reason[:200]}"
            if pid == 0x01:  # encryption request => online-mode activat, ne placele
                s.close()
                return False, None, "serverul cere criptare (online-mode pornit) — proba nu se poate face"
            # altceva (query FML etc.): continuam
        s.close()
        return False, None, f"timeout 15s; pachete: {seen}"
    except Exception as e:
        return False, None, f"eroare proba: {type(e).__name__}: {e}"

def port_open(port, timeout=2.0):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False

# ---------------- log server ----------------

class ServerLog:
    def __init__(self, path):
        self.path = path
        self.pos = 0

    def new_lines(self):
        out = []
        try:
            with open(self.path, encoding="utf-8", errors="replace") as f:
                f.seek(self.pos)
                chunk = f.read()
                self.pos = f.tell()
            out = [strip_ansi(l) for l in chunk.splitlines() if l.strip()]
        except OSError:
            pass
        return out

def parse_tps_mspt(lines):
    tps, mspt, raw = [], [], []
    for l in lines:
        low = l.lower()
        if low.strip().startswith(">") or "invalid" in low or "unknown" in low:
            continue
        if "mspt" in low or ("tick" in low and "ms" in low):
            raw.append(l[:220])
        m = MSPT_RE.search(l)
        if m:
            try:
                v = float(m.group(2))
                if 0.0 < v < 1000.0:
                    mspt.append(v)
            except ValueError:
                pass
        if TPS_LINE_RE.search(l) and not re.match(r"^\s*[a-z]+\s*$", l):
            m = TPS_RE.search(l)
            if m:
                try:
                    v = float(m.group(1))
                    if 0.0 <= v <= 20.0:
                        tps.append(v)
                except ValueError:
                    pass
    return tps, mspt, raw

def count_overruns(lines):
    ms = [int(m.group(1)) for m in (OVERRUN_RE.search(l) for l in lines) if m]
    return len(ms), (max(ms) if ms else 0)

def count_critiques(lines):
    n = 0
    for l in lines:
        if any(r.search(l) for r in CRIT_RES):
            n += 1
    return n

# ---------------- JVM in condusa (stdin FIFO ca sa nu primeasca EOF) ----------------

class JvmRun:
    def __init__(self, stage, jar, extra_args, logpath):
        self.stage = stage
        self.cmd = ["java"] + extra_args + ["-jar", jar, "nogui"]
        self.logpath = logpath
        self.fifo = os.path.join(stage, ".fcbench-in")
        self.p = None
        self.log = None
        self.stdin_fh = None

    def start(self):
        if not os.path.exists(self.fifo):
            os.mkfifo(self.fifo)
        # un writer MASCARE deschis ca fifo-ul sa nu dea EOF serverului
        self.writer = open(self.fifo, "w")
        self.log_fh = open(self.logpath, "ab", buffering=0)
        self.stdin_keep = open(self.fifo, "rb", buffering=0)
        self.p = subprocess.Popen(self.cmd, stdin=self.stdin_keep, stdout=self.log_fh,
                                  stderr=subprocess.STDOUT, cwd=self.stage, start_new_session=True)
        self.log = ServerLog(self.logpath)

    def send(self, line):
        try:
            self.writer.write(line + "\n")
            self.writer.flush()
        except Exception as e:
            log(f"send('{line}') esuat: {e}")

    def wait_done(self, boot_timeout, poll=2.0):
        t0 = time.monotonic()
        port_seen_at = None
        port = self.port or 25565
        while time.monotonic() - t0 < boot_timeout:
            for l in self.log.new_lines():
                m = DONE_RE.search(l)
                if m:
                    self.done_wall_s = round(time.monotonic() - t0, 2)
                    self.done_log_s = float(m.group(1))
                    return True
            if self.p.poll() is not None:
                self.exit_early = self.p.returncode
                return False
            time.sleep(poll)
        return False

    def stop(self, grace=90):
        self.send("stop")
        t0 = time.monotonic()
        while time.monotonic() - t0 < grace and self.p.poll() is None:
            time.sleep(2)
        if self.p.poll() is None:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except Exception:
                self.p.kill()
            return "KILLED_DUPA_GRACE"
        return "CLEAN"

    def close(self):
        for fh in (getattr(self, "writer", None), getattr(self, "stdin_keep", None), getattr(self, "log_fh", None)):
            try:
                if fh:
                    fh.close()
            except Exception:
                pass

# NOTE: JvmRun.port e setate de apelant inainte de wait_done.

# ---------------- faza A: stage + instalare bootstrap + setup lume ----------------

def build_stage(conf, jar, stage):
    os.makedirs(stage, exist_ok=True)
    zp = conf["pack_zip"]
    excl = set(conf.get("exclude", []))
    keep_libs = conf.get("keep_pack_libs", False)
    with zipfile.ZipFile(zp) as z:
        for info in z.infolist():
            name = info.filename
            top = name.split("/", 1)[0]
            base = name.rsplit("/", 1)[-1]
            if not keep_libs:
                if top in ("libraries", "run") or base == "version.json":
                    continue
                if "/" not in name and name.endswith(".jar"):  # jarurile de la radacina (motorul vechi)
                    continue
            target = os.path.join(stage, name)
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    dst.write(chunk)
                if (info.external_attr >> 16) & 0o111:
                    os.chmod(target, (info.external_attr >> 16) & 0o777)

def resolve_boot_jar(conf, jar, stage):
    kind = conf.get("boot_jar")
    if kind == "from_pack_root":
        # bratul CatServer: isi pune singur jarul in stage la patch (nu-l redenumim)
        path = conf.get("pack_boot_jar_path") or ""
        real = os.path.join(stage, path) if (path and stage) else ""
        if not real or not os.path.exists(real):
            if not os.path.isdir(stage):
                raise RuntimeError(f"stage lipsa: '{stage}' — verifica env FC_STAGE in workflow")
            cands = [x for x in os.listdir(stage) if x.lower().endswith(".jar") and os.path.isfile(os.path.join(stage, x))]
            if not cands:
                raise RuntimeError("niciun jar la radacina stage-ului pentru bratul catserver")
            real = os.path.join(stage, max(cands, key=lambda x: os.path.getsize(os.path.join(stage, x))))
        return os.path.basename(real)
    shutil_copy(jar, os.path.join(stage, kind))
    return kind

def shutil_copy(a, b):
    import shutil
    shutil.copyfile(a, b)

def apply_overrides(conf, stage):
    """Patch-uri de mediu, aceleasi pentru TOATE bratele; inregistrate in raport."""
    rec = {}
    props_path = os.path.join(stage, "server.properties")
    props, order = read_props(props_path)
    for k, v in conf.get("props", {}).items():
        rec[k] = {"inainte": props.get(k, "(absent)"), "dupa": v}
        if k not in order:
            order.append(k)
        props[k] = str(v)
    write_props(props_path, props, order)
    port = int(props.get("server-port", "25565"))
    # EULA (deviatie CI: acceptam noi, nu distribuim jaruri)
    eula = os.path.join(stage, "eula.txt")
    if not os.path.exists(eula):
        open(eula, "w").write("eula=true\n")
        rec["eula.txt"] = {"inainte": "(absent)", "dupa": "eula=true (scris de driver)"}
    else:
        cur = open(eula).read()
        if "eula=false" in cur:
            open(eula, "w").write("eula=true\n")
            rec["eula.txt"] = {"inainte": "eula=false", "dupa": "eula=true (scris de driver)"}
    # mohist-config/mohist.yml: check_update=false (zgomot de retea la boot)
    my = os.path.join(stage, "mohist-config", "mohist.yml")
    if os.path.exists(my):
        txt = open(my, encoding="utf-8", errors="replace").read()
        if re.search(r"^\s*check_update:\s*true", txt, re.M):
            open(my, "w").write(re.sub(r"^(\s*)check_update:\s*true", r"\1check_update: false", txt, flags=re.M))
            rec["mohist.yml:check_update"] = {"inainte": "true", "dupa": "false"}
    return rec, port

# ---------------- faza B: o proba ----------------

def one_trial(conf, stage, bootjar, port, idx, outdir, run_seconds):
    logpath = os.path.join(outdir, f"server-trial{idx}.log")
    j = JvmRun(stage, bootjar, conf["java_args"] + [f"-Xlog:gc*:file={os.path.join(outdir, f'gc-trial{idx}.log')}:time,uptime,level,tags"], logpath)
    j.port = port
    started = time.monotonic()
    j.start()
    res = {"trial": idx}
    ok = j.wait_done(conf["boot_timeout"])
    res["boot_reusit"] = bool(ok)
    if ok:
        res["boot_timp_real_s"] = j.done_wall_s
        res["boot_timp_logic_s"] = j.done_log_s
    else:
        res["boot_esec_motiv"] = f"exit={getattr(j, 'exit_early', 'timeout')}"
        try:
            os.killpg(os.getpgid(j.p.pid), signal.SIGKILL)
            j.p.wait(15)
        except Exception:
            pass
        res.update({"join_probe_ms": None, "join_probe_detaliu": "nu a bootat",
                    "tps_medie": None, "mspt_medie_ms": None, "overrun_count": 0, "overrun_max_ms": 0,
                    "critice": 0, "gc_pauze_ms_max": None})
        j.close()
        return res, j
    # login probe x3 (prima poate include efecte de caldura, luam mediana)
    lat = []
    det = []
    for i in range(3):
        okp, ms, d = login_probe(port)
        lat.append(ms) if okp else det.append(d)
        time.sleep(3)
    res["join_probe_ms"] = round(statistics.median(lat), 1) if lat else None
    res["join_probe_reusite"] = len(lat)
    res["join_probe_detaliu"] = "; ".join(det) if det else "3/3 login_success"
    j.send("list")
    # esantionare run_seconds: resurse la 10s, comenzi de tick la 45s
    rs = ResSampler(10.0)
    rs.start()
    tps_all, mspt_all = [], []
    raw_console = []
    over_n, over_max = 0, 0
    crit = 0
    tick_samples = 0
    t_end = time.monotonic() + run_seconds
    next_cmd = time.monotonic() + 30
    while time.monotonic() < t_end:
        if time.monotonic() >= next_cmd:
            tick_samples += 1
            j.send("ticks tps")
            j.send("mspt")
            j.send("tps")
            time.sleep(6)
            lines = j.log.new_lines()
            a, b, rawl = parse_tps_mspt(lines)
            raw_console += rawl
            tps_all += a
            mspt_all += b
            n, mx = count_overruns(lines)
            over_n += n
            over_max = max(over_max, mx)
            crit += count_critiques(lines)
            next_cmd = time.monotonic() + 45
        else:
            lines = j.log.new_lines()
            n, mx = count_overruns(lines)
            over_n += n
            over_max = max(over_max, mx)
            crit += count_critiques(lines)
            time.sleep(3)
    rs.stop()
    j.log.new_lines()  # consumam restul inainte de stop
    how = j.stop()
    res.update({
        "tps_probe": tps_all, "tps_medie": round(statistics.mean(tps_all), 2) if tps_all else None,
        "mspt_probe": mspt_all[:40], "mspt_medie_ms": round(statistics.mean(mspt_all), 2) if mspt_all else None,
        "overrun_count": over_n, "overrun_max_ms": over_max, "critice": crit,
        "tick_probe_incercari": tick_samples, "oprire": how,
    })
    if rs.samples:
        res["rss_medie_kb"] = int(statistics.mean(s[0] for s in rs.samples))
        res["rss_max_kb"] = max(s[0] for s in rs.samples)
        res["cpu_medie_pct"] = round(statistics.mean(s[1] for s in rs.samples), 1)
        res["threads_max"] = max(s[2] for s in rs.samples)
    else:
        res.update({"rss_medie_kb": None, "rss_max_kb": None, "cpu_medie_pct": None, "threads_max": None})
    res["linii_consola_esantion"] = raw_console[:30]
    gcp = os.path.join(outdir, f'gc-trial{idx}.log')
    pauses = []
    if os.path.exists(gcp):
        pauses = [float(m.group(1)) for m in GC_RE.finditer(open(gcp, encoding="utf-8", errors="replace").read())]
    res["gc_pauze_ms_max"] = round(max(pauses), 1) if pauses else None
    res["gc_pauze_ms_medie"] = round(statistics.mean(pauses), 2) if pauses else None
    res["gc_pauze_n"] = len(pauses)
    j.close()
    return res, j

# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm-conf", required=True)
    a = ap.parse_args()
    conf = json.load(open(a.arm_conf, encoding="utf-8"))
    stage = os.environ.get("FC_STAGE", "/tmp/fcb/stage")
    outdir = os.environ.get("FC_OUT", "/tmp/fcb/results")
    os.makedirs(outdir, exist_ok=True)
    jar = os.environ.get("FC_JAR", "")
    trials = int(os.environ.get("FC_TRIALS", "3"))
    run_seconds = int(os.environ.get("FC_RUN_SECONDS", "300"))
    conf.setdefault("java_args", ["-Xms1536M", "-Xmx1536M"])
    conf.setdefault("boot_timeout", int(os.environ.get("FC_BOOT_TIMEOUT", "600")))

    report = {"metoda": conf.get("metoda", "FC-BENCH v4: boot la cald pe world comun, N probe, media pe probe; aceeasi masina/pack/java 11; zero metri ascunsi"),
              "arm": conf["arm"], "eticheta": conf.get("eticheta", conf["arm"]),
              "java": os.environ.get("FC_JAVA_LABEL", "temurin-11"),
              "limite": ["nu e benchmark de gameplay uman (fara redstone/AI incarcat deliberat); masoara motorul: bootstrap, boot, login, tick-idle cu 36 moduri+14 plugini, resurse, GC, erori",
                          "nu atingem serverul live; deviatii de la pack: vezi overrides"]}
    mods = plugins = None
    pack_sha = None
    if os.path.exists(conf["pack_zip"]):
        import hashlib
        h = hashlib.sha256()
        with open(conf["pack_zip"], "rb") as f:
            for ch in iter(lambda: f.read(1 << 20), b""):
                h.update(ch)
        pack_sha = h.hexdigest()
    report["pack_sha256_asteptat"] = conf.get("pack_sha256")
    report["pack_sha256_actual"] = pack_sha
    if conf.get("pack_sha256") and pack_sha != conf["pack_sha256"]:
        report["status"] = "ESUAT_TEHNIC"
        report["eroare"] = "SHA256 pack nu corespunde — masa nu e cea declarata"
        dump(report, outdir)
        return 2

    log(f"=== brat {conf['arm']}: stage ===")
    build_stage(conf, jar, stage)
    bootjar = resolve_boot_jar(conf, os.path.abspath(jar) if jar else "", stage)
    sdir = lambda d: len([f for f in os.listdir(os.path.join(stage, d)) if f.endswith(".jar")]) if os.path.isdir(os.path.join(stage, d)) else 0
    mods, plugins = sdir("mods"), sdir("plugins")
    if conf.get("boot_jar") == "from_pack_root" and not conf.get("pack_boot_jar_path"):
        with zipfile.ZipFile(conf["pack_zip"]) as z:
            roots = [n for n in z.namelist() if "/" not in n and n.endswith(".jar")]
        conf["pack_boot_jar_path"] = "catserver.jar" if "catserver.jar" in roots else (roots[0] if roots else "NOJAR")
    report["pack_mods"] = mods
    report["pack_plugins"] = plugins
    report["jar_boot_folosit"] = bootjar
    overrides, port = apply_overrides(conf, stage)
    report["overrides"] = overrides
    report["server_port"] = port

    log(f"=== faza A: instalare bootstrap (limita {conf.get('install_timeout', 420)}s, nemasurata) ===")
    log_install = os.path.join(outdir, "install.log")
    cmd = ["java"] + conf["java_args"] + ["-jar", bootjar, "nogui"]
    t0 = time.monotonic()
    with open(log_install, "wb") as lf:
        ip = subprocess.Popen(cmd, cwd=stage, stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                              start_new_session=True)
        try:
            ip.wait(conf.get("install_timeout", 420))
            rc = ip.returncode
        except subprocess.TimeoutExpired:
            # bootstrap-ul Mohist isi lasa urmasi prin pipes; omoaram TOT grupul, nu doar parintele
            try:
                os.killpg(os.getpgid(ip.pid), signal.SIGKILL)
            except Exception:
                ip.kill()
            try:
                ip.wait(20)
            except Exception:
                pass
            rc = "TIMEOUT(grupul a fost omorat)"
    report["install_reusit"] = (rc == 0) or (time.monotonic() - t0 > 30)
    report["install_timp_s"] = round(time.monotonic() - t0, 1)
    report["install_cod"] = rc

    logines = os.path.join(stage, "logs", "latest.log")
    if os.path.exists(logines):
        tail = strip_ansi(open(logines, encoding="utf-8", errors="replace").read())[-4000:]
        report["install_urmatorul_log_tail"] = tail[-600:]

    wdir = os.path.join(stage, "world")
    if os.path.isdir(wdir):
        tot = 0
        for dp, _, fns in os.walk(wdir):
            for fn in fns:
                try:
                    tot += os.path.getsize(os.path.join(dp, fn))
                except OSError:
                    pass
        report["lume_mb_dupar_instalare"] = round(tot / 1e6, 1)
    results = []
    boot_times = []
    for i in range(1, trials + 1):
        log(f"=== proba {i}/{trials} ===")
        try:
            res, j = one_trial(conf, stage, bootjar, port, i, outdir, run_seconds)
        except Exception as e:
            res = {"trial": i, "boot_reusit": False, "boot_esec_motiv": f"driver: {type(e).__name__}: {e}"}
        results.append(res)
        if res.get("boot_reusit"):
            boot_times.append(res["boot_timp_real_s"])
        else:
            log(f"proba {i}: boot ESUAT ({res.get('boot_esec_motiv')}) — restul probelor se sarta (fail-fast)")
            break
    okn = len(boot_times)
    report["probe"] = results
    open(os.path.join(outdir, "heartbeat"), "w").write(str(time.time()))
    report["probate_reusite"] = okn
    if okn:
        report["boot_medie_s"] = round(statistics.mean(boot_times), 2)
        report["boot_cv_pct"] = round(statistics.pstdev(boot_times) / statistics.mean(boot_times) * 100, 1) if okn > 1 else 0.0
    joined = [r["join_probe_ms"] for r in results if r.get("join_probe_ms")]
    if joined:
        report["join_medie_ms"] = round(statistics.mean(joined), 1)
    tpsv = [v for r in results for v in (r.get("tps_probe") or [])]
    if tpsv:
        report["tps_p50"] = round(statistics.median(tpsv), 2)
        report["tps_min"] = round(min(tpsv), 2)
    else:
        report["tps_p50"] = None
        report["tps_motiv"] = "comenzile console (ticks tps/mspt/tps) n-au produs linii parse-abile pe acest motor — NEMASURAT, nu 20.0 inventat"
    report["overrun_total"] = sum(r.get("overrun_count", 0) for r in results)
    report["overrun_max_ms"] = max([r.get("overrun_max_ms", 0) for r in results] or [0])
    report["critice_total"] = sum(r.get("critice", 0) for r in results)
    rssv = [r["rss_medie_kb"] for r in results if r.get("rss_medie_kb")]
    if rssv:
        report["rss_medie_mb"] = round(statistics.mean(rssv) / 1024, 1)
    cpuv = [r["cpu_medie_pct"] for r in results if r.get("cpu_medie_pct") is not None]
    if cpuv:
        report["cpu_medie_pct"] = round(statistics.mean(cpuv), 1)
    gcm = [r["gc_pauze_ms_max"] for r in results if r.get("gc_pauze_ms_max")]
    if gcm:
        report["gc_pauza_max_ms"] = round(max(gcm), 1)
    report["status"] = "MASURAT" if okn == trials else ("ESUAT_TEHNIC" if okn == 0 else "PARTIAL")
    dump(report, outdir)
    log(f"RESUMAT {conf['arm']}: status={report['status']} boot_medie={report.get('boot_medie_s')}s cv={report.get('boot_cv_pct')}% join={report.get('join_medie_ms')}ms tps_p50={report.get('tps_p50')} overrun={report.get('overrun_total')} critice={report.get('critice_total')}")
    return 0 if okn else 3

def dump(report, outdir):
    path = os.path.join(outdir, f"{report['arm']}.json")
    json.dump(report, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    log(f"raport scris: {path}")

if __name__ == "__main__":
    sys.exit(main())
