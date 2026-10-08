#!/usr/bin/env python3
"""Construieste Freeroam Lite: client .mrpack + DOUA variante de server:
  - MaxLite  : Forge pur + moduri-comenzi (FTB Essentials/Ranks) -> consum MINIM
  - Arclight : hibrid Forge+Bukkit cu pluginuri reale (EssentialsX, LuckPerms...)

Ruleaza in GitHub Actions (internet: api.modrinth.com, cdn.modrinth.com,
api.cfwidget.com, edge.forgecdn.net, maven.minecraftforge.net, github.com).

Utilizare: python3 scripts/build_lite.py <pack-original.mrpack> <director-output>
"""
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "iZentric/ServerRolePlayLite build_lite (github)"}


def log(msg):
    print(msg, flush=True)


def matches(name, patterns):
    n = name.lower()
    return any(p.lower() in n for p in patterns)


def http_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest, tries=4):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    import time
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
                shutil.copyfileobj(r, f)
            return
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            log(f"    (reincerc {i+1}/{tries-1} dupa eroare: {e})")
            time.sleep(5 * (i + 1))


def resolve_modrinth(slug, mc, loader):
    gv = urllib.parse.quote(json.dumps([mc]))
    ld = urllib.parse.quote(json.dumps([loader]))
    url = f"https://api.modrinth.com/v2/project/{slug}/version?game_versions={gv}&loaders={ld}"
    versions = http_json(url)
    if not versions:
        raise ValueError("nicio versiune")
    v = versions[0]
    f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
    return {"filename": f["filename"], "url": f["url"], "hashes": f.get("hashes", {}),
            "size": f.get("size", 0)}


def resolve_curseforge(slug, mc, loader):
    """Rezolva prin api.cfwidget.com (fara cheie API) + edge.forgecdn.net."""
    data = http_json(f"https://api.cfwidget.com/minecraft/mc-mods/{slug}")
    all_mc = [f for f in data.get("files", []) if mc in f.get("versions", [])]
    files = [f for f in all_mc if loader.capitalize() in f.get("versions", [])]
    if not files:
        # fallback: doar versiunea de MC; prefera fisierele cu numele loaderului
        named = [f for f in all_mc if loader.lower() in f.get("name", "").lower()]
        files = named or all_mc
    if not files:
        raise ValueError("niciun fisier compatibil")
    f = max(files, key=lambda x: x["id"])
    fid = f["id"]
    name = f["name"]
    if not name.endswith(".jar"):
        name = name + ".jar"
    url = f"https://edge.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{urllib.parse.quote(name)}"
    return {"filename": name, "url": url, "hashes": {}, "size": 0}


def resolve_any(slug, mc, loader):
    """Incearca Modrinth, apoi CurseForge, pentru fiecare alias (separate cu |)."""
    for alias in slug.split("|"):
        for fn, src in ((resolve_modrinth, "modrinth"), (resolve_curseforge, "curseforge")):
            try:
                info = fn(alias, mc, loader)
                info["source"] = src
                return info
            except Exception as e:  # noqa: BLE001
                log(f"    ({src}: {alias} -> {e})")
    log(f"  !! '{slug}' sarit (nu exista pt {mc} {loader} nicaieri)")
    return None


def resolve_ftb_maven(artifacts, prefix="1605"):
    """Maven-ul oficial FTB - sursa sigura pentru buildurile 1.16.5 (1605.x)."""
    for host in ("https://maven.ftb.dev/releases", "https://maven.saps.dev/releases"):
        for art in artifacts:
            try:
                url = f"{host}/dev/ftb/mods/{art}/maven-metadata.xml"
                req = urllib.request.Request(url, headers=UA)
                xml = urllib.request.urlopen(req, timeout=30).read().decode()
                vers = [v for v in re.findall(r"<version>([^<]+)</version>", xml)
                        if v.startswith(prefix)]
                if not vers:
                    continue

                def key(v):
                    m = re.search(r"build\.(\d+)", v)
                    return (v.split("-")[0], int(m.group(1)) if m else 0)

                v = sorted(vers, key=key)[-1]
                name = f"{art}-{v}.jar"
                return {"filename": name, "url": f"{host}/dev/ftb/mods/{art}/{v}/{name}",
                        "hashes": {}, "size": 0, "source": "ftb-maven"}
            except Exception as e:  # noqa: BLE001
                log(f"    (ftb-maven {art} @ {host}: {e})")
    return None


