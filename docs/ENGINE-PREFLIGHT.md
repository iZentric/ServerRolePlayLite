# ENGINE PREFLIGHT — 2026-10-11 22:16:21 UTC

```
java: 13346 /home/mndvasi9/.local/jdk17/bin/java @unix_args.txt
supervisor: 13232 bash /home/mndvasi9/c.sh
public tunnel: 13296 /home/mndvasi9/frpc -c /home/mndvasi9/frpc.toml
port 25565: LISTEN 0      4096               *:25565            *:*          
Minecraft status ping (local only; not client login): {"version": {"name": "CUANTIC 1.16.5", "protocol": 754}, "players": {"online": 0, "max": 25}}
jar: 96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c  /home/mndvasi9/cuantic-live/CatServer-1.16.5-1d8d6313-server.jar
mods / plugins: 36 / 14
disk home + temp:
/dev/sdb1                 5.0G  3.3G  1.8G  65% /home/mndvasi9
/dev/mapper/vg00-usr_tmp  4.9G  7.5M  4.6G   1% /tmp
memory:
              total        used        free      shared  buff/cache   available
Mem:          11884        5200        2878          71        3805        4880
51M	/home/mndvasi9/cuantic-live/world
voice chat config locations and UDP ports (no secrets):
/home/mndvasi9/cuantic-live/world/serverconfig/voicechat-server.toml
	port = 24454
log cursor: 5947
players (console, current): [22:16:21] [Server thread/INFO]: There are 0 out of maximum 25 players online.
load:  22:16:27 up  6:06,  0 users,  load average: 1.09, 0.54, 0.28
live spark health (idle, no synthetic workload):
> TPS from last 5s, 10s, 1m, 5m, 15m:
    20.0, 20.0, *20.0, *20.0, *20.0
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
    0.1/0.2/0.3/19.5; 0.1/0.2/0.6/191.7
> CPU usage from last 10s, 1m, 15m:
    25%, 27%, 27%  (system)
> TPS from last 5s, 10s, 1m, 5m, 15m:
    *20.0, *20.0, *20.0, *20.0, *20.0
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
    0.1/0.2/0.3/19.5; 0.1/0.2/0.6/191.7
> CPU usage from last 10s, 1m, 15m:
    12%, 26%, 26%  (system)

Note: inspect before any restart; never infer zero players from an empty reply.
```
