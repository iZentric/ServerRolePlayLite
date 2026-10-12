# ENGINE TICKET — Spark-guided JAR prototype, experimental

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38175428475

Exact-source CatServer LGPL-3.0; patch: patches/engine-ticket/SortedArraySet.java.patch.
No real player or vehicles in A/B. Live JAR unchanged. No promotion without repeatable win and player testing.

## Smoke
```json
{
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "done_seconds": "7.470",
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
## ABBA 64 force-loaded chunks
```json
{
  "method": "ABBA same machine: original CatServer, optimized SortedArraySet, optimized, original; isolated 64 forced chunks + 40 zombies; no players",
  "limits": "2 runs/arm on fresh worlds, no modded player login, driving, production world, or real traffic; experimental JAR NEVER promoted automatically",
  "live-A1": {
    "label": "live-A1",
    "boot_done_s": 7.578,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2616.9,
    "rss_peak_mb": 2626.9,
    "cpu_seconds_during_command_and_warmup": 19.63,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      0.8,
      6.2,
      2310.6
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie",
      "[21:20:51] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "patched-B1": {
    "label": "patched-B1",
    "boot_done_s": 7.748,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2576.2,
    "rss_peak_mb": 2587.9,
    "cpu_seconds_during_command_and_warmup": 19.13,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      0.9,
      5.3,
      2296.8
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie",
      "[21:23:13] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "patched-B2": {
    "label": "patched-B2",
    "boot_done_s": 8.009,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2591.6,
    "rss_peak_mb": 2591.7,
    "cpu_seconds_during_command_and_warmup": 19.71,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      1.0,
      4.4,
      2394.8
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie",
      "[21:25:33] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "live-A2": {
    "label": "live-A2",
    "boot_done_s": 8.268,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2204.1,
    "rss_peak_mb": 2207.3,
    "cpu_seconds_during_command_and_warmup": 18.97,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.5,
      0.9,
      5.6,
      2372.5
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie",
      "[21:28:02] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "summary": {
    "live": {
      "p95_ms_median_of_2": 5.9,
      "cpu_seconds_median_of_2": 19.3,
      "rss_mb_median_of_2": 2410.5
    },
    "patched": {
      "p95_ms_median_of_2": 4.85,
      "cpu_seconds_median_of_2": 19.42,
      "rss_mb_median_of_2": 2583.9
    }
  },
  "verdict": "NOT PROVEN BETTER than live JAR; no promotion"
}
```
## Build tail
```
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

BUILD SUCCESSFUL in 2m 5s
21 actionable tasks: 18 executed, 3 up-to-date
```
