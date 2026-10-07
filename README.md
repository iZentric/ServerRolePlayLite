# 🏙️ ServerRolePlay **Lite**

Varianta **optimizată** a modpack-ului **Freeroam 1.0.0 „PL2 Gambo"** (Palma City) —
aceleași moduri, dar merge pe **orice PC** (client) și pe **hosting gratuit** (server).

> Minecraft **1.16.5** · Forge **36.2.42** · 28 moduri originale + optimizări

## ⬇️ Download (gata făcute)

👉 **[Releases → lite](https://github.com/iZentric/ServerRolePlayLite/releases/tag/lite)**

| Fișier | Pentru cine | Ce e |
|---|---|---|
| `Freeroam-Lite-Client-*.mrpack` | 🎮 jucători | TOATE modurile originale + moduri de FPS + setări lite. Se instalează cu [Modrinth App](https://modrinth.app/) sau [Prism Launcher](https://prismlauncher.org/) (drag & drop) |
| `Freeroam-Lite-Server-*.zip` | 🖥️ server | modurile de server (fără cele client-only care doar îl încetinesc) + Forge + scripturi de pornire + configurări optimizate |

## 📖 Ghiduri

| Document | Ce conține |
|---|---|
| [`docs/ZAMPTO-SETUP.md`](docs/ZAMPTO-SETUP.md) | 🚀 Instalare pas-cu-pas pe Zampto (hostul tău) |
| [`docs/HOSTING.md`](docs/HOSTING.md) | 🏆 Comparație hosturi gratuite + alternative |
| [`analysis/REPORT.md`](analysis/REPORT.md) | 📋 Raportul build-ului: ce s-a păstrat/adăugat exact |

## 🔧 Cum funcționează

- `pack-rules.json` — regulile de optimizare (editabile)
- `scripts/build_lite.py` — construiește pachetele lite din pack-ul original
- `.github/workflows/build-lite.yml` — GitHub Actions rulează build-ul automat la
  orice modificare a regulilor și publică rezultatele la Releases

Vrei să schimbi ceva (alt view-distance, alt mod adăugat)? Editează `pack-rules.json`
sau fișierele din `scripts/` și build-ul se reface automat.

## ⚡ Optimizările aplicate

**Client** (toate modurile originale rămân!):
- adăugate: EntityCulling + alte moduri de FPS disponibile pt 1.16.5 Forge
- `options.txt` lite: render 8 chunks, graphics fast, fără nori/umbre, VSync off

**Server**:
- scoase DOAR modurile client-only (Rubidium, Oculus, Dynamic Surroundings etc. —
  pe server nu fac nimic, doar măresc pornirea și RAM-ul)
- flaguri JVM Aikar (G1GC) pentru TPS stabil la RAM mică
- `server.properties` reglat: view-distance 7, compresie rețea, fără watchdog kill
