== SONDA EXTERNA 25565 ==
STATUS FAILED: timed out
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-16 19:53:58 UTC — gazda → artefact → relay

```
mod automat din marker: install port=25565 jar=b1.0827
== INSTALL FunCity pe productie ==
  disc liber inainte: 514 MiB
  rollback: /home/mndvasi9/funcity-backup/install-20261016-195252 (tar world complet: ~1-2 min)
  ATENTIE: tar world a esuat (disc?) — instalez oricum, rollback partial ramas
  server vechi: oprit curat (save facut de el)
  c.sh: java -> J=$( [ -x "$HOME/funcity-live/jdk11/bin/java" ] && echo "$HOME/funcity-live/jdk1...
  /home/mndvasi9/cuantic-live/server.properties: server-port=25565 (fortat de la /home/mndvasi9/funcity-live care era port de staging)
  jar+args+props+mods->productie (world neatins, voicechat pe default)
  c.sh repornit — il las sa faca boot (max 150s)
  boot 25565: DA | [19:48:35 INFO]: Done (3.940s)! For help, type "help"
  erori la pornire: 33 ( numaratoare la intreg logul, nu doar boot-ul curent)
    B [19:53:32 INFO]: Starting Minecraft server on *:25,565
  FUNCITY E PE PRODUCTIE — intri pe 92.5.171.150:25565
RC=0
```
