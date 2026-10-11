# Strict screen — motor CUANTIC sursă modificată vs live și oficial

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38181841511

JAR candidat recompilabil din patch-ul [SortedArraySet](../patches/engine-ticket/SortedArraySet.java.patch) (run 38175428475), NU doar branding.

Același pack 36/14, Java 17, seed, runner. Două probe per variantă; 64 chunkuri forțate + 40 zombie, fără jucători/vehicule.

Criteriu: **cea mai slabă probă a candidatului < cea mai bună probă a ambelor baseline-uri pentru fiecare din RSS stabil, CPU stabil, p95, Done intern, boot extern**. Egal sau mai slab în ORICARE metrică => respins. Un PASS sintetic NU autorizează lansarea: necesită scenarii repetate și login/client modat cu vehicule.

Niciun JAR live/release schimbat. „Mai bun decât orice motor pe orice sarcină” nu poate fi dovedit prin probe finite.

```json
{
  "method": "A/B/C/C/B/A; same runner Java17, same release pack, -Xms1G -Xmx3G, seed and 64 forced chunks + 40 zombies; 55s warmup/75s steady, fresh world per run",
  "limits": "two samples per arm; zero players/vehicles; synthetic *screen* not proof of universal superiority, stability or FPS; production release forbidden without real modded player + vehicles",
  "pack_sha256": "fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15",
  "official_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0",
  "candidate_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3",
  "branded-A1": {
    "label": "branded-A1",
    "boot_done_s": 10.547,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2239.9,
    "rss_peak_mb": 2246.9,
    "rss_steady_median_mb": 2246.4,
    "rss_steady_peak_mb": 2246.9,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.58,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.6,
      1.1,
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
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie",
      "[22:49:36] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "official-B1": {
    "label": "official-B1",
    "boot_done_s": 9.717,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2102.5,
    "rss_peak_mb": 2103.0,
    "rss_steady_median_mb": 2102.6,
    "rss_steady_peak_mb": 2103.0,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.88,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.7,
      1.2,
      14.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie",
      "[22:53:30] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "patched-C1": {
    "label": "patched-C1",
    "boot_done_s": 9.911,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2182.9,
    "rss_peak_mb": 2183.5,
    "rss_steady_median_mb": 2183.0,
    "rss_steady_peak_mb": 2183.5,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 2.87,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.5,
      1.0,
      14.7
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie",
      "[22:57:25] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "patched-C2": {
    "label": "patched-C2",
    "boot_done_s": 9.846,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2478.9,
    "rss_peak_mb": 2479.4,
    "rss_steady_median_mb": 2478.9,
    "rss_steady_peak_mb": 2479.4,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.14,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.6,
      1.0,
      15.5
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:01:19] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "official-B2": {
    "label": "official-B2",
    "boot_done_s": 10.025,
    "boot_wall_seconds": 86.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2201.9,
    "rss_peak_mb": 2202.8,
    "rss_steady_median_mb": 2201.9,
    "rss_steady_peak_mb": 2202.8,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.21,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.6,
      1.1,
      15.1
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie",
      "[23:05:13] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "branded-A2": {
    "label": "branded-A2",
    "boot_done_s": 9.879,
    "boot_wall_seconds": 98.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2367.6,
    "rss_peak_mb": 2368.5,
    "rss_steady_median_mb": 2367.6,
    "rss_steady_peak_mb": 2368.5,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 4.27,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.4,
      0.7,
      1.2,
      13.6
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:09:19] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "screen": {
    "synthetic_screen_pass": false,
    "checks": {
      "rss_steady_median_mb": {
        "samples": {
          "branded": [
            2246.4,
            2367.6
          ],
          "official": [
            2102.6,
            2201.9
          ],
          "patched": [
            2183.0,
            2478.9
          ]
        },
        "candidate_worst": 2478.9,
        "best_baseline": 2102.6,
        "pass": false
      },
      "cpu_steady_s": {
        "samples": {
          "branded": [
            3.58,
            4.27
          ],
          "official": [
            3.88,
            3.21
          ],
          "patched": [
            2.87,
            3.14
          ]
        },
        "candidate_worst": 3.14,
        "best_baseline": 3.21,
        "pass": true
      },
      "p95_ms": {
        "samples": {
          "branded": [
            1.1,
            1.2
          ],
          "official": [
            1.2,
            1.1
          ],
          "patched": [
            1.0,
            1.0
          ]
        },
        "candidate_worst": 1.0,
        "best_baseline": 1.1,
        "pass": true
      },
      "boot_internal_done_s": {
        "samples": {
          "branded": [
            10.547,
            9.879
          ],
          "official": [
            9.717,
            10.025
          ],
          "patched": [
            9.911,
            9.846
          ]
        },
        "candidate_worst": 9.911,
        "best_baseline": 9.717,
        "pass": false
      },
      "boot_wall_s": {
        "samples": {
          "branded": [
            86.02,
            98.02
          ],
          "official": [
            86.02,
            86.02
          ],
          "patched": [
            86.02,
            86.02
          ]
        },
        "candidate_worst": 86.02,
        "best_baseline": 86.02,
        "pass": false
      }
    },
    "reason": "REJECT: at least one metric tied or regressed against at least one baseline; do not promote"
  }
}
```
