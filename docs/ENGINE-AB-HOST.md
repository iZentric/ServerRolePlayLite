# ENGINE HOST AB — gazda reala, copii izolate pe :25566

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38122045449
NU este test cu un client real; serverul public :25565 a ramas neatins.

```json
{
  "method": "two PRIVATE copies on the actual live host; live JVM stays up; no real players",
  "disclaimer": "Synthetic workload only. Does NOT establish client handshake or universal superiority.",
  "world_copied": "world",
  "live_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 11.331,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": null,
    "rss_peak_mb": null,
    "spark_tick_min_median_p95_max_ms_1m": null,
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": false,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "command_feedback_last": [],
    "valid": false
  },
  "status": "ABORTED / NO LIVE JAR CHANGED",
  "reason": "baseline-2023 failed isolated boot/spark; no other test run"
}
```
