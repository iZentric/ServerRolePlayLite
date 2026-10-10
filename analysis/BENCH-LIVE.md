# BENCH live CUANTIC — 2026-10-10 11:53:37 UTC

```
== PUNTE ==
list: FARA-RASPUNS
health: > TPS from last 5s, 10s, 1m, 5m, 15m:     20.0, 20.0, 20.0, 20.0, 20.0  > CPU usage from last 10s, 1m, 15m:     95%, 93%, 93%  (system)     93%, 91%, 91%  (process)  > Memory usage:     1.4 GB / 11.6 GB   (12%)     [┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Disk usage:     3.3 GB / 5.0 GB   (65%)     [┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻] 
gc: [11:52:34] [spark-worker-pool-1-thread-3/INFO]: [⚡] Calculating GC statistics... [11:52:34] [spark-worker-pool-1-thread-3/INFO]:  > Garbage Collector statistics      G1 Young Generation collector:       100.14 ms avg, 7 total collections       3s avg frequency      G1 Old Generation collector:       0 collections [11:52:34] [Craft Scheduler Thread - 8/INFO]: [FastLogin] Handling player iZentric [11:52:35] [User Authenticator #1/INFO]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270 [11:52:36] [Server thread/INFO]: Using new advancement loading for net.minecraft.advancements.PlayerAdvancements@40375d21 [11:52:36] [Server thread/INFO]: iZentric[/127.0.0.1:36144] logged in with entity id 135 at (76.03056010237415, 70.0, -130.36221080338566) 
mem: FARA-RASPUNS
chat: [11:53:35] [Server thread/INFO]: [Server] agent: puntea de comanda functioneaza (test) 
== OS ==
ram_libera=4463MB total=11884MB
disc=66% din 5.0G (/dev/sdb1)
load: 1.05 0.99 0.69 2/678 13760  cpu=2 fire
jstat_gcutil (60s, 6 esantioane):
  java cpu=113% rss=3449MB live=02:19
== LOG ==
Done: Done (19.605s)
Can't keep up: total=0 in_ultimele_4000=0
chunk/incarcare (linii complete):
  [11:52:01] [Server thread/INFO]: [LuckPerms] Successfully enabled. (took 4899ms)
  [11:52:28] [Server thread/WARN]: Dedicated server took 69.838 seconds to load
jcmd/GC:
  13171:
   garbage-first heap   total 4128768K, used 1070340K [0x0000000518000000, 0x0000000800000000)
    region size 8192K, 46 young (376832K), 2 survivors (16384K)
   Metaspace       used 197944K, committed 200128K, reserved 1245184K
    class space    used 32716K, committed 33664K, reserved 1048576K
jstat:
  	at jdk.jcmd/sun.tools.jstat.Jstat.main(Jstat.java:70)
  Caused by: java.lang.IllegalArgumentException: Could not map vmid to user Name
  	at java.base/jdk.internal.perf.Perf.attach(Native Method)
  	at java.base/jdk.internal.perf.Perf.attachImpl(Perf.java:273)
  	at java.base/jdk.internal.perf.Perf.attach(Perf.java:203)
  	at jdk.internal.jvmstat/sun.jvmstat.perfdata.monitor.protocol.local.PerfDataBuffer.<init>(PerfDataBuffer.java:65)
  	... 4 more
din /proc: VmHWM:	 3828608 kB VmRSS:	 3532288 kB 
latenta TCP pana la propriul port public: 6ms
erori CRITICE in sesiune: 0
frpc: [0m
```
