#!/usr/bin/env python3
"""SCARA CUANTIC — transforma un JAR candidat din „NEAVĂGAT” în număr măsurat.

Rulează NUMAI pe un runner GitHub (ubuntu-latest), niciodată pe serverul live și
niciodată dintr-un sandbox fără rețea. Facem doi pași mici și verificați:

  1. DESCĂRCARE + SHA  — candidat autentic 1.16.5, hash consemnat, licență notată;
  2. SMOKE pe 36/14    — același pack, înlocuit doar motorul; dacă nu ajunge la
                         `Done`, e INCOMPATIBIL (fără scor), nu „mai lent”;
  3. A/B cu N probe     — doar pentru candidații care au pornit; mediane + plaja
                         din interiorul brațului, ca să se vadă dacă diferența e
                         mai mare decât zgomotul.

Verdictul public îl dă `scripts/cuantic_tenx_gate.py`: fără clienți Forge confirmați
în `/list` rămâne NEMĂSURAT, oricât de bune ar părea cifrele sintetice.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

JAR = "CatServer-1.16.5-1d8d6313-server.jar"   # numele fix folosit de scripturile de pornire
EXPECTED_MODS = 36
EXPECTED_PLUGINS = 14
MIN_TRIALS = 3
USER_AGENT = "cuantic-ladder/1.0 (benchmark reproductibil; GitHub Actions)"


# ---------------------------------------------------------------- candidat + rețea
def candidates_from_spec(spec):
    """`nume|url[|sha256][|licenta]` -> listă de dicționari. Fără URL = fără descărcare."""
    out = []
    for item in [raw.strip() for raw in spec.split(",") if raw.strip()]:
        parts = [p.strip() for p in item.split("|")]
        name, url = parts[0], (parts[1] if len(parts) > 1 else "")
        out.append({"name": name, "url": url,
                    "sha256": parts[2].lower() if len(parts) > 2 and parts[2] else None,
                    "licence": parts[3] if len(parts) > 3 and parts[3] else "neverificată"})
    return out


def maven_versions(group_artifact):
    """Lista de versiuni publicate de Maven Central (doar din runner, unde e rețea)."""
    url = f"https://repo1.maven.org/maven2/{group_artifact.replace('.', '/')}/maven-metadata.xml"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}),
                                timeout=30) as resp:
        text = resp.read().decode("utf-8", "replace")
    return re.findall(r"<version>([^<]+)</version>", text)


def download(url, dest, expected_sha=None):
    """Descarcă într-un fișier nou și îl aruncă imediat dacă SHA-ul nu se potrivește."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=180) as resp, dest.open("wb") as fh:
        shutil.copyfileobj(resp, fh)
    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    if expected_sha and sha != expected_sha.lower():
        dest.unlink(missing_ok=True)
        raise ValueError(f"SHA-256 nu se potrivește: {sha} != {expected_sha}")
    return sha


# ---------------------------------------------------------------- împachetare
def pack_inventory(pack):
    with zipfile.ZipFile(pack) as z:
        names = [n for n in z.namelist() if n.endswith(".jar")]
        mods = [n for n in names if n.startswith("mods/") and n.count("/") == 1]
        plugins = [n for n in names if n.startswith("plugins/") and n.count("/") == 1]
        roots = [n for n in names if "/" not in n]
    return mods, plugins, roots


def assert_baseline(pack):
    mods, plugins, roots = pack_inventory(pack)
    if len(mods) != EXPECTED_MODS or len(plugins) != EXPECTED_PLUGINS or JAR not in roots:
        raise ValueError(f"pack-ul nu e baseline-ului așteptat: {len(mods)}/{len(plugins)} {roots}")
    return {"mods": len(mods), "plugins": len(plugins),
            "pack_sha256": hashlib.sha256(pack.read_bytes()).hexdigest()}


def replace_jar(dest, candidate_jar):
    """Copie izolat + motor înlocuit. Atât: niciun mod tăiat, nicio configurație nouă."""
    jar = dest / JAR
    original = hashlib.sha256(jar.read_bytes()).hexdigest()
    shutil.copyfile(candidate_jar, jar)
    return {"baseline_jar_sha256": original,
            "candidate_jar_sha256": hashlib.sha256(jar.read_bytes()).hexdigest()}


