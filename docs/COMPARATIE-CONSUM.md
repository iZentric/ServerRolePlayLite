# 🔬 Cercetare completă: consumul MINIM pentru server modat 1.16.5

Cerința: moduri Forge (pack-ul Freeroam) + comenzi/funcții de „pluginuri" + consum cât mai mic.

## A. Jarul serverului (software-ul de bază)

| Software | Moduri Forge | Pluginuri Bukkit | Consum | Stare proiect | Verdict |
|---|---|---|---|---|---|
| **Forge pur 36.2.42** | ✅ | ❌ | 🟢 **CEL MAI MIC** (zero straturi în plus) | oficial, stabil | 🏆 câștigător consum |
| **Arclight 1.16.5** | ✅ | ✅ | 🟡 mic (strat subțire prin Mixin) | activ, recomandat #1 dintre hibrizi | 🥈 dacă vrei pluginuri reale |
| Mohist 1.16.5 | ✅ | ✅ | 🟠 mai mare; „optimizările" lor = marketing neverificat | activ | nu |
| CatServer 1.16.5 | ✅ | ✅ | 🟠 nedovedit | semi-activ | nu |
| Magma 1.16.5 | ✅ | ✅ | — | ❌ mort | nu |
| Mist 1.16.5 (fork Mohist+Paper) | ✅ | ✅ | 🟡 | ❌ abandonat | nu |
| LoliServer 1.16.5 (fork Mohist) | ✅ | ✅ | 🟠 | ❌ abandonat | nu |
| SpongeForge 1.16.5 | ✅ | ❌ (doar pluginuri Sponge, altă lume) | 🔴 greu | activ-ish | nu |
| Paper / Purpur / Pufferfish | ❌ | ✅ | 🟢 foarte mic | activ | **inutil: nu poate rula modurile!** |

> Regula de aur din comunitate: orice hibrid ține DOUĂ API-uri în viață simultan → consum și
> riscuri în plus. Cel mai mic consum = fără hibrid.

## B. Moduri server-side care ÎNLOCUIESC pluginurile (zero overhead, zero instalare la jucători)

| Mod (1.16.5 Forge) | Înlocuiește pluginul | Comenzi |
|---|---|---|
| **FTB Essentials** | EssentialsX | /sethome /home /tpa /tpaccept /back /spawn /rtp /warp /setwarp /nick /mute /fly /heal /invsee /trashcan |
| **FTB Ranks** (+ FTB Library) | LuckPerms | ranguri + permisiuni + prefixe chat |
| FTB Chunks | WorldGuard/claims | protecție terenuri (claim pe hartă) — opțional |
| Simple Voice Chat (DEJA în pack!) | pluginuri de voice | voce în joc |

## C. Moduri de performanță suplimentare pentru server (1.16.5 Forge)

| Mod | Ce optimizează | Inclus deja? |
|---|---|---|
| ModernFix | pornire 2x mai rapidă + RAM mult redus | ✅ era în pack |
| FerriteCore | RAM (drastic la pack-uri mari) | ✅ era în pack |
| LazyDFU | pornire + RAM | ✅ era în pack |
| Clumps | orburi XP comasate | ✅ adăugat |
| AI-Improvements | AI-ul mobilor (CPU) | ✅ adăugat |
| MemoryLeakFix | scurgeri de memorie | ✅ adăugat |
| **RoadRunner** (port Lithium) | logica de joc, tick-uri — „cel mai important pe 1.16.5" | ➕ se adaugă acum |
| **Radon** (port Phosphor) | motorul de lumină — generare chunk-uri rapidă | ➕ se adaugă acum |
| **FastFurnace + FastWorkbench** | cuptoare/crafting fără recalculări | ➕ se adaugă acum |
| **Smooth Boot (Reloaded)** | distribuția thread-urilor la pornire | ➕ se adaugă acum |
| **Saturn** | amprenta de memorie | ➕ se adaugă acum |
| Performant | TPS, dar închis ca sursă + conflicte cu RoadRunner | ❌ sărit intenționat |
| MCMT (multithreading) | tick-uri pe mai multe nuclee, dar crăpă cu moduri de vehicule | ❌ sărit intenționat |

## 🏆 Concluzia

**Consum minim absolut = Forge pur + FTB Essentials/Ranks (comenzi) + artileria de performanță de mai sus.**
Arclight rămâne disponibil ca variantă secundară dacă vrei vreodată pluginuri Spigot reale.

Build-ul produce ACUM ambele variante la Releases:
- `Freeroam-Lite-Server-MaxLite-*.zip` ← **Forge pur, consumul cel mai mic** (recomandat)
- `Freeroam-Lite-Server-Arclight-*.zip` ← hibrid cu EssentialsX/LuckPerms/Vault/Chunky

