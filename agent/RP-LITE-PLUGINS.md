# FunCity RP Lite — oraș nou, construit liber, numai loguri

**Corecție de produs de la proprietar, 19.10.2026:** orașul se construiește **de la zero** de către proprietar și jucători; nu cerem claims, regiuni protejate, interdicții de construit sau anti-grief preventiv în oraș. Păstrăm **CoreProtect ca jurnal** și rollback punctual numai de către admin. Nici logarea, nici drepturile de admin nu opresc automat un incident. Aceasta este o alegere pentru ținta nouă, **NU o schimbare a serverului live ori o autorizație de ștergere a unei lumi existente**.

| Rol în orașul nou | Plugin țintă | Decizie |
|---|---|---|
| Autentificarea contului jucătorului | **un plugin de autentificare, încă neales/nepinuit** | CERUT de proprietar; nu presupunem că există în packul CUANTIC ori live. Configurile AuthMe din HYPECITY BK sunt numai referință, fără transferul conturilor/parolelor. |
| Comenzi uzuale, economie de bază și spawn | EssentialsX + EssentialsXSpawn | PĂSTRATE; spawn e punct de revenire, nu teren protejat. |
| Chat text RP | EssentialsXChat | PĂSTRAT; vocea Simple Voice Chat e separată. |
| Ranguri/permisiuni de admin, moderator și job | LuckPerms | PĂSTRAT, **fără a folosi rangurile ca blocaj implicit pentru construcția jucătorilor**. |
| API de economie / protocol | Vault; ProtocolLib numai cât timp există dependenți efectivi | PĂSTRATE provizoriu, până la auditul JAR-urilor și testul funcțiilor, fără a confunda API cu job/economie completă. |
| Skinuri RP | SkinsRestorer | PĂSTRAT provizoriu pentru aspect; nu este pluginul de autentificare și nu rezolvă singur `online-mode=false`. |
| Jurnal și investigație | CoreProtect | **UNICUL** sistem de log/rollback cerut; lipsește dintre cele 14 pluginuri ale arhivei istorice. Îl verificăm în ținta efectivă, inclusiv la blocuri modate, containere și eventual vehicule. |
| Protecții și claims | niciun plugin | **SCOASE din țintă**: EssentialsXAntiBuild, EssentialsXProtect, WorldGuard, ClaimChunk. `spawn-protection=0` există deja în `functity-config/server.properties`, dar valoarea live nu este dovedită. |
| Editare administrativă în masă | WorldEdit | SCOS din runtime normal; numai unealtă separată, dacă proprietarul are o nevoie concretă. Nu este necesar pentru a le permite jucătorilor să construiască. |
| Unelte și identitate veche | Chunky; Cuantic-Brand | Chunky numai în laborator pentru pregen autorizat; brandingul vechi SCOS. |

**Numărul nu este verdict de performanță:** din 14 pluginuri istorice CUANTIC, ținta normală păstrează provizoriu 7 nume (EssentialsX, EssentialsXChat, EssentialsXSpawn, LuckPerms, ProtocolLib, SkinsRestorer, Vault), iar CoreProtect și **pluginul de autentificare încă neales** sunt cerințe suplimentare de verificat, nu JAR-uri prezente în acel ZIP. Nu presupunem că pluginurile de joburi, economie ori autentificare văzute în referințe sunt instalate pe FunCity. `scripts/fc_plugin_audit.py` verifică numai metadata `plugin.yml` a celor 14 JAR-uri istorice; **nu poate verifica configul activ, permisiunile sau logarea**. Auditul hosted read-only rămâne de rulat după push.

## Lecția referințelor, adaptată la orașul vostru

`Jobs.yml`/`aJobs.yml` și `zonamafie.yml` din captura istorică sunt indicii despre **meniuri**; căile arhivate s-au pierdut. Aici un job are nevoie de providerul real al comenzii/recompensei; o zonă mafie/poliție poate fi convenție RP și meniu fără WorldGuard. Putem evalua AuthMe ca exemplu din HYPECITY BK, dar nu copiem configurațiile sensibile, conturile, parolele, protecțiile ori regiunile din serverele vechi. Prima probă a jucătorului este conectare Forge + autentificare prin plugin; numai după autentificare îi testăm construcția liberă. Testăm un jucător obișnuit care pune/sparge blocuri la spawn și în oraș, folosește mobilierul și vehiculele, apoi consultăm logul CoreProtect, atribuirea și un rollback/restaurare pe **copie**. Dacă un bloc/vehicul modat nu e logat, declarăm acea limită înainte de beta; nu pretindem că orașul este protejat prin loguri.

## Descărcare cu net slab: noul oraș schimbă ordinea auditului

Auditul hosted [39266263549](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39266263549) a măsurat pentru **vechiul candidat** 24-moduri un ZIP de **135.771.416 B** și **32.537.149 B** downloaduri remote declarate; nu este timp de instalare măsurat. `Pizzaland_v68.jar` (~83 MB comprimați) și `Modernxl 1.16.5.jar` (~35,4 MB comprimați) domină ZIP-ul. Dacă **lumea de beta este creată înainte de a fi folosit vreun mod**, nu există construcții vechi de migrat din acel oraș; de aceea Pizzaland (registru/rol încă necunoscut) devine **prima verificare binară și de dependențe** pentru un candidat *separat* fără el pe client și server. ModernXL, CFM și ModernLife pot avea blocuri diferite chiar dacă toate oferă mobilier; nu le numim duplicate fără inventar de conținut și alegerea mobilierului RP. Nu ștergem JAR-uri din packul instalat, lumea activă sau release pe baza numelui sau a mărimii.

**Poarta minimă înainte de beta/publicare:** audit de SHA, proveniență/licență și dependențe pentru JAR-urile scoase; un `.mrpack` unic importat curat și reinstalat; conectare Forge client/server **și** autentificare prin plugin (cont nou, reconectare, restricții înainte de auth, fără ocolire), apoi audio/UDP; construcție liberă de către jucător fără protecții preventive; jurnal CoreProtect pentru blocuri modate și rollback administrativ; joburi/mafii și economie efectivă; backup și restaurare probată pe lume nouă. Testele de parser și selecția de repo NU sunt aceste probe.
