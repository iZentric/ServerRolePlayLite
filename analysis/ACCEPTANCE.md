# ACCEPTANCE CUANTIC — 2026-10-10 17:09:06 UTC (live.log: 463 linii)
[CADE] T1 proces java + port: java=nil port25565=0
[TRECE] T2 boot: Done (17.307s) | Dedicated server took 94.033 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 3
      	at net.minecraft.server.SessionLockManager$AlreadyLockedException.func_233000_a_(SourceFile:98) ~[?:?]
      [17:07:15] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
      [17:08:35] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 30
[VERIFICA] T5 plugini: pe disk: 14 jar; 0 linii de incarcare | esuati: 2
[CADE] T6 punte console: niciun raspuns la 'list' in 24 s
[VERIFICA] T7 salvare lume: 'Saved the game'=NU | level.dat mtime 1791652085->1791652085 | regiuni 12->12
[INFO] T8 resurse: disc liber 1882MB (ocupat 64%), MemAvailable 7850MB, RSS java ?MB, swap 5099MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.
[VERIFICA] T10 /version: brand apare, dar linia de provenienta lipseste



SCOR: TRECE=2 VERIFICA=4 CADE=2 din 10 teste
