# FunCity — arhitectura motorului hibrid (1.16.5)

Data documentului: 2026-10-13. Licența de distribuție aleasă de proprietar: **privat**.
Toate afirmațiile de mai jos poartă marcajul lor de adevăr: [verificat @2026-10-13 cu sursă],
[măsurat pe box], [estimare], [netestat]. Nimic nu e "cel mai rapid din lume" — e ce putem
dovedi pe hardware-ul și cu setul declarate.

## 1. Ce moștenim și ce construim

Moștenit (nu redenumim, declarăm):
- **Minecraft 1.16.5** — cod de server proprietar Mojang, nu se redistribute; build-ul
  nostru produce un *instpector-patched JAR* prin ForgeGradle la timp de build (mecanismul
  legal standard al ecosistemului Forge).
- **Forge 1.16.5 (36.x)** — loader, Mappetats/AT, FML.
- **Mohist 1.16.5** [verificat @2026-10-13: repo github.com/MohistMC/Mohist, branch 1.16.5,
  ultimul release public Maven `1.16.5-1237` Apr 2024, **licență GPL-3.0** conform POM
  [sonatype]] — puntea Forge↔Bukkit (mixin-uri + reimpl. CraftBukkit). Pe box rulează build
  1242 (nedașuit public, mai nou decât 1237) — [măsurat pe box pe 2026-10-12].
- Câteva componente din setupul live actual rămân ca plugin/mod externi, nu intră în motor.

Construim noi (identitatea FunCity, în ordinea valorii):
1. **Serie de patch-uri pe stratul hibrid** — pornind de la defectele *dovedite* pe motorul
   live al proprietarului: crash-urile hopper→vehicul (NPE în VanillaInventoryCodeHooks /
   InventoryMoveItemEvent, 23 din 47 de crash-reports analizate în backup — documentat în
   `analysis/RP-BACKUPS-2026-10-12.md`). Un patch de stabilitate real > 100 de micro-opturi.
2. **Cache pe calea fierbinte a podului de evenimente** [netestat ca bottleneck — prima
   acțiune e profiling cu Spark/JFR, abia apoi patch].
3. **Politică de JVM și profiluri de configurare** (Compatibility/Balanced/Performance)
   generate de motor, nu aruncate din liste de flaguri; moștenește și institucionalizează
   ce a ieșit din duelul de motoare al proiectului (Aikar-style G1 la -Xmx proporțional,
   plafon RAM protejat anti-OOM ca pe box).
4. **Harness de validare reproducibil**: build CI pe runner GitHub, bench headless cu
   comandă prin stdin (fără rcon, fără boti), export recent-ticks + Spark, praguri de
   acceptare fixate *înainte* de măsurători.

Nu promitem: Folia-style region threading (schimbare arhitecturală cu spargere de
compatibilitate pe pluginii RP existenți), C2ME/Lithium/Krypton native pe 1.16.5 Forge
(porturile din epocă rămân candidate doar în profilul Experimental, fiecare cu fișa lui).

## 2. De ce 1.16.5 și nu 1.21.x (decizie strategică, 2026-10-13)

1. Clientul `lite` trebuie să meargă pe orice laptop vechi → 4 GB RAM, Java 8友好 — 1.16.5
   e singurul care bate acolo cu setul complet de moduri RP; un 1.21 cu MTR/elevatoare/
   trafic nu încape și nu e migrat gratis (porturi de moduri = luni de negotiation, nu de cod).
2. Ecosistemul țintă (36 moduri + 28 pluginuri) trăiește pe 1.16.5; motorul care nu rulează
   setul proprietarului nu-și are rostul pentru el.
3. Licență: baza Mohist = GPL-3.0 — **compatibilă cu folosirea privată fără nicio obligație**
   (serverul nu e "distribuire"); CatServer (AGPL) ar fi impucat publicarea surselor către
   jucători. Dacă FunCity devine public într-o zi, GPL nu ne blochează: publicăm sursele și
   gata. NeoForge 1.21 + Arclight rămâne track-ul doi, separat, validat abia după ce
   FunCity 1.16.5 produce cifre.

## 3. Registrul de candidați (fișe complete în functity/FISE/, aici doar verdictul)

Cercetarea nu pretinde "fiecare JAR de pe internet". Aria: motorle hibride din ladder-ul
existent (34 de entry-uri, `analysis/` — lats redate), optimizarile 1.16.5 citate în surse
ecosistemice + căutări cu date pe 2026-10-13. Restul lumii: [nevăzut, asumat].

