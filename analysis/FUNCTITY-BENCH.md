# FunCity FC-BENCH v4.2 — rezultate măsurate pe runner hosted izolat

Date: rundele A/B, 2026-10-14 04:19–06:19 UTC; runda C, 11:39–11:59 UTC · FC-BENCH runs 38510786719 (A), 38519665645 (B), 38558064533 (C); reprocesare GC hosted 38978721931.
Metodă: 4 brațe × 3 probe pe același world, Java 11 Temurin, -Xmx1536M, pack CUANTIC 36 moduri / 14 pluginuri cu SHA fix, runner ubuntu-24.04. A/B păstrează timpul „Done (x.xs)” raportat de motor; în C v4.2 boot-ul este cronometrat extern până la „Done” (poll ~0,25 s), iar MSPT vine din `forge tps`. Timpii de boot A/B și C nu sunt direct comparabili.
Rapoarte brute: `functity-out:bench-v4/20261014-0538/` (A), `20261014-0619/` (B), `20261014-1157/` + `20261014-1159/` (C; agregatul este în `1159/summary.md`); jurnalele GC în `functity-out:bench-v4/gc/<run>/<braț>/` și verdict în `analysis/FUNCTITY-GC.md`.

## Verdict (stări: TRECUT / EȘUAT / NEMĂSURAT)

- Stabilitate: **TRECUT** — 36/36 boot-uri au ajuns la „Done”, 0 erori critice și 0 `Can't keep up!`; TPS idle 20,0; oprire CLEAN în toate cele 36 de probe.
- Boot A/B (`Done` intern): FunCity b1 vs Mohist oficial 1237 **fără diferență stabilă declarabilă** (3,0–4,8 s vs 3,8–4,3 s); față de CatServer, rundele A/B indică 29–55% mai puțin timp intern până la Done. În C, ceasul extern a măsurat 37,74 s pentru b1, 42,24 s pentru b0, 45,00 s pentru 1237 și 42,41 s pentru CatServer; aceasta este o măsură diferită, raportată separat în JSON, fără comparație directă cu A/B.
- Join cu client Forge modat: **NEMĂSURAT** — proba vanilla protocol 754 este respinsă corect de FML pe toate brațele; join real necesită bot cu setul de moduri.
- MSPT (`forge tps`): **MĂSURAT în runda C** — 18 citiri/arm (`Overall: Mean tick time`), medie/maximul citirilor: CatServer 0,08/0,14 ms; Mohist 1237 0,18/0,21 ms; b0 0,09/0,11 ms; b1 0,08/0,12 ms. TPS p50 = 20,0 și overrun = 0. Sunt medii cumulative pe server gol, nu p95 sau maximul unui tick; diferențele sub-milisecundă nu dovedesc un câștig în gameplay. MSPT rămâne NEMĂSURAT în A/B.
- Pauze GC: **MĂSURATE în A/B/C**, 36/36 probe cu jurnal recunoscut (`analysis/FUNCTITY-GC.md`). În C, max/p95 boot (ms): CatServer 151,2/93,8; 1237 131,6/99,0; b0 112,4/74,3; b1 144,2/82,4. După Done, max idle în ~929 s: 44,3 / 66,7 / 50,9 / 54,5 ms (ordinea CatServer/1237/b0/b1); Full-GC: 3 la CatServer, declanșate explicit prin `System.gc()`, 0 la Mohist-family. Max-ul b1 din C depășește 1237 și b0, dar p95-ul b1 este sub 1237 și peste b0; cu trei probe nu declarăm nici „fără regresie”, nici o regresie stabilă. Sub sarcină cu jucători: NEMĂSURAT.
- Repetabilitate: A/B au CV<10% în 7/8 braț-runde (max 9,2%); C are CV<10% în 4/4 brațe (max 7,3%) pentru cronometrul extern. Metodele de boot diferă și nu se agregă într-un singur CV.

