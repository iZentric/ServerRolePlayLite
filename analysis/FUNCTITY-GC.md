# FUNCTITY-GC — pauzele GC ale FC-BENCH v4, reprocesate din artefacte (2026-10-14 11:34 UTC)

Alergare CI: 38557476084 · artefacte: run 38510786719: fcbench-catserver fcbench-functity_b0 fcbench-functity_b1 fcbench-oficial1237  | jurnale gc: 12;run 38519665645: fcbench-catserver fcbench-functity_b0 fcbench-functity_b1 fcbench-oficial1237  | jurnale gc: 12; · rc parser: RC=0
Jurnale brute: https://github.com/iZentric/ServerRolePlayLite/tree/functity-out/bench-v4/gc


FC-GC: pauzele STW din -Xlog:gc* (Java 11 G1) ale alergarilor FC-BENCH v4, reprocesate din artefactele CI fara alergare noua; percentile nearest-rank; boot/idle despartite la boot_timp_real_s al fiecarei probe

## Alergare 38510786719

| brat | probe | pauze (toate) | max ms | p95 ms | medie ms | Full-GC | idle p95/proba ms | idle max/proba ms | idle pauze/min | boot total ms/proba |
|---|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | 3/3 | 151 | 146.3 | 94.6 | 30.64 | 3 | 32.0/NEMASURAT/33.8 | 32.0/NEMASURAT/33.8 | 0.31/NEMASURAT/0.27 | 1479/1545/1536 |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | 3/3 | 143 | 105.2 | 75.0 | 29.90 | 0 | 42.6/NEMASURAT/NEMASURAT | 42.6/NEMASURAT/NEMASURAT | 102.51/NEMASURAT/NEMASURAT | 1372/1446/1381 |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | 3/3 | 147 | 96.7 | 76.4 | 27.72 | 0 | NEMASURAT/NEMASURAT/45.0 | NEMASURAT/NEMASURAT/45.0 | NEMASURAT/NEMASURAT/1034.48 | 1332/1360/1339 |
| Mohist oficial 1.16.5-1237 (referinta) | 3/3 | 150 | 118.6 | 81.0 | 30.61 | 0 | 37.0/NEMASURAT/NEMASURAT | 37.0/NEMASURAT/NEMASURAT | 0.35/NEMASURAT/NEMASURAT | 1592/1476/1486 |

## Alergare 38519665645

| brat | probe | pauze (toate) | max ms | p95 ms | medie ms | Full-GC | idle p95/proba ms | idle max/proba ms | idle pauze/min | boot total ms/proba |
|---|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | 3/3 | 149 | 174.4 | 99.3 | 32.78 | 3 | NEMASURAT/NEMASURAT/49.0 | NEMASURAT/NEMASURAT/49.0 | NEMASURAT/NEMASURAT/71.17 | 1723/1613/1499 |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | 3/3 | 143 | 83.6 | 70.7 | 30.99 | 0 | NEMASURAT/NEMASURAT/42.1 | NEMASURAT/NEMASURAT/42.1 | NEMASURAT/NEMASURAT/4.30 | 1466/1441/1454 |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | 3/3 | 139 | 127.5 | 71.7 | 31.47 | 0 | 51.0/NEMASURAT/NEMASURAT | 51.0/NEMASURAT/NEMASURAT | 350.88/NEMASURAT/NEMASURAT | 1558/1317/1449 |
| Mohist oficial 1.16.5-1237 (referinta) | 3/3 | 141 | 98.6 | 60.0 | 26.04 | 0 | 34.2/37.3/NEMASURAT | 34.2/37.3/NEMASURAT | 3.85/0.29/NEMASURAT | 1176/1237/1186 |

Semnificatie: pauza = timp in care TOATE firele serverului stau (STW). Un tick are 50 ms; o pauza sub ~10 ms
nu se vede in joc, una peste 50 ms = tick sarit. `idle` = dupa `Done`, server gol cu 36 moduri + 14 plugini;
nu e gameplay. Full-GC = 0 inseamna ca G1 nu a ajuns la colectare completa in fereastra masurata.