def zip_dir(zf, src_dir, arc_prefix=""):
    for base, _dirs, files in os.walk(src_dir):
        for fn in sorted(files):
            full = os.path.join(base, fn)
            arc = os.path.join(arc_prefix, os.path.relpath(full, src_dir))
            zf.write(full, arc)


OPTIONS_LITE = """\
renderDistance:8
graphicsMode:0
ao:1
maxFps:120
enableVsync:false
particles:1
renderClouds:false
entityShadows:false
biomeBlendRadius:0
mipmapLevels:2
"""

def strip_client_assets(jar_path):
    """ULTRA: scoate texturi/modele/sunete/shadere din jar-urile de SERVER.
    Serverul nu randeaza nimic - pastram lang/, data/, cod, mods.toml.
    Scoatem si semnaturile (jar modificat = semnatura invalida oricum)."""
    import tempfile
    CLIENT_DIRS = ("/textures/", "/models/", "/sounds/", "/shaders/", "/blockstates/", "/font/")
    try:
        before = os.path.getsize(jar_path)
        fd, tmp = tempfile.mkstemp(suffix=".jar", dir=os.path.dirname(jar_path))
        os.close(fd)
        with zipfile.ZipFile(jar_path) as zin, \
             zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                n = item.filename
                low = n.lower()
                if n.startswith("assets/") and "/lang/" not in low and (
                        any(d in low for d in CLIENT_DIRS)
                        or low.endswith((".png", ".ogg", ".wav", ".fsh", ".vsh", ".bbmodel"))):
                    continue
                if n.startswith("META-INF/") and low.endswith((".sf", ".rsa", ".dsa", ".ec")):
                    continue
                zout.writestr(item, zin.read(item))
        os.replace(tmp, jar_path)
        after = os.path.getsize(jar_path)
        if before - after > 1024 * 100:
            log(f"    ✂ {os.path.basename(jar_path)}: {before/1e6:.1f} -> {after/1e6:.1f} MB")
        return before - after
    except Exception as e:  # noqa: BLE001
        log(f"    !! strip esuat pe {os.path.basename(jar_path)}: {e} (ramane intreg)")
        return 0


SERVER_PROPERTIES = """\
#Minecraft server properties - Freeroam Lite (consum minim)
motd=\\u00A7e\\u00A7lFreeroam Lite \\u00A77- RolePlay pentru toti!
max-players=25
view-distance=4
sync-chunk-writes=false
network-compression-threshold=256
spawn-protection=128
allow-flight=true
enable-command-block=true
max-tick-time=-1
sync-chunk-writes=false
entity-broadcast-range-percentage=60
online-mode=true
pvp=true
difficulty=normal
gamemode=survival
level-name=world
enable-status=true
white-list=false
"""

SPIGOT_YML = """\
# spigot.yml - performanta maxima (doar varianta Arclight)
settings:
  save-user-cache-on-stop-only: true
  netty-threads: 2
world-settings:
  default:
    mob-spawn-range: 4
    entity-activation-range:
      animals: 16
      monsters: 20
      raiders: 24
      misc: 8
    entity-tracking-range:
      players: 48
      animals: 32
      monsters: 32
      misc: 16
      other: 32
    merge-radius:
      item: 3.5
      exp: 4.0
    item-despawn-rate: 4800
    max-entity-collisions: 2
    tick-inactive-villagers: false
    nerf-spawner-mobs: true
    ticks-per:
      hopper-transfer: 8
      hopper-check: 8
      monster-spawns: 2
    hopper-amount: 3
    arrow-despawn-rate: 300
    trident-despawn-rate: 300
"""

