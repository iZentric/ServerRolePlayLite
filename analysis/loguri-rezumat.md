# Loguri Zampto — judecata

Logul: **1047 randuri**, 154978 bytes

- 🟢 **BOOT**: `[16:52:17] [Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer]: Done (21.007s)! For help, type "help"`
- `[16:51:14] [Server thread/INFO] [net.minecraft.server.dedicated.DedicatedServer]: Starting minecraft server version 1.16.5`
- 👥 Intrari jucatori: **0**
- ❌ Erori: **32** | ⚠️ Avertismente: **428** | 💀 Fatale: **0**

## Ultimele 10 erori (daca exista)
```

[16:54:28] [Netty Epoll Server IO #2/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
[16:55:20] [Protocol Worker #1 - FastLogin - [recv: ENCRYPTION_BEGIN[class=PacketLoginInEncryptionBegin, id=1], START[class=PacketLoginInStart, id=0], send: ]/ERROR] [Minecraft]: [FastLogin] Unhandled
[16:55:21] [Netty Epoll Server IO #0/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
[16:55:21] [Netty Epoll Server IO #0/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
[16:55:51] [Protocol Worker #1 - FastLogin - [recv: ENCRYPTION_BEGIN[class=PacketLoginInEncryptionBegin, id=1], START[class=PacketLoginInStart, id=0], send: ]/ERROR] [Minecraft]: [FastLogin] Unhandled
[16:55:51] [Netty Epoll Server IO #3/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
[16:55:51] [Netty Epoll Server IO #3/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
[16:56:24] [Protocol Worker #1 - FastLogin - [recv: ENCRYPTION_BEGIN[class=PacketLoginInEncryptionBegin, id=1], START[class=PacketLoginInStart, id=0], send: ]/ERROR] [Minecraft]: [FastLogin] Unhandled
[16:56:25] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
[16:56:25] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list

```


## Memorie
```

[16:50:43] [main/INFO] [memoryleakfix]: [MemoryLeakFix] Will be applying 3 memory leak fixes!
[16:50:43] [main/INFO] [memoryleakfix]: [MemoryLeakFix] Currently enabled memory leak fixes: [entityMemoriesLeak, biomeTemperatureLeak, drownedNavigationLeak]

```


## Coada logului (ultimele 25 randuri)
```

	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635) [?:?]
	at java.lang.Thread.run(Thread.java:840) [?:?]
[16:55:51] [User Authenticator #8/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270
[16:55:51] [Netty Epoll Server IO #3/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
[16:55:51] [Netty Epoll Server IO #3/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
[16:55:51] [Server thread/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: com.mojang.authlib.GameProfile@6a1d0d18[id=0e2f8d53-21b4-32a4-a498-0967ed108270,name=iZentric,properties={},legacy=
[16:56:24] [Protocol Worker #1 - FastLogin - [recv: ENCRYPTION_BEGIN[class=PacketLoginInEncryptionBegin, id=1], START[class=PacketLoginInStart, id=0], send: ]/INFO] [com.github.games647.fastlogin.bukk
[16:56:24] [Protocol Worker #1 - FastLogin - [recv: ENCRYPTION_BEGIN[class=PacketLoginInEncryptionBegin, id=1], START[class=PacketLoginInStart, id=0], send: ]/ERROR] [Minecraft]: [FastLogin] Unhandled
java.lang.NoSuchMethodError: 'com.comphenix.protocol.reflect.EquivalentConverter com.comphenix.protocol.wrappers.BukkitConverters.getWrappedPublicKeyDataConverter()'
	at com.github.games647.fastlogin.bukkit.listener.protocollib.ProtocolLibListener.onLoginStart(ProtocolLibListener.java:249) ~[FastLoginBukkit.jar:?]
	at com.github.games647.fastlogin.bukkit.listener.protocollib.ProtocolLibListener.onPacketReceiving(ProtocolLibListener.java:145) ~[FastLoginBukkit.jar:?]
	at com.comphenix.protocol.async.AsyncListenerHandler.processPacket(AsyncListenerHandler.java:642) [ProtocolLib.jar:4.8.0]
	at com.comphenix.protocol.async.AsyncListenerHandler.listenerLoop(AsyncListenerHandler.java:596) [ProtocolLib.jar:4.8.0]
	at com.comphenix.protocol.async.AsyncListenerHandler.access$200(AsyncListenerHandler.java:48) [ProtocolLib.jar:4.8.0]
	at com.comphenix.protocol.async.AsyncListenerHandler$2.run(AsyncListenerHandler.java:229) [ProtocolLib.jar:4.8.0]
	at com.comphenix.protocol.async.AsyncListenerHandler$3.run(AsyncListenerHandler.java:300) [ProtocolLib.jar:4.8.0]
	at org.bukkit.craftbukkit.v1_16_R3.scheduler.CraftTask.run(CraftTask.java:81) [forge:?]
	at org.bukkit.craftbukkit.v1_16_R3.scheduler.CraftAsyncTask.run(CraftAsyncTask.java:54) [forge:?]
	at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1136) [?:?]
	at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:635) [?:?]
	at java.lang.Thread.run(Thread.java:840) [?:?]
[16:56:25] [User Authenticator #9/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: UUID of player iZentric is 0e2f8d53-21b4-32a4-a498-0967ed108270
[16:56:25] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.NetworkRegistry]: Channels [serverpause:channel] rejected their client side version number
[16:56:25] [Netty Epoll Server IO #5/ERROR] [net.minecraftforge.fml.network.FMLHandshakeHandler]: Terminating connection with client, mismatched mod list
[16:56:25] [Server thread/INFO] [net.minecraft.network.login.ServerLoginNetHandler]: com.mojang.authlib.GameProfile@aa5835[id=0e2f8d53-21b4-32a4-a498-0967ed108270,name=iZentric,properties={},legacy=fa

```
