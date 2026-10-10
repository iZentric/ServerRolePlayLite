# RAM-TEST CUANTIC — 2026-10-10 13:31:25 UTC

```
== dupa (xmx=8G, incalzire 120s) ==
list:   [13:30:54] [Server thread/INFO]: There are 1 out of maximum 25 players online. [13:30:54] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     2.8/3.8/12.2/28.6; 0.7/3.6/16.5/962.2  > CPU usage from last 10s, 1m, 15m:     17%, 19%, 30%  (system)     16%, 17%, 29%  (process)  > Memory usage:     2.0 GB / 11.6 GB   (16%)     [┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     325.0 bytes/s / 0 pps (lo rx)     325.0 bytes/s / 0 pps (lo tx)     453.0 bytes/s / 3 pps (eth0 rx)     398.0 bytes/s / 3 pps (eth0 tx) 
gc:     > Garbage Collector statistics      G1 Young Generation collector:       140.5 ms avg, 6 total collections       20s avg frequency      G1 Old Generation collector:       0 collections 
jcmd:    garbage-first heap   total 6930432K, used 2163717K [0x0000000518000000, 0x0000000800000000)   region size 8192K, 187 young (1531904K), 3 survivors (24576K)  Metaspace       used 191331K, committed 193408K, reserved 1245184K   class space    used 31804K, commi
proc:   VmHWM:	 3974336 kB VmRSS:	 3974336 kB 
os:     libera=3842MB totala=11884MB
keepup: total=0
flags:  == inainte == -Xms1485M -Xmx11884M -XX:+UseG1GC -Xms1485M -Xmx11884M dupa: -Xms1485M -Xmx8G  
```

## cum se compara cu proba de dinainte (-Xmx2G, tot cu jucator in lume)
```
2G  : MSPT 1.6/2.4/4.9/12.5 ms · GC Young 47.2 ms mediu, 25 colectari · G1 Old 0 · heap 743MB/2GB · RSS 2613MB (varf 2.59GB) · keep-up 0
8G : vezi block-ul de mai sus
```
