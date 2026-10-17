== SONDA EXTERNA 25565 ==
{"version": {"name": "Mohist 1.16.5", "protocol": 754}, "players": {"online": 0, "max": 25}}
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-17 00:01:26 UTC — gazda → artefact → relay

```
mod automat din marker: bench port=25566 jar=catserver
== FC-BENCH v5 — engine: catserver — 2 fire, Xmx3G, world copiat din productie ==
  jar: CatServer-1.16.5-1d8d6313-server.jar (8 MiB) sha 96f824793ab3
  server-port sincronizat cu markerul: 25566 | motd: FunCity RP Lite
java11 absent local: descarc Temurin 11 JRE (adoptium, verificat sha256)
    log la CRASH:
      | [23:56:54] [main/INFO]: Initializing MixinExtras via org.embeddedt.modernfix.forge.shadow.mixinextras.service.MixinExtrasServiceImpl(version=0.3.2).
      | [23:56:55] [main/INFO]: Patching LivingEntity#attackEntityFrom
      | [23:56:55] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
      | [23:56:55] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: Defaulting to no-operation (NOP) logger implementation
      | [23:56:55] [main/INFO]: [org.slf4j.helpers.Util:report:128]: SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
      | [23:56:55] [main/INFO]: ModernFix reached bootstrap stage (9.900 s after launch)
      | [23:56:56] [main/INFO]: Injecting BlockStateBase cache population hook into func_204519_t from me.jellysquid.mods.lithium.mixin.block.flatten_states.AbstractBlo
      | [23:56:56] [main/INFO]: Using Java 9+ class definer
      | [23:56:56] [main/INFO]: Patching ItemStack#onItemUse
      | [23:57:00] [main/INFO]: Vanilla bootstrap took 4261 milliseconds
      | [23:57:00] [modloading-worker-1/INFO]: Patching DataPackRegistries#<init>
      | [23:57:00] [modloading-worker-1/INFO]: Ksyxis: Ready to remove unneeded chunks. (platform: forge, version: 1.4.6, mixin: 0.8.4)
  runda 3: CRASH Done=?s zid=1s RSS=1MiB keep-up=0 erori=0
  liber la disc acum: 195 MiB
(sfarsit rc=0)
RC=0
  runda 1: CRASH Done=?s zid=18s RSS=?MiB keep-up=0 erori=0
  server-port sincronizat cu markerul: 25566 | motd: FunCity RP Lite
java11 absent local: descarc Temurin 11 JRE (adoptium, verificat sha256)
  runda 2: OK Done=1.761s zid=33s RSS=?MiB keep-up=0 erori=0
  server-port sincronizat cu markerul: 25566 | motd: FunCity RP Lite
java11 absent local: descarc Temurin 11 JRE (adoptium, verificat sha256)
  runda 3: OK Done=12.615s zid=67s RSS=?MiB keep-up=0 erori=0
  liber la disc acum: 194 MiB
(sfarsit rc=0)
RC=0
```
