# BENCH live CUANTIC — 2026-10-10 17:53:19 UTC

```
== PUNTE ==
list: [17:53:00] [Server thread/INFO]: There are 1 out of maximum 25 players online. [17:53:00] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     2.2/2.8/6.8/38.2; 0.9/2.9/6.6/38.2  > CPU usage from last 10s, 1m, 15m:     40%, 41%, 38%  (system)     13%, 15%, 20%  (process)  > Memory usage:     1.4 GB / 6.0 GB   (23%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     19.5 KB/s / 55 pps (lo rx)     19.5 KB/s / 55 pps (lo tx) 
gc: [17:53:06] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [17:53:06] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       93.42 ms avg, 12 total collections       22s avg frequency      G1 Old Generation collector:       0 collections 
mem: > Memory usage:     721.2 MB / 6.0 GB   (11%)     [┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     19.5 KB/s / 55 pps (lo rx)     19.5 KB/s / 55 pps (lo tx)     27.9 KB/s / 52 pps (enp1s0 rx)     27.7 KB/s / 60 pps (enp1s0 tx)  > Disk usage:     3.2 GB / 5.0 GB   (63%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  
chat: [17:53:15] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4649MB total=11884MB
disc=64% din 5.0G (/dev/sdb1)
load: 0.87 1.37 1.31 1/664 83465  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=54.1% rss=3273MB live=05:40
== LOG ==
Done: Done (23.009s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [17:40:06] [Server thread/WARN]: Dedicated server took 72.704 seconds to load
  [17:40:20] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 100.844647ms. Summary: Getting prefix for iZentric
  [17:48:29] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 7108ms)
  [17:49:01] [Server thread/WARN]: Dedicated server took 82.921 seconds to load
  [17:49:14] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 65.333151ms. Summary: Getting prefix for iZentric
jcmd/GC:
  77570:
   garbage-first heap   total 3686400K, used 783612K [0x0000000680000000, 0x0000000800000000)
    region size 8192K, 9 young (73728K), 1 survivors (8192K)
   Metaspace       used 193822K, committed 195904K, reserved 1245184K
    class space    used 32031K, committed 32960K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3352064 kB VmRSS:	 3352064 kB 
latenta TCP pana la propriul port public: 5ms
erori CRITICE in sesiune: 0
frpc: [0m
```
