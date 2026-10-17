== SONDA EXTERNA 25565 ==
{"version": {"name": "Mohist 1.16.5", "protocol": 754}, "players": {"online": 0, "max": 25}}
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-17 12:29:27 UTC — gazda → artefact → relay

```
mod automat din marker: host-info port=x jar=x
== FUNCTITY HOST-INFO (read-only) — 2026-10-17 12:29:09 UTC ==
utilizator: mndvasi9 | HOME=/home/mndvasi9 | hostname: 66df1b1189a9
sistem: Linux 5.4.17-2136.358.2.2.el8uek.aarch64 aarch64 | Oracle Linux Server 8.10
cpu:  | 2 fire
  MemTotal:: 11884 MiB
  MemAvailable:: 5089 MiB
  disc /home/mndvasi9: 4861 MiB folositi din 5110 (96%), liber 250 MiB
java sistem: java version "25.0.4.1" 2026-08-18 LTS
java11: /home/mndvasi9/funcity-live/jdk11/bin/java
node: v20.20.2 | python3: Python 3.9.25 | git: git version 2.43.7
— gazda server (producție):
  director /home/mndvasi9/cuantic-live: 508 MiB total, subdirectoare mari:
    150	/home/mndvasi9/cuantic-live/world
    140	/home/mndvasi9/cuantic-live/libraries
    70	/home/mndvasi9/cuantic-live/snapshot-1791664630.tar.gz
    58	/home/mndvasi9/cuantic-live/plugins
    40	/home/mndvasi9/cuantic-live/foxlaunch-data
    30	/home/mndvasi9/cuantic-live/mods
  lume: 150 MiB | world_nether:  | world_the_end: 
  jar producție: /home/mndvasi9/cuantic-live/CatServer-1.16.5-1d8d6313-server.jar
/home/mndvasi9/cuantic-live/FunCity-1.16.5-b1.0827.jar
  config port/motd/online-mode: max-players=25 motd=FunCity RP Lite - TEST candidat b1.0827 (nu e serverul obisnuit) online-mode=false server-port=25565 
— procese si porturi:
  toate java de pe gazda:
        609    01:21:43 /home/mndvasi9/.local/jdk17/bin/java @unix_args.txt
  ocupanti porturi 25565/25566:
    LISTEN 0      4096               *:25565            *:*    users:(("java",pid=609,fd=112))
  java producție: 609 | supervisor c.sh: 445
  frpc: 560 | port 25565: da | port 25566: nu
  jucatori (din live.log, ultima 'There are'): There are 0 out of maximum 25
  last Done producție: Done (11.827s)
— service supervizare: systemd user: offline
absent | crontab: 0 linii
— spatiu pentru staging+backup: trebuie ~ 2x lumea; liber 250 MiB
(sfarsit rc=0)
RC=0
```
