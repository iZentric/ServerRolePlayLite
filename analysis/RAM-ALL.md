# RAM-ALL — 2026-10-10 13:50:20 UTC

```
args.sh: actualizat
c.sh: actualizat (guardian OOM inclus)
masina: MemTotal=11884MB MemAvailable=5092MB swap=5119MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx11884M -> -Xmx11884M
 PORNIT la -Xmx11884MB (asta e de fapt memoria pe care o are serverul
Masuratori cu serverul pe 11884MB:
  heap:  garbage-first heap   total 7577600K, used 810932K [0x0000000518000000, 0x0000000800000000)   region size 8192K, 14 young (114688K), 5 survivors (40960K) 
  proces: VmHWM:	 4389888 kB VmRSS:	 4389888 kB 
  masina acum: MemAvailable:    3488256 kB 
  boot: Done (17.094s) | Can't keep up: 0
  port 25565: 1
  supervisor repornit (a stat oprit DA pe toata cautarea)
```

baseline anterior (masurate, 2G): MSPT p95 4.9 ms, GC young 47.2 ms, VmHWM 2613 MB.
