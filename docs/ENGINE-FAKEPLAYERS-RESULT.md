# Fake players: CUANTIC pack + Curtain, test izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38187492388

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
    "[00:19:57] [Worker-Main-1/FATAL]: Failed to schedule load callback for chunk [3, -15]",
    "[00:19:57] [Server thread/FATAL]: Preparing crash report with UUID 205cc27b-834a-4bdb-9484-d11b2a270c2c"
  ]
}
```
