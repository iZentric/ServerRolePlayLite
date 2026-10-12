#!/usr/bin/env python3
"""Descoperă candidații hibrid 1.16.5 și îi predă scenei ca specific verbatim.

Fiecare candidat are o listă de URL-uri oficiale posibile; le testăm cu HEAD din
runner (unde rețeaua e liberă) și păstrăm doar primul care răspunde 200. Fără un
URL verificat, candidatul intră în raport ca „sursă de neatins” — nu ca eșec de
performanță și, oricum, nu ca număr inventat.
"""
import argparse
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

USER_AGENT = "cuantic-ladder/1.0 (verificare sursa oficiala; GitHub Actions)"

CANDIDATES = {
    "Mohist 1.16.5-1237": {
        "licence": "GPL-3.0",
        "urls": [
            "https://repo1.maven.org/maven2/com/mohistmc/mohist/1.16.5-1237/mohist-1.16.5-1237.jar",
            "https://maven.mohistmc.com/com/mohistmc/mohist/1.16.5-1237/mohist-1.16.5-1237.jar",
        ],
        "note": "Maven Central este sursa indicata de Artifice; oglinda proprie a proiectului e fallback",
    },
    "Magma 1.16.5-36.2.39-c1c5a946": {
        "licence": "GPL-3.0 (de reconfirmat pe tag)",
        "urls": [
            "https://git.magmafoundation.org/api/v4/projects/8/packages/maven/org/magmafoundation/"
            "Magma/1.16.5-36.2.39-c1c5a946/Magma-1.16.5-36.2.39-c1c5a946-server.jar",
            "https://repo.magmafoundation.org/releases/org/magmafoundation/Magma/"
            "1.16.5-36.2.39-c1c5a946/Magma-1.16.5-36.2.39-c1c5a946-server.jar",
        ],
        "note": "proiectul 1.16.x e marcat arhivat; pagina principala a dat 522 la 12 oct 2026",
    },
    "LoliServer 1.16.5": {
        "licence": "GPL-3.0 / LGPL-3.0 în dezacord între oglinzi",
        "urls": [],
        "note": "repository-ul GitHub Loli-Server/LoliServer a intors 404 (stins); "
                "nu luam binare de pe oglinzi neoficiale",
    },
}


def reachable(url, timeout=25):
    """GET cu Range pe primul octet: multe repo-uri Maven raspund gresit la HEAD."""
    request = urllib.request.Request(url, method="GET",
                                     headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            resp.read(2)
            return resp.status in (200, 206)
    except (urllib.error.URLError, OSError, ValueError):
        return False


def discover(only=None, offline=False, probe_timeout=25, probe=True):
    """-> (spec pentru scripts/cuantic_ladder.py, listă de detaliuri pentru raport)."""
    selected = [(name, cfg) for name, cfg in CANDIDATES.items()
                if not only or only.lower() in name.lower()]
    entries, parts = [], []
    for name, cfg in selected:
        entry = {"name": name, "licence": cfg["licence"], "note": cfg["note"],
                 "tried": cfg["urls"], "url": None, "status": "fără sursă oficială"}
        for url in cfg["urls"]:
            if not probe:
                # fara sondaj pastram URL-ul oficial ca atare; scaderea il verifica
                # cu SHA real si un esec de retea apare ca ESUAT, nu ca verdict.
                entry.update(url=url, status="nesondat (verificare in descărcare)")
                break
            if offline:
                entry["status"] = "rețea dezactivată (mod offline)"
                break
            if reachable(url, timeout=probe_timeout):
                entry.update(url=url, status="accesibil (HEAD 200)")
                break
            entry["status"] = "niciun URL oficial nu a răspuns 200"
        entries.append(entry)
        parts.append(f"{name}|{entry['url'] or ''}||{cfg['licence']}" if entry["url"]
                     else f"{name} ({entry['status']}; {entry['note']})")
    return ",".join(parts), entries


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="cale unde se scrie JSON-ul cu detaliile descoperirii")
    ap.add_argument("--only", default=None)
    ap.add_argument("--offline", action="store_true", help="nu atinge rețeaua (pentru teste)")
    ap.add_argument("--no-probe", action="store_true", help="păstrează URL-urile fără sondaj; scara le verifică la descărcare")
    args = ap.parse_args(argv)
    spec, entries = discover(only=args.only, offline=args.offline, probe=not args.no_probe)
    print(spec)          # prima linie = spec-ul, citit de workflow
    if args.out:
        Path(args.out).write_text(json.dumps({"candidates": entries, "spec": spec},
                                             ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0            # descoperirea nu e niciodată un verdict: eșecul de rețea e doar înregistrat


if __name__ == "__main__":
    sys.exit(main())
