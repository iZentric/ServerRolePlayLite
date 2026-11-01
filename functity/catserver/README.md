# Motor FunCity — sursă verificabilă, Forge + Bukkit 1.16.5

[Obiective măsurabile și starea actuală](GOALS.md).

**Identitate:** fork experimental al [CatServer LGPL-3.0, tag 23.05.26-1](https://github.com/Luohuayu/CatServer/tree/1d8d63138be77a606df2a5e940b960065948f983), pin `1d8d63138be77a606df2a5e940b960065948f983`. Păstrează Forge 36.2.39, namespace-ul CraftBukkit/Spigot, protocolul, `catserver.yml` și atribuirea upstream; numele de operator/logger devine FunCity. Nu este o versiune nouă de Minecraft ori un substitut fără risc pentru Mohistul actual.

## Cod schimbat, nu doar numele

1. [0001 operator identity](patches/0001-funcity-operator-identity.patch): numai două șiruri de identitate, fără identități Forge/Bukkit modificate.
2. [0002 Forge block-place veto](patches/0002-preserve-forge-block-place-cancellation.patch): `onBlockPlaceEvent` păstrează anularea Forge după callbackurile Bukkit pentru place/multiplace; dacă Forge permite, decizia Bukkit rămâne identică.
3. [0003 Forge block-break veto](patches/0003-preserve-forge-block-break-cancellation.patch): `onBreakBlockEvent` reține anularea Forge înainte de callbackul Bukkit. Un plugin care dezanulează propriul `BlockBreakEvent` nu mai poate șterge veto-ul Forge; pentru evenimente permise de Forge, decizia Bukkit rămâne identică. XP/drop rămân pe traseul vechi.

Ambele patchuri sunt remedieri punctuale de **corectitudine**, nu optimizări MSPT demonstrate; nu schimbă tickuri, permisiuni sau politica lumii în afara acestor decizii.

[Poarta sursă de plasare](../../scripts/fc_funcity_bridge_patch_test.py) verifică cele 8 combinații, iar [poarta de spargere](../../scripts/fc_funcity_break_veto_test.py) refuză metoda upstream care putea pierde veto-ul. [Contractul Java 11 fără Gradle](../../.github/workflows/funcity-bridge-java-contract.yml) compilează metodele reale patch-uite cu tipuri simulate și respinge deliberat câte un mutant fără veto pentru place și break; [rularea 41316259012](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41316259012) a trecut **20/20 cazuri place/multiplace/break**, cu ambii mutanți respinși. Acesta este un test de logică, **nu** boot sau compatibilitate cu modurile real instalate. Workflowul [de build](../../.github/workflows/funcity-catserver-source-build.yml) rulează la JDK 8/11/17, folosește Gradle serial pentru setup/build, verifică clasele FunCity atât compilate cât și în `data/*-universal.jar` din launcher, apoi încearcă boot/stop Java 11 pe loopback, cu lume generată și **zero** moduri/pluginuri/jucători. Verificarea este fail-closed; nu publică JAR, lume ori loguri brute. Dacă unul dintre pași eșuează, nu există binar aprobat.

## Alegerea bazei: trei motoare 1.16.5

| Bază | Dovezi existente și limită | Decizie |
|---|---|---|
| [CatServer LGPL-3.0, pin 1d8d6313](https://github.com/Luohuayu/CatServer/tree/1d8d63138be77a606df2a5e940b960065948f983) | [2/2 builduri/booturi pe lume goală cu 0001–0003](GOALS.md); semnal A/B sintetic 18 moduri/6 pluginuri, zero jucători. | **Baza propriului candidat**: patch mic, licență compatibilă și builder deja fixat. |
| [Tenet 1.16.5 GPL-3.0](https://github.com/TiangongCraft/Tenet/tree/1.16.5) / motorul live Mohist-family | Live-ul a atins `Done` cu 34 moduri/13 pluginuri, dar are ERROR nerezolvat; **nu** dovedește că ramura Tenet rulează același pack. Hookul Tenet observat nu este un benchmark. | Reper de compatibilitate, fără copiere de cod GPL sau schimbări de threading netestate. |
| [Arclight 1.16 GPL-3.0, pin 5c6b7953](https://github.com/IzzelAliz/Arclight/tree/5c6b79537ffded1435ae05a864796e5651124f62) | Nu a ajuns la `Done` în proba izolată anterioară cu 28 moduri/6 pluginuri. [Dispatcherul break](https://github.com/IzzelAliz/Arclight/blob/5c6b79537ffded1435ae05a864796e5651124f62/arclight-common/src/main/java/io/izzel/arclight/common/mod/server/event/BlockBreakEventDispatcher.java) suprascrie și el anularea Forge cu starea Bukkit; nu este o sursă de fix copiat. | Nu-l alegem pentru acest pack fără probă nouă; fără copiere GPL. |

Această alegere este despre compatibilitate demonstrabilă și risc, **nu** dovada că motorul este cel mai rapid sau ține un anumit număr de jucători. [Comparația nouă F/X/O pe 18 moduri, 6 pluginuri și 0 jucători](COMPARATIE-EXPERIMENTALA-2026-11-01.md) a inclus și buildul FunCity custom cu 0003; îl păstrăm candidat, fără a-i atribui o capacitate RP. Patchul 0003 este o corecție proprie a defectului observat în CatServer, nu cod transplantat din alt motor.

## Ce am preluat și ce am refuzat de la alte motoare

- Din [Paper/server.properties](https://docs.papermc.io/paper/reference/server-properties/) preluăm **principiul** bugetului de chunkuri, nu cod Paper incompatibil cu Forge: brațul [view4-only](../capacity/3g-view4-only/server.properties) schimbă numai distanța, fără watchdog în A/B.
- Din [Forge 1.16.x](https://github.com/MinecraftForge/MinecraftForge/blob/1.16.x/src/main/java/net/minecraftforge/common/ForgeConfig.java) păstrăm implicit `removeErroringEntities=false` și `removeErroringTileEntities=false` în candidatul de siguranță: nu transformăm excepțiile modurilor în ștergere tăcută a conținutului.
- Am verificat [hookul Tenet 1.16.5](https://github.com/TiangongCraft/Tenet/blob/1.16.5/src/main/java/com/mohistmc/forge/ForgeEventHandler.java): filtrează apelurile Bukkit la threadul principal. **Nu îl copiem** în CatServer fără test, fiindcă ar omite evenimente Forge async observabile azi de pluginuri; nu este un câștig de capacitate demonstrat. Vechile patchuri hopper/ticketuri au eșuat ori au fost neconcludente în A/B.

## Config de laborator, nu live

[Profilul 3 GiB / vedere 4 și protecții hibride](../capacity/README.md) este un braț reversibil pe copie. Configurile `defaultconfigs/` nu suprascriu automat `world/serverconfig/` al unei lumi existente. Niciun installer nu trebuie să trimită peste hostul activ lumea, portul, modurile, pluginurile sau autentificarea pe baza acestor fișiere.

## Candidat local PRIVAT, pregătit pentru proba pe copie (Linux izolat)

Workflowul [`funcity-catserver-source-build.yml`](../../.github/workflows/funcity-catserver-source-build.yml) și calculatorul de laborator folosesc **același script** [`fc_funcity_build_private.sh`](../../scripts/fc_funcity_build_private.sh). Pe GitHub, JAR-ul dispare cu runnerul și **nu** se încarcă într-un artifact/Release public (poate încorpora componente terțe). Pe calculatorul privat, scriptul clonează commitul CatServer pin-uit, aplică doar cele trei patchuri, compilează, verifică JAR-ul universal înglobat și pornește/oprește Java 11 pe lume goală înainte de a salva local `FunCityEngine-private-trial.jar` **și `runtime-seed/` cu bibliotecile/instalarea generate de launcher**. Aceste fișiere pot include componente terțe: rămân private, nu se includ în GitHub. Necesită Linux cu JDK 17 activ pentru build, Java 11 separat, resurse suficiente pentru Gradle (setup de până la 5 GiB + compilator fork de 4 GiB), spațiu pe disc și acces legitim la dependențele upstream. Nu rula buildul pe PC-ul serverului activ.

```bash
# PE UN LABORATOR PRIVAT, separat de PC/host. Ambele căi de ieșire trebuie să fie NOI și în afara repo-ului.
bash scripts/fc_funcity_build_private.sh /cale/privata/fc-build /cale/java11/bin/java
sha256sum /cale/privata/fc-build/FunCityEngine-private-trial.jar
```

Pentru proba reală: pregătește separat o **copie inactivă verificată** a întregii rădăcini RP (inclusiv lumea și fișierele extra), nu o cale spre instanța în rulare; backupul original rămâne separat. Confirmă că sunt 34 JAR-uri în `mods/`, 13 în `plugins/`, lumea referită în `server.properties` are `level.dat`, EULA fusese deja acceptată și `online-mode=false` este potrivit pentru autentificarea offline existentă. **Numai după verificarea fizică a izolării copiei**, pune în acea copie markerul literal `FUNCITY_INACTIVE_ISOLATED_COPY_V1` pe o singură linie în `.funcity-isolated-copy`. Scriptul [de probă](../../scripts/fc_funcity_private_trial.py) cere și izolare de rețea la nivel de kernel (`unshare` + `iproute2`); astfel pluginurile copiate nu pot trimite date către baze de date/webhook-uri externe. Pentru că rețeaua este închisă, scriptul cere **`runtime-seed/` creat la prima pornire din build**; verifică SHA-urile și SHA-ul motorului, păstrează bibliotecile vechi ale copiei și pune numai în copia nouă bibliotecile necesare CatServer. Nu deschide egressul pentru a masca lipsa lor. Dacă izolarea nu poate fi creată, refuză proba, nu scoate firewallul. Copiază și verifică SHA-256 al tuturor fișierelor într-un director **nou**, înlocuiește `server.jar` **doar acolo** și păstrează `server-before-funcity-trial.jar` în copie; restrânge bind la loopback, whitelist, query/RCON off, apoi încearcă două booturi/opriri pe Java 11. Logurile brute rămân în laborator, **nu** se trimit în GitHub/chat. Exemplu după ce cunoști SHA-ul local de mai sus:

```bash
python3 scripts/fc_funcity_private_trial.py \
  --java /cale/java11/bin/java \
  --source-copy /cale/privata/copie-inactiva-verificata \
  --output /cale/privata/fc-test-NOU \
  --engine /cale/privata/fc-build/FunCityEngine-private-trial.jar \
  --runtime-seed /cale/privata/fc-build/runtime-seed \
  --sha256 SHA256_HEX_AL_BINARULUI_LOCAL
```

Pentru **ținta 2 vCPU / 12 GB** de laborator poți adăuga `--heap-gib 8` numai la această probă pe copie; scriptul refuză înainte de copiere dacă nu găsește cel puțin 10 GiB disponibili (inclusiv limita cgroup). Implicit rămâne `-Xmx2G`; această opțiune nu măsoară clienți și nu schimbă motorul sau hostul live. [Criteriul de capacitate pentru 12 GB](../capacity/README.md) este separat.

**Limită:** acest laborator încă nu există cu lumea completă în mediul disponibil aici; cele două booturi pe pachet complet nu au fost executate. Proba nu oferă acces client din rețea (intenționat), deci autentificarea efectivă, voice UDP, vehiculele, restarturile cu jucători și capacitatea rămân etape separate. Unele pluginuri pot necesita servicii externe; eșecul sub izolare se investighează fără a conecta copia direct la producție. Nu instala candidatul pe host înainte de H2–H6, backup complet și controlul real Start/Restart/rollback.

## Ce lipsește înainte de a spune «motorul meu e gata»

- Buildul și bootul gol Java 11 cu `stop` explicit și exportul bibliotecilor de bootstrap au trecut de două ori **cu patchurile 0001–0003** în [41316259001](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41316259001) și [41317093607](https://github.com/iZentric/ServerRolePlayLite/actions/runs/41317093607); fiabilitatea pe packul RP nu este garantată. Nu confunda un `Done` pe lume goală cu proba pe **copie izolată** cu toate cele 34 moduri, 13 pluginuri și lumea RP reală.
- Client Forge Lite real: login/autentificare offline și anti-impersonare, reconectare, sincronizare de registru/recipes, voce UDP, vehicule/NPC, economie/permisiuni/CoreProtect și păstrarea inventarelor și construcțiilor după restart/restore. Verificăm pe copie mod Forge care anulează plasarea + plugin Bukkit de construcție; testăm separat WorldGuard cu entități modate și chunk loaders la restart dacă sunt folosite.
- Rampă A/B/B/A cu jucători distribuiți în oraș, p95/p99 MSPT, CPU fir principal, GC/RSS/uplink și zero pierderi RP pe host comparabil; [poarta de capacitate](../../scripts/fc_funcity_capacity_verdict.py) respinge dovezile incomplete. Vechile patchuri de hopper/ticketuri au dat regresii sau rezultate neconcludente și nu sunt incluse.
- Backup SHA + rollback privat și control oficial de Start/Restart înainte de orice înlocuire a `server.jar`. SFTP singur nu este controlul serverului. [Preflightul read-only](../../.github/workflows/pc-hidencloud-restart-readiness.yml) citește numai `server.properties` și `spigot.yml` prin SFTP cu cheia PC rotită și verifică dacă `start.sh` apare în lista rădăcinii; testează separat pe fixture chei duplicate, RCON și căi de script nesigure. Nu descarcă sau execută scriptul hostului, nu trimite `/restart` și nu dovedește că panoul poate relansa procesul. Chiar dacă toate condițiile statice trec, H6 rămâne deschisă până la backup complet și test real de restart/rollback.

**Limită explicită:** nimeni nu poate garanta zero buguri pentru orice combinație de moduri/pluginuri ori că acesta este cel mai rapid hybrid din 2026 fără aceleași teste pe aceeași sarcină. Motorul live rămâne neschimbat până la verificarea de mai sus; nu redistribuim un launcher cu componente terțe ca Release/ZIP neverificat.
