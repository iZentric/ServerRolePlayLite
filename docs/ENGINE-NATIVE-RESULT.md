# CatServer CUANTIC vs CatServer oficial — benchmark pereche

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38180230255

Sursa oficială: Luohuayu/CatServer release 23.05.26-1 (1.16.5-1d8d6313), LGPL-3.0.
A/B/B/A, Java 17, același pack, același runner; 55s încălzire + 75s măsurare stabilă, fără jucători sau vehicule. Nicio schimbare live.

```json
{
  "method": "A/B/B/A: branded live JAR vs official exact CatServer 1.16.5-1d8d6313; same 36 mods/14 plugins, Java 17, fresh same-seed world, same GH runner, 64 force-loaded chunks, 40 zombies; 55s warmup then 75s steady window",
  "limits": "two samples/arm; zero players/vehicles, synthetic workload; no claim of faster real-world RP or client FPS, no live changes",
  "pack_sha256": "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15",
  "branded_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "official_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0",
  "uncompressed_jar_entries_different": [
    "CUANTIC-ENGINE.txt",
    "data/forge-1.16.5-36.2.39-universal.jar"
  ],
  "branded-A1": {
    "label": "branded-A1",
    "boot_done_s": 9.77,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2205.1,
    "rss_peak_mb": 2205.8,
    "rss_steady_median_mb": 2205.1,
    "rss_steady_peak_mb": 2205.8,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.32,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      0.8,
      1.3,
      11.3
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:03] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "official-B1": {
    "label": "official-B1",
    "boot_done_s": 10.298,
    "boot_wall_seconds": 90.01,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2185.6,
    "rss_peak_mb": 2186.1,
    "rss_steady_median_mb": 2185.6,
    "rss_steady_peak_mb": 2186.1,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.32,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.7,
      1.2,
      13.7
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie",
      "[22:29:01] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "official-B2": {
    "label": "official-B2",
    "boot_done_s": 10.13,
    "boot_wall_seconds": 90.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2475.6,
    "rss_peak_mb": 2476.3,
    "rss_steady_median_mb": 2475.6,
    "rss_steady_peak_mb": 2476.3,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.43,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.7,
      1.2,
      11.5
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie",
      "[22:33:00] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "branded-A2": {
    "label": "branded-A2",
    "boot_done_s": 10.509,
    "boot_wall_seconds": 88.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2451.9,
    "rss_peak_mb": 2452.7,
    "rss_steady_median_mb": 2452.0,
    "rss_steady_peak_mb": 2452.7,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 2.86,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.6,
      1.1,
      14.4
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie",
      "[22:36:56] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "summary": {
    "branded": {
      "cpu_steady_s": {
        "values": [
          3.32,
          2.86
        ],
        "median": 3.09,
        "within_arm_range": 0.46
      },
      "rss_steady_mib": {
        "values": [
          2205.1,
          2452.0
        ],
        "median": 2328.55,
        "within_arm_range": 246.9
      },
      "p95_steady_ms": {
        "values": [
          1.3,
          1.1
        ],
        "median": 1.2,
        "within_arm_range": 0.2
      },
      "boot_done_s": {
        "values": [
          9.77,
          10.509
        ],
        "median": 10.139,
        "within_arm_range": 0.739
      },
      "boot_wall_s": {
        "values": [
          86.02,
          88.02
        ],
        "median": 87.02,
        "within_arm_range": 2.0
      }
    },
    "official": {
      "cpu_steady_s": {
        "values": [
          3.32,
          3.43
        ],
        "median": 3.375,
        "within_arm_range": 0.11
      },
      "rss_steady_mib": {
        "values": [
          2185.6,
          2475.6
        ],
        "median": 2330.6,
        "within_arm_range": 290.0
      },
      "p95_steady_ms": {
        "values": [
          1.2,
          1.2
        ],
        "median": 1.2,
        "within_arm_range": 0.0
      },
      "boot_done_s": {
        "values": [
          10.298,
          10.13
        ],
        "median": 10.214,
        "within_arm_range": 0.168
      },
      "boot_wall_s": {
        "values": [
          90.01,
          90.02
        ],
        "median": 90.015,
        "within_arm_range": 0.01
      }
    }
  },
  "verdict": "TWO-SAMPLE OBSERVATION ONLY: compare within-arm ranges and do not claim 171 MB/6% from historical unpaired minima. No promotion without representative player/vehicle test."
}
```
