# FunCity 1.16.5 — fiecare mod de server, ales strategic pentru mulți jucători (22.10.2026)

**Verdict:** păstrăm conținutul RP și dependențele cât timp sunt folosite; nu maximizăm jucătorii eliminând obiecte din lume. **CatServer oficial + RoadRunner, ModernFix, FerriteCore** este baza *de test* cea mai bine susținută până acum. Restul optimizărilor se câștigă prin profilarea unei sarcini relevante, nu prin numărul de JAR-uri. [Boot 28/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39694738682) și [A/B 18/6/80 zombie](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39692158792) nu reprezintă 100 de jucători. [Inventarul PC numai citire](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39696088517) a confirmat **34 moduri/13 pluginuri, toate cele 28 propuse prezente + șase suplimentare**. Cele șase sunt printre opt nume publice din inventarul istoric, dar captura agregată **nu spune care șase**; nu pretindem că știm sau că sunt inutile. Analiza de mai jos acoperă toate cele 36 nume istorice și nu modifică nimic pe PC.

**Legendă:** `28` = numele este în ținta de 28 și s-a găsit la inventarul read-only, nu i-am verificat hashul/conținutul sau funcționarea cu 13 pluginuri. `8?` = unul dintre cele opt nume în afara țintei; **șase** dintre opt există pe PC, identitatea lor nu a fost publicată. `B` = trebuie păstrat până la inventar de lume și gameplay; `D` = dependență; `P` = optimizer/compatibilitate de profilat; `O` = opțional în ținta viitoare, nu șterge din live. „Câștig” înseamnă un hotspot și un A/B repetat, nu doar boot.

## Conținut RP: nu sacrifica lumea pentru o cifră de TPS

| Mod (nume de JAR prescurtat) | Stare | Decizie și proba necesară |
|---|---|---|
| `additional-guns` | 28 · B | Arme RP: ține dacă sunt folosite; testează foc/proiectile/inventare cu jucători; dacă e hotspot, analizează frecvența proiectilelor, nu scoate unilateral armele. |
| `cgm` | 28 · B | Al doilea conținut de arme, nu îl declara duplicat doar pentru că există Additional Guns; verifică rețete/proiectilele fiecăruia. |
| `cfm` | 28 · B | Mobilier: păstrează ID-uri/block entities din lume; profilează orașul dens și redarea clientului separat de tick. |
| `Modernxl` | 28 · B | Mobilier RP; riscă blocuri lipsă la eliminare; confirmă folosirea în lumea reală înainte de decizie. |
| `modernlife` | 28 · B | Conținut RP; aceeași poartă de registru/obiecte și hotspot, nu îl marca optimizer. |
| `Pizzaland` | 28 · B condiționat | Dacă există obiecte sau rețete RP folosite, păstrează; dacă nu, analizează separat migrarea lumii și clientului. Dimensiunea arhivei client nu dovedește cost tick per jucător. |
| `pamhc2foodcore` | 28 · B condiționat | Hrană/rețete: fără inventar de obiecte și meniuri, nu scoate; măsoară dacă rețetele se profilează la mulți jucători. |
| `roadstuff` | 28 · B | Drumuri/blocuri existente; păstrează până la auditul lumii, verifică update-uri de bloc doar dacă apar în profiler. |
| `supplementaries` | 28 · B | Decor/funcții modate: păstrează dacă lumea le folosește; potențialele block entities se testează în oraș aglomerat. |
| `vehicle-mod` | 28 · B | Vehicule centrale RP: măsoară mișcare, coliziuni și pachete când mulți conduc simultan; niciun optimizer care le rupe AI/network nu trece. |
| `emotecraft` | 28 · B | Emote RP: ține dacă cerute; testează animații/handshake cu client Lite și traficul în grup mare. |
| `voicechat` | 28 · B | Voce RP cerută și pe client: păstrează versiunea compatibilă; măsoară **UDP, upload, conexiuni și latență** sub conversații simultane, separat de TPS. |

## Dependențe/compatibilitate: nu le scoate izolat

| Mod | Stare | Decizie și proba necesară |
|---|---|---|
| `mapperbase` | 28 · D | Dependență Road Stuff; nu scoate cât timp Road Stuff rămâne. |
| `obfuscate` | 28 · D | Dependență pentru arme/vehicule din pack; verifică metadata și registrul înainte de orice schimbare. |
| `player-animation-lib` | 28 · D | Dependență Emotecraft; nu scoate separat. |
| `selene` | 28 · D | Dependență Supplementaries; nu scoate separat. |
| `Placebo` | 28 · D condiționat | Dependență obligatorie declarată de FastSuite și FastWorkbench; dacă testezi scoaterea ambelor, reverifică toate dependențele înainte de a considera eliminarea lui. |
| `connectivity` | 28 · P, prioritate siguranță | Nu e multiplicator automat de jucători: urmărește login/rețea/timeout și păstrează dacă remediază o problemă măsurată. În **template-ul repo**, `disableLoginLimits=true` și `disablePacketLimits=true` trebuie revizuite pentru abuz, fără a presupune că sunt configurația live. Nu lăsa limitele de siguranță dezactivate doar pentru un login sintetic mai rapid. |
| `incontrol` | 28 · P, posibilă mecanică RP | Verifică **local, fără publicarea configurației**, dacă există reguli de spawn active; dacă da, păstrează mecanica. Dacă nu, braț A/B și verificare spawn înainte de eliminare. |

