# BENCH live CUANTIC — 2026-10-10 17:51:09 UTC

```
== PUNTE ==
list: [17:50:08] [Server thread/INFO]: There are 1 out of maximum 25 players online. [17:50:08] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     2.3/3.0/9.0/26.3; 2.0/3.8/18.8/1514.7  > CPU usage from last 10s, 1m, 15m:     37%, 51%, 62%  (system)     11%, 26%, 38%  (process)  > Memory usage:     759.0 MB / 6.0 GB   (12%)     [┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     28.8 KB/s / 45 pps (lo rx)     28.8 KB/s / 45 pps (lo tx) 
gc: [17:50:14] [spark-worker-pool-1-thread-2/INFO]: [⚡] Calculating GC statistics... [17:50:14] [spark-worker-pool-1-thread-2/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       109.5 ms avg, 10 total collections       9s avg frequency      G1 Old Generation collector:       0 collections 
mem: FARA-RASPUNS
chat: [17:51:05] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4647MB total=11884MB
disc=64% din 5.0G (/dev/sdb1)
load: 1.24 1.61 1.36 1/661 80635  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=74.4% rss=3266MB live=03:30
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
   garbage-first heap   total 3686400K, used 1170456K [0x0000000680000000, 0x0000000800000000)
    region size 8192K, 57 young (466944K), 1 survivors (8192K)
   Metaspace       used 192667K, committed 194816K, reserved 1245184K
    class space    used 31952K, committed 32896K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3348416 kB VmRSS:	 3344576 kB 
latenta TCP pana la propriul port public: 6ms
erori CRITICE in sesiune: 0
frpc: [0m
```
