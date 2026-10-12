#!/usr/bin/env python3
"""RP-INSPECT — trece printr-o arhivă de backup RP și lasă doar ce e util unui motor.

Regulile sunt alese ca să nu miros date de jucători și ca raportul să încapă în repo:
  * INVENTAR: lista completă de fișiere (nume, mărime, data) — „m-am uitat prin tot”,
    fără să copiem totul;
  * CONFIG: only root-level config + mod/plugin inventar + coada de loguri, fără `world/`,
    fără playerdata, fără arhive;
  * tot ce e binar (.jar/.mca/.db/.zip) devine o linie în inventar, nu un fișier extras.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile

# Un drum e "teren" (nu ne intereseaza, oricat de multi .yml ar contine): world*, regiuni,
# inventare de jucatori, plugin-data. Restul e solutia in sine si il citim.
SKIP_DIR = re.compile(r"(^|/)(world|world_[a-z0-9]+|DIM-?\d+|region|entities|poi|advancements|"
                      r"playerdata|stats|resourcepacks|patchy|libraries|versions|backups)/", re.I)
SKIP_DIR_TAIL = re.compile(r"/(data|world|world_nether|world_the_end)/", re.I)
ROOT_ONLY_CONFIG = re.compile(r"^[^/]+\.(yml|yaml|properties|conf|cfg|toml|ini|txt|json)$", re.I)
KEEP_CONFIG = re.compile(r"\.(yml|yaml|properties|conf|cfg|toml|ini|json|txt)$", re.I)
SKIP_NAME = re.compile(r"(level\.dat|session\.lock|usercache|banned-|whitelist|ops\.json|permissions\.yml"
                       r"|vials|viabackwards|vault|luckperms|h2\.mv.db|\.mca$|\.jar$|\.zip$|\.gz$"
                       r"|secrets|password|token|api-key|private)", re.I)
LOG_TAIL_BYTES = 120_000
MAX_FILE = 2_000_000


def _listing(archive: Path) -> list[tuple[str, int]]:
    name = archive.name.lower()
    if name.endswith((".tar.gz", ".tgz", ".tar")):
        out = subprocess.run(["tar", "-tvf", str(archive)], capture_output=True, text=True).stdout
        rows = []
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 6:
                rows.append((" ".join(parts[5:]), int(parts[2]) if parts[2].isdigit() else 0))
        return rows
    subprocess.run(["7z", "l", "-slt", str(archive)], capture_output=True, text=True)
    out = subprocess.run(["7z", "l", "-y", str(archive)], capture_output=True, text=True).stdout
    rows, started = [], False
    for line in out.splitlines():
        if re.match(r"^-----", line):
            started = True
            continue
        if not started or not line.strip():
            continue
        m = re.match(r"(\S+)\s+(\S+)\s+(\d{4}-\S+)\s+(.*)", line)
        if m:
            size = int(m.group(2)) if m.group(2).isdigit() else 0
            rows.append((m.group(4).strip(), size))
    return rows


def extract(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    name = archive.name.lower()
    if name.endswith((".tar.gz", ".tgz")):
        subprocess.run(["tar", "-xzf", str(archive), "-C", str(dest)], check=False)
    elif name.endswith(".tar"):
        subprocess.run(["tar", "-xf", str(archive), "-C", str(dest)], check=False)
    elif name.endswith(".zip"):
        subprocess.run(["unzip", "-q", "-o", str(archive), "-d", str(dest)], check=False)
    else:  # .rar si restul, prin 7zip
        subprocess.run(["7z", "x", "-y", f"-o{dest}", str(archive)], check=False)


def _tail(src: Path, dst: Path) -> None:
    with open(src, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - LOG_TAIL_BYTES))
        data = f.read()
    dst.write_bytes(data)


def keep(rel: str) -> bool:
    """Decizia e pe drumul din arhiva, ca sa mearga si fara extragere."""
    body = re.sub(r"^[^/]+/", "", rel)
    if SKIP_NAME.search(body):
        return False
    if SKIP_DIR.search("/" + body) or SKIP_DIR_TAIL.search("/" + body):
        return False
    if re.search(r"\.(jar|mca|db|zip|gz|tar|dat|dat_old|png|jpg|pdf|bin)$", body, re.I):
        return False
    if ROOT_ONLY_CONFIG.match(body):
        return True
    if re.search(r"\.(log)$", body, re.I):                      # loguri: doar coada, dar le vrem
        return True
    if re.match(r"^(plugins|mods|config|bungee|velocity)/", body) and \
       KEEP_CONFIG.search(body) and "/playerdata/" not in "/" + body:
        return True                                              # configurile din plugins/ sunt aurul
    return False


def collect(root: Path, out: Path) -> dict:
    (out / "config").mkdir(parents=True, exist_ok=True)
    kept, skipped = [], {"teren": 0, "suspect": 0, "mare": 0, "binar": 0}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        body = re.sub(r"^[^/]+/", "", rel)
        try:
            size = p.stat().st_size
        except OSError:
            continue
        if SKIP_NAME.search(body):
            skipped["suspect"] += 1
            continue
        if not keep(rel):
            if re.search(r"\.(jar|mca|db|zip|gz|dat)$", body, re.I):
                skipped["binar"] += 1
            elif SKIP_DIR.search("/" + body) or SKIP_DIR_TAIL.search("/" + body):
                skipped["teren"] += 1
            elif size > MAX_FILE:
                skipped["mare"] += 1
            else:
                skipped["teren"] += 1
            continue
        if size > MAX_FILE and not re.search(r"\.log$", body, re.I):
            skipped["mare"] += 1
            continue
        dst = out / "config" / body.replace("/", "__")
        try:
            if re.search(r"\.log$", body, re.I):
                _tail(p, dst)
            else:
                shutil.copy2(p, dst)
            kept.append({"file": body, "bytes": size})
        except OSError:
            continue
    return {"kept": kept, "skipped": skipped}


def inventory(archive: Path, out: Path, listing: list[tuple[str, int]]) -> dict:
    lines, total = [], 0
    for name, size in listing:
        total += size
        lines.append(f"{size}|{name}")
    (out / "inventar.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    groups: dict[str, dict] = {}
    for name, size in listing:
        key = re.sub(r"^[^/]+/", "", name).split("/")[0] or "(raza)"
        g = groups.setdefault(key, {"count": 0, "bytes": 0})
        g["count"] += 1
        g["bytes"] += size
    return {"files": len(listing), "bytes": total, "top": sorted(
        groups.items(), key=lambda kv: -kv[1]["bytes"])[:25]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--archive", required=True)
    ap.add_argument("--extract-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    archive, root, out = Path(a.archive), Path(a.extract_dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    extract(archive, root)
    listing = _listing(archive)
    inv = inventory(archive, out, listing)
    picked = collect(root, out)
    n_cfg = len(list((out / "config").glob("*")))
    with tarfile.open(out / "configuri.tar.gz", "w:gz") as tf:
        for p in sorted((out / "config").glob("*")):
            tf.add(p, arcname=p.name, recursive=False)
    size_cfg = out.joinpath("configuri.tar.gz").stat().st_size if (out / "configuri.tar.gz").exists() else 0
    report = {"archive": archive.name, "bytes": archive.stat().st_size,
              "listing": inv["files"], "uncompressed_bytes": inv["bytes"],
              "groups_top": dict(inv["top"]), "config_files_kept": n_cfg,
              "config_bytes": size_cfg, "skipped": picked["skipped"],
              "files": [k["file"] for k in picked["kept"]][:400]}
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
