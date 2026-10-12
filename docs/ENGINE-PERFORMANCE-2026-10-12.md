# CUANTIC — lista de verificări și performanță (12 octombrie 2026)

**Stare la 09:23 UTC (instantaneu, nu monitorizare continuă):** o probă publică nouă de la 09:22:35 UTC a returnat `Connection refused`; starea de ACUM nu poate fi declarată „pornit”. [Preflight numai citire](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38228758329) și [CHK — recuperare condițională](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38229164231) sunt în coadă până revine runnerul self-hosted. CHK verifică procesul înainte de pornire; **un job queued nu pornește serverul**. Nu repornim peste jucători. Mai poate exista un proces Java fără conexiune publică (ex. tunel/port): nu confundăm cele două situații.

## Ce s-a testat și ce a ieșit

| # | Probă | Rezultat | Ce demonstrează / ce NU demonstrează |
| --- | --- | --- | --- |
| 1 | Test public al adresei Minecraft | **Eșec la 09:22:35 UTC**: conexiune refuzată ([status](../analysis/ALIVE.md)) | Nu dovedește că procesul Java este oprit; preflightul de pe gazdă încă nu a rulat. |
| 2 | Recuperare sigură a gazdei | **În așteptare**: [preflight](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38228758329) și [CHK](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38229164231) | Nu putem confirma startul sau modificarea tunelului înaintea logurilor de la runner. |
| 3 | CUANTIC live vs CatServer oficial, Java 17, același pack A/B/B/A | CPU stabil 3,32/2,86 s vs 3,32/3,43 s; p95 1,3/1,1 ms vs 1,2/1,2 ms; RSS 2205/2452 MiB vs 2186/2476 MiB, pe perechi ([date](ENGINE-NATIVE-RESULT.md)) | Variația între repetări e mai mare decât câștigul pretins. Fără jucători/vehicule; niciun câștig overall demonstrat. |
| 4 | Patch nativ `SortedArraySet.removeIf` în JAR, același pack 36/14 | **Respins** după repetare: startup/CPU/p95/RSS nu au trecut simultan pragul strict ([date](ENGINE-STRICT-RESULT.md)) | Nu publicăm patch-ul și nu schimbăm live pentru un benchmark care nu câștigă clar. |
| 5 | Fake players (Curtain) pe runner izolat | **Eșec de conectare/spawn**: status și `/list` au rămas 0/25 după trei încercări ([date](ENGINE-FAKEPLAYERS-RESULT.md)) | Nu sunt trei jucători conectați, nu există probă CPU/TPS cu „boți” și nu reprezintă clientul modat real. |
| 6 | Inventar release-ului public | **Trecut** pe runner găzduit GitHub: SHA a corespuns, exact 36 moduri / 14 pluginuri ([raport](ENGINE-PACK-AUDIT.md), [run](https://github.com/iZentric/ServerRolePlayLite/actions/runs/38229356587)). FerriteCore, ModernFix, RoadRunner, Spark și alte moduri de optimizare sunt deja în arhivă; `view-distance=4`, `use-native-transport=true`. | Inventar, nu test de impact. Nu adăugăm aceleași moduri încă o dată; nu reducem view-distance sub 4 doar pentru un scor gol. Gazda live poate avea alte configurații. |
| 7 | Teste automate ale auditorului și site-ului local | **9 trecute** (2 pentru SHA/inventar/redactare; 7 pentru afirmații de pe site) | Validare de cod, nu test de login/vehicule ori TPS real. |

**Notă de siguranță:** arhiva publică are `online-mode=false`; aceasta este o decizie de autentificare/proxy, nu o optimizare de performanță. Nu modificăm modul de autentificare pe producție fără auditul fluxului de login/proxy și verificarea jucătorilor.

**Decizie:** JAR-ul live/recomandat rămâne cel deja validat, SHA-256 `96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c`; nu am pus un JAR nou pe server și nu voi prezenta un câștig egal ca upgrade. Clientul **rămâne modat Forge 1.16.5**; nu înlocuim pack-ul cu vanilla/Paper.

## Ce urmează, în ordinea cu risc minim

1. **Runnerul self-hosted trebuie să revină online.** Preflight: Java, supervisor, port 25565, tunel `frpc`, RAM, loguri și `/list`. Dacă Java e oprit, CHK îl pornește condițional; dacă e deja pornit, nu îl restartează. Repetăm statusul public și apoi loginul modat. Dacă runnerul nu revine, este nevoie de intervenție pe mașina gazdă; un server de probă pe GitHub nu ar fi serverul jucătorilor.
2. **Profilare, nu reglaj la ghici:** pe gazda online, eșantion Spark/TPS/p95/CPU/RSS la repaus și cu jucători consimțitori, vehicule și activitatea RP obișnuită; fără stress test pe producție. Verificăm întâi portul, tunelul și logurile înainte de a atribui lagul JAR-ului.
3. **Candidat izolat și prag strict:** testăm *o singură schimbare per serie*, cu același pack/client, aceeași lume/seed și Java, A/B/B/A plus login modat și vehicule. Startup, CPU, p95 și RAM trebuie să fie strict mai bune, repetabile, fără regresii; altfel respingem și nu distribuim JAR-ul. Nu adăugăm automat moduri „performance” deja prezente, nu forțăm schimbarea OptiFine cu Rubidium/Oculus.
4. **Test cu boți reali, doar după handshake Forge valid:** testul anterior nu a produs jucători. Un bot server-side nu simulează FPS-ul unui laptop; pentru acesta e necesar un client modat autentic pe PC slab. Fără a atribui cifre unor conexiuni eșuate.

Această listă este un jurnal al probelor, nu o promisiune că serverul este sus sau că un anumit motor e cel mai rapid din lume.
