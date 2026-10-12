# BENCH CUANTIC — server live, **jucător real în lume**

Probele nu sunt simulate: datele vin de pe instanța activă (`92.5.171.150:25565`), cu **1 jucător online**
(`iZentric`), prin puntea de consolă (comenzi → `cmd.in` → stdin JVM → răspuns citit din `live.log`).
Raport brut: [`analysis/BENCH-LIVE.md`](../analysis/BENCH-LIVE.md) · generator: [`scripts/bench-live.sh`](../scripts/bench-live.sh)
Când: 2026-10-09 23:11 UTC.

| Metrică | CUANTIC (optimizat) | baseline (pack original, aceeași mașină) | Observație |
|---|---|---|---|
| **MSPT min/med/95%ile/max** (10 s) | 1.6 / **2.4** / 4.9 / 12.5 ms | — | 2.4 ms pe tick = ~12% din bugetul de 50 ms |
| **MSPT** (1 min) | 0.8 / 2.4 / 7.8 / **278.9** ms | — | spike-ul de 279 ms e din fereastra în care eu rulasem `spark health/gc` + `list`; **nu e atribuit cu certitudine** |
| **TPS** | raportat de `spark health` (fără „Can't keep up") | — | `Can't keep up`: **0** pe tot logul sesiunii |
| **CPU** | 8% proc / 9% sistem (10 s), 13%/17% (1 m), pe **2 vCPU** | — | ~0.26 dintr-un nucleu, cu un jucător activ |
| **RAM (heap)** | 742.7 MB / 2.0 GB (36%) | — | `-Xmx2G` |
| **RAM (proces, peak)** | **VmHWM 2.59 GB** (RSS 2.62 GB) | nu există încă un baseline în același scenariu | cifra de 4.19 GB vârf (`analysis/viteza*`) e **aceeași construcție** la load sintetic, deci **nu e comparație** — o lasă pentru baseline-ul dedicat |
| **GC pauze** | G1 Young: **47.2 ms mediu**, 25 colector, frecvență 24 s; **G1 Old: 0 colector** | — | zero full-GC = fără freeze lungi |
| **Timp pornire** | `Done (14.448s)` (acceptă jucători) / `Dedicated server took 92.639 s to load` (tot, inclusiv pluginurile) | `Done 14–83 s` (variație mare pe disc împrăștiat) | 92 s e costul async al pluginurilor + regiuni; jucătorii pot intra după 14 s |
| **Latentă rețea** | **4 ms** TCP RTT Cloud Shell → `92.5.171.150:25565` (prin frps) | — | tunelul nu adaugă o secundă de net, adaugă milisecunde |
| **Discuri** | 3.15 GB folosiți din 5.0 GB home (63%) | — | limita reală a cutiei, nu a serverului |
| **Erori critice** | 0 (`crash|OOM|tick loop exception`) | 0 | |

## Cum se reproduc (oricine, 0 lei)
```bash
# pe masina care gazduieste serverul, cu un jucator in lume
echo "list" > ~/cuantic-live/cmd.in            # citi in ~/cuantic-live/live.log
echo "spark health" > ~/cuantic-live/cmd.in    # MSPT min/med/p95/max + CPU + heap
echo "spark gc" > ~/cuantic-live/cmd.in         # pauze GC pe colector
bash scripts/bench-live.sh                      # tot + esantion OS, in analysis/BENCH-LIVE.md
```

## Limitari oneste (ce NU acopera raportul asta)
- **1 jucător, nu 3-10.** Cifrele de sub sarcina mare (tp99, GC sub lupta cu multi playeri, chunk gen paralel) nu sunt masurate.
- `jstat -gcutil` **nu merge** in Cloud Shell (`Could not map vmid to user Name`) ⇒ am folosit `jcmd GC.heap_info` + `/proc/<pid>/status` (VmHWM/VmRSS) + spark.
- spike-ul de 278.9 ms **nu este atribuit** unui mod anume; atribuirea ar cere `spark profiler` cu export si corelare cu evenimentul.
- discul de 5 GB: la ~3.5 GB ocupati nu mai incape un al doilea world/back-up mare.
- nu exista inca masurare „hybrid cost" (Arclight vs Forge curat, acelasi set de moduri) — e urmatorul experiment;
  la fel si un **baseline real** (packul original, nemodificat, aceeasi masina, acelasi scenariu) ca sa putem
  afirma cite o economie face Cuantic. Fara el, nu vindem „−38%" nicaiura.
