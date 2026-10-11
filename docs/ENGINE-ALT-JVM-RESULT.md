# Arclight Java 17 and Mist Java 8 — exact CUANTIC pack

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178448453

Isolated hosted VM, same 36 mods/14 plugins; no client login, vehicles or live deploy.
Different Java versions cannot be compared numerically: baseline J8 is used only against Mist J8.

## Arclight on J17
```json
{
  "method": "same exact 36 mod + 14 plugin JAR files and same configs/seed; one isolated smoke per hybrid JAR; no production access",
  "limits": "no modded-client login, vehicle gameplay, player load or A/B performance result; successful boot alone is not an upgrade",
  "baseline_zip": "CUANTIC-Server-CatServer-1.7.7.zip",
  "baseline_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "inventory_sha256": "d40f39acaa43f496893bd469953a093df33268e243ee233f0abcc2df6e7d37ca",
  "candidates": {
    "Arclight": {
      "same_mod_plugin_payload_sha256": true,
      "smoke": {
        "jar": "CatServer-1.16.5-1d8d6313-server.jar",
        "done_seconds": null,
        "enabled_plugins": 0,
        "plugin_names": [],
        "critical_lines": [],
        "timed_out": false,
        "exit_code_after_stop": 0,
        "handshake_with_real_client": "NOT TESTED",
        "performance_under_players": "NOT TESTED",
        "passed_smoke": false
      },
      "candidate_pack_inventory": {
        "mods": 36,
        "plugins": 14,
        "identical_to_baseline": true,
        "differences": [],
        "root_jars": [
          "arclight-forge-1.16.5-1.0.25.jar"
        ]
      },
      "source_engine": "arclight-forge-1.16.5-1.0.25.jar",
      "jar_sha256": "f7615ceb7fbb343aaef7bfc6238b131a28cf9a08190994e94e78e14a6d49ea78",
      "required_plugins_enabled": false,
      "qualified_for_performance_A_B": false,
      "diagnostic_key_lines": [
        "\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:650]: Caused by: java.lang.reflect.InvocationTargetException",
        "\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:659]: Caused by: org.spongepowered.asm.mixin.transformer.throwables.MixinTransformerError: An unexpected critical error was encountered",
        "jection.throwables.InjectionError: Critical injection failure: Redirector arclight$mobGriefing(Lnet/minecraft/world/World;Lnet/minecraft/util/math/BlockPos;Lnet/minecraft/entity/LivingEntity;)Z in mixins.arclight.core.json:entity.ai.goal.BreakBlockGoalMixin failed injection check, (0/1) succeeded. Scanned 1 target(s). Using refmap mixins.arclight.refmap.json",
        "\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [io.izzel.arclight.common.ArclightMain:run:53]: Fail to launch Arclight."
      ],
      "diagnostic_tail": "eeded. Scanned 1 target(s). Using refmap mixins.arclight.refmap.json\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.injection.struct.InjectionInfo.postInject(InjectionInfo.java:468)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinTargetContext.applyInjections(MixinTargetContext.java:1362)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.applyInjections(MixinApplicatorStandard.java:1051)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.applyMixin(MixinApplicatorStandard.java:400)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.apply(MixinApplicatorStandard.java:325)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.TargetClassContext.apply(TargetClassContext.java:383)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.TargetClassContext.applyMixins(TargetClassContext.java:365)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinProcessor.applyMixins(MixinProcessor.java:363)\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \t... 42 more\n\u001b[m\u001b[0m[21:57:37] [main/INFO] [STDERR/]: [io.izzel.arclight.common.ArclightMain:run:53]: Fail to launch Arclight.\n\u001b[m"
    }
  }
}
```
## CatServer vs Mist on J8
```json
{
  "method": "same exact 36 mod + 14 plugin JAR files and same configs/seed; one isolated smoke per hybrid JAR; no production access",
  "limits": "no modded-client login, vehicle gameplay, player load or A/B performance result; successful boot alone is not an upgrade",
  "baseline_zip": "CUANTIC-Server-CatServer-1.7.7.zip",
  "baseline_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "inventory_sha256": "d40f39acaa43f496893bd469953a093df33268e243ee233f0abcc2df6e7d37ca",
  "candidates": {
    "live-CatServer": {
      "same_mod_plugin_payload_sha256": true,
      "smoke": {
        "jar": "CatServer-1.16.5-1d8d6313-server.jar",
        "done_seconds": "7.075",
        "enabled_plugins": 13,
        "plugin_names": [
          "Vault",
          "ProtocolLib",
          "WorldEdit",
          "Chunky",
          "Cuantic-Brand",
          "SkinsRestorer",
          "Essentials",
          "EssentialsChat",
          "EssentialsAntiBuild",
          "EssentialsSpawn",
          "WorldGuard",
          "ClaimChunk",
          "EssentialsProtect"
        ],
        "critical_lines": [],
        "timed_out": false,
        "exit_code_after_stop": 0,
        "handshake_with_real_client": "NOT TESTED",
        "performance_under_players": "NOT TESTED",
        "passed_smoke": false
      },
      "candidate_pack_inventory": null,
      "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
      "required_plugins_enabled": false,
      "qualified_for_performance_A_B": false,
      "diagnostic_key_lines": [
        "Caused by: java.lang.ClassNotFoundException: Failed to remap class me.lucko.luckperms.bukkit.loader.BukkitLoaderPlugin",
        "Caused by: java.lang.UnsupportedClassVersionError: me/lucko/luckperms/bukkit/loader/BukkitLoaderPlugin has been compiled by a more recent version of the Java Runtime (class file version 55.0), this version of the Java Runtime only recognizes class file versions up to 52.0"
      ],
      "diagnostic_tail": "05] [Server thread/INFO]: [WorldGuard] Disabling WorldGuard v7.0.5+3827266\n[21:59:05] [Server thread/INFO]: [WorldGuard] Shutting down executor and cancelling any pending tasks...\n[21:59:05] [Server thread/INFO]: Disabling EssentialsSpawn v2.19.7\n[21:59:05] [Server thread/INFO]: Disabling EssentialsAntiBuild v2.19.7\n[21:59:05] [Server thread/INFO]: Disabling EssentialsChat v2.19.7\n[21:59:05] [Server thread/INFO]: Disabling Essentials v2.19.7\n[21:59:05] [Server thread/INFO]: [Vault] [Economy] Essentials Economy unhooked.\n[21:59:05] [Server thread/INFO]: [SkinsRestorer] Disabling SkinsRestorer v14.2.12\n[21:59:05] [Server thread/INFO]: [WorldEdit] Disabling WorldEdit v7.2.5+57d5ac9\n[21:59:05] [Server thread/INFO]: Unregistering com.sk89q.worldedit.bukkit.BukkitServerInterface from WorldEdit\n[21:59:05] [Server thread/INFO]: [ProtocolLib] Disabling ProtocolLib v4.8.0\n[21:59:05] [Server thread/INFO]: [Vault] Disabling Vault v1.7.3-b131\n[21:59:05] [Server thread/INFO]: [Cuantic-Brand] Disabling Cuantic-Brand v1.7.7\n[21:59:05] [Server thread/INFO]: [Chunky] Disabling Chunky v1.2.217\n[21:59:05] [Server thread/INFO]: Saving players\n[21:59:05] [Server thread/INFO]: Saving worlds\n[21:59:05] [Server thread/INFO]: Saving chunks for level 'ServerLevel[world]'/minecraft:overworld\n[21:59:05] [Server thread/INFO]: ThreadedAnvilChunkStorage (world): All chunks are saved\n[21:59:05] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM-1]'/minecraft:the_nether\n[21:59:05] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM-1): All chunks are saved\n[21:59:05] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM1]'/minecraft:the_end\n[21:59:05] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM1): All chunks are saved\n[21:59:05] [Server thread/INFO]: Saving usercache.json\n"
    },
    "Mist": {
      "same_mod_plugin_payload_sha256": true,
      "smoke": {
        "jar": "CatServer-1.16.5-1d8d6313-server.jar",
        "done_seconds": null,
        "enabled_plugins": 0,
        "plugin_names": [],
        "critical_lines": [],
        "timed_out": true,
        "exit_code_after_stop": 143,
        "handshake_with_real_client": "NOT TESTED",
        "performance_under_players": "NOT TESTED",
        "passed_smoke": false
      },
      "candidate_pack_inventory": {
        "mods": 36,
        "plugins": 14,
        "identical_to_baseline": true,
        "differences": [],
        "root_jars": [
          "mist-1.16.5-33-server.jar"
        ]
      },
      "source_engine": "mist-1.16.5-33-server.jar",
      "jar_sha256": "1c5554d51ac28d7a101d113387f0ad5023618054a03021515924444d75ff06de",
      "required_plugins_enabled": false,
      "qualified_for_performance_A_B": false,
      "diagnostic_key_lines": [],
      "diagnostic_tail": "Mist must be ran using Java 11 to Java 15.\nIf you want to download Java 11 automatically, print 'Yes'. If not, print 'No'.\nThe downloaded Java will be used only for this server installation.\n"
    }
  }
}
```
## Preliminary J8 A/B only if both passed
```json
NOT RUN
```
