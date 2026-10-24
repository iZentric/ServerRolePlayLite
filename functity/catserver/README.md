# Motor FunCity — sursă verificabilă, Forge + Bukkit 1.16.5

[Obiective măsurabile și starea actuală](GOALS.md).

**Identitate:** fork experimental al [CatServer LGPL-3.0, tag 23.05.26-1](https://github.com/Luohuayu/CatServer/tree/1d8d63138be77a606df2a5e940b960065948f983), pin `1d8d63138be77a606df2a5e940b960065948f983`. Păstrează Forge 36.2.39, namespace-ul CraftBukkit/Spigot, protocolul, `catserver.yml` și atribuirea upstream; numele de operator/logger devine FunCity. Nu este o versiune nouă de Minecraft ori un substitut fără risc pentru Mohistul actual.

## Cod schimbat, nu doar numele

1. [0001 operator identity](patches/0001-funcity-operator-identity.patch): numai două șiruri de identitate, fără identități Forge/Bukkit modificate.
2. [0002 Forge block-place veto](patches/0002-preserve-forge-block-place-cancellation.patch): `CatServerEventHandler.onBlockPlaceEvent` se abonează inclusiv la `EntityPlaceEvent` deja anulat. Upstream îi putea reseta accidental starea după răspunsul `BlockPlaceEvent`/`BlockMultiPlaceEvent` Bukkit. Candidatul reține `forgeCanceled` înainte de callback și decide `forgeCanceled || bukkitCancelled || !canBuild`. Pentru evenimente neanulate de Forge, decizia rămâne identică. Nu schimbă breaking, ticks, permisiunile pluginurilor sau regulile lumii. Este un fix punctual de **corectitudine**; nu este o optimizare MSPT demonstrată.

[Poarta sursă](../../scripts/fc_funcity_bridge_patch_test.py) verifică aplicarea exactă pe sursa pin-uită și cele 8 combinații booleene. [Contractul Java 11 fără Gradle](https://github.com/iZentric/ServerRolePlayLite/actions/runs/40129947766) a compilat și executat **metoda Java reală patch-uită** cu stubs pentru 16 cazuri (place + multiplace, 8 combinații fiecare) și a respins versiunea mutantă fără veto Forge. Acesta este un test de logică pe tipuri simulate, **nu** boot sau compatibilitate cu modurile real instalate. Workflowul [de build](../../.github/workflows/funcity-catserver-source-build.yml) rulează la JDK 8/11/17, folosește Gradle serial pentru setup/build, verifică clasele FunCity atât compilate cât și în `data/*-universal.jar` din launcher, apoi încearcă boot/stop Java 11 pe loopback, cu lume generată și **zero** moduri/pluginuri/jucători. Verificarea este fail-closed; nu publică JAR, lume ori loguri brute. Dacă unul dintre pași eșuează, nu există binar aprobat.

## Ce am preluat și ce am refuzat de la alte motoare

- Din [Paper/server.properties](https://docs.papermc.io/paper/reference/server-properties/) preluăm **principiul** bugetului de chunkuri, nu cod Paper incompatibil cu Forge: brațul [view4-only](../capacity/3g-view4-only/server.properties) schimbă numai distanța, fără watchdog în A/B.
- Din [Forge 1.16.x](https://github.com/MinecraftForge/MinecraftForge/blob/1.16.x/src/main/java/net/minecraftforge/common/ForgeConfig.java) păstrăm implicit `removeErroringEntities=false` și `removeErroringTileEntities=false` în candidatul de siguranță: nu transformăm excepțiile modurilor în ștergere tăcută a conținutului.
- Am verificat [hookul Tenet 1.16.5](https://github.com/TiangongCraft/Tenet/blob/1.16.5/src/main/java/com/mohistmc/forge/ForgeEventHandler.java): filtrează apelurile Bukkit la threadul principal. **Nu îl copiem** în CatServer fără test, fiindcă ar omite evenimente Forge async observabile azi de pluginuri; nu este un câștig de capacitate demonstrat. Vechile patchuri hopper/ticketuri au eșuat ori au fost neconcludente în A/B.

## Config de laborator, nu live

[Profilul 3 GiB / vedere 4 și protecții hibride](../capacity/README.md) este un braț reversibil pe copie. Configurile `defaultconfigs/` nu suprascriu automat `world/serverconfig/` al unei lumi existente. Niciun installer nu trebuie să trimită peste hostul activ lumea, portul, modurile, pluginurile sau autentificarea pe baza acestor fișiere.

## Ce lipsește înainte de a spune «motorul meu e gata»

- Boot/stop Java 11 pe binarul compilat; apoi pornire pe **copie izolată** cu întregul inventar 34 JAR-uri server + 13 pluginuri și lumea RP reală. `Done` pe o lume goală nu este această probă.
- Client Forge Lite real: login/autentificare offline și anti-impersonare, reconectare, sincronizare de registru/recipes, voce UDP, vehicule/NPC, economie/permisiuni/CoreProtect și păstrarea inventarelor și construcțiilor după restart/restore. Verificăm pe copie mod Forge care anulează plasarea + plugin Bukkit de construcție; testăm separat WorldGuard cu entități modate și chunk loaders la restart dacă sunt folosite.
- Rampă A/B/B/A cu jucători distribuiți în oraș, p95/p99 MSPT, CPU fir principal, GC/RSS/uplink și zero pierderi RP pe host comparabil; [poarta de capacitate](../../scripts/fc_funcity_capacity_verdict.py) respinge dovezile incomplete. Vechile patchuri de hopper/ticketuri au dat regresii sau rezultate neconcludente și nu sunt incluse.
- Backup SHA + rollback privat și control oficial de Start/Restart înainte de orice înlocuire a `server.jar`. SFTP singur nu este controlul serverului.

**Limită explicită:** nimeni nu poate garanta zero buguri pentru orice combinație de moduri/pluginuri ori că acesta este cel mai rapid hybrid din 2026 fără aceleași teste pe aceeași sarcină. Motorul live rămâne neschimbat până la verificarea de mai sus; nu redistribuim un launcher cu componente terțe ca Release/ZIP neverificat.
