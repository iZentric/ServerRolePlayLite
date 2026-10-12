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
                      r"playerdata|stats|resourcepacks|patchy|libraries|versions|backups|"
                      r"\.archive-unpack)/", re.I)
SKIP_DIR_TAIL = re.compile(r"/(data|world|world_nether|world_the_end)/", re.I)
ROOT_ONLY_CONFIG = re.compile(r"^[^/]+\.(yml|yaml|properties|conf|cfg|toml|ini|txt|json)$", re.I)
KEEP_CONFIG = re.compile(r"\.(yml|yaml|properties|conf|cfg|toml|ini|json|txt)$", re.I)
SKIP_NAME = re.compile(r"(level\.dat|session\.lock|usercache|banned-|whitelist|ops\.json|permissions\.yml"
                       r"|new text document|notes?\.txt|licen[cs]e[-_]?key|\.pem$|id_rsa"
                       r"|vials|viabackwards|vault|luckperms|h2\.mv.db|\.mca$|\.jar$|\.zip$|\.gz$"
                       r"|secrets|password|token|api-key|private)", re.I)
NESTED = re.compile(r"\.(tar\.gz|tgz|tar|zip|rar)$", re.I)
LOG_TAIL_BYTES = 120_000
TAIL_BYTES = 400_000          # orice alt fisier text care nu incape integral: doar coada
MAX_FILE = 2_000_000
MAX_TOTAL = 25_000_000        # plafon de text publicat per server, ca sa nu umflam repo-ul


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
    else:  # .rar si restul, intai 7zip, apoi unar (7z din p7zip-full nu stie rar5)
        try:
            subprocess.run(["7z", "x", "-y", f"-o{dest}", str(archive)], check=False)
        except FileNotFoundError:
            pass
        if not any(dest.iterdir()):
            if shutil.which("unar"):
                subprocess.run(["unar", "-quiet", "-force-overwrite", "-output-directory",
                                str(dest), str(archive)], check=False)
                # unar creeaza un folder cu numele arhivei: urca continutul cu un nivel
                for sub in [p for p in dest.iterdir() if p.is_dir()]:
                    for child in sub.iterdir():
                        child.rename(dest / child.name)
                    if not any(sub.iterdir()):
                        sub.rmdir()
            else:
                print("nici 7z, nici unar nu sunt instalate: nu pot dezarhiva", file=sys.stderr)


def _tail(src: Path, dst: Path, limit: int = LOG_TAIL_BYTES) -> int:
    with open(src, "rb") as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(max(0, size - limit))
        data = f.read()
    dst.write_bytes(data)
    return len(data)


SECRET_SCAN = re.compile(r"((licen[cs]e|api[_-]?key|token|secret|passw)[a-z_]*\W{0,3}[=:]\W{0,2}[A-Za-z0-9+/_=.-]{12,}"
                         r"|(?:^|\n)\s*#?\s*(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{20,}\s*(?:\n|$))",
                         re.I | re.M)


