== SONDA EXTERNA (hosted, post-raport) ==
{"version": {"name": "CUANTIC 1.16.5", "protocol": 754}, "players": {"online": 1, "max": 25}}

# FUNCTITY-STAGE 2026-10-14 10:47:50 UTC — gazda → artefact → relay

```
mod automat din marker: host-info port=25565 jar=identicare
== FUNCTITY HOST-INFO (read-only) — 2026-10-14 10:47:35 UTC ==
utilizator: mndvasi9 | HOME=/home/mndvasi9 | hostname: b927eb1d45a4
sistem: Linux 5.4.17-2136.358.2.2.el8uek.aarch64 aarch64 | Oracle Linux Server 8.10
cpu:  | 2 fire
  MemTotal:: 11884 MiB
  MemAvailable:: 4528 MiB
  disc /home/mndvasi9: 4435 MiB folositi din 5110 (87%), liber 676 MiB
java sistem: java version "25.0.4.1" 2026-08-18 LTS
java11: /home/mndvasi9/funcity-live/jdk11/bin/java
node: v20.20.2 | python3: Python 3.9.25 | git: git version 2.43.7
— gazda server (producție):
  director /home/mndvasi9/cuantic-live: 440 MiB total, subdirectoare mari:
    150	/home/mndvasi9/cuantic-live/world
    83	/home/mndvasi9/cuantic-live/libraries
    70	/home/mndvasi9/cuantic-live/snapshot-1791664630.tar.gz
    55	/home/mndvasi9/cuantic-live/plugins
    40	/home/mndvasi9/cuantic-live/foxlaunch-data
    30	/home/mndvasi9/cuantic-live/mods
  lume: 150 MiB | world_nether:  | world_the_end: 
  jar producție: /home/mndvasi9/cuantic-live/CatServer-1.16.5-1d8d6313-server.jar
  config port/motd/online-mode: max-players=25 motd=\u00A7b\u00A7lCUANTIC \u00A78\u00A7o1.7.7 \u00A7f| \u00A7aorice PC, zero lag \u00A7f| \u00A7dOras+Survival+Claims \u00A7f| \u00A7ecost 0 online-mode=false server-port=25565 
— procese si porturi:
  toate java de pe gazda:
      32144       17:08 /home/mndvasi9/.local/jdk17/bin/java @unix_args.txt
  ocupanti porturi 25565/25566:
    LISTEN 0      4096               *:25565            *:*    users:(("java",pid=32144,fd=30))
  java producție: 32144 | supervisor c.sh: 32030
  frpc: 32094 | port 25565: da | port 25566: nu
  jucatori (din live.log, ultima 'There are'): There are 0 out of maximum 25
  last Done producție: Done (11.827s)
— service supervizare: systemd user: offline
absent | crontab: 0 linii
— spatiu pentru staging+backup: trebuie ~ 2x lumea; liber 676 MiB
(sfarsit rc=0)
RC=0
```
