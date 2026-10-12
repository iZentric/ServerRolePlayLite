# Spark CPU profile: server thread (60 s, 1 player)

Source: https://spark.lucko.me/u5aki9eatL (full raw export)
Live JAR unchanged. This is diagnostic sampling, not an A/B benchmark.
Times below are sampled stack weights, not per-tick costs or proof of speedup.

## Server thread: 50433.5 ms sampled

### Widest direct branches

- 49641.2 ms (98.4%): `java.lang.Thread.run`
- 370.7 ms (0.7%): `java.unknown_Java`
- 276.1 ms (0.5%): `net.minecraft.server.MinecraftServer.func_213202_o`
- 140.2 ms (0.3%): `com.sk89q.worldguard.protection.managers.index.HashMapIndex.get`
- 5.3 ms (0.0%): `java.util.Spliterators$IteratorSpliterator.estimateSize`

### Top self-time methods (child weights subtracted)

- 4181.2 ms (8.3%): `net.minecraft.world.server.ServerChunkProvider.lambda$tickChunks$6`
- 2872.6 ms (5.7%): `it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap.get`
- 1793.6 ms (3.6%): `it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap$MapIterator.nextEntry`
- 1788.5 ms (3.5%): `net.minecraft.world.server.ServerWorld.func_217441_a`
- 1742.5 ms (3.5%): `native.vtable stub`
- 1341.9 ms (2.7%): `native.itable stub`
- 1291.7 ms (2.6%): `net.minecraft.util.SortedArraySet.removeIf`
- 1186.2 ms (2.4%): `jdk.internal.misc.Unsafe.park`
- 923.7 ms (1.8%): `net.minecraftforge.eventbus.EventBus$$Lambda$2635.0x000000020188a8d0.invoke`
- 909.3 ms (1.8%): `net.minecraft.world.World.func_212866_a_`
- 897.3 ms (1.8%): `java.util.HashMap.getNode`
- 894.5 ms (1.8%): `java.util.Collections.shuffle`
- 757.2 ms (1.5%): `net.minecraft.block.FlowingFluidBlock.func_225542_b_`
- 754.4 ms (1.5%): `net.minecraft.world.spawner.WorldEntitySpawner.func_234977_a_`
- 747.4 ms (1.5%): `net.minecraft.world.server.ChunkManager.func_219169_g`
- 739.7 ms (1.5%): `java.util.Random.nextInt`
- 733.1 ms (1.5%): `it.unimi.dsi.fastutil.objects.ReferenceOpenHashSet.contains`
- 707.7 ms (1.4%): `net.minecraft.world.IEntityReader.func_190525_a`
- 548.7 ms (1.1%): `net.minecraft.world.spawner.WorldEntitySpawner.func_234964_a_`
- 452.7 ms (0.9%): `net.minecraft.util.ClassInheritanceMultiMap.createAllOfType`
- 407.8 ms (0.8%): `java.util.EnumMap.isValidKey`
- 407.6 ms (0.8%): `net.minecraft.util.BitArray.func_188142_a`
- 399.8 ms (0.8%): `java.util.stream.AbstractPipeline.evaluate`
- 376.0 ms (0.7%): `native.Interpreter`
- 374.1 ms (0.7%): `net.minecraft.server.MinecraftServer.func_213205_aW`
- 360.0 ms (0.7%): `net.minecraft.world.chunk.ChunkDistanceGraph.func_215477_a`
- 358.5 ms (0.7%): `com.google.common.collect.Iterators.addAll`
- 355.2 ms (0.7%): `net.minecraft.entity.player.PlayerInventory.func_70301_a`
- 354.4 ms (0.7%): `net.minecraft.world.server.ChunkManager.func_219183_a`
- 351.2 ms (0.7%): `java.util.ArrayList.clear`

### Notable paths ending in a >=1% self-time frame