# ---------------------------------------------------------------- verdict
def _arm(rows, key):
    values = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    if not values:
        return None
    return {"values": values, "count": len(values),
            "median": round(statistics.median(values), 3),
            "within_arm_range": round(max(values) - min(values), 3)}


METRIC_KEYS = (("rss_steady_mib", "rss_steady_median_mb"),
               ("cpu_steady_s", "cpu_seconds_steady_after_55s"),
               ("p95_steady_ms", "p95_ms"),
               ("boot_done_s", "boot_done_s"))


def summarise(baseline, candidate, min_trials=MIN_TRIALS):
    """Același limbaj ca rapoartele commit-uite: medii, plajă și un verdict timid."""
    state = {"baseline_trials": len(baseline), "candidate_trials": len(candidate),
             "min_trials": min_trials}
    if len(candidate) < min_trials or len(baseline) < min_trials:
        state["verdict"] = "NEMĂSURAT"
        state["reason"] = (f"brațele au {len(baseline)} / {len(candidate)} probe valide; "
                           f"poarta cere minimum {min_trials} pe braț")
        return state
    metrics = {}
    for name, key in METRIC_KEYS:
        a, b = _arm(baseline, key), _arm(candidate, key)
        if not a or not b:
            continue
        floor = max(a["within_arm_range"], b["within_arm_range"])
        delta = round(b["median"] - a["median"], 3)
        metrics[name] = {"baseline": a, "candidate": b, "delta": delta,
                         "noise_floor": floor, "above_noise": abs(delta) > floor}
    state["metrics"] = metrics
    if not metrics:
        state["verdict"] = "INCOMPLET"
        state["reason"] = "niciuna dintre măsurile comune nu e prezentă în ambele brațe"
        return state
    worse = [k for k, v in metrics.items() if v["above_noise"] and v["delta"] > 0]
    if worse:
        state["verdict"] = "RESPINS"
        state["reason"] = ("peste zgomot, mai rău la: " + ", ".join(sorted(worse))
                           + ". Pragul e all-or-nothing: o singură regresie respinge candidatul.")
    else:
        state["verdict"] = "PARITATE_OBSERVATĂ"
        state["reason"] = ("niciun braț nu a pierdut peste plaja de zgomot a aceluiași JAR; "
                           "asta nu e dovadă de câștig și nu justifică înlocuirea binarului live")
    state["limits"] = ("sintetic, fără jucători: nu demonstrează login cu client Forge, vehicule, "
                       "supraviețuire sau FPS. Verdictul public îl dă scripts/cuantic_tenx_gate.py")
    return state


