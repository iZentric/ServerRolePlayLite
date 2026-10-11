# Hybrid engine family — same CUANTIC 1.16.5 modpack compatibility

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178055825

GitHub-hosted isolated boots only; the live world and JAR are untouched.
A successful smoke does not prove modded login, vehicle compatibility or speed superiority.

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
        "done_seconds": "9.848",
        "enabled_plugins": 14,
        "plugin_names": [
          "LuckPerms",
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
        "passed_smoke": true
      },
      "candidate_pack_inventory": null,
      "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
      "required_plugins_enabled": true,
      "qualified_for_performance_A_B": true
    },
    "own-ticket-JAR": {
      "same_mod_plugin_payload_sha256": true,
      "smoke": {
        "jar": "CatServer-1.16.5-1d8d6313-server.jar",
        "done_seconds": "9.953",
        "enabled_plugins": 14,
        "plugin_names": [
          "LuckPerms",
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
        "passed_smoke": true
      },
      "candidate_pack_inventory": null,
      "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3",
      "required_plugins_enabled": true,
      "qualified_for_performance_A_B": true
    },
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
      "diagnostic_tail": "eeded. Scanned 1 target(s). Using refmap mixins.arclight.refmap.json\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.injection.struct.InjectionInfo.postInject(InjectionInfo.java:468)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinTargetContext.applyInjections(MixinTargetContext.java:1362)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.applyInjections(MixinApplicatorStandard.java:1051)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.applyMixin(MixinApplicatorStandard.java:400)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinApplicatorStandard.apply(MixinApplicatorStandard.java:325)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.TargetClassContext.apply(TargetClassContext.java:383)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.TargetClassContext.applyMixins(TargetClassContext.java:365)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \tat org.spongepowered.asm.mixin.transformer.MixinProcessor.applyMixins(MixinProcessor.java:363)\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [java.lang.Throwable:printStackTrace:682]: \t... 42 more\n\u001b[m\u001b[0m[21:55:21] [main/INFO] [STDERR/]: [io.izzel.arclight.common.ArclightMain:run:53]: Fail to launch Arclight.\n\u001b[m"
    },
    "Mist": {
      "same_mod_plugin_payload_sha256": true,
      "smoke": {
        "jar": "CatServer-1.16.5-1d8d6313-server.jar",
        "done_seconds": null,
        "enabled_plugins": 0,
        "plugin_names": [],
        "critical_lines": [],
        "timed_out": false,
        "exit_code_after_stop": 1,
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
      "diagnostic_tail": "d update to fix recent bugs ! (https://github.com/MinecraftMist/Mist/releases)\n2026-10-11 21:55:56,249 main WARN Advanced terminal features are not available in this environment\n[21:55:56 INFO]: ModLauncher running: args [--gameDir, ., --launchTarget, fmlserver, --fml.forgeVersion, 36.2.4, --fml.mcpVersion, 20210115.111550, --fml.mcVersion, 1.16.5, --fml.forgeGroup, net.minecraftforge, nogui]\n[21:55:56 INFO]: ModLauncher 8.0.9+86+master.3cf110c starting: java version 17.0.20.1 by Eclipse Adoptium\nException in thread \"main\" java.lang.IllegalAccessError: class cpw.mods.modlauncher.SecureJarHandler (in unnamed module @0x1a32f1f1) cannot access class sun.security.util.ManifestEntryVerifier (in module java.base) because module java.base does not export sun.security.util to unnamed module @0x1a32f1f1\n\tat cpw.mods.modlauncher.SecureJarHandler.lambda$static$1(SecureJarHandler.java:41)\n\tat cpw.mods.modlauncher.api.LamdbaExceptionUtils.uncheck(LamdbaExceptionUtils.java:95)\n\tat cpw.mods.modlauncher.SecureJarHandler.<clinit>(SecureJarHandler.java:41)\n\tat cpw.mods.modlauncher.Launcher.lambda$new$6(Launcher.java:55)\n\tat java.base/java.util.concurrent.ConcurrentHashMap.computeIfAbsent(ConcurrentHashMap.java:1708)\n\tat cpw.mods.modlauncher.api.TypesafeMap.computeIfAbsent(TypesafeMap.java:52)\n\tat cpw.mods.modlauncher.api.TypesafeMap.computeIfAbsent(TypesafeMap.java:47)\n\tat cpw.mods.modlauncher.Environment.computePropertyIfAbsent(Environment.java:62)\n\tat cpw.mods.modlauncher.Launcher.<init>(Launcher.java:55)\n\tat cpw.mods.modlauncher.Launcher.main(Launcher.java:66)\n\tat net.minecraftforge.server.ServerMain$Runner.runLauncher(ServerMain.java:109)\n\tat net.minecraftforge.server.ServerMain$Runner.access$100(ServerMain.java:106)\n\tat net.minecraftforge.server.ServerMain.main(ServerMain.java:103)\n"
    }
  }
}
```
