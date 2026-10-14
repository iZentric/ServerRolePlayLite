# FC-GC — pauze GC masurate din jurnalele FC-BENCH

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
