# Auditul modurilor din fostul candidat Lite: rost și cost posibil

> **Context istoric.** [Noua regulă plugin-first](PLUGIN-FIRST.md) nu mai păstrează automat niciun mod din tabel: numai conținut propriu confirmat și optimizări demonstrate, după probe. Tabelul explică fostul candidat 24/29, nu o listă nouă de instalare.

**Ținta din repo, nu packul instalat:** 24 moduri client / 29 server = 20 comune, 4 numai client, 9 numai server. Pe PC, [inventarul read-only](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39300017812) a găsit încă 25 moduri într-un profil Prism și 34 în folderul serverului local; nu le-am schimbat. „Cost” mai jos descrie **ce resursă ar putea solicita**, nu o măsurătoare de FPS, RAM sau TPS. Niciun mod nu devine „degeaba” doar pentru că nu optimizează; dacă aduce un obiect RP folosit, are un scop. Deciziile de eliminare se probează pe o copie, cu client/server aliniate.

**Cifre reale disponibile:** în ZIP-ul vechi `.mrpack`, `Pizzaland_v68.jar` ocupă **83.093.958 B comprimați** și `Modernxl 1.16.5.jar` **35.404.591 B comprimați** (împreună ~118,5 MB din ~135,8 MB ai arhivei). [Auditul binar hosted](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39301837320) arată că Pizzaland este **Pizzaland Roleplay** (`pizzamod`): binarul client are 8.241 fișiere `assets/`, cel server 21; ModernXL are 4.631 pe client, 2 pe server. Numele egale nu înseamnă JAR-uri byte-identice. Asta dovedește mult conținut livrat pe client, **nu** FPS/RAM măsurat. Alte efecte runtime cer probe; nu inventăm procente.

## Pe client **și** pe server — 20

