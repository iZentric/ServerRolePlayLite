# BENCH live CUANTIC — 2026-10-12 15:07:19 UTC

```
== PUNTE ==
list: [15:07:00] [Server thread/INFO]: There are 0 out of maximum 25 players online. 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     0.1/0.1/0.1/19.6; 0.1/0.1/0.2/19.6  > CPU usage from last 10s, 1m, 15m:     24%, 5%, 10%  (system)     0%, 0%, 7%  (process)  > Memory usage:     895.5 MB / 6.0 GB   (14%)     [┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     1.0 bytes/s / 0 pps (lo rx)     1.0 bytes/s / 0 pps (lo tx) 
gc: [15:07:06] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [15:07:06] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       117.5 ms avg, 6 total collections       28s avg frequency      G1 Old Generation collector:       0 collections 
mem: > Memory usage:     895.5 MB / 6.0 GB   (14%)     [┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     1.0 bytes/s / 0 pps (lo rx)     1.0 bytes/s / 0 pps (lo tx)     2.5 KB/s / 2 pps (enp1s0 rx)     1.1 KB/s / 2 pps (enp1s0 tx)  > Disk usage:     3.3 GB / 5.0 GB   (66%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  
chat: [15:07:15] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=5260MB total=11884MB
disc=67% din 5.0G (/dev/sdb1)
load: 0.29 0.48 0.36 1/590 39372  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=46.1% rss=2989MB live=03:52
== LOG ==
Done: Done (12.066s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [10:16:38] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5166ms)
  [10:16:55] [Server thread/WARN]: Dedicated server took 58.475 seconds to load
  [10:17:11] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 68.365124ms. Summary: Getting prefix for iZentric
  [15:04:08] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5987ms)
  [15:04:26] [Server thread/WARN]: Dedicated server took 59.949 seconds to load
jcmd/GC:
  38256:
   garbage-first heap   total 4644864K, used 938271K [0x0000000680000000, 0x0000000800000000)
    region size 8192K, 36 young (294912K), 2 survivors (16384K)
   Metaspace       used 181572K, committed 183360K, reserved 1245184K
    class space    used 30690K, committed 31488K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3060736 kB VmRSS:	 3060736 kB 
latenta TCP pana la propriul port public: 4ms
erori CRITICE in sesiune: 0
frpc: [0m
```
