# ENGINE AB GitHub — acelasi runner, lume sintetica, fara jucatori

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38121496593

ATENTIE: nu dovedeste performanta cu jucatori sau handshake-ul clientului!

```json
{
  "method": "A then B; same GitHub runner, separate fresh worlds with same seed; one sample each",
  "limits": "synthetic zero-player workload; not real client handshake/TPS with players; no live deployment",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 7.054,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2411.4,
    "rss_peak_mb": 2411.5,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.1,
      2.7,
      706.1
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "command_feedback_last": [
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie",
      "[07:31:37] [Server thread/INFO]: Summoned new Zombie"
    ],
    "valid": true
  },
  "candidate-2024": {
    "label": "candidate-2024",
    "boot_done_s": 6.728,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 2337.5,
    "rss_peak_mb": 2337.5,
    "spark_tick_min_median_p95_max_ms_1m": [
      0.0,
      0.1,
      2.8,
      850.5
    ],
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": true,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "command_feedback_last": [
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie",
      "[07:35:11] [Server thread/INFO]: Summoned new Zombie"
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
