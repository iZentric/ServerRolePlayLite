# FunCity RP Lite — în validare

FunCity este un proiect pentru o comunitate Minecraft 1.16.5 modată: oraș construit de proprietar și jucători **de la zero**, RP cu joburi/mafii, vehicule, mobilier și voce. Orașul nu are protecții preventive/claims; CoreProtect este cerut ca **jurnal** și instrument de rollback administrativ, nu ca prevenire automată. Motorul din repo este derivat din [MohistMC](https://github.com/MohistMC/Mohist)/Tenet (GPL-3.0); la orice distribuție a unui JAR derivat trebuie verificate licența, atribuirea și sursa corespunzătoare.

## Ce există deja

- `agent/DECIZII.md` și `agent/LISTA-MODURI-RP-LITE.md`: selecția **provizorie** 24 moduri client / 29 moduri server, nu pack instalat sau demonstrație de performanță.
- `agent/RP-LITE-PLUGINS.md`: rolurile pluginurilor și construcția liberă; CoreProtect trebuie verificat în instanța reală.
- `agent/AUDIT-CAPACITATE-RP.md`: configurații și backupuri istorice inspectate, date lipsă și riscuri pentru un server cu mulți jucători. Valorile `max-players` din capturi nu sunt capacitate măsurată.
- `agent/BETA-LITE.md`: poarta pentru import, conectare Forge și autentificare prin plugin, voce UDP, funcții RP, backup/restaurare și beta; **nu a fost trecută**.
- `scripts/fc_community_preflight.py`: doar citire, calculează un prag prudent de spațiu pentru un viitor backup/test; **nu face backup și nu dovedește capacitatea**.
- `functity/`: surse/patchuri ale motorului; `scripts/functity-stage.sh`: script existent de staging care nu trebuie lansat pe live fără confirmare și backup verificat.

## Stare

Niciun release Lite nou nu a fost publicat, niciun profil client nu a fost importat/verificat în Forge sau autentificat prin plugin, iar capacitatea cu jucători RP și performanța pe laptopuri vechi nu au fost măsurate. Fotografiile istorice ale gazdei și release-urile CUANTIC nu certifică serverul activ, uptime-ul, spațiul liber actual sau backupuri zilnice. Nu publicăm o adresă ori promisiuni despre „mulți jucători” până la probe actuale.

Progres și blocaje: `agent/PROGRES.md`. Orice modificare a lumii/serverului live necesită decizie separată, backup restaurat în test și plan de rollback.
