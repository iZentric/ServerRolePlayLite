# Cuantic față de cele cinci motoare compatibile testate — același job

**Sursa:** [GitHub Actions 41607833576](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41607833576), job `all-five-same-runner` **SUCCESS**, adnotările `F`, `C`, `O`, `X`, `Q` (și `Five public engines complete`). Scriptul este [`fc_cuantic_all_engines_ab.py`](../../scripts/fc_cuantic_all_engines_ab.py). Un singur runner Ubuntu 24.04, Java 11, aceeași lume generată și resetată pentru fiecare probă; **18 moduri publice, 6 pluginuri, 80 zombie, 0 jucători conectați**. Ordine palindromică `F/C/O/X/Q/Q/X/O/C/F`, două probe pe motor. Toate cele zece probe au pornit/oprit și au trecut validările; valorile se publică doar la serie completă. Aceasta **nu** este lumea RP privată (34 moduri/13 pluginuri), hostul de 2 vCPU/12 GB sau un test de conectare a clienților. Nu extrapolăm capacitatea de jucători.

| Motor (SHA-256 prefix) | CPU s/~30 s, probele 1 / 2 | Mediană CPU s | Tick mediu raportat de `forge tps`, ms, 1 / 2 | RSS median eșantionat, MiB, 1 / 2 |
|---|---:|---:|---:|---:|
| **F — FunCity arhivat** (`d6ffa35c…`) | 5,11 / 4,64 | 4,875 | 1,25 / 1,08 | 2691,16 / 2802,70 |
| **C — CatServer vechi** (`96f82479…`) | 2,15 / 2,10 | 2,125 | 0,36 / 0,40 | 2575,36 / 2603,74 |
| **O — CatServer oficial** (`8edea98c…`) | 2,18 / 1,77 | 1,975 | 0,37 / 0,36 | 2619,38 / 2585,07 |
| **X — FunCity din sursă** (`a712f038…`) | 2,08 / 1,71 | **1,895** | 0,38 / 0,37 | 2469,15 / 2485,61 |
| **Q — Cuantic din aceeași sursă** (`967a6871…`) | 1,81 / 2,27 | 2,040 | **0,34 / 0,37** | **2408,22 / 2436,10** |

**Cum citim tabelul:** CPU este timpul procesului dintr-o fereastră de ~30 s (mai mic = mai bine); tick-ul este *valoarea medie raportată de Forge*, calculată în script ca mediana ultimelor șase răspunsuri `forge tps` din fiecare probă — **nu p95/p99**, nu latența cu jucători. RSS este mediana a șase eșantioane din fereastră, **nu vârful RAM**, nici memoria necesară întregului pack. Două probe/motor nu dovedesc stabilitate statistică; nu există un câștigător absolut. X are cea mai mică mediană CPU **numai în acest job**; Q are cele mai mici valori RSS observate și tick-uri mici, dar nu câștigă toate măsurile.

**Poarta Cuantic rămâne respinsă:** Q (2,040 s) respectă plafonul istoric absolut 2,515 s și tick-urile 0,34/0,37 respectă 1,50/1,52 ms. Însă în **același job** Q are CPU median mai mare decât O (2,040 > 1,975 s, ~3,3%) și X (2,040 > 1,895 s, ~7,7%). Tick-urile Q sortate 0,34/0,37 nu depășesc O sortat 0,36/0,37; acest lucru **nu compensează** încălcarea cerinței CPU ≤ oficial. Screeningul anterior [O/Q/Q/O 41591063563](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41591063563) a respins Q și la CPU, și la tick; nu amestecăm numeric valorile dintre acele două joburi. **Nu promovăm, publicăm sau instalăm Cuantic pe live.**

**De ce a fost mai lent?** Măsurarea arată *că* în această serie Q a consumat mai mult CPU median decât O și X, nu *de ce*. Identitatea din patchurile 0001 (X) și 0004 (Q) are aceeași semantică în sursă, în afara a două șiruri de branding; veto-urile Forge/Bukkit 0002/0003 sunt identice, fără patch de performanță Cuantic. `[presupus]` Variația de încălzire JVM, GC și încărcarea runnerului ar putea contribui la diferența dintre cele două probe; profilarea JFR A/B pe scena identică, cu suficiente repetări, este necesară pentru a atribui costul unui subsistem. **Nu atribuim fără date CPU-ul brandingului, GC-ului ori unui mod.** Testarea pe copia TEST 34/13 cu clienți reali și rollback rămâne necesară înainte de orice decizie de producție.

## „Toate” celelalte familii cunoscute — fără clasament numeric fals

| Familie | De ce nu este rând comparabil în acest job |
|---|---|
| Arclight Forge 1.16.5 | A trecut un smoke cu packul public 15/6 într-un test anterior, dar a eșuat la boot cu un pack istoric diferit; nu a parcurs acest job 18/6/80, fără CPU/tick comun. |
| Mist 1.16.5 | Nu a ajuns la `Done` în stage-ul 15/6 și a eșuat și pe un alt pack istoric; nu există probă de performanță validă pentru scena de aici. |
| Mohist/Tenet, forkuri vechi Cuantic, Paper/Folia/Rust | Packuri/protocoale/JDK-uri sau arhitecturi diferite; fără probă completă pe același runner și aceeași scenă. Paper/Folia/Rust nu încarcă direct modurile Forge 1.16.5 cerute. |

[Istoricul probelor pe familii și limitările lor](../../agent/MOTOR-TABEL-VERIFICAT.md) nu trebuie combinat numeric cu tabelul de mai sus. Alegerea minimă reversibilă CatServer păstrează API-urile Forge+Bukkit; un transplant mare de tick/chunk crește riscul pentru moduri, iar o rescriere Paper/Rust pierde suportul direct Forge. Alegerea este una de **compatibilitate de testat**, nu o afirmație că Q este mai rapid. Live-ul este neatins.
