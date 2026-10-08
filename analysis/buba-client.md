# BUBA CLIENT — 2026-10-08 21:25:54 UTC

## Rejectii handshake (cu 2 linii in jur)
```
15-[20:39:10] [main/INFO] [memoryleakfix]: [MemoryLeakFix] Currently enabled memory leak fixes: [entityMemoriesLeak, biomeTemperatureLeak, drownedNavigationLeak]
16:[20:39:10] [main/INFO] [MixinExtras|Service]: Initializing MixinExtras via org.embeddedt.modernfix.forge.shadow.mixinextras.service.MixinExtrasServiceImpl(version=0.3.2).
17-[20:39:13] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LivingEntity#attackEntityFrom
18-[20:39:13] [main/INFO] [STDERR]: [org.slf4j.helpers.Util:report:128]: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
--
52-[20:39:30] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableDeluxeBed was corrected from null to its default, true. 
53:[20:39:30] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableExtractor was corrected from null to its default, true. 
54-[20:39:30] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableGrate was corrected from null to its default, true. 
55-[20:39:30] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableMicrowave was corrected from null to its default, true. 
--
147-[20:39:34] [main/INFO] [ModernFix]: Invalidating pack caches
148:[20:39:36] [Worker-Main-2/ERROR] [net.minecraft.tags.TagCollectionReader]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
149-[20:39:37] [Worker-Main-2/INFO] [net.minecraft.item.crafting.RecipeManager]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
150-[20:39:37] [Worker-Main-2/INFO] [net.minecraft.item.crafting.RecipeManager]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
--
184-[20:39:40] [Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer]: Starting Minecraft server on *:26252
185:[20:39:40] [Server thread/INFO] [net.minecraft.network.NetworkSystem]: Using epoll channel type
186-[20:39:40] [Server thread/WARN] [net.minecraft.server.dedicated.DedicatedServer]: **** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!
187-[20:39:40] [Server thread/WARN] [net.minecraft.server.dedicated.DedicatedServer]: The server will make no attempt to authenticate usernames. Beware.
--
373-[20:40:25] [Server thread/INFO] [Essentials]: Starting usermap repair
374:[20:40:25] [Server thread/WARN] [Essentials]: Missing userdata folder, aborting
375-[20:40:25] [Server thread/INFO] [Essentials]: Attempting to migrate ignore list to UUIDs
376-[20:40:25] [Server thread/INFO] [Essentials]: Attempting to migrate legacy userdata keys to Configurate
--
491-[21:18:18] [User Authenticator #1/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270
492:[21:18:19] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
493:[21:18:19] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
494:[21:18:19] [Server thread/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: com.mojang.authlib.GameProfile@3615ea53[id=0e2f8d53-21b4-32a4-a498-0967ed108270,name=iZentric,properties={},legacy=false] (/86.120.225.250:26423) lost connection: Connection closed - mismatched mod channel list
495-[21:18:26] [RCON Listener #1/INFO] [net.minecraft.network.rcon.RConThread]: Thread RCON Client /172.214.97.229 started
496-[21:18:26] [RCON Client /172.214.97.229 #12/INFO] [net.minecraft.network.rcon.ClientThread]: Thread RCON Client /172.214.97.229 shutting down
```
## Moduri incarcate de server (nume + versiuni din log)
```
## Forge afisat la boot:
[20:39:00] [main/INFO] [cpw.mods.modlauncher.Launcher]: ModLauncher running: args [--gameDir, ., --launchTarget, fmlserver, --fml.forgeVersion, 36.2.39, --fml.mcpVersion, 20210115.111550, --fml.mcVersion, 1.16.5, --fml.forgeGroup, net.minecraftforge, nogui]
[20:39:00] [main/INFO] [net.minecraftforge.fml.loading.FixSSL]: Added Lets Encrypt root certificates as additional trust
[20:39:06] [main/INFO] [ModernFix]: Applied Forge config corruption patch
[20:39:07] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LivingEntity#attackEntityFrom
[20:39:09] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching ItemStack#onItemUse
[20:39:09] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LootTableManager#apply
```
