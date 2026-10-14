#!/usr/bin/env python3
"""FC-GC — pauzele GC din jurnalele reale `-Xlog:gc*` (Java 11, G1) ale bancii FC-BENCH.

De ce exista: FC-BENCH v4 a scris jurnalul GC per proba (`gc-trialN.log`, decoratori
time,uptime,level,tags), dar parserul din scripts/fc_bench.py cauta un format inexistent
(`GC(n) ... TotalTime: x ms`) si a raportat onest NEMASURAT. Jurnalele au ramas in
artefactele alergarilor (14 zile), deci cifrele se pot scoate FARA o alergare noua.

Formatul recunoscut (o linie pe pauza, tag exact `gc`, nu `gc,start`/`gc,phases`):
  [2026-10-14T06:02:21.010+0000][0.566s][info][gc           ] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 51M->12M(1536M) 9.876ms
  [...][12.345s][info][gc] GC(7) Pause Remark 300M->300M(1536M) 4.321ms
  [...][12.400s][info][gc] GC(7) Pause Cleanup 300M->299M(1536M) 0.123ms
  [...][80.000s][info][gc] GC(9) Pause Full (System.gc()) 500M->200M(1536M) 456.789ms
`Concurrent Cycle 45.6ms` NU e pauza (firele aplicatiei merg) si nu intra in statistica.

Folosire:
  python3 scripts/fc_gc_reprocess.py --in /tmp/gc --out /tmp/gc/out
    --in  : radacina cu artefacte descarcate: <run>/<artefact>/gc-trialN.log + <arm>.json
  python3 scripts/fc_gc_reprocess.py --file gc-trial1.log   (statistica unui singur jurnal)

Reguli de onestitate: fisier absent sau format nerecunoscut => stare NEMASURAT cu motiv,
niciodata 0; separarea boot/idle foloseste `boot_timp_real_s` din JSON-ul bratului
(uptime <= boot => faza de pornire; restul = idle cu pack-ul incarcat).
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics
import sys
from typing import Iterable

PAUSE_RE = re.compile(
    r"^(?:\[(?P<time>[^\]]*)\])?"            # [2026-10-14T06:02:21.010+0000]  (optional)
    r"(?:\[(?P<uptime>[0-9]+(?:\.[0-9]+)?)s\])?"  # [0.566s]                   (optional)
    r"(?:\[(?P<level>[a-z]+)\s*\])?"           # [info]                       (optional)
    r"\[gc\s*\]\s+"                            # [gc           ]  — tag exact
    r"GC\((?P<id>\d+)\)\s+Pause\s+(?P<kind>Young|Remark|Cleanup|Full)"
    r"(?P<detail>(?:\s+\((?:[^()]|\([^()]*\))*\))*)\s+"  # (Normal) (G1 Evacuation Pause) / (System.gc())
    r"(?P<before>\d+)(?P<bu>[KMG])->(?P<after>\d+)(?P<au>[KMG])\((?P<cap>\d+)(?P<cu>[KMG])\)\s+"
    r"(?P<ms>[0-9]+(?:\.[0-9]+)?)ms\s*$"
)
HEAP_MAX_RE = re.compile(r"\[gc,init\s*\]\s+Heap Max Capacity:\s+([0-9]+)([KMG])|size:\s+([0-9]+)\s+MB, Compressed Oops")

_UNIT_MB = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0}


def _mb(value: str, unit: str) -> float:
    return round(int(value) * _UNIT_MB[unit], 1)


def parse_gc_lines(lines: Iterable[str]) -> list[dict]:
    """Toate pauzele (STW) dintr-un jurnal unified-logging, in ordinea aparitiei."""
    out: list[dict] = []
    for raw in lines:
        line = raw.rstrip("\r\n")
        m = PAUSE_RE.match(line)
        if not m:
            continue
        up = m.group("uptime")
        out.append({
            "id": int(m.group("id")),
            "kind": m.group("kind"),
            "detail": m.group("detail").strip(),
            "uptime_s": float(up) if up is not None else None,
            "ms": float(m.group("ms")),
            "heap_before_mb": _mb(m.group("before"), m.group("bu")),
            "heap_after_mb": _mb(m.group("after"), m.group("au")),
            "heap_cap_mb": _mb(m.group("cap"), m.group("cu")),
        })
    return out


def percentile(values: list[float], pct: float) -> float | None:
    """Percentila nearest-rank (fara interpolare — nu inventam valori intre probe)."""
    if not values:
        return None
    s = sorted(values)
    k = max(1, math.ceil(pct / 100.0 * len(s)))
    return s[k - 1]


def _stats(pauses: list[dict]) -> dict:
    ms = [p["ms"] for p in pauses]
    if not ms:
        return {"n": 0, "total_ms": 0.0, "max_ms": None, "medie_ms": None, "p95_ms": None, "p99_ms": None}
    return {
        "n": len(ms),
        "total_ms": round(sum(ms), 1),
        "max_ms": round(max(ms), 1),
        "medie_ms": round(statistics.mean(ms), 2),
        "p95_ms": round(percentile(ms, 95), 1),
        "p99_ms": round(percentile(ms, 99), 1),
    }


def summarize(pauses: list[dict], boot_s: float | None = None) -> dict:
    """Statistica unei probe: total + pe tip + boot/idle (daca stim durata bootului)."""
    kinds = {k: sum(1 for p in pauses if p["kind"] == k) for k in ("Young", "Remark", "Cleanup", "Full")}
    res = {
        "stare": "MASURAT" if pauses else "NEMASURAT",
        "total": _stats(pauses),
        "pe_tip": kinds,
        "full_gc": kinds["Full"],
        "young_max_ms": round(max((p["ms"] for p in pauses if p["kind"] == "Young"), default=0.0), 1) if pauses else None,
        "heap_dupa_ultimul_young_mb": next((p["heap_after_mb"] for p in reversed(pauses) if p["kind"] == "Young"), None),
        "heap_cap_mb": pauses[-1]["heap_cap_mb"] if pauses else None,
        "durata_jurnal_s": max((p["uptime_s"] for p in pauses if p["uptime_s"] is not None), default=None) if pauses else None,
    }
    if boot_s is not None and pauses and all(p["uptime_s"] is not None for p in pauses):
        boot = [p for p in pauses if p["uptime_s"] <= boot_s]
        idle = [p for p in pauses if p["uptime_s"] > boot_s]
        res["boot_s_folosit"] = boot_s
        res["boot"] = _stats(boot)
        res["idle"] = _stats(idle)
        if idle and res["durata_jurnal_s"] and res["durata_jurnal_s"] > boot_s:
            fereastra = res["durata_jurnal_s"] - boot_s
            res["idle"]["pauze_pe_minut"] = round(len(idle) / fereastra * 60.0, 2)
            res["idle"]["timp_oprit_pct"] = round(sum(p["ms"] for p in idle) / 1000.0 / fereastra * 100.0, 3)
    else:
        res["boot"] = None
        res["idle"] = None
        res["motiv_fara_split"] = "fara boot_timp_real_s sau fara decorator uptime" if pauses else "fara pauze recunoscute"
    return res


def summarize_file(path: pathlib.Path, boot_s: float | None = None) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"stare": "NEMASURAT", "motiv": f"jurnal absent: {e}", "fisier": str(path)}
    pauses = parse_gc_lines(text.splitlines())
    res = summarize(pauses, boot_s)
    res["fisier"] = path.name
    res["linii_jurnal"] = text.count("\n")
    if not pauses:
        res["motiv"] = "format nerecunoscut sau JVM fara pauze inregistrate (jurnal gol?)"
    return res


# ---------- agregare pe artefacte FC-BENCH (fcbench-<arm>/gc-trialN.log + <arm>.json) ----------

def _trial_boot_seconds(arm_json: dict | None, trial: int) -> float | None:
    if not arm_json:
        return None
    for p in arm_json.get("probe", []):
        if int(p.get("trial", -1)) == trial:
            v = p.get("boot_timp_real_s")
            return float(v) if v is not None else None
    return None


def process_artifact_dir(d: pathlib.Path) -> dict:
    """Un artefact = un brat: toate gc-trial*.log + JSON-ul bratului (pentru bootul fiecarei probe)."""
    arm_json = None
    for j in sorted(d.glob("*.json")):
        try:
            cand = json.loads(j.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(cand, dict) and "arm" in cand and "probe" in cand:
            arm_json = cand
            break
    arm = (arm_json or {}).get("arm") or d.name.replace("fcbench-", "")
    trials = []
    for lg in sorted(d.glob("gc-trial*.log*")):
        m = re.search(r"gc-trial(\d+)", lg.name)
        t = int(m.group(1)) if m else len(trials) + 1
        trials.append({"trial": t, **summarize_file(lg, _trial_boot_seconds(arm_json, t))})
    all_p = []
    for lg in sorted(d.glob("gc-trial*.log*")):
        all_p += parse_gc_lines(lg.read_text(encoding="utf-8", errors="replace").splitlines())
    masurate = [t for t in trials if t.get("stare") == "MASURAT"]
    agg = {
        "arm": arm,
        "eticheta": (arm_json or {}).get("eticheta", arm),
        "java": (arm_json or {}).get("java"),
        "probe_cu_jurnal": len(trials),
        "probe_masurate": len(masurate),
        "stare": "MASURAT" if masurate else "NEMASURAT",
        "toate_pauzele": _stats(all_p),
        "full_gc_total": sum(1 for p in all_p if p["kind"] == "Full"),
        "idle_p95_ms_pe_proba": [t["idle"]["p95_ms"] for t in masurate if t.get("idle")],
        "idle_max_ms_pe_proba": [t["idle"]["max_ms"] for t in masurate if t.get("idle")],
        "idle_pauze_pe_minut_pe_proba": [t["idle"].get("pauze_pe_minut") for t in masurate if t.get("idle")],
        "boot_total_ms_pe_proba": [t["boot"]["total_ms"] for t in masurate if t.get("boot")],
        "probe": trials,
    }
    if not trials:
        agg["motiv"] = "niciun gc-trial*.log in artefact (alergare fara -Xlog:gc* sau artefact expirat)"
    return agg


def process_root(root: pathlib.Path) -> dict:
    """<root>/<run_id>/<artefact>/... -> {runs: {run_id: {arm: agregat}}}"""
    runs: dict = {}
    for run_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        arms = {}
        for art in sorted(p for p in run_dir.iterdir() if p.is_dir()):
            if not list(art.glob("gc-trial*.log*")) and not list(art.glob("*.json")):
                continue
            a = process_artifact_dir(art)
            arms[a["arm"]] = a
        if arms:
            runs[run_dir.name] = {"arms": arms}
    return {"metoda": "FC-GC: pauzele STW din -Xlog:gc* (Java 11 G1) ale alergarilor FC-BENCH v4, "
                      "reprocesate din artefactele CI fara alergare noua; percentile nearest-rank; "
                      "boot/idle despartite la boot_timp_real_s al fiecarei probe",
            "runs": runs}


def _f(v, fmt="%.1f", suffix=""):
    return "NEMASURAT" if v is None else (fmt % v) + suffix


def render_markdown(data: dict, titlu: str = "FC-GC — pauze GC masurate din jurnalele FC-BENCH") -> str:
    L = [f"# {titlu}", "", data.get("metoda", ""), ""]
    for run_id, run in data.get("runs", {}).items():
        L += [f"## Alergare {run_id}", "",
              "| brat | probe | pauze (toate) | max ms | p95 ms | medie ms | Full-GC | idle p95/proba ms | idle max/proba ms | idle pauze/min | boot total ms/proba |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, a in run["arms"].items():
            t = a["toate_pauzele"]
            if a["stare"] != "MASURAT":
                L.append(f"| {a['eticheta']} | {a['probe_cu_jurnal']} | NEMASURAT | — | — | — | — | — | — | — | — |")
                continue
            L.append("| " + " | ".join([
                a["eticheta"], f"{a['probe_masurate']}/{a['probe_cu_jurnal']}", str(t["n"]),
                _f(t["max_ms"]), _f(t["p95_ms"]), _f(t["medie_ms"], "%.2f"), str(a["full_gc_total"]),
                "/".join(_f(x) for x in a["idle_p95_ms_pe_proba"]) or "—",
                "/".join(_f(x) for x in a["idle_max_ms_pe_proba"]) or "—",
                "/".join(_f(x, "%.2f") for x in a["idle_pauze_pe_minut_pe_proba"]) or "—",
                "/".join(_f(x, "%.0f") for x in a["boot_total_ms_pe_proba"]) or "—",
            ]) + " |")
        L.append("")
    L += ["Semnificatie: pauza = timp in care TOATE firele serverului stau (STW). Un tick are 50 ms; o pauza sub ~10 ms",
          "nu se vede in joc, una peste 50 ms = tick sarit. `idle` = dupa `Done`, server gol cu 36 moduri + 14 plugini;",
          "nu e gameplay. Full-GC = 0 inseamna ca G1 nu a ajuns la colectare completa in fereastra masurata.", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="root", help="radacina cu <run>/<artefact>/gc-trialN.log")
    ap.add_argument("--out", help="director de iesire (gc.json + GC.md)")
    ap.add_argument("--file", help="un singur jurnal GC -> statistica JSON pe stdout")
    ap.add_argument("--boot", type=float, default=None, help="secunde de boot pentru --file (split boot/idle)")
    a = ap.parse_args(argv)
    if a.file:
        print(json.dumps(summarize_file(pathlib.Path(a.file), a.boot), ensure_ascii=False, indent=1))
        return 0
    if not a.root:
        ap.error("--in sau --file")
    data = process_root(pathlib.Path(a.root))
    out = pathlib.Path(a.out or ".")
    out.mkdir(parents=True, exist_ok=True)
    (out / "gc.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "GC.md").write_text(render_markdown(data), encoding="utf-8")
    print(render_markdown(data))
    n_arm = sum(len(r["arms"]) for r in data["runs"].values())
    n_ok = sum(1 for r in data["runs"].values() for x in r["arms"].values() if x["stare"] == "MASURAT")
    print(f"brate: {n_arm}, masurate: {n_ok}", file=sys.stderr)
    return 0 if n_ok else 2


if __name__ == "__main__":
    sys.exit(main())
