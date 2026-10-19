# Lista exactă a modurilor din ținta FunCity RP Lite — 19.10.2026

**Țintă de repo, nu pack instalat/live:** **24 JAR-uri client** și **29 JAR-uri server**, conform `agent/DECIZII.md` (20 comune, 4 numai client, 9 numai server). Orașul nou începe de la zero, îl construiesc proprietarul și jucătorii; fără protecții preventive, cu CoreProtect doar ca jurnal/rollback manual admin (CoreProtect este **plugin**, nu mod din tabel). Ținta încă NU a fost importată/testată în Minecraft; nu confundăm inventarul static cu necesitatea sau performanța măsurată.

**Cum citești „de ce rămâne”:** `RP` = funcție selectată, nu imposibil de eliminat; `DEP` = bibliotecă necesară **cât rămâne** modul părinte; `COMP` = potrivire client/server sau defect vizual/handshake raportat care necesită probă înainte de scoatere; `OPT` = beneficiu plauzibil, **nemăsurat** pe laptop/serverul nostru; `AUDIT` = proveniență/registru/dependeți neclari, nu un verdict că trebuie păstrat. Orice conținut nou se decide **înainte** de construcția lumii; după ce există iteme/blocuri salvate se verifică lumea și rollback-ul. „Înlocuire” înseamnă teste pe client+server, nu redenumirea unui JAR.

## În **ambele** părți — 20 JAR-uri exacte

| JAR | De ce rămâne acum; ce permite scoaterea/înlocuirea |
|---|---|
| `additional-guns-0.7.1-1.16.5.jar` | RP: addon de arme CGM, nu încă un motor independent de arme; se poate omite dacă armele lui nu intră în design, înainte de lumea nouă și după test de dependență/registry. |
| `cfm-7.0.0pre22-1.16.3.jar` | RP: mobilier funcțional; scoaterea pierde piesele sale distincte, nu dovedește că ModernXL e înlocuitor. Decide setul de mobilier înainte de construit. |
| `cgm-1.2.6-1.16.5.jar` | RP: arme și bază pentru Additional Guns; alternativă doar dacă se schimbă întregul sistem de arme, permisiuni și funcția în joc. |
| `Clumps-6.0.0.28.jar` | COMP: XP/registru pe ambele părți; au existat erori `clumps:xp_orb_big`. Eliminare numai coordonată client/server, cu login Forge, XP și registry probate. |
| `emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar` | RP: emote multiplayer; poate fi scos dacă renunțăm explicit la emote, apoi poate fi reevaluată și biblioteca de animație. |
| `ferritecore-2.1.1-forge.jar` | OPT: memorie pe ambele părți; nu e obligatoriu pentru gameplay prin nume. Rămâne până la test RAM/GC și compatibilitate A/B. |
| `lazydfu-0.1.3.jar` | OPT: pornire, nu FPS/TPS în joc. Poate fi scos după timp de start repetat și login intact. |
| `mapperbase-1.16.5-2.4.0.0.jar` | DEP: Road Stuff îl cere. Scoatere numai împreună cu Road Stuff după decizia privind blocurile de drum. |
| `modernfix-forge-5.18.0+mc1.16.5.jar` | OPT/compatibilitate: memorie, pornire și corecții; comparație A/B și test Forge înaintea înlocuirii, fără a adăuga mixin-uri la întâmplare. |
| `modernlife-1.16.5-1.15.jar` | RP: CCTV, obiecte, mobilier și biciclete; poate fi omis dacă se renunță la aceste funcții înaintea lumii noi. Nu e sinonim cu CFM. |
| `Modernxl 1.16.5.jar` | RP provizoriu: mobilier modern, ~35,4 MB comprimați în vechiul ZIP. Candidat real de simplificare dacă piesele nu sunt dorite; compară setul de blocuri cu CFM/ModernLife, apoi testează pe ambele părți. |
| `obfuscate-0.6.3-1.16.5.jar` | DEP: CGM/Vehicle pe 1.16.5. Scoatere doar dacă ambii părinți sunt eliminați/înlocuiți și Forge confirmă compatibilitatea. |
| `pamhc2foodcore-1.16.3-1.0.2.jar` | RP opțional: hrană/economie cu survival limitat; nu e indispensabil. Poate fi omis înainte de construirea lumii dacă nu există job/rețetă RP care îl cere. |
| `Pizzaland_v68.jar` | AUDIT prioritar: rolul, licența, registrul și dependențele exactului JAR nu sunt confirmate; ~83,1 MB comprimați în ZIP-ul vechi. **Nu există dovadă că nu poate fi scos.** Prima candidatură pentru un test separat fără el pe ambele părți înainte de generarea lumii noi; nu îl scoatem nevăzut. |
| `player-animation-lib-forge-0.4.0+1.16.5.jar` | DEP: animațiile Emotecraft. Scoatere dacă Emotecraft și alți dependenți sunt absenți, confirmat prin metadata/login. |
| `roadstuff-1.16.5-4.3.0.jar` | RP: blocuri de drum pentru oraș; se poate omite dacă orașul nu le folosește, odată cu Mapper Base și înainte de construire. |
| `selene-1.16.5-1.9.0.jar` | DEP: Supplementaries. Scoatere numai dacă nu mai există niciun dependent. |
| `supplementaries-1.16.5-0.18.4b.jar` | RP: decor/utilități distincte; poate fi eliminat dacă se renunță la conținut, împreună cu Selene dacă nu mai are alți dependenți. |
| `vehicle-mod-0.45.2-1.16.5 (1).jar` | RP: vehiculele orașului; nu poate fi substituit cu un mod de FPS. Schimbarea modelului de vehicule cere test de entități, client/server și Obfuscate. |
| `voicechat-forge-1.16.5-2.3.23.jar` | RP cerut explicit: voce de proximitate pentru mafii/joburi, pe client **și** server. 513/513 clase coincid între JAR-ul istoric server și cel oficial, dar resursele diferă; audio/UDP/login **netestate**. Înlocuire doar cu sistem vocal compatibil testat, nu cu PlasmoVoice din alt proiect. |

