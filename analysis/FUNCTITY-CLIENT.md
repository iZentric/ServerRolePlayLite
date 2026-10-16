# FunCity — pachetul de client și prima conectare

Stare: **gata de testat imediat ce staging-ul e VIU** (raportul live e în `analysis/FUNCTITY-STAGE.md`).
Nivel de încredere: lista de componente = **măsurată** (audit ZIP vs staging); pașii de mai jos = **verificați logic, dar încă nefăcuți cu un client real** — asta se validează prin testul tău.

## 1. Ce iei

- **Descarcă release-ul `lite`** din acest repo:
  `https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite`
  arhiva `CUANTIC-Server-CatServer-1.7.7.zip`, SHA-256 `fe1e2610…8a8a15` (verificare: `certutil -hashfile fisier.zip SHA256` în cmd).
- Din arhă ai nevoie **doar de folderul `mods/`** (36 fișiere). Folderul `plugins/` NU se pune la client — alea sunt doar pentru server.
- Setul de 36 e identic cu ce rulează pe server (validat la staging: aceleași nume de jar, `voicechat-forge-1.16.5-2.3.23.jar`, `cgm-1.2.6`, `vehicle-mod-0.45.2`, `modernlife`, `cfm`, `supplementaries` etc.).

> De ce copie completă și nu selecție „client-only": în mixul ăsta (Forge+hivern) niciun mod server-side nu strică la client, iar lipsa unuia client-side sparge handshake-ul. Selecția fină o facem după ce intri cu succes.

## 2. Launcher

Recomandat: **Prism Launcher** (gratuit, open-source; Windows). Alternative: MultimMC.

1. Prism → **Add Instance** → versiune **Forge 1.16.5** — instalează loader **36.2.34** (recomandat oficial; îl oferă Prism la tab-ul Version).
2. Click dreapta pe instanță → **Folderul instanței** → pune conținutul lui `mods/` din arhivă acolo.
3. **Settings → Java**: Java **11** (nu 17/21!). Prism descarcă singur Java 11 (temurin) la Run→Java dacă nu ai. Argumente: `-Xmx4G` pe PC de 8-16 GB RAM; `-Xmx3G` sub 8 GB. (Nu lăsa sub 2G — 36 moduri + animații.)
4. **Settings → Game Settings → fullscreen/off**, la discreție.

## 3. Conectare

- Adresa staging (cât rulează testul): **`92.5.171.150:25566`**
- Adresa producție (când FunCity va înlocui CUANTIC): **`92.5.171.150:25565`**
- Offline-mode pe staging: intri cu orice nume; pe producție e whitelist-ul existent — numărul tău e deja acolo.
- Voice chat: tasta **V** (hold) în joc — e același mod pe client+server, nu trebuie configurat nimic.

## 4. Testul scurt cerut (3 minute, răspunde-mi Da/Nu pe fiecare linie)

1. **Intrare** — te conectezi, vezi spawn-ul orașului, 0 crash la ecran.
2. **Deplasare** — mergei/aleargi/sari; FPS vizibil acceptabil (`F3` — zi-mi ce arată la `fps:`).
3. **Inventar** — deschizi E, iei/aranjezi un item; check ca items din `cfm`/`pamhc2foodcore` se văd (mobile & mâncare).
4. **Vehicul** — spawnează/urcă într-o mașină (`vehicle-mod` / `roadstuff`) și mergi 20 secunde.
5. **Reconectare** — ieși din joc și intri la loc în 1 minut.
6. **Persistență** — după reconectare, itemele luate la pasul 3 încă sunt ale tale / unde le-ai lăsat.

Dacă 1-6 trec: staging validat cu client real → pot muta candidatul pe 25565 (producție) cu acordul tău și rollback gata.

## 5. Ce NU e încă demonstrat (label, ca să nu vindem aer)

- Timpii de join sub mulți jucători, load worldgen — netestat (staging = 2 fire CPU).
- Performanța „hibrizilor alternativi" — CatServer/Arclight rămân doar benchmark de referință, nu opțiune instalată.
- Selecția client-only/server-only a modurilor — amânată intenționat (vezi §1).
