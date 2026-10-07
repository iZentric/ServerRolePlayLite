#!/usr/bin/env python3
"""Construieste Freeroam Lite (client .mrpack + server .zip) din pack-ul original.

Ruleaza in GitHub Actions (are nevoie de internet: api.modrinth.com, cdn.modrinth.com,
maven.minecraftforge.net).

Utilizare: python3 scripts/build_lite.py <pack-original.mrpack> <director-output>
"""
import json
import os
import shutil
import sys
import urllib.parse
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "iZentric/ServerRolePlayLite build_lite (contact: github)"}


def log(msg):
    print(msg, flush=True)


def matches(name, patterns):
    n = name.lower()
    return any(p.lower() in n for p in patterns)


def http_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def resolve_modrinth(slug, mc, loader):
    """Cea mai noua versiune a unui mod de pe Modrinth pentru mc+loader, sau None."""
    gv = urllib.parse.quote(json.dumps([mc]))
    ld = urllib.parse.quote(json.dumps([loader]))
    url = f"https://api.modrinth.com/v2/project/{slug}/version?game_versions={gv}&loaders={ld}"
    try:
        versions = http_json(url)
        if not versions:
            raise ValueError("nicio versiune compatibila")
        v = versions[0]
        f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
        return {
            "slug": slug,
            "version": v["version_number"],
            "filename": f["filename"],
            "url": f["url"],
            "hashes": f["hashes"],
            "size": f["size"],
        }
    except Exception as e:  # noqa: BLE001 - build tolerant
        log(f"  !! '{slug}' sarit (nu e disponibil pt {mc} {loader}): {e}")
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

SERVER_PROPERTIES = """\
#Minecraft server properties - Freeroam Lite (optimizat pentru host gratuit)
motd=\\u00A7e\\u00A7lFreeroam Lite \\u00A77- RolePlay pentru toti!
max-players=20
view-distance=7
network-compression-threshold=256
spawn-protection=0
allow-flight=true
enable-command-block=true
max-tick-time=-1
sync-chunk-writes=false
entity-broadcast-range-percentage=75
online-mode=true
pvp=true
difficulty=normal
gamemode=survival
level-name=world
enable-status=true
white-list=false
"""

AIKAR_FLAGS = (
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 "
    "-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch "
    "-XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M "
    "-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 "
    "-XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 "
    "-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 "
    "-XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1"
)

README_SERVER = """\
=== FREEROAM LITE - SERVER (Minecraft 1.16.5, Forge 36.2.42) ===

CERINTE: Java 8 sau Java 11. RAM recomandat: 4 GB (minim 2 GB).

--- PE HOST GRATUIT (Eternal Zero / Zampto / FreemcHosting etc.) ---
1. In panoul hostului alege tipul serverului: Forge 1.16.5 (build 36.2.42).
2. Urca TOT continutul acestui zip in folderul serverului (prin File Manager sau SFTP).
3. Daca hostul instaleaza singur Forge, nu mai rula installerul - doar pastreaza
   folderul mods/ + server.properties + eula.txt.
4. Porneste serverul din panou. Prima pornire dureaza 2-5 minute.

--- PE PC-UL TAU (Windows) ---
1. Instaleaza Java 8/11 (https://adoptium.net/temurin/releases/?version=11).
2. Dubluclick pe install-forge.bat (o singura data).
3. Dubluclick pe start.bat.
4. Pentru prieteni fara port forwarding: foloseste playit.gg (gratuit).

--- PE LINUX ---
1. ./install-forge.sh  (o singura data)
2. ./start.sh

NOTA: eula.txt este setat pe true = acceptati automat EULA-ul Minecraft
(https://aka.ms/MinecraftEULA). Daca nu sunteti de acord, puneti eula=false.

Memorie: editati start.sh / start.bat si schimbati -Xmx4G in cat aveti disponibil
(ex. -Xmx2G pe host cu 2 GB; lasati ~0.5 GB liber pentru sistem pe hosturi mici).
"""


