# TEHNOLOGII CUANTIC 1.6.2 — matricea candidaților (cercetare + decizii)

Cercetarea de fata: 5 apeluri de căutare, 13 surse unice accesate, toate în 2026-10-10.
Nu e „tot internetul" — e lista de candidați care au sens pentru **Motorul nostru exact:
CatServer 1.16.5 (Forge+Bukkit+Spigot) + Freeroam, Java 17, 2 vCPU / 11.8 GB RAM / disc 5 GB**.
Regula din promptul CUANTIC: se integrează DOAR ce aduc castig măsurat + compatibilitate verificată.

## Decizii luate în 1.6.2

| Componenta | Ce rezolvă | Verificat pe 1.16.5? | Licență | Decizie |
|---|---|---|---|---|
| **FerriteCore 2.1.1-forge** | Rescrie BlockState-urile (≈600 MB în pack mare), storage-ul de proprietăți (≈170 MB), stringele ModelResourceLocation (≈300 MB), **NBT-ul chunk-urilor parțial încărcate (90-100 MB, side: server)** | da — Modrinth listează explicit „1.16.5 / Forge / Client-side, Server-side", fără dependințe | MIT | **ADOPTAT** (server + oglindit pe client, ca lista de moduri să fie identică) |
| **bukkit.yml `chunk-gc.load-threshold: 300`** | Feature-ul e **dezactivat implicit** (load-threshold=0) deși eliberează chunk-urile libere = RAM + CPU | da (Bukkit 1.16) | Bukkit | **ADOPTAT** |
| Chunky (pregenerator) | Pre-generează chunk-uri = zero lag la explorare, disc limitat la border | da — Forge 1.16.5+ și variantă Bukkit | GPL-3.0 | **RESPINS pe Cloud Shell**: home = 5 GB cu 63% ocupați (1913 MB liberi, măsurat azi); pregen ar umple discul și ar omorî java. **Rămâne adoptat pe VM** (disc mare). |
| LazyDFU | DFU-ul face boot-ul lent (9 s pe Ryzen 9, 57 s pe i5-8250U măsurate de autor) | da, dar **deja acoperit** | MIT | **RESPINS (duplicat)** — ModernFix e în pack și face la fel (logul nostru: `Ksyxis: Enabled compatibility hack with ModernFix`). Două exemple de „ia de la toți" care de fapt încetinește. |
| Arclight / Mohist / Magma | Hy alternative mod+plugin | Arclight 1.16.5 există; Mohist „Updates paused"; Magma = doar 1.12.2 | MIT/GPL | **RESPINS ca motor**: CatServer e singurul marcat **LTS/STABLE** pe 1.16.5; măsurătorile noastre: CatServer+J17 = 2814 MB / 11.1 s, Arclight întreg = **NU PORNESTE**. |
| Paper / Purpur / DivineMC / Pufferfish / Leaves | Cele mai bune servere pe pluginuri | **NU** pe 1.16.5 cu moduri Forge (sunt doar Bukkit) — DivineMC declară Minecraft 26.3 / Java 25 | GPL-3.0 | **RESPINS ca bază** (păstrate ca referință de idei: CatServer duce deja „some Paper optimization" conform README-ului) |
| ClearLag / void-world / config-uri „aggressive" | Promit TPS, taie entități aleatoriu | — | — | **RESPINS** — stricà survival-ul cerut (mobs, farms) și maschează problema în loc s-o rezolve |
| Java 8/11 (recomandarea README-ului CatServer) | Compatibilitate maximă cu moduri | — | — | **PĂSTRĂM Java 17**: setul complet de flaguri GC e validat pe 17 în CI; README-ul zice „Java 12-17 supported, may have compatibility issues" — la noi T3/T4 arată 0 kickuri și 0 erori de handshake. |

## Resurse citate (surse primare, nu bloguri)
- CatServer 1.16.5 README (LTS/STABLE, remap, „some Paper optimization", recomandare Java 8/11, LGPL-3.0): https://github.com/Luohuayu/CatServer/blob/1.16.5/docs/README_EN.md
- CatServer mirror + licență LGPLv3, ultima actualizare publicată 2026-03-13: https://sourceforge.net/projects/catserver.mirror/
- FerriteCore, defalcarea pe puncte a memoriei economisite (inclusiv 90-100 MB server-side la chunk NBT): https://github.com/malte0811/FerriteCore/blob/main/summary.md
- FerriteCore 2.1.1-forge, 1.16.5, client+server, fără dependințe: https://modrinth.com/mod/ferrite-core/version/2.1.1-forge și https://www.curseforge.com/minecraft/mc-mods/ferritecore/files/4074330 (106.01 KB, MIT)
- LazyDFU, cifrele autorului (9 s / 57 s DFU): https://modrinth.com/mod/lazydfu
- Chunky (Bukkit), comenzi + licență GPL: https://dev.bukkit.org/projects/chunky-pregenerator
- Ghidul de valori pentru spigot.yml/bukkit.yml (mob-spawn-range 3, entity-activation-range 16/24/8, chunk-gc load-threshold): https://winternode.com/help/games/minecraft-java/configuration/server-optimization și https://builtbybit.com/threads/guide-optimizing-spigot-remove-lag-fix-tps-improve-performance.187104/
- Comparativul de stabilitate al hibridelor („hybrid nu garantează compatibilitate universală"): https://space-node.net/blog/paper-purpur-arclight-mods-plugins-2026 și https://www.libhunt.com/compare-Arclight-vs-Mohist

## Cifrele noastre, aceleași condiții (1 jucător, warm 120 s, Spark, aceeași mașină)
| | 2G + 3 flaguri | 8G + 3 flaguri | 11884M + set validat | 1.6.2 (+FerriteCore, load-threshold) |
|---|---|---|---|---|
| MSPT 10s med/p95/max | 2.4 / 4.9 / 12.5 | 1.6 / 9.1 / 29.5 | 1.1 / 2.0 / 10.3 | în curs (BENCH după apply) |
| GC young mediu × nr | 47.2 ms × 25 | 111.38 ms × 8 | 115.88 ms × 8 | |
| RAM (RSS) | 2613 MB | 3367 MB | 3192→3732 MB | |
| boot | 14.448 s | — | 13.664 s | |

## Ce NU s-a putut verifica de aici (și nu se declară trecut)
Login real cu noul mrpack pe calculatorul lui (kick de listă de moduri), latența pe scaunul
jucătorului, desync/rubberband, duplicări de itemi, mai mulți jucători simultan. Testul T9 din
`analysis/ACCEPTANCE.md` lasă asta scrisă explicit, nu o transformăm în „trecut".
