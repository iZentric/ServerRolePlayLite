# JVM-TUNE CUANTIC — 2026-10-10 12:53:56 UTC

```
== brata C: heap 2G + set complet de flaguri GC (Java 17 validat) ==
list:   [12:53:25] [Server thread/INFO]: There are 0 out of maximum 25 players online. 
health: > Tick durations (min/med/95%ile/max ms) from last 10s, 1m:     0.6/0.7/1.1/18.0; 0.6/0.7/0.8/25.7  > CPU usage from last 10s, 1m, 15m:     2%, 3%, 24%  (system)     2%, 2%, 23%  (process)  > Memory usage:     1.0 GB / 11.6 GB   (8%)     [┃┃┃┃┃╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻╻]  > Network usage: (system, last 15m)     646.0 bytes/s / 3 pps (eth0 rx)     578.0 bytes/s / 3 pps (eth0 tx)     134.5 KB/s / 16 pps (enp1s0 rx)     1.0 KB/s / 11 pps (enp1s0 tx) 
gc:     > Garbage Collector statistics      G1 Young Generation collector:       79.89 ms avg, 9 total collections       14s avg frequency      G1 Old Generation collector:       0 collections 
jcmd:     region size 8192K, 51 young (417792K), 5 survivors (40960K)  Metaspace       used 188601K, committed 190528K, reserved 1245184K   class space    used 31279K, committed 32128K, reserved 1048576K 
proc:   VmHWM:	 3703872 kB VmRSS:	 3477824 kB 
os:     libera=4481MB
keepup: total=0

## flaguri acceptate de Java 17 (32)
  -XX:+UseG1GC
  -XX:+ParallelRefProcEnabled
  -XX:MaxGCPauseMillis=37
  -XX:+UnlockExperimentalVMOptions
  -XX:+UnlockDiagnosticVMOptions
  -XX:+DisableExplicitGC
  -XX:G1NewSizePercent=23
  -XX:G1HeapRegionSize=8M
  -XX:G1ReservePercent=20
  -XX:G1HeapWastePercent=20
  -XX:G1MixedGCCountTarget=3
  -XX:InitiatingHeapOccupancyPercent=10
  -XX:G1RSetUpdatingPauseTimePercent=0
  -XX:SurvivorRatio=32
  -XX:MaxTenuringThreshold=1
  -XX:G1SATBBufferEnqueueingThresholdPercent=30
  -XX:G1ConcMarkStepDurationMillis=5.0
  -XX:G1ConcRSHotCardLimit=16
  -XX:G1ConcRefinementServiceIntervalMillis=150
  -XX:GCTimeRatio=99
  -XX:+PerfDisableSharedMem
  -XX:+UseStringDeduplication
  -XX:+UseFastUnorderedTimeStamps
  -XX:NmethodSweepActivity=1
  -XX:ReservedCodeCacheSize=256M
  -XX:NonNMethodCodeHeapSize=12M
  -XX:ProfiledCodeHeapSize=122M
  -XX:NonProfiledCodeHeapSize=122M
  -XX:-DontCompileHugeMethods
  -XX:MaxNodeLimit=240000
  -XX:NodeLimitFudgeFactor=8000
  -XX:AllocatePrefetchStyle=3
## aruncate (nu mai exista in 17):
## brate anterior, aceeasi masina, acelasi jucator
  A) -Xmx2G, 3 flaguri              : MSPT 1.6/2.4/4.9/12.5 ms · GC 47.2 ms mediu/25 · Old 0 · heap 743MB/2G · RSS 2613MB · keep-up 0
  B) -Xmx8G, 3 flaguri (toata RAM-ul): MSPT 1.2/1.6/9.1/29.5 · GC 111.38 ms mediu/8 · Old 0 · heap 1.2G/8G · RSS 3366MB · keep-up 0
```
