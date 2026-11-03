# Scorecard: performanță măsurată, moduri RP și capacitate

**Întrebarea:** care este cel mai bun motor pentru *lumea și modurile noastre*, eventual Rust, și câți jucători ține? **Verdict la 3 noiembrie 2026: nedeterminat pentru 34 moduri/13 pluginuri și clienți reali.** Niciun motor Rust nu a trecut un test cu acest pack. Nu se poate certifica „mai bun decât orice motor” fără definirea rivalilor, a sarcinii și a metricilor; rezultatele de mai jos compară numai cinci builduri valide pe o scenă publică redusă. Nu am instalat nimic pe live.

## Toate cifrele comparabile disponibile pentru cele cinci motoare

[Sursa primară: jobul 41607833576](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41607833576), adnotări F/C/O/X/Q din jobul `all-five-same-runner` (check run `125822003891`); metoda în [`fc_cuantic_all_engines_ab.py`](../../scripts/fc_cuantic_all_engines_ab.py). **Un singur runner, Java 11, lume generată resetată, 18 moduri publice, 6 pluginuri, 80 zombie, 0 clienți**, ordinea F/C/O/X/Q/Q/X/O/C/F. Fiecare pereche și mediana ei sunt din *același* job; nu includem rezultate din alte joburi în clasament.

| Motor | CPU s/~30 s (1 / 2), mediană | Tick mediu `forge tps` ms (1 / 2), mediană | RSS median eșantionat MiB (1 / 2), mediana perechii |
|---|---:|---:|---:|
| F — FunCity arhivat | 5,11 / 4,64 → **4,875** | 1,25 / 1,08 → **1,165** | 2691,16 / 2802,70 → **2746,93** |
| C — CatServer vechi | 2,15 / 2,10 → **2,125** | 0,36 / 0,40 → **0,380** | 2575,36 / 2603,74 → **2589,55** |
| O — CatServer oficial | 2,18 / 1,77 → **1,975** | 0,37 / 0,36 → **0,365** | 2619,38 / 2585,07 → **2602,23** |
| X — FunCity din sursă | 2,08 / 1,71 → **1,895** | 0,38 / 0,37 → **0,375** | 2469,15 / 2485,61 → **2477,38** |
| Q — Cuantic din aceeași sursă | 1,81 / 2,27 → **2,040** | 0,34 / 0,37 → **0,355** | 2408,22 / 2436,10 → **2422,16** |

**Derivări aritmetice, nu teste noi:** X are cel mai mic CPU median în acea scenă (**1,895 s**), Q cel mai mic tick mediu al perechii (**0,355 ms**) și RSS eșantionat (**2422,16 MiB**). Q a folosit **~3,29% mai mult CPU median decât O** (`2,040 / 1,975 − 1`), ~7,65% mai mult decât X; RSS-ul Q a fost cu **~180,07 MiB mai jos** decât O (medianele perechilor). Două probe, RSS *median al eșantioanelor*, tick **mediu raportat de Forge**, valorile rotunjite și variația runnerului nu demonstrează un avantaj persistent. X nu domină la tick; Q nu domină la CPU. **Niciun „cel mai bun pe toate axele”.** Q respectă pragurile absolute istorice CPU ≤2,515 s și tick ≤1,50/1,52 ms, dar **pică condiția CPU median ≤ oficial în același job**, deci [Cuantic rămâne necalificat](CUANTIC-GATE.md).

## Ce statistică avem și ce NU avem

| Metrică / funcție | Această scenă publică | Pe lumea RP 34/13 cu clienți | Ce ar necesita pentru verdict |
|---|---|---|---|
| CPU proces / ~30 s | **Măsurat de două ori/motor**, tabelul de mai sus. | **NEMĂSURAT** | CPU total + fir principal sub sarcină reală; nu echivalează CPU idle cu capacitate. |
| Tick mediu Forge | **Măsurat**, fără distribuție completă a tickurilor. | **NEMĂSURAT** | MSPT per tick, p50/p95/p99, TPS efectiv; trafic, mașini, NPC și chunkuri. |
| RSS (memorie rezidentă) | **Mediana a șase probe în fereastra de test**, nu vârful. | **NEMĂSURAT** | RSS vârf și evoluție lungă; heap, GC, memorie native, cache OS. |
| Boot și încărcare pluginuri | Toate trialurile au trecut `Done`, activare și oprire curată; **timpii de boot nu sunt publicați în tabelul acestui job**. | **NEMĂSURAT împreună 34/13 pe candidatul nou** | Identitate/hash JAR, 34/34 + 13/13 încărcate fără erori; două booturi pe copie. |
| Login modat, autentificare, voice UDP, vehicule, economie, CoreProtect, salvare/restart | **NU AU FOST TESTATE cu clienți** | **NEMĂSURAT** | 2 clienți Forge reali, anti-impersonare, condus, protecții, voice reciproc, backup/restore. |
| Rețea, upload/UDP, disk IO, GC pauses, lag p99, FPS client, chunk-load latency | **NEMĂSURATE** în clasamentul 5 motoare. | **NEMĂSURATE** | Sesiuni instrumentate pe aceeași copie/hardware, cu clienți RP și trafic comparabil. |
| Jucători simultani susținuți | **0 conectați** la fiecare trial. | **NECUNOSCUT** | Rampă controlată 5→10→15→20; fără extrapolare din idle, `max-players` ori numărul de zombie. |
| Motor Rust nativ | **Niciun braț Rust** în test. | **Nu există candidat compatibil 34/13 validat** | Portări funcționale/client/registru/lume și poarta 47/47 înainte de compararea vitezei. |

