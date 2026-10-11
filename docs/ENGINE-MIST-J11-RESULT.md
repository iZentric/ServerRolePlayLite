# CatServer vs Mist — same pack and Java 11

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38178847794

Mist launch screen requires Java 11–15; both arms use J11 here. Only isolated GitHub VMs.
No Forge client login, human player, city traffic, vehicle driving or live JAR change.

## Compatibility gate
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
        "done_seconds": "11.411",
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
      "diagnostic_key_lines": [
        "Exception in thread \"main\" [22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: java.lang.NoSuchMethodError: 'void sun.security.util.ManifestEntryVerifier.<init>(java.util.jar.Manifest)'"
      ],
      "diagnostic_tail": "oup:uncaughtException:1050]: \tat cpw.mods.modlauncher.TransformingClassLoader.loadClass(TransformingClassLoader.java:98)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat java.base/java.lang.ClassLoader.loadClass(ClassLoader.java:527)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat java.base/java.lang.Class.forName0(Native Method)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat java.base/java.lang.Class.forName(Class.java:398)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat net.minecraftforge.fml.loading.FMLServerLaunchProvider.lambda$launchService$0(FMLServerLaunchProvider.java:51)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat cpw.mods.modlauncher.LaunchServiceHandlerDecorator.launch(LaunchServiceHandlerDecorator.java:37)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat cpw.mods.modlauncher.LaunchServiceHandler.launch(LaunchServiceHandler.java:54)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat cpw.mods.modlauncher.LaunchServiceHandler.launch(LaunchServiceHandler.java:72)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat cpw.mods.modlauncher.Launcher.run(Launcher.java:82)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat cpw.mods.modlauncher.Launcher.main(Launcher.java:66)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat net.minecraftforge.server.ServerMain$Runner.runLauncher(ServerMain.java:109)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat net.minecraftforge.server.ServerMain$Runner.access$100(ServerMain.java:106)\n[22:05:49 INFO]: [java.lang.ThreadGroup:uncaughtException:1050]: \tat net.minecraftforge.server.ServerMain.main(ServerMain.java:103)\n"
    }
  }
}
```
## Equal-runtime A/B/B/A, only if both passed
```json
NOT RUN
```
