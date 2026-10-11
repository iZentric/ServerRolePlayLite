# ENGINE AB GitHub — acelasi runner, lume sintetica, fara jucatori

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38125287891

ATENTIE: nu dovedeste performanta cu jucatori sau handshake-ul clientului!

```json
{
  "method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
  "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 9.279,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2196.2,
    "rss_peak_mb": 2196.3,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.2,
      0.5,
      5.4,
      1457.5
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie",
      "[08:36:42] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  },
  "candidate-2024": {
    "label": "candidate-2024",
    "boot_done_s": 10.456,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2561.3,
    "rss_peak_mb": 2568.7,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.1,
      0.4,
      5.9,
      1254.3
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie",
      "[08:39:48] [Server thread/INFO]: Summoned new Zombie"
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
