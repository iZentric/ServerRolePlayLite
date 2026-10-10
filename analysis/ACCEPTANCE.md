# ACCEPTANCE CUANTIC — 2026-10-10 16:30:51 UTC (live.log: 295 linii)
[CADE] T1 proces java + port: java=nil port25565=0
[TRECE] T2 boot: Done (14.901s) | Dedicated server took 64.366 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 3
      [16:29:18] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
      [16:29:38] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
      [16:30:06] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 30
[VERIFICA] T5 plugini: pe disk: 13 jar; 0 linii de incarcare | esuati: 1
[CADE] T6 punte console: niciun raspuns la 'list' in 24 s
[VERIFICA] T7 salvare lume: 'Saved the game'=NU | level.dat mtime 1791649780->1791649780 | regiuni 12->12
[INFO] T8 resurse: disc liber 1298MB (ocupat 75%), MemAvailable 7815MB, RSS java ?MB, swap 5103MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.
[VERIFICA] T10 /version: brand apare, dar linia de provenienta lipseste



SCOR: TRECE=2 VERIFICA=4 CADE=2 din 10 teste