def run_gate(payload_path):
    """Păstrăm poarta ca autoritate separată, nu o imităm aici."""
    gate = Path(__file__).with_name("cuantic_tenx_gate.py")
    try:
        proc = subprocess.run([sys.executable, str(gate), str(payload_path)],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:  # noqa: BLE001
        return {"exit": 1, "verdict": "NEMĂSURAT", "reason": f"poarta nu a putut fi rulat: {exc}"}
    try:
        out = {"exit": proc.returncode, **(json.loads(proc.stdout or "{}"))}
    except ValueError:
        out = {"exit": proc.returncode, "reason": "ieșirea porții nu e JSON valid"}
    out.setdefault("verdict", "NEMĂSURAT")
    if out["exit"] != 0 and out["verdict"] == "NEMĂSURAT":
        out.setdefault("reason", "poarta a refuzat afirmația")
    return out


# ---------------------------------------------------------------- execuție
def boot_one(workdir, label, report_dir, ticket_workload=True):
    """Un singur pornit izolat, prin aceleași unelte ca rapoartele commit-uite."""
    try:
        import engine_ab
    except ImportError:  # runner fără checkout complet? nu înscena un rezultat
        return {"label": label, "valid": False, "error": "engine_ab indisponibil"}
    return engine_ab.run(label, workdir, report_dir, ticket_workload=ticket_workload)


def smoke_boot(workdir, output):
    import engine_lab
    engine_lab.BOOT_TIMEOUT = 300
    return engine_lab.smoke(Path(workdir), Path(output))


def ladder(spec, pack, out, trials=MIN_TRIALS, do_ab=True):
    out.mkdir(parents=True, exist_ok=True)
    try:
        baseline = assert_baseline(pack)
    except OSError as exc:
        raise SystemExit(f"pack inexcesibil: {exc}") from exc
    result = {"method": "scară CUANTIC: descărcare cu SHA, smoke pe pack identic 36/14, "
                        "A/B sintetic cu N probe pe braț, pe un runner GitHub izolat",
              "limits": "nu ating serverul live; nu declară compatibilitate cu clientul modat; "
                        "un motor care nu pornește e INCOMPATIBIL, nu mai lent",
              "baseline_pack": baseline, "candidates": {}}
    for cand in candidates_from_spec(spec):
        row = {"url": cand["url"], "licence_declared": cand["licence"], "sha256_expected": cand["sha256"]}
        result["candidates"][cand["name"]] = row
        stage = out / re.sub(r"[^A-Za-z0-9_.-]", "-", cand["name"].lower())
        stage.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(pack) as z:
            z.extractall(stage)
        try:
            if not cand["url"]:
                raise ValueError("fără URL de descărcare → candidat neidentificat, nu e scor")
            jar = stage / "candidate.jar"
            row["sha256_actual"] = download(cand["url"], jar, cand["sha256"])
            row.update(replace_jar(stage, jar))
            log = stage / "smoke.log"
            row["smoke_passed"] = bool(smoke_boot(stage, log))
            text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
            done = re.search(r"Done \(([0-9.]+)s\)", text)
            row["boot_done_s"] = float(done.group(1)) if done else None
            row["plugins_enabled"] = len(re.findall(r"Enabling ", text))
            row["key_lines"] = [line[:180] for line in text.splitlines()
                               if re.search(r"ERROR|Exception|Fail to launch|Done \(", line)][:8]
        except (OSError, ValueError, urllib.error.URLError) as exc:  # noqa: BLE001
            row["error"] = f"{type(exc).__name__}: {exc}"[:300]
            continue
        if not do_ab or not row.get("smoke_passed"):
            row["ab"] = {"verdict": "NEAVĂGAT" if not row.get("smoke_passed") else "SĂRIT",
                         "reason": ("nu a ajuns la `Done` cu pack-ul intact: fără scor de performanță"
                                    if not row.get("smoke_passed") else "A/B dezactivat prin argument")}
            continue
        base_rows, cand_rows = [], []
        for i in range(trials):
            for rows, dir_name, candidate in ((base_rows, "baseline", None), (cand_rows, "candidate", stage / "candidate.jar")):
                work = out / f"{cand['name']}-{dir_name}-{i}".replace("/", "-")
                work.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(pack) as z:
                    z.extractall(work)
                if candidate:
                    replace_jar(work, candidate)
                arm = boot_one(work, f"{dir_name}-{i}", work)
                arm["p95_ms"] = (arm.get("spark_tick_min_median_p95_max_ms_1m") or [None, None, None, None])[2]
                rows.append(arm)
        result["candidates"][cand["name"]]["ab"] = summarise(base_rows, cand_rows, trials)
        payload = out / f"{cand['name']}-gate.json"
        payload.write_text(json.dumps({"baseline": [], "candidate": []}, indent=2))
        result["candidates"][cand["name"]]["claim_gate"] = run_gate(payload)
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", default="", help="nume|url[|sha256][|licenta], separate prin virgulă")
    ap.add_argument("--spec-file", help="cetete same string dintr-un fisier (scapam de ghilimelele din shell)")
    ap.add_argument("--pack", required=True, help="CUANTIC-Server-CatServer-1.7.7.zip neschimbat")
    ap.add_argument("--out", required=True)
    ap.add_argument("--trials", type=int, default=MIN_TRIALS)
    ap.add_argument("--no-ab", action="store_true", help="doar descărcare + smoke")
    ap.add_argument("--list-maven", help="afișează versiunile din Maven Central pentru group:artifact")
    args = ap.parse_args(argv)
    if args.spec_file:
        args.spec = Path(args.spec_file).read_text(encoding="utf-8").strip()
    if args.list_maven:
        print("\n".join(maven_versions(args.list_maven)))
        return 0
    if not args.spec.strip():
        print(json.dumps({"error": "specifică --spec nume|url; fără candidat, scara nu inventează numere"},
                         ensure_ascii=False))
        return 2
    result = ladder(args.spec, Path(args.pack).resolve(), Path(args.out).resolve(),
                    trials=max(MIN_TRIALS, args.trials), do_ab=not args.no_ab)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