```json
{
 "data": "2026-10-14 11:59 UTC (runda C, FC-BENCH 38558064533)",
 "metoda": "FC-BENCH v4.2: 4 brațe × 3 probe boot-la-cald, world comun, Java 11, -Xmx1536M, pack 36/14 cu SHA fix, runner GitHub-hosted ubuntu-24.04; A/B raportează Done intern, C raportează wall extern până la Done + forge tps. Timpii de boot A/B și C nu se compară direct.",
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
    "catserver": {
     "stare": "MASURAT",
     "done_s": [
      9.983,
      6.923,
      7.301
     ],
     "wall_s": 43.35,
     "cv": 4.3,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2227.8,
     "cpu": 2.5,
     "join": null
    },
    "oficial1237": {
     "stare": "MASURAT",
     "done_s": [
      6.976,
      3.312,
      2.633
     ],
     "wall_s": 44.68,
     "cv": 8.5,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2254.6,
     "cpu": 2.7,
     "join": null
    },
    "functity_b0": {
     "stare": "MASURAT",
     "done_s": [
      6.607,
      3.336,
      2.791
     ],
     "wall_s": 42.68,
     "cv": 5.8,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2267.6,
     "cpu": 2.4,
     "join": null
    },
    "functity_b1": {
     "stare": "MASURAT",
     "done_s": [
      4.703,
      2.316,
      2.079
     ],
     "wall_s": 33.34,
     "cv": 5.7,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2256.1,
     "cpu": 1.8,
     "join": null
    }
   }
  },
  "B": {
   "run": "38519665645",
   "precizie": "wall 0,25 s + uptime logic",
   "arms": {
    "catserver": {
     "stare": "MASURAT",
     "done_s": [
      7.986,
      5.601,
      5.465
     ],
     "wall_s": 34.98,
     "cv": 4.9,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2218.5,
     "cpu": 1.5,
     "join": null
    },
    "oficial1237": {
     "stare": "MASURAT",
     "done_s": [
      6.362,
      2.675,
      2.392
     ],
     "wall_s": 35.73,
     "cv": 9.2,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2259.7,
     "cpu": 2.4,
     "join": null
    },
    "functity_b0": {
     "stare": "MASURAT",
     "done_s": [
      6.291,
      3.284,
      3.197
     ],
     "wall_s": 44.08,
     "cv": 4.4,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2258.5,
     "cpu": 2.6,
     "join": null
    },
    "functity_b1": {
     "stare": "MASURAT",
     "done_s": [
      7.691,
      3.615,
      3.048
     ],
     "wall_s": 45.41,
     "cv": 5.1,
     "tps": 20.0,
     "overrun": 0,
     "critice": 0,
     "rss_mb": 2240.4,
     "cpu": 2.7,
     "join": null
    }
   }
  },
  "C": {
   "run": "38558064533",
   "precizie": "FC-BENCH v4.2: cronometru extern lansare JVM → Done (poll ~0,25 s); MSPT din forge tps / Overall Mean tick time",
   "arms": {
    "catserver": {
     "stare": "MASURAT",
     "boot_wall_to_done_s": [
      44.08,
      41.57,
      41.57
     ],
     "boot_medie_wall_s": 42.41,
     "cv_wall_pct": 2.8,
     "tps_p50": 20.0,
     "mspt_medie_ms": 0.08,
     "mspt_max_esantion_ms": 0.14,
     "mspt_esantioane": 18,
     "overrun_total": 0,
     "critice_total": 0,
     "rss_mb": 2214.0,
     "cpu_pct": 2.3,
     "join_medie_ms": null,
     "oprire": [
      "CLEAN",
      "CLEAN",
      "CLEAN"
     ]
    },
    "oficial1237": {
     "stare": "MASURAT",
     "boot_wall_to_done_s": [
      47.84,
      43.83,
      43.33
     ],
     "boot_medie_wall_s": 45.0,
     "cv_wall_pct": 4.5,
     "tps_p50": 20.0,
     "mspt_medie_ms": 0.18,
     "mspt_max_esantion_ms": 0.21,
     "mspt_esantioane": 18,
     "overrun_total": 0,
     "critice_total": 0,
     "rss_mb": 2263.9,
     "cpu_pct": 2.9,
     "join_medie_ms": null,
     "oprire": [
      "CLEAN",
      "CLEAN",
      "CLEAN"
     ]
    },
    "functity_b0": {
     "stare": "MASURAT",
     "boot_wall_to_done_s": [
      46.58,
      40.56,
      39.57
     ],
     "boot_medie_wall_s": 42.24,
     "cv_wall_pct": 7.3,
     "tps_p50": 20.0,
     "mspt_medie_ms": 0.09,
     "mspt_max_esantion_ms": 0.11,
     "mspt_esantioane": 18,
     "overrun_total": 0,
     "critice_total": 0,
     "rss_mb": 2229.6,
     "cpu_pct": 2.4,
     "join_medie_ms": null,
     "oprire": [
      "CLEAN",
      "CLEAN",
      "CLEAN"
     ]
    },
    "functity_b1": {
     "stare": "MASURAT",
     "boot_wall_to_done_s": [
      40.58,
      37.07,
      35.57
     ],
     "boot_medie_wall_s": 37.74,
     "cv_wall_pct": 5.6,
     "tps_p50": 20.0,
     "mspt_medie_ms": 0.08,
     "mspt_max_esantion_ms": 0.12,
     "mspt_esantioane": 18,
     "overrun_total": 0,
     "critice_total": 0,
     "rss_mb": 2245.2,
     "cpu_pct": 1.7,
     "join_medie_ms": null,
     "oprire": [
      "CLEAN",
      "CLEAN",
      "CLEAN"
     ]
    }
   }
  }
 },
 "praguri": {
  "CV < 10% pe braț A/B (Done intern)": "TRECUT (7/8, max 9,2%)",
  "CV < 10% pe braț C (boot extern)": "TRECUT (4/4, max 7,3%; metodă separată)",
  "0 erori critice pe toate probele": "TRECUT (0/36)",
  "0 'Can't keep up!' în probele de 300 s": "TRECUT (0 în A/B/C)",
  "TPS idle p50 >= 19,8": "TRECUT (20,0 în A/B/C)"
 },
 "limite": [
  "runnerul CI (4 vCPU, 16 GB, partajat) NU este gazda live (2 vCPU); cifrele compară motoarele doar în banca izolată",
  "sarcina măsurată este boot + server gol cu pack complet; nu este test de gameplay cu jucători, chunk-uri sau vehicule",
  "join cu client Forge modat rămâne NEMĂSURAT până la proba cu bot mineflayer",
  "timpii A/B provin din Done intern; C folosește ceas extern până la Done — nu se compară între versiuni de metodă",
  "MSPT este doar runda C: media cumulativă Overall din forge tps, 18 citiri/arm la server gol; nu este p95 sau maxim de tick individual",
  "GC A/B/C măsoară boot + server gol; pauzele și MSPT sub încărcare reală rămân NEMĂSURATE"
 ],
 "gc": {
  "sursa": "analysis/FUNCTITY-GC.md (FC-GC 38978721931, reprocesare hosted a rundelor 38510786719, 38519665645 și 38558064533)",
  "unitate": "ms STW; boot = până la Done, idle = după Done; fiecare rundă are 3 probe/arm, aproximativ 929 s idle agregat/arm",
  "runde": {
   "A": {
    "catserver": {
     "boot_max_ms": 146.3,
     "boot_p95_ms": 94.6,
     "boot_total_ms": [
      1479,
      1545,
      1536
     ],
     "boot_pauze": [
      49,
      47,
      53
     ],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 33.8,
     "full_gc": 3,
     "heap_dupa_young_mb": [
      635,
      624,
      632
     ]
    },
    "functity_b0": {
     "boot_max_ms": 105.2,
     "boot_p95_ms": 75.0,
     "boot_total_ms": [
      1372,
      1446,
      1381
     ],
     "boot_pauze": [
      47,
      48,
      45
     ],
     "idle_pauze": 3,
     "idle_fereastra_s": 929,
     "idle_max_ms": 42.6,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      532,
      549,
      544
     ]
    },
    "functity_b1": {
     "boot_max_ms": 96.7,
     "boot_p95_ms": 76.4,
     "boot_total_ms": [
      1332,
      1360,
      1339
     ],
     "boot_pauze": [
      53,
      47,
      46
     ],
     "idle_pauze": 1,
     "idle_fereastra_s": 928,
     "idle_max_ms": 45.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      545,
      558,
      560
     ]
    },
    "oficial1237": {
     "boot_max_ms": 118.6,
     "boot_p95_ms": 81.0,
     "boot_total_ms": [
      1592,
      1476,
      1486
     ],
     "boot_pauze": [
      53,
      48,
      48
     ],
     "idle_pauze": 1,
     "idle_fereastra_s": 929,
     "idle_max_ms": 37.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      572,
      544,
      547
     ]
    }
   },
   "B": {
    "catserver": {
     "boot_max_ms": 174.4,
     "boot_p95_ms": 99.3,
     "boot_total_ms": [
      1723,
      1613,
      1499
     ],
     "boot_pauze": [
      50,
      53,
      45
     ],
     "idle_pauze": 1,
     "idle_fereastra_s": 928,
     "idle_max_ms": 49.0,
     "full_gc": 3,
     "heap_dupa_young_mb": [
      653,
      617,
      625
     ]
    },
    "functity_b0": {
     "boot_max_ms": 83.6,
     "boot_p95_ms": 70.7,
     "boot_total_ms": [
      1466,
      1441,
      1454
     ],
     "boot_pauze": [
      48,
      45,
      47
     ],
     "idle_pauze": 3,
     "idle_fereastra_s": 929,
     "idle_max_ms": 42.1,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      516,
      550,
      553
     ]
    },
    "functity_b1": {
     "boot_max_ms": 127.5,
     "boot_p95_ms": 71.7,
     "boot_total_ms": [
      1558,
      1317,
      1449
     ],
     "boot_pauze": [
      49,
      43,
      46
     ],
     "idle_pauze": 1,
     "idle_fereastra_s": 929,
     "idle_max_ms": 51.0,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      535,
      550,
      551
     ]
    },
    "oficial1237": {
     "boot_max_ms": 98.6,
     "boot_p95_ms": 68.0,
     "boot_total_ms": [
      1176,
      1237,
      1186
     ],
     "boot_pauze": [
      48,
      45,
      46
     ],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 37.3,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      536,
      557,
      547
     ]
    }
   },
   "C": {
    "catserver": {
     "boot_max_ms": 151.2,
     "boot_p95_ms": 93.8,
     "boot_total_ms": [
      1561,
      1344,
      1456
     ],
     "boot_pauze": [
      49,
      47,
      52
     ],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 44.3,
     "full_gc": 3,
     "heap_dupa_young_mb": [
      626,
      625,
      641
     ]
    },
    "oficial1237": {
     "boot_max_ms": 131.6,
     "boot_p95_ms": 99.0,
     "boot_total_ms": [
      1646,
      1767,
      1789
     ],
     "boot_pauze": [
      48,
      48,
      48
     ],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 66.7,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      535,
      550,
      553
     ]
    },
    "functity_b0": {
     "boot_max_ms": 112.4,
     "boot_p95_ms": 74.3,
     "boot_total_ms": [
      1364,
      1296,
      1428
     ],
     "boot_pauze": [
      47,
      47,
      46
     ],
     "idle_pauze": 2,
     "idle_fereastra_s": 929,
     "idle_max_ms": 50.9,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      534,
      555,
      547
     ]
    },
    "functity_b1": {
     "boot_max_ms": 144.2,
     "boot_p95_ms": 82.4,
     "boot_total_ms": [
      1495,
      1428,
      1527
     ],
     "boot_pauze": [
      48,
      49,
      43
     ],
     "idle_pauze": 1,
     "idle_fereastra_s": 929,
     "idle_max_ms": 54.5,
     "full_gc": 0,
     "heap_dupa_young_mb": [
      522,
      544,
      559
     ]
    }
   }
  }
 }
}
```
