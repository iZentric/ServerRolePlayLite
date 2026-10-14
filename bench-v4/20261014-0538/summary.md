# FC-BENCH v4 — rezultate (masurate, nu estimate)

Metoda: boot la cald, 3 probe/arm, world comun post-instalare, java 11, -Xmx1536M, pack 36/14 cu SHA fix.
Deviatii declarate: seed fix, online-mode=false pentru probele de login, view-distance=10, check_update=false (Mohist).

| brat | stare | boot_mediu_s | CV% | join_mediu_ms | TPS_p50 | overrun | overrun_max_ms | critice | RSS_MB | CPU% | GC_max_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | MASURAT | 43.35 | 4.3 | None | 20.0 | 0 | 0 | 0 | 2227.8 | 2.5 | None |
| Mohist oficial 1.16.5-1237 (referinta) | MASURAT | 44.68 | 8.5 | None | 20.0 | 0 | 0 | 0 | 2254.6 | 2.7 | None |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | MASURAT | 42.68 | 5.8 | None | 20.0 | 0 | 0 | 0 | 2267.6 | 2.4 | None |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | MASURAT | 33.34 | 5.7 | None | 20.0 | 0 | 0 | 0 | 2256.1 | 1.8 | None |

## Verdicturi comparative

- boot_medie_s functity_b1 vs functity_b0: 33.34 vs 42.68 (-21.9%) — functity_b1 MAI BINE
- boot_medie_s functity_b0 vs oficial1237: 42.68 vs 44.68 (-4.5%) — functity_b0 MAI BINE
- boot_medie_s functity_b1 vs oficial1237: 33.34 vs 44.68 (-25.4%) — functity_b1 MAI BINE
- join_medie_ms functity_b1 vs oficial1237: NEMASURAT (lipsa date)
- rss_medie_mb functity_b1 vs oficial1237: 2256.1 vs 2254.6 (+0.1%) — functity_b1 MAI PROST
- tps_p50 functity_b1 vs oficial1237: 20.0 vs 20.0 (+0.0%) — functity_b1 egal
- boot_medie_s oficial1237 vs catserver: 44.68 vs 43.35 (+3.1%) — oficial1237 MAI PROST

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
