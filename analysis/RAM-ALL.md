# RAM-ALL — 2026-10-10 11:04:31 UTC

```
args.sh: actualizat
c.sh: actualizat (guardian OOM inclus)
masina: MemTotal=11884MB MemAvailable=5277MB swap=5119MB
args: MEMORIE -Xmx 11884M (masina are 11884MB), -Xms 1485M, plafon=11884MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx11884M -> -Xmx11884M
 PORNIT la -Xmx11884MB (asta e de fapt memoria pe care o are serverul
Masuratori cu serverul pe 11884MB:
  heap:  garbage-first heap   total 6520832K, used 1471711K [0x0000000518000000, 0x0000000800000000)   region size 8192K, 105 young (860160K), 1 survivors (8192K) 
  proces: VmHWM:	 3218624 kB VmRSS:	 3192000 kB 
  masina acum: MemAvailable:    4811840 kB 
  boot: Done (13.664s) | Can't keep up: 0
  port 25565: 1
```

baseline anterior (masurate, 2G): MSPT p95 4.9 ms, GC young 47.2 ms, VmHWM 2613 MB.
