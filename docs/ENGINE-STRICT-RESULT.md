# Strict screen — motor CUANTIC sursă modificată vs live și oficial

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38183484524

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
    "boot_done_s": 10.305,
    "boot_wall_seconds": 89.16,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2402.4,
    "rss_peak_mb": 2405.6,
    "rss_steady_median_mb": 2402.4,
    "rss_steady_peak_mb": 2402.9,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.78,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.7,
      0.8,
      1.3,
      14.6
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:26] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c"
  },
  "official-B1": {
    "label": "official-B1",
    "boot_done_s": 10.418,
    "boot_wall_seconds": 87.4,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2550.4,
    "rss_peak_mb": 2551.1,
    "rss_steady_median_mb": 2550.4,
    "rss_steady_peak_mb": 2551.1,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.82,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.5,
      0.8,
      1.4,
      13.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie",
      "[23:19:22] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "patched-C1": {
    "label": "patched-C1",
    "boot_done_s": 10.193,
    "boot_wall_seconds": 85.15,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2202.1,
    "rss_peak_mb": 2216.6,
    "rss_steady_median_mb": 2202.1,
    "rss_steady_peak_mb": 2202.7,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 4.41,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.8,
      1.1,
      1.6,
      17.7
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie",
      "[23:23:15] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "patched-C2": {
    "label": "patched-C2",
    "boot_done_s": 10.71,
    "boot_wall_seconds": 85.89,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2528.9,
    "rss_peak_mb": 2529.4,
    "rss_steady_median_mb": 2528.9,
    "rss_steady_peak_mb": 2529.4,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.72,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.6,
      0.8,
      1.3,
      12.3
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie",
      "[23:27:09] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "b081735815f53e1118608464c39659b537b10fc74fa96458a4a922b7d1215ee3"
  },
  "official-B2": {
    "label": "official-B2",
    "boot_done_s": 10.705,
    "boot_wall_seconds": 89.9,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2487.7,
    "rss_peak_mb": 2488.6,
    "rss_steady_median_mb": 2487.7,
    "rss_steady_peak_mb": 2488.6,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 4.03,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.7,
      0.8,
      1.3,
      15.6
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie",
      "[23:31:07] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true,
    "jar_sha256": "8edea98c597e7af44a45ef9093678c38ca3749d55a71cdff10218c1c6b946fd0"
  },
  "branded-A2": {
    "label": "branded-A2",
    "boot_done_s": 10.644,
    "boot_wall_seconds": 87.89,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2042.4,
    "rss_peak_mb": 2042.9,
    "rss_steady_median_mb": 2042.4,
    "rss_steady_peak_mb": 2042.9,
    "cpu_seconds_during_command_and_warmup": null,
    "cpu_seconds_steady_after_55s": 3.68,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.7,
      0.8,
      1.4,
      13.0
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "64 forced chunks + 40 zombies, no players",
    "ticket_64_confirmed": true,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie",
      "[23:35:03] [Server thread/INFO]: Summoned new Zombie"
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
            2402.4,
            2042.4
          ],
          "official": [
            2550.4,
            2487.7
          ],
          "patched": [
            2202.1,
            2528.9
          ]
        },
        "candidate_worst": 2528.9,
        "best_baseline": 2042.4,
        "pass": false
      },
      "cpu_steady_s": {
        "samples": {
          "branded": [
            3.78,
            3.68
          ],
          "official": [
            3.82,
            4.03
          ],
          "patched": [
            4.41,
            3.72
          ]
        },
        "candidate_worst": 4.41,
        "best_baseline": 3.68,
        "pass": false
      },
      "p95_ms": {
        "samples": {
          "branded": [
            1.3,
            1.4
          ],
          "official": [
            1.4,
            1.3
          ],
          "patched": [
            1.6,
            1.3
          ]
        },
        "candidate_worst": 1.6,
        "best_baseline": 1.3,
        "pass": false
      },
      "boot_internal_done_s": {
        "samples": {
          "branded": [
            10.305,
            10.644
          ],
          "official": [
            10.418,
            10.705
          ],
          "patched": [
            10.193,
            10.71
          ]
        },
        "candidate_worst": 10.71,
        "best_baseline": 10.305,
        "pass": false
      },
      "boot_wall_s": {
        "samples": {
          "branded": [
            89.16,
            87.89
          ],
          "official": [
            87.4,
            89.9
          ],
          "patched": [
            85.15,
            85.89
          ]
        },
        "candidate_worst": 85.89,
        "best_baseline": 87.4,
        "pass": true
      }
    },
    "reason": "REJECT: at least one metric tied or regressed against at least one baseline; do not promote"
  }
}
```
