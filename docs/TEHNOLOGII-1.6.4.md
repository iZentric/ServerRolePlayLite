# CUANTIC 1.6.4 — ce am căutat, ce am pus, ce am respins (cu surse)

Regula: nicio componentă „poate ajută". Fiecare bucată are motiv + sursă, iar ce nu merge la
1.16.5 / Forge / CatServer e scris mai jos ca respins, nu tăcut.

## Ce s-a schimbat în 1.6.4 (și de ce seamănă cu CatServer+J17 — pentru că nu-i dădeam straturile)

1. **Bug-ul real: straturile de tuning nu ajungeau pe serverul live.** `scripts/build_lite.py`
   scrie `spigot.yml`, `bukkit.yml`, `catserver.yml` în zip, dar `scripts/apply-live.sh` copia
   doar `*.jar|*.txt|*.json` ⇒ cutia live a rămas cu configurile **implicite** CatServer.
   Fix: apply copiază și `*.yml` + script nou `scripts/tune-live.sh` (idempotent, backup per
   fișier, verdict în `analysis/TUNE-LIVE.md` cu cheile aplicate și `Done (…s)` după repornire).
2. **`commands.yml`** cu `name: CUANTIC` + alias `/cuantic` (→ `version`) și `/cuantictps`.
3. **`server.properties`**: `use-native-transport=true` (cheie reală pe 1.16.5; Sponge 5.1 o
   documenta deja), `network-compression-threshold=512`, `entity-broadcast-range-percentage=60`,
   `view-distance=4`, `max-tick-time=-1`; **am scos `sync-chunk-writes`** (cheie din 1.19, ignorată
   pe 1.16.5 = componentă degeaba) și **am corectat MOTD-ul** (dublu backslash ⇒ Java Properties
   citea `\u00A7` literal, nu cod de culoare).
