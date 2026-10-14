# FC-BENCH v4 — rezultate (masurate, nu estimate)

Metoda: boot la cald, 3 probe/arm, world comun post-instalare, java 11, -Xmx1536M, pack 36/14 cu SHA fix.
Deviatii declarate: seed fix, online-mode=false pentru probele de login, view-distance=10, check_update=false (Mohist).

| brat | stare | boot_mediu_s | boot_uptime_s | CV% | join_mediu_ms | TPS_p50 | MSPT_ms | overrun | overrun_max_ms | critice | RSS_MB | CPU% | GC_max_ms | GC_p95_ms | Full-GC | GC_idle_max_ms/proba |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | MASURAT | 42.41 | None | 2.8 | None | 20.0 | 0.08 | 0 | 0 | 0 | 2214.0 | 2.3 | 151.2 | 106.0 | 3 | [31.2, 44.3, 0.0] |
| Mohist oficial 1.16.5-1237 (referinta) | MASURAT | 45.0 | None | 4.5 | None | 20.0 | 0.18 | 0 | 0 | 0 | 2263.9 | 2.9 | 131.6 | 107.6 | 0 | [51.1, 0.0, 66.7] |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | MASURAT | 42.24 | None | 7.3 | None | 20.0 | 0.09 | 0 | 0 | 0 | 2229.6 | 2.4 | 112.4 | 83.8 | 0 | [41.4, 50.9, 0.0] |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | MASURAT | 37.74 | None | 5.6 | None | 20.0 | 0.08 | 0 | 0 | 0 | 2245.2 | 1.7 | 144.2 | 92.1 | 0 | [0.0, 0.0, 54.5] |

## Verdicturi comparative

- boot_medie_s functity_b1 vs functity_b0: 37.74 vs 42.24 (-10.7%) — functity_b1 MAI BINE
- boot_medie_s functity_b0 vs oficial1237: 42.24 vs 45.0 (-6.1%) — functity_b0 MAI BINE
- boot_medie_s functity_b1 vs oficial1237: 37.74 vs 45.0 (-16.1%) — functity_b1 MAI BINE
- join_medie_ms functity_b1 vs oficial1237: NEMASURAT (lipsa date)
- rss_medie_mb functity_b1 vs oficial1237: 2245.2 vs 2263.9 (-0.8%) — functity_b1 MAI BINE
- tps_p50 functity_b1 vs oficial1237: 20.0 vs 20.0 (+0.0%) — functity_b1 egal
- mspt_medie_ms functity_b1 vs oficial1237: 0.08 vs 0.18 (-55.6%) — functity_b1 MAI BINE
- gc_pauza_max_ms functity_b1 vs oficial1237: 144.2 vs 131.6 (+9.6%) — functity_b1 MAI PROST
- gc_pauza_max_ms functity_b1 vs catserver: 144.2 vs 151.2 (-4.6%) — functity_b1 MAI BINE
- boot_medie_s oficial1237 vs catserver: 45.0 vs 42.41 (+6.1%) — oficial1237 MAI PROST

## Praguri (fixate INAINTE de rulare)

- catserver: boot CV<10%: TRECUT
- oficial1237: boot CV<10%: TRECUT
- functity_b0: boot CV<10%: TRECUT
- functity_b1: boot CV<10%: TRECUT
- functity_b1: 0 erori critice pe 3 probe: TRECUT

## Semnificatie si limite

- 'boot_medie_s' = timp real de pornire pana la 'Done' (Include FML+plugini, world deja existent). Nu e un castig de gameplay.
- TPS vine din comenzile console; NEMASURAT inseamna ca motorul nu le publica parseabil, NU ca ar fi 20.
- probele de login masoara intarzierea de logare headless (offline); nu includ ecranul de asset-uri al clientului.
- overrun = numar de 'Can't keep up!' in fereastra masurata; 0 nu garanteaza absenta sub 120s idle.
- MSPT = 'Overall: Mean tick time' din `forge tps` (media Forge de la pornire, server gol); NEMASURAT daca motorul nu raspunde la comanda.
- GC = pauze STW din -Xlog:gc* (JDK 11 G1): max/p95 pe toate pauzele (majoritatea la boot), Full-GC numarate, idle = dupa Done; vezi analysis/FUNCTITY-GC.md pentru metoda.
