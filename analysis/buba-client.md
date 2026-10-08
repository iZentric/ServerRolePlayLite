# BUBA CLIENT — 2026-10-08 22:37:25 UTC

## Rejectii handshake (cu 2 linii in jur)
```
15-[00:25:33] [main/INFO] [memoryleakfix]: [MemoryLeakFix] Currently enabled memory leak fixes: [entityMemoriesLeak, biomeTemperatureLeak, drownedNavigationLeak]
16:[00:25:33] [main/INFO] [MixinExtras|Service]: Initializing MixinExtras via org.embeddedt.modernfix.forge.shadow.mixinextras.service.MixinExtrasServiceImpl(version=0.3.2).
17-[00:25:35] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LivingEntity#attackEntityFrom
18-[00:25:35] [main/INFO] [STDERR]: [org.slf4j.helpers.Util:report:128]: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
--
52-[00:25:57] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableDeluxeBed was corrected from null to its default, true. 
53:[00:25:57] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableExtractor was corrected from null to its default, true. 
54-[00:25:57] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableGrate was corrected from null to its default, true. 
55-[00:25:57] [main/WARN] [net.minecraftforge.common.ForgeConfigSpec]: Incorrect key common.crafting.enableMicrowave was corrected from null to its default, true. 
--
147-[00:26:03] [main/INFO] [ModernFix]: Invalidating pack caches
148:[00:26:06] [Worker-Main-1/ERROR] [net.minecraft.tags.TagCollectionReader]: Couldn't load block tag farmersdelight:mushroom_colony_growable_on as it is missing following references: supplementaries:planter_rich (from supplementaries-1.16.5-0.18.4b.jar)
149-[00:26:06] [Worker-Main-1/INFO] [net.minecraft.item.crafting.RecipeManager]: Skipping loading recipe supplementaries:brass_lantern as it's serializer returned null
150-[00:26:06] [Worker-Main-1/INFO] [net.minecraft.item.crafting.RecipeManager]: Skipping loading recipe supplementaries:gold_gate as it's serializer returned null
--
185-[00:26:10] [Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer]: Starting Minecraft server on *:26252
186:[00:26:10] [Server thread/INFO] [net.minecraft.network.NetworkSystem]: Using epoll channel type
187-[00:26:11] [Server thread/WARN] [net.minecraft.server.dedicated.DedicatedServer]: **** SERVER IS RUNNING IN OFFLINE/INSECURE MODE!
188-[00:26:11] [Server thread/WARN] [net.minecraft.server.dedicated.DedicatedServer]: The server will make no attempt to authenticate usernames. Beware.
--
401-[00:27:00] [Server thread/INFO] [Essentials]: Starting usermap repair
402:[00:27:00] [Server thread/WARN] [Essentials]: Missing userdata folder, aborting
403-[00:27:00] [Server thread/INFO] [Essentials]: Attempting to migrate ignore list to UUIDs
404-[00:27:00] [Server thread/INFO] [Essentials]: Attempting to migrate legacy userdata keys to Configurate
```
## Moduri incarcate de server (nume + versiuni din log)
```
## Forge afisat la boot:
[00:25:19] [main/INFO] [cpw.mods.modlauncher.Launcher]: ModLauncher running: args [--gameDir, ., --launchTarget, fmlserver, --fml.forgeVersion, 36.2.39, --fml.mcpVersion, 20210115.111550, --fml.mcVersion, 1.16.5, --fml.forgeGroup, net.minecraftforge, nogui]
[00:25:20] [main/INFO] [net.minecraftforge.fml.loading.FixSSL]: Added Lets Encrypt root certificates as additional trust
[00:25:28] [main/INFO] [ModernFix]: Applied Forge config corruption patch
[00:25:30] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LivingEntity#attackEntityFrom
[00:25:32] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching ItemStack#onItemUse
[00:25:33] [main/INFO] [net.minecraftforge.coremod.CoreMod.placebo]: Patching LootTableManager#apply
```
