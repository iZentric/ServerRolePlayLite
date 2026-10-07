# 🫀 ANATOMIA COMPLETĂ A SERVERULUI — tot ce mișcă, fiecare piesă, cu ce se poate înlocui

> Harta cerută de șef: fiecare componentă, tehnologia ei actuală, configurile, și alternativele existente pe planetă.
> Stare: v1.5.0-ULTRA. Actualizată: 2026-10-08.

---

## ETAJUL 0 — GAZDA (fierul)

| Piesa | Acum | Alternative existente | Verdict |
|---|---|---|---|
| Host | **Zampto free** (8 GB, server "Evor", id 17192) | MineStrator, EternalZero, MCServerHost, HidenCloud, FreemcHosting (toate testate în docs/HOSTING.md) | Zampto = cel mai bun gratis |
| Panou | Pterodactyl (dash.zampto.net) | — (dat de host) | fix |
| Acces automat | SFTP node12.zampto.net:2022 (robot GitHub) | API-ul lor (mort — verificat) | SFTP e singura cale |

## ETAJUL 1 — MAȘINA VIRTUALĂ JAVA

| Piesa | Acum | Alternative | Verdict |
|---|---|---|---|
| JVM | Java 11 (imaginea Zampto) | OpenJ9 (−30-40% RAM), GraalVM | ❌ blocate — Zampto nu lasă JVM custom |
| Garbage Collector | **G1GC cu flagurile Aikar + StringDeduplication** | ZGC (experimental pe 11), Shenandoah | G1+Aikar = standardul optim pentru MC |
| Memorie | Xms 1G → Xmx 4G (crește doar la nevoie) | fix | optim |

## ETAJUL 2 — JAR-UL SERVERULUI (inima)

| Piesa | Acum | Alternative (TOATE care există pe 1.16.5) | Verdict |
|---|---|---|---|
| Server jar | **Mist 1.16.5-33** = Mohist + patch-uri Paper | CatServer (cel mai compatibil), Arclight (cel mai stabil), Mohist (mai gras), MaxLite/Forge pur (fără pluginuri), fork custom compilat de noi (+5-15% teoretic) | Mist = minim consum CU pluginuri |
| Loader moduri | Forge 36.2.42 | ❌ nimic — dictat de pack | fix |
| Strat pluginuri | Bukkit/Spigot/Paper API injectat de Mist | ❌ singura tehnologie存在 pe Forge 1.16.5 | fix |

## ETAJUL 3 — MODURILE (28 ale tale + 13 de performanță)

| Grup | Conținut | Înlocuibil? |
|---|---|---|
| Modurile tale | Pizzaland v68, vehicule, furniture, voicechat etc. — **NEATINSE** (doar dezbrăcate de texturi pe server: −130 MB) | ❌ sunt proiectul |
| Performanță CPU | RoadRunner (=Lithium pe Forge), AI-Improvements, Clumps, FastFurnace, FastWorkbench, Get It Together Drops | ✅ setul complet existent — nu mai e nimic |
| Performanță RAM | FerriteCore, Saturn, ModernFix, memoryleakfix, **DataFixerSlayer** (ucide DFU) | ✅ setul complet |
| Lumină | Radon (=Phosphor) | Starlight nu există pe Forge 1.16.5 (verificat) |
| Pornire | LazyDFU (înlocuit de DataFixerSlayer), ModernFix | complet |
| Idle | **Hibernateforge** (adoarme serverul gol) | alternativ: lazymc (proxy Rust — blocat de panou), Multiplayer Server Pause |
| EXTREME (doar MaxLite) | MCMT (multithreading), Performant | pe hibride se bat cu stratul Bukkit |

## ETAJUL 4 — PLUGINURILE (13)

| Funcție | Acum | Înlocuibil cu |
|---|---|---|
| Economie/comenzi (/home /tpa) | EssentialsX 2.19.7 | FTB Essentials (mod, fără Bukkit) |
| Protecție zone + ban iteme | WorldGuard 7.0.5 | FTB Chunks (mod), GriefPrevention |
| Ploturi copii | GriefPrevention 16.18 | PlotSquared v5 (doar manual de pe SpigotMC) |
| Editat teren | WorldEdit 7.2.5 | WorldEdit mod Forge |
| Ranguri | LuckPerms 5.5 + Vault | FTB Ranks (mod) |
| NPC | ZNPCsPlus 1.0.8 + PacketEvents | Citizens (manual, SpigotMC) |
| Anti-grief iteme | EssentialsX AntiBuild + Protect | config WorldGuard blacklist |
| Pre-generare | Chunky 1.3 | fabrica de lume GitHub (planificată) |

## ETAJUL 5 — CONFIGURILE (fiecare fișier, fiecare valoare care contează)

### server.properties
- `view-distance=5` (de la 10 vanilla = −74% chunks per jucător)
- `sync-chunk-writes=false` (scrierea lumii nu mai blochează tick-ul — câștig mare pe 1.16.5)
- `max-players=15`, `network-compression-threshold=256`, `spawn-protection` on

### paper.yml (doar Mist — patch-urile Paper)
- `no-tick-view-distance: 8` → chunk-urile 6-8 se VĂD dar nu CONSUMĂ (−40-60% CPU chunks)
- `per-player-mob-spawns: true` → mobi corecți, nu exponențiali
- `optimize-explosions: true`, hopper fără evenimente de mutare

### spigot.yml (NOU în ULTRA)
- raze de activare: animale 12, monștri 20, misc 6 (mobii departe = înghețați)
- `mob-spawn-range: 3`, `nerf-spawner-mobs: true`
- merge items 3.5 / exp 4.0, hoppers la 8 ticks, `max-tick-time` cu gardă

### bukkit.yml
- spawn-limits: monștri 40 (de la 70), animale 8, ambient 2
- `period-in-ticks` rărite pentru autosave

### Flaguri JVM (start.sh)
- Aikar complet + `-XX:+UseStringDeduplication`

## ETAJUL 6 — LUMEA

| Piesa | Acum | Planul stil-Rust |
|---|---|---|
| Generare | live, pe serverul slab (scump!) | **Fabrica de lume**: GitHub generează + optimizează + livrează |
| Graniță | nu | world border după pregen |
| Întreținere | nu | MCASelector lunar (șterge chunks nevizitate) |

## ETAJUL 7 — SISTEMUL NERVOS (roboții GitHub)

| Robot | Stare |
|---|---|
| build-lite (construiește tot la orice schimbare) | ✅ viu |
| deploy-zampto (urcă pe server prin SFTP) | ✅ viu, trăgaci manual |
| backup-zampto (lumea salvată noaptea la 3:00) | ✅ scris, pornește singur |
| decompile-pizzaland (sursa v68 pentru studiu) | ⚙️ 90%, un bug rămas |
| fabrica de lume | 🔲 următoarea |
| monitor TPS/RAM/online | 🔲 după IP:port de la tine |

---

## REGULA DE AUR A PROIECTULUI
**Prioritate: să MEARGĂ modurile + pluginurile. Erorile se repară din mers. Fiecare pas = scanare completă a netului înainte. Stil Rust: consum minim obsesiv, totul automatizat, totul documentat.**
