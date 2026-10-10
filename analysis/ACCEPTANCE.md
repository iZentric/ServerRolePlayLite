# ACCEPTANCE CUANTIC — 2026-10-10 11:18:16 UTC (live.log: 409 linii)
[TRECE] T1 proces java + port: java=5900 port25565=1
[TRECE] T2 boot: Done (13.664s) | Dedicated server took 96.788 seconds
[VERIFICA] T3 erori in log (ultimele 4000 linii, filtering pe cunoscute-nevinovate): 3
      	at net.minecraft.server.SessionLockManager$AlreadyLockedException.func_233000_a_(SourceFile:98) ~[?:?]
      	at net.minecraftforge.fml.loading.FMLServerLaunchProvider.lambda$launchService$0(FMLServerLaunchProvider.java:51)[11:03:44] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
      [11:04:18] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
[TRECE] T4 handshake cu clientul: semne de kick pe lista de moduri = 0 | moduri pe server: 32
[VERIFICA] T5 plugini: niciun rand 'This server is running' | esuati: 1
[TRECE] T6 punte console: There are 1 out of maximum 25 players
[TRECE] T7 salvare lume: 'Saved the game'=DA | level.dat mtime 1791630868->1791631123 | regiuni 12->12
[INFO] T8 resurse: disc liber 1913MB (ocupat 63%), MemAvailable 4194MB, RSS java 3732MB, swap 5111MB liber
[N-A] T9 testate DOAR din server. Lipsesc cu client real: latența clientului (ping real de pe scaunul
      lui), desync/rubberband vizual, dublagi de itemi, interactiuni cu moduri de client,
      jucatori multi. Acestea se raporteaza de la client, nu de aici - nu le declara trecute.

SCOR: TRECE=5 VERIFICA=2 CADE=0 din 9 teste
