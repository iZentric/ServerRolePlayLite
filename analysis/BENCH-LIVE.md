# BENCH live CUANTIC — 2026-10-10 14:48:14 UTC

```
== PUNTE ==
list: FARA-RASPUNS
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     466.1/466.1/466.1/466.1; 466.1/466.1/466.1/466.1  > CPU usage from last 10s, 1m, 15m:     98%, 93%, 93%  (system)     97%, 91%, 91%  (process)  > Memory usage:     1.2 GB / 11.6 GB   (10%)     [┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Disk usage:     3.5 GB / 5.0 GB   (70%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻] 
gc: [14:47:12] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [14:47:12] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       96.71 ms avg, 7 total collections       3s avg frequency      G1 Old Generation collector:       0 collections 
mem: FARA-RASPUNS
chat: [14:48:12] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4397MB total=11884MB
disc=71% din 5.0G (/dev/sdb1)
load: 0.99 1.22 0.84 2/674 41280  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=90.1% rss=3414MB live=02:19
== LOG ==
Done: Done (16.631s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [14:45:00] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5675ms)
  [14:45:20] [Server thread/WARN]: Dedicated server took 68.14 seconds to load
  [14:46:38] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5698ms)
  [14:47:02] [Server thread/WARN]: Dedicated server took 67.377 seconds to load
jcmd/GC:
  40699:
   garbage-first heap   total 3194880K, used 795955K [0x0000000518000000, 0x0000000800000000)
    region size 8192K, 16 young (131072K), 3 survivors (24576K)
   Metaspace       used 184738K, committed 186624K, reserved 1245184K
    class space    used 30983K, committed 31808K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3522176 kB VmRSS:	 3496128 kB 
latenta TCP pana la propriul port public: 4ms
erori CRITICE in sesiune: 0
frpc: [0m
```
