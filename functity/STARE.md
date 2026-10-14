# FunCity — stare la 2026-10-13 ~23:30 UTC (canal: annotatii + fisiere pe functity-out)

## Ce exista, verificat
- **Build 0 (baseline)** = `functity-out:builds/b0/FunCity-1.16.5-b0.jar` (8.704.235B,
  sha256 248fb54d…) — Mohist 1.16.5 la pin 754b578e, compilat de CI-ul nostru
  (JDK 11, recipe setup+mohistJar, buildfix P0/P0c/P0d aplicat mereu).
- **Build 1 (+P1)** = `builds/b1.2256/FunCity-1.16.5-b1.2256.jar` (8.704.330B,
  sha256 6a63721c…, verifica in SHA256SUMS pe branch) = baseline + patch-ul nostru
  dropper-NPE-guard. BUILD SUCCESSFUL in 5m54s, reproductibil (lant de patch-uri
  verificat cu `git apply --check` pe arborele fix).
- **Smoc 36/14 pe ambele** (FC-SMOKE36 38481996264): FML porneste pe ambii (`ModLauncher
  mohist-8.1.3`, `--launchTarget fmlserver`), **14/14 plugini Bukkit enablați**
  (LuckPerms…ClaimChunk), zero linii critice, Done 6.4s in faza 2 (bootstrap Mohist =
  2 faze: instalare + rulare; masuratorile trebuie facute in faza 2 cu `run/`+libraries
  deja instalate).
- **Comparabil cu oficialul 1237** pe aceeasi banca: `This server is running Mohist
  version 1.16.5-1237`, tot 14/14, tot 0 critice, Done 6.3s. Diferenta marime
  b1.2256 vs oficial = ~95B (P1-ul nostru) peste +6KB (pin mai nou decit 1237).

## Reguli de infra invatate (in ARHITECTURA 6.9/6.9b — pe scurt)
- Java 11; `setup mohistJar`; colector tintit pe projects/mohist/build/libs cu poarta
  de manifest `ServerLaunchArgs`; publicare = clone cu token in URL pe functity-out;
  diagnostic vizibil DOAR prin annotatii/fisier pe branch (blob/artifact URL-urile sint
  blocate din sandbox); bancii II trebuie curatate `libraries/ run/ version.json /*.jar`
  din pack (guava 21 al CatServer-ului ucide Mohist-ul), dar `mods/*.jar plugins/*.jar`
  RAMIN (excluderea `*.jar` globală = falsa alarmă enabling=0).

## Urma (ordinea batuta in cuie)
1. **FC-BENCH v4** = masuratori MSPT/TPS cu harness 2-faze (install o data / brat,
   3 probe warm × 2 brate, forceload 64 + 40 zombies, fereastra 55+75s ca in scara veche)
   — brate: oficial1237 vs b0 vs b1.2256, Java 11, toti pe acelasi runner.
2. Test P1 functional: dropper→entitate-vehicul in lumea de test (reproduce NPE-ul din
   23/47 crash-uri) — cu P1 oprit vs pornit, apoi soak 30 min.
3. FISE: primele 2 carduri „acceptat" (ferritecore, randompatches partial) dupa ce
   banca v4 are numaratori — doar cu cifrele noastre.