def main():
    if len(sys.argv) != 3:
        sys.exit("Utilizare: build_lite.py <pack.mrpack> <out_dir>")
    src_pack, out_dir = sys.argv[1], sys.argv[2]
    rules = json.load(open(os.path.join(ROOT, "pack-rules.json")))
    mc, forge = rules["minecraft"], rules["forge"]
    work = os.path.join(out_dir, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)

    log("== Dezarhivez pack-ul original ==")
    with zipfile.ZipFile(src_pack) as z:
        z.extractall(work)
    index = json.load(open(os.path.join(work, "modrinth.index.json")))
    override_mods_dir = os.path.join(work, "overrides", "mods")
    override_jars = sorted(os.listdir(override_mods_dir)) if os.path.isdir(override_mods_dir) else []

    report = {
        "client_removed": [], "client_kept_index": [], "client_kept_override": [],
        "client_added": [], "server_removed": [], "server_kept": [], "server_added": [],
    }

    # ---------------- CLIENT MRPACK ----------------
    log("== Construiesc clientul lite (.mrpack) ==")
    client_files = []
    for f in index["files"]:
        name = os.path.basename(f["path"])
        if matches(name, rules["remove_from_client"]):
            report["client_removed"].append(name)
            log(f"  - scot (client): {name}")
        else:
            client_files.append(f)
            report["client_kept_index"].append(name)

    for slug in rules["add_client_modrinth"]:
        info = resolve_modrinth(slug, mc, "forge")
        if info:
            client_files.append({
                "path": f"mods/{info['filename']}",
                "hashes": info["hashes"],
                "env": {"client": "required", "server": "unsupported"},
                "downloads": [info["url"]],
                "fileSize": info["size"],
            })
            report["client_added"].append(info["filename"])
            log(f"  + adaug (client): {info['filename']}")

    new_index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": rules["pack_version"],
        "name": rules["pack_name"],
        "summary": "Varianta lite a pack-ului Freeroam (Palma City) - merge pe orice PC.",
        "dependencies": {"minecraft": mc, "forge": forge},
        "files": client_files,
    }

    client_mrpack = os.path.join(out_dir, f"Freeroam-Lite-Client-{rules['pack_version']}.mrpack")
    with zipfile.ZipFile(client_mrpack, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(new_index, indent=2))
        z.writestr("overrides/options.txt", OPTIONS_LITE)
        for jar in override_jars:
            if matches(jar, rules["remove_from_client"]):
                report["client_removed"].append(jar)
                log(f"  - scot (client/override): {jar}")
            else:
                z.write(os.path.join(override_mods_dir, jar), f"overrides/mods/{jar}")
                report["client_kept_override"].append(jar)
    log(f"  => {client_mrpack} ({os.path.getsize(client_mrpack)/1e6:.1f} MB)")

    # ---------------- SERVER ZIP ----------------
    log("== Construiesc serverul lite (.zip) ==")
    sdir = os.path.join(out_dir, "server")
    smods = os.path.join(sdir, "mods")
    shutil.rmtree(sdir, ignore_errors=True)
    os.makedirs(smods, exist_ok=True)

    for f in index["files"]:
        name = os.path.basename(f["path"])
        if matches(name, rules["remove_from_server"]):
            report["server_removed"].append(name)
            log(f"  - scot (server): {name}")
            continue
        log(f"  ↓ descarc: {name}")
        download(f["downloads"][0], os.path.join(smods, name))
        report["server_kept"].append(name)

    for jar in override_jars:
        if matches(jar, rules["remove_from_server"]):
            report["server_removed"].append(jar)
            log(f"  - scot (server/override): {jar}")
        else:
            shutil.copy2(os.path.join(override_mods_dir, jar), os.path.join(smods, jar))
            report["server_kept"].append(jar)

    for slug in rules["add_server_modrinth"]:
        info = resolve_modrinth(slug, mc, "forge")
        if info:
            log(f"  + adaug (server): {info['filename']}")
            download(info["url"], os.path.join(smods, info["filename"]))
            report["server_added"].append(info["filename"])

    log("  ↓ descarc installerul Forge")
    forge_installer = f"forge-{mc}-{forge}-installer.jar"
    download(
        f"https://maven.minecraftforge.net/net/minecraftforge/forge/{mc}-{forge}/{forge_installer}",
        os.path.join(sdir, forge_installer),
    )

    server_jar = f"forge-{mc}-{forge}.jar"
    with open(os.path.join(sdir, "install-forge.sh"), "w") as f:
        f.write(f"#!/bin/sh\njava -jar {forge_installer} --installServer\n")
    with open(os.path.join(sdir, "install-forge.bat"), "w") as f:
        f.write(f"java -jar {forge_installer} --installServer\r\npause\r\n")
    with open(os.path.join(sdir, "start.sh"), "w") as f:
        f.write(f"#!/bin/sh\njava -Xms2G -Xmx4G {AIKAR_FLAGS} -jar {server_jar} nogui\n")
    with open(os.path.join(sdir, "start.bat"), "w") as f:
        f.write(f"java -Xms2G -Xmx4G {AIKAR_FLAGS} -jar {server_jar} nogui\r\npause\r\n")
    with open(os.path.join(sdir, "server.properties"), "w") as f:
        f.write(SERVER_PROPERTIES)
    with open(os.path.join(sdir, "eula.txt"), "w") as f:
        f.write("# Prin folosirea acestui pachet acceptati https://aka.ms/MinecraftEULA\neula=true\n")
    with open(os.path.join(sdir, "CITESTE-MA.txt"), "w") as f:
        f.write(README_SERVER)

    server_zip = os.path.join(out_dir, f"Freeroam-Lite-Server-{rules['pack_version']}.zip")
    with zipfile.ZipFile(server_zip, "w", zipfile.ZIP_DEFLATED) as z:
        zip_dir(z, sdir)
    log(f"  => {server_zip} ({os.path.getsize(server_zip)/1e6:.1f} MB)")

    # ---------------- RAPORT ----------------
    rep_path = os.path.join(out_dir, "REPORT.md")
    with open(rep_path, "w") as f:
        f.write(f"# Raport build Freeroam Lite ({rules['pack_version']})\n\n")
        f.write(f"Pack original: **{index.get('name')} {index.get('versionId')}** — Minecraft {mc}, Forge {forge}\n\n")
        f.write("## 📱 CLIENT (pentru jucatori — orice PC)\n\n")
        f.write("### Scos (mai mult FPS, mai putina RAM)\n")
        for n in sorted(set(report["client_removed"])):
            f.write(f"- ❌ {n}\n")
        f.write("\n### Adaugat (optimizare)\n")
        for n in report["client_added"]:
            f.write(f"- ✅ {n} (EntityCulling — nu mai randeaza ce nu vezi)\n")
        f.write("\n### Pastrat\n")
        for n in report["client_kept_index"] + report["client_kept_override"]:
            f.write(f"- {n}\n")
        f.write("\n## 🖥️ SERVER (pentru host gratuit)\n\n### Scos (moduri doar-client)\n")
        for n in sorted(set(report["server_removed"])):
            f.write(f"- ❌ {n}\n")
        f.write("\n### Adaugat\n")
        for n in report["server_added"]:
            f.write(f"- ✅ {n}\n")
        f.write("\n### Pastrat\n")
        for n in report["server_kept"]:
            f.write(f"- {n}\n")
        f.write("\n## Setari aplicate\n")
        f.write("- Client: `options.txt` lite (render 8 chunks, graphics fast, fara nori/umbre entitati, VSync off)\n")
        f.write("- Server: `view-distance=7`, compresie retea, `max-tick-time=-1`, flaguri JVM Aikar (G1GC)\n")
        f.write("- RAM server: 2–4 GB (editabil in start.sh/start.bat)\n")

    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(sdir, ignore_errors=True)
    log("GATA.")


if __name__ == "__main__":
    main()
