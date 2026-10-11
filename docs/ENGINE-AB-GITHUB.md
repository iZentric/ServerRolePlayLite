# ENGINE AB GitHub — acelasi runner, lume sintetica, fara jucatori

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38183484565

ATENTIE: nu dovedeste performanta cu jucatori sau handshake-ul clientului!

```json
{
  "method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
  "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 11.31,
    "boot_wall_seconds": 104.69,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2069.3,
    "rss_peak_mb": 2071.4,
    "rss_steady_median_mb": null,
    "rss_steady_peak_mb": null,
    "cpu_seconds_during_command_and_warmup": 14.44,
    "cpu_seconds_steady_after_55s": null,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.3,
      0.5,
      7.1,
      1360.4
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie",
      "[23:15:37] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  },
  "candidate-2024": {
    "label": "candidate-2024",
    "boot_done_s": 10.336,
    "boot_wall_seconds": 96.15,
    "boot_wall_poll_interval_seconds": 0.25,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2443.6,
    "rss_peak_mb": 2447.6,
    "rss_steady_median_mb": null,
    "rss_steady_peak_mb": null,
    "cpu_seconds_during_command_and_warmup": 15.54,
    "cpu_seconds_steady_after_55s": null,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.2,
      0.6,
      6.6,
      1475.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie",
      "[23:18:19] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  }
}
```

Erori la finalul fiecarei probe:
## engine-ab-results/baseline-2023.log
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
## engine-ab-results/candidate-2024.log
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
