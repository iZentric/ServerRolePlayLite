== SONDA EXTERNA 25565 ==
STATUS FAILED: server closed during status query
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-16 19:50:14 UTC — gazda → artefact → relay

```
mod automat din marker: install port=25565 jar=b1.0827
== INSTALL FunCity pe productie ==
  rollback: /home/mndvasi9/funcity-backup/install-20261016-194714 (tar world complet: ~1-2 min)
  ATENTIE: tar world a esuat (disc?) — instalez oricum, rollback partial ramas
  server vechi: oprit curat (save facut de el)
  c.sh: java -> J=$( [ -x "$HOME/funcity-live/jdk11/bin/java" ] && echo "$HOME/funcity-live/jdk1...
  jar+args+props+mods->productie (world neatins, voicechat pe default)
  c.sh repornit — il las sa faca boot (max 150s)
  boot 25565: NU | [19:48:35 INFO]: Done (3.940s)! For help, type "help"
  erori la pornire: 33 ( numaratoare la intreg logul, nu doar boot-ul curent)
    B [19:48:02 INFO]: Starting Minecraft server on *:25,566
  boot NU s-a confirmat in 150s — am readus unix_args+properties vechi; LAS c.sh pornit sa incerce motorul vechi singur; ROLLBACK.txt in /home/mndvasi9/cuantic-live
RC=0
```
