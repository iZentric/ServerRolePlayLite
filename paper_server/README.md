# FunCity Paper low-spec server package

This is a **Paper-only** Java server setup. It does not use Forge, Arclight, Mohist, CatServer, mods, or custom server forks. The old `pack-rules.json` remains historical evidence for plugin choices, not an install recipe.

## Version decision

Use **Minecraft 26.2, Paper stable build 134**, with **Java 25**. Paper 26.3 has a stable build, but it is not selected because the public CoreProtect Community Edition 24.1 release required for block logging documents support only through 26.2. ProtocolLib's stable release is also behind; this lean stack does not include it because no retained plugin needs packet interception. The selected 26.2 release is the newest stable Paper target verified against the retained required plugin set.

- Fill v3 metadata: <https://fill.papermc.io/v3/projects/paper/versions/26.2/builds>
- Observed stable build: `paper-26.2-134.jar`
- Observed SHA-256: `3cce0a4922baf79bd8e1275ee5ff9f073f24675770e09b0d4be9442d513e7a6b`
- Paper's Java requirement for 26.1+: Java 25: <https://docs.papermc.io/paper/getting-started/>

`download_paper.py` always queries the official Fill v3 endpoint with a descriptive User-Agent, chooses the newest `STABLE` build for the pinned game version, downloads only the `server:default` file, and refuses to install it unless the downloaded bytes match Fill's SHA-256. Do not substitute a mirror or an old API endpoint.

## Plugin lock and scope

See [`plugins.lock.json`](plugins.lock.json) for the compatibility notes and source project pages. The retained stack is:

| Plugin | Locked version | Purpose |
| --- | --- | --- |
| EssentialsX + EssentialsXChat + EssentialsXSpawn | 2.22.0 | Core commands, chat, spawn |
| LuckPerms | 5.5.88 | Roles and permissions |
| WorldEdit | 7.4.5 | Admin map editing; WorldGuard dependency |
| WorldGuard | 7.0.19 | Protected spawn/administrative regions |
| CoreProtect Community Edition | 24.1 | Block history and rollback; caps the server at 26.2 |
| VaultUnlocked | 2.20.3 | Maintained Vault-compatible economy/chat/permission bridge |
| Chunky | 1.5.3 | Controlled world pre-generation |
| spark | Paper-bundled | Profiling; do not install a duplicate by default |

Plugin JAR binaries are intentionally not committed. Download each exact release from its official project page in the lock file and place it under `runtime/plugins/`. Install only the Bukkit/Paper artifact. The `runtime/` directory is ignored by Git.

Not carried over: ClaimChunk's last listed build has no declared 26.2 support, and the current FunCity direction is an open RP city without player land claims. ProtocolLib is not needed by this plugin set; SkinsRestorer is omitted while the server remains `online-mode=true`; EssentialsX AntiBuild/Protect overlap with WorldGuard. These decisions are explicit, not silent compatibility guesses. If any becomes a hard requirement, re-check it before installing or changing the Paper target.

## Hardware and memory

The laptop CPU, OS, RAM and disk type were left as placeholders and are not known. The separately reported HidenCloud allocation is **3 GiB RAM / 15 GiB disk**; that is a hosting allocation, not verified laptop hardware. At 3 GiB, the requested `RAM minus 2 GiB` policy leaves a 1 GiB heap, which is a severe limit for Paper 26.2 plus plugins. The launcher follows that policy and reserves about 2 GiB for the OS, but a 3 GiB host is not represented as comfortably sized. Do not run Chunky pre-generation on the 15 GiB allocation without checking free disk space first.

The launchers detect host/cgroup RAM and set equal `-Xms` and `-Xmx` to total GiB minus 2 GiB. If the machine has 2 GiB or less, startup stops rather than allocating an unsafe heap. `PAPER_HEAP_GB` can override the detected amount for a deliberately configured container, but only use it when you know the actual memory limit.

## First setup and first boot

Python 3.10+ and Java 25 must be on `PATH`. The launcher is for a fresh runtime folder and does not touch the old Arclight/hybrid server files.

### Linux

```sh
cd paper_server
python3 download_paper.py
java -version
# First invocation creates eula.txt and exits because the EULA is not accepted yet.
java -jar runtime/paper.jar --nogui
```

