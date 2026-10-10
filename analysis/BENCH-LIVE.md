# BENCH live CUANTIC — 2026-10-10 11:13:13 UTC

```
== PUNTE ==
list: [11:11:41] [Server thread/INFO]: There are 1 out of maximum 25 players online. [11:11:41] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     0.8/1.1/2.0/10.3; 0.7/1.2/2.4/20.2  > CPU usage from last 10s, 1m, 15m:     5%, 11%, 13%  (system)     4%, 5%, 11%  (process)  > Memory usage:     1.3 GB / 11.6 GB   (11%)     [┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     12.9 KB/s / 63 pps (lo rx)     12.9 KB/s / 63 pps (lo tx) 
gc: [11:12:11] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [11:12:11] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       115.88 ms avg, 8 total collections       59s avg frequency      G1 Old Generation collector:       0 collections 
mem: FARA-RASPUNS
chat: [11:13:11] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4216MB total=11884MB
disc=63% din 5.0G (/dev/sdb1)
load: 0.05 0.47 0.94 2/658 7284  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=30.4% rss=3713MB live=10:21
== LOG ==
Done: Done (13.664s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [11:04:05] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 6416ms)
  [11:04:28] [Server thread/WARN]: Dedicated server took 96.788 seconds to load
  [11:04:34] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 61.286961ms. Summary: Getting prefix for iZentric
jcmd/GC:
  5900:
   garbage-first heap   total 6520832K, used 1837353K [0x0000000518000000, 0x0000000800000000)
    region size 8192K, 144 young (1179648K), 4 survivors (32768K)
   Metaspace       used 193804K, committed 195968K, reserved 1245184K
    class space    used 31989K, committed 32960K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3802560 kB VmRSS:	 3802560 kB 
latenta TCP pana la propriul port public: 5ms
erori CRITICE in sesiune: 0
frpc: [0m
```
