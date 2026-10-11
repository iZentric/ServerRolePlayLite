# ENGINE HOST AB — gazda reala, copii izolate pe :25566

Run: https://github.com/iZentric/ServerRolePlayLite/actions/runs/38122173323
NU este test cu un client real; serverul public :25565 a ramas neatins.

```json
{
  "method": "two PRIVATE copies on the actual live host; live JVM stays up; no real players",
  "disclaimer": "Synthetic workload only. Does NOT establish client handshake or universal superiority.",
  "world_copied": "world",
  "live_jar_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "baseline-2023": {
    "label": "baseline-2023",
    "boot_done_s": 11.798,
    "plugins_enabled": 14,
    "mods_on_disk": 36,
    "rss_median_mb": 1859.2,
    "rss_peak_mb": 1859.2,
    "spark_tick_min_median_p95_max_ms_1m": null,
    "critical_errors": [],
    "exit_code": 0,
    "clean_stop": false,
    "synthetic_workload_requested": "one forced chunk + 256 empty hoppers + 40 zombies, no players",
    "command_feedback_last": [],
    "valid": false,
    "log_tail_on_failure": [
      "[07:42:24] [Server thread/INFO]: Successfully initialized RadioManager",
      "[07:42:24] [Server thread/WARN]: Dedicated server took 85.95 seconds to load",
      "[07:42:25] [VoiceChatServerThread/ERROR]: Failed to run voice chat at UDP port 24454, make sure no other application is running at that port",
      "[07:42:25] [VoiceChatServerThread/ERROR]: Voice chat server error Address already in use",
      "[07:42:25] [VoiceChatServerThread/ERROR]: Shutting down server",
      "[07:42:25] [Server thread/INFO]: Essentials found a compatible payment resolution method: Vault Compatibility Layer (v1.7.3-b131)!",
      "[07:42:25] [Craft Scheduler Thread - 3/INFO]: Fetching version information...",
      "[07:42:25] [Craft Scheduler Thread - 2/INFO]: [Vault] Checking for Updates ... ",
      "[07:42:25] [Server thread/INFO]: Shutting down locating executor service",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m----------------------------------------------\u001b[0;39m",
      "[07:42:25] [Server thread/INFO]: Saved 0 license plates",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    +===================+\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    |   SkinsRestorer   |\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    |-------------------|\u001b[0;39m",
      "[07:42:25] [Server thread/INFO]: CarClear: 0 | true",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    |  \u001b[34;1m\u001b[4m\u001b[21mStandalone Mode\u001b[0;39m\u001b[32;1m  |\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    +===================+\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m----------------------------------------------\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[36;1m    Version: \u001b[32;1m15.12.6\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[36;1m    Commit: \u001b[32;1mc8c321f\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m    This is the latest version!\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[32;1m----------------------------------------------\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[34;1mDo you have issues? Read our troubleshooting guide: \u001b[33;1mhttps://skinsrestorer.net/docs/troubleshooting\u001b[0;39m",
      "[07:42:25] [Craft Scheduler Thread - 1/INFO]: \u001b[33;1m[\u001b[32;22mSkinsRestorer\u001b[33;1m] \u001b[0;39m\u001b[34;1mWant to support SkinsRestorer or receive priority support? Become a supporter: \u001b[33;1mhttps://skinsrestorer.net/pricing\u001b[0;39m",
      "[07:42:25] [Server thread/INFO]: Stopping server",
      "[07:42:25] [Server thread/INFO]: Unregistering com.sk89q.worldedit.bukkit.BukkitServerInterface from WorldEdit",
      "[07:42:25] [Server thread/INFO]: Saving players",
      "[07:42:25] [Server thread/INFO]: Saving worlds",
      "[07:42:25] [Server thread/INFO]: Saving chunks for level 'ServerLevel[world]'/minecraft:overworld",
      "[07:42:25] [Server thread/INFO]: ThreadedAnvilChunkStorage (world): All chunks are saved",
      "[07:42:25] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM-1]'/minecraft:the_nether",
      "[07:42:25] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM-1): All chunks are saved",
      "[07:42:25] [Server thread/INFO]: Saving chunks for level 'ServerLevel[DIM1]'/minecraft:the_end",
      "[07:42:25] [Server thread/INFO]: ThreadedAnvilChunkStorage (DIM1): All chunks are saved",
      "[07:42:25] [Server thread/INFO]: Saving usercache.json"
    ]
  },
  "status": "ABORTED / NO LIVE JAR CHANGED",
  "reason": "baseline-2023 failed isolated boot/spark; no other test run"
}
```
