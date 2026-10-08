# VERDICT CatServer (Thu Oct  8 07:49:30 UTC 2026)
- REZULTAT: **PORNIT** in 150s | RAM: **4107MB**
- Done-line:
    [07:48:58] [Server thread/INFO]: Done (20.634s)! For help, type "help"
- Erori cheie:
          1 [07:48:58] [Server thread/WARN]: Could not load any license plate
          1 [07:48:46] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
          1 [07:48:06] [Worker-Main-1/ERROR]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
          1 [07:47:58] [modloading-worker-0/FATAL]: Attempted to load class hl for invalid dist DEDICATED_SERVER
          1 [07:47:58] [modloading-worker-0/FATAL]: Attempted to load class hk for invalid dist DEDICATED_SERVER
          1 [07:47:58] [modloading-worker-0/FATAL]: Attempted to load class hg for invalid dist DEDICATED_SERVER
          1 [07:47:56] [modloading-worker-0/ERROR]: File not found
          1 [07:47:47] [main/ERROR]: Mixin config pizzamod.mixin.json does not specify "minVersion" property
          1 The libraries file download completed, if an error occurs only need re-run the server
          1 Downloading error_prone_annotations-2.1.3.jar Size: 13.3828125 KB
- Contextul erorilor invalid-dist (vinovatul cu nume):
    	at java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656) [?:?]
    [07:47:58] [modloading-worker-0/INFO]: Forge mod loading, version 36.2.39, for MC 1.16.5 with MCP 20210115.111550
    [07:47:58] [modloading-worker-0/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hl for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
    [07:47:58] [modloading-worker-0/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: 	at java.base/java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656)
    [07:47:58] [modloading-worker-0/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hk for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
    [07:47:58] [modloading-worker-0/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: 	at java.base/java.util.concurrent.ForkJoinPool.scan(ForkJoinPool.java:1656)
    [07:47:58] [modloading-worker-0/INFO]: [net.minecraftforge.fml.loading.RuntimeDistCleaner:processClassWithFlags:75]: java.lang.RuntimeException: Attempted to load class hg for invalid dist DEDICATED_SERVER (It may crash the server, please report it to the mod author)
- Contextul erorii File not found (ultimul mister):
    [07:47:51] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
    [07:47:51] [main/INFO]: ModernFix reached bootstrap stage (1.261 min after launch)
    [07:47:52] [main/INFO]: Injecting BlockStateBase cache population hook into func_204519_t from me.jellysquid.mods.lithium.mixin.block.flatten_states.AbstractBlockStateMixin
    [07:47:52] [main/INFO]: Using Java 9+ class definer
    [07:47:52] [main/INFO]: Patching ItemStack#onItemUse
    [07:47:55] [main/INFO]: Vanilla bootstrap took 3717 milliseconds
    [07:47:56] [modloading-worker-0/INFO]: Patching DataPackRegistries#<init>
    [07:47:56] [modloading-worker-0/INFO]: Ksyxis: Ready to remove unneeded chunks. (platform: forge, version: 1.4.5, mixin: 0.8.4)
    [07:47:56] [modloading-worker-0/ERROR]: File not found
    java.io.FileNotFoundException: config/modernlife-common.toml (No such file or directory)
    	at java.io.FileInputStream.open0(Native Method) ~[?:?]
- CANTARUL PE MOD (cei mai scumpi la incarcare, din debug.log):
     Dedicated server took 142.29 s
- Pluginuri pornite:
    [07:48:26] [Server thread/INFO]: [LuckPerms] Enabling LuckPerms v5.5.71
    [07:48:33] [Server thread/INFO]: [Vault] Enabling Vault v1.7.3-b131
    [07:48:34] [Server thread/INFO]: [ProtocolLib] Enabling ProtocolLib v4.8.0
    [07:48:34] [Server thread/INFO]: [WorldEdit] Enabling WorldEdit v7.2.5+57d5ac9
    [07:48:44] [Server thread/INFO]: [Chunky] Enabling Chunky v1.2.217
    [07:48:44] [Server thread/INFO]: [SkinsRestorer] Enabling SkinsRestorer v14.2.12
    [07:48:46] [Server thread/INFO]: [Essentials] Enabling Essentials v2.19.7
    [07:48:53] [Server thread/INFO]: [EssentialsChat] Enabling EssentialsChat v2.19.7
    [07:48:53] [Server thread/INFO]: [EssentialsAntiBuild] Enabling EssentialsAntiBuild v2.19.7
    [07:48:53] [Server thread/INFO]: [EssentialsSpawn] Enabling EssentialsSpawn v2.19.7
    [07:48:53] [Server thread/INFO]: [WorldGuard] Enabling WorldGuard v7.0.5+3827266
    [07:48:55] [Server thread/INFO]: [EssentialsProtect] Enabling EssentialsProtect v2.19.7
    [07:48:55] [Server thread/INFO]: [AuthMe] Enabling AuthMe v5.6.0-bCUSTOM
    [07:48:56] [Server thread/INFO]: [FastLogin] Enabling FastLogin v1.12-SNAPSHOT-65a379c
