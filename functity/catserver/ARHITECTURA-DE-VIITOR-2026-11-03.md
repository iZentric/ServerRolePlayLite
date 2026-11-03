# FunCity hibrid — direcția de performanță (3 noiembrie 2026)

**Țintă:** mai mulți clienți Forge reali pe **2 vCPU / 12 GB** decât CatServer oficial, păstrând lumea RP 1.16.5, cele 34 moduri, 13 pluginuri, autentificarea, vocea, vehiculele și mecanicile survival. „Mai rapid decât Paper” poate fi un obiectiv separat numai pe o sarcină comparabilă: Paper nu execută acest pachet Forge. Nicio cifră de jucători ori promisiune de zero buguri nu rezultă dintr-un nume de motor.

## Trei arhitecturi, o alegere

| Arhitectură | Potențial | Cost pentru acest server | Decizie |
|---|---|---|---|
| Rescriere completă în Rust, de ex. [Pumpkin](https://github.com/Pumpkin-MC/Pumpkin) | Motor modern, libertate mare | Alt API de plugin; nu a demonstrat încărcarea JAR-urilor Forge+Bukkit 1.16.5 și a lumii RP | Cercetare separată, nu migrare a packului actual; fără copiere GPL. |
| Ticking pe regiuni, model [Folia](https://github.com/PaperMC/Folia) | Paralelism când mulți jucători sunt dispersați | Proiectul recomandă ideal ≥16 nuclee, iar pluginurile au nevoie de adaptare la lipsa unui fir principal unic; ținta noastră are 2 vCPU | Nu transplantăm region threading orb în Forge+Bukkit. |
| **Fork FunCity al sursei oficiale [CatServer 1.16.5](https://github.com/Luohuayu/CatServer/tree/1d8d63138be77a606df2a5e940b960065948f983)** | Păstrează ABI-ul Forge/Bukkit și permite optimizări specifice scenei RP | Firul principal poate rămâne plafonul; trebuie profil și A/B cu clienți reali | **Calea aleasă pentru packul actual**; brandul și veto-urile Forge/Bukkit sunt deja patchurile `0001`–`0003`. |

## Regula de construcție

1. **Contractul hibrid rămâne pe firul proprietar al lumii:** plasare/spargere, evenimente Forge/Bukkit, entități, inventar, auth, economie și vehicule nu sunt mutate în threaduri fără auditul fiecărui mod/plugin. Patchurile de veto rămân, cu testul lor de regresie.
2. **Întâi profil, apoi o singură intervenție:** comparăm CatServer oficial și FunCity pe copia completă, cu aceiași clienți și aceeași sarcină; profilul JFR privat indică dacă domină tickul pluginurilor, lumina, chunk IO sau compresia/trimiterea. [Analizorul](../../scripts/fc_funcity_jfr_hotspots.py) este pregătit; nu diagnostichează 34/13 până la o captură privată reală.
3. **Rust este candidat doar pentru un hot path fără stare de joc**, precum transformarea unor bytes de pachet, *dacă* măsurătorile indică acel cost și protocolul Forge poate fi păstrat prin streamuri zlib valide cu aceleași date decomprimate (nu neapărat bytes comprimați identici). Limita JNI/copia datelor, erorile native, GC, memoria și fallbackul Java trebuie testate; un manager Rust separat nu accelerează tickul JVM. [Prototipul Rust + libdeflate și shimul JNI](../../experiments/packet-compression/README.md) au trecut testele zlib cu 6 payload-uri publice, iar JNI a redus timpul brut de compresie, dar **nu este integrat în server.jar**: lipsește profilul Netty sub clienți reali.
4. Alte intervenții se testează **separat**: view-distance 5→4 (vizibilitate/condus), Starlight (lumină și RSS), Chunk Sending (login/chunkuri). FerriteCore, ModernFix și RoadRunner rămân în baseline-ul public sintetic; prezența și efectul lor în packul privat se verifică înainte de o decizie. Nu combinăm schimbări într-un singur braț ca să atribuim fals un câștig.
5. **Verdictul este [H5](GOALS.md), nu o promisiune:** pe 2 vCPU/12 GB, 34/13 și clienți reali, A/B/B/A 5→10→15→20, p95/p99 MSPT, CPU, RSS, uplink și GC. FunCity câștigă capacitate doar dacă trece de două ori o treaptă la care CatServer oficial eșuează de două ori, fără regresii RP/voice/auth/vehicule și cu rollback verificat. Dacă nu, păstrăm baseline-ul și raportăm rezultatul real.

**Stare:** buildul și bootul gol Java 11 trec; scena publică 18/6/0 clienți nu dovedește X mai rapid decât CatServer oficial; în [ultima repetare](COMPARATIE-EXPERIMENTALA-2026-11-01.md), oficialul a folosit mai puțin CPU. Jobul pe TEST este încă în așteptare; lumea privată, JAR-ul live, clientul și PC-ul activ nu au fost mutate. O viitoare migrare a versiunii Minecraft este o cale distinctă: niciun mod sau plugin 1.16.5 nu este presupus compatibil automat cu un loader nou.