```json
{
 "metoda": "FC-GC: pauzele STW din -Xlog:gc* (Java 11 G1) ale alergarilor FC-BENCH v4, reprocesate din artefactele CI fara alergare noua; percentile nearest-rank; boot/idle despartite la boot_timp_real_s al fiecarei probe",
 "runs": {
  "38510786719": {
   "arms": {
    "catserver": {
     "arm": "catserver",
     "eticheta": "CatServer din pack (motorul istoric al serverului)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 151,
      "total_ms": 4626.0,
      "max_ms": 146.3,
      "medie_ms": 30.64,
      "p95_ms": 94.6,
      "p99_ms": 145.7
     },
     "full_gc_total": 3,
     "idle_p95_ms_pe_proba": [
      32.0,
      null,
      33.8
     ],
     "idle_max_ms_pe_proba": [
      32.0,
      null,
      33.8
     ],
     "idle_pauze_pe_minut_pe_proba": [
      0.31,
      null,
      0.27
     ],
     "boot_total_ms_pe_proba": [
      1478.7,
      1545.4,
      1536.0
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 50,
        "total_ms": 1510.8,
        "max_ms": 146.3,
        "medie_ms": 30.22,
        "p95_ms": 87.0,
        "p99_ms": 146.3
       },
       "pe_tip": {
        "Young": 37,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 146.3,
       "heap_dupa_ultimul_young_mb": 635.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 238.067,
       "boot_s_folosit": 46.01,
       "boot": {
        "n": 49,
        "total_ms": 1478.7,
        "max_ms": 146.3,
        "medie_ms": 30.18,
        "p95_ms": 87.0,
        "p99_ms": 146.3
       },
       "idle": {
        "n": 1,
        "total_ms": 32.0,
        "max_ms": 32.0,
        "medie_ms": 32.03,
        "p95_ms": 32.0,
        "p99_ms": 32.0,
        "pauze_pe_minut": 0.31,
        "timp_oprit_pct": 0.017
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 651
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 47,
        "total_ms": 1545.4,
        "max_ms": 132.5,
        "medie_ms": 32.88,
        "p95_ms": 96.2,
        "p99_ms": 132.5
       },
       "pe_tip": {
        "Young": 34,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 132.5,
       "heap_dupa_ultimul_young_mb": 624.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 41.819,
       "boot_s_folosit": 42.02,
       "boot": {
        "n": 47,
        "total_ms": 1545.4,
        "max_ms": 132.5,
        "medie_ms": 32.88,
        "p95_ms": 96.2,
        "p99_ms": 132.5
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 612
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 54,
        "total_ms": 1569.8,
        "max_ms": 145.7,
        "medie_ms": 29.07,
        "p95_ms": 94.6,
        "p99_ms": 145.7
       },
       "pe_tip": {
        "Young": 39,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 145.7,
       "heap_dupa_ultimul_young_mb": 632.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 260.448,
       "boot_s_folosit": 42.01,
       "boot": {
        "n": 53,
        "total_ms": 1536.0,
        "max_ms": 145.7,
        "medie_ms": 28.98,
        "p95_ms": 94.6,
        "p99_ms": 145.7
       },
       "idle": {
        "n": 1,
        "total_ms": 33.8,
        "max_ms": 33.8,
        "medie_ms": 33.85,
        "p95_ms": 33.8,
        "p99_ms": 33.8,
        "pauze_pe_minut": 0.27,
        "timp_oprit_pct": 0.015
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 701
      }
     ]
    },
    "functity_b0": {
     "arm": "functity_b0",
     "eticheta": "FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 143,
      "total_ms": 4275.8,
      "max_ms": 105.2,
      "medie_ms": 29.9,
      "p95_ms": 75.0,
      "p99_ms": 85.6
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      42.6,
      null,
      null
     ],
     "idle_max_ms_pe_proba": [
      42.6,
      null,
      null
     ],
     "idle_pauze_pe_minut_pe_proba": [
      102.51,
      null,
      null
     ],
     "boot_total_ms_pe_proba": [
      1371.7,
      1446.3,
      1380.8
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 50,
        "total_ms": 1448.6,
        "max_ms": 105.2,
        "medie_ms": 28.97,
        "p95_ms": 77.1,
        "p99_ms": 105.2
       },
       "pe_tip": {
        "Young": 36,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 105.2,
       "heap_dupa_ultimul_young_mb": 532.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 47.766,
       "boot_s_folosit": 46.01,
       "boot": {
        "n": 47,
        "total_ms": 1371.7,
        "max_ms": 105.2,
        "medie_ms": 29.18,
        "p95_ms": 77.1,
        "p99_ms": 105.2
       },
       "idle": {
        "n": 3,
        "total_ms": 77.0,
        "max_ms": 42.6,
        "medie_ms": 25.65,
        "p95_ms": 42.6,
        "p99_ms": 42.6,
        "pauze_pe_minut": 102.51,
        "timp_oprit_pct": 4.382
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 644
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 48,
        "total_ms": 1446.3,
        "max_ms": 85.6,
        "medie_ms": 30.13,
        "p95_ms": 66.7,
        "p99_ms": 85.6
       },
       "pe_tip": {
        "Young": 36,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 85.6,
       "heap_dupa_ultimul_young_mb": 549.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 41.546,
       "boot_s_folosit": 42.01,
       "boot": {
        "n": 48,
        "total_ms": 1446.3,
        "max_ms": 85.6,
        "medie_ms": 30.13,
        "p95_ms": 66.7,
        "p99_ms": 85.6
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 620
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 45,
        "total_ms": 1380.8,
        "max_ms": 84.2,
        "medie_ms": 30.68,
        "p95_ms": 75.0,
        "p99_ms": 84.2
       },
       "pe_tip": {
        "Young": 33,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 84.2,
       "heap_dupa_ultimul_young_mb": 544.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 39.127,
       "boot_s_folosit": 40.01,
       "boot": {
        "n": 45,
        "total_ms": 1380.8,
        "max_ms": 84.2,
        "medie_ms": 30.68,
        "p95_ms": 75.0,
        "p99_ms": 84.2
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 581
      }
     ]
    },
    "functity_b1": {
     "arm": "functity_b1",
     "eticheta": "FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 147,
      "total_ms": 4075.0,
      "max_ms": 96.7,
      "medie_ms": 27.72,
      "p95_ms": 76.4,
      "p99_ms": 93.2
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      null,
      null,
      45.0
     ],
     "idle_max_ms_pe_proba": [
      null,
      null,
      45.0
     ],
     "idle_pauze_pe_minut_pe_proba": [
      null,
      null,
      1034.48
     ],
     "boot_total_ms_pe_proba": [
      1331.5,
      1359.6,
      1339.0
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 53,
        "total_ms": 1331.5,
        "max_ms": 96.7,
        "medie_ms": 25.12,
        "p95_ms": 79.4,
        "p99_ms": 96.7
       },
       "pe_tip": {
        "Young": 39,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 96.7,
       "heap_dupa_ultimul_young_mb": 545.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 34.222,
       "boot_s_folosit": 36.01,
       "boot": {
        "n": 53,
        "total_ms": 1331.5,
        "max_ms": 96.7,
        "medie_ms": 25.12,
        "p95_ms": 79.4,
        "p99_ms": 96.7
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 683
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 47,
        "total_ms": 1359.6,
        "max_ms": 76.4,
        "medie_ms": 28.93,
        "p95_ms": 76.2,
        "p99_ms": 76.4
       },
       "pe_tip": {
        "Young": 33,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 76.4,
       "heap_dupa_ultimul_young_mb": 558.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 31.886,
       "boot_s_folosit": 32.01,
       "boot": {
        "n": 47,
        "total_ms": 1359.6,
        "max_ms": 76.4,
        "medie_ms": 28.93,
        "p95_ms": 76.2,
        "p99_ms": 76.4
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 605
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 47,
        "total_ms": 1383.9,
        "max_ms": 90.9,
        "medie_ms": 29.45,
        "p95_ms": 82.2,
        "p99_ms": 90.9
       },
       "pe_tip": {
        "Young": 33,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 90.9,
       "heap_dupa_ultimul_young_mb": 560.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 32.068,
       "boot_s_folosit": 32.01,
       "boot": {
        "n": 46,
        "total_ms": 1339.0,
        "max_ms": 90.9,
        "medie_ms": 29.11,
        "p95_ms": 82.2,
        "p99_ms": 90.9
       },
       "idle": {
        "n": 1,
        "total_ms": 45.0,
        "max_ms": 45.0,
        "medie_ms": 44.95,
        "p95_ms": 45.0,
        "p99_ms": 45.0,
        "pauze_pe_minut": 1034.48,
        "timp_oprit_pct": 77.505
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 605
      }
     ]
    },
    "oficial1237": {
     "arm": "oficial1237",
     "eticheta": "Mohist oficial 1.16.5-1237 (referinta)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 150,
      "total_ms": 4590.9,
      "max_ms": 118.6,
      "medie_ms": 30.61,
      "p95_ms": 81.0,
      "p99_ms": 114.5
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      37.0,
      null,
      null
     ],
     "idle_max_ms_pe_proba": [
      37.0,
      null,
      null
     ],
     "idle_pauze_pe_minut_pe_proba": [
      0.35,
      null,
      null
     ],
     "boot_total_ms_pe_proba": [
      1591.6,
      1475.8,
      1486.4
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 54,
        "total_ms": 1628.7,
        "max_ms": 118.6,
        "medie_ms": 30.16,
        "p95_ms": 80.9,
        "p99_ms": 118.6
       },
       "pe_tip": {
        "Young": 40,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 118.6,
       "heap_dupa_ultimul_young_mb": 572.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 222.26,
       "boot_s_folosit": 50.02,
       "boot": {
        "n": 53,
        "total_ms": 1591.6,
        "max_ms": 118.6,
        "medie_ms": 30.03,
        "p95_ms": 80.9,
        "p99_ms": 118.6
       },
       "idle": {
        "n": 1,
        "total_ms": 37.0,
        "max_ms": 37.0,
        "medie_ms": 37.05,
        "p95_ms": 37.0,
        "p99_ms": 37.0,
        "pauze_pe_minut": 0.35,
        "timp_oprit_pct": 0.022
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 696
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 48,
        "total_ms": 1475.8,
        "max_ms": 114.5,
        "medie_ms": 30.75,
        "p95_ms": 82.9,
        "p99_ms": 114.5
       },
       "pe_tip": {
        "Young": 34,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 114.5,
       "heap_dupa_ultimul_young_mb": 544.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 41.767,
       "boot_s_folosit": 42.01,
       "boot": {
        "n": 48,
        "total_ms": 1475.8,
        "max_ms": 114.5,
        "medie_ms": 30.75,
        "p95_ms": 82.9,
        "p99_ms": 114.5
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 618
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 48,
        "total_ms": 1486.4,
        "max_ms": 84.8,
        "medie_ms": 30.97,
        "p95_ms": 81.0,
        "p99_ms": 84.8
       },
       "pe_tip": {
        "Young": 34,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 84.8,
       "heap_dupa_ultimul_young_mb": 547.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 41.598,
       "boot_s_folosit": 42.01,
       "boot": {
        "n": 48,
        "total_ms": 1486.4,
        "max_ms": 84.8,
        "medie_ms": 30.97,
        "p95_ms": 81.0,
        "p99_ms": 84.8
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 618
      }
     ]
    }
   }
  },
  "38519665645": {
   "arms": {
    "catserver": {
     "arm": "catserver",
     "eticheta": "CatServer din pack (motorul istoric al serverului)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 149,
      "total_ms": 4884.5,
      "max_ms": 174.4,
      "medie_ms": 32.78,
      "p95_ms": 99.3,
      "p99_ms": 166.2
     },
     "full_gc_total": 3,
     "idle_p95_ms_pe_proba": [
      null,
      null,
      49.0
     ],
     "idle_max_ms_pe_proba": [
      null,
      null,
      49.0
     ],
     "idle_pauze_pe_minut_pe_proba": [
      null,
      null,
      71.17
     ],
     "boot_total_ms_pe_proba": [
      1723.0,
      1613.4,
      1499.1
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 50,
        "total_ms": 1723.0,
        "max_ms": 174.4,
        "medie_ms": 34.46,
        "p95_ms": 94.2,
        "p99_ms": 174.4
       },
       "pe_tip": {
        "Young": 37,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 174.4,
       "heap_dupa_ultimul_young_mb": 653.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 37.036,
       "boot_s_folosit": 37.32,
       "boot": {
        "n": 50,
        "total_ms": 1723.0,
        "max_ms": 174.4,
        "medie_ms": 34.46,
        "p95_ms": 94.2,
        "p99_ms": 174.4
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 651
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 53,
        "total_ms": 1613.4,
        "max_ms": 146.8,
        "medie_ms": 30.44,
        "p95_ms": 84.0,
        "p99_ms": 146.8
       },
       "pe_tip": {
        "Young": 38,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 146.8,
       "heap_dupa_ultimul_young_mb": 617.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 33.174,
       "boot_s_folosit": 33.31,
       "boot": {
        "n": 53,
        "total_ms": 1613.4,
        "max_ms": 146.8,
        "medie_ms": 30.44,
        "p95_ms": 84.0,
        "p99_ms": 146.8
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 688
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 46,
        "total_ms": 1548.1,
        "max_ms": 166.2,
        "medie_ms": 33.65,
        "p95_ms": 102.7,
        "p99_ms": 166.2
       },
       "pe_tip": {
        "Young": 33,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 1
       },
       "full_gc": 1,
       "young_max_ms": 166.2,
       "heap_dupa_ultimul_young_mb": 625.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 35.153,
       "boot_s_folosit": 34.31,
       "boot": {
        "n": 45,
        "total_ms": 1499.1,
        "max_ms": 166.2,
        "medie_ms": 33.31,
        "p95_ms": 102.7,
        "p99_ms": 166.2
       },
       "idle": {
        "n": 1,
        "total_ms": 49.0,
        "max_ms": 49.0,
        "medie_ms": 49.0,
        "p95_ms": 49.0,
        "p99_ms": 49.0,
        "pauze_pe_minut": 71.17,
        "timp_oprit_pct": 5.812
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 599
      }
     ]
    },
    "functity_b0": {
     "arm": "functity_b0",
     "eticheta": "FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 143,
      "total_ms": 4431.2,
      "max_ms": 83.6,
      "medie_ms": 30.99,
      "p95_ms": 70.7,
      "p99_ms": 81.4
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      null,
      null,
      42.1
     ],
     "idle_max_ms_pe_proba": [
      null,
      null,
      42.1
     ],
     "idle_pauze_pe_minut_pe_proba": [
      null,
      null,
      4.3
     ],
     "boot_total_ms_pe_proba": [
      1465.5,
      1440.6,
      1454.5
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 48,
        "total_ms": 1465.5,
        "max_ms": 83.6,
        "medie_ms": 30.53,
        "p95_ms": 74.9,
        "p99_ms": 83.6
       },
       "pe_tip": {
        "Young": 34,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 83.6,
       "heap_dupa_ultimul_young_mb": 516.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 45.626,
       "boot_s_folosit": 46.33,
       "boot": {
        "n": 48,
        "total_ms": 1465.5,
        "max_ms": 83.6,
        "medie_ms": 30.53,
        "p95_ms": 74.9,
        "p99_ms": 83.6
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 618
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 45,
        "total_ms": 1440.6,
        "max_ms": 81.4,
        "medie_ms": 32.01,
        "p95_ms": 69.0,
        "p99_ms": 81.4
       },
       "pe_tip": {
        "Young": 33,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 81.4,
       "heap_dupa_ultimul_young_mb": 550.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 41.404,
       "boot_s_folosit": 41.57,
       "boot": {
        "n": 45,
        "total_ms": 1440.6,
        "max_ms": 81.4,
        "medie_ms": 32.01,
        "p95_ms": 69.0,
        "p99_ms": 81.4
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 581
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 50,
        "total_ms": 1525.0,
        "max_ms": 76.5,
        "medie_ms": 30.5,
        "p95_ms": 69.0,
        "p99_ms": 76.5
       },
       "pe_tip": {
        "Young": 36,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 76.5,
       "heap_dupa_ultimul_young_mb": 553.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 86.236,
       "boot_s_folosit": 44.33,
       "boot": {
        "n": 47,
        "total_ms": 1454.5,
        "max_ms": 76.5,
        "medie_ms": 30.95,
        "p95_ms": 69.0,
        "p99_ms": 76.5
       },
       "idle": {
        "n": 3,
        "total_ms": 70.5,
        "max_ms": 42.1,
        "medie_ms": 23.5,
        "p95_ms": 42.1,
        "p99_ms": 42.1,
        "pauze_pe_minut": 4.3,
        "timp_oprit_pct": 0.168
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 644
      }
     ]
    },
    "functity_b1": {
     "arm": "functity_b1",
     "eticheta": "FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 139,
      "total_ms": 4375.0,
      "max_ms": 127.5,
      "medie_ms": 31.47,
      "p95_ms": 71.7,
      "p99_ms": 95.0
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      51.0,
      null,
      null
     ],
     "idle_max_ms_pe_proba": [
      51.0,
      null,
      null
     ],
     "idle_pauze_pe_minut_pe_proba": [
      350.88,
      null,
      null
     ],
     "boot_total_ms_pe_proba": [
      1558.1,
      1316.6,
      1449.3
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 50,
        "total_ms": 1609.1,
        "max_ms": 78.3,
        "medie_ms": 32.18,
        "p95_ms": 71.7,
        "p99_ms": 78.3
       },
       "pe_tip": {
        "Young": 36,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 78.3,
       "heap_dupa_ultimul_young_mb": 535.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 48.751,
       "boot_s_folosit": 48.58,
       "boot": {
        "n": 49,
        "total_ms": 1558.1,
        "max_ms": 78.3,
        "medie_ms": 31.8,
        "p95_ms": 71.7,
        "p99_ms": 78.3
       },
       "idle": {
        "n": 1,
        "total_ms": 51.0,
        "max_ms": 51.0,
        "medie_ms": 51.05,
        "p95_ms": 51.0,
        "p99_ms": 51.0,
        "pauze_pe_minut": 350.88,
        "timp_oprit_pct": 29.851
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 644
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 43,
        "total_ms": 1316.6,
        "max_ms": 94.0,
        "medie_ms": 30.62,
        "p95_ms": 71.5,
        "p99_ms": 94.0
       },
       "pe_tip": {
        "Young": 31,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 94.0,
       "heap_dupa_ultimul_young_mb": 550.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 44.479,
       "boot_s_folosit": 44.58,
       "boot": {
        "n": 43,
        "total_ms": 1316.6,
        "max_ms": 94.0,
        "medie_ms": 30.62,
        "p95_ms": 71.5,
        "p99_ms": 94.0
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 555
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 46,
        "total_ms": 1449.3,
        "max_ms": 127.5,
        "medie_ms": 31.51,
        "p95_ms": 69.5,
        "p99_ms": 127.5
       },
       "pe_tip": {
        "Young": 32,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 127.5,
       "heap_dupa_ultimul_young_mb": 551.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 42.998,
       "boot_s_folosit": 43.07,
       "boot": {
        "n": 46,
        "total_ms": 1449.3,
        "max_ms": 127.5,
        "medie_ms": 31.51,
        "p95_ms": 69.5,
        "p99_ms": 127.5
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 592
      }
     ]
    },
    "oficial1237": {
     "arm": "oficial1237",
     "eticheta": "Mohist oficial 1.16.5-1237 (referinta)",
     "java": "temurin-11 @ ubuntu-24.04 (4 vCPU, 16GB)",
     "probe_cu_jurnal": 3,
     "probe_masurate": 3,
     "stare": "MASURAT",
     "toate_pauzele": {
      "n": 141,
      "total_ms": 3671.5,
      "max_ms": 98.6,
      "medie_ms": 26.04,
      "p95_ms": 60.0,
      "p99_ms": 87.3
     },
     "full_gc_total": 0,
     "idle_p95_ms_pe_proba": [
      34.2,
      37.3,
      null
     ],
     "idle_max_ms_pe_proba": [
      34.2,
      37.3,
      null
     ],
     "idle_pauze_pe_minut_pe_proba": [
      3.85,
      0.29,
      null
     ],
     "boot_total_ms_pe_proba": [
      1176.1,
      1237.4,
      1186.4
     ],
     "probe": [
      {
       "trial": 1,
       "stare": "MASURAT",
       "total": {
        "n": 49,
        "total_ms": 1210.3,
        "max_ms": 87.3,
        "medie_ms": 24.7,
        "p95_ms": 53.1,
        "p99_ms": 87.3
       },
       "pe_tip": {
        "Young": 35,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 87.3,
       "heap_dupa_ultimul_young_mb": 536.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 55.92,
       "boot_s_folosit": 40.32,
       "boot": {
        "n": 48,
        "total_ms": 1176.1,
        "max_ms": 87.3,
        "medie_ms": 24.5,
        "p95_ms": 53.1,
        "p99_ms": 87.3
       },
       "idle": {
        "n": 1,
        "total_ms": 34.2,
        "max_ms": 34.2,
        "medie_ms": 34.21,
        "p95_ms": 34.2,
        "p99_ms": 34.2,
        "pauze_pe_minut": 3.85,
        "timp_oprit_pct": 0.219
       },
       "fisier": "gc-trial1.log",
       "linii_jurnal": 631
      },
      {
       "trial": 2,
       "stare": "MASURAT",
       "total": {
        "n": 46,
        "total_ms": 1274.7,
        "max_ms": 98.6,
        "medie_ms": 27.71,
        "p95_ms": 60.0,
        "p99_ms": 98.6
       },
       "pe_tip": {
        "Young": 34,
        "Remark": 6,
        "Cleanup": 6,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 98.6,
       "heap_dupa_ultimul_young_mb": 557.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 242.015,
       "boot_s_folosit": 32.81,
       "boot": {
        "n": 45,
        "total_ms": 1237.4,
        "max_ms": 98.6,
        "medie_ms": 27.5,
        "p95_ms": 60.0,
        "p99_ms": 98.6
       },
       "idle": {
        "n": 1,
        "total_ms": 37.3,
        "max_ms": 37.3,
        "medie_ms": 37.32,
        "p95_ms": 37.3,
        "p99_ms": 37.3,
        "pauze_pe_minut": 0.29,
        "timp_oprit_pct": 0.018
       },
       "fisier": "gc-trial2.log",
       "linii_jurnal": 594
      },
      {
       "trial": 3,
       "stare": "MASURAT",
       "total": {
        "n": 46,
        "total_ms": 1186.4,
        "max_ms": 83.3,
        "medie_ms": 25.79,
        "p95_ms": 73.7,
        "p99_ms": 83.3
       },
       "pe_tip": {
        "Young": 32,
        "Remark": 7,
        "Cleanup": 7,
        "Full": 0
       },
       "full_gc": 0,
       "young_max_ms": 83.3,
       "heap_dupa_ultimul_young_mb": 547.0,
       "heap_cap_mb": 1536.0,
       "durata_jurnal_s": 33.767,
       "boot_s_folosit": 34.05,
       "boot": {
        "n": 46,
        "total_ms": 1186.4,
        "max_ms": 83.3,
        "medie_ms": 25.79,
        "p95_ms": 73.7,
        "p99_ms": 83.3
       },
       "idle": {
        "n": 0,
        "total_ms": 0.0,
        "max_ms": null,
        "medie_ms": null,
        "p95_ms": null,
        "p99_ms": null
       },
       "fisier": "gc-trial3.log",
       "linii_jurnal": 592
      }
     ]
    }
   }
  }
 }
}```