**Alți rivali:** Arclight, Mist, Mohist/Tenet și Paper/Folia/Pumpkin nu au încheiat *aceeași* scenă cu toate condițiile de compatibilitate, deci rămân **neclasați**, nu sunt „învinși” de cifrele F/C/O/X/Q. Paper/Folia/Rust nu încarcă direct JAR-urile Forge 1.16.5 cerute. Un boot parțial ori bench pe pack diferit nu probează că merg modurile voastre.

## Care motor merită continuat pentru modurile voastre?

Trei direcții cu costuri diferite: **(1) Rust nativ** poate fi eficient `[presupus]`, dar fără runtime Forge și portarea contractelor pentru cele 47 JAR-uri nu este încă un substitut; **(2) Rust pentru un hot path în CatServer** păstrează modul de joc dacă este validat JNI, dar nu rezolvă tickul ca atare; **(3) CatServer oficial/derivat cu Forge+Bukkit** poate încărca JAR-urile actuale și este **baseline de TEST**, nu câștigător de capacitate certificat. Alegem (3) drept martor pentru pachetul real și dezvoltăm (1) numai ca pilot separat; nicio variantă nu este declarată „mai bună decât orice” înainte de A/B real. [Contractele de migrare Rust și auditul privat](RUST-MIGRARE-47-COMPONENTE-SI-CAPACITATE.md) sunt pregătite, dar **nu avem aici copia privată sau testul client**.

Pentru a afirma o superioritate **în acest RP**:

1. **Copie inactivă, backup verificat, inventar local privat SHA-256** pentru exact 34 moduri/13 pluginuri, fără a urca lumea/JAR-urile/logurile; cele șase moduri suplimentare față de ținta publică de 28 nu se ghicesc. [Inventarul offline](../../scripts/fc_rust_migration_inventory.py) este pregătit și a trecut teste pe fixture, nu pe packul privat. Proba resurselor TEST [41446267019](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41446267019) a avut jobul privat **anulat**, nu furnizează măsurători de capacitate.
2. **Compatibilitate înainte de viteză:** 34/34 și 13/13, ID-uri de bloc/entitate/inventar păstrate, două booturi, doi clienți Forge reali, auth/voice/vehicule/RP/protecții și două restarturi, restore plus rollback. La primul defect, candidatul se respinge chiar dacă CPU e mai mic. Motorul Rust ar avea nevoie de evaluator propriu (nu falsificăm schema Java 11 a verdictului actual).
3. **Benchmark cu aceeași scenă și hardware verificat**, martor O vs candidat compatibil: A/B/B/A la 5→10→15→20 clienți, ≥5 minute încălzire și ≥20 minute măsurate/sesiune, două treceri pe treaptă, stop la primul eșec. TPS ≥19,5, MSPT p95 ≤35 ms și p99 ≤45 ms, CPU total ≤75% din 2 vCPU **plus fir principal fără saturație**, RSS ≤ RAM măsurată −2048 MiB, uplink ≤70%, GC stabil și zero erori/defecte RP. Proba se face pe host echivalent; **12 GB sunt ținta planificată, istoricul hostului activ include 3 GiB**, deci nu pretindem rezultate 2 vCPU/12 GB din CI.
4. Un candidat „ține mai mulți” numai dacă trece **2/2** o treaptă la care O eșuează **2/2**, fără pierderi funcționale. O limită publică prudentă ar fi ≤80% din cea mai înaltă treaptă confirmată. Exemplu **condițional**, nu estimare actuală: 10 trecuți și 15 eșuați → cel mult 8 sloturi. **Astăzi nu avem nici 5 validați pe 34/13**, deci cifra reală rămâne necunoscută.

Acest raport nu instalează un motor, nu promite portarea tuturor modurilor și nu expune date private. Următorul rezultat numeric valid cere acces la **copia TEST izolată**, nu la live; până atunci pot arăta numai cifrele de mai sus și limitele lor.
