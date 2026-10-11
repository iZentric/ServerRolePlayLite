# Strategia CUANTIC — RP modat, survival, mafii și oraș

**Stare la 12 octombrie 2026:** există pack-ul Forge 1.16.5 (36 moduri server / 14 pluginuri) și motorul CatServer testat; proba reală a surprins un jucător la trei citiri. Nu există dovadă de capacitate la 25 de jucători, sesiune reprezentativă cu vehicule, FPS pe laptop ieftin sau implementare completă a mafiei. Acest document este o **ordine de lucru**, nu lista unor funcții deja livrate. [Benchmarkul motoarelor](BENCHMARK-MOTOARE-CUANTIC-2026-10-12.md) arată de ce păstrăm JAR-ul live.

## Principii care nu se negociază

1. **Rămâne modpack Forge 1.16.5.** Gameplay-ul și compatibilitatea clientului contează mai mult decât un TPS „record” obținut tăind modurile sau pluginurile. Nu adăugăm moduri performanță la întâmplare.
2. **Nu întrerupem sesiuni active pentru experimente.** Un upgrade cere fereastră liberă, snapshot/restaurare verificată și rollback; rezultatele CI nu sunt automat rezultate live.
3. **Nu promitem „fără nicio problemă”.** În schimb stabilim indicatori, înregistrăm erori și prioritizăm remedierile.
4. **Securitatea înaintea economiei și a facțiunilor.** Dacă serverul acceptă nume fără autentificare, identitatea afișată nu dovedește cine este jucătorul. Nu acordăm bani, OP sau conducerea unei mafii pe baza numelui până când accesul privilegiat este protejat. Alegerea metodei de autentificare care păstrează intrarea simplă aparține proprietarului; nu activăm unilateral o poartă nouă de login.

## Ordinea de implementare

| Prioritate | Ce facem | Criteriu de acceptare | Stare |
|---|---|---|---|
| P0 — siguranță operațională | Verificăm backup-ul și **restaurarea** lumii într-o copie izolată; checksum JAR și configurații; alertă la port căzut, disc insuficient, OOM și excepții de tick. Restrângem permisiunile și documentăm cine poate avea OP. | Restaurare verificată, fără pierderea sesiunii live; procedură scrisă de rollback. | Parțial: probe, supervisor și checksum există; restaurarea nu este dovedită în acest raport. |
| P1 — joc real pe pack-ul normal | Sesiune 15–20 min în oraș cu 1, apoi 2–5 jucători și vehicule. Citiri datate: conectare, TPS/MSPT p95/max, RAM/GC, crash-uri și FPS pe laptop modest. | Login cu clientul normal, deplasare/condus și acțiuni RP fără erori critice în test; nu extrapolăm automat la 25/25. | Baseline cu 1 jucător există, **nu** testul complet cu vehicule. |
| P2 — survival urban | Definim zona de spawn, terenuri, resurse, proprietăți și economie. Folosim întâi pluginurile existente unde se potrivește; evităm grind-ul excesiv și conflictele cu modurile de conținut. | Jucător nou poate intra, câștiga resurse, construi legal și se poate proteja de grief; economie testată și documentată. | Propunere; funcționalitatea completă nu este certificată. |
| P3 — mafii și RP | Regulament public: facțiuni, roluri, conflicte, teritorii, câștiguri, sancțiuni și jurnal pentru moderare. Protecție anti-abuz, fără privilegii OP ascunse. | Două grupuri pot juca un scenariu cap-coadă fără duplicare de bani, grief involuntar sau puteri neautorizate; regulile sunt explicate înainte de lansare. | Propunere, nu o funcție anunțată ca lansată. |
| P4 — optimizare și extindere | Separăm testul **OptiFine + modurile normale** de testul Rubidium/Oculus pe același laptop slab. Orice JAR candidat trece A/B repetabil, apoi login modat și vehicule pe un mediu sigur. | Pentru o sarcină identică: fără regresii la compatibilitate, CPU, p95 și memorie; FPS client documentat pe hardware concret. | Trei patch-uri pierd; al patrulea are rezultat mixt. Niciun upgrade live. |

**Prag de investigare, nu garanție de producție:** într-o probă convenită de 15 minute cu 5 jucători și vehicule, dacă TPS susținut scade sub 19,5, p95 MSPT se apropie de bugetul de 50 ms sau apar erori critice, nu creștem numărul de jucători promiși. Măsurăm și FPS-ul clientului separat; un MSPT bun pe server nu repară FPS-ul laptopului.

## Ce publicăm pe site

- Descărcare directă a **JAR-ului actual**, identic byte-cu-byte cu cel verificat, plus pachetul complet. Nu îl numim „motor nou mai rapid”.
- Benchmark A/B/B/A și limitele lui; versiunile incompatibile nu primesc scor TPS inventat.
- Direcția oraș–survival–mafii marcată ca plan până când scenariile sunt testate.
- Starea serverului cu oră de măsurare și eticheta *ping*, nu prezență garantată în timp real.
