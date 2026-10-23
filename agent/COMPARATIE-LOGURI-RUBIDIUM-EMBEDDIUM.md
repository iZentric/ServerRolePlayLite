# Ultimele loguri client Rubidium vs Embeddium TEST (read-only, 22.10.2026)

Sursă: [auditul PC 39676077697](https://github.com/iZentric/ServerRolePlayLite/actions/runs/39676077697), profilurile Prism `FunCity RP Lite` și `FunCity RP Lite Embeddium TEST`. Scriptul a citit **numai `logs/latest.log`** din fiecare; nicio linie brută, nume, adresă, lume sau fișier de log nu a fost încărcat/afișat. Datele sunt contori și intervale extrase local, nu un benchmark.

| Ce arată ultimul `latest.log` | Lite / Rubidium | TEST / Embeddium |
| --- | ---: | ---: |
| Durata **acoperită de log** (prima–ultima linie cu oră), **nu timpul de încărcare** | 35 s | 52 s |
| Primul mesaj de inițializare audio față de primul mesaj al logului, **nu „meniul gata”** | 25 s | 11 s |
| Primul indiciu textual de **încercare** de conectare | absent | la 43 s |
| Indicii de oprire în log | 1 | 1 |
| Linii `WARN` / `ERROR` / `FATAL` | 625 / 19 / 0 | 619 / 19 / 0 |
| Marcatori de crash/mixin fatal | 0 | 0 |
| `ERROR` cu Rubidium/Embeddium/Oculus în linie | 0 | 0 |
| `WARN` cu Rubidium/Embeddium/Oculus în linie | 3 | 0 |
| Indicii de resurse/model/texturi în WARN/ERROR | 432 | 432 |
| Indicii generice de erori de rețea în WARN/ERROR | 2 | 3 |

**Interpretare corectă:** Niciun log nu arată în aceste categorii un crash fatal sau o eroare atribuită direct rendererului. Ambele au multe mesaje de resurse (432 clasificate identic) și câte 19 linii ERROR; **nu** putem spune „fără probleme” ori atribui toate mesajele unui anumit mod. Markerul Embeddium de la 43 s arată doar o încercare/indiciu de conectare, **nu** dovedește că intrarea în lume ori vocea a reușit. Nu este normal să comparăm 52 cu 35 și să numim unul „pornire mai rapidă”: testul Embeddium conține un indiciu de conectare, iar ultimul log Rubidium nu; niciunul nu furnizează un marker verificabil de «meniu gata» sau FPS per cadru.

**Verdict:** logurile nu arată un avantaj FPS pentru vreun renderer. Proprietarul a spus că performanța „e cam la fel”, fără cifre și fără setări confirmate egale. În lipsa unui câștig clar, **păstrăm Rubidium în Lite-ul funcțional**, iar TEST rămâne opțional separat. Pentru comparație validă trebuie aceeași distanță (ultimul audit găsise Lite 12/Fancy, TEST este 5/Fast), aceeași scenă și metrici FPS/1% low obținute din joc sau un recorder local. Logurile Minecraft nu oferă aceste metrici. Serverul/originalul nu au fost modificate de audit.
