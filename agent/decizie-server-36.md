# FunCity — alegerea serverului de test, mod cu mod (2026-10-19)

> Actualizare V2: `agent/DECIZII.md` are verdictul PĂSTRAT/SCOS pentru toate cele 36; acest tabel descrie baseline-ul istoric, nu lista de instalare. REVIZUIT după clarificarea RP: S03 FastFurnace SCOS din țintă, S36 Voice Chat PĂSTRAT pe server și în clientul nou.

**Bază verificată:** `git show b1ec20c:docs/ENGINE-PACK-AUDIT.md` inventariază **36 JAR-uri de server și 14 pluginuri** într-un ZIP public pinuit. NU dovedește inventarul live sau că un mod reduce TPS. Auditul surselor pentru 25 JAR-uri client și 15 nume suplimentare server este în `agent/audit-modpack.md`; pentru ultimele două moduri din inventarul de 36, vezi [spark 1.9.1](https://modrinth.com/mod/spark/version/9NSIbttL) și [instalarea Simple Voice Chat](https://modrepo.de/minecraft/voicechat/wiki/installation). **Decizia de acum:** motor de comparație FunCity b1.0827, fără JAR nou; `agent/alegere-motor-lean.md` explică de ce. **36 nu este ținta finală!** `P` = păstrăm NUMAI în baseline/copia A, NU că beneficiul lui e demonstrat; orice optimizare P fără hotspot sau A/B pozitiv este candidat pentru copia lean, testat individual. `T` = candidat timpuriu de scoatere/config pe copia B, nu live; `L` = depinde de conținutul RP efectiv folosit, dependențe și client. Alegerea finală pe nume necesită măsurare, nu presupunerea că „mai multe optimizări” ajută.

| # | JAR exact în ZIP | Decizie | Motiv / proba care poate schimba decizia |
|---:|---|:---:|---|
| 1 | `AI-Improvements-1.16.5-0.5.0.jar` | P | AI server; nu costă PC, dar verifică profil tick și comportamentul moburilor. |
| 2 | `Clumps-6.0.0.28.jar` | P | XP orbs; registru client–server a eșuat anterior fără el. |
| 3 | `FastFurnace-1.16.5-4.5.0.jar` | P | Rețete/cuptoare; autorul FastSuite spune că nu e înlocuit complet de FastSuite. Dacă profilul nu arată hotspot, A/B separat. |
| 4 | `FastSuite-1.16.4-1.1.1.jar` | P | Rețete JSON; autorul recomandă triada cu FastFurnace/Workbench pentru performanță maximă *în rețete*, nu TPS universal ([1](https://www.curseforge.com/minecraft/mc-mods/fastsuite)). |
| 5 | `FastWorkbench-1.16.5-4.6.2.jar` | P | Banc de lucru/recipe cache; A/B doar după profil. |
| 6 | `Ksyxis-1.4.6.jar` | T | Spawn chunks; `keep-spawn-loaded:true` în `bukkit.yml` repo poate contrazice câștigul. Testează număr chunkuri și spawn separat, fără ambele variabile odată. |
| 7 | `Modernxl 1.16.5.jar` | L | Mobilier RP; nu șterge blocuri salvate pentru un câștig neprobat. |
| 8 | `Pizzaland_v68.jar` | L | Binar/registry RP neidentificat complet; audit de lume/sursă înainte de orice eliminare. |
| 9 | `Placebo-1.16.5-4.7.1.jar` | P | Bibliotecă, nu bonus TPS în sine; verifică dependențele reale ale JAR-urilor înainte de scoatere ([7](https://www.curseforge.com/minecraft/mc-mods/placebo/files/4501015)). |
| 10 | `RoadRunner-mc1.16.5-1.5.2.jar` | P | Optimizare logică/tick. Nu suprapune Performant din HYPECITY fără compatibilitate și A/B. |
| 11 | `SpawnerFix-1.16.2-1.0.0.3.jar` | T | Autorul îl numește corecție **client-side de randare** a spawnerelor ([1](https://www.curseforge.com/minecraft/mc-mods/spawner-fix)); primul braț server fără el e pregătit în `scripts/fc_spawner_ab.py`. |
| 12 | `additional-guns-0.7.1-1.16.5.jar` | L | Arme RP peste CGM; verifică itemele lumii și folosirea înainte de eliminare. |
| 13 | `bwncr-1.16.5-3.10.16.jar` | T | Localizează sunetul Wither/dragon; nu e optimizare TPS, dar verifică audio/gameplay înainte de probă fără el. |
| 14 | `cfm-7.0.0pre22-1.16.3.jar` | L | Mobilier funcțional și blocuri salvate; baseline păstrat. |
| 15 | `cgm-1.2.6-1.16.5.jar` | L | Arme RP; păstrează împreună cu Obfuscate dacă sunt folosite. |
| 16 | `connectivity-2.4-1.16.5.jar` | P | Rețea/login; două erori istorice Clumps cer test de handshake, nu scoatere oarbă. |
| 17 | `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | L | Emote multiplayer; dacă sunt folosite, păstrează Player Animation Lib. |
| 18 | `ferritecore-2.1.1-forge.jar` | P | Reducere memorie; nu promite procent fără măsurare pe packul nostru. |
| 19 | `getittogetherdrops-1.16.5-v1.2.jar` | P | Reduce numărul de drop-uri/tick în scenarii aglomerate; A/B după hotspot, fără schimbarea lootului pe nevăzute. |
| 20 | `incontrol-1.16-5.2.12.jar` | T | Reguli spawn/gameplay; dacă nu există reguli active în configul *încărcat*, candidat de eliminare. Inventarul ZIP nu e dovada regulilor. |
| 21 | `lazydfu-0.1.3.jar` | P | Pornire; nu vinde drept câștig TPS în joc. |
| 22 | `letmedespawn-forge-1.16-1.0.2a.jar` | P | Despawn de mobi cu iteme; poate modifica gameplay, profil + test de comportament. |
| 23 | `mapperbase-1.16.5-2.4.0.0.jar` | L | Bibliotecă necesară cât timp rămâne Road Stuff. |
| 24 | `memoryleakfix-forge-pre1.17-1.1.5.jar` | P | Leak-uri pe termen lung, nu FPS instant; verifică GC/heap în sesiune lungă. |
| 25 | `modernfix-forge-5.18.0+mc1.16.5.jar` | P | Memorie/pornire și corecții; verifică compatibilitatea cu RoadRunner, nu adăuga alt mixin stack. |
| 26 | `modernlife-1.16.5-1.15.jar` | L | CCTV/obiecte/bicicletă RP; audit lume/client înainte de scoatere. |
| 27 | `obfuscate-0.6.3-1.16.5.jar` | L | Dependență CGM/Vehicle; nu-l scoate separat de părinți. |
| 28 | `pamhc2foodcore-1.16.3-1.0.2.jar` | L | Mâncare/economie; dacă nu se folosește, primul test este pe copie de lume. |
| 29 | `player-animation-lib-forge-0.4.0+1.16.5.jar` | L | Bibliotecă Emotecraft; nu o scoate singură. |
| 30 | `roadstuff-1.16.5-4.3.0.jar` | L | Drumuri/blocuri oraș; dacă lumea le folosește, rămâne și Mapper Base. |
| 31 | `selene-1.16.5-1.9.0.jar` | L | Bibliotecă Supplementaries; nu o scoate singură. |
| 32 | `smoothchunk1.16.5-2.0.jar` | P | Distribuie salvările chunkurilor; măsoară spikes de MSPT la save, nu FPS client. |
| 33 | `spark-1.9.1-forge.jar` | T | **Profiler**, nu optimizer; păstrează în laborator pentru top hotspoturi, decide separat dacă trebuie încărcat permanent în producție ([2](https://modrinth.com/mod/spark/version/9NSIbttL)). |
| 34 | `supplementaries-1.16.5-0.18.4b.jar` | L | Decorațiuni/utilități RP; Selene cât timp rămâne. |
| 35 | `vehicle-mod-0.45.2-1.16.5 (1).jar` | L | Vehicule RP; necesită Obfuscate, verifică entități salvate. |
| 36 | `voicechat-forge-1.16.5-2.3.23.jar` | T | Dacă vrem voce RP, autorul cere mod și pe client; inventarul istoric client 25 **nu îl are**. Poate intra în joc fără voce, dar funcția nu merge fără client compatibil ([1](https://modrepo.de/minecraft/voicechat/wiki/installation)). Nu pretinde voce activă; testează decizia audio separat, nu adăuga JAR pe PC fără compatibilitate. |

**Ipoteze concurente/prag înainte de schimbări:** H1 scoaterea SpawnerFix din **serverul de test** simplifică bootstrap fără afectarea registrului, a spawnerelor și a clientului; H2 nu schimbă nimic sau rupe un mixin pe motorul hibrid. Compară exact un JAR, același SHA pack/motor/snapshot de lume, 3/3 porniri pe fiecare braț, zero erori critice, login Forge și funcții RP. Pentru performanță cere scenariu cu jucători, MSPT p95 ≤45 ms, TPS mediu ≥19,5, RSS/GC/network și avantaj stabil >zgomot, fără regresie gameplay; la eșec se păstrează JAR-ul. Scripturile au numai fixture-uri, **nu un A/B real**. Ksyxis/keep-spawn, InControl, bwncr, spark și vocea sunt experimente **separate**, fără combinarea eliminărilor.

**Nu putem demonstra „combinația de performanță maximă”** doar din paginile autorilor sau numărul de fișiere: lumea, profilul de jucători, configul activ și laptopul nu sunt măsurate. Nu există pack ZIP/JAR server de test accesibil local, nici login Forge validat pentru o selecție nouă. Alegerea finală *de acum* este baseline-ul cu funcțiile RP și optimizările existente, **niciun mod/plugin nou**, plus primul candidat clar SpawnerFix **doar în laborator**. Nu schimba serverul live, lumea sau release-ul fără backup, rollback probat și confirmare.
