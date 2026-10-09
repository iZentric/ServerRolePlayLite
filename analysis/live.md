# CUANTIC LIVE — 2026-10-09 17:11:57 UTC
```
== CUANTIC LIVE v5 — 2026-10-09 17:09:15 UTC ==
supervisor: 1 procese | java: 1
boot: Done (14.240s)
linii cheie din log:
  144:[17:09:41] [Server thread/INFO]: Starting Minecraft server on *:25565
  217:[17:10:06] [Server thread/ERROR]: You are running a server that does not properly support Bukkit plugins. Bukkit plugins should not be used with Forge/Fabric mods! For Forge: Consider using ForgeEssentials, or SpongeForge + Nucleus.
  286:[17:10:14] [Server thread/WARN]: Caused by: java.lang.reflect.InvocationTargetException
  294:[17:10:14] [Server thread/WARN]: Caused by: fr.xephi.authme.libs.ch.jalu.injector.exceptions.InjectorReflectionException: Could not invoke constructor of class 'class fr.xephi.authme.security.totp.TotpAuthenticator'
  308:[17:10:14] [Server thread/WARN]: Caused by: java.lang.reflect.InvocationTargetException
  316:[17:10:14] [Server thread/WARN]: Caused by: fr.xephi.authme.libs.com.warrenstrange.googleauth.GoogleAuthenticatorException: Could not initialise SecureRandom with the specified algorithm: SHA1PRNG. Another provider can be chosen setting the fr.xephi.authme.libs.com.warrenstrange.googleauth.rng.algorithm system property.
  323:[17:10:14] [Server thread/WARN]: Caused by: java.security.NoSuchAlgorithmException: no such algorithm: SHA1PRNG for provider SUN
  342:[17:10:15] [Server thread/INFO]: Done (14.240s)! For help, type "help"
ss -lnt:
  State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
  LISTEN 0      511          0.0.0.0:4444      0.0.0.0:*          
  127.0.0.1:25565 = refuzat
  10.89.0.2:25565 = refuzat
  10.215.108.231:25565 = refuzat
mem: Mem:          11884        2203        5665          80        4014        7853 | java RSS: 0MB
bore: NU | log: [2m2026-10-09T17:10:19.561370Z[0m [32m INFO[0m [2mbore_cli::client[0m[2m:[0m connected to server [3mremote_port[0m[2m=[0m15540 [2m2026-10-09T17:10:19.561432Z[0m [32m INFO[0m [2mbore_cli::client[0m[2m:[0m listening at bore.pub:15540 
  probe 1: "online":false 
  probe 2: "online":false 
  probe 3: "online":false 
  probe 4: "online":false 
  probe 5: "online":false 
  probe 6: "online":false 
server: VIU | supervisor: VIU | bore: VIU
==> BOOT Done (14.240s) | ONLINE DIN INTERNET: NU | ADRESA: NU
GATA
```
----- live.log (ultimele 12) -----
```
[17:11:50] [main/INFO]: Initializing MixinExtras via org.embeddedt.modernfix.forge.shadow.mixinextras.service.MixinExtrasServiceImpl(version=0.3.2).
[17:11:51] [main/INFO]: Patching LivingEntity#attackEntityFrom
[17:11:51] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
[17:11:51] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: Defaulting to no-operation (NOP) logger implementation
[17:11:51] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
[17:11:51] [main/INFO]: ModernFix reached bootstrap stage (7.973 s after launch)
[17:11:52] [main/INFO]: Injecting BlockStateBase cache population hook into func_204519_t from me.jellysquid.mods.lithium.mixin.block.flatten_states.AbstractBlockStateMixin
[17:11:52] [main/INFO]: Using Java 9+ class definer
[17:11:52] [main/INFO]: Patching ItemStack#onItemUse
[17:11:55] [main/INFO]: Vanilla bootstrap took 4064 milliseconds
[17:11:56] [modloading-worker-0/INFO]: Patching DataPackRegistries#<init>
[17:11:56] [modloading-worker-0/INFO]: Ksyxis: Ready to remove unneeded chunks. (platform: forge, version: 1.4.6, mixin: 0.8.4)
```
----- bore.log -----
```
[2m2026-10-09T17:10:19.561370Z[0m [32m INFO[0m [2mbore_cli::client[0m[2m:[0m connected to server [3mremote_port[0m[2m=[0m15540
[2m2026-10-09T17:10:19.561432Z[0m [32m INFO[0m [2mbore_cli::client[0m[2m:[0m listening at bore.pub:15540
[2m2026-10-09T17:11:22.541136Z[0m [32m INFO[0m [1mproxy[0m[1m{[0m[3mid[0m[2m=[0m1f8fc393-3bb1-4c63-b8cb-b018fa32a751[1m}[0m[2m:[0m [2mbore_cli::client[0m[2m:[0m new connection
[2m2026-10-09T17:11:29.635813Z[0m [32m INFO[0m [1mproxy[0m[1m{[0m[3mid[0m[2m=[0m1f8fc393-3bb1-4c63-b8cb-b018fa32a751[1m}[0m[2m:[0m [2mbore_cli::client[0m[2m:[0m connection exited
```