BUKKIT_YML = """\
# bukkit.yml - performanta maxima (doar varianta Arclight)
settings:
  allow-end: false
spawn-limits:
  monsters: 40
  animals: 8
  water-animals: 3
  water-ambient: 5
  ambient: 5
chunk-gc:
  period-in-ticks: 400
ticks-per:
  animal-spawns: 400
  monster-spawns: 4
  water-spawns: 11
  ambient-spawns: 11
  autosave: 6000
"""

PAPER_YML = """\
# paper.yml - optimizari Paper (doar varianta Mist) - consum minim cu pluginuri
world-settings:
  default:
    no-tick-view-distance: 8
    per-player-mob-spawns: true
    optimize-explosions: true
    disable-chest-cat-detection: true
    grass-spread-tick-rate: 4
    max-auto-save-chunks-per-tick: 8
    despawn-ranges:
      soft: 28
      hard: 96
    hopper:
      disable-move-event: true
    anti-xray:
      enabled: false
"""

SPIGOT_YML = """\
# Freeroam Lite ULTRA - raze de activare taiate (mobii departe de jucatori dorm)
settings:
  save-user-cache-on-stop-only: true
  netty-threads: 2
world-settings:
  default:
    entity-activation-range:
      animals: 12
      monsters: 20
      raiders: 24
      misc: 6
    entity-tracking-range:
      players: 48
      animals: 32
      monsters: 32
      misc: 16
      other: 32
    mob-spawn-range: 3
    nerf-spawner-mobs: true
    merge-radius:
      item: 3.5
      exp: 4.0
    ticks-per:
      hopper-transfer: 8
      hopper-check: 8
      monster-spawns: 2
    max-tick-time:
      tile: 20
      entity: 20
"""

AIKAR_FLAGS = (
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 "
    "-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC "
    "-XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M "
    "-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 "
    "-XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 "
    "-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 "
    "-XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -XX:+UseStringDeduplication"
)

README_MAXLITE = """\
=== FREEROAM LITE - SERVER "MAX LITE" (Forge pur 1.16.5 - CONSUM MINIM) ===

FARA strat Bukkit = cel mai mic consum posibil. Comenzile de "pluginuri" vin
din moduri server-side (jucatorii NU instaleaza nimic in plus):
  FTB Essentials -> /sethome /home /tpa /back /spawn /rtp /warp /nick /mute /fly
  FTB Ranks      -> ranguri si permisiuni (/ftbranks)

CERINTE: Java 8 sau Java 11 (NU 17+). RAM: porneste de la 1 GB, maxim 4 GB.

--- PE HOST (Zampto etc.) ---
1. Urca TOT continutul acestui zip in folderul serverului.
2. Ruleaza o data installerul (consola: java -jar forge-1.16.5-36.2.42-installer.jar --installServer)
   sau alege direct Forge 1.16.5 din panou.
3. Startup -> JAR: forge-1.16.5-36.2.42.jar ; Java version: 11 (sau 8).
4. Start. Prima pornire: 2-5 minute.

--- PE PC (Windows) ---
1. Java 11: https://adoptium.net/temurin/releases/?version=11
2. Dubluclick install-forge.bat (o singura data), apoi start.bat.

--- COMENZI DUPA PORNIRE ---
/sethome, /home, /tpa <nume>, /back, /spawn, /rtp, /warp
/ftbranks (din consola: ftbranks add <rank>) - ranguri
/forge tps - vezi performanta
"""

README_ARCLIGHT = """\
=== FREEROAM LITE - SERVER HIBRID (Arclight 1.16.5 = Forge + pluginuri Bukkit) ===

MODURI (mods/) + PLUGINURI (plugins/): EssentialsX(+Chat/Spawn), Vault, LuckPerms, Chunky.
Consum putin mai mare decat varianta MaxLite, dar accepta orice plugin Spigot.

CERINTE: Java 8 sau Java 11 (NU 17+). RAM: porneste de la 1 GB, maxim 4 GB.

--- PE HOST (Zampto etc.) ---
1. Urca TOT continutul acestui zip in folderul serverului.
2. Startup -> JAR: arclight-forge-1.16.5-1.0.25.jar ; Java version: 11 (sau 8).
3. Start. Prima pornire: 3-6 minute (Arclight isi descarca librariile).

--- COMENZI DUPA PORNIRE ---
/lp user <nume> permission set * true  -> admin total
/sethome /home /spawn /tpa             -> EssentialsX
/chunky radius 1000 + /chunky start    -> pre-genereaza lumea
"""