4. **`max-tnt-per-tick: 20`** în `spigot.yml`.
5. **Am scos `per-player-mob-spawns` din `spigot.yml`.** E cheie de **Paper**, nu de Spigot 1.16.5:
   pe CatServer ar fi fost ignorată în liniște (exact „cheia moartă" pe care o refuzăm). Rămâne
   în `paper.yml`, pentru varianta Mist, care are patch-uri Paper.
6. **Manifest reparat:** `manifest-cuantic.json` din fiecare zip dădea `NameError: name 'rules' is
   not defined`, înghițit de `except` ⇒ **nu se scria de loc** din 1.6.3. Acum `packv()` citește
   `pack-rules.json` și `engine` = jar-ul real, nu eticheta bătută în tastatură.
7. **Banner CUANTIC** în `start.sh` / `start.bat` (versiune + „orice PC / zero lag / cost 0").

## Duelul de GC: de ce a rămas G1 (și de ce „Shenandoah/ZGC sună bine" e o capcană)

Am adăugat `scripts/gc-duel.sh` (A = setul nostru G1, B = G1 cu `MaxGCPauseMillis=20`,
C = Shenandoah, D = ZGC), cu **măsurare pe serverul live, 150 s pe axă, și restaurare garantată**
din backup. Verdictul se scrie în `analysis/GC-DUEL.md`. Nu-l pornim orbește: rulează la cerere,
din butonul workflow-ului `TUNE`.

De ce nu le-am adoptat din oficiu, din surse (nu din „simt eu"):
- **Zerve (2026)**, „Best JVM Flags for Minecraft": benchmark-urile lui **brucethemoose** pe workload
  Minecraft: *„Shenandoah performs well on clients, but kills server throughput"* — fără generația
  tânără, firele concurente scanează tot heap-ul; pe 2 vCPU ale noastre asta se plătește.
- **Zerve**, aceeași sursă: ZGC a avut nevoie de **16 GB heap ca să egalizeze 8 GB pe G1** —
  noi avem 11.8 GB la tot bricheta ⇒ overhead-ul de memorie nu încape; iar *generational ZGC*
  cere **Java 21**, iar CatServer pe Java 21 **nu pornește** (măsurat în duelul nostru de motoare).
- **space-node.net (2026)**: G1+Aikar = 20-40 ms pauze medii, p99 < 200 ms; fix ceea ce vedem
  (115.9 ms medie cu 8 evenimente pe fereastră, p95 MSPT 2.0 ms, `Can't keep up` = 0).
- **onliveserver.com (2026)**: Shenandoah 3-10 ms pauze, dar cu cost de throughput — bun unde AI-ul e mic.
Concluzie: rămânem pe G1 cu setul validat, cu **datele noastre** pe masă; dacă duel-ul arată altceva,
setul se schimbă în `deploy/jvm-flags-17.txt` și o scriem aici.

## Respins, cu motiv (ca să nu le mai „redescoperim" peste două zile)

| Componentă | De ce nu |
|---|---|
| Starlight (Forge) | fișierele oficiale sunt 1.17.1+ (curseforge `starlight-forge/files/all`); pe 1.16.5 există doar forkul „Starlight x Create", **All Rights Reserved**, proveniență neprobată |
| LazyDFU | native Fabric; pe Forge efectul e acoperit de ModernFix (deja în pack) |
| Krypton / Lithium / Caetus / C2ME | Fabric; portul Forge pentru 1.16.5 e **RoadRunner** (1.5.2, 384 KB, deja în pack) |
| Arclight întreg | război de mixin cu motoarele de FPS ⇒ **NU PORNESTE** (măsurat) |
| CatServer + Java 21 | ASM nu citește J21 ⇒ **NU PORNESTE** (măsurat) |
| Mist | trăiește doar „dezbrăcat", cu LuckPerms mort; 4822 MB vs 2643 MB (măsurat) |
| Mohist | „updates paused" (libhunt/space-node) |
| Chunky pregen complet | discul gazdei: 5 GB, 66% ocupat; pregen full = crash de disc, nu de server |
| OpenJ9 / Semeru | RAM mai mic pe hârtie, dar risc mixin pe Forge 1.16.5; îl măsurăm izolat, nu-l punem în pack |
| Purpur/Pufferfish/Electrum | sunt **Bukkit pur**, nu rulează Forge ⇒ ar tăia modurile (kick = eșec) |
| Paper's per-player-mob-spawns pe CatServer | cheie ignorată ⇒ scoasă din spigot.yml (1.6.4) |

## Surse citite în această rundă (8 căutări, 20+ documente)

- curseforge.com/minecraft/mc-mods/roadrunner/files/4997510 · github.com/MaxNeedsSnacks/roadrunner/releases · mmcreviews.com/all/mods/roadrunner/
- curseforge.com/minecraft/mc-mods/starlight-forge/files/all · /files/3457784 · /mc-mods/starlight-x-create/files/3583654 · gdlauncher.com/mods/curseforge/starlight-forge · skinmc.net/project/starlight-forge
- mintlify.wiki/PaperMC/Paper/optimization/entity-performance · docs.dedicatedmc.io/server-optimization/paper-config-optimization-guide · wabbanode.com/blog/minecraft/best-settings-lag-free-minecraft-server · low.ms (best-minecraft-server-settings) · shockbyte.com (spigot.yml) · namehero.com (optimize)
- nexus-games.com/us/blog/minecraft-server-tps-fix-lag · docs.diekieboy.com/optimization-guide · docs.hidencloud.com (server-configuration) · mamboserver.com (how-to-optimize)
- zerve.gg/blog/best-jvm-flags-minecraft · onliveserver.com/java-garbage-collection-tuning-game-servers · space-node.net/blog/shenandoah-vs-zgc-minecraft-garbage-collector-2026 · javacodegeeks.com (G1 vs ZGC vs Shenandoah) · medium.com (G1/ZGC/Shenandoah)
- minecraft.fandom.com/wiki/Server.properties · docs.spongepowered.org/5.1.0 (server.properties) · pineriver.net (best settings)
