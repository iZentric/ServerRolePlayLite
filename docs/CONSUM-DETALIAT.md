# 📊 CONSUMUL LA ORICE — cifre concrete (adunate de pe tot netul)

> Pack-ul tău: 28 moduri Forge 1.16.5. Cifrele marcate (est.) sunt estimări derivate
> din benchmark-urile publice citate la final; restul sunt măsurători publicate.

## 1. RAM la IDLE (server pornit, 0 jucători)

| Software | RAM gol (fără moduri) | RAM cu pack-ul tău (28 moduri) | Note |
|---|---|---|---|
| Vanilla 1.16.5 | **0.77 GB** (măsurat) | — nu poate rula moduri | baseline |
| Paper | 0.5–0.8 GB (−10-30% vs vanilla) | — nu poate rula moduri | doar pluginuri |
| **Forge pur = MaxLite** | ~1.5 GB | **~1.8–2.3 GB (est.)** | 🏆 cel mai mic cu modurile tale |
| **Mist (Paper patches)** | ~1.6 GB | ~2.0–2.5 GB (est.) | RAM ≈ Arclight, dar CPU mult mai mic |
| **Arclight** | ~1.7 GB | ~2.1–2.6 GB (est.) | +0.2–0.4 GB stratul Bukkit + 7 pluginuri |
| Mohist | ~1.8 GB | ~2.3–2.9 GB (est.) | cel mai gras hibrid activ |
| SpongeForge | ~2.2 GB | ~2.8–3.5 GB (est.) | eliminat |

## 2. Consum PER JUCĂTOR

| Software | RAM / jucător | CPU |
|---|---|---|
| Paper | ~40 MB | 1 core ≈ 25-40 jucători vanilla |
| Vanilla | ~50-100 MB | 1 core ≈ 15-25 jucători |
| Forge modat | **~100–175 MB** | 1 core ≈ 8-15 jucători (moduri grele) |
| cu per-player-mob-spawns (doar Mist) | −20-30% din costul mobilor | ✓ |

→ Pe Zampto (8 GB): **MaxLite ține lejer 10-15 jucători** cu pack-ul tău.

## 3. Impactul SETĂRILOR (astea fac diferența cea mai mare!)

| Setare | Valoare normală | La noi | Câștig măsurat |
|---|---|---|---|
| view-distance | 10 (441 chunks/jucător) | **6 (169 chunks)** | **−62% chunks** → −10-15% RAM per nivel redus |
| no-tick-view-distance | n/a | **8 (doar Mist)** | −40-60% CPU pe tick-uit chunks; vezi departe fără cost |
| simulation (benchmark Paper 50 jucători) | VD10: 8.2 GB RAM, 16-18 TPS | VD7+no-tick: **4.8 GB, 20 TPS** | **−41% RAM, −41% MSPT** |
| entity-activation-range | 32 | **16-24** | mobii departe de jucători nu mai ticăie |
| hopper-transfer | 1 tick | **8 tick** | hopperele = top 3 mâncătoare de TPS |
| spawn-limits monsters | 70 | **40** | −43% mobi |
| Xms (RAM la pornire) | = Xmx (ocupă tot) | **1 GB, crește la nevoie** | idle real mult mai mic |
| tick-inactive-villagers | true | **false** | villagerii = CPU gratis pierdut |

## 4. Impactul MODURILOR de performanță (toate incluse în toate variantele)

| Mod | Ce taie | Mărime efect |
|---|---|---|
| ModernFix | pornire + RAM | pornire ~2x mai rapidă, RAM „semnificativ redus" (autor) |
| FerriteCore | RAM blockstates | „drastic la pack-uri mari" — sute de MB |
| Saturn | RAM buffers | zeci-sute MB |
| MemoryLeakFix | scurgeri | oprește creșterea RAM în timp |
| RoadRunner (Lithium) | CPU logica jocului | „cel mai important mod de server pe 1.16.5" |
| Radon (Phosphor) | CPU lumină | generare chunk-uri vizibil mai rapidă |
| AI-Improvements | CPU AI mobi | −CPU pe entități |
| Clumps | entități XP | orburile = 1 entitate în loc de zeci |
| FastFurnace/Workbench | CPU rețete | recalculări eliminate |
| LazyDFU | pornire + RAM | DFU nu se mai încarcă degeaba |

## 5. CONCLUZIA cu cifre (pentru serverul tău de pe Zampto)

| Variantă | RAM idle (est.) | RAM cu 5 jucători (est.) | CPU | Pluginuri |
|---|---|---|---|---|
| 🏆 MaxLite | **1.8–2.3 GB** | 2.4–3.1 GB | cel mai mic | comenzi din moduri |
| 🥇 Mist EXPERIMENTAL | 2.0–2.5 GB | 2.5–3.2 GB | **cel mai mic CU pluginuri** (no-tick + per-player-spawns) | ✅ reale |
| 🥈 Arclight | 2.1–2.6 GB | 2.7–3.5 GB | mic | ✅ reale |
| ❌ Mohist | 2.3–2.9 GB | 3.0–4.0 GB | mediu | ✅ |

### Surse
- Test real idle vanilla 774 MiB + ATM9 12.5 GB: hostadvice.com (Pine Hosting, 2026)
- Tabele bază+per-jucător+per-mod: calculatorsuniverse.com, infinitycalculator.com
- Benchmark view-distance/no-tick (−41% RAM, −41% MSPT): sparkanalyzer.io
- Per-core jucători + optimizări CPU: paperchunk.com
- Paper −10-30% RAM: wisehosting.com
