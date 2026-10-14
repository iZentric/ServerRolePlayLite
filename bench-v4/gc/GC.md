# FC-GC — pauze GC masurate din jurnalele FC-BENCH

FC-GC: pauzele STW din -Xlog:gc* (Java 11 G1) ale alergarilor FC-BENCH v4, reprocesate din artefactele CI fara alergare noua; percentile nearest-rank; boot/idle despartite la boot_timp_real_s al fiecarei probe

## Alergare 38510786719

| brat | probe | boot: pauze/proba | boot: total ms/proba | boot max ms | boot p95 ms | idle (dupa Done): pauze / fereastra | idle max ms | Full-GC | heap dupa ultimul young (MB) |
|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | 3/3 | 49/47/53 | 1479/1545/1536 | 146.3 | 94.6 | 2 / 929 s (0.13/min) | 33.8 | 3 — (System.gc()) @0.534s 5.061ms; (System.gc()) @0.555s 4.787ms; (System.gc()) @0.555s 5.139ms | 635/624/632 |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | 3/3 | 47/48/45 | 1372/1446/1381 | 105.2 | 75.0 | 3 / 929 s (0.19/min) | 42.6 | 0 | 532/549/544 |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | 3/3 | 53/47/46 | 1332/1360/1339 | 96.7 | 76.4 | 1 / 928 s (0.07/min) | 45.0 | 0 | 545/558/560 |
| Mohist oficial 1.16.5-1237 (referinta) | 3/3 | 53/48/48 | 1592/1476/1486 | 118.6 | 81.0 | 1 / 929 s (0.07/min) | 37.0 | 0 | 572/544/547 |

## Alergare 38519665645

| brat | probe | boot: pauze/proba | boot: total ms/proba | boot max ms | boot p95 ms | idle (dupa Done): pauze / fereastra | idle max ms | Full-GC | heap dupa ultimul young (MB) |
|---|---|---|---|---|---|---|---|---|---|
| CatServer din pack (motorul istoric al serverului) | 3/3 | 50/53/45 | 1723/1613/1499 | 174.4 | 99.3 | 1 / 928 s (0.07/min) | 49.0 | 3 — (System.gc()) @0.437s 5.378ms; (System.gc()) @0.459s 5.679ms; (System.gc()) @0.473s 5.726ms | 653/617/625 |
| FunCity b0 — build propriu, pin 754b578e, FARA patch-uri (baseline) | 3/3 | 48/45/47 | 1466/1441/1454 | 83.6 | 70.7 | 3 / 929 s (0.19/min) | 42.1 | 0 | 516/550/553 |
| FunCity b1.2256 — baseline + P0b/P0c/P0d + P1 dropper-guard | 3/3 | 49/43/46 | 1558/1317/1449 | 127.5 | 71.7 | 1 / 929 s (0.07/min) | 51.0 | 0 | 535/550/551 |
| Mohist oficial 1.16.5-1237 (referinta) | 3/3 | 48/45/46 | 1176/1237/1186 | 98.6 | 68.0 | 2 / 929 s (0.13/min) | 37.3 | 0 | 536/557/547 |

Semnificatie: pauza = timp in care TOATE firele serverului stau (STW). Un tick are 50 ms; o pauza sub ~10 ms
nu se vede in joc, una peste 50 ms = tick sarit. `boot` = de la pornirea JVM pana la `Done` (incarcare moduri,
nu gameplay). `idle` = dupa `Done`, server gol cu 36 moduri + 14 plugini, fara jucatori — 0 pauze inseamna
ca heap-ul nu s-a umplut in fereastra, nu ca GC-ul ar fi gratuit sub sarcina. Full-GC cu `(System.gc())`
= cerut explicit de cod la pornire, nu presiune de memorie.
