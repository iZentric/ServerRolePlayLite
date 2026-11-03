# FunCity — tabel de performanță cu și fără jucători

**3 noiembrie 2026.** Serverul dorit este Forge+Bukkit 1.16.5, lumea RP și pachetul privat **34 moduri/13 pluginuri**, pe ținta declarată **2 vCPU/12 GB**. Prototipul WebGL2 din repository **nu** este acest server și nu furnizează date de capacitate.

## Fără jucători: măsurat, dar NU pe pachetul vostru

Ultimul A/B din același [job 41573354240](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41573354240): Java 11, runner GitHub (nu gazda de 2 vCPU), lume generată, **18 moduri publice / 6 pluginuri / 80 mobi / 0 clienți**. Două trialuri pe motor, F/X/O/O/X/F; mediana se calculează **numai în acest job**. Tickul afișat este *mediu*, nu p95.

| Motor | CPU s / ~30 s, cele două trialuri | CPU median s / ~30 s | Tick mediu ms, cele două trialuri | RSS MiB, cele două trialuri |
|---|---:|---:|---:|---:|
| FunCity vechi arhivat | 9,57 / 6,72 | 8,145 | 3,30 / 2,83 | 2680 / 2294 |
| FunCity sursă CatServer + patchuri `0001`–`0003` | 2,90 / 3,51 | 3,205 | 1,59 / 1,52 | 2223 / 2083 |
| **CatServer oficial** | **2,72 / 2,31** | **2,515** | **1,52 / 1,50** | 2244 / 2322 |

În acest job CatServer oficial a consumat **mai puțin CPU decât candidatul FunCity** în ambele trialuri; în [jobul anterior 41334471306](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41334471306) erau aproape la egalitate. **Nu** calculăm o medie între joburi și **nu** deducem câți jucători încap din 0 clienți/18/6.

## Cu jucători: numai estimare de buget, NU capacitate măsurată

[Presupus] Model ilustrativ **liniar** pentru lucrul pe firul principal când toți jucătorii produc sarcină comparabilă: `cost_tick ≈ B + N × c`, unde `B` este costul de bază **necunoscut pe lumea 34/13** și `c` este costul incremental **necunoscut** al unui jucător activ. H5 cere p95 MSPT **≤35 ms**, p99 **≤45 ms**, TPS **≥19,5**. Columna `35/N` este doar **limita optimistă matematică pentru c dacă B=0**; în realitate B>0 și comportamentul nu este neapărat liniar. Nu este un MSPT prognozat, o rată observată per jucător sau o cifră de sloturi.

| Clienți Forge simultani | Buget optimist `35/N` ms per jucător activ (B=0) | MSPT/TPS/CPU/RSS real pe 34/13 | Decizie de test |
|---:|---:|---|---|
| **0** | nu se aplică | necunoscut pe 34/13; tabelul de mai sus este altă scenă | bootul privat + profil de bază |
| **5** | 7,00 | **nemăsurate** | prima treaptă H5 |
| **10** | 3,50 | **nemăsurate** | numai după treapta 5 |
| **15** | 2,33 | **nemăsurate** | numai după treapta 10 |
| **20** | 1,75 | **nemăsurate** | numai după treapta 15 |
| **30** | 1,17 | **nemăsurate** | ținta inițială cerută, nu un rezultat |
| **60** | 0,58 | **nemăsurate** | obiectiv ulterior, condiționat de probe |
| **100** | 0,35 | **nemăsurate** | obiectiv viitor; hardware-ul poate necesita upgrade |

[Presupus] La 12 **GiB** efectivi, poarta H5 ar limita RSS la **≤10.240 MiB** (2 GiB rezervate OS/cache), CPU total la **≤75% din cele două vCPU alocate**, uplink la **≤70%**. Dacă planul este 12 GB zecimali, limita MiB se recalculează după măsurarea cgroup/hostului; **nici limita reală, nici un maxim de jucători nu sunt confirmate**. Testul de capacitate cere aceeași lume/pack, clienți reali, A/B/B/A cu ≥5 min încălzire și ≥20 min măsurate per sesiune, două treceri la nivelul superior unde baseline eșuează de două ori, plus auth/voice/vehicule/RP/rollback. Vezi [criteriile H5](GOALS.md).

**Verdict actual:** fără jucători există doar măsurarea publică 18/6; **cu jucători pe 34/13 nu există încă nici măsurători, nici o estimare numerică defensibilă a capacității**. Jobul pentru resursele TEST [41446267019](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41446267019) rămâne în coadă. Nu se schimbă live-ul sau numărul de sloturi din acest tabel.
