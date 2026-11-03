# FunCity 1.16.5 — comparație reproductibilă, NU plafon de jucători

**1 noiembrie 2026; actualizat 3 noiembrie.** Am rulat trei joburi GitHub, pe câte un runner efemer/Java 11 per job, cu aceeași lume generată, 18 moduri istorice deja publice, 6 pluginuri, FerriteCore/ModernFix/RoadRunner și 80 mobi. Cele 6 trialuri din fiecare job au două repetiții pe motor; JAR-urile sunt identificate SHA-256, sursa custom este construită din pinul CatServer cu patchurile 0001–0003, iar binarul/seedul custom dispar odată cu runnerul. **0 clienți în toate trialurile.** Runnerul nu este hostul declarat 2 vCPU/12 GB; nu comparăm numeric între joburi, ci numai între brațele aceluiași job.

| Job / ordine | Motor | CPU s / ~30 s, două trialuri | RSS MiB | Tick mediu ms (`forge tps`) |
|---|---|---:|---:|---:|
| [41332962178](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41332962178), F/C/O/O/C/F | FunCity arhivat | 6,46 / 7,30 | 2926 / 2751 | 2,38 / 2,49 |
| același | CatServer vechi | 3,63 / 3,49 | 2669 / 2505 | 1,14 / 1,25 |
| același | CatServer oficial | 3,17 / 3,34 | 2676 / 2439 | 1,25 / 1,12 |
| [41334471306](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41334471306), F/X/O/O/X/F | FunCity arhivat | 6,27 / 8,50 | 2217 / 2314 | 3,44 / 3,27 |
| același | **FunCity custom 0001–0003** | **5,25 / 4,17** | 2057 / 2186 | **2,31 / 2,04** |
| același | CatServer oficial | 5,87 / 3,74 | 2263 / 2233 | 2,45 / 2,14 |
| [41573354240](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41573354240), F/X/O/O/X/F | FunCity arhivat | 9,57 / 6,72 | 2680 / 2294 | 3,30 / 2,83 |
| același | FunCity custom 0001–0003 | 2,90 / 3,51 | 2223 / 2083 | 1,59 / 1,52 |
| același | **CatServer oficial** | **2,72 / 2,31** | 2244 / 2322 | **1,52 / 1,50** |

**Decizie de laborator:** păstrăm **FunCity custom bazat pe CatServer** drept candidat privat, nu drept câștigător de viteză. X a fost sub FunCity arhivat la CPU în ambele runde care l-au inclus. În prima rundă X/O CPU median a fost ~4,71 / ~4,81 s/30 s; în runda din 3 noiembrie, **O a consumat mai puțin CPU decât X în ambele repetiții** (median ~2,52 / ~3,21 s) și a avut tick mediu puțin mai mic. Nu combinăm medianele între joburi și nu ascundem această inversare: **niciun avantaj stabil al X față de O nu este demonstrat**; patchurile X sunt în primul rând corecții de compatibilitate. Runda separată cu CatServer vechi/actual a favorizat familia CatServer față de FunCity arhivat în scena ei, nu demonstrează că oricare duce mai mulți jucători.

După cele șase trialuri din [41573354240](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41573354240), candidatul X cu **ambele JAR-uri experimentale adăugate**, Starlight + Chunk Sending (18 originale + 2, 6 pluginuri), a atins `Done` și s-a oprit curat pe o nouă copie generată. **Aceasta este doar o probă de boot, nu un A/B de performanță** pentru addonuri: fără clienți, pachete trimise, încărcare independent verificată sau lumea 34/13. Nu se publică JAR-uri/loguri brute.

**Ce NU este testat:** lumea RP, 34/34 moduri, 13/13 pluginuri, client Forge/autentificare/voice/vehicule, MSPT p95/p99, 2 vCPU/12 GB reali și o rampă de jucători. Nu transformăm `max-players`, 80 mobi sau media tickului în număr de jucători. Pentru verdictul cerut trebuie o copie privată izolată pe hardware comparabil, resurse/backup confirmate, clienți reali 5→10→15→20, A/B/B/A și [poarta H5](GOALS.md). Jobul read-only [41332962136](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41332962136) a trecut fixture-urile hosted, dar proba PC a fost anulată; [sonda TEST 41446267019](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41446267019) rămâne în coadă. Niciuna nu validează hardware-ul hostului.
