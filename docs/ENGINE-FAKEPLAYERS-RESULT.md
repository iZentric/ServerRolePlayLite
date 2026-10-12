# Fake players: CUANTIC pack + Curtain, test izolat

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38187803047

Curtain upstream: https://github.com/Gu-ZT/Curtain/releases/tag/1.3.2 (1.16.5; cod /player în ramura 1.16.5).

Testul adaugă un JAR Curtain derivat NUMAI în copia temporară: dezactivăm strict mixin-ul NaturalSpawnerMixin incompatibil cu CatServer; funcția /player rămâne. Pack-ul original are 36 moduri, testul are 37. Nici serverul live, nici release-ul nu au fost modificate.

Fake players folosesc conexiune internă, nu login FML real, FPS client sau mașini. Aceasta este probă de fezabilitate, nu A/B de performanță și nu 25 de oameni reali.

```json
{
  "method": "temporary GH runner, Java17, released 36/14 pack plus ONE isolated Curtain 1.16.5 test mod; 3 server-side fake players via /player; verify fresh list + local status, 40s ticking",
  "limits": "Fake players are not network clients: no Forge FML login, resource pack, client FPS or vehicle-driver validation. Added Curtain changes the test pack; the test-only derived jar disables one incompatible non-player NaturalSpawnerMixin. Feasibility/smoke, NOT performance A/B or production recommendation.",
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
  "test_mod_sha256": "affa757e4abb12cd577fed599577923be15472af332c4af00407d013f43902e9",
  "test_only_disabled_mixin": "NaturalSpawnerMixin (CatServer target mismatch; NOT a player mixin)",
  "boot_done_s": 11.073,
  "boot_wall_s": 101.82,
  "mods_on_disk": 37,
  "plugins_enabled": 14,
  "join_log_tails": [
    "minecraft:overworld to be force loaded\n[00:25:04] [Server thread/INFO]: Using new advancement loading for net.minecraft.advancements.PlayerAdvancements@69762724\n[00:25:04] [Server thread/INFO]: benchA01[local] logged in with entity id 1 at (0.5, 90.0, 0.5)\n[00:25:04] [Server thread/INFO]: An unexpected error occurred trying to execute that command\n",
    "00:25:05] [Craft Scheduler Thread - 2/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m[GitHubUpdate] Update saved as plugins/update/SkinsRestorer.jar\u001b[0;39m\n[00:25:05] [Server thread/INFO]: benchA02[local] logged in with entity id 2 at (8.5, 90.0, 0.5)\n[00:25:05] [Server thread/INFO]: An unexpected error occurred trying to execute that command\n",
    ": Can only manipulate existing players\n[00:25:05] [Server thread/INFO]: Using new advancement loading for net.minecraft.advancements.PlayerAdvancements@8b2563f\n[00:25:05] [Server thread/INFO]: benchA03[local] logged in with entity id 3 at (16.5, 90.0, 0.5)\n[00:25:05] [Server thread/INFO]: An unexpected error occurred trying to execute that command\n"
  ],
  "list_reply": "There are 0 out of maximum 25 players online.",
  "list_count": 0,
  "local_status": {
    "version": {
      "name": "CUANTIC 1.16.5",
      "protocol": 754
    },
    "players": {
      "online": 0,
      "max": 25
    }
  },
  "error": "fresh list does not contain all three fake players",
  "critical_lines": [],
  "root_causes": [
    "[00:24:17] [Thread-1/INFO]: [com.electronwill.nightconfig.core.file.FileWatcher$WatcherThread:run:183]: com.electronwill.nightconfig.core.io.ParsingException: Invalid TOML data: entry \"[maxThreads]\" defined twice in its table."
  ],
  "log_tail": "rver thread/INFO]: Can only manipulate existing players\n[00:25:05] [Server thread/INFO]: Using new advancement loading for net.minecraft.advancements.PlayerAdvancements@8b2563f\n[00:25:05] [Server thread/INFO]: benchA03[local] logged in with entity id 3 at (16.5, 90.0, 0.5)\n[00:25:05] [Server thread/INFO]: An unexpected error occurred trying to execute that command\n[00:25:05] [Server thread/INFO]: Can only manipulate existing players\n[00:25:05] [Server thread/INFO]: CONSOLE issued server command: /list \n[00:25:05] [Server thread/INFO]: There are 0 out of maximum 25 players online.\n[00:25:05] [Server thread/INFO]: [ProtocolLib] The updater found an update: 5.4.0 (Running 4.8.0). Download at https://www.spigotmc.org/resources/protocollib.1997/\n[00:25:06] [Server thread/INFO]: Shutting down locating executor service\n[00:25:06] [Server thread/INFO]: Saved 0 license plates\n[00:25:06] [Server thread/INFO]: CarClear: 0 | true\n[00:25:06] [Server thread/INFO]: Stopping server\n[00:25:06] [Server thread/INFO]: Unregistering com.sk89q.worldedit.bukkit.BukkitServerInterface from WorldEdit\n[00:25:06] [Server thread/INFO]: Saving players\n[00:25:06] [Server thread/INFO]: Saving worlds\n[00:25:06] [Server thread/INFO]: Saving chunks for level 'ServerLevel[world]'/minecraft:overworld\n[00:25:06] [Server thread/INFO]: ThreadedAnvilChunkStorage (world): All chunks are saved\n[00:25:06] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM-1]'/minecraft:the_nether\n[00:25:06] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM-1): All chunks are saved\n[00:25:06] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM1]'/minecraft:the_end\n[00:25:06] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM1): All chunks are saved\n[00:25:06] [Server thread/INFO]: Saving usercache.json\n"
}
```