Read `runtime/eula.txt`. Only if you agree to Mojang/Microsoft's EULA, edit it to `eula=true`. Then create `runtime/plugins/`, install the locked plugin JARs there before generating plugin defaults, and run the first full boot:

```sh
mkdir -p runtime/plugins
chmod +x start.sh download_paper.py tune_configs.py backup.py
./start.sh
# Wait for Paper's "Done" line, then type: stop
python3 tune_configs.py
python3 backup.py
./start.sh
```

The first successful boot generates the defaults. Stop cleanly before running the tuner. It edits only keys already present in those generated files, aborts if any required key is absent, and makes timestamped `.bak` copies before changing anything. It does not create YAML keys or accept the EULA.

### Windows PowerShell

```powershell
cd paper_server
py .\download_paper.py
java -version
java -jar .\runtime\paper.jar --nogui
```

Read `runtime\eula.txt`; set `eula=true` only if you agree. Create `runtime\plugins\`, install the locked Paper plugin JARs there, then:

```powershell
New-Item -ItemType Directory -Force .\runtime\plugins | Out-Null
.\start.bat
# Wait for Paper's "Done" line, then type: stop
py .\tune_configs.py
py .\backup.py
.\start.bat
```

The Windows launcher is `start.ps1` wrapped by `start.bat`. Both launchers restart after a non-zero server exit and stop restarting after a clean `stop` (exit code 0). A crash loop waits 15 seconds between attempts; inspect the console/log instead of letting a broken plugin restart forever.

## Low-CPU configuration applied after defaults are generated

The tuner applies this starting profile only to generated paths that Paper provides:

- `server.properties`: view-distance **8**, simulation-distance **4**.
- `spigot.yml`: mob-spawn-range **3 chunks**.
- `bukkit.yml` and Paper world defaults: reduced, matching mob caps (monsters 35, animals/creatures 6, water categories 3–4, axolotls 2, ambient 1); per-player mob spawning enabled.
- Paper world defaults: where the generated keys exist, hard despawn range **48 blocks** and soft range **24 blocks** across mob categories. 48 blocks matches the 3-chunk spawn radius; no unknown key is added.

These are conservative starting points, not measured performance guarantees. Lower mob caps and shorter despawn distances change gameplay; review them in RP and profile the real server before making further reductions. No server config was generated or edited in this checkout because the Paper JAR could not be downloaded/launched here.

## Start, update and backup

Normal start:

- Linux: `./start.sh`
- Windows: `start.bat`

Before updating Paper, stop the server cleanly and run `python3 backup.py` (Windows: `py .\backup.py`). For a new stable build within the same Minecraft version, run `python3 download_paper.py --force`; the script re-queries Fill v3 and verifies the new checksum. For a Minecraft-version change, first re-check **every required plugin** and update the version choice in this package; do not follow “latest” blindly. Keep an off-machine copy of backups. Archives include worlds, plugin data/config, and server config; they may contain private credentials, so keep them private and never commit them.

## Spark: TPS and MSPT

Paper includes spark. From the server console or in-game with permission:

```text
/spark tps
/spark profiler start --timeout 120
```

20 TPS is the target. Brief dips can happen; sustained TPS below 20 means the server is falling behind. One Minecraft tick has a 50 ms budget: average MSPT at or below 50 ms is keeping up, while sustained MSPT above 50 ms means ticks are late and TPS will fall. Spark values are averages over windows, so compare the 1-minute/5-minute readings and use the profiler to identify the actual hot path (entities, chunks, plugin tasks, or saves) before changing more settings. Do not judge performance from one brief sample or a single average.

## Optional public access

If the home router cannot forward TCP 25565, a playit.gg tunnel can be added separately. Use the provider's official agent and keep its tunnel token out of Git, logs and chat. Do not switch `online-mode` off as a substitute for networking.

## Verification status

The bootstrap, checksum verifier, launchers, config tuner and backup utility are source-controlled. This sandbox could not retrieve the Paper artifact from Fill or accept the EULA on the server owner's behalf, so no real Paper `Done` line, runtime YAML, plugin load, TPS/MSPT sample, or laptop performance result is claimed. The exact laptop CPU/RAM/disk/OS also remain unknown. Follow the commands above on the machine that will host the server, then review `logs/latest.log` and the generated backups.
