# ENGINE PREFLIGHT — 2026-10-11 21:01:01 UTC

```
java: 6738 /home/mndvasi9/.local/jdk17/bin/java @unix_args.txt
supervisor: 6624 bash /home/mndvasi9/c.sh
public tunnel: 6688 /home/mndvasi9/frpc -c /home/mndvasi9/frpc.toml
port 25565: LISTEN 0      4096               *:25565            *:*          
Minecraft status ping (local only; not client login): {"version": {"name": "CUANTIC 1.16.5", "protocol": 754}, "players": {"online": 1, "max": 25}}
jar: 96f824793ab3a685a390d82305202403ea8cbe5c011a1c79ce0ec024a4d7789c  /home/mndvasi9/cuantic-live/CatServer-1.16.5-1d8d6313-server.jar
mods / plugins: 36 / 14
disk home + temp:
/dev/sdb1                 5.0G  3.3G  1.8G  65% /home/mndvasi9
/dev/mapper/vg00-usr_tmp  4.9G  4.8M  4.6G   1% /tmp
memory:
              total        used        free      shared  buff/cache   available
Mem:          11884        5657        2226          72        4000        4422
35M	/home/mndvasi9/cuantic-live/world
voice chat config locations and UDP ports (no secrets):
/home/mndvasi9/cuantic-live/world/serverconfig/voicechat-server.toml
	port = 24454
log cursor: 5302
players (console, current): [21:01:01] [Server thread/INFO]: There are 1 out of maximum 25 players online.
load:  21:01:07 up  4:50,  0 users,  load average: 1.06, 0.50, 0.19
live spark health (idle, no synthetic workload):
> TPS from last 5s, 10s, 1m, 5m, 15m:
    19.99, 20.0, *20.0, *20.0, *20.0
> Tick durations (min/med/95%ile/max ms) from last 10s, 1m:
    1.4/2.0/6.5/21.4; 0.3/1.9/8.4/1433.4
> CPU usage from last 10s, 1m, 15m:
    38%, 46%, 46%  (system)

Note: inspect before any restart; never infer zero players from an empty reply.
```
