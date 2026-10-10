# RAM-ALL — 2026-10-10 12:03:28 UTC

```
args.sh: actualizat
c.sh: actualizat (guardian OOM inclus)
masina: MemTotal=11884MB MemAvailable=7927MB swap=5119MB
args: MEMORIE -Xmx 11884M (masina are 11884MB), -Xms 1485M, plafon=11884MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx11884M -> -Xmx11884M
  java a murit la 6s: 
  cobor plafonul la 9744MB
args: MEMORIE -Xmx 9744M (masina are 11884MB), -Xms 1218M, plafon=9744MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx9744M -> -Xmx9744M
  java a murit la 6s: 
  cobor plafonul la 7990MB
args: MEMORIE -Xmx 7990M (masina are 11884MB), -Xms 998M, plafon=7990MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx7990M -> -Xmx7990M
  java a murit la 6s: 
  cobor plafonul la 6551MB
args: MEMORIE -Xmx 6551M (masina are 11884MB), -Xms 818M, plafon=6551MB
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
  incercare -Xmx6551M -> -Xmx6551M
  java a murit la 6s: 
  cobor plafonul la 5371MB
NICIUN plafon nu a mers (ultima incercare 5371MB) - revin la varianta sigura:
args: MEMORIE -Xmx 11884M (masina are 11884MB), -Xms 1485M, plafon=niciodata
args: OK (CatServer-1.16.5-1d8d6313-server.jar, 37 linii)
rollback:
-Xmx11884M
  supervisor pornit cu varianta sigura
```

baseline anterior (masurate, 2G): MSPT p95 4.9 ms, GC young 47.2 ms, VmHWM 2613 MB.
