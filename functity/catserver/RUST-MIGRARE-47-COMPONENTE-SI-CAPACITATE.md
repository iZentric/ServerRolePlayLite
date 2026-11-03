# Rust pentru serverul RP: migrare funcțională, nu redenumire de JAR

**Stare la 3 noiembrie 2026:** cerința este ca lumea RP Minecraft 1.16.5, cele **34 moduri și 13 pluginuri** să funcționeze, iar numărul de jucători să fie cât mai mare. Acceptăm scrierea de pluginuri proprii **din surse pentru care avem drepturi**, nu eliminarea funcțiilor RP. Aceste 47 JAR-uri sunt *numărate*, nu inventariate complet nominal și testate pe Rust. Nu avem în acest repo lumea privată, codul celor 13 pluginuri ori două sesiuni cu jucători reali. Nimic de aici nu schimbă live-ul.

## Comparația celor trei căi

| Cale | Păstrează acum modurile/clientul/lumea? | Rust și posibil câștig | Decizie |
|---|---|---|---|
| **A. Server nou integral Rust** (de ex. [Pumpkin](https://github.com/Pumpkin-MC/Pumpkin)) | **Nu este demonstrat.** Pumpkin țintește versiunile *latest* Java/Bedrock și declară dezvoltare activă; nu există dovadă că rulează Forge 1.16.5, JAR-uri Forge/Bukkit 1.16.5 sau registrul și lumea RP. Necesită implementare/portare per funcție și test client+salvare. | Potențial mare, **câștig nemăsurat**; cost mare, inclusiv protocol, permisiuni și protecții. | **Pilot separat**, fără migrare a lumii live; continuăm numai dacă trece contractele de mai jos. |
| **B. CatServer/Forge+Bukkit + componentă Rust mică** | Păstrează ABI-ul pentru 34/13 **în principiu**, încă fără full-pack H3. | Rust numai pe hot path profilat (compresie/rețea etc.); overhead JNI, fallback Java; nu accelerează automat tickul. [Prototipul actual](../../experiments/packet-compression/README.md) nu e integrat. | Laborator după JFR cu clienți; nu promitem câștig. |
| **C. CatServer oficial/hibrid îmbunătățit în JVM** | Singura cale cu potențial de încărcare directă a JAR-urilor Forge+Bukkit existente, încă fără validarea 34/13 pe TEST. | Fără motor Rust, dar cel mai mic risc de regresie funcțională; [A/B public 5 motoare](TABEL-CINCI-MOTOARE-ACELASI-JOB-2026-11-03.md) nu a calificat Cuantic la CPU. | **Baseline de protejat** pentru RP; profilăm, reparăm și testăm înainte de orice înlocuire. |

**Alegere:** păstrăm C pentru utilizatori acum și dezvoltăm A ca *pilot Rust separat*; B numai dacă profilul dovedește un hot path potrivit. Aceasta nu declară C sau A „cel mai bun din lume”. Pumpkin este [GPL-3.0](https://github.com/Pumpkin-MC/Pumpkin), iar clientul, versiunile și plugin API-ul trebuie verificate la commitul pilotului. Nu transplantăm cod GPL în forkul CatServer LGPL ori surse private fără drepturi. `[presupus]` O implementare Rust ar putea reduce anumite costuri, dar fără 47/47 funcții și clienți reali comparația de capacitate nu este validă.

## „Convertim toate modurile”: ce înseamnă în practică

**Nu există convertor general JAR Forge/Bukkit → Rust.** Modurile sunt cod Java cu API-uri Forge/Minecraft, mixins, registru de entități/blocuri/iteme, pachete și uneori mod client obligatoriu. Pentru fiecare componentă existentă trebuie decis pe **inventarul real**, fără a declara vreuna „inutilă”:

1. **Conținut persistent RP** (de ex. vehicule, arme, mobilier, drumuri, mâncare): echivalente native pentru blocuri/iteme/entități, ID-uri/registry, recipes, AI/coliziuni, salvare NBT și pachetele pe care le așteaptă clientul Forge existent. Testăm lumea copiată înainte/după restart; blocuri și inventare fără pierderi. Dacă păstrăm clientul Forge, implementăm și demonstrăm handshake/registrul/pachetele specifice modurilor; un server vanilla Rust nu le oferă implicit. Alternativ, un **client nou cu aceleași funcții** ar fi proiect separat și necesită acordul utilizatorilor.
2. **Voce, animații și dependențe**: controlul este și pe client; voice UDP trebuie să rămână funcțional între doi clienți, inclusiv autentificare și protecția identității. Nu înlocuim doar JAR-ul server și declarăm „merge”.
3. **Moduri server-only de optimizare**: nu trebuie traduse ca JAR-uri, ci intenția lor trebuie acoperită de noul motor și măsurată fără deteriorarea comportamentului. `34` este numărul inventarului existent, **nu** 34 portări obligatoriu identice ca structură; păstrăm funcționalitatea, nu binarele Java pe Rust.
4. **Cele 13 pluginuri**: audităm sursa și licența fiecăruia. Dacă e cod propriu/licențiat, portăm funcția și contractele de eveniment Bukkit; pentru proprietare fără drepturi, scriem independent după specificație sau obținem permisiune, **nu** copiem/decompilăm. Autentificare offline anti-impersonare, permisiuni, protecții (veto Forge+Bukkit), economie, baze de date, CoreProtect/audit, comenzi și rollback sunt porți distincte. Fără lista și sursele private nu pot confirma că toate 13 sunt portabile legal.

**Protocolul de migrare:** inventar SHA-256 al copiei inactivate → matrice privată `JAR/rol/server-client/licență/dependințe/ID-uri persistente/pachete/servicii externe/teste` → un vertical slice Rust *necritic* cu client real și lume copie → câte o familie de conținut cu fixture de salvare și teste negative → 47/47 funcții verificate și 2/2 clienți Forge reali → restart, backup, restore și rollback → doar apoi benchmark comparativ. Dacă o familie esențială nu se poate porta fără pierdere, păstrăm hibridul; **nu ștergem moduri sau blocuri** ca să treacă bootul.

Instrument local nou: [`scripts/fc_rust_migration_inventory.py`](../../scripts/fc_rust_migration_inventory.py) citește **numai o copie inactivă privată** cu markerul deja cerut de [procedura de izolare](README.md), refuză symlinkuri și orice număr diferit de 34/13, calculează SHA-256 și creează un **manifest privat mode 0600 în afara repo-ului**. Toate câmpurile de portare rămân `UNVERIFIED`: instrumentul nu clasifică automat, nu publică nume, nu citește lumea și nu măsoară performanța. Exemplu **numai după confirmarea izolării copiei și a backupului**:

```sh
python3 scripts/fc_rust_migration_inventory.py \
  /cale/spre/copia-PRIVATA-inactiva \
  /cale/privata/manifest-rust-NOU.json
```

Nu urca manifestul, lumea, sursele private, logurile sau JAR-urile în repo/Actions/chat. Nu pune markerul pe live pentru a trece verificarea; rularea nu instalează sau convertește nimic.

## Câți jucători duce?

**Număr actual verificat pentru Rust cu această lume: necunoscut.** Rust nu a rulat cele 47 componente; nici pe hibrid nu există test 34/13 cu clienți reali. Cele cinci motoare au fost măsurate numai cu 0 clienți pe alt runner/scenă. Memoria 2 vCPU/12 GB este o **țintă de test**, nu limita hostului confirmată acum; există și istoric de host 3 GiB. Din aceste date nu rezultă nici 10, nici 30, nici 100 de jucători simultani.

`[presupus]` Un buget exploratoriu este `cost_tick(N) ≈ B + N·c`; **B și c sunt necunoscute** pentru lumea/packul real, iar aglomerarea, mașinile, chunkurile, GC și voice-ul pot face costul neliniar. Nu folosim această ecuație ca forecast. O cifră publică se obține numai prin [H5](GOALS.md): pe hardware verificat echivalent, **aceeași lume și funcții**, A/B/B/A cu ≥5 min încălzire + ≥20 min măsurate per braț, trepte **5→10→15→20 clienți reali** (mai sus numai după validare), login/voice/vehicule/protecții verificate, TPS ≥19,5, p95 tick ≤35 ms, p99 ≤45 ms, RSS ≤ RAM real −2048 MiB, CPU ≤75% din 2 vCPU, uplink ≤70%, GC stabil. Candidatul Rust câștigă o treaptă numai dacă trece **2/2** când hibridul eșuează **2/2** în aceleași condiții. Se oprește la primul eșec. `max-players` configurat nu este capacitate.

**Exemplu condițional, nu rezultat:** dacă 10 clienți reali trec și 15 nu, regula conservatoare H5 ar permite **cel mult 8 sloturi publicate** (80% din 10), după testul compatibilității; în acest moment **nici 10 nu sunt validați**. Instrumentul existent [`fc_funcity_capacity_verdict.py`](../../scripts/fc_funcity_capacity_verdict.py) verifică date agregate de A/B/B/A pentru hibrid pe 34/13; pentru Rust va fi necesar un evaluator separat care identifică explicit clientul/protocolul și echivalența funcțiilor. Nu îl folosim cu `java_major=11` fals ca să „validăm” Rust.
