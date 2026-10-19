# FunCity Lite — registrul alegerilor (2026-10-19)

REVIZUIT 19.10.2026: proprietarul a confirmat vocea RP și survival limitat; vezi `agent/RP-EVIDENCE.md`. Alegere **în vigoare în repo**; nu este afirmație că acele JAR-uri sunt instalate acum sau că FPS/TPS au fost măsurate. Sursa inventarelor: `diag/pc-client.txt` (25 JAR client, captură PC) și `git show b1ec20c:docs/ENGINE-PACK-AUDIT.md` (36 moduri / 14 pluginuri, arhivă CUANTIC). Motivarea/legăturile către paginile autorilor: `agent/audit-modpack.md`, `agent/revizie-25-moduri.md`, `agent/decizie-server-36.md`; excepții directe: [SpawnerFix](https://www.curseforge.com/minecraft/mc-mods/spawner-fix), [FastSuite](https://www.curseforge.com/minecraft/mc-mods/fastsuite), [Voice Chat](https://modrepo.de/minecraft/voicechat/wiki/installation), [Out of Sight](https://github.com/Corosauce/OutOfSight/blob/master/src/main/java/com/corosus/out_of_sight/config/Config.java). O schimbare de JAR în client/server instalat sau un release cere binar verificat + import/login Forge + RP/rollback; alegerea **precedă** măsurătoarea, dar nu o înlocuiește. Mai jos „sursa” este prescurtată: C = `diag/pc-client.txt` + `agent/audit-modpack.md`, S = auditul arhivei + `agent/audit-modpack.md`, P = auditul pluginurilor din arhivă; verdictul poate fi revizuit numai cu dovada din ultima coloană.

## Motor și valori

| ID | Alegere | Motiv | Sursa | Ce o schimbă |
|---|---|---|---|---|
| M | FunCity b1.0827 PĂSTRAT ca motor | Forge+Bukkit compatibil cu conținutul RP; nu e dovedit cel mai rapid | `agent/alegere-motor-lean.md`, CI în `agent/PROGRES.md` | candidat cu 3 runde, login și RP intacte, MSPT/RSS mai bune |
| V1 | view-distance=5 | nu tăiem vederea clientului la 5 | `functity-config/server.properties` | vedere RP și A/B justifică altă valoare |
| V2 | entity-broadcast-range-percentage=80 | păstrăm vederea vehiculelor/jucătorilor | `functity-config/server.properties` | A/B rețea/FPS fără pop-in |
| V3 | network-compression-threshold=256 | internet slab; -1 dezactivează compresia | `functity-config/server.properties`; `scripts/functity-stage.sh` | CPU/rețea A/B arată regresie |
| V4 | spawn 20/6/2; nerf-spawner-mobs=false; despawn=6000 | survival RP nu se golește doar pentru TPS | `functity-config/{bukkit,spigot}.yml` | profil + verificare gameplay |
| V5 | keep-spawn-loaded=true, Ksyxis PĂSTRAT | decizie existentă; efectul combinat necunoscut | `functity-config/bukkit.yml`; S | A/B chunks/tick/login cu o singură schimbare |
| V6 | fără mod nou de performanță | cost și risc de compatibilitate nejustificat | `agent/comparatie-proiecte-vechi.md` | hotspot documentat + A/B |

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
| C18 | `Pizzaland_v68.jar` | PĂSTRAT | registry neidentificat; risc pentru lume | C · audit binar/lume |
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
| S08 | `Pizzaland_v68.jar` | PĂSTRAT | registry neidentificat | S · audit lume/binar |
| S09 | `Placebo-1.16.5-4.7.1.jar` | PĂSTRAT | bibliotecă pentru stack | S · audit dependențe binare |
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

Rolurile unice, suprapunerile *de investigat* (EssentialsXAntiBuild/WorldGuard/LuckPerms și EssentialsXProtect/WorldGuard), cerința CoreProtect și auditul binar read-only sunt descrise în `agent/RP-LITE-PLUGINS.md`. Nu elimina pluginuri PĂSTRATE doar pentru că numele funcțiilor seamănă: configul activ și testele de protecție încă lipsesc.

| ID | Plugin | Alegere | Motiv | Sursa · ce o schimbă |
|---|---|---|---|---|
| P01 | Chunky | SCOS din runtime normal | pregen e unealtă de laborator | P · pregen autorizat |
| P02 | Cuantic-Brand | SCOS | identitate veche; FunCity în motor | P · dependență funcțională |
| P03 | EssentialsX | PĂSTRAT | comenzi/economie RP | P · funcție echivalentă validată |
| P04 | EssentialsXAntiBuild | PĂSTRAT | permisiuni existente necunoscute | P · audit reguli dovedește neutilizare |
| P05 | EssentialsXChat | PĂSTRAT | chat RP | P · funcție echivalentă |
| P06 | EssentialsXProtect | PĂSTRAT | protecție configurată necunoscută | P · audit funcție/permisiuni |
| P07 | EssentialsXSpawn | PĂSTRAT | spawn și comenzi | P · funcție echivalentă |
| P08 | LuckPerms | PĂSTRAT | permisiuni | P · migrare verificată |
| P09 | ProtocolLib | PĂSTRAT | posibil dependent plugin/protocol | P · audit binar dependențe |
| P10 | SkinsRestorer | PĂSTRAT | skinuri RP | P · funcție nefolosită |
| P11 | Vault | PĂSTRAT | interfață economie/pluginuri | P · audit dependent |
| P12 | claimchunk | SCOS | oraș deschis, fără claims | P + `AGENTS.md` · decizie RP inversată |
| P13 | WorldEdit | PĂSTRAT | administrare oraș | P · neutilizare/înlocuitor |
| P14 | WorldGuard | PĂSTRAT | reguli regiuni necunoscute; nu-l confunda cu claims jucători | P · audit regiuni active |
| P15* | CoreProtect | PĂSTRAT ca cerință | registrul unic de incidente; **nu apare în cele 14** | `AGENTS.md` · soluție alternativă validată |

*P15 nu este un JAR găsit în arhiva istorică; înainte de beta cu incidente se verifică existența binarului și permisiunile în packul efectiv.*
