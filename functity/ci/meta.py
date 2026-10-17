#!/usr/bin/env python3
"""Provenien completa a unui build FunCity: meta.py <dir-fc> <build_id> <pin> <repo>.
Scrie JSON pe stdout. Fiecare camp = citit din artefact, nu din memorie."""
import glob, hashlib, json, os, subprocess, sys

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return "N/A"

def main():
    fc, build, pin, repo = sys.argv[1:5]
    jars = sorted(glob.glob(os.path.join(fc, "FunCity-*.jar")))
    patches_applied, rejected = [], ""
    rej = os.path.join(fc, "patch-rejected.txt")
    if os.path.exists(rej):
        rejected = open(rej, encoding="utf-8").read()[:500]
    pdir = os.path.join(repo, "functity", "patches")
    for pt in sorted(glob.glob(os.path.join(pdir, "*.patch"))):
        patches_applied.append({"fisier": os.path.basename(pt),
                                "sha256": hashlib.sha256(open(pt, "rb").read()).hexdigest()[:16]})
    jar = jars[0] if jars else None
    manifest_sig = ""
    if jar:
        mf = sh(f"unzip -p {jar} META-INF/MANIFEST.MF")
        manifest_sig = "MOHIST (ServerLaunchArgs prezent)" if "ServerLaunchArgs" in mf else "FARA SEMNATURA MOHIST"
    print(json.dumps({
        "produs": "FunCity — motor propriu pe baza Mohist 1.16.5",
        "build": build or "b0",
        "baza_upstream": {"repo": "MohistMC/Mohist", "branch": "1.16.5", "commit": pin,
                          "licenta": "GPL-3.0 (baza); derivatele publicate raman sub licencia proiectului"},
        "buildfix_aplicate": ["P0b: ForgeGradle 6.0.16 pin", "P0c/P0d: reparații pipeline (functity/buildfix)"],
        "patchuri_proprii": patches_applied,
        "patchuri_respinse": rejected,
        "jar": os.path.basename(jar) if jar else None,
        "jar_sha256": sh(f"sha256sum {jar} | cut -d' ' -f1") if jar else None,
        "jar_marime_b": sh(f"stat -c %s {jar}") if jar else None,
        "semnatura_manifest": manifest_sig or "niciun jar colectat",
        "gradle_exit": (sh(f"grep -o 'gradle exit: [0-9]*' {os.path.join(fc, 'BUILD-LOG.txt')} | tail -1") or "N/A"),
        "data_utc": sh("date -u '+%F %T'"),
        "masina_build": "ubuntu-24.04 hosted (GitHub runner)",
        "java": sh("java -version 2>&1 | head -1"),
    }, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
