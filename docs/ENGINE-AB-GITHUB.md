# ENGINE AB GitHub — acelasi runner, lume sintetica, fara jucatori

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38180230214

ATENTIE: nu dovedeste performanta cu jucatori sau handshake-ul clientului!

```json
{
  "method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
  "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 10.945,
    "boot_wall_seconds": 96.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 1985.7,
    "rss_peak_mb": 2007.8,
    "rss_steady_median_mb": null,
    "rss_steady_peak_mb": null,
    "cpu_seconds_during_command_and_warmup": 14.49,
    "cpu_seconds_steady_after_55s": null,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.5,
      5.5,
      1107.8
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie",
      "[22:25:11] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  },
  "candidate-2024": {
    "label": "candidate-2024",
    "boot_done_s": 10.589,
    "boot_wall_seconds": 94.02,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2384.0,
    "rss_peak_mb": 2384.4,
    "rss_steady_median_mb": null,
    "rss_steady_peak_mb": null,
    "cpu_seconds_during_command_and_warmup": 14.61,
    "cpu_seconds_steady_after_55s": null,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.7,
      4.9,
      1157.8
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie",
      "[22:27:51] [Server thread/INFO]: Summoned new Zombie"
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
