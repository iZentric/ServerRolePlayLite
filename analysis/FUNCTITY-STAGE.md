== SONDA EXTERNA 25565 ==
{"version": {"name": "Mohist 1.16.5", "protocol": 754}, "players": {"online": 1, "max": 25}}
== SONDA EXTERNA 25566 ==
STATUS FAILED: timed out

# FUNCTITY-STAGE 2026-10-16 21:20:43 UTC — gazda → artefact → relay

```
mod automat din marker: test port=25566 jar=b1.0827
== FUNCTITY TEST (boot->stop->reboot->persistenta) — 2026-10-16 21:18:00 UTC ==
  server-port sincronizat cu markerul: 25566 | motd: FunCity RP Lite
  voicechat: serverconfig/voicechat-server.toml -> port=24455
--- PROBA 1: boot (include instalarea bibliotecilor Mohist daca lips) ---
pornesc FunCity pe portul 25566 (heap 3G, java: /home/mndvasi9/funcity-live/jdk11/bin/java)
  [21:19:10 INFO]: Done (8.498s)! For help, type "help"
== verificare log ==
  mods in flotasare: 'Forge mod loading' = 1 (linii); 'found [0-9]* mods' = 
  plugini (Enabling): 14 linii Enabling
  erori EROARE/ERROR in log: 4 | Can't keep up: 0
  critice suspecte: 0
  motd anuntat prin SLP:
    SLP esuat: ECONNREFUSED
oprire curata (server a iesit dupa 'stop')
--- PROBA 2: repornire din datele salvate (persistenta) ---
  level.dat prezent (1 MiB)
pornesc FunCity pe portul 25566 (heap 3G, java: /home/mndvasi9/funcity-live/jdk11/bin/java)
  [21:20:19 INFO]: Done (4.838s)! For help, type "help"
oprire curata (server a iesit dupa 'stop')
RESULTAT: boot1+stop+boot2 OK, 0 crash la salvare/realuare
(sfarsit rc=0)
RC=0
```
