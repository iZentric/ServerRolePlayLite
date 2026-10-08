# VERDICT CatServer (Thu Oct  8 07:28:12 UTC 2026)
- REZULTAT: **PORNIT** in 170s | RAM: **4199MB**
- Done-line:
    [07:27:41] [Server thread/INFO]: Done (23.207s)! For help, type "help"
- Erori cheie:
          1 [07:27:41] [Server thread/WARN]: Could not load any license plate
          1 [07:27:28] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
          1 [07:26:46] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
          1 [07:26:37] [modloading-worker-1/FATAL]: Attempted to load class hl for invalid dist DEDICATED_SERVER
          1 [07:26:37] [modloading-worker-1/FATAL]: Attempted to load class hk for invalid dist DEDICATED_SERVER
          1 [07:26:37] [modloading-worker-1/FATAL]: Attempted to load class hg for invalid dist DEDICATED_SERVER
          1 [07:26:35] [modloading-worker-0/ERROR]: File not found
          1 [07:26:26] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
          1 The libraries file download completed, if an error occurs only need re-run the server
          1 Downloading error_prone_annotations-2.1.3.jar Size: 13.3828125 KB
- Contextul erorilor invalid-dist (vinovatul cu nume):
    	at java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656) [?:?]
    [07:26:37] [modloading-worker-1/INFO]: Forge mod loading, version 36.2.39, for MC 1.16.5 with MCP 20210115.111550
    [07:26:37] [modloading-worker-1/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hl for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
    [07:26:37] [modloading-worker-1/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: 	at java.base/java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656)
    [07:26:37] [modloading-worker-1/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hk for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
    [07:26:37] [modloading-worker-1/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: 	at java.base/java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656)
    [07:26:37] [modloading-worker-1/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hg for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
- Contextul erorii File not found (ultimul mister):
    [07:26:30] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
    [07:26:30] [main/INFO]: ModernFix reached bootstrap stage (1.546 min after launch)
    [07:26:31] [main/INFO]: Injecting BlockStateBase cache population hook into func_204519_t from me.jellysquid.mods.lithium.mixin.block.flatten_states.AbstractBlockStateMixin
    [07:26:31] [main/INFO]: Using Java 9+ class definer
    [07:26:31] [main/INFO]: Patching ItemStack#onItemUse
    [07:26:34] [main/INFO]: Vanilla bootstrap took 3654 milliseconds
    [07:26:34] [modloading-worker-0/INFO]: Patching DataPackRegistries#<init>
    [07:26:34] [modloading-worker-0/INFO]: Ksyxis: Ready to remove unneeded chunks. (platform: forge, version: 1.4.5, mixin: 0.8.4)
    [07:26:35] [modloading-worker-0/ERROR]: File not found
    java.io.FileNotFoundException: config/modernlife-common.toml (No such file or directory)
    	at java.io.FileInputStream.open0(Native Method) ~[?:?]
- Pluginuri pornite:
    [07:27:06] [Server thread/INFO]: [LuckPerms] Enabling LuckPerms v5.5.71
    [07:27:13] [Server thread/INFO]: [Vault] Enabling Vault v1.7.3-b131
    [07:27:14] [Server thread/INFO]: [ProtocolLib] Enabling ProtocolLib v4.8.0
    [07:27:14] [Server thread/INFO]: [WorldEdit] Enabling WorldEdit v7.2.5+57d5ac9
    [07:27:26] [Server thread/INFO]: [Chunky] Enabling Chunky v1.2.217
    [07:27:26] [Server thread/INFO]: [SkinsRestorer] Enabling SkinsRestorer v14.2.12
    [07:27:28] [Server thread/INFO]: [Essentials] Enabling Essentials v2.19.7
    [07:27:35] [Server thread/INFO]: [EssentialsChat] Enabling EssentialsChat v2.19.7
    [07:27:35] [Server thread/INFO]: [EssentialsAntiBuild] Enabling EssentialsAntiBuild v2.19.7
    [07:27:35] [Server thread/INFO]: [EssentialsSpawn] Enabling EssentialsSpawn v2.19.7
    [07:27:35] [Server thread/INFO]: [WorldGuard] Enabling WorldGuard v7.0.5+3827266
    [07:27:37] [Server thread/INFO]: [EssentialsProtect] Enabling EssentialsProtect v2.19.7
    [07:27:37] [Server thread/INFO]: [AuthMe] Enabling AuthMe v5.6.0-bCUSTOM
    [07:27:39] [Server thread/INFO]: [FastLogin] Enabling FastLogin v1.12-SNAPSHOT-65a379c
