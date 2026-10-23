# FunCity Lite — registrul alegerilor (2026-10-19)

**AUDIT HIBRID 23.10.2026 — fără «fixuri» care ascund date pierdute:** [buildul sursă 39992979019](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39992979019) a trecut setup, dar a eșuat la `:forge:compileJava`; s-a revenit la rețeta Gradle serial/javac fork încercată anterior, fără a pretinde că următorul build a trecut. [Brațul izolat de configurație](../functity/capacity/README.md) propune vizibilitatea lagului, reactivarea limitelor Connectivity și dezactivarea eliminării silențioase a entităților Forge cu erori; aceste valori **nu sunt live** și pot compromite loginul unor moduri, deci doar după probă pe copia lumii, client Forge și voice. CatServer are raportări deschise de compatibilitate [chunk loaders](https://github.com/Luohuayu/CatServer/issues/902) și [WorldGuard/modded spawn](https://github.com/Luohuayu/CatServer/issues/903); nu declarăm că FunCity le-a rezolvat. Fără patch speculative de chunk-ticket/hopper, fără promisiune de «cel mai bun hybrid din 2026» sau număr de jucători înainte de A/B real.

**ALEGE CAPACITATE 23.10.2026:** CatServer oficial 1.16.5 este baza auditată pentru **candidatul de sursă FunCity** (LGPL/proveniență păstrată), iar [profilul separat 3 GiB / distanță 4](../functity/capacity/README.md) schimbă *doar* `view-distance=5→4` și watchdogul `-1→60000`; nu este configurația live. Fereastra nominală de chunkuri scade 121→81/jucător, dar capacitatea reală, vehiculele și conectarea 34/13 sunt netestate. 4 rămâne candidat până la A/B cu client/vehicule; nu scădem trackingul jucătorilor, pluginurile sau modurile. Workflowul de sursă încearcă build verificat al identității FunCity; nu este un JAR construit/distribuit ori un motor mai rapid dovedit. Folosim modelele Paper (profilare spark, bugetul de chunkuri) ca **principii**, nu Folia/Paper-only ca înlocuitori pentru Forge+Bukkit. Nicio schimbare pe host/PC din această decizie.

**DECIZIE OPERAȚIONALĂ 23.10.2026 — motorul de pe HidenCloud:** **PĂSTRAT FunCity/Mohist-Tenet actual**, cu `server.jar` neschimbat. Este singurul motor pentru care [hostul cu întregul pack 34 moduri/13 pluginuri a ajuns la `Done`](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39973502888); acesta este cel mai bine **validat funcțional pentru packul actual**, NU demonstrat cel mai rapid, sigur la login/voice sau fără erori (o eroare pre-`Done` rămâne). [CatServer oficial are avantaj sintetic pe 18/6 (15 RP + 3 optimizări)](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39692158792), iar [28/6 a bootat pe ambele](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39694738682), dar niciunul nu a trecut încă lumea reală 34/13+client/login/voice. [E: are 38 launchere distincte](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39991071463), dintre care 15 cu indicii Mohist; inventarul static nu reprezintă test de runtime. **Ce schimbă decizia:** copie izolată a întregului pack/lumii pe Java 11 și RAM 3 GiB, aceleași probe repetate de compatibilitate RP/login/voce/MSPT/RSS, rollback verificat, apoi controlul oficial al panoului pentru pornire. Backupul hostului oprit [39987066839](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39987066839) e verificat, dar nu acoperă intrările suplimentare. Nu promova un motor experimental pe host doar pentru că a câștigat un microbenchmark. **Pentru potențialul de capacitate**, primul candidat pe copie este CatServer oficial, nu pentru live: [cercetarea comparativă 1.16.5 și pragurile de jucători](HIBRID-CAPACITATE-1165-2026-10-23.md).

**ACTUALIZARE 22.10.2026 — prioritară față de vechiul tabel S01–S36:** în serverul de test aliniat profilului Lite, **Clumps este EXCLUS** (tabelul istoric S02 îl marchează în continuare PĂSTRAT numai ca snapshot al țintei vechi de 29). Candidatul nou este **28 moduri**, nu cel vechi de 29 și nu inventarul real citit fără modificări din [CI 39696088517](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39696088517): 34 JAR-uri, 13 pluginuri, toate cele 28 de nume țintă prezente plus 6 extra. [Bootul complet 39694738682](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39694738682) a trecut pe CatServer oficial, FunCity b1.0827 și CatServer vechi cu 28/6, dar nu a validat loginul clientului/world-ul actual. [A/B-ul motor 39692158792](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39692158792) favorizează CatServer oficial pentru CPU/tick pe scenă sintetică; **numai bază pentru fork FunCity pe copie**. RoadRunner + FerriteCore + ModernFix rămân stiva prudentă RP, Performant doar alternativă în loc de RoadRunner. [Raport cu limite și branding](MOTOR-FUNCITY-ALEGERE-TESTE-2026.md). Nu instala/scoate JAR-uri din live pe baza acestui tabel.

**VERDICT DUPĂ FEEDBACK 21.10.2026:** proprietarul spune că performanța Embeddium TEST este „cam la fel”. Nu avem probă A/B cu setări egale, așa că nu îl promovăm; Lite-ul funcțional rămâne Rubidium. TEST se păstrează separat, fără alte schimbări de moduri. [Detalii](RESEARCH-PERFORMANTA-CLIENT.md).

**APLICARE LIMITATĂ 21.10.2026:** candidatul decis a fost creat ca profil Prism separat `FunCity RP Lite Embeddium TEST` în [run 39673731817](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39673731817); nu a fost pornit, deci nu a trecut încă login/RP/FPS. Lite-ul existent, originalul și serverul nu au fost schimbate. [Configurația/criteriile](RESEARCH-PERFORMANTA-CLIENT.md).

**DECIZIA CURENTĂ 21.10.2026:** proprietarul deleagă agentului *numai performanța*, păstrând același conținut RP. [Decizia consolidată](RESEARCH-PERFORMANTA-CLIENT.md): Rubidium + TexTrue Rubidium Options rămân baseline-ul funcțional; Embeddium 0.3.18 + TexTrue Embeddium Options 0.1.1 sunt perechea alternativă aleasă pentru un A/B pe copie, fără modificări în conținut/server/original Prism. Nu o promova până când loginul, grafica RP și câștigul FPS/1% low repetabil sunt dovedite pe PC-ul proprietarului; nu deduce din surse FPS garantat. Serverul avea încă view 6 și clientul Lite render 12 la audit; presetul 5/Fast a fost blocat în siguranță de Prism activ.

**REVIZUIRE A CANDIDAȚILOR 21.10.2026:** «Nu există variante mai bune» nu a fost demonstrat. Există un candidat complet pentru test pe copie: [Embeddium 0.3.18](https://modrinth.com/mod/embeddium/version/0.3.18+mc1.16.5) + [TexTrue's Embeddium Options 0.1.1](https://github.com/ThinkingStudios/textrues-embeddium-options/releases/tag/0.1.1%2Bmc1.16.5), fiecare **în locul** echivalentului Rubidium; Oculus 1.4.7 îndeplinește minimul anunțat în [changelogul Embeddium](https://github.com/FiniteReality/embeddium/wiki/Changelog#0214). Prioritate A/B pe COPIE după presetul grafic, nu instalare automată; compatibilitatea/FPS pe RP-ul nostru nu sunt dovedite. [Comparație și alte piste](RESEARCH-PERFORMANTA-CLIENT.md). Verdictul «Embeddium nu se înlocuiește acum» de mai jos înseamnă doar că live rămâne funcțional până la o probă, nu că alternativa este incompatibilă indiferent de TexTrue.

**OVERRIDE ACTUAL 21.10.2026 (are prioritate față de tabelele istorice de mai jos):** pentru `FunCity RP Lite` local cu login dovedit păstrăm 22 JAR-uri client, **fără** Entity Culling, Embeddium, Dynamic FPS sau Clumps. Serverul live păstrează 34 JAR-uri după scoaterea Clumps și adăugarea Voice Chat, cu backup și login confirmate. [Auditul setărilor PC 39655282257](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39655282257) a arătat că serverul este încă la view 6 și Lite la randare 12/Fancy/particule All/mipmap 4/umbre On, nu la 5. Alegem un preset reversibil Lite 5/Fast/particule Decreased/mipmap 0/umbre Off, **dar încercarea PC 39655771386 a blocat înainte de scriere fiindcă Prism era activ**; nu îl forța și nu pretinde că presetul este aplicat. Entity Culling rămâne exclus: la 5 chunkuri pot exista încă entități ascunse, însă varianta Forge 1.16.5 nu mai e suportată și calculul cere CPU liber; Rubidium rămâne rendererul dovedit compatibil cu loginul și TexTrue. [Raționament și surse](RESEARCH-PERFORMANTA-CLIENT.md). FPS/MSPT necunoscute; schimbarea server view-distance la 5 ar cere oprire normală cu zero jucători, verificare și rollback separat.

> **ARHIVĂ DE COMPARAȚIE, NU ȚINTA ACTUALĂ.** Proprietarul a cerut [pluginuri pentru RP, numai moduri de conținut proprii confirmate și optimizări doar dovedite](PLUGIN-FIRST.md). Verdicturile „PĂSTRAT” de mai jos descriu candidatul istoric 24/29, nu autorizarea pentru un pack nou. `agent/PLUGIN-FIRST.json` este poarta curentă; zero JAR-uri aprobate implicit, vocea rămâne de decis. Nu modifica PC-ul sau lumea existentă după acest tabel.

REVIZUIT 19.10.2026: proprietarul a confirmat vocea RP, survival limitat și **oraș nou construit de el și de jucători, fără protecții preventive în oraș; numai jurnal CoreProtect**; vezi `agent/RP-EVIDENCE.md`. Alegere **în vigoare în repo**; nu este afirmație că acele JAR-uri sunt instalate acum sau că FPS/TPS au fost măsurate. Sursa inventarelor: `diag/pc-client.txt` (25 JAR client, captură PC) și `git show b1ec20c:docs/ENGINE-PACK-AUDIT.md` (36 moduri / 14 pluginuri, arhivă CUANTIC). Motivarea/legăturile către paginile autorilor: `agent/audit-modpack.md`, `agent/revizie-25-moduri.md`, `agent/decizie-server-36.md`; excepții directe: [SpawnerFix](https://www.curseforge.com/minecraft/mc-mods/spawner-fix), [FastSuite](https://www.curseforge.com/minecraft/mc-mods/fastsuite), [Voice Chat](https://modrepo.de/minecraft/voicechat/wiki/installation), [Out of Sight](https://github.com/Corosauce/OutOfSight/blob/master/src/main/java/com/corosus/out_of_sight/config/Config.java). O schimbare de JAR în client/server instalat sau un release cere binar verificat + import/login Forge + RP/rollback; alegerea **precedă** măsurătoarea, dar nu o înlocuiește. Mai jos „sursa” este prescurtată: C = `diag/pc-client.txt` + `agent/audit-modpack.md`, S = auditul arhivei + `agent/audit-modpack.md`, P = auditul pluginurilor din arhivă; verdictul poate fi revizuit numai cu dovada din ultima coloană.

**Actualizare din PC și binare:** [comparația HYPECITY/FunCity](COMPARATIE-HYPECITY-PC.md) arată că 28/29 server alese sunt deja în folderul FunCityLocal, dar numai 7 nume sunt exact aceleași în HYPECITY principal. În [auditul hosted al JAR-urilor](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39301837320), Pizzaland este `Pizzaland Roleplay` (`pizzamod`), cu 8.241 asseturi în binarul client, nu „rol necunoscut”; FastSuite și FastWorkbench declară amândouă Placebo drept dependent necesar. Tabelul `PĂSTRAT` marchează **candidatul moștenit 24/29 pentru comparație**, nu necesitatea dovedită sau minimul Lite; [varianta temporară 23/28 fără Pizzaland](COMPARATIE-HYPECITY-PC.md) a trecut doar auditul structural și al dependențelor declarate ale JAR-urilor incluse; funcțiile RP, bootul și loginul rămân de verificat pe o copie. Nu schimba folderul PC/lumea/release-ul după tabel.

Planul de operare și gates pentru comunitate: `agent/PLAN-COMUNITATE.md`.

**CORECȚIE MULTIPLAYER:** modurile OPT/COMP păstrate sunt ipoteze de selecție, nu un set dovedit optim pentru mulți jucători. Snapshotul vechi cu 15.077 intrări nu păstrează căile majorității fișierelor, iar valoarea `max-players` nu este capacitate. Auditul diferențelor de config, pluginuri istorice și limitelor gazdei: `agent/AUDIT-CAPACITATE-RP.md`. Niciun optimizer nu devine „imposibil de scos” fără A/B pe scenariu RP încărcat și login client real.

**Selecția pentru un singur candidat de test este închisă:** motor FunCity b1.0827, moduri server 29/36 și client 24 (25 istorice −2 + voce). Nu mai înlocuim motorul și nu mai adăugăm optimizări doar pe reputație. Aceasta este o alegere de **ce construim/testăm**, nu o afirmație despre import, instalare, performanță sau capacitate. Rezumat operațional: [motor + server + client](SELECTIE-MOTOR-MODURI-CLIENT.md). HYPECITY-ul proprietarului (peste 60 de jucători, posibil spre 100 după relatarea lui) este reperul de experiență; arhiva CUANTIC oferă doar binarele istorice accesibile pentru candidat, nu configurația HYPECITY.

## Motor și valori

| ID | Alegere | Motiv | Sursa | Ce o schimbă |
|---|---|---|---|---|
| M | FunCity b1.0827 PĂSTRAT ca motor | Forge+Bukkit compatibil cu conținutul RP; nu e dovedit cel mai rapid | `agent/alegere-motor-lean.md`, CI în `agent/PROGRES.md` | candidat cu 3 runde, conectare client Forge și autentificare prin plugin intacte, RP intact, MSPT/RSS mai bune |
| V1 | view-distance=5 | nu tăiem vederea clientului la 5 | `functity-config/server.properties` | vedere RP și A/B justifică altă valoare |
| V2 | entity-broadcast-range-percentage=80 | păstrăm vederea vehiculelor/jucătorilor | `functity-config/server.properties` | A/B rețea/FPS fără pop-in |
| V3 | network-compression-threshold=256 | internet slab; -1 dezactivează compresia | `functity-config/server.properties`; `scripts/functity-stage.sh` | CPU/rețea A/B arată regresie |
| V4 | spawn 20/6/2; nerf-spawner-mobs=false; despawn=6000 | survival RP nu se golește doar pentru TPS | `functity-config/{bukkit,spigot}.yml` | profil + verificare gameplay |
| V5 | keep-spawn-loaded=true, Ksyxis PĂSTRAT | decizie existentă; efectul combinat necunoscut | `functity-config/bukkit.yml`; S | A/B chunks/tick/conectare client cu o singură schimbare |
| V6 | fără mod nou de performanță | cost și risc de compatibilitate nejustificat | `agent/comparatie-proiecte-vechi.md` | hotspot documentat + A/B |
| A1 | autentificarea **contului prin plugin**; JAR/versiune încă nealese | alegere explicită a proprietarului; distinctă de handshake-ul Forge care doar verifică modpackul | declarația proprietarului; `agent/RP-LITE-PLUGINS.md` | plugin compatibil, proveniență/SHA, cont nou+reconectare+izolare înainte de auth testate |

## Client — 25/25 nume istorice plus voce RP, ținta lean 24

| ID | JAR | Alegere | Motiv | Sursa · ce o schimbă |
|---|---|---|---|---|
| C01 | `additional-guns-0.7.1-1.16.5.jar` | PĂSTRAT | arme RP, registru | C · scan lume fără iteme și fără dependent |
| C02 | `cfm-7.0.0pre22-1.16.3.jar` | PĂSTRAT | mobilier RP | C · scan lume + decizie RP |
| C03 | `cgm-1.2.6-1.16.5.jar` | PĂSTRAT | arme RP | C · scan lume + decizie RP |
| C04 | `Clumps-6.0.0.28.jar` | PĂSTRAT | registru XP/handshake | C + `diag/fix.txt` · login fără el |
| C05 | `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | PĂSTRAT | emote RP | C · funcție retrasă explicit |
| C06 | `entitycollisionfpsfix-1.16-1.0.1.jar` | SCOS | cost în aglomerări, beneficiu nejustificat pentru profilul țintă | C · A/B laptop cu aglomerări demonstrează FPS p5 |
| C07 | `entityculling-forge-mc1.16.5-1.5.2.jar` | PĂSTRAT | ocluzie după pereți, nu tăiere de distanță | C + [autor](https://github.com/tr7zw/EntityCulling/blob/main/README.md) · A/B arată cost fără beneficiu |
| C08 | `ferritecore-2.1.1-forge.jar` | PĂSTRAT | RAM client | C · heap A/B fără câștig |
| C09 | `lazydfu-0.1.3.jar` | PĂSTRAT | timp de start | C · start A/B fără câștig |
| C10 | `mapperbase-1.16.5-2.4.0.0.jar` | PĂSTRAT | dependență Road Stuff | C · scoatere părinte |
| C11 | `modernfix-forge-5.18.0+mc1.16.5.jar` | PĂSTRAT | memorie/start și bugfix | C · regresie compatibilitate ori A/B |
| C12 | `modernlife-1.16.5-1.15.jar` | PĂSTRAT | CCTV/mobilier/biciclete RP | C · scan lume + decizie RP |
| C13 | `Modernxl 1.16.5.jar` | PĂSTRAT | mobilier RP | C · scan lume + decizie RP |
| C14 | `obfuscate-0.6.3-1.16.5.jar` | PĂSTRAT | CGM/Vehicle | C · niciun părinte folosit |
| C15 | `oculus-mc1.16.5-1.4.7.jar` | PĂSTRAT | texturi funcționale cu shaders OFF | C + logul vizual documentat · test vizual fără el |
| C16 | `out_of_sight-1.16.4-1.0.1.jar` | SCOS | entități deja limitate în repo; prag tile-entity poate ascunde mobilier | C + [config autor](https://github.com/Corosauce/OutOfSight/blob/master/src/main/java/com/corosus/out_of_sight/config/Config.java) · A/B de scenă RP |
| C17 | `pamhc2foodcore-1.16.3-1.0.2.jar` | PĂSTRAT | hrană/economie | C · scan lume/recipe + decizie RP |
| C18 | `Pizzaland_v68.jar` | PĂSTRAT | `Pizzaland Roleplay`, ID `pizzamod`, 8.241 asseturi client; în candidatul moștenit doar pentru test comparativ, **nu justificat ca necesar**; primul experiment de excludere coordonată înainte de construirea orașului | C + [audit binar](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39301837320) · dependenți + login/RP pe lumea nouă |
| C19 | `player-animation-lib-forge-0.4.0+1.16.5.jar` | PĂSTRAT | dependență Emotecraft | C · scoatere părinte |
| C20 | `radon-0.8.0a.jar` | PĂSTRAT | lumină, distinct de renderer | C · A/B fără câștig/compatibilitate |
| C21 | `roadstuff-1.16.5-4.3.0.jar` | PĂSTRAT | blocuri oraș | C · scan lume + decizie RP |
| C22 | `rubidium-mc1.16.5-0.2.13.jar` | PĂSTRAT | renderer laptop integrat | C · FPS p5/compatibilitate |
| C23 | `selene-1.16.5-1.9.0.jar` | PĂSTRAT | dependență Supplementaries | C · scoatere părinte |
| C24 | `supplementaries-1.16.5-0.18.4b.jar` | PĂSTRAT | decor RP | C · scan lume + decizie RP |
| C25 | `vehicle-mod-0.45.2-1.16.5 (1).jar` | PĂSTRAT | vehicule RP | C · decizie RP |
| C26 | `voicechat-forge-1.16.5-2.3.23.jar` | PĂSTRAT | voce de proximitate pentru mafii și joburi, pereche pentru server | [autor](https://modrepo.de/minecraft/voicechat/wiki/installation) + `agent/voicechat-1.16.5-2.3.23.json` · login/audio/UDP pe copie |

## Server — 36/36 nume din arhivă (nu inventar live)

| ID | JAR | Alegere | Motiv | Sursa · ce o schimbă |
|---|---|---|---|---|
| S01 | `AI-Improvements-1.16.5-0.5.0.jar` | PĂSTRAT | AI tick distinct | S · profil fără hotspot |
| S02 | `Clumps-6.0.0.28.jar` | PĂSTRAT | registry/XP pe ambele părți | S + `diag/fix.txt` · login fără el |
| S03 | `FastFurnace-1.16.5-4.5.0.jar` | SCOS | optimizează căutarea rețetelor cuptorului la fiecare tick; în RP cu survival limitat nu există profil de cuptoare active care să justifice încă un mixin | S + [autor](https://www.curseforge.com/minecraft/mc-mods/fastfurnace) · profil cu multe cuptoare + A/B |
| S04 | `FastSuite-1.16.4-1.1.1.jar` | PĂSTRAT | rețete, funcție distinctă | S + autor · profil/A-B |
| S05 | `FastWorkbench-1.16.5-4.6.2.jar` | PĂSTRAT | banc de lucru, distinct | S + autor FastSuite · profil/A-B |
| S06 | `Ksyxis-1.4.6.jar` | PĂSTRAT | decizie curentă spawn chunks | S · măsurare cu keep-spawn |
| S07 | `Modernxl 1.16.5.jar` | PĂSTRAT | mobilier RP | S · scan lume fără blocuri |
| S08 | `Pizzaland_v68.jar` | PĂSTRAT | Pizzaland Roleplay, ID `pizzamod`; 21 asseturi în server vs. 8.241 în client; păstrat doar în candidatul comparativ, nu cerință RP confirmată | S + [audit binar](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39301837320) · audit dependenți + boot/login fără el |
| S09 | `Placebo-1.16.5-4.7.1.jar` | PĂSTRAT | dependență declarată în `mods.toml` de FastSuite **și** FastWorkbench; nu îl scoate separat | S + [audit binar](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39301837320) · teste după decizia asupra ambilor părinți |
| S10 | `RoadRunner-mc1.16.5-1.5.2.jar` | PĂSTRAT | optimizare server; fără Performant | S · A/B compatibilitate |
| S11 | `SpawnerFix-1.16.2-1.0.0.3.jar` | SCOS | fix randare client, nu TPS server | S + autor · boot/login contrazice |
| S12 | `additional-guns-0.7.1-1.16.5.jar` | PĂSTRAT | arme RP | S · scan lume |
| S13 | `bwncr-1.16.5-3.10.16.jar` | SCOS | audio opțional, nu câștig de capacitate | S · funcție RP demonstrată |
| S14 | `cfm-7.0.0pre22-1.16.3.jar` | PĂSTRAT | mobilier RP | S · scan lume |
| S15 | `cgm-1.2.6-1.16.5.jar` | PĂSTRAT | arme RP | S · scan lume |
| S16 | `connectivity-2.4-1.16.5.jar` | PĂSTRAT | login/rețea | S · login A/B |
| S17 | `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | PĂSTRAT | emote RP | S · funcție retrasă |
| S18 | `ferritecore-2.1.1-forge.jar` | PĂSTRAT | memorie pe 2 core ARM | S · heap/RSS A/B |
| S19 | `getittogetherdrops-1.16.5-v1.2.jar` | PĂSTRAT | mai puține entități drop | S · profil fără hotspot |
| S20 | `incontrol-1.16-5.2.12.jar` | PĂSTRAT | reguli spawn posibile | S + `diag/oldcfg-report.txt` · config activ gol |
| S21 | `lazydfu-0.1.3.jar` | PĂSTRAT | pornire | S · start A/B |
| S22 | `letmedespawn-forge-1.16-1.0.2a.jar` | SCOS | schimbă despawn pentru câștig neconfirmat | S · profil + comportament RP |
| S23 | `mapperbase-1.16.5-2.4.0.0.jar` | PĂSTRAT | dependență Road Stuff | S · scoatere părinte |
| S24 | `memoryleakfix-forge-pre1.17-1.1.5.jar` | SCOS | leak specific nedovedit peste ModernFix | S · leak identificat și remediat |
| S25 | `modernfix-forge-5.18.0+mc1.16.5.jar` | PĂSTRAT | memorie/pornire/bugfix | S · regresie A/B |
| S26 | `modernlife-1.16.5-1.15.jar` | PĂSTRAT | RP | S · scan lume |
| S27 | `obfuscate-0.6.3-1.16.5.jar` | PĂSTRAT | dependență arme/vehicule | S · scoatere părinți |
| S28 | `pamhc2foodcore-1.16.3-1.0.2.jar` | PĂSTRAT | hrană RP | S · scan lume |
| S29 | `player-animation-lib-forge-0.4.0+1.16.5.jar` | PĂSTRAT | dependență Emotecraft | S · scoatere părinte |
| S30 | `roadstuff-1.16.5-4.3.0.jar` | PĂSTRAT | drumuri RP | S · scan lume |
| S31 | `selene-1.16.5-1.9.0.jar` | PĂSTRAT | dependență Supplementaries | S · scoatere părinte |
| S32 | `smoothchunk1.16.5-2.0.jar` | SCOS | fără dovada spike-urilor de save pe lumea noastră | S · profil de save |
| S33 | `spark-1.9.1-forge.jar` | SCOS din runtime normal | profiler numai pentru test | S + [autor](https://modrinth.com/mod/spark/version/9NSIbttL) · profilare necesară |
| S34 | `supplementaries-1.16.5-0.18.4b.jar` | PĂSTRAT | decor RP | S · scan lume |
| S35 | `vehicle-mod-0.45.2-1.16.5 (1).jar` | PĂSTRAT | vehicule RP | S · decizie RP |
| S36 | `voicechat-forge-1.16.5-2.3.23.jar` | PĂSTRAT | voce RP cerută explicit; clientul țintă include aceeași versiune | S + [autor](https://modrepo.de/minecraft/voicechat/wiki/installation) · audio/UDP testat pe copie |

## Pluginurile arhivei vechi; nu pretinde că acestea sunt cele live

Autentificarea jucătorului se face **prin plugin**, de ales/testat: în cele 14 JAR-uri istorice CUANTIC nu se află un plugin AuthMe; doar HYPECITY BK are fișiere de config AuthMe. Nu considerăm autentificarea implementată în ținta actuală și nu importăm date de cont. Oraș nou deschis: **nu există regiuni de protejat**, build-ul jucătorilor este permis; CoreProtect ține numai evidența și rollback-ul manual de admin. Scoaterea pluginurilor preventive este o alegere a țintei pe baza regulii proprietarului, nu dovadă că eliminarea este compatibilă pe serverul live. Rolurile și testele sunt în `agent/RP-LITE-PLUGINS.md`.

| ID | Plugin | Alegere | Motiv | Sursa · ce o schimbă |
|---|---|---|---|---|
| P01 | Chunky | SCOS din runtime normal | pregen e unealtă de laborator | P · pregen autorizat |
| P02 | Cuantic-Brand | SCOS | identitate veche; FunCity în motor | P · dependență funcțională |
| P03 | EssentialsX | PĂSTRAT | comenzi/economie RP | P · funcție echivalentă validată |
| P04 | EssentialsXAntiBuild | SCOS | restricțiile preventive de plasare/spargere contrazic orașul construit liber de jucători | declarația proprietarului · test build/rollback pe copie |
| P05 | EssentialsXChat | PĂSTRAT | chat RP | P · funcție echivalentă |
| P06 | EssentialsXProtect | SCOS | protecție preventivă nedorită; CoreProtect este jurnal, nu înlocuitor de restricții | declarația proprietarului · test evenimente/backup pe copie |
| P07 | EssentialsXSpawn | PĂSTRAT | spawn și comenzi | P · funcție echivalentă |
| P08 | LuckPerms | PĂSTRAT | permisiuni | P · migrare verificată |
| P09 | ProtocolLib | PĂSTRAT | posibil dependent plugin/protocol | P · audit binar dependențe |
| P10 | SkinsRestorer | PĂSTRAT | skinuri RP | P · funcție nefolosită |
| P11 | Vault | PĂSTRAT | interfață economie/pluginuri | P · audit dependent |
| P12 | claimchunk | SCOS | fără claims ori teren privat protejat | declarația proprietarului · decizie RP inversată |
| P13 | WorldEdit | SCOS din runtime normal | unealtă de construcție admin, nu necesară construcției libere de jucători; separat doar la cerere | P · nevoie de editări admin demonstrată |
| P14 | WorldGuard | SCOS | nici spawnul, nici zona mafii/poliție nu sunt protejate preventiv | declarația proprietarului · cerință nouă de regiune explicită |
| P15* | CoreProtect | PĂSTRAT ca cerință | log unic al acțiunilor și rollback manual admin; **nu apare în cele 14 istorice** | declarația proprietarului · compatibilitate modded probată / soluție alternativă validată |

*P15 nu este un JAR găsit în arhiva istorică; înainte de beta cu incidente se verifică existența binarului și permisiunile în packul efectiv.*
