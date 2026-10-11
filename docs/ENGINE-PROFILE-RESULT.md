# Profil CPU CUANTIC — server live, fara restart

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38174830546
Nu este o comparatie intre motoare.

```json
{
  "method": "60s CPU sampling on unchanged live CatServer while a human is online",
  "limits": "diagnostic profile, NOT an A/B or faster JAR",
  "players_at_start": 1,
  "players_at_end": 1,
  "spark_urls": [],
  "spark_messages": [
    "[21:04:25] [spark-worker-pool-1-thread-1/INFO]: [⚡] Expected flag at position 0 but got 'start' instead!",
    "[21:04:31] [spark-worker-pool-1-thread-4/INFO]: [⚡] Expected flag at position 0 but got 'start' instead!",
    "[21:05:37] [spark-worker-pool-1-thread-1/INFO]: [⚡] Expected flag at position 0 but got 'stop' instead!",
    "[21:05:47] [spark-worker-pool-1-thread-2/INFO]: [⚡] Expected flag at position 0 but got 'stop' instead!"
  ],
  "status": "PROFILE NOT EXPORTED; inspect spark messages"
}
```
