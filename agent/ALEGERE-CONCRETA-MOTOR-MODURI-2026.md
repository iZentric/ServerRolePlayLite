# Alegerea concretă FunCity RP 1.16.5 — native-first, după testul lean (22.10.2026)

**Aleg acum:** **CatServer oficial 23.05.26-1, cu ținta existentă de 28 moduri client-aligned / șase pluginuri în laborator**, drept baza cea mai defensabilă pentru **următorul test privat**, nu un nou instalator pe PC. RoadRunner rămâne **singur** (nu cu Performant); Ksyxis rămâne în țintă cât timp funcțiile zonei spawn nu sunt afectate; ModernFix/FerriteCore rămân provizoriu până la probă specifică de memorie. Păstrăm armele, vehiculele, vocea, blocurile, biblioteca lor, InControl și Connectivity până la verificarea funcției. Nu adăugăm Chunk Sending ori alte JAR-uri noi. Configurația propusă cu 22 **nu** devine înlocuitorul celor 28: [lista exactă de comparație](FUNCITY-SERVER-LEAN-22.json) rămâne numai un braț experimental de CI.

## Test nou: 28 față de 22, nu doar păreri

Am încercat să scot din **copia izolată** AI Improvements, FastSuite + FastWorkbench + Placebo ca **grup dependent**, Get It Together, Drops! și LazyDFU. [Rularea GitHub **39710079801 — PASS**](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39710079801) a folosit același CatServer oficial/Java 17, același world generat copiat înainte de fiecare probă, 80 zombie, aceleași șase pluginuri, ordine **F/L/L/F** (F=28, L=22), verificare SHA/metadata/dependențe/inventar, patru opriri curate.

| Braț, două observații brute | Boot până la `Done` | CPU s/~30 s | RSS MiB | `forge tps` tick mediu ms |
|---|---:|---:|---:|---:|
| **F: 28 moduri intacte** | **28,55 / 31,06 s** | 1,51 / 1,85 | 2034 / 1623 | 0,25 / 0,52 |
| **L: 22 moduri** | **44,35 / 44,60 s** | 2,01 / 1,53 | 1988 / 1648 | 0,66 / 0,47 |

**Verdict de laborator:** brațul 22 a pornit, dar **a pierdut ~13–16 s la boot în ambele probe**, fără reducere repetabilă de CPU, RSS sau tick. Nu avem motiv să promovăm 22 ca „mai rapid”: șase JAR-uri mai puțin ≠ capacitate mai mare. Lipsa LazyDFU poate explica o parte din costul de boot, dar testul a eliminat șase moduri simultan, deci **nu izolăm cauza** din acest A/B. Aceasta nu demonstrează că toate cele șase optimizatoare cresc numărul de jucători ori că 22 este mai rău sub trafic real; niciunul dintre brațe nu are clienți, crafting, condus sau cele 13 pluginuri.

**Restul dovezilor:** [ablația Ksyxis 28/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39706471206) a arătat avantaj în lumea generată fără jucători, dar poate modifica zona spawn. [RoadRunner versus Performant 15/6](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39706471113) a dat CPU mai mic RoadRunner, tick mediu mai mic Performant, fără RP real. [Sarcina cu 16 mașini](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39708297969) a eșuat validarea 16 la început/0 la sfârșit; **nu** susține o alegere de motor sau player capacity. Nu numim FerriteCore/ModernFix „dovedite” individual pe lumea RP doar fiindcă sunt în baseline. Forkul sursă branduit [39699780017](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39699780017) este anulat, fără JAR FunCity nou validat.

## Ce este ales și ce NU se aplică încă

1. **Motor pentru copia de test:** CatServer oficial, nu o fuziune de JAR-uri. Rămâne necesar un build de sursă FunCity verificat pentru orice produs cu brand; atribuirea/licența CatServer rămân vizibile. Nu înlocuim motorul actual de pe PC pe baza laboratorului.
2. **Stackul de lucru:** [cele 28 exacte](FUNCITY-SERVER-TARGET-28.json) sunt selecția provizorie; conținutul RP și dependențele sunt obligatorii până la audit al lumii/clientului. **PC-ul are de fapt 34 moduri/13 pluginuri** ([inventar read-only](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39696088517)), șase moduri suplimentare nu sunt identificate individual public. Nu le ștergem și nu redenumim 28 drept „instalate”.
3. **Filtru pentru nativ/performance-only:** singurul candidat de schimbare este un patch sursă mic pentru un hotspot *măsurat* pe copia completă; fără dublarea unui optimizer deja activ, fără gameplay sau cheltuială RAM/CPU mai mare și cu două runde A/B/B/A plus rollback. După compararea unei lumi pregenerate cu clienți Lite, șoferi, mafiile/pluginurile și voice (p95/p99 tick, heap post-GC, upload/UDP), putem justifica scoaterea câte unei piese sau înlocuirea RoadRunner cu Performant. **În lipsa acestor probe nu promovăm 22, nu tăiem funcții și nu inventăm o limită de jucători.**

**Aceasta este alegerea, nu o promisiune de „maxim”:** baza 28 are dovezi mai bune decât candidatul lean 22 testat; protejăm serverul real și folosim date, nu numărul de JAR-uri, pentru următoarea decizie.