| candidat | strat | licență | verdict |
|---|---|---|---|
| Mohist 1.16.5 | pod hibrid | GPL-3.0 | **baza** — pod matur singurul cu istoric pe box |
| FerriteCore (forge 1.16.5) | memorie/model bin | MIT | reutilizare directă [verificat există pe 1.16.5 forge] |
| Starlight forge 1.16.5 / „Starlight x Create" | lighting/chunk gen | LGPL | adaptare: verificat conflict cu MTR light providers — Experimental |
| Performant | entity/AI iterare | MIT | adaptare: se suprapune cu patch-uri proprii — alegeri pe profil |
| RoadRunner | chunk I/O | LGPL | adaptare: world format existing, verificat save roundtrip — Balanced+ |
| Krypton Reforged (forge 1.16.5) | rețea | GPL | adaptare cu test de login multi-client |
| RandomPatches | fix-uri diverse | MIT | reutilizare directă (selectiv, cu audit de patch-uri) |
| AI Improvements | pathfinding/AI | MIT | Experimental doar (mixin risc pe Forge 36.5) |
| Radium (port Lithium pe forge) | tic-uri entități | LGPL | Experimental doar; reputație de instabilitate pe epocă |
| FastSuite/FastWorkbench/FastFurnace | UI per-player | MIT | reutilizare directă în Balanced (câștig mic, risc nul) |
| Overworld Two / C2ME / Canary / Saturn | chunk gen / GC | variat | RESPINS pentru 1.16.5: nu există port stabil sau schimbă world-genul (seeds RP) |
| Smooth Boot | GC tune | MIT | RESPINS: înlocuit de politica proprie de JVM (pct. 1.3) |

Orice intră în Build 1 trece prin fișă completă: Problemă→Mecanism→Sursă→Licență→
Compatibilitate→Risc→Experiment→Rezultat→Decizie, cu link și commit la data verificării.

## 4. Arhitectura pe straturi (ce tice de unde)

```
┌─ config FunCity (profil + generare) ─┐
│ profil: compatibility|balanced|performance[+experimental opt-in] │
├─ stratul NOU (cod FunCity, repo propriu) ───────────────────────┤
│ P1 hopper/vehicle event hardening (NPE dovedit pe live)          │
│ P2 event-bridge type-cache (hot path Bukkit←Forge, doar dacă     │
│    JFR arată >=2% din tick — altfel nu-l punem)                  │
│ P3 profil de GC/JVM generat pe baza hardware-ului și MemTotal,   │
│    moștenește politica ramceil de pe box                         │
├─ Mohist (puntea, GPL) ─┬─ Forge 36.5 ─┬─ CraftBukkit reimpl ─────┤
├─ patch-uri de build: AT + mixin FunCity (doar P1/P2), restul     │
│   rămân moduri externe ca să se poată dezactiva individual       │
└─ vanilla 1.16.5 (nu se redistribuie; se obține la build) ───────┘
```

Reguli de threading: **nicio mutare de logică pe alte fire** în Build 1. Patch-urile de
concurență (dacă JFR le justifică) intră cu: ownership declarat pe clasa țintă,
test de ordonare (evenimente în aceeași ordine ca în vanilla pe seed fixat) și
reproducere pe runner + pe box.

## 5. Validare — metodă fixată ÎNAINTE de a măsura

- **Medii**: runner GitHub hosted (4 core/16GB, reproductibil, identic la fiecare tură) =
  referința CI; box-ul proprietarului (2 core, fără AVX2, ~12 GB) = ținta reală,
  folosit DOAR cu acordul explicit al lui marius pentru cursele de validare finală.
- **Workload**: W1 boot gol (pornire, memorie, classload); W2 chunk gen pe seed fixat
  (512×512 blocuri, 8 fire) — fărăOverworld Two, world vanilla; W3 entity spam 200 de
  vaci + hopperi în lanț (testul P1: trebuie **0 crash-uri**, baseline-ul live are 23/47);
  W4 redstone flywheel (ceas 1k ticuri); W5 RP-set complet (36+28) pornit, 90 s idle +
  „debug"-window. Fiecare curbă: warm-up 60 s, 3 rulări, mediana + dispersia.
- **Metrici**: TPS și MSPT p50/p95/p99 din `debug/recent-ticks` (bukkit debug, prin stdin),
  RSS/VmHWM, GC pause din JFR (`jdk.GCPhasePause`), timp de boot, erori în log, hash de
  integritate pe level.dat după salvări repetate. Praguri: P1 zero crash-uri; restul —
  niciun regress >3% vs baseline (Mohist-1242 live configurat identic), câștig declarat
  doar dacă iese din dispersie.
- **Onestitate**: Cifrele de pe runner NU se poartă 1:1 pe box (fără AVX2, 2 core, I/O mai
  lent) — raportăm separat, cu marcare clară [măsurat pe runner] vs [măsurat pe box].

## 6. Build și CI

- `functity-build.yml`: clonează MohistMC/Mohist @1.16.5 (commit fixat, nu branch —
  reproducibil), aplică `functity/patches/*.patch`, ForgeGradle `setup` + `build`, JAR-ul
  iese pe bransa `functity` cu SHA-256 în nume + manifest JSON (versiuni, commit-uri,
  licențe inventory). Fără artefacte netestate în release-ul `lite`, fără atingerea
  serverului live — reguli vechi, neschimbate.
- Fiecare tur de build = commit + raport în `functity/JURNAL.md` (ce-am implementat,
  ce-am testat, cifre, ce e blocat, pasul următor — formatul cerut de misiune).

## 7. Buget și limite declarate

Bugetul prezentei etape: resursele gratuite de CI (runner GitHub, fără costuri), fără
achiziții, fără servicii plătite. Nu există buget de "maximul posibil" — există etapa
urmează, și limita demonstrată se declară exact așa cum cere misiunea: performanța
noastră măsurată, nu superlativ de catalog. Când epuizez lista de candidați fără câștig
reproductibil peste dispersie, declar etapa incompletă doar dacă rămân direcții
neexplorate — și leenumăr.
