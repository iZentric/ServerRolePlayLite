# DOVADA ACCES — server Evor — 2026-10-08 21:02:43 UTC

## 1) Serverul e VIU (ping MC pe 26252, de la distanta)
PING ESUAT: Traceback (most recent call last):
  File "/tmp/mcping.py", line 29, in <module>
    print("MCSTATUS="+json.dumps({"live":True,"versiune":j["version"]["name"],"online":j["players"]["online"],"max":j["players"]["max"],"motd":str(j.get("description"))[:80]}))
                                                         ~^^^^^^^^^^^
KeyError: 'version'

## 2) Am citit filesystemul prin SFTP
- fisiere in root: 32 intrari
- moduri pe server: 32 .jar
- marime server.jar pe disc: 8014140 bytes
- marime latest.log: 60065 bytes

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
[20:40:46] [Craft Scheduler Thread - 0/INFO] []: [33;1m[[32;22mSkinsRestorer[33;1m] [0;39m[GitHubUpdate] Update saved as plugins/update/SkinsRestorer.jar[0;39m
[20:59:57] [Server thread/INFO] []: TPS from last 1m, 5m, 15m: 20.0, *20.0, *20.0
[20:59:57] [Server thread/INFO] []: Current Memory Usage: 1077/3160 mb (Max: 4096 mb)
[21:00:01] [Server thread/INFO] []: TPS from last 1m, 5m, 15m: 20.0, *20.0, *20.0
[21:00:01] [Server thread/INFO] []: Current Memory Usage: 1077/3160 mb (Max: 4096 mb)
[21:00:02] [Server thread/INFO] []: Unknown command. Type "/help" for help.
[21:02:08] [RCON Listener #1/INFO] [net.minecraft.network.rcon.RConThread]: Thread RCON Client /20.125.176.176 started
[21:02:08] [RCON Client /20.125.176.176 #2/INFO] [net.minecraft.network.rcon.ClientThread]: Thread RCON Client /20.125.176.176 shutting down
```

## 6) RCON — consola de la distanta
```
RCON FARA RASPUNS LA LOGIN: chiuvist inainte de cap
RCON COMANDA ESUATA: chiuvist inainte de cap
```
