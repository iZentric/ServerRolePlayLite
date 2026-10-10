# ACCEPTANCE CUANTIC — 2026-10-10 16:07:20 UTC (live.log: 866 linii)
[TRECE] T1 proces java + port: java=56931 port25565=1
[TRECE] T2 boot: Done (18.032s) | Dedicated server took 73.468 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 13
      [16:04:38] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
      [16:05:01] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
      [16:05:36] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 30
[VERIFICA] T5 plugini: pe disk: 13 jar; 0 linii de incarcare | esuati: 6
[TRECE] T6 punte console: There are 0 out of maximum 25 players
[TRECE] T7 salvare lume: 'Saved the game'=DA | level.dat mtime 1791648304->1791648458 | regiuni 12->12
[INFO] T8 resurse: disc liber 1361MB (ocupat 74%), MemAvailable 3773MB, RSS java 3997MB, swap 5103MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.
[CADE] T10 /version: niciun raspuns cu Cuantic (Cuantic-Brand plugin neluat sau punta moarta)



SCOR: TRECE=5 VERIFICA=2 CADE=1 din 10 teste