- 4181.2 ms self: `net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> java.util.ArrayList.forEach -> net.minecraft.world.server.ServerChunkProvider$$Lambda$14106.0x0000000202eb1db0.accept -> net.minecraft.world.server.ServerChunkProvider.lambda$tickChunks$6`
- 1793.6 ms self: `net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> net.minecraft.world.server.ServerChunkProvider.redirect$zca000$redirectChunksListClone -> com.google.common.collect.Iterators.addAll -> com.google.common.collect.Iterators$3.next -> it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap$ValueIterator.next -> it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap$MapIterator.nextEntry`
- 1788.5 ms self: `net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> java.util.ArrayList.forEach -> net.minecraft.world.server.ServerChunkProvider$$Lambda$14106.0x0000000202eb1db0.accept -> net.minecraft.world.server.ServerChunkProvider.lambda$tickChunks$6 -> net.minecraft.world.server.ServerWorld.func_217441_a`
- 1291.7 ms self: `net.minecraft.server.MinecraftServer.func_71217_p -> net.minecraft.server.dedicated.DedicatedServer.func_71190_q -> net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.TicketManager.func_219340_a -> net.minecraft.util.SortedArraySet.removeIf`
- 1186.2 ms self: `net.minecraft.server.MinecraftServer.func_240783_a_ -> net.minecraft.server.MinecraftServer.func_240802_v_ -> net.minecraft.server.MinecraftServer.func_213202_o -> net.minecraft.util.concurrent.ThreadTaskExecutor.func_213161_c -> net.minecraft.util.concurrent.ThreadTaskExecutor.func_223705_bi -> java.util.concurrent.locks.LockSupport.parkNanos -> jdk.internal.misc.Unsafe.park`
- 1150.2 ms self: `net.minecraft.world.server.ServerChunkProvider.func_217220_m -> net.minecraft.world.spawner.WorldEntitySpawner.func_234964_a_ -> net.minecraft.world.server.ServerChunkProvider$$Lambda$14103.0x0000000202ead628.query -> net.minecraft.world.server.ServerChunkProvider.func_241098_a_ -> net.minecraft.world.server.ServerChunkProvider.func_217213_a -> net.minecraft.world.server.ChunkManager.func_219219_b -> it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap.get`
- 894.5 ms self: `net.minecraft.server.dedicated.DedicatedServer.func_71190_q -> net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> java.util.Collections.shuffle -> java.util.Collections.shuffle`
- 757.2 ms self: `net.minecraft.world.server.ServerChunkProvider.func_217220_m -> java.util.ArrayList.forEach -> net.minecraft.world.server.ServerChunkProvider$$Lambda$14106.0x0000000202eb1db0.accept -> net.minecraft.world.server.ServerChunkProvider.lambda$tickChunks$6 -> net.minecraft.world.server.ServerWorld.func_217441_a -> net.minecraft.block.AbstractBlock$AbstractBlockState.func_227034_b_ -> net.minecraft.block.FlowingFluidBlock.func_225542_b_`
- 754.4 ms self: `java.util.ArrayList.forEach -> net.minecraft.world.server.ServerChunkProvider$$Lambda$14106.0x0000000202eb1db0.accept -> net.minecraft.world.server.ServerChunkProvider.lambda$tickChunks$6 -> net.minecraft.world.spawner.WorldEntitySpawner.func_234979_a_ -> net.minecraft.world.spawner.WorldEntitySpawner.func_234967_a_ -> net.minecraft.world.spawner.WorldEntitySpawner.func_234966_a_ -> net.minecraft.world.spawner.WorldEntitySpawner.func_234977_a_`
- 747.4 ms self: `net.minecraft.server.MinecraftServer.func_71217_p -> net.minecraft.server.dedicated.DedicatedServer.func_71190_q -> net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> net.minecraft.world.server.ChunkManager.func_219169_g`
- 739.7 ms self: `net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> java.util.Collections.shuffle -> java.util.Collections.shuffle -> java.util.Random.nextInt`
- 707.7 ms self: `net.minecraft.server.dedicated.DedicatedServer.func_71190_q -> net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.entity.MobEntity.func_70623_bb -> net.minecraft.world.IEntityReader.func_217362_a -> net.minecraft.world.IEntityReader.func_217366_a -> net.minecraft.world.IEntityReader.func_190525_a`
- 548.7 ms self: `net.minecraft.server.MinecraftServer.func_71217_p -> net.minecraft.server.dedicated.DedicatedServer.func_71190_q -> net.minecraft.server.MinecraftServer.func_71190_q -> net.minecraft.world.server.ServerWorld.func_72835_b -> net.minecraft.world.server.ServerChunkProvider.func_217207_a -> net.minecraft.world.server.ServerChunkProvider.func_217220_m -> net.minecraft.world.spawner.WorldEntitySpawner.func_234964_a_`
- 524.4 ms self: `net.minecraft.entity.ai.goal.AvoidEntityGoal.func_75250_a -> net.minecraft.world.IEntityReader.func_225318_b -> net.minecraft.world.World.func_225316_b -> net.minecraft.world.chunk.Chunk.func_177430_a -> net.minecraft.util.ClassInheritanceMultiMap.func_219790_a -> java.util.HashMap.get -> java.util.HashMap.getNode`

Nodes: 1334; distinct methods: 812.
Spark sample time includes waiting/parking if those frames were sampled; do not treat it as 50 s of CPU.

## Interpretare și limitări

- Căile dominante sunt încărcarea/tick-ul chunk-urilor, tick-ul lumii și scanarea ticketelor; nu există în acest profil un hot path demonstrat pentru patch-urile anterioare de hopper.
- `SortedArraySet.removeIf` apare cu ~1.292 ms cumulat în stiva eșantionată (~2,6% din 50.433 ms). Acesta este un **plafon teoretic** dacă metoda ar deveni gratuită, nu o estimare a îmbunătățirii reale.
- Comenzile consolei au raportat 1 jucător la începutul și sfârșitul profilării; metadatele Spark din export au `playerCount: 0`. Această discrepanță înseamnă că profilul **nu demonstrează** prezența continuă a jucătorului sau încărcarea cu vehicule în cele 60 s.
- [Prototype-ul CatServer cu scanare optimizată a ticketelor](ENGINE-TICKET-RESULT.md) a trecut compilarea și smoke-ul, dar [testul de stare stabilă](ENGINE-TICKET-STEADY-RESULT.md) nu a îmbunătățit simultan CPU și p95. Nu înlocuiește JAR-ul live.
