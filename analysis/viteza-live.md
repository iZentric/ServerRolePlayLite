# Vitezametru CUANTIC — ultima citire 2026-10-09 16:08:18 UTC

_Linii TPS in fisier: NU EXISTA (CatServer tipareste TPS doar in consola panoului — valoarea reala de citit acolo cand intra jucatorii)_

- Can't keep up (intarzieri tick): 0
- Evenimente join/leave: 6
- Linii [ERROR] in log: 0

_Nicun /spark healthreport rulat pe host inca — cand intra lumea, da comanda si raportul apare aici automat la urmatorul tur de cron_

## AUDIT DISC (release vs host — numarul 34 vs 30 = mostenire permisa, deploy nu sterge)
- jar-uri CARE LIPSC de pe host: **0**
- extra pe host (straini, nu declanseaza nimic): 4 — Ksyxis-1.4.5.jar Modernxl 1.16.5.jar 
- unix_args (flaguri, cu iertare de nume jar): **LA ZI** (e6e16bc1)
- player-idle-timeout=0 pe host
```
33,34c33,34
< -Xms2G
< -Xmx6G
---
> -Xms1G
> -Xmx4G
```
