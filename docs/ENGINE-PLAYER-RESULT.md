# ENGINE PLAYER — read-only pe JAR-ul live

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38174649414

Nu este comparatie A/B si nu atinge JAR-ul/lumea serverului.

```json
{
  "method": "real player on public live server; read-only status/list/spark; no restart or artificial workload",
  "limits": "single session, no competing JAR, cannot prove speedup",
  "ping_at_start": {
    "version": {
      "name": "CUANTIC 1.16.5",
      "protocol": 754
    },
    "players": {
      "online": 1,
      "max": 25
    }
  },
  "console_list_at_start": 1,
  "live_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "samples": [
    {
      "utc": "2026-10-11T21:01:50Z",
      "players": 1,
      "spark_mspt_min_med_p95_max_10s": [
        1.0,
        1.4,
        2.8,
        12.7
      ],
      "spark_mspt_min_med_p95_max_1m": [
        1.0,
        1.6,
        4.7,
        128.0
      ],
      "rss_mb": 3829.4
    },
    {
      "utc": "2026-10-11T21:02:32Z",
      "players": 1,
      "spark_mspt_min_med_p95_max_10s": [
        1.1,
        1.4,
        2.3,
        3.8
      ],
      "spark_mspt_min_med_p95_max_1m": [
        0.8,
        1.3,
        2.6,
        12.7
      ],
      "rss_mb": 3830.5
    },
    {
      "utc": "2026-10-11T21:03:14Z",
      "players": 1,
      "spark_mspt_min_med_p95_max_10s": [
        0.9,
        1.4,
        2.1,
        6.3
      ],
      "spark_mspt_min_med_p95_max_1m": [
        0.8,
        1.4,
        2.3,
        10.1
      ],
      "rss_mb": 3846.2
    }
  ],
  "status": "COMPLETED: 3 samples with real online player(s), NO JAR changed"
}
```
