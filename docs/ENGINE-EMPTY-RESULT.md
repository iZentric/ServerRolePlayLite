# ENGINE EMPTY HOPPER — minimal source patch to live CatServer, experimental only

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38127922977

Base source: Luohuayu/CatServer 1d8d63138be77a606df2a5e940b960065948f983, LGPL-3.0. Patch: scripts/patch_catserver_empty_hopper.py.
No real player login, vehicles, or production change.

## Smoke
```json
{
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "done_seconds": "6.868",
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
}
```
## A/B/B/A empty-hopper comparison
```json
{
  "method": "ABBA: live-2023, patched-2023, patched-2023, live-2023; same runner, pack/seed and empty (256 block fill validated) hoppers, no players",
  "limits": "two independent samples per arm, synthetic forced chunk; no modded login, real traffic, vehicles or weak laptop; NEVER deploy automatically",
  "live-A1": {
    "label": "live-A1",
    "boot_done_s": 7.447,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2465.6,
    "rss_peak_mb": 2469.8,
    "cpu_seconds_during_command_and_warmup": 9.29,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.4,
      3.8,
      922.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie",
      "[09:27:33] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "patched-B1": {
    "label": "patched-B1",
    "boot_done_s": 7.423,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2344.4,
    "rss_peak_mb": 2344.5,
    "cpu_seconds_during_command_and_warmup": 9.67,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.3,
      4.5,
      869.1
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:29:59] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "d5e0990ef1d4ebb07ef95d0e9326624308b827928403d2bfdbecce3723f2c011"
  },
  "patched-B2": {
    "label": "patched-B2",
    "boot_done_s": 6.813,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2445.4,
    "rss_peak_mb": 2452.4,
    "cpu_seconds_during_command_and_warmup": 9.92,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.3,
      3.4,
      898.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie",
      "[09:32:23] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "d5e0990ef1d4ebb07ef95d0e9326624308b827928403d2bfdbecce3723f2c011"
  },
  "live-A2": {
    "label": "live-A2",
    "boot_done_s": 7.675,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2424.2,
    "rss_peak_mb": 2433.6,
    "cpu_seconds_during_command_and_warmup": 9.96,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.3,
      3.7,
      962.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie",
      "[09:34:49] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "summary": {
    "live": {
      "p95_ms_median_of_2": 3.75,
      "cpu_seconds_workload_median_of_2": 9.62,
      "rss_median_mb_of_2": 2444.9
    },
    "patched": {
      "p95_ms_median_of_2": 3.95,
      "cpu_seconds_workload_median_of_2": 9.79,
      "rss_median_mb_of_2": 2394.9
    }
  },
  "verdict": "NOT PROVEN BETTER than current CatServer: no live promotion"
}
```
## Build tail
```
                unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                  ^
Note: Some input files use or override a deprecated API.
Note: Recompile with -Xlint:deprecation for details.
Note: Some input files use unchecked or unsafe operations.
Note: Recompile with -Xlint:unchecked for details.
4 warnings

> Task :forge:processResources
> Task :forge:classes
> Task :forge:jar
> Task :forge:reobfJar
> Task :forge:genServerBinPatches
> Task :forge:filterJarNew
> Task :forge:universalJar
> Task :forge:buildCatServer

Deprecated Gradle features were used in this build, making it incompatible with Gradle 8.0.

You can use '--warning-mode all' to show the individual deprecation warnings and determine if they come from your own scripts or plugins.

See https://docs.gradle.org/7.3.3/userguide/command_line_interface.html#sec:command_line_warnings

BUILD SUCCESSFUL in 1m 47s
21 actionable tasks: 18 executed, 3 up-to-date
```
