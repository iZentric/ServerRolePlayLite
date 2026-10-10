# BENCH live CUANTIC — 2026-10-10 11:35:53 UTC

```
== PUNTE ==
list: FARA-RASPUNS
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     0.6/1.6/354.1/354.1; 0.6/1.6/354.1/354.1  > CPU usage from last 10s, 1m, 15m:     98%, 91%, 91%  (system)     97%, 88%, 88%  (process)  > Memory usage:     1.1 GB / 11.6 GB   (9%)     [┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Disk usage:     3.2 GB / 5.0 GB   (64%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻] 
gc: [11:34:49] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [11:34:49] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       140.25 ms avg, 4 total collections       6s avg frequency      G1 Old Generation collector:       0 collections 
mem: FARA-RASPUNS
chat: [11:35:50] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=3258MB total=11884MB
disc=65% din 5.0G (/dev/sdb1)
load: 1.01 0.87 0.63 3/672 11051  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=108% rss=4647MB live=02:19
== LOG ==
Done: Done (11.504s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [11:34:16] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 4902ms)
  [11:34:34] [Server thread/WARN]: Dedicated server took 61.181 seconds to load
  [11:34:41] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 47.349221ms. Summary: Getting prefix for iZentric
jcmd/GC:
  10472:
   garbage-first heap   total 7356416K, used 2126221K [0x0000000518000000, 0x0000000800000000)
    region size 8192K, 177 young (1449984K), 5 survivors (40960K)
   Metaspace       used 192138K, committed 194368K, reserved 1245184K
    class space    used 31829K, committed 32832K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 4760128 kB VmRSS:	 4760128 kB 
latenta TCP pana la propriul port public: 5ms
erori CRITICE in sesiune: 0
frpc: [0m
```
