# FUNCTITY-STAGE 2026-10-14 09:47:09 UTC — gazda → artefact → relay

```
mod automat din marker: test port=25566 jar=b1.0827
== FUNCTITY TEST (boot->stop->reboot->persistenta) — 2026-10-14 09:44:25 UTC ==
  eula.txt scris la pornire (gasda eula=produtiei)
--- PROBA 1: boot (include instalarea bibliotecilor Mohist daca lips) ---
pornesc FunCity pe portul 25566 (heap 3G, java: /home/mndvasi9/funcity-live/jdk11/bin/java)
== verificare log ==
  mods in flotasare: 'Forge mod loading' = 1 (linii); 'found [0-9]* mods' = 
  plugini (Enabling): 14 linii Enabling
  erori EROARE/ERROR in log: 4 | Can't keep up: 0
  critice suspecte: 0
  motd anuntat prin SLP:
    SLP: timp depasit
oprire curata (server a iesit dupa 'stop')
--- PROBA 2: repornire din datele salvate (persistenta) ---
  level.dat prezent (1 MiB)
pornesc FunCity pe portul 25566 (heap 3G, java: /home/mndvasi9/funcity-live/jdk11/bin/java)
oprire curata (server a iesit dupa 'stop')
RESULTAT: boot1+stop+boot2 OK, 0 crash la salvare/realuare
(sfarsit rc=0)
RC=0
```
