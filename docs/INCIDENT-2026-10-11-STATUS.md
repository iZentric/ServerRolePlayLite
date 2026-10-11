# Incident disponibilitate CUANTIC — 11 octombrie 2026 UTC

**Stare după recuperare:** Minecraft răspundea atât local, cât și public la 22:16 UTC; 0/25 jucători la acea citire, Java și tunelul pornite, 36 de moduri/14 pluginuri, JAR SHA-256 `96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c`. Aceasta este o observație datată, nu o garanție de uptime viitor sau de login modat.

| Ora UTC | Dovadă | Rezultat |
|---|---|---|
| 22:13 | [Run site / ping public 38179530716](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38179530716) | Conexiune refuzată. Site-ul a afișat „neconfirmat”, fără restart automat. |
| 22:14 | [Preflight doar-citire, run 38179585319](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38179585319) | Java, supervisor și frpc absente; port 25565 închis; JAR-ul și cele 36/14 fișiere încă pe disc. Consola nu a răspuns, deci **nu** am dedus 0 jucători din lipsa răspunsului. |
| 22:14–22:16 | [CHK, run 38179631479](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38179631479) | Recuperare cu `ensure-up.sh`, fără schimbarea JAR-ului sau pack-ului; portul a intrat în LISTEN. Un serviciu extern de status a răspuns fals în timpul boot-ului; nu l-am luat drept verdict final. |
| 22:16 | [Preflight local 38179743452](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38179743452) + [site public 38179743447](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38179743447) | Handshake Minecraft local și public 0/25, protocol 754; Spark TPS 20,0 la acel moment, p95 10 s 0,3 ms; SHA JAR neschimbat. |

**Cauza opririi nu este determinată.** Logul supervisorului și logul Java s-au întrerupt fără o oprire ordonată observată; raportul CHK nu a găsit un eveniment OOM în ce a putut citi. Nu atribuim incidentul unui mod sau unui jucător fără dovadă.

**Măsuri următoare, nu declarate deja în producție:** monitor extern cu alertă și procedură de recuperare care nu depinde de Java, restaurare de backup testată într-o copie, investigarea ciclului de viață al runnerului/supervisorului și rotația coordonată a credențialelor tunelului. Eliminarea unei credențiale din fișierele sursă nu o șterge din istoricul Git și nu înlocuiește rotația pe ambele capete. Nu programăm un restart experimental cât timp sunt jucători online.
