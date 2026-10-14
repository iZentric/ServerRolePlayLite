# FunCity FC-BENCH v4 — verdic masurate pe runner izolat

Data probei: 2026-10-14 04:19–06:19 UTC · alergari CI 38510786719 (A) si 38519665645 (B, precizie 0,25 s)
Metoda: 4 braate × 3 probe boot-la-cald pe ACELASI world (comun dupa instalarea bootstrap), java 11 Temurin,
-Xmx1536M, runner ubuntu-24.04, pack CUANTIC 36 moduri / 14 pluginuri cu SHA256 fix (fe1e2610…), surse 100% din
git (functity-out). Runda A a avut eșantionare wall cuantificata la 2 s — de aceea comparatia se face pe
„Done (x.xs)” masurat de motor insusi, nu pe wall.
Raportari brute: branch `functity-out` → `bench-v4/20261014-0538/` (A) si `bench-v4/20261014-0619/` (B + agregat);
jurnalele GC brute: `bench-v4/gc/<run>/<brat>/gc-trialN.log` (publicate de FC-GC din artefactele CI).

## Verdict (stari: TRECUT / ESUAT / NEMASURAT)

- Stabilitate: **TRECUT** — 24/24 boot-uri pana la „Done”, 0 erori critice, 0 `Can't keep up!`, TPS idle 20,0 pe
  toate braatele in ambele runde, oprire CLEAN in toate probele.
- FunCity vs Mohist oficial 1237 (timpul „Done” auto-masurat de motor): **fara regresie, fara castig** —
  3,0–4,8 s vs 3,8–4,3 s, in jurul zgomotului masurii; wall-ul a răsturnat ordinile intre runde (A: b1 cel mai
  rapid, B: b1 cel mai lent) → dovedește ca wall pe runner partajat NU e folosit la clasament.
- FunCity vs CatServer din pack (acelasi „Done”): **TRECUT cu castig masurat** — motoarele Mohist-family termina
  boot-ul cu 29–55% mai repede decat CatServer (media pe probe: FunCity 3,0–4,8 s, Mohist oficial 3,8–4,3 s,
  CatServer 6,4–8,1 s).
- Latenta de join cu client modat: **NEMASURAT** — proba vanilla (protocol 754, offline) a fost refuzata de FML
  pe TOATE braatele cu mesajul „server requires Forge client”; comportament identic peste tot, deci corect, dar
  cifre de join reale necesita bot mineflayer cu setul de moduri (faza urmatoare).
- Pauze GC (STW, -Xlog:gc* JDK 11 G1, reprocesate din artefactele A/B de FC-GC 38557476084 — `analysis/FUNCTITY-GC.md`):
  **MASURAT, fara regresie** — la boot fiecare motor face 43–53 pauze tinere, 1,2–1,7 s STW in total pe boot,
  pauza maxima la boot: CatServer 146/174 ms, Mohist 1237 119/99 ms, FunCity b0 105/84 ms, FunCity b1 97/128 ms
  (A/B); p95 pe boot 68–99 ms peste tot. Dupa „Done” (server gol, 3×~310 s pe brat): 1–3 pauze pe brat,
  maxima 34–51 ms (in jurul unui tick de 50 ms), 0 Full-GC pe Mohist-family; CatServer are 1 `Full (System.gc())` per
  pornire la 0,5 s (5 ms, cerut de cod, nu presiune). Heap viu dupa ultimul young la boot: Mohist-family
  516–572 MB, CatServer 617–653 MB. Ce NU spune: nimic despre GC sub sarcina cu jucatori.
- MSPT (`forge tps`): **NEMASURAT** in A/B (harness-ul trimitea `ticks tps`/`mspt`, necunoscute pe hibride);
  corectat in v4.2, se masoara din runda C.
- Repetabilitate: **TRECUT** — CV sub 10% la 7 din 8 braat-runde (cel mai mare 9,2%).

