# ENGINE CURRENT — real source patch to live CatServer, experimental only

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38126700415

Base source: Luohuayu/CatServer 1d8d63138be77a606df2a5e940b960065948f983, LGPL-3.0. Patch: scripts/patch_catserver_current.py.
No real player login, vehicles, or production change.

## Smoke
```json
{
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "done_seconds": "6.637",
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
## A/B/B/A filled-hopper comparison
```json
{
  "method": "ABBA: live-2023, patched-2023, patched-2023, live-2023; same runner, same pack/seed and filled-hopper commands (256/256 validated), no players",
  "limits": "two independent samples per arm, synthetic forced chunk; no modded login, real traffic, vehicles or weak laptop; NEVER deploy automatically",
  "live-A1": {
    "label": "live-A1",
    "boot_done_s": 6.049,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2275.4,
    "rss_peak_mb": 2291.1,
    "cpu_seconds_during_command_and_warmup": 8.8,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.1,
      0.4,
      9.3
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie",
      "[09:06:19] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "patched-B1": {
    "label": "patched-B1",
    "boot_done_s": 5.807,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2596.9,
    "rss_peak_mb": 2604.5,
    "cpu_seconds_during_command_and_warmup": 9.44,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.3,
      0.7,
      8.4
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie",
      "[09:09:21] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "ddd8ec9804524ad1a7c6abd9b04ffd3194726f75bac9a92ab5ac55e8d70db747"
  },
  "patched-B2": {
    "label": "patched-B2",
    "boot_done_s": 6.018,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2724.1,
    "rss_peak_mb": 2728.1,
    "cpu_seconds_during_command_and_warmup": 9.88,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.3,
      0.8,
      8.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie",
      "[09:12:41] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "ddd8ec9804524ad1a7c6abd9b04ffd3194726f75bac9a92ab5ac55e8d70db747"
  },
  "live-A2": {
    "label": "live-A2",
    "boot_done_s": 5.702,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2654.9,
    "rss_peak_mb": 2655.4,
    "cpu_seconds_during_command_and_warmup": 8.93,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.1,
      0.5,
      7.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie",
      "[09:15:59] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "summary": {
    "live": {
      "p95_ms_median_of_2": 0.45,
      "cpu_seconds_workload_median_of_2": 8.87,
      "rss_median_mb_of_2": 2465.15
    },
    "patched": {
      "p95_ms_median_of_2": 0.75,
      "cpu_seconds_workload_median_of_2": 9.66,
      "rss_median_mb_of_2": 2660.5
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

BUILD SUCCESSFUL in 1m 37s
21 actionable tasks: 18 executed, 3 up-to-date
```
