# ENGINE AB GitHub — acelasi runner, lume sintetica, fara jucatori

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38175422809

ATENTIE: nu dovedeste performanta cu jucatori sau handshake-ul clientului!

```json
{
  "method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
  "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 7.415,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2530.3,
    "rss_peak_mb": 2540.1,
    "cpu_seconds_during_command_and_warmup": 10.23,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.2,
      0.4,
      4.0,
      1095.9
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie",
      "[21:14:14] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  },
  "candidate-2024": {
    "label": "candidate-2024",
    "boot_done_s": 7.279,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2616.2,
    "rss_peak_mb": 2616.3,
    "cpu_seconds_during_command_and_warmup": 9.94,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.2,
      0.4,
      4.1,
      937.4
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "ticket_64_confirmed": null,
    "hopper_data_merge_responses": null,
    "hopper_fill_256_confirmed": null,
    "command_feedback_last": [
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie",
      "[21:16:34] [Server thread/INFO]: Summoned new Zombie"
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