| JAR exact | Ce oferă / de ce rămâne | Cost posibil; e „degeaba”? |
|---|---|---|
| `additional-guns-0.7.1-1.16.5.jar` | Arme suplimentare pentru CGM, funcție RP. | Modele/texturi și registru pe ambele părți. **Candidat** dacă nimeni nu folosește armele acestui addon, nu scoatem fără test. |
| `cfm-7.0.0pre22-1.16.3.jar` | Mobilier utilizabil în oraș. | Asseturi și blocuri; **păstrăm** cât timp acel mobilier intră în design. |
| `cgm-1.2.6-1.16.5.jar` | Sistemul de arme folosit de Additional Guns. | Modele, efecte și logica armelor; **păstrăm** pentru RP, cu Obfuscate. |
| `Clumps-6.0.0.28.jar` | Grupa XP și păstrează același registru client/server; am avut eroare `clumps:xp_orb_big`. | Un mod în plus, dar poate reduce mulțimea de globuri XP. **Nu îl scoatem unilateral**. |
| `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | Emote sincronizate pentru RP. | Animații pe client și sincronizare; **păstrăm** dacă emotele sunt folosite, altfel reevaluăm împreună cu biblioteca sa. |
| `ferritecore-2.1.1-forge.jar` | Reducerea utilizării de memorie a unor structuri. | Mixinuri/compatibilitate; câștig RAM **nemăsurat** aici. **Păstrăm** până la A/B. |
| `lazydfu-0.1.3.jar` | Scurtează uneori pornirea. | Nu promitem FPS sau TPS în joc. **Candidat de scos** dacă timpul de start nu se îmbunătățește. |
| `mapperbase-1.16.5-2.4.0.0.jar` | Bibliotecă pentru Road Stuff. | Încă o bibliotecă; **nu e inutilă** cât timp păstrăm blocurile de drum. |
| `modernfix-forge-5.18.0+mc1.16.5.jar` | Corecții și optimizări de pornire/memorie. | Mixinuri pot interacționa cu alte moduri; **păstrăm**, verificăm compatibilitatea. |
| `modernlife-1.16.5-1.15.jar` | CCTV, biciclete și mobilier distinct de CFM. | Blocuri/entități/texturi; **păstrăm** funcțiile RP folosite, audităm dacă sunt nefolosite. |
| `Modernxl 1.16.5.jar` | Mobilier modern, set separat de CFM/ModernLife. | **35,4 MB comprimați** în ZIP-ul vechi plus asseturi în client. **Audit prioritar** al pieselor dorite; suprapunerea de categorie nu dovedește că sunt aceleași obiecte. |
| `obfuscate-0.6.3-1.16.5.jar` | Dependență pentru CGM și Vehicle pe 1.16.5. | Bibliotecă în ambele părți; **obligatorie cât timp rămân armele/vehiculele**. |
| `pamhc2foodcore-1.16.3-1.0.2.jar` | Alimente/rețete pentru economie și survival limitat. | Registru și rețete; **candidat** dacă nu există job ori mâncare RP care le folosește. |
| `Pizzaland_v68.jar` | Metadata binară confirmă **Pizzaland Roleplay**, mod ID `pizzamod` (nu dependență declarată a lui ModernXL). Utilizarea obiectelor sale în RP nu e dovedită. | **83,1 MB comprimați** în vechiul ZIP; 8.241 fișiere asset în binarul client. Lipsește din ambele inventare HYPECITY server. **Nu îl justificăm în minimul Lite doar prin moștenire**: primul candidat de excludere pe copia de test, cu verificarea obiectelor, dependențelor tuturor modurilor și login/registry. |
| `player-animation-lib-forge-0.4.0+1.16.5.jar` | Biblioteca animațiilor Emotecraft. | Bibliotecă suplimentară; **păstrăm** cât timp Emotecraft depinde de ea. |
| `roadstuff-1.16.5-4.3.0.jar` | Drumuri și blocuri pentru construcția orașului. | Asseturi/registru; **păstrăm** dacă se construiește cu ele, altfel reevaluăm și Mapper Base înaintea lumii. |
| `selene-1.16.5-1.9.0.jar` | Bibliotecă pentru Supplementaries. | Încă o bibliotecă; **păstrăm** cât timp există Supplementaries. |
| `supplementaries-1.16.5-0.18.4b.jar` | Decor și mici mecanici RP. | Asseturi, blocuri și posibile block entities; **păstrăm** doar cu funcțiile dorite testate. |
| `vehicle-mod-0.45.2-1.16.5 (1).jar` | Vehiculele cerute pentru oraș. | Randare pe client, entități/tick/rețea pe server când sunt folosite; **păstrăm** funcția RP, măsurăm la trafic real. |
| `voicechat-forge-1.16.5-2.3.23.jar` | Voce de proximitate pentru mafii/joburi, în ambele părți. | Binarul oficial declarat ~7,84 MB, CPU/rețea și port UDP la utilizare; **păstrăm** și testăm audio cu doi clienți. Nu este pluginul de autentificare. |

## Numai pe **client** — încă 4

| JAR exact | Ce oferă / de ce rămâne | Cost posibil; e „degeaba”? |
|---|---|---|
| `entityculling-forge-mc1.16.5-1.5.2.jar` | Nu desenează entități ascunse după pereți. | Folosește puțin CPU pentru verificări, poate economisi GPU; **păstrăm** până la test de vizibilitate și FPS. |
| `oculus-mc1.16.5-1.4.7.jar` | Compatibilitate vizuală cu Rubidium; fără el au fost raportate texturi defecte. | Cod suplimentar chiar cu shaders oprite; **păstrăm** până când proba fără el păstrează textura corectă. |
| `radon-0.8.0a.jar` | Lucrări de iluminare distincte de renderer. | Mixinuri și cost/beneficiu **neconfirmate** în scena noastră; **candidat A/B**, nu promisiune de FPS. |
| `rubidium-mc1.16.5-0.2.13.jar` | Renderer alternativ pentru clientul Forge. | Compatibilitatea și afișarea blocurilor trebuie probate; **păstrăm** ca optimizare relevantă pentru GPU integrat. |

## Numai pe **server** — încă 9; nu se descarcă pe laptopul jucătorului

| JAR exact | Ce oferă / de ce rămâne | Cost posibil; e „degeaba”? |
|---|---|---|
| `AI-Improvements-1.16.5-0.5.0.jar` | Reduce posibil costul AI al mobilor. | Mixinuri; **candidat A/B** dacă scena RP nu are cost AI relevant. |
| `FastSuite-1.16.4-1.1.1.jar` | Optimizări ale căutării rețetelor. | Mixinuri/caching; **candidat A/B** dacă survivalul redus nu încarcă sistemul. |
| `FastWorkbench-1.16.5-4.6.2.jar` | Optimizarea bancurilor de lucru, diferită de FastSuite. | Mixinuri/caching; **candidat A/B** dacă craftingul nu este hotspot. |
| `Ksyxis-1.4.6.jar` | Schimbă comportamentul chunkurilor de spawn. | Posibilă suprapunere cu `keep-spawn-loaded=true`; **audit prioritar** al configului încărcat și A/B. |
| `Placebo-1.16.5-4.7.1.jar` | **Dependență binară declarată** de FastSuite și FastWorkbench în JAR-urile verificate. | Nu îl scoatem singur; doar odată cu ambii părinți, dacă nu există și alți dependenți. Nu este un optimizer independent. |
| `RoadRunner-mc1.16.5-1.5.2.jar` | Optimizări ale logicii/tickului. | Mixinuri și risc de incompatibilitate; **păstrăm** până la MSPT A/B, fără a adăuga Performant peste el. |
| `connectivity-2.4-1.16.5.jar` | Tratează posibile probleme de conectare/pachete Forge. | Mod de rețea în plus; **păstrăm** până la conectare client stabilă și audit al limitelor dezactivate. Nu autentifică contul. |
| `getittogetherdrops-1.16.5-v1.2.jar` | Unește dropuri pentru mai puține entități. | Mixinuri/alterare de loot; **candidat A/B** dacă nu avem multe dropuri în scena RP. |
| `incontrol-1.16-5.2.12.jar` | Poate aplica reguli personalizate de spawn. | Dacă nu există reguli active pe lumea nouă, poate fi cost/complexitate inutile; **audit prioritar** al configului efectiv. |

## Ce am scos deja **din ținta de test**, nu de pe PC/live

- Client: `out_of_sight-1.16.4-1.0.1.jar` poate ascunde mobilier modat la distanță; `entitycollisionfpsfix-1.16-1.0.1.jar` are beneficiu nedovedit în scena noastră. Entity Culling rămâne pentru ocluzie după zid.
- Server: `SpawnerFix` este descris ca fix de randare client, nu de tick server; `bwncr` e audio opțional; `FastFurnace`, `letmedespawn`, `memoryleakfix`, `smoothchunk` au cost/beneficiu neprobat ori schimbă gameplay; `spark` nu stă în runtime normal, se folosește doar la profilare. Acestea sunt decizii de selecție, **nu** dovada unui câștig MSPT.

**Experiment verificat doar structural:** [A 24/29 versus B 23/28 fără Pizzaland](COMPARATIE-HYPECITY-PC.md) a produs un ZIP client B de **52.677.334 B** față de **135.771.416 B** pentru A; niciun JAR inclus fizic în B (28 server, 10 client) nu declară `pizzamod` drept dependență obligatorie. Nu este import, login, măsurătoare RAM/FPS sau verdict despre conținutul RP.

**Verdict practic:** `Pizzaland` și `ModernXL` sunt primele întrebări despre volumul clientului; `Pam's Food`, Additional Guns și unele decorațiuni sunt condiționate de folosirea lor în RP. Pe server, `In Control!`, `Ksyxis` și triada **FastSuite + FastWorkbench + Placebo** sunt verificările potrivite împotriva „modurilor în plus degeaba”. Placebo singur **nu** este candidat: ambii optimizatori declarați depind de el. Restul păstrează fie o funcție RP cerută, fie o dependență/compatibilitate necesară, fie o optimizare de probat. Pentru nicio piesă nu există încă FPS/RAM/MSPT măsurat în lumea FunCity cu clientul Lite. Compararea directă a inventarelor PC: [HYPECITY versus FunCity](COMPARATIE-HYPECITY-PC.md).
