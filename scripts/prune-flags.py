#!/usr/bin/env python3
"""CUANTIC PRUNE-FLAGS — taie din setul de flaguri JVM tot ce NU cunoaste Java de pe server.

De ce exista: kitul Aikar e scris pentru OpenJDK 11. Cativa flaguri (G1ConcRSHotCardLimit,
UseFastUnorderedTimeStamps, NmethodSweepActivity...) au DISPARUT in 15/17, iar JVM-ul refuza
SA PORNEASCA DELOC cu „Unrecognized VM option". Pe Cloud Shell / VM rulam Temurin 17 => server mort.
Regula: niciun build nu publica flaguri neverificate pe ACELASI Java pe care ruleaza serverul.

Rulat in CI (build-lite.yml) pe Java 17; scrie deploy/jvm-flags-17.txt, folosit apoi de build_lite.py.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "scripts", "build_lite.py")
OUT = os.path.join(ROOT, "deploy", "jvm-flags-17.txt")


def main():
    java = os.environ.get("JAVA", "java")
    src = open(BUILD, encoding="utf-8").read()
    m = re.search(r"AIKAR_FLAGS = \((.*?)\n\)", src, re.S)
    if not m:
        print("nu gasesc AIKAR_FLAGS in build_lite.py")
        return 1
    flags = eval("(" + m.group(1) + ")").split()  # noqa: S307 - fisierul nostru, literal controlat
    try:
        ver = subprocess.run([java, "-version"], capture_output=True, text=True)
        print("java:", (ver.stderr or ver.stdout).splitlines()[0])
    except OSError as e:
        print("java indisponibil in CI:", e)
        return 1

    dropped, unlock_added = [], False
    for _ in range(60):
        r = subprocess.run([java] + flags + ["-version"], capture_output=True, text=True)
        if r.returncode == 0:
            break
        err = (r.stderr or "") + (r.stdout or "")
        mo = (re.search(r"Unrecognized VM option '([^']+)'", err)
              or re.search(r"Cannot specify VM option '([^']+)'", err)
              or re.search(r"VM option '([^']+)' is experimental", err))
        if not mo:
            print("eroare neasteptata la validare:\n" + err[:600])
            break
        raw = mo.group(1)
        if "experimental" in err and not unlock_added:
            # nu aruncam flagul: mai intai il deblocam
            flags.insert(0, "-XX:+UnlockExperimentalVMOptions")
            unlock_added = True
            print("adaugat: -XX:+UnlockExperimentalVMOptions (pt", raw + ")")
            continue
        bad = raw.split("=")[0]
        keep = [f for f in flags if not re.match(r"^-XX:[+-]?" + re.escape(bad) + r"(=.*)?$", f)]
        if len(keep) == len(flags):
            print("nu pot elimina „" + bad + "” (nu e in lista) — ma opresc:", err[:200])
            break
        print("taiat: " + bad)
        dropped.append(bad)
        flags = keep

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# generat de scripts/prune-flags.py in CI, pe Java 17 (nu ghicit)\n")
        f.write("\n".join(flags) + "\n")
    print("OK: %d flaguri validate, %d taiate" % (len(flags), len(dropped)))
    if dropped:
        print("eliminate:", ", ".join(dropped))
    return 0 if flags else 1


if __name__ == "__main__":
    sys.exit(main())
