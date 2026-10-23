# FunCity Capacity — candidat 1.16.5/Java 11, NU instalare

**Alegere:** cod sursă derivat din [CatServer 23.05.26-1 LGPL-3.0](https://github.com/Luohuayu/CatServer/releases/tag/23.05.26-1), pin `1d8d63138be77a606df2a5e940b960065948f983`, cu [patchul de identitate FunCity](../catserver/patches/0001-funcity-operator-identity.patch). Numele de operator și loggerul sunt FunCity; păstrăm creditul, licența, namespace-urile/configul necesare compatibilității. **În acest punct nu există motor FunCity compilat/validat ori patch de performanță măsurat.** Nici Java 11 boot, nici loginul/modurile/pluginurile reale, nici capacitatea nu sunt demonstrate de branding.

## Braț reversibil de distanță (numai în repo)

- Baseline `functity-config/server.properties`: `view-distance=5`, watchdog dezactivat istoric (`max-tick-time=-1`).
- Candidat [3g-view4/server.properties](3g-view4/server.properties): **view-distance=4** și `max-tick-time=60000`; restul proprietăților sunt identice. Un pătrat ideal de chunkuri vizibile în jurul unui singur jucător scade de la `(2×5+1)²=121` la `(2×4+1)²=81`, **nu** o promisiune de 33% CPU/RAM ori +33% jucători: chunkurile între jucători se suprapun, lumea poate fi deja încărcată și vehiculele/orașul pot suferi pop-in. Watchdogul nu înlocuiește rezolvarea unui tick lent și poate declanșa oprire în sarcini excepționale; test pe copie înainte de live.
- Nu atingem `entity-tracking-range` pentru jucători/vehicule, `entity-broadcast-range-percentage`, limitele survival RP, lumea, pluginurile, modurile, clientul sau portul hostului. `max-players=64` este plafon configurat, **nu** capacitate măsurată. Nu adăugăm `simulation-distance` din versiuni moderne în Forge 1.16.5.
- [Poarta statică](../../scripts/fc_funcity_capacity_profile_test.py) validează cheia unică, exact cele două modificări și lipsa de schimbări de bind/auth; nu pornește serverul și nu scrie pe PC/host.

## Modele împrumutate ca PRINCIPII, nu cod copiat

- [Documentația Paper](https://docs.papermc.io/paper/basic-troubleshooting/) explică limita firului principal și nevoia de profil în momentul lagului; [Paper profiling](https://docs.papermc.io/paper/profiling/) recomandă spark. Aceasta **nu** înseamnă că serverul nostru este Paper sau că orice setare Paper funcționează pe CatServer 1.16.5.
- [spark tick loop](https://spark.lucko.me/docs/guides/The-tick-loop) explică bugetul de 50 ms/tick și de ce o medie bună poate ascunde spike-uri. Păstrăm p95/p99 MSPT, CPU, RSS/heap/GC, traficul de chunkuri și erorile ca criterii. Nu copiem Folia region threading: modurile și pluginurile actuale nu au fost auditate pentru acea schimbare de model.
- Păstrăm FerriteCore + ModernFix + RoadRunner, deoarece [ablația locală 28/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39711748552) a favorizat primele două în scena ei. Nu instalăm optimizatoare necunoscute și nu ascundem entități/erori pentru un număr de jucători imaginar.

## Poarta de promovare

1. Build sursă reproductibil cu SHA și identitate FunCity confirmată în **clasele compilate**; fără Release/JAR redistribuit înainte de auditul drepturilor. Workflowul [source-build](../../.github/workflows/funcity-catserver-source-build.yml) poate dura; `setup` sau simpla aplicare a patchului nu înseamnă `BUILD_PASS`.
2. Boot și oprire curată la Java 11 cu 28/6 în GitHub; apoi copie izolată a **34 moduri + 13 pluginuri și a lumii reale** la plafonul 3 GiB, client Lite, login/anti-impersonare, voice, condus, NPC, persistență și restaurare. PC-ul activ și hostul live nu sunt laborator fără izolare și control.
3. A/B/B/A repetat pe aceeași lume și aceleași sarcini, inclusiv vedere/condus 4 vs 5; niveluri progresive de jucători cel puțin 10 minute/nivel, ≥3 probe/nivel. Ultimul nivel eligibil: TPS mediu ≥19,5, MSPT p95 ≤45 ms, RSS/heap/GC sub plafon și **zero regresii funcționale**. Dacă 4 chunkuri produc pop-in sau incompatibilități, rămâne 5. La 3 GiB poate fi necesar hardware mai mare; nu putem deduce +N jucători dintr-un nume de motor.

**Stare live:** `server.jar` de pe HidenCloud rămâne motorul original Mohist/Tenet; candidatul oficial CatServer este doar staged inactiv. Backupul hostului oprit este verificat, intrările extra nu sunt acoperite. SFTP nu permite restart și agentul nu are accesul oficial de power din panou. Nu declara FunCity instalat sau hostul Online.