## Optimizări: fiecare are o măsură distinctă

| Mod | Stare | Prioritate, efect urmărit și condiția de a rămâne |
|---|---|---|
| `RoadRunner` | 28 · P, **baseline** | Tick/AI; [pe CatServer](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39694213284) a consumat mai puțin CPU decât Performant în ambele ferestre scurte, dar nu a câștigat timpul mediu de tick. Nu îl combina cu Performant; testează AI, NPC și vehiculele în lumea RP. |
| `modernfix` | 28 · P, **baseline** | Fixuri/încărcare/memorie: păstrează prudent, măsoară heap după GC, boot, stabilitate și eventualele mixinuri suprapuse. Nu i se atribuie un număr de jucători din simpla prezență. |
| `ferritecore` | 28 · P, **baseline** | Memorie/structuri: compară heap după GC și RSS sub aceleași zone/jucători; câștig de memorie ≠ automat TPS. |
| `AI-Improvements` | 28 · P | AI la multe entități; întâi profilează AI, apoi A/B cu RoadRunner identic pe ambele brațe și verifică spawn/NPC. Dacă AI nu domină, nu poate explica capacitatea. |
| `getittogetherdrops` | 28 · P | Mai puține entități drop în ferme/loot; testează scenarii de drop și corectitudinea pickupului/economiei/CoreProtect, nu doar MSPT. |
| `FastSuite` | 28 · P | Cache/rețete: profitabil doar unde matching-ul rețetelor costă; profil crafting cu mulți jucători și testează rezultatul rețetelor modate. |
| `FastWorkbench` | 28 · P | Workbench: braț separat de FastSuite, același test de crafting + poartă de corectitudine; Placebo rămâne cât depinde de el. |
| `Ksyxis` | 28 · P | Spawn chunks/start: **pregenerarea lumii nu înlocuiește** problema chunk-urilor de spawn ținute active; template-ul repo are `keep-spawn-loaded: true`. Compară Ksyxis și comportamentul spawn **fără a schimba simultan două setări**, apoi costul de tick stabil și startupul. |
| `lazydfu` | 28 · P, prioritate mică la capacitate | Optimizează în principal pornirea/inițializarea; păstrează dacă nu dă regresii, dar nu îl contabiliza ca multiplicator TPS în orașul plin. |

## Opt nume istorice în afara țintei de 28; șase reale încă neidentificate în raportul agregat

| Mod | Stare | Verdict strategic înainte de orice ștergere |
|---|---|---|
| `Clumps` | 8? · O | **Exclus explicit** din clientul Lite și ținta de server după probă privată cu backup/login; nu îl reinstala. Inventarul agregat nu publică prezența individuală a JAR-urilor extra. |
| `FastFurnace` | 8? · O | Cuptoare/rețete: numai dacă profilerul indică hotspot de multe cuptoare; FastSuite nu îl înlocuiește complet. Braț separat, corectitudine rețete/fuel. |
| `SpawnerFix` | 8? · O | Fix de randare client în auditul istoric, nu câștig server MSPT demonstrat; **candidat** de scoatere numai din copie după handshake și test spawner. |
| `bwncr` | 8? · O | Sunet opțional; verifică audio RP înainte de eliminare, nu îl numi optimizare de TPS. |
| `letmedespawn` | 8? · O | Schimbă despawn; nu pentru capacitate fără profil + testul NPC/mobi persistenți/questuri. |
| `memoryleakfix` | 8? · O | Doar dacă există creștere de heap după GC demonstrată și fix neacoperit de ModernFix; test lung și verificare mixinuri. |
| `smoothchunk` | 8? · O | **Pregen elimină generarea**, nu elimină salvarea chunk-urilor. Numai dacă p99 crește la save, măsoară latență disc/fișiere pe copie și posibil regresii. |
| `spark` | 8? · O | Profiler temporar când măsurăm, nu „mod de capacitate”; folosește profilul local privat, publică doar metrici agregate. |

**Fără certitudine despre cele șase:** chiar dacă un JAR opțional există acum, nu îl ștergem fără audit de dependențe, lume/config și rollback. Un JAR „SCOS” în tabelul istoric descrie *ținta de test*, nu confirmă absența lui pe PC.

## Ce aduce cel mai mare câștig potențial la capacitate, în această ordine

