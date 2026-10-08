# DOVADA ACCES — server Evor — 2026-10-08 21:05:12 UTC

## 1) Serverul e VIU (ping MC pe 26252, de la distanta)
PING ESUAT: Traceback (most recent call last):
  File "/tmp/mcping.py", line 33, in <module>
    j=json.loads(raw)
      ^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/json/__init__.py", line 341, in loads
    s = s.decode(detect_encoding(s), 'surrogatepass')
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xb9 in position 1: invalid start byte

## 2) Am citit filesystemul prin SFTP
- fisiere in root: 32 intrari
- moduri pe server: 32 .jar
- marime server.jar pe disc: 8014140 bytes
- marime latest.log: 60319 bytes

## 3) Jarul de pe server = FORJA noastra (EvoKode custom, byte-cu-byte)
- md5 server.jar (pe host): `d4a117de014ce77c37d6d506bdb8ad6b`
- md5 jar din release custom: `d4a117de014ce77c37d6d506bdb8ad6b`
- IDENTIC: **DA**

## 4) RCON inarmat (chei din server.properties, valorile sunt cenzurate)
- enable-rcon
- rcon.password
- rcon.port

## 5) Ultimele 8 linii din logul SERVERULUI (bataia lui de inima)
```
[20:59:57] [Server thread/INFO] []: Current Memory Usage: 1077/3160 mb (Max: 4096 mb)
[21:00:01] [Server thread/INFO] []: TPS from last 1m, 5m, 15m: 20.0, *20.0, *20.0
[21:00:01] [Server thread/INFO] []: Current Memory Usage: 1077/3160 mb (Max: 4096 mb)
[21:00:02] [Server thread/INFO] []: Unknown command. Type "/help" for help.
[21:02:08] [RCON Listener #1/INFO] [net.minecraft.network.rcon.RConThread]: Thread RCON Client /20.125.176.176 started
[21:02:08] [RCON Client /20.125.176.176 #2/INFO] [net.minecraft.network.rcon.ClientThread]: Thread RCON Client /20.125.176.176 shutting down
[21:04:38] [RCON Listener #1/INFO] [net.minecraft.network.rcon.RConThread]: Thread RCON Client /4.151.214.97 started
[21:04:38] [RCON Client /4.151.214.97 #3/INFO] [net.minecraft.network.rcon.ClientThread]: Thread RCON Client /4.151.214.97 shutting down
```

## 6) RCON — consola de la distanta
```
RCON: conectat dar fara raspuns util (probabil chei gresite — MC inchide dupes esec)
```
