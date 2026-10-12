# CHK — 2026-10-12 09:54:58 UTC

```
== CHK — 2026-10-12 09:54:01 UTC ==
stare la intrare in CHK: java=NU sup=NU port25565=0 frpc=
ensure-up: supervisor PORNIT (fara RUNNER_TRACKING_ID)
ensure-up: java=DA port25565=0
ensure-up: mover cmd.in->in.fifo PORNIT
dupa ensure-up: java=22897 (RUNNER_TRACKING_ID=0
0) | sup=22783 (RUNNER_TRACKING_ID=0
0) | frpc=22847
uptime: 09:54:30 up 17:44,  0 users,  load average: 1.46, 0.39, 0.24
ss 25565:
  LISTEN 0      4096               *:25565            *:*          
live.log: 6176 linii | Done (14.469s)
log final: [09:54:27] [Server thread/WARN]: To change this, set "online-mode" to "true" in the server.properties file. [09:54:28] [Server thread/INFO]: This server is running CUANTIC version 1.16.5-1d8d6313 (MC: 1.16.5) (Implementing API version 1.16.5-R0.1-SNAPSHOT, For
disc: /dev/sdb1       5.0G  3.4G  1.7G  67% /home/mndvasi9
fisiere: ADRESA banned-ips.json banned-players.json bind.log boot.log bore.log bukkit.yml bukkit.yml.bak.1791636852 bukkit.yml.bak.1791639103 CatServer-1.16.5-1d8d6313-server.jar catserver.yml chat.log cin CIT
pack marcat: .pack=CUANTIC-Server-CatServer-1.7.7.zip | .pack.new=1.7.7
=== INVENTAR COMPLET FISIERE SERVER LIVE (/home/mndvasi9/cuantic-live) ===
--- 1. MODURI (/home/mndvasi9/cuantic-live/mods: 36 jar-uri) ---
  additional-guns-0.7.1-1.16.5.jar 97K
  AI-Improvements-1.16.5-0.5.0.jar 28K
  bwncr-1.16.5-3.10.16.jar 11K
  cfm-7.0.0pre22-1.16.3.jar 977K
  cgm-1.2.6-1.16.5.jar 662K
  Clumps-6.0.0.28.jar 18K
  connectivity-2.4-1.16.5.jar 52K
  emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar 340K
  FastFurnace-1.16.5-4.5.0.jar 5.8K
  FastSuite-1.16.4-1.1.1.jar 11K
  FastWorkbench-1.16.5-4.6.2.jar 22K
  ferritecore-2.1.1-forge.jar 99K
  getittogetherdrops-1.16.5-v1.2.jar 7.7K
  incontrol-1.16-5.2.12.jar 203K
  Ksyxis-1.4.6.jar    24K
  lazydfu-0.1.3.jar   15K
  letmedespawn-forge-1.16-1.0.2a.jar 76K
  mapperbase-1.16.5-2.4.0.0.jar 160K
  memoryleakfix-forge-pre1.17-1.1.5.jar 221K
  modernfix-forge-5.18.0+mc1.16.5.jar 847K
  modernlife-1.16.5-1.15.jar 961K
  Modernxl            6.5M
  obfuscate-0.6.3-1.16.5.jar 140K
  pamhc2foodcore-1.16.3-1.0.2.jar 114K
  Pizzaland_v68.jar   1.6M
  Placebo-1.16.5-4.7.1.jar 150K
  player-animation-lib-forge-0.4.0+1.16.5.jar 158K
  RoadRunner-mc1.16.5-1.5.2.jar 385K
  roadstuff-1.16.5-4.3.0.jar 1.5M
  selene-1.16.5-1.9.0.jar 113K
  smoothchunk1.16.5-2.0.jar 14K
  spark-1.9.1-forge.jar 3.1M
  SpawnerFix-1.16.2-1.0.0.3.jar 62K
  supplementaries-1.16.5-0.18.4b.jar 2.6M
  vehicle-mod-0.45.2-1.16.5 1001K
  voicechat-forge-1.16.5-2.3.23.jar 7.5M
--- 2. PLUGINURI (/home/mndvasi9/cuantic-live/plugins: 14 jar-uri) ---
  Chunky-1.2.217.jar 217K
  claimchunk-0.0.22.jar 161K
  Cuantic-Brand-1.7.7.jar 4.7K
  EssentialsX-2.19.7.jar 2.9M
  EssentialsXAntiBuild-2.19.7.jar 18K
  EssentialsXChat-2.19.7.jar 27K
  EssentialsXProtect-2.19.7.jar 26K
  EssentialsXSpawn-2.19.7.jar 18K
  LuckPerms-Bukkit-5.5.71.jar 1.5M
  ProtocolLib.jar  4.8M
  SkinsRestorer.jar 7.7M
  Vault.jar        266K
  worldedit-bukkit-7.2.5-dist.jar 4.2M
  worldguard-bukkit-7.0.5-dist.jar 1.1M
--- 3. CONFIG & DEFAULTCONFIGS ---
  [OK] config/modernfix-mixins.properties (5336 bytes): mixin.perf.dynamic_resources=true mixin.perf.faster_item_rendering=true 
  [OK] config/incontrol/spawn.json (58 bytes): [   {"hostile": true, "maxcount": 50, "result": "deny"} ] 
  [OK] config/forge-common.toml (303 bytes):  [general] 	#Defines a default world type to use. The vanilla default world type is represented by 'default'. 	#The modd
  [OK] config/smoothchunk-common.toml (298 bytes):  ["Config category"] 	#Delay before a chunk is saved to disk, default: 300 seconds. If you enable the noSaveAll config, 
  [OK] defaultconfigs/forge-server.toml (183 bytes): [server]     removeErroringEntities = true     removeErroringTileEntities = true 
--- 4. STRATURI TUNING & ROOT (/home/mndvasi9/cuantic-live) ---
  [OK] CatServer-1.16.5-1d8d6313-server.jar (30887 linii, 8009910 bytes)
  [OK] unix_args.txt (39 linii, 1064 bytes)
  [OK] server.properties (52 linii, 1197 bytes)
  [OK] spigot.yml (161 linii, 4285 bytes)
  [OK] bukkit.yml (42 linii, 1160 bytes)
  [OK] catserver.yml (17 linii, 459 bytes)
  [OK] commands.yml (25 linii, 697 bytes)
  [OK] eula.txt (1 linii, 10 bytes)
  [OK] ops.json (7 linii, 136 bytes)
  [OK] manifest-cuantic.json (65 linii, 1893 bytes)
unix_args complet (39 linii): -Xms1024M -Xmx6144M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=37 -XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=23 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=20 -XX:G1MixedGCCountTarget=3 -XX:InitiatingHeapOccupancyPercent=10 -XX:G1RSetUpdatingPauseTimePercent=0 -XX:SurvivorRatio=32 -XX:MaxTenuringThreshold=1 -XX:G1SATBBufferEnqueueingThresholdPercent=30 -XX:G1ConcMarkStepDurationMillis=5.0 -XX:G1ConcRSHotCardLimit=16 -XX:G1ConcRefinementServiceIntervalMillis=150 -XX:GCTimeRatio=99 -XX:+PerfDisableSharedMem -XX:+UseStringDeduplication -XX:+UseFastUnorderedTimeStamps -XX:NmethodSweepActivity=1 -XX:ReservedCodeCacheSize=256M -XX:NonNMethodCodeHeapSize=12M -XX:ProfiledCodeHeapSize=122M -XX:NonProfiledCodeHeapSize=122M -XX:-DontCompileHugeMethods -XX:MaxNodeLimit=240000 -XX:NodeLimitFudgeFactor=8000 -XX:AllocatePrefetchStyle=3 -Dio.netty.allocator.maxOrder=9 -Dio.netty.leakDetection.level=DISABLED -jar CatServer-1.16.5-1d8d6313-server.jar nogui 
erori-cheie: [21:55:53] [Server thread/INFO]: Done (14.086s)! For help, type "help"|[07:26:48] [Server thread/INFO]: Done (12.685s)! For help, type "help"|[16:53:59] [Server thread/INFO]: Done (11.861s)! For help, type "help"|[21:00:26] [Server thread/INFO]: Done (11.125s)! For help, type "help"|[22:15:42] [Server thread/INFO]: Done (10.936s)! For help, type "help"|
=== ISTORIC PORNIRI / OPRIRI / JUCATORI (live.log) ===
5633:[21:44:31] [Server thread/INFO]: iZentric issued server command: /spark ping
5634:[21:45:58] [Server thread/INFO]: iZentric issued server command: /tps
5635:[21:47:45] [Server thread/INFO]: iZentric issued server command: /tps
5636:[21:47:46] [Server thread/INFO]: iZentric issued server command: /pl
5637:[21:47:56] [Server thread/INFO]: iZentric issued server command: /tps
5638:[21:48:19] [Server thread/INFO]: iZentric issued server command: /tps
5639:[21:51:40] [Server thread/INFO]: iZentric issued server command: /tps
5640:[21:57:01] [Server thread/INFO]: iZentric lost connection: Timed out
5641:[21:57:01] [Server thread/INFO]: Disconnecting client iZentric
5642:[21:57:01] [Server thread/INFO]: iZentric left the game
5644:[22:02:18] [User Authenticator #2/INFO]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270
5646:[22:02:20] [Server thread/INFO]: iZentric[/127.0.0.1:39058] logged in with entity id 6877 at (1128.2466181762993, 69.0, -865.1362920923776)
5647:[22:02:20] [Server thread/WARN]: Playerfile not found (iZentric - 0e2f8d53-21b4-32a4-a498-0967ed108270)
5648:[22:02:20] [Server thread/INFO]: Received secret request of iZentric (15)
5649:[22:02:20] [Server thread/INFO]: Sent secret to iZentric
5650:==== pornire 2026-10-11 22:14:44 UTC (memorie: -Xmx6144M, java: /home/mndvasi9/.local/jdk17/bin/java) ====
5872:[22:15:35] [Server thread/INFO]: [Cuantic] Motor hibrid activ: Cuantic 1.7.7 (MC 1.16.5, API 1.16.5-R0.1-SNAPSHOT, motor CUANTIC) | based on: 1.16.5-1d8d6313 (MC: 1.16.5) | runtime-tech: keepSpawnInMemory=false, enableSkipEntityTick=true, enableSkipTileEntityTick=true, maxEntityCollision=2, worldGenMaxTickTime=8, disableFMLStatusModInfo=true, enableDynmapCompatible=false, enableMythicMobsPatcherCompatible=false, defaultInstallPluginSpark=false, versionCheck=false, forceSaveOnWatchdog=true, noHopperEvent=3w, autoUnloadDims=[-1,1], disableStatSaving=true, saveUserCacheOnStopOnly=true, logVillagerDeaths=false, movedWronglyThreshold=0.35, movedTooQuicklyMultiplier=25.0
5921:[22:15:42] [Server thread/INFO]: Done (10.936s)! For help, type "help"
5994:[22:21:48] [User Authenticator #1/INFO]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270
5996:[22:21:50] [Server thread/INFO]: iZentric[/127.0.0.1:39850] logged in with entity id 1 at (1128.2466181762993, 69.0, -865.1362920923776)
5997:[22:21:51] [Server thread/WARN]: Playerfile not found (iZentric - 0e2f8d53-21b4-32a4-a498-0967ed108270)
5998:[22:21:51] [Server thread/INFO]: Received secret request of iZentric (15)
5999:[22:21:51] [Server thread/INFO]: Sent secret to iZentric
6000:[22:21:51] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 39.356720ms. Summary: Getting prefix for iZentric
6001:[22:22:08] [Server thread/INFO]: iZentric issued server command: /tps
6002:[22:23:24] [Server thread/INFO]: iZentric issued server command: /tps
6003:[22:26:10] [Server thread/INFO]: iZentric issued server command: /tps
6004:[22:28:38] [Server thread/INFO]: iZentric issued server command: /tps
6005:[22:29:53] [Server thread/INFO]: iZentric issued server command: /tps
6006:[22:30:02] [Server thread/INFO]: iZentric issued server command: /tps
6007:[22:30:32] [Server thread/INFO]: iZentric issued server command: /tps
6008:[22:30:40] [Server thread/INFO]: iZentric issued server command: /tp
6009:[22:30:47] [Server thread/INFO]: iZentric issued server command: /tps
6010:[22:31:41] [Server thread/INFO]: iZentric issued server command: /tps
6011:[22:31:43] [Server thread/INFO]: iZentric issued server command: /spark ping
6012:[22:33:30] [Server thread/INFO]: iZentric issued server command: /tps
6013:[22:34:32] [Server thread/INFO]: iZentric issued server command: /tps
6014:[22:35:19] [Server thread/INFO]: iZentric issued server command: /tps
6015:[22:35:36] [Server thread/INFO]: iZentric issued server command: /tps
6016:[23:12:55] [Server thread/INFO]: iZentric issued server command: /tps
6017:[23:42:15] [Server thread/INFO]: iZentric issued server command: /tps
6018:[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
6019:[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
6020:[00:14:29] [Server thread/INFO]: iZentric issued server command: /tps
6021:==== pornire 2026-10-12 09:54:02 UTC (memorie: -Xmx6144M, java: /home/mndvasi9/.local/jdk17/bin/java) ====
=== ULTIMELE 60 LINII DIN live.log ===
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:schneemobil from classpath:/assets/vehicle/vehicles/schneemobil.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:couch_rainbow from classpath:/assets/vehicle/vehicles/couch_rainbow.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:luxuswagen from classpath:/assets/vehicle/vehicles/luxuswagen.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:moped from classpath:/assets/vehicle/vehicles/moped.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:fertilizer from classpath:/assets/vehicle/vehicles/fertilizer.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:mini_bike from classpath:/assets/vehicle/vehicles/mini_bike.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:police_car from classpath:/assets/vehicle/vehicles/police_car.json
[09:54:22] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:dirt_bike from classpath:/assets/vehicle/vehicles/dirt_bike.json
[09:54:22] [Thread-0/INFO]: Please use /mfsrc to reload any changed mod config files
[09:54:22] [modloading-worker-0/INFO]: 12 Karten erfolgreich geladen.
[09:54:23] [main/WARN]: Method overwrite conflict for func_225532_a_ in modernfix-common.mixins.json:perf.biome_zoomer.FuzzyOffsetBiomeZoomerMixin, previously written by me.jellysquid.mods.lithium.mixin.gen.voronoi_biomes.VoronoiBiomeAccessTypeMixin. Skipping method.
[09:54:23] [main/INFO]: Environment: authHost='https://authserver.mojang.com', accountsHost='https://api.mojang.com', sessionHost='https://sessionserver.mojang.com', servicesHost='https://api.minecraftservices.com', name='PROD'
[09:54:24] [main/INFO]: Reloading ResourceManager: Default, Modernxl 1.16.5.jar, voicechat-forge-1.16.5-2.3.23.jar, getittogetherdrops-1.16.5-v1.2.jar, cgm-1.2.6-1.16.5.jar, player-animation-lib-forge-0.4.0+1.16.5.jar, incontrol-1.16-5.2.12.jar, spark-1.9.1-forge.jar, pamhc2foodcore-1.16.3-1.0.2.jar, Clumps-6.0.0.28.jar, FastWorkbench-1.16.5-4.6.2.jar, RoadRunner-mc1.16.5-1.5.2.jar, Placebo-1.16.5-4.7.1.jar, modernlife-1.16.5-1.15.jar, modernfix-forge-5.18.0+mc1.16.5.jar, additional-guns-0.7.1-1.16.5.jar, obfuscate-0.6.3-1.16.5.jar, vehicle-mod-0.45.2-1.16.5 (1).jar, lazydfu-0.1.3.jar, FastFurnace-1.16.5-4.5.0.jar, cfm-7.0.0pre22-1.16.3.jar, mapperbase-1.16.5-2.4.0.0.jar, roadstuff-1.16.5-4.3.0.jar, ferritecore-2.1.1-forge.jar, AI-Improvements-1.16.5-0.5.0.jar, memoryleakfix-forge-pre1.17-1.1.5.jar, bwncr-1.16.5-3.10.16.jar, forge-1.16.5-36.2.39-universal.jar, supplementaries-1.16.5-0.18.4b.jar, Pizzaland_v68.jar, emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar, selene-1.16.5-1.9.0.jar, bukkit, smoothchunk1.16.5-2.0.jar, Ksyxis-1.4.6.jar, SpawnerFix-1.16.2-1.0.0.3.jar, FastSuite-1.16.4-1.1.1.jar, letmedespawn-forge-1.16-1.0.2a.jar, connectivity-2.4-1.16.5.jar
[09:54:24] [main/INFO]: Invalidating pack caches
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:candelabra_silver as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/blackboard_clear as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_clear as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:blackstone_tile_vertical_slab as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:firefly_jar_tf as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:deepslate_lamp as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_dye as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:stone_tile_vertical_slab as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich_soul as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:copper_lantern_2 as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:checker_vertical_slab as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:candelabra_silver as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/blackboard_clear as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_clear as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:blackstone_tile_vertical_slab as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:firefly_jar_tf as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:deepslate_lamp as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_dye as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:stone_tile_vertical_slab as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich_soul as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:copper_lantern_2 as it's serializer returned null
[09:54:25] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:checker_vertical_slab as it's serializer returned null
[09:54:26] [Worker-Main-1/INFO]: Registered 0 additional loot tables.
[09:54:26] [Worker-Main-1/INFO]: Loaded 1861 advancements
[09:54:26] [Worker-Main-1/INFO]: Registered 0 additional recipes.
[09:54:26] [Worker-Main-1/INFO]: Successfully processed 2391 recipes into the AuxRecipeManager.
[09:54:27] [Server thread/INFO]: Starting minecraft server version 1.16.5
[09:54:27] [Server thread/INFO]: Loading properties
[09:54:27] [Server thread/INFO]: Default game type: SURVIVAL
[09:54:27] [Server thread/INFO]: Generating keypair
[09:54:27] [Server thread/INFO]: Starting Minecraft server on *:25565
[09:54:27] [Server thread/INFO]: Using default channel type
[09:54:27] [Server thread/WARN]: **** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!
[09:54:27] [Server thread/WARN]: The server will make no attempt to authenticate usernames. Beware.
[09:54:27] [Server thread/WARN]: While this makes the game possible to play without internet access, it also opens up the ability for hackers to connect with any username they choose.
[09:54:27] [Server thread/WARN]: To change this, set "online-mode" to "true" in the server.properties file.
[09:54:28] [Server thread/INFO]: This server is running CUANTIC version 1.16.5-1d8d6313 (MC: 1.16.5) (Implementing API version 1.16.5-R0.1-SNAPSHOT, Forge version 36.2.39)
[09:54:30] [Server thread/INFO]: Debug logging is enabled
[09:54:30] [Server thread/INFO]: Using 2 threads for Netty based IO
[09:54:30] [Server thread/INFO]: Server Ping Player Sample Count: 12
=== ULTIMELE 35 LINII DIN sup.log ===
[0m 00:13:02 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:13:17 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:13:32 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:13:47 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:14:02 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:14:18 mc=DA port=SUS log=6019
 log blocat:
[00:11:36] [Server thread/INFO]: iZentric issued server command: /tps
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[0m 00:14:33 mc=DA port=SUS log=6020
 00:14:48 mc=DA port=SUS log=6020
 log blocat:
[00:11:37] [Server thread/INFO]: iZentric issued server command: /pl
[00:14:29] [Server thread/INFO]: iZentric issued server command: /tps
[0mRULEAZA: pack CUANTIC-Server-CatServer-1.7.7.zip, java openjdk version "17.0.20.1" 2026-08-18
JAVA: /home/mndvasi9/.local/jdk17/bin/java -> openjdk version "17.0.20.1" 2026-08-18
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 39 linii)
MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus).
 09:54:02 mc=DA port=nu asculta log=6021
 09:54:17 mc=DA port=nu asculta log=6055
=== CRASH REPORTS ===
=== DMESG OOM ===
sup.log: JAVA: /home/mndvasi9/.local/jdk17/bin/java -> openjdk version "17.0.20.1" 2026-08-18|args: OK (CatServer-1.16.5-1d8d6313-server.jar, 39 linii)|MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus).| 09:54:02 mc=DA port
frpc.toml: 10
adresa din fisier: 92.5.171.150:25565
  dinafara 1: "online":false |  |  "message":"Unknown problem with returned server data."
  dinafara 2: "online":false |  |  "message":"Unknown problem with returned server data."
  dinafara 3: "online":false |  |  "message":"Unknown problem with returned server data."
```
