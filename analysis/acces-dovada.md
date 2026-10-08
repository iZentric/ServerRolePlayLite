# DOVADA ACCES — server Evor — 2026-10-08 20:27:15 UTC

## 1) Serverul e VIU (ping MC pe 26252, de la distanta)
PING ESUAT: Traceback (most recent call last):
  File "/tmp/mcping.py", line 24, in <module>
    s=socket.create_connection(("node12.zampto.net",port),15)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 852, in create_connection
    raise exceptions[0]
  File "/usr/lib/python3.12/socket.py", line 837, in create_connection
    sock.connect(sa)
TimeoutError: timed out

## 2) Am citit filesystemul prin SFTP
- fisiere in root: 32 intrari
- moduri pe server: 32 .jar
- marime server.jar pe disc: 8014140 bytes
- marime latest.log: 53602 bytes

## 3) Jarul de pe server = FORJA noastra (EvoKode custom, byte-cu-byte)
- md5 server.jar (pe host): `e62cf3b73bb8aa9fd84e2aacd2ae530c`
- md5 jar din release custom: `d4a117de014ce77c37d6d506bdb8ad6b`
- IDENTIC: **NU**

## 4) RCON inarmat (chei din server.properties, valorile sunt cenzurate)
- enable-rcon
- rcon.port
- rcon.password

## 5) Ultimele 8 linii din logul SERVERULUI (bataia lui de inima)
```
[22:20:59] [Server thread/INFO] [net.minecraft.server.MinecraftServer]: Saving worlds
[22:20:59] [Server thread/INFO] [net.minecraft.server.MinecraftServer]: Saving chunks for level 'ServerLevel[world]'/minecraft:overworld
[22:20:59] [Server thread/INFO] [net.minecraft.world.server.ChunkManager]: ThreadedAnvilChunkStorage (world): All chunks are saved
[22:20:59] [Server thread/INFO] [net.minecraft.server.MinecraftServer]: Saving chunks for level 'ServerLevel[DIM-1]'/minecraft:the_nether
[22:20:59] [Server thread/INFO] [net.minecraft.world.server.ChunkManager]: ThreadedAnvilChunkStorage (DIM-1): All chunks are saved
[22:20:59] [Server thread/INFO] [net.minecraft.server.MinecraftServer]: Saving chunks for level 'ServerLevel[DIM1]'/minecraft:the_end
[22:20:59] [Server thread/INFO] [net.minecraft.world.server.ChunkManager]: ThreadedAnvilChunkStorage (DIM1): All chunks are saved
[22:21:00] [Server thread/INFO] [net.minecraft.server.MinecraftServer]: Saving usercache.json
```
