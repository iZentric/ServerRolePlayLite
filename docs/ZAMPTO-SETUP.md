# 🚀 Instalare server Freeroam Lite pe Zampto (gratuit)

Ghid pas cu pas pentru contul tău Zampto (dash.zampto.net).
Serverul = **Minecraft 1.16.5 + Forge 36.2.42**, are nevoie de **Java 8 sau 11**.

## Pasul 1 — Creează serverul
1. Intră pe [dash.zampto.net/create](https://dash.zampto.net/create)
2. Alege **Minecraft Java**
3. La tip/versiune: caută **Forge** și alege **1.16.5** (dacă îți cere build exact: `36.2.42`)
4. Locație: **Germania** (ping mai bun din România decât Italia)
5. Resurse: pune maxim ce-ți dă free tier-ul (RAM cât mai mult — ideal 6-8 GB;
   modpack-ul merge și cu 4 GB)
6. Creează serverul și intră în panoul lui (butonul de management)

## Pasul 2 — Urcă pack-ul de server
1. Descarcă **`Freeroam-Lite-Server-1.0.0-lite.zip`** de aici:
   👉 https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite
2. În panoul serverului: tab-ul **Files**
3. **Oprește serverul** dacă rulează
4. Șterge folderul `mods` existent (dacă e vreunul) ca să nu se amestece
5. Apasă **Upload** și urcă ZIP-ul (sau prin SFTP dacă e prea mare pentru upload web —
   ai parola SFTP în Settings → SFTP)
6. Click-dreapta pe ZIP în file manager → **Unarchive/Extract**
7. Verifică să existe: `mods/` (cu ~20 jar-uri), `server.properties`, `eula.txt`

## Pasul 3 — Configurează pornirea
1. Tab-ul **Startup** (sau Settings):
   - Dacă hostul a instalat deja Forge 1.16.5 → nu schimbi nimic
   - Dacă îți cere JAR-ul manual: rulează o dată în consolă/`install-forge.sh`,
     apoi setează JAR-ul: `forge-1.16.5-36.2.42.jar`
2. **Java version**: alege **Java 11** (sau Java 8). ⚠️ NU Java 17+ — 1.16.5 nu merge!
3. Pornește serverul. Prima pornire durează 2-5 minute (generează lumea).

## Pasul 4 — Conectează-te
- IP-ul serverului e afișat în panou (ex. `xxx.zampto.net:25565`)
- Dă IP-ul prietenilor + pack-ul de client:
  **`Freeroam-Lite-Client-1.0.0-lite.mrpack`** (același link de Releases)
- Clientul se instalează cu [Modrinth App](https://modrinth.app/) sau
  [Prism Launcher](https://prismlauncher.org/): drag & drop fișierul `.mrpack`

## ⚠️ Important la Zampto Free Tier
- Trebuie să **reînnoiești** resursele periodic: Settings → **Manage Free Tier**
  ([dash.zampto.net/freetier/resources](https://dash.zampto.net/freetier/resources)) —
  altfel serverul se oprește!
- Nu e garantat 24/7 — dacă s-a oprit, îl repornești din panou.
- Fă **backup** la folderul `world/` din când în când (download din Files).

## 🤖 Deploy automat (opțional, fără chei SSH!)

Zampto folosește SFTP cu **user + parolă** (nu chei SSH). Dacă vrei ca fișierele să se
urce automat pe server la cerere:

1. În panoul Zampto al serverului, găsește datele SFTP (de obicei în tab-ul
   **Settings** al serverului): adresa (ex. `xxx.zampto.net`), portul (de obicei
   `2022`) și userul (ex. `evo1.abc123`). Parola o setezi tu la
   [Settings → SFTP](https://dash.zampto.net/settings/sftp).
2. În GitHub: repo-ul tău → **Settings → Secrets and variables → Actions →
   New repository secret** și adaugă pe rând:
   - `ZAMPTO_SFTP_HOST` = adresa serverului SFTP
   - `ZAMPTO_SFTP_USER` = userul SFTP
   - `ZAMPTO_SFTP_PASS` = parola SFTP
   - `ZAMPTO_SFTP_PORT` = portul (doar dacă NU e 2022)
3. **Oprește serverul** din panou (să nu scrii fișiere peste el cât rulează).
4. În GitHub: tab-ul **Actions → Deploy pe Zampto (SFTP) → Run workflow**.
5. Când termină, pornește serverul din panou.

> Parola rămâne doar în seiful GitHub Secrets — n-o vede nimeni, nici în loguri.

## 🔐 Securitate
- Nu da nimănui parola, cheia API sau parola SFTP (nici în chat-uri!).
- Activează **2FA TOTP** din Settings — durează 2 minute și îți protejează serverul.
