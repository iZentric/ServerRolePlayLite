# ENGINE PREFLIGHT — 2026-10-11 07:48:51 UTC

```
java: 122012 /home/mndvasi9/.local/jdk17/bin/java @unix_args.txt
supervisor: 121898 bash /home/mndvasi9/c.sh
public tunnel: 121962 /home/mndvasi9/frpc -c /home/mndvasi9/frpc.toml
port 25565: LISTEN 0      4096               *:25565            *:*          
jar: 96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c  /home/mndvasi9/cuantic-live/CatServer-1.16.5-1d8d6313-server.jar
mods / plugins: 36 / 14
disk home + temp:
/dev/sdb1                 5.0G  3.3G  1.8G  65% /home/mndvasi9
/dev/mapper/vg00-usr_tmp  4.9G  203M  4.4G   5% /tmp
memory:
              total        used        free      shared  buff/cache   available
Mem:          11884        5220        4574          71        2089        4879
35M	/home/mndvasi9/cuantic-live/world
voice chat config locations and UDP ports (no secrets):
/home/mndvasi9/cuantic-live/world/serverconfig/voicechat-server.toml
	port = 24454
log cursor: 4448
players (console, current): [07:48:51] [Server thread/INFO]: There are 0 out of maximum 25 players online.
load:  07:48:57 up 21:35,  0 users,  load average: 0.53, 0.48, 0.42
live spark health (idle, no synthetic workload):
> TPS from last 5s, 10s, 1m, 5m, 15m:
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
> CPU usage from last 10s, 1m, 15m:
> Memory usage:
> TPS from last 5s, 10s, 1m, 5m, 15m:
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
> CPU usage from last 10s, 1m, 15m:
> Memory usage:

Note: inspect before any restart; never infer zero players from an empty reply.
```
