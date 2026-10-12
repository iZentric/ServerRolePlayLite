# ENGINE TICKET — steady-state follow-up

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38176647079
Candidate from build run 38175428475; same unmodified production pack in a disposable GitHub VM.
No players, driving, or production world. Live JAR unchanged.

CPU window begins after 55s warmup and lasts 75s; Spark 1m p95 sampled near the end.

```json
{
  "method": "ABBA same machine: original CatServer, optimized SortedArraySet, optimized, original; isolated 64 forced chunks + 40 zombies; no players",
  "limits": "2 runs/arm on fresh worlds, no modded player login, driving, production world, or real traffic; experimental JAR NEVER promoted automatically",
  "live-A1": {
    "label": "live-A1",
    "boot_done_s": 9.893,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2094.9,
    "rss_peak_mb": 2095.4,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.74,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.5,
      0.8,
      1.3,
      16.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:32:15] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "patched-B1": {
    "label": "patched-B1",
    "boot_done_s": 9.893,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2166.2,
    "rss_peak_mb": 2167.0,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.73,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      0.8,
      1.4,
      12.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie",
      "[21:36:17] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "patched-B2": {
    "label": "patched-B2",
    "boot_done_s": 9.835,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2161.7,
    "rss_peak_mb": 2167.3,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.46,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.7,
      1.1,
      15.3
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie",
      "[21:40:15] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "live-A2": {
    "label": "live-A2",
    "boot_done_s": 9.849,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2186.7,
    "rss_peak_mb": 2187.1,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 4.01,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.7,
      1.1,
      15.2
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie",
      "[21:44:11] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "summary": {
    "live": {
      "p95_ms_median_of_2": 1.2,
      "cpu_seconds_steady_median_of_2": 3.875,
      "rss_mb_median_of_2": 2140.8
    },
    "patched": {
      "p95_ms_median_of_2": 1.25,
      "cpu_seconds_steady_median_of_2": 3.595,
      "rss_mb_median_of_2": 2163.95
    }
  },
  "verdict": "NOT PROVEN BETTER than live JAR; no promotion"
}
```