```json
{
 "data": "2026-10-14 06:19 UTC",
 "metoda": "FC-BENCH v4: 4 braate x 3 probe boot-la-cald, world comun, java 11, -Xmx1536M, pack 36/14 SHA fix, runner GitHub izolat",
 "brate": {
  "catserver": "CatServer 1.16.5-1d8d6313 (motorul istoric al serverului)",
  "oficial1237": "Mohist oficial 1.16.5-1237 (referinta din ecosistem)",
  "functity_b0": "FunCity b0 — build propriu, pin 754b578e, fara patch-uri",
  "functity_b1": "FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard"
 },
 "runde": {
  "A": {
   "run": "38510786719",
   "precizie": "wall cuantificat 2 s",
   "arms": {
    "catserver": {"stare": "MASURAT", "done_s": [9.983, 6.923, 7.301], "wall_s": 43.35, "cv": 4.3, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2227.8, "cpu": 2.5, "join": null},
    "oficial1237": {"stare": "MASURAT", "done_s": [6.976, 3.312, 2.633], "wall_s": 44.68, "cv": 8.5, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2254.6, "cpu": 2.7, "join": null},
    "functity_b0": {"stare": "MASURAT", "done_s": [6.607, 3.336, 2.791], "wall_s": 42.68, "cv": 5.8, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2267.6, "cpu": 2.4, "join": null},
    "functity_b1": {"stare": "MASURAT", "done_s": [4.703, 2.316, 2.079], "wall_s": 33.34, "cv": 5.7, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2256.1, "cpu": 1.8, "join": null}
   }
  },
  "B": {
   "run": "38519665645",
   "precizie": "wall 0,25 s + uptime logic",
   "arms": {
    "catserver": {"stare": "MASURAT", "done_s": [7.986, 5.601, 5.465], "wall_s": 34.98, "cv": 4.9, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2218.5, "cpu": 1.5, "join": null},
    "oficial1237": {"stare": "MASURAT", "done_s": [6.362, 2.675, 2.392], "wall_s": 35.73, "cv": 9.2, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2259.7, "cpu": 2.4, "join": null},
    "functity_b0": {"stare": "MASURAT", "done_s": [6.291, 3.284, 3.197], "wall_s": 44.08, "cv": 4.4, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2258.5, "cpu": 2.6, "join": null},
    "functity_b1": {"stare": "MASURAT", "done_s": [7.691, 3.615, 3.048], "wall_s": 45.41, "cv": 5.1, "tps": 20.0, "overrun": 0, "critice": 0, "rss_mb": 2240.4, "cpu": 2.7, "join": null}
   }
  }
 },
 "praguri": {
  "CV < 10% pe brat": "TRECUT (7/8, max 9,2%)",
  "0 erori critice pe 3 probe": "TRECUT (0 pe toate, ambele runde)",
  "0 'Can't keep up!' in fereastra de 300 s": "TRECUT",
  "TPS idle p50 >= 19.8": "TRECUT (20,0)"
 },
 "limite": [
  "masina CI (4 vCPU, runner partajat) NU e gazda live (2 vCPU) — cifrele compara motoarele intre ele, nu promit valori pe box",
  "sarcina e boot + idle cu pack complet; nu e test de gameplay cu 10-25 jucatori",
  "join cu client modat rămâne NEMASURAT pana la runda cu bot mineflayer",
  "wall pe runner partajat are zgomot de ordinul secundelor intre alergari; folosim doar timpul 'Done' auto-masurat de motor",
  "GC: pauzele masurate sint boot + server gol; sub sarcina (jucatori, chunk-uri) heap-ul se umple altfel — NEMASURAT",
  "MSPT: NEMASURAT in A/B (comenzi gresite in harness), masurat din runda C cu `forge tps`"
 ],
 "gc": {
  "sursa": "analysis/FUNCTITY-GC.md (FC-GC 38557476084, reprocesare 2026-10-14 11:39 UTC din artefactele A/B)",
  "unitate": "ms STW; boot = pana la Done, idle = dupa Done (3 probe x ~310 s pe brat)",
  "runde": {
   "A": {
    "catserver": {
     "boot_max_ms": 146.3,
     "boot_p95_ms": 94.6,
     "boot_total_ms": [1479, 1545, 1536],
     "boot_pauze": [49, 47, 53],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 33.8,
     "full_gc": 3,
     "heap_dupa_young_mb": [635, 624, 632]
    },
    "functity_b0": {
     "boot_max_ms": 105.2,
     "boot_p95_ms": 75.0,
     "boot_total_ms": [1372, 1446, 1381],
     "boot_pauze": [47, 48, 45],
     "idle_pauze": 3,
     "idle_fereastra_s": 929,
     "idle_max_ms": 42.6,
     "full_gc": 0,
     "heap_dupa_young_mb": [532, 549, 544]
    },
    "functity_b1": {
     "boot_max_ms": 96.7,
     "boot_p95_ms": 76.4,
     "boot_total_ms": [1332, 1360, 1339],
     "boot_pauze": [53, 47, 46],
     "idle_pauze": 1,
     "idle_fereastra_s": 928,
     "idle_max_ms": 45.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [545, 558, 560]
    },
    "oficial1237": {
     "boot_max_ms": 118.6,
     "boot_p95_ms": 81.0,
     "boot_total_ms": [1592, 1476, 1486],
     "boot_pauze": [53, 48, 48],
     "idle_pauze": 1,
     "idle_fereastra_s": 929,
     "idle_max_ms": 37.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [572, 544, 547]
    }
   },
   "B": {
    "catserver": {
     "boot_max_ms": 174.4,
     "boot_p95_ms": 99.3,
     "boot_total_ms": [1723, 1613, 1499],
     "boot_pauze": [50, 53, 45],
     "idle_pauze": 1,
     "idle_fereastra_s": 928,
     "idle_max_ms": 49.0,
     "full_gc": 3,
     "heap_dupa_young_mb": [653, 617, 625]
    },
    "functity_b0": {
     "boot_max_ms": 83.6,
     "boot_p95_ms": 70.7,
     "boot_total_ms": [1466, 1441, 1454],
     "boot_pauze": [48, 45, 47],
     "idle_pauze": 3,
     "idle_fereastra_s": 929,
     "idle_max_ms": 42.1,
     "full_gc": 0,
     "heap_dupa_young_mb": [516, 550, 553]
    },
    "functity_b1": {
     "boot_max_ms": 127.5,
     "boot_p95_ms": 71.7,
     "boot_total_ms": [1558, 1317, 1449],
     "boot_pauze": [49, 43, 46],
     "idle_pauze": 1,
     "idle_fereastra_s": 929,
     "idle_max_ms": 51.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [535, 550, 551]
    },
    "oficial1237": {
     "boot_max_ms": 98.6,
     "boot_p95_ms": 68.0,
     "boot_total_ms": [1176, 1237, 1186],
     "boot_pauze": [48, 45, 46],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 37.3,
     "full_gc": 0,
     "heap_dupa_young_mb": [536, 557, 547]
    }
   }
  }
 }
}
```
