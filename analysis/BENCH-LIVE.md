# BENCH live CUANTIC — 2026-10-09 23:12:33 UTC

```
== PUNTE ==
list: [23:11:01] [Server thread/INFO]: There are 1 out of maximum 25 players online. [23:11:01] [Server thread/INFO]: default: iZentric 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     1.6/2.4/4.9/12.5; 0.8/2.4/7.8/278.9  > CPU usage from last 10s, 1m, 15m:     9%, 17%, 15%  (system)     8%, 11%, 13%  (process)  > Memory usage:     742.7 MB / 2.0 GB   (36%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     14.2 KB/s / 76 pps (lo rx)     14.2 KB/s / 76 pps (lo tx) 
gc: [23:11:31] [spark-worker-pool-1-thread-2/INFO]: [⚡] Calculating GC statistics... [23:11:31] [spark-worker-pool-1-thread-2/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       47.2 ms avg, 25 total collections       24s avg frequency      G1 Old Generation collector:       0 collections 
mem: FARA-RASPUNS
chat: [23:12:31] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4730MB total=11884MB
disc=63% din 5.0G (/dev/sdb1)
load: 0.62 1.03 1.17 4/699 61978  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=32.4% rss=2613MB live=12:37
== LOG ==
Done: Done (14.448s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [23:01:06] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 5283ms)
  [23:01:28] [Server thread/WARN]: Dedicated server took 92.639 seconds to load
jcmd/GC:
  59733:
   garbage-first heap   total 1974272K, used 1077617K [0x0000000080000000, 0x0000000100000000)
    region size 8192K, 42 young (344064K), 2 survivors (16384K)
   Metaspace       used 201674K, committed 203776K, reserved 1245184K
    class space    used 33016K, committed 33984K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 2719424 kB VmRSS:	 2676160 kB 
latenta TCP pana la propriul port public: 4ms
erori CRITICE in sesiune: 0
frpc: [0m
```
