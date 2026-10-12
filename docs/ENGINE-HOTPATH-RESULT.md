# ENGINE HOTPATH — Cuantic source fork, isolated CI, NOT live

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38125287933

Upstream: Luohuayu/CatServer at 1c92118fcca69ffac97a48c8e1f6e1bb861b41d1 (LGPL-3.0). Patch: scripts/patch_catserver_hotpath.py.
No real player handshake, no release, no production promotion.

## Smoke
```json
{
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "done_seconds": "9.616",
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
## Filled hopper A/B
```json
{
  "method": "A/B/C same GitHub runner + exact pack, 256 hoppers with 64 stone items each, 40 zombies, zero players, one sample each",
  "limits": "one synthetic run per arm in order A/B/C, not a modded client handshake or performance with players/vehicles; no deployment",
  "live-CatServer-2023": {
    "label": "live-CatServer-2023",
    "boot_done_s": 9.17,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2550.2,
    "rss_peak_mb": 2556.0,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.2,
      0.7,
      14.7
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie",
      "[08:46:54] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "upstream-CatServer-2024": {
    "label": "upstream-CatServer-2024",
    "boot_done_s": 9.84,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2425.4,
    "rss_peak_mb": 2425.8,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.2,
      2.9,
      16.7
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie",
      "[08:50:23] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "f4936ec1e05912269dc154920805a374a01d079e25fcb49ae286c3e7bd6c8cf9"
  },
  "cuantic-hotpath-2024": {
    "label": "cuantic-hotpath-2024",
    "boot_done_s": 9.788,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2171.6,
    "rss_peak_mb": 2172.0,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.1,
      1.9,
      33.6
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 filled hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": 256,
    "hopper_fill_256_confirmed": true,
    "command_feedback_last": [
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie",
      "[08:54:36] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8876d48f9d2c610a44c3206845d569ce109b372c06daf669af9cb70fccb26bb5"
  },
  "verdict": "no demonstrated p95 win versus BOTH alternatives in this run",
  "p95_delta_vs_live_ms": 1.2,
  "p95_delta_vs_upstream_ms": -1.0
}
```
## Build tail
```
/tmp/cuantic-cat-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                        ^
/tmp/cuantic-cat-source/src/main/java/catserver/server/remapper/MappingLoader.java:84: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
                sun.misc.Unsafe unsafe = (sun.misc.Unsafe) unsafeField.get(null);
                                                  ^
/tmp/cuantic-cat-source/src/main/java/moe/loliserver/utils/EnumHelper.java:171: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
        private static sun.misc.Unsafe unsafe = null;
                               ^
/tmp/cuantic-cat-source/src/main/java/moe/loliserver/utils/EnumHelper.java:188: warning: sun.misc.Unsafe is internal proprietary API and may be removed in a future release
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

BUILD SUCCESSFUL in 2m 36s
21 actionable tasks: 18 executed, 3 up-to-date
```
