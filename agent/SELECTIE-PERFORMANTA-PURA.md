# FunCity Lite — optimizări alese pentru joc activ pe PC Windows 10 vechi

**Decizie pentru candidatul de test, 20.10.2026.** Păstrăm toate cele **11 moduri de conținut RP + 4 dependențe** pe perechea client/server. Optimizările nu înlocuiesc conținutul. Cifrele de FPS, MSPT și RAM pe laptopul vizat sunt **nemăsurate**; o alegere pe baza rolului tehnic nu este dovadă de câștig. Înainte de orice schimbare în Prism, închide Minecraft/Prism și verifică backupul. Nu schimbăm serverul existent.

## Clientul LowSpec deja instalat: 21 JAR-uri în același profil

| JAR / categorie | Decizie | Motiv / verificare necesară |
|---|---|---|
| `rubidium-mc1.16.5-0.2.13.jar` | **Păstrează pentru test în joc** | Optimizare de randare relevantă pentru FPS în timpul jocului; verifică pornirea, driverul/OpenGL al GPU-ului vechi, blocurile RP și FPS cu/fără pe aceeași scenă. Dacă GPU-ul nu îl suportă, nu inventa o compatibilitate. |
| `ferritecore-2.1.1-forge.jar` | **Păstrează pentru test** | Reduce anumite structuri de memorie; poate conta când Windows 10 și clientul concurează pentru RAM. Măsoară memorie reală și paginare, nu promite FPS. |
| `modernfix-forge-5.18.0+mc1.16.5.jar` | **Păstrează pentru test** | Fixuri/optimizări de memorie și încărcare, cu risc de interacțiune între mixinuri. Verifică pornirea și funcțiile RP. |
| `entityculling-forge-mc1.16.5-1.5.2.jar` | **Păstrează condiționat de A/B** | Nu desenează entități ascunse; relevant în oraș, dar consumă și CPU. Măsoară FPS p5/mediană cu/ fără în aceeași scenă, fără dispariția eronată a elementelor RP. |
| `lazydfu-0.1.3.jar` | **Păstrează ca optimizare de pornire/compatibilitate** | Nu ridică FPS în joc; a eliminat avertismentul ModernFix privind absența lui. Nu îl vinde drept optimizare de FPS. |
| `oculus-mc1.16.5-1.4.7.jar` | **Compatibilitate vizuală, NU mod de performanță** | Shaders rămân oprite. A fost inclus din cauza problemelor de texturi raportate cu Rubidium. Testează vizual cu/fără pe o copie înainte să-l scoți din profilul existent; nu-l număra ca FPS câștigat. |

**Nu adăugăm Dynamic FPS**: reduce consumul mai ales când fereastra nu e activă; utilizatorul cere performanță *în timpul jocului*. Nu adăugăm acum Out of Sight (ar putea ascunde mobilierul de la distanță), Entity Collision FPS Fix (beneficiu local nedemonstrat), Radon (mixinuri de iluminare cu risc de incompatibilitate) sau Clumps (schimbă registrul XP și a produs eroare la handshake fără pereche corectă). Aceste patru nu sunt conținutul RP lipsă; orice probă ulterioară se face separat, pe pereche client/server dacă schimbă registrul. Nu adăugăm moduri doar pentru că au „FPS” în nume.

**Setările inițiale LowSpec:** 5 chunkuri, shaders OFF, grafică Fast, particule minime, mipmap 0, umbre entități OFF. Limita actuală de heap este 2 GiB, nu o recomandare universală: dacă PC-ul are foarte puțină memorie, verifică RAM-ul disponibil și paginarea înainte de a crește heapul. Testul trebuie făcut pe GPU-ul și driverul Windows 10 reale, cu aceeași rezoluție/scenă și clientul conectat; fișierele din Prism nu măsoară FPS.

## Server: strict trei optimizări cu efect larg de probat

| JAR | Decizie | Condiție de păstrare |
|---|---|---|
| `RoadRunner-mc1.16.5-1.5.2.jar` | **Trial tick/logică**, nu producție | Compatibilitate moduri/pluginuri, MSPT p95 și CPU cu/fără mod pe copie, aceeași lume și sarcină; fără Performant suprapus. |
| `ferritecore-2.1.1-forge.jar` | **Trial memorie**, nu producție | RSS/GC stabil mai bun fără regresie în gameplay; beneficiul pe client nu dovedește beneficiul pe server. |
| `modernfix-forge-5.18.0+mc1.16.5.jar` | **Trial memorie/fixuri**, nu producție | Compatibilitate mixinuri + comparație reală de memorie/boot; nu îl păstra pentru un câștig sub zgomot. |

Serverul de bază cu **15 JAR-uri** a pornit/oprit pe PC; trialul cu **18 JAR-uri** și aceleași șase pluginuri a pornit/oprit tot pe PC. Asta arată **numai** că bootul nu s-a blocat: [bază](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39333730944), [trial](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39336314432). Nu includem preventiv FastSuite/FastWorkbench/Placebo, Ksyxis, AI Improvements, moduri de drops/rețea sau alte optimizări înguste fără un hotspot demonstrat; nu combinăm Performant cu RoadRunner.

## Când putem spune că merită și că putem da drumul?

1. **Client:** pornește LowSpec pe PC-ul vechi real, verifică driverul, conectează-l la un server complet *de test*, confirmă blocuri, vehicule, emote și inventar. Măsoară FPS p5/mediană și utilizarea RAM pe aceleași trasee/situații aglomerate, repetat. Dacă Rubidium sau Oculus strică vizualul, probează individual cu backup înainte de schimbarea profilului.
2. **Server:** pe o copie a aceleiași lumi, teste A/B repetate la sarcină reprezentativă, o schimbare odată; urmărește MSPT p95, TPS, CPU, RSS/GC, erori, login și RP. Fără avantaj stabil și important peste variația normală, optimizerul nu intră în serverul final.
3. **Public:** verifică drepturile/SHA tuturor JAR-urilor, autentificarea prin plugin, vocea și backup/restaurarea; după un release și o conectare reală reușite, obține acordul pentru setările live. Nu publicăm adresa sau lumea înainte de aceste probe.

**Rezultat de acum:** lista scurtă este decisă pentru *test*, nu instalată pe serverul existent; nu există FPS sau MSPT care să demonstreze „cel mai rapid”.
