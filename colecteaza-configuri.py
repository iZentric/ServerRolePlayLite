#!/usr/bin/env python3
# Colecteaza DOAR config-urile serverelor de RP — fara date de jucatori, fara seed.
# Ruleaza in folderul parinte al serverelor:   python3 colecteaza-configuri.py
# sau pe liste:                                 python3 colecteaza-configuri.py server1 server2
# Iesi un singur fisier: configuri-rp.tar.gz (plus bucati de 20 MB langa el, daca e mare).
import hashlib
import os
import re
import sys
import tarfile
import gzip
from pathlib import Path

MAX_FILE = 400_000          # 400 kB per fisier de config: orice e mai mare nu e config
LOG_TAIL = 20_000           # linii, din loguri curatate
SUFFIX = {".properties", ".yml", ".yaml", ".toml", ".conf", ".cfg", ".ini", ".txt", ".json"}
SKIP_NAMES = {
    "usercache.json", "ops.json", "whitelist.json", "banned-players.json", "banned-ips.json",
    "permissions.yml", "server.log", "eula.txt", "bukkit.yml.tmp",
}
SKIP_SUBSTR = ("seed", "rcon", "token", "secret", "password", "api", "private", "keystore",
               "node_modules", "patchy", "launcher_profiles", "servers.json", "realms")
WORLDISH = re.compile(r"^(world|world_|DIM|data|region|entities|advancements|stats|playerdata|"
                      r"level\.dat|session\.lock|icons|resourcepacks|logs/run/backup|backups|crash-reports)", re.I)
IP = re.compile(r"\b\d{1,3}(\.\d{1,3}){3}\b")
UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F-]{20,}\b")
PII = re.compile(r"(?:logged on|logged in|left the game|joined the game).{0,60}", re.I)


def scrub(text):
    text = IP.sub("IP.STRIP", text)
    text = UUID.sub("UUID.STRIP", text)
    return PII.sub("ACTIVITATE.STRIP", text)


def interesting(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root).as_posix()
        parts = [p for p in rel.split("/") if p]
        if any(WORLDISH.match(p) or WORLDISH.match("/".join(parts[:i + 1])) for i, p in enumerate(parts)):
            dirnames[:] = []
            continue
        if any(s in rel.lower() for s in ("backup", "crash-reports", "resourcepack", "patchy")):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not WORLDISH.match(d) and "backup" not in d.lower()]
        for fn in filenames:
            if fn in SKIP_NAMES or any(s in fn.lower() for s in SKIP_SUBSTR):
                continue
            p = Path(dirpath) / fn
            if p.suffix.lower() not in SUFFIX and not re.search(r"\.log(\.gz)?$", fn, re.I):
                continue
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size == 0 or (size > MAX_FILE and not re.search(r"\.log", fn)):
                continue
            yield p, size


def main(argv):
    here = Path.cwd()
    servers = [Path(a) for a in argv[1:]] or [p for p in sorted(here.iterdir()) if p.is_dir()]
    out_dir = here / "configuri-rp"
    if out_dir.exists():
        import shutil
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    manifest = []
    for s in servers:
        if not s.is_dir():
            continue
        tag = re.sub(r"[^A-Za-z0-9._-]", "-", s.name)[:60]
        files = list(interesting(s))
        n_ok = 0
        with tarfile.open(out_dir / f"{tag}.configs.tar", "w:gz") as tf:
            for p, size in files:
                try:
                    arc = f"{tag}/{p.relative_to(s).as_posix()}"
                    tf.add(p, arcname=arc, recursive=False)
                    n_ok += 1
                except (OSError, tarfile.TarError):
                    continue
        # inventar JAR-uri: nume + marime + hash scurt, nu binarul in sine
        lines = []
        for sub in ("mods", "plugins"):
            d = s / sub
            if d.is_dir():
                for j in sorted(d.glob("*.jar")):
                    h = hashlib.sha256()
                    with open(j, "rb") as f:
                        for blk in iter(lambda: f.read(1 << 20), b""):
                            h.update(blk)
                    lines.append(f"{sub}/{j.name}|{j.stat().st_size}|{h.hexdigest()[:16]}")
        (out_dir / f"{tag}.inventar.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        # loguri curatate
        logs = sorted(list(s.glob("logs/latest.log")) + list(s.glob("logs/*.log.gz")),
                      key=lambda p: p.stat().st_mtime, reverse=True)[:2]
        tail = ""
        for lg in logs:
            try:
                data = gzip.open(lg, "rt", errors="replace").read() if lg.suffix == ".gz" \
                    else lg.read_text(errors="replace")
            except OSError:
                continue
            tail += "\n".join(data.splitlines()[-LOG_TAIL:]) + "\n"
        if tail:
            (out_dir / f"{tag}.log.curat.txt").write_text(scrub(tail)[-2_000_000:], encoding="utf-8")
        manifest.append(f"{tag}: {n_ok} fisiere config · {len(lines)} JAR-uri · {len(tail)} caractere log curatat")
        print(manifest[-1])

    if not manifest:
        print("N-am gasit niciun server cu config-uri în acest folder.")
        return 1
    dest = here / "configuri-rp.tar.gz"
    with tarfile.open(dest, "w:gz") as tf:
        for p in sorted(out_dir.iterdir()):
            tf.add(p, arcname=p.name, recursive=False)
    mb = dest.stat().st_size / 1024 / 1024
    print(f"\nGATA: {dest} ({mb:.1f} MB)")
    if mb > 25:
        for i in range(0, int(mb // 20) + 1):
            pass
        import subprocess
        subprocess.run(["split", "-b", "20m", str(dest), str(dest) + ".part-"], check=False)
        print("Am impartit în bucati de 20 MB — trimite-le pe rand, le lipesc eu la loc.")
    print("\nCe NU e în arhiva (deliberat): world*/level.dat (seed), usercache/ops/whitelist/bans (UUID-uri),")
    print("server.log (IP-uri), backup-uri, resourcepacks, JAR-uri în sine (doar inventarul cu hash).")
    print("Verifica-ti singur inainte sa-mi dai fisierul: tar tzf configuri-rp.tar.gz | grep -iE 'world|usercache|level.dat' && echo ATENTIE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
