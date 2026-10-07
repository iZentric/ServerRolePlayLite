# 🖥️ Hosting GRATUIT pentru serverul Freeroam Lite

Analiză făcută pe baza listei [FMHL (myuui.com)](https://myuui.com/) + verificări proprii.
Pentru un server **modat** (Freeroam/RP) ai nevoie minim de: **4 GB RAM, 2 core-uri, 5+ GB stocare**.
Din România, ping-ul cel mai bun îl ai pe locații din **Germania, Polonia, Italia, Finlanda, Franța**.

## 🏆 Recomandările mele (în ordine)

| # | Host | RAM | CPU | Stocare | Locație | 24/7 | Rating | Link |
|---|------|-----|-----|---------|---------|------|--------|------|
| 🥇 | **Eternal Zero** | **6 GB** | 3 core (Xeon W-2295) | 20 GB | Finlanda / Canada | ✅ DA | 4.6★ | [eternalzero.cloud](https://eternalzero.cloud/) |
| 🥈 | **Zampto** | **8 GB** | 2.5 core (E5-2680v4) | 10 GB | **Germania** / Italia | ❌ | 4.5★ | [zampto.net](https://zampto.net/) |
| 🥉 | **FreemcHosting** | 4 GB | 2 core (E5-2650v2) | **25 GB** | **Germania** | ✅ DA | 4.3★ | [freemchosting.com](https://client.freemchosting.com/) |
| 4 | **MineStrator** | 4 GB | 2 core (Xeon Gold 6230R) | 8 GB | Franța | ✅ DA | 4.8★ | [minestrator.com](https://minestrator.com/en/order/myboxfree) |
| 5 | **AxentHost** | 2+ GB | 2 core (Ryzen 9 3900) | 5+ GB | **Germania** / SUA | ✅ DA | 4.4★ | [axenthost.com](https://axenthost.com/) |
| 6 | **HidenCloud** | 3 GB | 2 core (Ryzen 9 7950X3D) | 15 GB | Franța + multe | ✅ DA | 4.4★ | [hidencloud.com](https://www.hidencloud.com/service/free-server) |

### De ce Eternal Zero pe locul 1
- cea mai multă RAM gratuită cu 24/7 real (6 GB — suficient pentru pack modat + 10-15 jucători)
- 3 core-uri = cel mai mult CPU din listă (TPS-ul serverului depinde de CPU, nu doar de RAM!)
- 20 GB stocare = încape pack-ul + harta fără probleme
- Finlanda = ping decent din RO (~45-60ms)

### De ce Zampto pe locul 2
- 8 GB RAM (cea mai multă!) și servere în **Germania** (ping ~30-40ms din RO)
- minus: nu garantează 24/7 (serverul se poate opri când nu joacă nimeni și trebuie repornit din panou)

### Alternative de rezervă
| Host | Specificații | Observații |
|------|--------------|------------|
| MCServerHost | 4 GB, Ryzen 9 7950X3D | doar SUA/UK/Singapore → ping slab din RO |
| FreeGameHost | 4 GB, 2 core | Franța OK |
| OuiHeberg | 8 GB RAM dar **doar 2 GB stocare** | nu încape un modpack! |
| Tick Hosting | 8 GB dar **1 singur core** | TPS slab la modpack |
| Aternos | 2.2 GB, coadă de așteptare | doar ca ultimă variantă; pornire lentă, dar suportă direct mrpack |

## ⚠️ Sfaturi pentru hosturi gratuite
1. **Nu stoca nimic important doar pe host** — fă backup regulat la lume (download folder `world/`).
2. Majoritatea îți opresc serverul dacă e gol — folosește panoul lor de "auto-restart" sau un bot de ping.
3. Încarcă varianta **server-lite** a pack-ului (fără moduri client-only) — pornește de 2x mai repede și consumă cu ~30% mai puțină RAM.
4. Dacă hostul are opțiune de versiune Java, alege **Java 17** (pentru MC 1.18–1.20.4) sau **Java 21** (pentru 1.20.5+).

## 🏠 Varianta "pe PC-ul tău" (bonus)
Dacă vrei să-l ții pornit doar când joci, de pe propriul PC, fără port forwarding:
1. Instalează [playit.gg](https://playit.gg/) (tunel gratuit) → primești o adresă publică gen `xyz.playit.gg`.
2. Pornește serverul local cu scriptul din acest repo.
3. Prietenii se conectează la adresa playit.gg.
