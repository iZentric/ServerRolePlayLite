# FunCity RP Lite — pe înțelesul tuturor

> **Status: proiect public pe GitHub, încă în teste. Noul server Lite NU este pornit pentru jucători. Nu există un modpack Lite verificat pentru descărcare.**

## Ce vrem să fie

Un oraș Minecraft 1.16.5 construit de comunitate. Păstrăm conținutul RP din primul pack (mobilier, vehicule, arme, hrană, emote). Joburile, economia, rolurile și autentificarea sunt gândite prin pluginuri. LowSpec este profilul pentru PC-uri mai slabe, **nu** o garanție de FPS.

## Ce motor folosim?

**FunCity b1.0827 rămâne motorul pentru copia de test**, fiindcă a pornit cu modurile RP și pluginurile noastre. Este însă **derivat Mohist/Tenet**, nu un motor 100% independent sau fără probleme: fără corecția temporară Guava 21 a eșuat la boot. [Cinci motoare au fost testate în paralel](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39431729563) pe același conținut de 15 JAR-uri: FunCity, două CatServer și Arclight au pornit; Mist nu a ajuns la `Done`. [Tabelul motoarelor și limitele](agent/MOTOR-TABEL-VERIFICAT.md) · [pagina cu liniile Lite și istorice, separate](site/index.html#motoare). [A/B strict pe același runner](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39434450455) a comparat FunCity cu CatServer vechi: trei probe fiecare, aceeași lume generată și 40 zombie, exit zero și fără erori critice după oprire. CatServer a consumat mai puțin CPU în acest scenariu sintetic, dar [o rulare intermediară](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39431729723) a eșuat la ultimul B, iar cifrele sunt diferite de prima rundă. Oricum, nu avem MSPT sau jucător conectat; liniile de pe [site](site/index.html#motoare) nu certifică motorul final. Nu schimbăm motorul existent până nu avem client conectat, login, backup și un build corectat.

**Ținta actuală:** [FunCity RP Lite = toate cele 28 de JAR-uri enumerate acum de proprietar pentru Freeroam + numai optimizări compatibile](agent/MODPACK-TINTA-LOWSPEC.md). Dacă profilul real conține și alte JAR-uri, nu le scoatem. Cele 21 menționate mai jos sunt doar LowSpec-ul construit anterior din alt reper; nu îl numim packul final. Lista 28 încă nu are verificare SHA de pe PC.

## Ce am făcut deja

1. Am completat **același profil LowSpec** din Prism: 21 JAR-uri client; cele șase piese RP lipsă sunt puse la loc. **Nu sunt toate cele 25 JAR-uri din vechiul client**: Clumps, Radon, Out of Sight și Entity Collision FPS Fix nu sunt în LowSpec; Clumps poate conta la handshake Forge, deci nu spunem că doar optimizările au fost schimbate. Arhiva server CUANTIC avea 36 moduri; stage-ul nostru de test are 15/18, fără voce. [Comparația cu vechiul FunCity și limitele](agent/CONTROL-MODURI-ORIGINALE.md); **profilul original „Freeroam 1.0.0” indicat acum de proprietar nu fusese comparat**. Au rămas patru profiluri vizibile, iar celelalte sunt arhivate, nu șterse. [Testul de inventar](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39335419784).
2. Am pornit și oprit pe PC **o copie de server cu 15 JAR-uri** de conținut/dependențe și șase pluginuri. Serverul existent și lumea lui nu au fost modificate. [Testul serverului](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39333730944).
3. Am ales [optimizările pentru joc activ pe PC vechi și pentru server](agent/SELECTIE-PERFORMANTA-PURA.md): Rubidium, FerriteCore, ModernFix și Entity Culling sunt candidații client pentru FPS/memorie în joc; LazyDFU ajută doar pornirea, Oculus este pentru compatibilitate vizuală, **nu** mod de FPS. **Nu adăugăm Dynamic FPS** (economisește mai ales când jocul nu e activ). Pe server încercăm numai RoadRunner, FerriteCore și ModernFix într-o copie. Copia cu 18 JAR-uri a pornit/oprit, dar **nu știm încă dacă e mai rapidă**. [Testul optimizărilor](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39336314432).

## Dacă PC-ul abia poate rula Windows 10

**Nu presupune că va duce și Minecraft Forge cu 21 de JAR-uri.** Windows 10 care pornește nu este un test de FPS, iar clientul are conținut RP mare. Profilul actual poate folosi până la 2 GiB numai pentru heap-ul Java; pe un PC cu 2 GiB RAM total nu mai rămâne loc rezonabil pentru Windows, iar la 4 GiB total există risc mare de paginare. Chiar și cu mai mult RAM, placa video/driverul trebuie să suporte jocul și Rubidium. Alegem optimizări pentru joc activ, fără Dynamic FPS sau shaders, dar **nu promitem că un PC la minimul Windows 10 va putea juca**. Dacă nu pornește, primul test este clientul pe PC-ul real, nu publicarea serverului.

## De ce nu apăsăm încă „pornește public”?

**Nu am testat intrarea în joc cu LowSpec pe acest server.** Nu avem încă autentificarea prin plugin, vocea și funcțiile RP probate împreună; nici backup/restaurare testate pentru noua instalare. Nu știm dacă avem dreptul să redistribuim toate JAR-urile vechi. Pornirea publică acum ar putea expune conturi/lumea sau ar da jucătorilor un pack care nu intră.

**Următorii pași, în această ordine:** inventariem originalul Freeroam și verificăm că viitorul pack păstrează toate JAR-urile → verificăm drepturile JAR-urilor → pornim clientul și serverul complet *pe copie* și testăm conectarea → alegem/testăm loginul și RP/vocea → facem backup și test de restaurare → măsurăm dacă cele trei optimizări merită → publicăm release-ul și abia apoi deschidem serverul, cu acord pentru setările live.

## Pentru tine, acum

- **Nu descărca** vechile release-uri ca fiind noul FunCity Lite; sunt alte pachete.
- **Nu da public** adresă sau lume de server de aici: nu există încă o adresă nouă validată.
- Urmărește [PR-ul cu dezvoltarea actuală](https://github.com/iZentric/ServerRolePlayLite/pull/2) și [detaliile tehnice](agent/PROGRES.md). PR-ul este public, dar are conflicte cu `main`; noua pagină nu apare încă pe prima pagină GitHub sau pe Pages.

**Pe scurt:** codul este public; clientul și serverul au trecut verificări limitate; **lansarea pentru jucători nu este încă gata**.
