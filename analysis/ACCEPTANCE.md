# ACCEPTANCE CUANTIC — 2026-10-10 17:22:41 UTC (live.log: 859 linii)
[TRECE] T1 proces java + port: java=73570 port25565=1
[TRECE] T2 boot: Done (17.307s) | Dedicated server took 94.033 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 10
      [17:21:46] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
      [17:22:16] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
      [17:22:37] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 30
[VERIFICA] T5 plugini: pe disk: 14 jar; activati (Enabling): 13 | esuati: 7
[CADE] T6 punte console: niciun raspuns la 'list' in 18 s
[VERIFICA] T7 salvare lume: 'Saved the game'=NU | level.dat mtime 1791652959->1791652959 | regiuni 12->12
[INFO] T8 resurse: disc liber 1871MB (ocupat 64%), MemAvailable 5348MB, RSS java 2494MB, swap 5103MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.
[TRECE] T10 /version: brand + provenienta upstream confirmate ([17:20:30] [Server thread/INFO]: This server is running CUANTIC version 1.16.5-1d8d6313 (MC: 1.16.5) (Implemen)

SCOR: TRECE=4 VERIFICA=3 CADE=1 INFO=1 N-A=1 (total 10/10 teste, T1-T10)