## Numai **client** — încă 4 JAR-uri

| JAR | De ce rămâne acum; ce permite scoaterea/înlocuirea |
|---|---|
| `entityculling-forge-mc1.16.5-1.5.2.jar` | OPT: nu desenează entități ascunse după pereți; nu este același lucru cu view-distance. A/B FPS p5 și vizibilitatea mobilierului/vehiculelor. |
| `oculus-mc1.16.5-1.4.7.jar` | COMP vizual: rămâne pentru texturile cu probleme raportate, deși shaders sunt OFF; funcționează cu Rubidium. Test vizual/login fără el înainte de scoatere. |
| `radon-0.8.0a.jar` | OPT: iluminare client, nu înlocuiește Rubidium sau ModernFix; scoatere după test de lumină/compatibilitate/perf pe laptop slab. |
| `rubidium-mc1.16.5-0.2.13.jar` | OPT: renderer pe laptopuri vechi, asociat cu Oculus; FPS și corectitudinea texturilor se compară cu/fără, nu e promisiune de FPS universal. |

## Numai **server** — încă 9 JAR-uri

| JAR | De ce rămâne acum; ce permite scoaterea/înlocuirea |
|---|---|
| `AI-Improvements-1.16.5-0.5.0.jar` | OPT: tick AI; nu există hotspot dovedit pe lumea nouă. Poate fi scos după comparație de MSPT/CPU și spawn RP. |
| `FastSuite-1.16.4-1.1.1.jar` | OPT: procesare rețete, **nu** substituie integral FastWorkbench/FastFurnace; ultimul e deja scos din țintă. Profil de crafting înainte de a păstra/scoate. |
| `FastWorkbench-1.16.5-4.6.2.jar` | OPT: bancuri de lucru, distinct de FastSuite; candidat A/B dacă craftingul nu e hotspot. |
| `Ksyxis-1.4.6.jar` | OPT: politica spawn chunks; păstrat până se verifică împreună cu `keep-spawn-loaded=true` și se măsoară chunkuri/login pe copia nouă. |
| `Placebo-1.16.5-4.7.1.jar` | DEP posibilă pentru stackul modat; dependentul exact încă trebuie confirmat din metadata binară. Dacă nu există dependent, **se poate scoate** după boot/login. |
| `RoadRunner-mc1.16.5-1.5.2.jar` | OPT: tick/logică server; nu adăugăm Performant din HYPECITY pe deasupra. A/B MSPT/compatibilitate cu ModernFix înainte de înlocuire. |
| `connectivity-2.4-1.16.5.jar` | COMP: rețea/handshake Forge; poate fi scos numai după login stabil, aceleași moduri și test trafic/erori. |
| `getittogetherdrops-1.16.5-v1.2.jar` | OPT: unește drop-uri; fără scenariu cu iteme multe câștigul este necunoscut, deci candidat A/B și verificare loot RP. |
| `incontrol-1.16-5.2.12.jar` | AUDIT: reguli spawn posibile, dar configul încărcat nu a fost verificat. Dacă nu sunt reguli necesare pe lumea nouă, poate fi scos fără a schimba gameplay-ul dorit, după boot/spawn. |

**SCOASE deja doar din țintă, nu din server/PC/live:** client `entitycollisionfpsfix-1.16-1.0.1.jar`, `out_of_sight-1.16.4-1.0.1.jar`; server `FastFurnace-1.16.5-4.5.0.jar`, `SpawnerFix-1.16.2-1.0.0.3.jar`, `bwncr-1.16.5-3.10.16.jar`, `letmedespawn-forge-1.16-1.0.2a.jar`, `memoryleakfix-forge-pre1.17-1.1.5.jar`, `smoothchunk1.16.5-2.0.jar`, `spark-1.9.1-forge.jar` (profiler numai de laborator). Separat, ținta pluginurilor de protecție a orașului este **zero**; CoreProtect este pluginul de log dorit, neconfirmat pe live.

**De ce nu le „înlocuim” imediat:** un addon poate depinde de o bibliotecă, iar Forge înregistrează identificatori de iteme/blocuri și verifică potrivirea client/server. Înlocuirea unuia dintre modurile de conținut după ce orașul a fost construit poate invalida blocuri, iteme sau entități salvate. Profităm de startul de la zero pentru a decide conținutul înainte de construcție, dar numai după verificarea dependențelor și un import + login Forge + scenarii RP, voce, loguri și rollback pe o lume de test. **Nu există încă demonstrația că toate cele 53 de instalări (24 + 29) sunt necesare sau că packul se instalează rapid.**
