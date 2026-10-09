# Vitezametru CUANTIC — ultima citire 2026-10-09 13:15:50 UTC

_Linii TPS in fisier: NU EXISTA (CatServer tipareste TPS doar in consola panoului — valoarea reala de citit acolo cand intra jucatorii)_

- Can't keep up (intarzieri tick): 0
- Evenimente join/leave: 6
- Linii [ERROR] in log: 0

_Nicun /spark healthreport rulat pe host inca — cand intra lumea, da comanda si raportul apare aici automat la urmatorul tur de cron_

## AUDIT DISC (release vs host — numarul 34 vs 30 = mostenire permisa, deploy nu sterge)
- jar-uri CARE LIPSC de pe host: **30**
    - AI-Improvements-1.16.5-0.5.0.jar
    - Clumps-6.0.0.28.jar
    - FastFurnace-1.16.5-4.5.0.jar
    - FastWorkbench-1.16.5-4.6.2.jar
    - Ksyxis-1.4.6.jar
    - Pizzaland_v68.jar
    - Placebo-1.16.5-4.7.1.jar
    - RoadRunner-mc1.16.5-1.5.2.jar
- extra pe host (straini, nu declanseaza nimic): 34 — mods/AI-Improvements-1.16.5-0.5.0.jar mods/Clumps-6.0.0.28.jar 
- unix_args flaguri: **DIFERA** (host 019710e2 vs release 74ada85d)
- player-idle-timeout=0 pe host
auto-deploy armat: ec2be0adbc80
