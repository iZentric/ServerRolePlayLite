# CHK — 2026-10-12 15:04:23 UTC

```
== CHK — 2026-10-12 15:03:25 UTC ==
stare la intrare in CHK: java=NU sup=NU port25565=0 frpc=
ensure-up: supervisor PORNIT (fara RUNNER_TRACKING_ID)
ensure-up: java=DA port25565=0
ensure-up: mover cmd.in->in.fifo PORNIT
dupa ensure-up: java=38256 (RUNNER_TRACKING_ID=0
0) | sup=38143 (RUNNER_TRACKING_ID=0
0) | frpc=38207
uptime: 15:03:54 up 22:53,  0 users,  load average: 1.50, 0.54, 0.34
ss 25565:
  LISTEN 0      4096               *:25565            *:*          
live.log: 756 linii | Done (11.827s)
log final: [15:03:52] [Server thread/WARN]: While this makes the game possible to play without internet access, it also opens up the ability for hackers to connect with any username they choose. [15:03:52] [Server thread/WARN]: To change this, set "online-mode" to "true"
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
erori-cheie: [10:16:55] [Server thread/INFO]: Done (11.827s)! For help, type "help"|
=== ISTORIC PORNIRI / OPRIRI / JUCATORI (live.log) ===
307:[10:17:10] [Server thread/WARN]: Playerfile not found (iZentric - 0e2f8d53-21b4-32a4-a498-0967ed108270)
308:[10:17:11] [Server thread/INFO]: Received secret request of iZentric (15)
309:[10:17:11] [Server thread/INFO]: Sent secret to iZentric
310:[10:17:11] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 68.365124ms. Summary: Getting prefix for iZentric
314:[10:17:30] [Server thread/INFO]: default: iZentric
319:[10:17:30] [Server thread/INFO]: default: iZentric
326:[10:17:31] [Server thread/INFO]: default: iZentric
327:[10:17:38] [Server thread/INFO]: iZentric issued server command: /deop iZentric
328:[10:17:38] [Server thread/INFO]: [iZentric: Made iZentric no longer a server operator]
329:[10:17:40] [Server thread/INFO]: iZentric issued server command: /op iZentric
330:[10:17:40] [Server thread/INFO]: [Cuantic/OP] Operator acordat automat pentru iZentric
332:[10:17:43] [Server thread/INFO]: iZentric issued server command: /tps
335:[10:18:00] [Server thread/INFO]: default: iZentric
338:[10:18:01] [Server thread/INFO]: default: iZentric
483:[10:18:56] [Server thread/INFO]: default: iZentric
486:[10:18:56] [Server thread/INFO]: default: iZentric
499:[10:19:02] [Server thread/INFO]: default: iZentric
531:[10:20:22] [Server thread/INFO]: default: iZentric
534:[10:20:22] [Server thread/INFO]: default: iZentric
563:[10:20:33] [Server thread/INFO]: default: iZentric
577:[10:25:03] [Server thread/INFO]: iZentric issued server command: /tps
578:[10:27:37] [Server thread/INFO]: iZentric issued server command: /tps
579:[10:27:38] [Server thread/INFO]: iZentric issued server command: /tps
580:[10:32:25] [Server thread/INFO]: iZentric issued server command: /tp
581:[10:32:26] [Server thread/INFO]: iZentric issued server command: /tps
582:[10:32:38] [Server thread/INFO]: iZentric issued server command: /tps
583:[10:32:40] [Server thread/INFO]: iZentric issued server command: /pl
584:[10:33:31] [Server thread/INFO]: iZentric issued server command: /tps
585:[10:35:44] [Server thread/INFO]: iZentric issued server command: /tps
586:[10:36:45] [Server thread/INFO]: iZentric issued server command: /tps
587:[10:36:46] [Server thread/INFO]: iZentric issued server command: /plw
588:[10:38:34] [Server thread/INFO]: iZentric issued server command: /tps
589:[10:39:11] [Server thread/INFO]: iZentric issued server command: /tps
590:[10:39:12] [Server thread/INFO]: iZentric issued server command: /plw
591:[10:50:43] [Server thread/INFO]: iZentric issued server command: /tps
592:[10:55:26] [Server thread/INFO]: iZentric issued server command: /tps
593:[11:18:16] [Server thread/INFO]: iZentric issued server command: /tps
594:[11:19:49] [Server thread/INFO]: iZentric issued server command: /tps
595:[11:20:40] [Server thread/INFO]: iZentric issued server command: /tps
596:[11:25:07] [Server thread/INFO]: iZentric issued server command: /tps
597:[11:26:27] [Server thread/INFO]: iZentric issued server command: /tps
598:[11:27:18] [Server thread/INFO]: iZentric issued server command: /tps
599:[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
600:[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
601:==== pornire 2026-10-12 15:03:26 UTC (memorie: -Xmx6144M, java: /home/mndvasi9/.local/jdk17/bin/java) ====
=== ULTIMELE 60 LINII DIN live.log ===
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:basilico_gt from classpath:/assets/vehicle/vehicles/basilico_gt.json
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:angel_car from classpath:/assets/vehicle/vehicles/angel_car.json
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:hello_cat from classpath:/assets/vehicle/vehicles/hello_cat.json
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:dirt_bike from classpath:/assets/vehicle/vehicles/dirt_bike.json
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:vehicle_trailer from classpath:/assets/vehicle/vehicles/vehicle_trailer.json
[15:03:46] [modloading-worker-0/INFO]: Loaded vehicle properties for vehicle:couch from classpath:/assets/vehicle/vehicles/couch.json
[15:03:46] [modloading-worker-0/INFO]: Mapper Base setup started!
[15:03:46] [modloading-worker-0/INFO]: RoadStuff setup started!
[15:03:46] [modloading-worker-0/INFO]: 12 Karten erfolgreich geladen.
[15:03:47] [Thread-0/INFO]: Please use /mfsrc to reload any changed mod config files
[15:03:47] [main/WARN]: Method overwrite conflict for func_225532_a_ in modernfix-common.mixins.json:perf.biome_zoomer.FuzzyOffsetBiomeZoomerMixin, previously written by me.jellysquid.mods.lithium.mixin.gen.voronoi_biomes.VoronoiBiomeAccessTypeMixin. Skipping method.
[15:03:47] [main/INFO]: Environment: authHost='https://authserver.mojang.com', accountsHost='https://api.mojang.com', sessionHost='https://sessionserver.mojang.com', servicesHost='https://api.minecraftservices.com', name='PROD'
[15:03:48] [main/INFO]: Reloading ResourceManager: Default, Modernxl 1.16.5.jar, voicechat-forge-1.16.5-2.3.23.jar, getittogetherdrops-1.16.5-v1.2.jar, cgm-1.2.6-1.16.5.jar, player-animation-lib-forge-0.4.0+1.16.5.jar, incontrol-1.16-5.2.12.jar, spark-1.9.1-forge.jar, pamhc2foodcore-1.16.3-1.0.2.jar, Clumps-6.0.0.28.jar, FastWorkbench-1.16.5-4.6.2.jar, RoadRunner-mc1.16.5-1.5.2.jar, Placebo-1.16.5-4.7.1.jar, modernlife-1.16.5-1.15.jar, modernfix-forge-5.18.0+mc1.16.5.jar, additional-guns-0.7.1-1.16.5.jar, obfuscate-0.6.3-1.16.5.jar, vehicle-mod-0.45.2-1.16.5 (1).jar, lazydfu-0.1.3.jar, FastFurnace-1.16.5-4.5.0.jar, cfm-7.0.0pre22-1.16.3.jar, mapperbase-1.16.5-2.4.0.0.jar, roadstuff-1.16.5-4.3.0.jar, ferritecore-2.1.1-forge.jar, AI-Improvements-1.16.5-0.5.0.jar, memoryleakfix-forge-pre1.17-1.1.5.jar, bwncr-1.16.5-3.10.16.jar, forge-1.16.5-36.2.39-universal.jar, supplementaries-1.16.5-0.18.4b.jar, Pizzaland_v68.jar, emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar, selene-1.16.5-1.9.0.jar, bukkit, smoothchunk1.16.5-2.0.jar, Ksyxis-1.4.6.jar, SpawnerFix-1.16.2-1.0.0.3.jar, FastSuite-1.16.4-1.1.1.jar, letmedespawn-forge-1.16-1.0.2a.jar, connectivity-2.4-1.16.5.jar
[15:03:48] [main/INFO]: Invalidating pack caches
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:candelabra_silver as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/blackboard_clear as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_clear as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:blackstone_tile_vertical_slab as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:firefly_jar_tf as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:deepslate_lamp as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_dye as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:stone_tile_vertical_slab as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich_soul as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:copper_lantern_2 as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:checker_vertical_slab as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:candelabra_silver as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/blackboard_clear as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_clear as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:blackstone_tile_vertical_slab as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:firefly_jar_tf as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:deepslate_lamp as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:inspirations/flag_dye as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:stone_tile_vertical_slab as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:planter_rich_soul as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:copper_lantern_2 as it's serializer returned null
[15:03:50] [Worker-Main-1/INFO]: Skipping loading recipe supplementaries:checker_vertical_slab as it's serializer returned null
[15:03:51] [Worker-Main-1/INFO]: Registered 0 additional loot tables.
[15:03:51] [Worker-Main-1/INFO]: Loaded 1861 advancements
[15:03:51] [Worker-Main-1/INFO]: Registered 0 additional recipes.
[15:03:51] [Worker-Main-1/INFO]: Successfully processed 2391 recipes into the AuxRecipeManager.
[15:03:52] [Server thread/INFO]: Starting minecraft server version 1.16.5
[15:03:52] [Server thread/INFO]: Loading properties
[15:03:52] [Server thread/INFO]: Default game type: SURVIVAL
[15:03:52] [Server thread/INFO]: Generating keypair
[15:03:52] [Server thread/INFO]: Starting Minecraft server on *:25565
[15:03:52] [Server thread/INFO]: Using default channel type
[15:03:52] [Server thread/WARN]: **** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!
[15:03:52] [Server thread/WARN]: The server will make no attempt to authenticate usernames. Beware.
[15:03:52] [Server thread/WARN]: While this makes the game possible to play without internet access, it also opens up the ability for hackers to connect with any username they choose.
[15:03:52] [Server thread/WARN]: To change this, set "online-mode" to "true" in the server.properties file.
[15:03:52] [Server thread/INFO]: This server is running CUANTIC version 1.16.5-1d8d6313 (MC: 1.16.5) (Implementing API version 1.16.5-R0.1-SNAPSHOT, Forge version 36.2.39)
[15:03:55] [Server thread/INFO]: Debug logging is enabled
[15:03:55] [Server thread/INFO]: Using 2 threads for Netty based IO
[15:03:55] [Server thread/INFO]: Server Ping Player Sample Count: 12
=== ULTIMELE 35 LINII DIN sup.log ===
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:35:41 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:35:56 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:36:11 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:36:27 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:36:42 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:36:57 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0m 11:37:12 mc=DA port=SUS log=600
 log blocat:
[11:27:32] [Server thread/INFO]: iZentric issued server command: /spawn
[11:29:10] [Server thread/INFO]: iZentric issued server command: /tps
[0mRULEAZA: pack CUANTIC-Server-CatServer-1.7.7.zip, java openjdk version "17.0.20.1" 2026-08-18
JAVA: /home/mndvasi9/.local/jdk17/bin/java -> openjdk version "17.0.20.1" 2026-08-18
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 39 linii)
MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus).
 15:03:27 mc=DA port=nu asculta log=601
 15:03:42 mc=DA port=nu asculta log=635
=== CRASH REPORTS ===
=== DMESG OOM ===
sup.log: JAVA: /home/mndvasi9/.local/jdk17/bin/java -> openjdk version "17.0.20.1" 2026-08-18|args: OK (CatServer-1.16.5-1d8d6313-server.jar, 39 linii)|MC pornit. Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul (serverul ramane sus).| 15:03:27 mc=DA port
frpc.toml: 10
adresa din fisier: 92.5.171.150:25565
  dinafara 1: "online":false |  |  "message":"Unknown problem with returned server data."
  dinafara 2: "online":false |  |  "message":"Unknown problem with returned server data."
  dinafara 3: "online":false |  |  "message":"Unknown problem with returned server data."
```