def looks_secret(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            blob = f.read(65_536)
    except OSError:
        return False
    try:
        text = blob.decode("utf-8", "ignore")
    except Exception:
        return False
    return bool(SECRET_SCAN.search(text))


SCRUB = re.compile(r"((?:licen[cs]e|api[_-]?key|auth[_-]?token|token|secret|passw)[a-z_-]*\W{0,3}[=:]\s?['\"]?)"
                   r"([A-Za-z0-9+/_=.:-]{12,})", re.I)
LONGKEY = re.compile(r"(?:^|\n)(\s*#?\s*)((?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{20,})(?=\s*(?:\n|$))")


def scrub(path: Path) -> None:
    """Redacteaza cheile din loc, nu arunca fisierul: configul e la fel de util fara credential."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return
    out = SCRUB.sub(lambda m: m.group(1) + "<REDACTAT>", text)
    out = LONGKEY.sub(lambda m: m.group(1) + "<KEY-REDACTAT>", out)
    if out != text:
        path.write_text(out, encoding="utf-8")


def keep_body(rel: str) -> str:
    """Varianta de drum care trece de keep(); gol daca nu vrem fisierul."""
    for b in _candidates(rel):
        if keep(b):
            return b
    return ""


def _candidates(rel: str) -> list[str]:
    """Atat drumul integral cat si cel fara primul component (folderul de wrap al arhivei)."""
    out = [rel.strip("/")]
    stripped = re.sub(r"^[^/]+/", "", rel).strip("/")
    if stripped and stripped != out[0]:
        out.append(stripped)
    return out


def keep(rel: str) -> bool:
    """Decizia e pe drumul din arhiva, ca sa mearga si fara extragere."""
    for body in _candidates(rel):
        if SKIP_NAME.search(body):
            return False
        if SKIP_DIR.search("/" + body) or SKIP_DIR_TAIL.search("/" + body):
            return False
        if re.search(r"\.(jar|mca|db|zip|gz|tar|dat|dat_old|png|jpg|pdf|bin)$", body, re.I):
            return False
        if ROOT_ONLY_CONFIG.match(body):
            return True
        if re.search(r"\.(log|txt|sk)$", body, re.I):           # loguri/cozi de chat/scrieri Skript
            return True
        if re.match(r"^(plugins|mods|config|bungee|velocity)/", body) and \
           KEEP_CONFIG.search(body) and "/playerdata/" not in "/" + body:
            return True                                          # configurile din plugins/ sunt aurul
    return False


def collect(root: Path, out: Path, budget: int = MAX_TOTAL) -> dict:
    (out / "config").mkdir(parents=True, exist_ok=True)
    kept, skipped = [], {"teren": 0, "suspect": 0, "mare": 0, "binar": 0}
    total_bytes = 0
    cand = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        body = keep_body(rel)
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
        if size > MAX_FILE and not re.search(r"\.(log|txt|sk|yml|yaml|properties|cfg|toml|json)$", body, re.I):
            skipped["mare"] += 1
            continue
        cand.append((body, size))
    # latime inainte de adancime: maxim 6 fisiere pe grup (dir-parinte), apoi buget pe prioritati
    per_group: dict[str, list[tuple[str, int]]] = {}
    for body, size in cand:
        g = body.rsplit("/", 2)[0] if body.count("/") >= 2 else "(radacina)"
        per_group.setdefault(g, []).append((body, size))
    picked_list: list[tuple[int, int, str, int]] = []
    for g, rows in per_group.items():
        rows.sort(key=lambda r: -r[1])
        for pr_i, (body, size) in enumerate(rows[:6]):
            prio = 0 if "/" not in body else (1 if re.search(r"\.(log|txt|sk)$", body, re.I) else 2)
            picked_list.append((prio, pr_i, body, size))
    picked_list.sort(key=lambda t: (t[0], -t[3], t[2]))
    for prio, _i, body, size in picked_list:
        if total_bytes >= budget:
            skipped["mare"] += 1
            continue
        dst = out / "config" / body.replace("/", "__")
        try:
            if re.search(r"\.(log)$", body, re.I) or size > MAX_FILE:
                n = _tail(p, dst)
            elif size > MAX_FILE:
                n = _tail(p, dst, TAIL_BYTES)
            else:
                shutil.copy2(p, dst)
                n = size
            if looks_secret(dst):
                scrub(dst)
                if looks_secret(dst):
                    dst.unlink(missing_ok=True)
                    skipped["suspect"] += 1
                    continue
            total_bytes += n
            kept.append({"file": body, "bytes": size})
        except OSError:
            continue
    return {"kept": kept, "skipped": skipped, "written": total_bytes}


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
    rows = list(_listing(archive))
    skipped = {"teren": 0, "suspect": 0, "mare": 0, "binar": 0}
    kept_all, written = [], 0

    def absorb(r: Path, budget: int) -> int:
        nonlocal rows, skipped, kept_all, written
        picked = collect(r, out, budget)
        kept_all.extend(picked["kept"])
        for k in skipped:
            skipped[k] += picked["skipped"][k]
        written += picked["written"]
        return picked["written"]

    used = absorb(root, MAX_TOTAL)
    # arhive in arhiva: backup-urile de server pun de regula un *.tar.gz in interior
    nested = [q for q in sorted(root.rglob("*"))
              if q.is_file() and NESTED.search(q.name) and q.stat().st_size <= 1_600_000_000][:6]
    for n_i, n in enumerate(nested):
        sub = root / ("_sub_%d" % n_i)
        try:
            extract(n, sub)
            rows += _listing(n)
            used += absorb(sub, max(0, MAX_TOTAL - used))
        finally:
            shutil.rmtree(sub, ignore_errors=True)

    inv = inventory(archive, out, rows)
    n_cfg = len(list((out / "config").glob("*")))
    report = {"archive": archive.name, "bytes": archive.stat().st_size,
              "listing": inv["files"], "uncompressed_bytes": inv["bytes"],
              "groups_top": dict(inv["top"]), "nested": [n.name for n in nested],
              "config_files_kept": n_cfg, "config_bytes": used,
              "skipped": skipped, "files": [k["file"] for k in kept_all][:500]}
    (out / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
