# RAM-TEST CUANTIC — 2026-10-09 23:37:14 UTC

```
== dupa (xmx=8G, incalzire 120s) ==
list:   [23:36:40] [Server thread/INFO]: There are 1 out of maximum 25 players online. [23:36:40] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     1.2/1.6/9.1/29.5; 0.2/1.7/12.5/1343.2  > CPU usage from last 10s, 1m, 15m:     19%, 26%, 19%  (system)     18%, 25%, 18%  (process)  > Memory usage:     1.2 GB / 8.0 GB   (14%)     [┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     8.2 KB/s / 14 pps (lo rx)     8.2 KB/s / 14 pps (lo tx)     337.0 bytes/s / 2 pps (eth0 rx)     290.0 bytes/s / 2 pps (eth0 tx) 
gc:     > Garbage Collector statistics      G1 Young Generation collector:       111.38 ms avg, 8 total collections       21s avg frequency      G1 Old Generation collector:       0 collections 
jcmd:    garbage-first heap   total 4390912K, used 1264556K [0x0000000600000000, 0x0000000800000000)   region size 8192K, 73 young (598016K), 3 survivors (24576K)  Metaspace       used 196965K, committed 199104K, reserved 1245184K   class space    used 32615K, committ
proc:   VmHWM:	 3366976 kB VmRSS:	 3366976 kB 
os:     libera=3988MB totala=11884MB
keepup: total=0
flags:  == inainte == -Xms512M -Xmx2G -XX:+UseG1GC -Xms512M -Xmx2G dupa: -Xms512M -Xmx8G  
```

## cum se compara cu proba de dinainte (-Xmx2G, tot cu jucator in lume)
```
2G  : MSPT 1.6/2.4/4.9/12.5 ms · GC Young 47.2 ms mediu, 25 colectari · G1 Old 0 · heap 743MB/2GB · RSS 2613MB (varf 2.59GB) · keep-up 0
8G : vezi block-ul de mai sus
```
