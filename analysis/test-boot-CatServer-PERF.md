# VERDICT CatServer-PERF (Thu Oct  8 07:49:14 UTC 2026)
- REZULTAT: **PORNIT** in 130s | RAM: **3102MB**
- Done-line:
    [07:48:45] [Server thread/INFO]: Done (15.539s)! For help, type "help"
- Erori cheie:
          1 [07:48:45] [Server thread/WARN]: Could not load any license plate
          1 [07:48:37] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
          1 [07:48:09] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
          1 [07:48:01] [modloading-worker-0/ERROR]: File not found
          1 [07:47:54] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
          1 [07:47:52] [main/ERROR]: Zip Error when loading jar file /home/runner/work/ServerRolePlayLite/ServerRolePlayLite/srv/mods/performant-1.16.2-5-4.1m.jar
          1 The libraries file download completed, if an error occurs only need re-run the server
          1 Downloading error_prone_annotations-2.1.3.jar Size: 13.3828125 KB
- Contextul erorilor invalid-dist (vinovatul cu nume):
- Contextul erorii File not found (ultimul mister):
    [07:47:57] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: Defaulting to no-operation (NOP) logger implementation
    [07:47:57] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
    [07:47:57] [main/INFO]: ModernFix reached bootstrap stage (1.294 min after launch)
    [07:47:58] [main/INFO]: Using Java 9+ class definer
    [07:47:59] [main/INFO]: Patching ItemStack#onItemUse
    [07:48:00] [main/INFO]: Vanilla bootstrap took 3195 milliseconds
    [07:48:01] [modloading-worker-0/INFO]: Patching DataPackRegistries#<init>
    [07:48:01] [modloading-worker-0/INFO]: Ksyxis: Ready to remove unneeded chunks. (platform: forge, version: 1.4.5, mixin: 0.8.4)
    [07:48:01] [modloading-worker-0/ERROR]: File not found
    java.io.FileNotFoundException: config/modernlife-common.toml (No such file or directory)
    	at java.io.FileInputStream.open0(Native Method) ~[?:?]
- CANTARUL PE MOD (cei mai scumpi la incarcare, din debug.log):
     Dedicated server took 125.323 s
- Pluginuri pornite:
    [07:48:22] [Server thread/INFO]: [LuckPerms] Enabling LuckPerms v5.5.71
    [07:48:27] [Server thread/INFO]: [Vault] Enabling Vault v1.7.3-b131
    [07:48:27] [Server thread/INFO]: [ProtocolLib] Enabling ProtocolLib v4.8.0
    [07:48:27] [Server thread/INFO]: [WorldEdit] Enabling WorldEdit v7.2.5+57d5ac9
    [07:48:36] [Server thread/INFO]: [Chunky] Enabling Chunky v1.2.217
    [07:48:36] [Server thread/INFO]: [SkinsRestorer] Enabling SkinsRestorer v14.2.12
    [07:48:37] [Server thread/INFO]: [Essentials] Enabling Essentials v2.19.7
    [07:48:41] [Server thread/INFO]: [EssentialsChat] Enabling EssentialsChat v2.19.7
    [07:48:41] [Server thread/INFO]: [EssentialsAntiBuild] Enabling EssentialsAntiBuild v2.19.7
    [07:48:41] [Server thread/INFO]: [EssentialsSpawn] Enabling EssentialsSpawn v2.19.7
    [07:48:41] [Server thread/INFO]: [WorldGuard] Enabling WorldGuard v7.0.5+3827266
    [07:48:42] [Server thread/INFO]: [EssentialsProtect] Enabling EssentialsProtect v2.19.7
    [07:48:42] [Server thread/INFO]: [AuthMe] Enabling AuthMe v5.6.0-bCUSTOM
    [07:48:43] [Server thread/INFO]: [FastLogin] Enabling FastLogin v1.12-SNAPSHOT-65a379c