1. **Siguranță/compatibilitate înaintea performanței:** inventar exact privat al celor șase JAR-uri și 13 pluginuri; verificare autenticitate/anti-impersonare, limite de login/pachete și `removeErroringEntities/TileEntities=true` din **template-ul repo** (risc să dispară obiecte în loc să avem o eroare diagnosticabilă). Nimic din repo nu certifică setările live; nu le schimbăm cu jucători online.
2. **Pregen în copie cu backup/rollback:** numai dimensiunile/zonele accesate de jucători, plus margine pentru extindere, spațiu disc și coordonate controlate. Repetă testul cu lume stabilă **și** cu primul load de zonă; pregenerarea taie spike-uri de generare, **nu** tickul celor deja încărcate, mișcarea, voice-ul, pluginurile ori salvările.
3. **Zone/entități/pluginuri:** `view-distance=5` este deja verificat activ într-un test anterior; la 5, un jucător izolat poate încărca teoretic până la `11×11=121` coloane de chunk, cu suprapunere mare în oraș și mult mai puțină în zone răsfirate. Pentru 60 complet răspândiți, `60×121=7260` este o **limită geometrică grosieră**, nu număr de chunk-uri active/tick ori necesar măsurat de RAM. Profilează threadul principal, NPC/vehicule, event handlers Bukkit, block entities/hoppers, CoreProtect/database, rețeaua și voice. Configul repo are `entity-broadcast-range-percentage=80`, activare entități și spawn 20/6/2: **nu** micșora vederea vehiculelor/jucătorilor sau spawnul RP fără comparație vizuală și test de gameplay. În Minecraft 1.16.5 nu presupunem că `simulation-distance` din `server.properties` este un control vanilla efectiv; verificăm ce suportă motorul exact înainte de a conta pe el.
4. **A/B câte o variabilă:** întâi 34/13 intact pe copie, apoi numai optimizatorul cu hotspot; aceeași lume pregenerată, număr de jucători și scenarii. La fiecare: două sesiuni repetate, tick real **p95 ≤35 ms / p99 ≤45 ms**, CPU thread principal și total, RSS/GC, I/O, upload/UDP, zerouri la erori RP, client join și restart. [Protocolul complet](CAPACITATE-FUNCITY-RP.md). Dacă lipsesc jucători reali, nu transformăm boții sau zombie în „capacitate demonstrată”.
5. **Hardware dacă se saturează threadul:** un proces Minecraft hibrid nu scalează automat tickul lumii pe 8–16 nuclee prin simpla adăugare de moduri. Contează performanța pe nucleu, RAM/GC, SSD și upload; gazda *istorică* avea 2 fire CPU/~11,9 GiB, dar nu știm dacă acestea sunt resursele de acum. Relatarea despre 60+ pe **alt hosting** HYPECITY nu este măsurătoare pentru acest PC. Nu promit 60 sau 100 fără hardware actual și rampă reală.

**Revizie de piață 22.10.2026:** [auditul suplimentar Forge 1.16.5](VERIFICARE-PIATA-SERVER-1165-2026.md) a găsit un *candidat nou*, Chunk Sending 2.5 server-only ([canary închis 28/6 + 29/6 de două ori PASS](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39704706580), fără clienți sau sarcină de rețea), dar nu a schimbat ținta celor 28 sau decizia live. VMP/ServerCore nu au fișier Forge 1.16.5 verificat, iar Krypton Reforged 1.16 cere clientul; nu sunt „mai multe FPS/TPS gratuite”.

**Ablație țintită pe 28 moduri/6 pluginuri:** [raportul cu date și eșecuri pentru AI, rețete/Placebo, Ksyxis și vehicule](RP-MAFII-MASINI-COST-SERVER-2026.md) arată un semnal Ksyxis în lumea generată. Testul de mașini a fost **invalidat**: 16 entități la început, 0 la sfârșit într-o rerulare; nu există verdict RoadRunner specific mașinilor. Lipsesc condusul, mafiile reale, 34/13 și mulți clienți; nu ștergem ori instalăm JAR-uri în live pe această bază.

**Native-first/opt-only:** [decizia cu porți pentru integrare sau eliminare](DECIZIE-NATIVE-FIRST-FUNCITY.md) clarifică faptul că beneficiul RP al ModernFix/FerriteCore nu a fost încă separat experimental; nu sunt „trei moduri garantat mai rapide”.

**Decizia după testul de reducere:** [brațul 22 vs 28](ALEGERE-CONCRETA-MOTOR-MODURI-2026.md) nu a adus câștig repetabil de runtime și a degradat bootul; **28 rămâne baza de laborator**, nu o instrucțiune de eliminare a celor șase JAR-uri suplimentare de pe PC.

**Concluzie de acțiune:** pentru multe persoane simultan, nu recomand un „mega-hibrid” cu toate JAR-urile de optimizare. Recomand CatServer oficial ca bază de fork, stiva prudentă RoadRunner/ModernFix/FerriteCore, conținut RP integral, pregenerare, măsurarea pluginurilor și modurilor în scenarii reprezentative, apoi doar patchuri sursă profilate. Motorul branduit încă nu este construit și validat; serverul/live-ul și clientul rămân nemodificate.