### Surse
- Lista hibrizilor + recomandări: github.com/Shawiizz/minecraft-hybrids
- Arclight vs Mohist: libhunt.com/compare-Arclight-vs-Mohist
- Mohist marketing neverificat: xgamingserver.com/blog/what-is-mohist
- r/admincraft despre hibrizi: reddit.com/r/admincraft/comments/13mob3r
- FTB Essentials (104M+ descărcări): curseforge.com/minecraft/mc-mods/ftb-essentials
- Ghid optimizare Forge 1.16.5 (RoadRunner/Radon): gamehostbros.com/guides/games/minecraft/forge-performance-guide
- Moduri server-side 1.16.5: reddit.com/r/feedthebeast/comments/lztjet

## D. Căutare suplimentară pe GitHub (proiecte „altceva")

| Proiect GitHub | Ce e | Verdict pentru 1.16.5 |
|---|---|---|
| Mirai (etil2jz) | fork Forge de performanță | ❌ ARHIVAT (mort) + era doar 1.18.2 |
| ModcraftForge | fork Forge performanță 1.16.4 | ❌ experiment abandonat, 4 stele |
| Tenet (ex-Thermos) | hibrid Forge+Bukkit | ❌ pentru versiuni vechi (1.7/1.12) |
| Kettle / Magma-Forge / Cauldron-Reloaded | hibrizi Forge+Bukkit | ❌ aceeași clasă cu Mohist, nu mai lite |
| HybridFix | plugin de optimizare PENTRU hibrizi | 🟡 util doar dacă rulezi Arclight |

**Concluzie finală, după GitHub + tot netul:** pentru moduri Forge 1.16.5 NU EXISTĂ nimic
mai lite decât **Forge pur + stack-ul de moduri de performanță** (varianta MaxLite din
acest repo). Orice alt „server software" ori e mort, ori adaugă straturi peste Forge.

## E. VERDICTUL FINAL: moduri EXACTE + pluginuri reale, consum minim

| Loc | Variantă (toate la Releases) | Pluginuri reale | Consum | Risc |
|---|---|---|---|---|
| 🥇 teoretic | **Mist EXPERIMENTAL** (Mohist+patch-uri Paper, no-tick-view-distance, per-player-mob-spawns) | ✅ | cel mai mic CU pluginuri | ⚠️ proiect abandonat 2021 |
| 🥈 sigur | **Arclight** ultra-tuned | ✅ | foarte mic | stabil, întreținut |
| 🏆 absolut | **MaxLite** (Forge pur + FTB comenzi) | ❌ (doar comenzi din moduri) | CEL MAI MIC posibil | zero |

---

## F. CATALOG COMPLET — TOT ce există pe net pentru moduri Forge 1.16.5 + pluginuri (căutare exhaustivă 2026)

| Soluție | Stare | Descărcabil? | Verdict |
|---|---|---|---|
| **Arclight 1.0.25** | ✅ întreținut | ✅ GitHub | în release-ul nostru |
| **Mist 1.16.5-33** (Mohist+Paper) | ⚠️ abandonat 2021 | ✅ GitHub | în release-ul nostru (EXPERIMENTAL) |
| **CatServer 1.16.5** (build mai 2023) | ⚠️ 1.16.5 înghețat, dar CEL MAI RECENT hibrid 1.16.5 | ✅ GitHub (23.05.26-1) | **ADĂUGAT — varianta 4** |
| Mohist 1.16.5 | ✅ există | ✅ mohistmc.com | sărit — cel mai gras, Mist e Mohist+patch-uri Paper |
| Magma 1.16.5 | ❌ fundația moartă, repo șters | ❌ niciun artefact pe GitHub | imposibil |
| LoliServer 1.16.5 | ❌ abandonat | ❌ zero release-uri | imposibil |
| SpongeForge 1.16.5 (API 8) | ⚠️ există RC | doar maven Sponge | NU rulează pluginuri Bukkit (EssentialsX/LuckPerms-Bukkit nu merg) — ecosistem separat |
| Cardboard / Banner | ✅ | ✅ | DOAR Fabric — pack-ul tău e Forge, inutilizabil |
| HybridFix | ✅ | ✅ | DOAR 1.12.2 |
| Conversie mod→plugin sau plugin→mod | — | — | **imposibil tehnic**: API-uri diferite (Forge hooks vs Bukkit API), nimeni n-a reușit vreodată automat |

**Concluzie: există EXACT 4 jar-uri funcționale pe lume pentru 1.16.5 Forge+pluginuri (Arclight, Mist, CatServer, Mohist). Avem 3 din 4 în release (am sărit doar Mohist, cel mai consumator, pentru că Mist = Mohist îmbunătățit).**
