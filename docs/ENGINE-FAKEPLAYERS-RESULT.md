# Fake players: CUANTIC pack + Curtain, test izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38187642686

Curtain upstream: https://github.com/Gu-ZT/Curtain/releases/tag/1.3.2 (1.16.5; cod /player în ramura 1.16.5).

Instalat NUMAI în copia temporară de test; pack-ul original are 36 moduri, testul are 37. Nici serverul live, nici release-ul nu au fost modificate.

Fake players folosesc conexiune internă, nu login FML real, FPS client sau mașini. Aceasta este probă de fezabilitate, nu A/B de performanță și nu 25 de oameni reali.

```json
{
  "method": "temporary GH runner, Java17, released 36/14 pack plus ONE isolated Curtain 1.16.5 test mod; 3 server-side fake players via /player; verify fresh list + local status, 40s ticking",
  "limits": "Fake players are not network clients: no Forge FML login, resource pack, client FPS or vehicle-driver validation. Adding Curtain changes the test pack. This is a feasibility/smoke run, not a performance A/B or production recommendation.",
  "pack_sha256": "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15",
  "curtain_sha256": "c9234d2c5ca43c337abac25a05022fe2f226c884855aa6941b6130c60777819d",
  "curtain_release": "Gu-ZT/Curtain 1.3.2/mc1.16.5",
  "expected_names": [
    "benchA01",
    "benchA02",
    "benchA03"
  ],
  "valid": false,
  "production_changes": false,
  "error": "No fresh response matching Done \\(([\\d.]+)s\\) (last log: .doWork(ChunkStatus.java:240) ~[?:?]\n\tat net.minecraft.world.chunk.ChunkStatus.func_223198_a(ChunkStatus.java:198) ~[?:?]\n\tat net.minecraft.world.server.ChunkManager.lambda$null$18(ChunkManager.java:532) ~[?:?]\n\tat com.mojang.datafixers.util.Either$Left.map(Either.java:38) ~[?:?]\n\tat net.minecraft.world.server.ChunkManager.lambda$scheduleChunkGeneration$20(ChunkManager.java:530) ~[?:?]\n\tat java.util.concurrent.CompletableFuture$UniCompose.tryFire(CompletableFuture.java:1150) ~[?:?]\n\t... 11 more\n)",
  "critical_lines": [
    "[00:21:54] [Worker-Main-3/FATAL]: Failed to schedule load callback for chunk [3, -15]",
    "[00:21:54] [Server thread/FATAL]: Preparing crash report with UUID 40f7e1ad-b29d-4239-aec9-e0a30e6a3263"
  ],
  "root_causes": [
    "[00:21:33] [Thread-1/INFO]: [com.electronwill.nightconfig.core.file.FileWatcher$WatcherThread:run:183]: com.electronwill.nightconfig.core.io.ParsingException: Invalid TOML data: entry \"[maxThreads]\" defined twice in its table.",
    "java.util.concurrent.CompletionException: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "ngepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: Redirector spawnEntity(Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/entity/Entity;Lnet/minecraft/entity/EntityClassification;Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/world/chunk/IChunk;Lnet/minecraft/util/math/BlockPos;Lnet/minecraft/world/spawner/WorldEntitySpawner$IDensityCheck;Lnet/minecraft/world/spawner/WorldEntitySpawner$IOnSpawnDensityAdder;)V in curtain.mixins.json:NaturalSpawnerMixin failed injection check, (0/1) succeeded. Scanned 1 target(s). Using refmap curtain.refmap.json",
    "net.minecraft.crash.ReportedException: Exception initializing level",
    "Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "ngepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: Redirector spawnEntity(Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/entity/Entity;Lnet/minecraft/entity/EntityClassification;Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/world/chunk/IChunk;Lnet/minecraft/util/math/BlockPos;Lnet/minecraft/world/spawner/WorldEntitySpawner$IDensityCheck;Lnet/minecraft/world/spawner/WorldEntitySpawner$IOnSpawnDensityAdder;)V in curtain.mixins.json:NaturalSpawnerMixin failed injection check, (0/1) succeeded. Scanned 1 target(s). Using refmap curtain.refmap.json",
    "org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "ngepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: Redirector spawnEntity(Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/entity/Entity;Lnet/minecraft/entity/EntityClassification;Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/world/chunk/IChunk;Lnet/minecraft/util/math/BlockPos;Lnet/minecraft/world/spawner/WorldEntitySpawner$IDensityCheck;Lnet/minecraft/world/spawner/WorldEntitySpawner$IOnSpawnDensityAdder;)V in curtain.mixins.json:NaturalSpawnerMixin failed injection check, (0/1) succeeded. Scanned 1 target(s). Using refmap curtain.refmap.json",
    "java.util.concurrent.CompletionException: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
    "ngepowered.asm.mixin.injection.throwables.InjectionError: Critical injection failure: Redirector spawnEntity(Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/entity/Entity;Lnet/minecraft/entity/EntityClassification;Lnet/minecraft/world/server/ServerWorld;Lnet/minecraft/world/chunk/IChunk;Lnet/minecraft/util/math/BlockPos;Lnet/minecraft/world/spawner/WorldEntitySpawner$IDensityCheck;Lnet/minecraft/world/spawner/WorldEntitySpawner$IOnSpawnDensityAdder;)V in curtain.mixins.json:NaturalSpawnerMixin failed injection check, (0/1) succeeded. Scanned 1 target(s). Using refmap curtain.refmap.json"
  ],
  "log_tail": "dler.java:131) ~[mixin-0.8.4.jar:0.8.4+unknown-b0.git-unknown]\n\tat org.spongepowered.asm.launch.MixinLaunchPluginLegacy.processClass(MixinLaunchPluginLegacy.java:131) ~[mixin-0.8.4.jar:0.8.4+unknown-b0.git-unknown]\n\tat cpw.mods.modlauncher.serviceapi.ILaunchPluginService.processClassWithFlags(ILaunchPluginService.java:154) ~[modlauncher-8.1.3.jar:8.1.3+8.1.3+main-8.1.x.c94d18ec]\n\tat cpw.mods.modlauncher.LaunchPluginHandler.offerClassNodeToPlugins(LaunchPluginHandler.java:85) ~[modlauncher-8.1.3.jar:?]\n\tat cpw.mods.modlauncher.ClassTransformer.transform(ClassTransformer.java:120) ~[modlauncher-8.1.3.jar:?]\n\tat cpw.mods.modlauncher.TransformingClassLoader$DelegatedClassLoader.findClass(TransformingClassLoader.java:265) ~[modlauncher-8.1.3.jar:?]\n\tat cpw.mods.modlauncher.TransformingClassLoader.loadClass(TransformingClassLoader.java:136) ~[modlauncher-8.1.3.jar:?]\n\tat cpw.mods.modlauncher.TransformingClassLoader.loadClass(TransformingClassLoader.java:98) ~[modlauncher-8.1.3.jar:?]\n\tat java.lang.ClassLoader.loadClass(ClassLoader.java:525) ~[?:?]\n\tat net.minecraft.world.gen.NoiseChunkGenerator.func_230354_a_(NoiseChunkGenerator.java:629) ~[?:?]\n\tat net.minecraft.world.chunk.ChunkStatus.func_222602_b(ChunkStatus.java:89) ~[?:?]\n\tat net.minecraft.world.chunk.ChunkStatus$ISelectiveWorker.doWork(ChunkStatus.java:240) ~[?:?]\n\tat net.minecraft.world.chunk.ChunkStatus.func_223198_a(ChunkStatus.java:198) ~[?:?]\n\tat net.minecraft.world.server.ChunkManager.lambda$null$18(ChunkManager.java:532) ~[?:?]\n\tat com.mojang.datafixers.util.Either$Left.map(Either.java:38) ~[?:?]\n\tat net.minecraft.world.server.ChunkManager.lambda$scheduleChunkGeneration$20(ChunkManager.java:530) ~[?:?]\n\tat java.util.concurrent.CompletableFuture$UniCompose.tryFire(CompletableFuture.java:1150) ~[?:?]\n\t... 11 more\n"
}
```
