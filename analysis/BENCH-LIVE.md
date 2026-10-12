# BENCH live CUANTIC — 2026-10-12 10:18:22 UTC

```
== PUNTE ==
list: [10:18:01] [Server thread/INFO]: There are 1 out of maximum 25 players online. [10:18:01] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     1.1/1.3/3.5/14.9; 0.3/1.5/6.9/1869.1  > CPU usage from last 10s, 1m, 15m:     38%, 44%, 47%  (system)     12%, 29%, 35%  (process)  > Memory usage:     1.3 GB / 6.0 GB   (22%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     28.2 KB/s / 45 pps (lo rx)     28.2 KB/s / 45 pps (lo tx) 
gc: [10:18:06] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [10:18:06] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       75.22 ms avg, 9 total collections       9s avg frequency      G1 Old Generation collector:       0 collections 
mem: > Memory usage:     1.3 GB / 6.0 GB   (22%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     28.2 KB/s / 45 pps (lo rx)     28.2 KB/s / 45 pps (lo tx)     19.0 KB/s / 43 pps (enp1s0 rx)     32.4 KB/s / 49 pps (enp1s0 tx)  > Disk usage:     3.3 GB / 5.0 GB   (66%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  
chat: [10:18:18] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4956MB total=11884MB
disc=67% din 5.0G (/dev/sdb1)
load: 1.06 0.83 0.51 1/603 30314  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=94.6% rss=3319MB live=02:24
== LOG ==
Done: Done (11.827s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [10:16:38] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5166ms)
  [10:16:55] [Server thread/WARN]: Dedicated server took 58.475 seconds to load
  [10:17:11] [Server thread/WARN]: Permissions lag notice with (LuckPermsHandler). Response took 68.365124ms. Summary: Getting prefix for iZentric
jcmd/GC:
  29039:
   garbage-first heap   total 3850240K, used 1431921K [0x0000000680000000, 0x0000000800000000)
    region size 8192K, 92 young (753664K), 3 survivors (24576K)
   Metaspace       used 192470K, committed 194624K, reserved 1245184K
    class space    used 31930K, committed 32896K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3655424 kB VmRSS:	 3398720 kB 
latenta TCP pana la propriul port public: 4ms
erori CRITICE in sesiune: 0
frpc: [0m
```