def write_start_scripts(sdir, server_jar):
    with open(os.path.join(sdir, "start.sh"), "w") as f:
        f.write(f"#!/bin/sh\njava -Xms1G -Xmx4G {AIKAR_FLAGS} -jar {server_jar} nogui\n")
    with open(os.path.join(sdir, "start.bat"), "w") as f:
        f.write(f"java -Xms1G -Xmx4G {AIKAR_FLAGS} -jar {server_jar} nogui\r\npause\r\n")
    with open(os.path.join(sdir, "server.properties"), "w") as f:
        f.write(SERVER_PROPERTIES)
    with open(os.path.join(sdir, "eula.txt"), "w") as f:
        f.write("# Prin folosirea acestui pachet acceptati https://aka.ms/MinecraftEULA\neula=true\n")


def main():
    if len(sys.argv) != 3:
        sys.exit("Utilizare: build_lite.py <pack.mrpack> <out_dir>")
    src_pack, out_dir = sys.argv[1], sys.argv[2]
    rules = json.load(open(os.path.join(ROOT, "pack-rules.json")))
    mc, forge = rules["minecraft"], rules["forge"]
    ver = rules["pack_version"]
    work = os.path.join(out_dir, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)

    log("== Dezarhivez pack-ul original ==")
    with zipfile.ZipFile(src_pack) as z:
        z.extractall(work)
    index = json.load(open(os.path.join(work, "modrinth.index.json")))
    override_mods_dir = os.path.join(work, "overrides", "mods")
    override_jars = sorted(os.listdir(override_mods_dir)) if os.path.isdir(override_mods_dir) else []

    report = {"client_added": [], "server_removed": [], "server_kept": [],
              "server_added": [], "maxlite_added": [], "arclight_added": []}

    # ---------------- CLIENT MRPACK ----------------
    log("== CLIENT lite (.mrpack) - toate modurile originale pastrate ==")
    client_files = list(index["files"])
    for slug in rules["add_client_modrinth"]:
        try:
            info = resolve_modrinth(slug, mc, "forge")
        except Exception as e:  # noqa: BLE001
            log(f"  !! '{slug}' sarit (client): {e}")
            continue
        client_files.append({
            "path": f"mods/{info['filename']}",
            "hashes": info["hashes"],
            "env": {"client": "required", "server": "unsupported"},
            "downloads": [info["url"]],
            "fileSize": info["size"],
        })
        report["client_added"].append(info["filename"])
        log(f"  + {info['filename']}")

    new_index = {
        "formatVersion": 1, "game": "minecraft", "versionId": ver,
        "name": rules["pack_name"],
        "summary": "Varianta lite a pack-ului Freeroam (Palma City) - merge pe orice PC.",
        "dependencies": {"minecraft": mc, "forge": forge},
        "files": client_files,
    }
    client_mrpack = os.path.join(out_dir, f"Freeroam-Lite-Client-{ver}.mrpack")
    with zipfile.ZipFile(client_mrpack, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(new_index, indent=2))
        z.writestr("overrides/options.txt", OPTIONS_LITE)
        for jar in override_jars:
            z.write(os.path.join(override_mods_dir, jar), f"overrides/mods/{jar}")
    log(f"  => {client_mrpack} ({os.path.getsize(client_mrpack)/1e6:.1f} MB)")

    # ---------------- MODURI DE SERVER (comune ambelor variante) ----------------
    log("== Moduri de server (comune) ==")
    base = os.path.join(out_dir, "server-base")
    bmods = os.path.join(base, "mods")
    shutil.rmtree(base, ignore_errors=True)
    os.makedirs(bmods, exist_ok=True)

    for f in index["files"]:
        name = os.path.basename(f["path"])
        if matches(name, rules["remove_from_server"]):
            report["server_removed"].append(name)
            log(f"  - scot (client-only): {name}")
            continue
        log(f"  ↓ {name}")
        download(f["downloads"][0], os.path.join(bmods, name))
        report["server_kept"].append(name)
    for jar in override_jars:
        if matches(jar, rules["remove_from_server"]):
            report["server_removed"].append(jar)
        else:
            shutil.copy2(os.path.join(override_mods_dir, jar), os.path.join(bmods, jar))
            report["server_kept"].append(jar)

    for slug in rules["add_server_modrinth"] + rules.get("add_server_extra_perf", []):
        info = resolve_any(slug, mc, "forge")
        if info:
            log(f"  + perf: {info['filename']} [{info['source']}]")
            download(info["url"], os.path.join(bmods, info["filename"]))
            report["server_added"].append(info["filename"])

    if rules.get("ultra_strip_assets"):
        log("== ULTRA: dezbrac jar-urile de server de assets client ==")
        saved = 0
        for j in sorted(os.listdir(bmods)):
            if j.endswith(".jar"):
                saved += strip_client_assets(os.path.join(bmods, j))
        log(f"  => total economisit: {saved/1e6:.1f} MB")

    # ---------------- VARIANTA 1: MAX LITE (Forge pur) ----------------
    log("== SERVER MaxLite (Forge pur - consum minim) ==")
    s1 = os.path.join(out_dir, "srv-maxlite")
    shutil.rmtree(s1, ignore_errors=True)
    shutil.copytree(base, s1)
    for slug in rules.get("maxlite_command_mods", []):
        if "ftb-library" in slug:
            info = resolve_ftb_maven(["ftb-library-forge", "ftblibrary", "ftb-library"]) \
                or resolve_any(slug, mc, "forge")
        else:
            info = resolve_any(slug, mc, "forge")
        if info:
            log(f"  + comenzi: {info['filename']} [{info['source']}]")
            download(info["url"], os.path.join(s1, "mods", info["filename"]))
            report["maxlite_added"].append(info["filename"])
    for slug in rules.get("maxlite_extreme_mods", []):
        info = resolve_any(slug, mc, "forge")
        if info:
            log(f"  + EXTREME: {info['filename']} [{info['source']}]")
            download(info["url"], os.path.join(s1, "mods", info["filename"]))
            report["maxlite_added"].append(f"EXTREME: {info['filename']}")
    forge_installer = f"forge-{mc}-{forge}-installer.jar"
    log("  ↓ Forge installer")
    download(f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc}-{forge}/{forge_installer}",
             os.path.join(s1, forge_installer))
    with open(os.path.join(s1, "install-forge.sh"), "w") as f:
        f.write(f"#!/bin/sh\njava -jar {forge_installer} --installServer\n")
    with open(os.path.join(s1, "install-forge.bat"), "w") as f:
        f.write(f"java -jar {forge_installer} --installServer\r\npause\r\n")
    write_start_scripts(s1, f"forge-{mc}-{forge}.jar")
    with open(os.path.join(s1, "CITESTE-MA.txt"), "w") as f:
        f.write(README_MAXLITE)
    z1 = os.path.join(out_dir, f"Freeroam-Lite-Server-MaxLite-{ver}.zip")
    with zipfile.ZipFile(z1, "w", zipfile.ZIP_DEFLATED) as z:
        zip_dir(z, s1)
    log(f"  => {z1} ({os.path.getsize(z1)/1e6:.1f} MB)")

    # ---------------- VARIANTA 2: ARCLIGHT (hibrid cu pluginuri) ----------------
    log("== SERVER Arclight (hibrid cu pluginuri) ==")
    s2 = os.path.join(out_dir, "srv-arclight")
    shutil.rmtree(s2, ignore_errors=True)
    shutil.copytree(base, s2)
    plugdir = os.path.join(s2, "plugins")
    os.makedirs(plugdir, exist_ok=True)
    for url in rules.get("plugins_github", []):
        name = os.path.basename(urllib.parse.urlparse(url).path)
        try:
            log(f"  ↓ plugin: {name}")
            download(url, os.path.join(plugdir, name))
            report["arclight_added"].append(f"plugin: {name}")
        except Exception as e:  # noqa: BLE001
            log(f"  !! plugin {name} sarit: {e}")
    for slug in rules.get("plugins_modrinth", []):
        try:
            info = resolve_modrinth(slug, mc, "bukkit")
        except Exception as e:  # noqa: BLE001
            log(f"  !! plugin '{slug}' sarit: {e}")
            continue
        log(f"  ↓ plugin: {info['filename']}")
        download(info["url"], os.path.join(plugdir, info["filename"]))
        report["arclight_added"].append(f"plugin: {info['filename']}")
    for sp in rules.get("plugins_spiget", []):
        try:
            res = sp["resource"]
            pat = re.compile(sp["match"])
            vers = http_json(f"https://api.spiget.org/v2/resources/{res}/versions?size=1000&sort=-releaseDate")
            v = next((x for x in vers if pat.match(x.get("name", ""))), None)
            if not v:
                raise ValueError(f"nicio versiune care sa se potriveasca cu {sp['match']}")
            log(f"  ↓ plugin: {sp['save_as']} (spiget v{v['name']})")
            download(f"https://api.spiget.org/v2/resources/{res}/versions/{v['id']}/download",
                     os.path.join(plugdir, sp["save_as"]))
            report["arclight_added"].append(f"plugin: {sp['save_as']} ({v['name']})")
        except Exception as e:  # noqa: BLE001
            log(f"  !! plugin spiget '{sp.get('save_as')}' sarit: {e}")
    log("  ↓ Arclight")
    download(rules["arclight_url"], os.path.join(s2, rules["arclight_jar"]))
    with open(os.path.join(s2, "spigot.yml"), "w") as f:
        f.write(SPIGOT_YML)
    with open(os.path.join(s2, "bukkit.yml"), "w") as f:
        f.write(BUKKIT_YML)
    with open(os.path.join(s2, "spigot.yml"), "w") as f:
        f.write(SPIGOT_YML)
    write_start_scripts(s2, rules["arclight_jar"])
    with open(os.path.join(s2, "CITESTE-MA.txt"), "w") as f:
        f.write(README_ARCLIGHT)
    z2 = os.path.join(out_dir, f"Freeroam-Lite-Server-Arclight-{ver}.zip")
    with zipfile.ZipFile(z2, "w", zipfile.ZIP_DEFLATED) as z:
        zip_dir(z, s2)
    log(f"  => {z2} ({os.path.getsize(z2)/1e6:.1f} MB)")

    # ---------------- VARIANTA 3: MIST (hibrid EXPERIMENTAL, patch-uri Paper) ----------------
    log("== SERVER Mist (hibrid experimental cu patch-uri Paper) ==")
    s3 = os.path.join(out_dir, "srv-mist")
    shutil.rmtree(s3, ignore_errors=True)
    shutil.copytree(s2, s3)
    os.remove(os.path.join(s3, rules["arclight_jar"]))
    log("  ↓ Mist")
    download(rules["mist_url"], os.path.join(s3, rules["mist_jar"]))
    with open(os.path.join(s3, "paper.yml"), "w") as f:
        f.write(PAPER_YML)
    write_start_scripts(s3, rules["mist_jar"])
    with open(os.path.join(s3, "CITESTE-MA.txt"), "w") as f:
        f.write(README_ARCLIGHT.replace("Arclight 1.16.5 = Forge + pluginuri Bukkit",
                                        "Mist 1.16.5 = Mohist + patch-uri PAPER, EXPERIMENTAL")
                .replace("arclight-forge-1.16.5-1.0.25.jar", rules["mist_jar"])
                .replace("(Arclight isi descarca librariile)", "(isi descarca librariile)")
                + "\nNOTA: Mist e un proiect abandonat din 2021 (experimental!). Daca ceva\n"
                  "crapa, treci pe varianta Arclight (stabila) sau MaxLite (consum minim).\n")
    z3 = os.path.join(out_dir, f"Freeroam-Lite-Server-Mist-EXPERIMENTAL-{ver}.zip")
    with zipfile.ZipFile(z3, "w", zipfile.ZIP_DEFLATED) as z:
        zip_dir(z, s3)
    log(f"  => {z3} ({os.path.getsize(z3)/1e6:.1f} MB)")

    # ---------------- VARIANTA 4: CATSERVER (hibrid, cel mai STABIL cu moduri+pluginuri) ----------------
    log("== SERVER CatServer (hibrid stabil moduri+pluginuri, build 2023) ==")
    s4 = os.path.join(out_dir, "srv-catserver")
    shutil.rmtree(s4, ignore_errors=True)
    shutil.copytree(s2, s4)
    os.remove(os.path.join(s4, rules["arclight_jar"]))
    log("  ↓ CatServer")
    download(rules["catserver_url"], os.path.join(s4, rules["catserver_jar"]))
    write_start_scripts(s4, rules["catserver_jar"])
    with open(os.path.join(s4, "CITESTE-MA.txt"), "w") as f:
        f.write(README_ARCLIGHT.replace("Arclight 1.16.5 = Forge + pluginuri Bukkit",
                                        "CatServer 1.16.5 = Forge + pluginuri Bukkit/Spigot (cel mai STABIL hibrid)")
                .replace("arclight-forge-1.16.5-1.0.25.jar", rules["catserver_jar"])
                .replace("(Arclight isi descarca librariile)", "(isi descarca librariile)")
                + "\nNOTA: CatServer e renumit pentru compatibilitate maxima moduri+pluginuri\n"
                  "(build mai 2023, cel mai recent hibrid 1.16.5 intretinut). Daca Mist crapa,\n"
                  "incearca intai varianta asta inainte de Arclight.\n")
    z4 = os.path.join(out_dir, f"Freeroam-Lite-Server-CatServer-{ver}.zip")
    with zipfile.ZipFile(z4, "w", zipfile.ZIP_DEFLATED) as z:
        zip_dir(z, s4)
    log(f"  => {z4} ({os.path.getsize(z4)/1e6:.1f} MB)")

    # ---------------- RAPORT ----------------
    with open(os.path.join(out_dir, "REPORT.md"), "w") as f:
        f.write(f"# Raport build Freeroam Lite ({ver})\n\n")
        f.write(f"Pack original: **{index.get('name')} {index.get('versionId')}** — MC {mc}, Forge {forge}\n\n")
        f.write("## 📱 CLIENT — toate modurile originale pastrate\n\n### Adaugat (doar FPS/RAM)\n")
        for n in report["client_added"]:
            f.write(f"- ✅ {n}\n")
        f.write("\n## 🖥️ SERVER MaxLite (Forge pur — CONSUM MINIM, recomandat)\n\n### Comenzi in loc de pluginuri\n")
        for n in report["maxlite_added"]:
            f.write(f"- ✅ {n}\n")
        f.write("\n## 🖥️ SERVER Arclight (hibrid cu pluginuri reale)\n\n")
        for n in report["arclight_added"]:
            f.write(f"- ✅ {n}\n")
        f.write("\n## Comune ambelor servere\n\n### Scos (client-only, inutil pe server)\n")
        for n in sorted(set(report["server_removed"])):
            f.write(f"- ❌ {n}\n")
        f.write("\n### Moduri de performanta adaugate\n")
        for n in report["server_added"]:
            f.write(f"- ✅ {n}\n")
        f.write("\n### Setari consum minim\n")
        f.write("- JVM: porneste la 1 GB, creste doar la nevoie (max 4 GB), G1GC Aikar\n")
        f.write("- view-distance=4 + sync-chunk-writes=false, max-players=15, mobi activati doar langa jucatori\n")
        f.write("- Arclight in plus: hoppers rarite, spawn-limits mici, villagers inactivi inghetati\n")

    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(base, ignore_errors=True)
    shutil.rmtree(s1, ignore_errors=True)
    shutil.rmtree(s2, ignore_errors=True)
    shutil.rmtree(s3, ignore_errors=True)
    shutil.rmtree(s4, ignore_errors=True)
    log("GATA.")


if __name__ == "__main__":
    main()
