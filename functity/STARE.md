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
