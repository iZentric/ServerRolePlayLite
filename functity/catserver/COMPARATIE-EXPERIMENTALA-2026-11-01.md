# FunCity 1.16.5 — comparație reproductibilă, NU plafon de jucători

**1 noiembrie 2026.** Am rulat două joburi GitHub, pe câte un runner efemer/Java 11 per job, cu aceeași lume generată, 18 moduri istorice deja publice, 6 pluginuri, FerriteCore/ModernFix/RoadRunner și 80 mobi. Cele 6 trialuri din fiecare job au două repetiții pe motor; JAR-urile sunt identificate SHA-256, sursa custom este construită din pinul CatServer cu patchurile 0001–0003, iar binarul/seedul custom dispar odată cu runnerul. **0 clienți în toate trialurile.** Runnerul nu este hostul declarat 2 vCPU/12 GB; nu comparăm numeric între joburi, ci numai între brațele aceluiași job.

| Job / ordine | Motor | CPU s / ~30 s, două trialuri | RSS MiB | Tick mediu ms (`forge tps`) |
|---|---|---:|---:|---:|
| [41332962178](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41332962178), F/C/O/O/C/F | FunCity arhivat | 6,46 / 7,30 | 2926 / 2751 | 2,38 / 2,49 |
| același | CatServer vechi | 3,63 / 3,49 | 2669 / 2505 | 1,14 / 1,25 |
| același | CatServer oficial | 3,17 / 3,34 | 2676 / 2439 | 1,25 / 1,12 |
| [41334471306](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41334471306), F/X/O/O/X/F | FunCity arhivat | 6,27 / 8,50 | 2217 / 2314 | 3,44 / 3,27 |
| același | **FunCity custom 0001–0003** | **5,25 / 4,17** | 2057 / 2186 | **2,31 / 2,04** |
| același | CatServer oficial | 5,87 / 3,74 | 2263 / 2233 | 2,45 / 2,14 |

**Decizie de laborator:** păstrăm **FunCity custom bazat pe CatServer** drept candidat privat: a fost sub FunCity arhivat la CPU și tick în ambele trialuri ale rundei care l-a inclus. Față de CatServer oficial, diferența de CPU median (~4,71 vs ~4,81 s/30 s) este prea mică/variabilă ca să susțină un câștig de viteză; patchurile custom sunt în primul rând de corectitudine. Runda separată cu CatServer vechi/actual a favorizat familia CatServer față de FunCity arhivat în scena ei, nu demonstrează că oricare din acestea duce mai mulți jucători.

**Ce NU este testat:** lumea RP, 34/34 moduri, 13/13 pluginuri, client Forge/autentificare/voice/vehicule, MSPT p95/p99, 2 vCPU/12 GB reali și o rampă de jucători. Nu transformăm `max-players`, 80 mobi sau media tickului în număr de jucători. Pentru verdictul cerut trebuie o copie privată izolată pe hardware comparabil, resurse/backup confirmate, clienți reali 5→10→15→20, A/B/B/A și [poarta H5](GOALS.md). Jobul read-only [41332962136](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41332962136) are fixture-urile hosted trecute, însă proba PC este încă în așteptarea runnerului; nu validează hardware-ul hostului.