4. MC-RUN v9 pe box — WAITING USER: runner-ul masinii a murit ~20:48; fara
   wake nu mai am canal sa-l ridic. (Serverul box-ului: java viu, port ascultat, SLP
   nu raspunde de la ~17:00 — verdictul v8 arata „nu s-a redresat in 7 min".)

## 7. FC-BENCH v4 — PRIMA MASURARE REALA (rulare 38510786719, brațe publicate 05:29–05:38 UTC, 2026-10-14)

Metoda: 4 brațe × 3 probe boot-la-cald, world comun dupa instalare, java 11 Temurin, -Xmx1536M,
runner ubuntu-24.04 izolat, pack CUANTIC 36/14 cu SHA256 fix (fe1e26…), sursa 100% din git
(functity-out), zero CDN. Verificat in timpul alergarii: 36 mods/14 plugins prezente in stage.

| brat | boot mediu (wall,ant) | CV% | TPS idle | overrun | critice | RSS MB | CPU% idle | login probe |
|---|---|---|---|---|---|---|---|---|
| CatServer 1d8d6313 (motorul istoric, din pack) | 43.35 | 4.3 | 20.0 | 0 | 0 | 2227.8 | 2.5 | refuz Forge (corect) |
| Mohist oficial 1237 | 44.68 | 8.5 | 20.0 | 0 | 0 | 2254.6 | 2.7 | refuz Forge (corect) |
| FunCity b0 (fara patch-uri) | 42.68 | 5.8 | 20.0 | 0 | 0 | 2267.6 | 2.4 | refuz Forge (corect) |
| FunCity b1.2256 (P0+P1) | 33.34 | 5.7 | 20.0 | 0 | 0 | 2256.1 | 1.8 | refuz Forge (corect) |

Ce declaram: b1 nu are regresie fata de oficial la pornire/idle (dimpotriva, -25.4% wall in aceasta
alergare) si zero erori critice pe 12 boot-uri totale. Ce NU declaram: ca b1 "e mai rapid" —
cifrele wall aveau cuantificare de 2s (polling), iar avantajul de ~9s trebuie confirmat cu
v4.19 (poll 0.25s + uptime obiectiv din log) inainte de orice FISE "castig".
Proba de login (client vanilla 1.16.5, protocol 754) a primit refuz FML cu mesajul de Forge-obligatoriu
pe TOATE bratele — consistent cu live-ul (clientii modati intra, vanilla nu); intarzierea reala de
join cu client modat ramane de masurat printr-o faza viitoare (bot mineflayer inmediat ce legam
npm in aceeasi banda de retea).
Prag inainte de rulare: CV<10% pe brat → TRECUT toate 4.
Raportari: functity-out: bench-v4/{20261014-0529,0531,0537,0538}/ (JSON+server-loguri+driver),
verdict agregat: bench-v4/20261014-0538/summary.md.

Banchetul a scos la lumina si 6 buguri de infra CI, acum fixate (mencțiuneat ca sa nu le re-luam):
pack via CDN intermitent → functity-out:pack/ (blob git, auto-reparat de FC-PACKPROBE);
`tr -d '\r'` in YAML devine `tr -d ''` → sed; deadlock `open(fifo,'w')` fara cititor → fd O_RDWR;
instalare intrerupa la EOF pe stdin → FIFO si la faza A + kill pe intreg grupul (killpg);
rapoarte ingestibile prin loguri (Azure blocheaza sandbox-ul) → canal git functity-out +
live-snapshots la 2 min; summary-API/annotations gh: gh nu expun nimic util → tot pe git.

## 7b. Runda B (confirmare, FC-BENCH v4.19, run 38519665645, 2026-10-14 06:19)
v4.19 a introdus poll 0,25 s + **timp obiectiv `Done (x.xs)` auto-măsurat de motor**, pentru că wall-ul pe runner
partajat s-a dovedit zgomotos (ordinea bratelor s-a inversat între runde: b1 cel mai rapid la wall în A, cel mai lent
în B — în ambele runde timpul „Done" e stabil, 2–10 s). Medii Done pe 3 probe (A · B): CatServer 8,07 · 6,35 s;
oficial 4,31 · 3,81 s; b0 4,24 · 4,26 s; b1 3,03 · 4,78 s.
**Verdic final: fără regresie vs mohist oficial (la nivel de zgomot, la boot), câștig măsurat vs CatServer la boot
(29–55%), CV ≤ 9,2%, 0 erori critice, TPS idle 20,0, oprire curată 24/24 porniri. Nu declarăm „cel mai rapid".**
Nu au ieftinit nulla din pack ca sa iasa cifrele; pragurile au ramas cele batute in cuie inainte.
Date complete: `analysis/FUNCTITY-BENCH.md` (JSON verificat prin test, nu hardcodat) — aceleasi cifre sint publicate
si pe site, sectiunea „FunCity — motorul propriu, măsurat, nu promis", cu garda proprie
(`tests/test_functity_bench_site.py`: ce n-a fost măsurat apare NEMĂSURAT, nu umplut).

## 8. Urmatorii pasi (in ordine)
1. Bot mineflayer cu pachet complet → tinta „masurat" pentru latenta de join (singura marime din sectiunea 5 inca
   acoperita doar de respingerea corecta a clientului vanilla).
2. ~~Parser MSPT/GC pe formatul real din loguri~~ → **GC FACUT** (2026-10-14 11:39 UTC): FC-GC
   (`.github/workflows/fc-gc.yml` + `scripts/fc_gc_reprocess.py`) a reprocesat jurnalele `-Xlog:gc*` din
   artefactele rundelor A/B fara alergare noua — verdict in `analysis/FUNCTITY-GC.md`, jurnale brute pe
   `functity-out:bench-v4/gc/`. Rezultat: fara regresie b1 vs 1237/b0 (boot max 97/128 vs 119/99 vs 105/84 ms,
   idle 1–3 pauze ≤ 51 ms in ~930 s, 0 Full-GC); CatServer are pauzele de boot cele mai mari (146/174 ms) si un
   `Full (System.gc())` de 5 ms la pornire. **MSPT** ramine NEMASURAT pina la runda C (v4.2 trimite `forge tps`;
   `ticks tps`/`mspt` erau comenzi necunoscute pe hibride — cauza reala a lipsei din A/B).
3. FISE/STARE: upgrade „netestat" → „masurat" pentru cele cite sectiunea 7 le-a acoperit.
4. Linie de trezire in box (MC-RUN v9, doar dupa acord).
