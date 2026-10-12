# Referință live pentru migrare — citită, nu măsurată activ

Rulată pe gazda pe care rulează serverul (CHK). Pasul doar citește /proc și live.log:
nu pornește, nu oprește și nu modifică serverul. Portul public 25565 și frpc rămân cum sunt.

```json
{
  "when": "2026-10-12T16:44:30Z",
  "host": "b809acccc0ab",
  "cpu": {
    "model": null,
    "cores": 2,
    "mhz": null,
    "avx2": false
  },
  "disk": {
    "free_gib": 1.7,
    "total_gib": 5.0,
    "used_pct": 66.8
  },
  "micro_ops_s": 236188,
  "source": "/home/mndvasi9/cuantic-live",
  "steal_pct": 0.0,
  "steal_hidden": false,
  "java_pid": 38256,
  "rss_mib": 4794.6,
  "boot_done_s": 12.066,
  "plugins_enabled": 28,
  "cant_keep_up": 0,
  "mods": 36,
  "pack_sha256": "96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c",
  "jar": "CatServer-1.16.5-1d8d6313-server.jar",
  "address": "92.5.171.150:25565"
}
```
