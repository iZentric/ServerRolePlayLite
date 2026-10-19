# FunCity Lite — ce dovedesc proiectele vechi din folderul PC

**Proveniență:** workflow-ul istoric `.github/workflows/pc-oldcfg.yml` la `24fbf33` avea explicit rădăcina `E:\Administrator\Desktop\FunCity` și a salvat `diag/oldcfg-report.txt` (`diag/oldcfg-done.txt`: 18.10.2026, 07:35:54). Raportul numără 15.077 fișiere de configurație în proiecte precum `cuantic`, `servere referinta\hypecity`, HYPECITY BK și `modpack uri`, dar este **trunchiat după 424**. Este o captură istorică din PC, nu o citire actuală a unității E și nu un test FPS. Nu copiem sau publicăm configurații cu date de utilizator din arhiva brută.

| Repere verificabile | CUANTIC (`diag/oldcfg-report.txt`, secțiuni `cuantic`) | FunCity în **repo**, nu neapărat live |
|---|---|---|
| Distanță server | `view-distance=4` | `view-distance=5` |
| Transmisie entități | `entity-broadcast-range-percentage=60` | `80` |
| Compresie rețea | `network-compression-threshold=512` | `-1` |
| Limită declarată | `max-players=25` | `64` (nu este capacitate măsurată) |
| Spawn | 20 monștri / 6 animale / 2 acvatice | aceleași limite în `bukkit.yml`; keep-spawn-loaded=true în repo |
| Gameplay spawner/loot | `nerf-spawner-mobs=true`, despawn item 2400 | `false`, despawn 6000: **nu** copiem vechea setare dacă strică survival/RP |

Alte urme reale: arhiva HYPECITY BK include o configurație FerriteCore și una Performant (`diag/oldcfg-report.txt`), deci folosea și moduri, nu era „fără moduri”. `diag/pc-lowend.txt` raportează la un moment dat două profiluri Prism cu opțiuni low-spec și heap plafonat la 2 GB; `diag/pc-client.txt` inventariază mai târziu 25 de JAR-uri FunCity. Aceste rapoarte **nu** conțin o măsurătoare comparabilă de FPS pe laptopurile vechi și nu justifică instalarea Dynamic FPS ori combinarea Performant cu RoadRunner în FunCity.

**Decizie practică:** credem observația proprietarului că proiectele vechi au fost accesibile pe PC-uri slabe; le folosim ca baseline de *metodă*: profil grafic conservator, puține date trimise și dependențe curate, cu RP păstrat. Candidaturile pentru A/B individual: view 5→4 și/sau broadcast 80→60, respectiv compresie -1→512, fiecare separat pe copie, cu login Forge, vizibilitate vehicule/mobilier, rețea, CPU server, FPS/RAM client și revenire. Nu aplicăm din reflex limitările de gameplay (`nerf-spawner-mobs`, despawn) și nu pretindem că setările serverului transformă orice GPU vechi într-unul rapid. Dacă diferența este sub zgomot ori se pierd funcții RP, păstrăm baza FunCity.

**Accesul nou la PC:** încercarea de dispatch manual a unui inventar read-only de maximum 5 minute a fost refuzată de GitHub `403 Resource not accessible by integration`; lista de administrare a runnerelor are același 403. Nu a pornit niciun job; workflow-ul temporar a fost retras și înlocuit cu stubul manual read-only. Nu sunt probe actuale de pe `E:` sau FPS nou.
