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
