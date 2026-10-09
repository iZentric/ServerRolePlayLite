# 🎮 CUM INTRI PE CUANTIC — 3 pași, pe orice PC

> Server Java 1.16.5 hybrid (Forge + Bukkit). Merge și pe un PC de 4 GB RAM, fără placă video.

## Pasul 1 — Ia pack-ul de client (obligatoriu)
- **Automat:** descarcă și dă dublu-click pe [INSTALEAZA-PACK.bat](https://github.com/iZentric/ServerRolePlayLite/raw/arena/a29b4ef4-serverroleplaylite/deploy/INSTALEAZA-PACK.bat)
- **Manual:** [Releases → `lite`](https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite) → `CUANTIC-Client-1.5.8.mrpack` (133 MB)

Fără pack-ul ăla **nu intri**: serverul verifică lista de moduri la handshake.

## Pasul 2 — Launcher
1. **Prism Launcher**: https://prismlauncher.org/download ( gratuit, merge și fără cont Microsoft — serverul e `online-mode=false`)
2. Prism → **Add Instance → Import** → fișierul `.mrpack`. Java 8 sau 11 e suficient pentru client.
3. Alternative care importă `.mrpack`: Modrinth App (File → Import Modpack) sau TL Legacy (tab-ul Modpacks). Nu merge cu launcher-ul vanilla fără mods.

## Pasul 3 — Intră în joc
Multiplayer → **Add Server** → Server Address:

```
92.5.171.150:25565
```

## ❗ „Failed to synchronize registry data from server, closing connection"
Înseamnă că **ai ajuns la server** (rețeaua și tunelul sunt OK) dar clientul tău are altă listă de moduri decât
serverul. Reparația e întotdeauna una singură: pornește instanța importată din `CUANTIC-Client-1.5.8.mrpack`,
nu Forge gol și nu vanilla. Dacă primești în plus `Missing or additional mod list: ...`, acolo scrie exact
modul cu versiune diferită — se rezolvă prin reimport al aceluiași `.mrpack`.

## 🥔 PC foarte slab
Video Settings: Render Distance 4 (serverul oricum trimite 4) · Graphics Fast · Smooth Lighting OFF ·
Particles Minimal · Clouds OFF · Entity Shadows OFF · Mipmap 0.

## 👑 Pe server
Orașul e în centru (protejat), survival liber în jur. Crack = numele tău e de-ajuns.
