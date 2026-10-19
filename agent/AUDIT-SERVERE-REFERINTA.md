# Servere de referință: ce am putut verifica din captura veche (19.10.2026)

**Răspuns direct: NU am verificat fiecare server și fiecare configurație din `E:\Administrator\Desktop\FunCity\servere referinta`.** Nu am acces la unitatea E în acest sandbox. Am auditat doar captura istorică din repo, colectată la 18.10.2026. Nu o confund cu serverul live și nu folosesc fișierele de jucători drept feedback.

## Proveniență și acoperire

- `diag/oldcfg-report.txt` păstrează **424 intrări cu căi** din 15.077 fișiere selectate, apoi se oprește la limita de raport. Dintre cele 424, **12** sunt `cuantic` (în afara `servere referinta`), **412** sunt HYPECITY BK; dintre ultimele, **379** sunt `plugins/AutoPickup/PlayerData/*.yml` (date de jucători, nu configurație de funcționalități) și doar **33** sunt alte fișiere. Căile din raport nu atestă completitudinea acestor proiecte.
- Am reconstituit **numai în memorie** ZIP-ul din toate cele 35 `diag/oc_part*.txt`, verificând CRC pentru fiecare intrare: **9.032.359 B**, **15.077 intrări** / **25.401.054 B necomprimați**, dintre care 14.535 `.yml`, 293 `.properties`, 143 `.toml`, 101 `.conf` și 5 `.cfg`. Arhiva conține **7.512 nume distincte** și **7.565 coliziuni de nume**: scriptul istoric a arhivat căile absolute ca basenames, astfel `config.yml`, `server.properties`, `Jobs.yml` etc. nu pot fi legate sigur de serverul de origine. Nu am extras-o pe disc și nu public conținutul fișierelor private.
- În ZIP apar numai aceste cinci extensii, iar cea mai mare intrare are 288.948 B; o versiune istorică a `.github/workflows/pc-oldcfg.yml` aplica filtre, dar **nu am identificat cu certitudine revizia exactă care a produs această captură**. Prin urmare nu este un inventar complet al configurațiilor de pe disc, nici al pluginurilor încărcate, JAR-urilor sau lumilor. Nu apare niciun `.log` **în captură**; asta nu înseamnă că pe PC nu există loguri. Nici feedback verificabil al jucătorilor nu există în materialul disponibil.

| Proiect din primul extras de directoare | Configurații cu **cale păstrată** disponibile | Ce putem spune |
|---|---:|---|
| `cuantic` (nu e în `servere referinta`) | 12 | Setări server vizibile; nu presupunem că sunt toate. |
| `servere referinta/HYPECITY BK vechi nostalgic pentru cei de pe mooncraft` | 412, din care 379 profiluri AutoPickup | 33 fișiere non-profil vizibile înaintea trunchierii; restul nu poate fi atribuit cu certitudine. |
| `servere referinta/hypecity` | 0 | Folderul apare în extras, nu și conținutul lui identificabil. |
| `servere referinta/minecity` | 0 | Doar numele folderului; nu putem valida funcții/configurații. |
| `servere referinta/nmc` | 0 | Doar numele folderului. |
| `servere referinta/viberp` | 0 | Doar numele folderului. |
| `FunCity server` (în afara referințelor) | 0 | Numele apare în index; nu dovedim starea lui curentă. |

Lista folderelor provine din **primele 40 directoare** ale raportului, nu dintr-un inventar exhaustiv. Cele 15.077 fișiere fără căi în ZIP nu trebuie distribuite artificial între aceste proiecte. Șase intrări poartă doar basename-ul `server.properties`; **nu** sunt dovada a șase servere distincte.

## Ce se poate învăța fără a copia orbește

- În cele **12** configurații CUANTIC cu căi, `server.properties` arată view-distance 4, broadcast 60%, compresie 512, iar `bukkit.yml` are limite spawn 20/6/2. `spigot.yml` arată `nerf-spawner-mobs=true` și despawn 2400; NU le transferăm în FunCity: afectează gameplay-ul. FunCity țintă păstrează view 5, spawn 20/6/2, keep-spawn și compresie 256 deja aleasă în repo.
- În HYPECITY BK, `bukkit.yml` arată spawn 8/5/1, iar `config/PlasmoVoice/server.yml` descrie voce de proximitate (distanțe 8/16/24 și vorbit permis). Este **Plasmo Voice, nu Simple Voice Chat**: dovedește intenția unei funcții RP în acel proiect istoric, nu compatibilitatea/modul/portul FunCity actual. `mohist-config/mohist.yml`, `plugins/AuthMe/*` și `AutoPickup` indică o combinație Forge/pluginuri/login, dar prezența configurației nu dovedește funcționarea sau siguranța ei.
- Arhiva fără căi conține `Jobs.yml` de trei ori, `aJobs.yml` de două ori, `zonamafie.yml` de două ori și `politie.yml` de trei ori. Structura `Jobs.yml`/`aJobs.yml` este de **meniuri** (`open_command`, `items`, click commands), nu dovadă că o economie/job a rulat sau că acestea aparțin unui server anume. Există și intrări `regions.yml` care menționează zone de fermier; fără cale și hartă/world snapshot nu validăm protecția sau economia.

## Cum folosim reperele ca să construim RP fără să rupem serverul

| Funcția țintă | Probă din istoric | Verificare necesară pe o copie FunCity izolată |
|---|---|---|
| Acces/identitate/permisiuni | HYPECITY BK are fișiere Mohist și AuthMe, dar fără probă de funcționare. | Login Forge cu modurile și pluginurile alese, permisiuni minime, fără copiere de conturi sau configurații de autentificare. |
| Voce pentru mafii și joburi | PlasmoVoice era configurat în HYPECITY BK; pentru FunCity alegerea separată este Simple Voice Chat client/server. | Conectare între versiuni, configurare UDP reală și probă audio de proximitate între doi clienți; clasele JAR identice din CI nu țin loc de test. |
| Joburi și economie | Meniuri `Jobs.yml`/`aJobs.yml` în ZIP fără server identificabil. | Un meniu deschide comanda potrivită; drepturile, angajarea și o recompensă reală se verifică separat, fără a inventa un plugin sau venituri din meniuri. |
| Mafii/poliție/teritorii | `zonamafie.yml`, `politie.yml` și regiuni istorice fără cale în ZIP. | Pentru orașul FunCity nou nu copiem protecțiile; verificăm construcție liberă, meniuri/comenzi și log CoreProtect + rollback admin după o modificare controlată. |
| Conținut și laptopuri vechi | Configuri istorice și dorința proprietarului de RP; fără FPS măsurat. | Arme, vehicule, mobilier și texturi funcționale pe client; compare numai o setare de randare/rețea sau un mod la un moment dat, fără a sacrifica vizibilitatea RP. |

Păstrăm deciziile din `agent/DECIZII.md`, nu copiem orbește configurațiile vechi. Backup/rollback al lumii și datelor pluginurilor **înainte** de orice test sau schimbare live; nu importăm conturi, parole, UUID-uri, locații, baze de date, setări de securitate sau comenzi din proiecte istorice. Nu atribuim opinii jucătorilor fără sursă. Tabelul este o **poartă de validare**, nu dovada că probele au trecut.

**Următorul prag:** numai o captură autorizată read-only care păstrează căile relative, cu redactarea datelor private, ar permite verificarea *fiecărui proiect și a fiecărei configurații*; dispatch-ul runnerului PC a dat 403 și nu îl repetăm. Până atunci starea corectă este „audit parțial al referințelor istorice”, nu „toate serverele verificate”, „beta funcțională” sau „live”.
