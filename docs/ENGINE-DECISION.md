# CUANTIC engine — rezultat comparativ, 11 octombrie 2026

## Decizie

**Pastram motorul curent in productie.** Candidatul CatServer upstream este disponibil doar ca artifact CI, nu release/deploy. A pornit cu cele 36 moduri si 14 pluginuri in teste izolate, dar nu s-a demonstrat un castig de performanta; pe runnerul GitHub p95 este usor mai rau in singura proba. Nu se poate afirma ca acest JAR este „mai bun decat orice JAR hibrid sau ne-hibrid”. Mai ales un Paper/vanilla fara moduri nu ofera acelasi gameplay, deci un rezultat numeric direct ar induce in eroare.

## Probe executate

| Loc / sursa | Motor actual (CatServer 1.7.7 / 2023) | Candidat upstream 2024 | Interpretare |
|---|---:|---:|---|
| [GitHub, acelasi runner](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38121496593) | boot `Done` 7.054 s; 14 pluginuri; 36 moduri; RSS median 2411.4 MiB; spark p95 2.7 ms | boot 6.728 s; 14 pluginuri; 36 moduri; RSS median 2337.5 MiB; spark p95 2.8 ms | O singura proba per varianta, lumi proaspete cu acelasi seed, comenzi pentru 256 hoppers + 40 zombie, fara jucatori. Zombie apar in log; raportul nu valideaza independent numarul de hoppers plasati. Diferenta RSS ~74 MiB, dar **p95 nu s-a imbunatatit**. Valorile `Done` nu reprezinta intreaga durata de bootstrap. |
| [Gazda reala, probe PRIVATE :25566](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38122349973) | snapshot al lumii reale; prima incercare a fost oprita de coliziunea portului UDP voice 24454, remediata in copia de test; a doua incercare nu a ajuns la `Done` in 240 s si a fost terminata | **netestat pe gazda** (nu am pornit B dupa esecul lui A) | Niciun verdict A/B pentru host; nu mai stresam masina live prin incercari automate. Nicio modificare la lumea sau JAR-ul productiei. |
| [Preflight live dupa probe](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38122699066) | acelasi hash SHA-256 `96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c`; Java, supervisor si tunel active; status Minecraft local: protocol 754, 0/25 jucatori; 36 moduri, 14 pluginuri; spark 20 TPS si 0.1 ms p95 la idle | — | Confirma raspunsul status **local**, nu login modat / accesul extern sau performanta cu jucatori. |

Logurile, metodologia si numerele complete: [`ENGINE-AB-GITHUB.md`](ENGINE-AB-GITHUB.md), [`ENGINE-AB-HOST.md`](ENGINE-AB-HOST.md), [`ENGINE-PREFLIGHT.md`](ENGINE-PREFLIGHT.md). Benchmarkul masoara mai ales timpul la idle; nu reprezinta traficul din oras, vehiculele, numarul de entitati din productie sau dispozitivele client slabe. Maximele izolate si diferentele de sub 1 ms nu sunt dovezi de superioritate statistica.

## Conditii pentru urmatoarea promotie

1. Comparatie repetata, cu sarcina reprezentativa si jucatori reali pe clientul modat Forge 1.16.5, inclusiv vehicule si o zona RP incarcata; proba separata pe un laptop slab cu **OptiFine + modurile normale**, nu amestecata cu Rubidium/Oculus. Pastram acelasi pack si aceeasi lume/clona, aceleasi limite RAM si un test client autentificat.
2. Pe gazda live nu pornim din nou doua JVM-uri fara buget RAM/CPU suficient; preferam un runner separat identic sau o fereastra de mentenanta cu backup verificat. Primul test pe gazda a descoperit si ca Forge Simple Voice Chat foloseste `world/serverconfig/voicechat-server.toml`, port UDP 24454; o copie trebuie sa aiba un port separat.
3. Orice schimbare a JAR-ului public necesita *raspuns explicit cu zero jucatori in consola*, snapshot verificat al lumii, JAR-ului, modurilor si configuratiilor, un rollback automat la original la orice esec si verificare dupa rollback (status Minecraft si autentificare client modat). Nu utilizam `apply-live.sh` pentru experiment: inlocuieste pack-ul si opreste Java.

Nu am facut deploy al candidatului. Smoke-testul candidatului confirma doar incarcarea modurilor si pluginurilor, **nu** compatibilitatea la conectare sau un avantaj de performanta. Artifactul candidat expira la 17 octombrie 2026.
