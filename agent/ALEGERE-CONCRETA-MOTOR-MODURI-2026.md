# Alegerea concretă FunCity RP 1.16.5 — native-first, după testul lean (22.10.2026)

**Aleg acum:** **CatServer oficial 23.05.26-1, cu ținta existentă de 28 moduri client-aligned / șase pluginuri în laborator**, drept baza cea mai defensabilă pentru **următorul test privat**, nu un nou instalator pe PC. RoadRunner rămâne **singur** (nu cu Performant): pe 28/6 brațul Performant a declanșat un marker fatal și a fost respins. Ksyxis rămâne în țintă cât timp funcțiile zonei spawn nu sunt afectate; ModernFix/FerriteCore au acum probe separate favorabile de CPU/heap în CI, dar nu teste cu jucători. Păstrăm armele, vehiculele, vocea, blocurile, biblioteca lor, InControl și Connectivity până la verificarea funcției. Nu adăugăm Chunk Sending ori alte JAR-uri noi. Configurația propusă cu 22 **nu** devine înlocuitorul celor 28: [lista exactă de comparație](FUNCITY-SERVER-LEAN-22.json) rămâne numai un braț experimental de CI.

## Test nou: 28 față de 22, nu doar păreri

Am încercat să scot din **copia izolată** AI Improvements, FastSuite + FastWorkbench + Placebo ca **grup dependent**, Get It Together, Drops! și LazyDFU. [Rularea GitHub **39710079801 — PASS**](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39710079801) a folosit același CatServer oficial/Java 17, același world generat copiat înainte de fiecare probă, 80 zombie, aceleași șase pluginuri, ordine **F/L/L/F** (F=28, L=22), verificare SHA/metadata/dependențe/inventar, patru opriri curate.

| Braț, două observații brute | Boot până la `Done` | CPU s/~30 s | RSS MiB | `forge tps` tick mediu ms |
|---|---:|---:|---:|---:|
| **F: 28 moduri intacte** | **28,55 / 31,06 s** | 1,51 / 1,85 | 2034 / 1623 | 0,25 / 0,52 |
| **L: 22 moduri** | **44,35 / 44,60 s** | 2,01 / 1,53 | 1988 / 1648 | 0,66 / 0,47 |

**Verdict de laborator:** brațul 22 a pornit, dar **a pierdut ~13–16 s la boot în ambele probe**, fără reducere repetabilă de CPU, RSS sau tick. Nu avem motiv să promovăm 22 ca „mai rapid”: șase JAR-uri mai puțin ≠ capacitate mai mare. Lipsa LazyDFU poate explica o parte din costul de boot, dar testul a eliminat șase moduri simultan, deci **nu izolăm cauza** din acest A/B. Aceasta nu demonstrează că toate cele șase optimizatoare cresc numărul de jucători ori că 22 este mai rău sub trafic real; niciunul dintre brațe nu are clienți, crafting, condus sau cele 13 pluginuri.

**Restul dovezilor:** [ablația Ksyxis 28/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39706471206) a arătat avantaj în lumea generată fără jucători, dar poate modifica zona spawn. [RoadRunner versus Performant 15/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39706471113) a dat CPU mai mic RoadRunner, tick mediu mai mic Performant, fără RP real. [Sarcina cu 16 mașini](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39708297969) a eșuat validarea 16 la început/0 la sfârșit; **nu** susține o alegere de motor sau player capacity. FerriteCore/ModernFix au acum o ablație izolată favorabilă în lumea generată (mai jos), **nu** sunt dovedite pe lumea RP cu clienți. Forkul sursă branduit [39699780017](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39699780017) este anulat, fără JAR FunCity nou validat.

## Alte două probe direcționate pe întregul set 28/6

1. **[RoadRunner versus Performant pe 28/6 — 39711647739](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39711647739): FAILURE de compatibilitate pentru armul Performant.** Motorul oficial, baseline-ul 28/6 și primul trial RoadRunner au trecut; la trialul cu Performant, verificarea a detectat un **marker fatal server/plugin** și a oprit comparația. Nu publicăm logul sau valori de performanță dintr-un trial invalid. Concluzia practică este să **nu** înlocuim RoadRunner cu Performant în acest ansamblu; nu pretindem că Performant nu funcționează cu *orice* pachet, fiindcă pe 15/6 a pornit anterior.
2. **[Ablație FerriteCore/ModernFix pe 28/6 — 39711748552](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39711748552): PASS 6/6**, ordine B/F/M/M/F/B, aceeași lume generată cu 80 zombie și 6 pluginuri. Un singur mod eliminat la fiecare braț, memorie de heap *după un GC explicit* la sfârșitul probei, CPU/RSS din fereastra de ~30 s dinaintea GC:

| Braț | Heap folosit post-GC MiB (2 probe) | RSS mediană MiB | CPU s/~30 s | Tick mediu ms |
|---|---:|---:|---:|---:|
| B: toate cele 28 | **322,06 / 319,86** | 1639 / 1605 | **1,08 / 0,87** | 0,22 / 0,24 |
| F: fără FerriteCore | 447,39 / 447,28 | 2098 / 2066 | 0,94 / 0,90 | 0,35 / 0,26 |
| M: fără ModernFix | 345,40 / 344,90 | 1905 / 1651 | 5,11 / 4,98 | 0,32 / 0,32 |

**Ce decid aceste probe:** FerriteCore a redus memoria heap post-GC cu ~125 MiB față de brațul fără el, în acest scenariu; fără ModernFix, CPU-ul măsurat a crescut mult în ambele repetări. Nu le scoatem pentru a fi „mai nativi” doar fiindcă sunt JAR-uri. Sunt diferențe de laborator cu 0 jucători și 2 probe/arm, **nu** dovadă de +N jucători, p95/p99 sau lipsă de risc la condus, voice și 13 pluginuri. „Heap post-GC” și RSS măsoară lucruri diferite, iar performanța exactă depinde de lume/hardware.

## Ce este ales și ce NU se aplică încă

1. **Motor pentru copia de test:** CatServer oficial, nu o fuziune de JAR-uri. Rămâne necesar un build de sursă FunCity verificat pentru orice produs cu brand; atribuirea/licența CatServer rămân vizibile. Nu înlocuim motorul actual de pe PC pe baza laboratorului.
2. **Stackul de lucru:** [cele 28 exacte](FUNCITY-SERVER-TARGET-28.json) sunt selecția provizorie; conținutul RP și dependențele sunt obligatorii până la audit al lumii/clientului. **PC-ul are de fapt 34 moduri/13 pluginuri** ([inventar read-only](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39696088517)), șase moduri suplimentare nu sunt identificate individual public. Nu le ștergem și nu redenumim 28 drept „instalate”.
3. **Filtru pentru nativ/performance-only:** singurul candidat de schimbare este un patch sursă mic pentru un hotspot *măsurat* pe copia completă; fără dublarea unui optimizer deja activ, fără gameplay sau cheltuială RAM/CPU mai mare și cu două runde A/B/B/A plus rollback. După compararea unei lumi pregenerate cu clienți Lite, șoferi, mafiile/pluginurile și voice (p95/p99 tick, heap post-GC, upload/UDP), putem justifica scoaterea câte unei piese sau înlocuirea RoadRunner cu Performant. **În lipsa acestor probe nu promovăm 22, nu tăiem funcții și nu inventăm o limită de jucători.**

**Aceasta este alegerea, nu o promisiune de „maxim”:** baza 28 are dovezi mai bune decât candidatul lean 22 testat; protejăm serverul real și folosim date, nu numărul de JAR-uri, pentru următoarea decizie.
