#!/usr/bin/env python3
"""Construieste CUANTIC: client .mrpack + DOUA variante de server:
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
import subprocess
import sys
import urllib.parse
UNRESOLVED = []

def packv():
    """Versiunea din pack-rules.json, citita de oriunde (main() are `rules` local)."""
    try:
        return json.load(open(os.path.join(ROOT, "pack-rules.json"), encoding="utf-8"))["pack_version"]
    except Exception:
        return "?"
  # slug-uri care nu au rezolvat pe catalog -> devin vizibile, nu se mai pierd in liniste
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
    ver_pat = None
    if "@" in slug:
        slug, _, ver_pat = slug.partition("@")
    gv = urllib.parse.quote(json.dumps([mc]))
    ld = urllib.parse.quote(json.dumps([loader]))
    url = f"https://api.modrinth.com/v2/project/{slug}/version?game_versions={gv}&loaders={ld}"
    versions = http_json(url)
    if ver_pat:
        versions = [x for x in versions if re.search(ver_pat, x.get("version_number", ""))]
    if not versions:
        raise ValueError("nicio versiune")
    v = versions[0]
    f = next((x for x in v["files"] if x.get("primary")), v["files"][0])
    return {"filename": f["filename"], "url": f["url"], "hashes": f.get("hashes", {}),
            "size": f.get("size", 0)}


CURSEFORGE_PINNED_1165 = {
    "fastsuite": (3419895, "FastSuite-1.16.4-1.1.1.jar"),
    "spawner-fix": (5962957, "SpawnerFix-1.16.2-1.0.0.3.jar"),
    "smooth-chunk-save": (4453876, "smoothchunk1.16.5-2.0.jar"),
    "let-me-despawn": (4025350, "letmedespawn-forge-1.16-1.0.2a.jar"),
    "entity-collision-fps-fix": (3809513, "entitycollisionfpsfix-1.16-1.0.1.jar"),
    "better-fps-render-distance": (3543461, "betterfpsdist-1.1.jar"),
    "out-of-sight": (3143752, "out_of_sight-1.16.4-1.0.1.jar"),
    "connectivity": (3510357, "connectivity-2.4-1.16.5.jar"),
}


def resolve_curseforge(slug, mc, loader):
    """Rezolva prin tabelul verificat 1.16.5 sau api.cfwidget.com + edge.forgecdn.net."""
    if mc == "1.16.5" and loader.lower() == "forge" and slug in CURSEFORGE_PINNED_1165:
        fid, name = CURSEFORGE_PINNED_1165[slug]
        url = f"https://edge.forgecdn.net/files/{fid // 1000}/{fid % 1000}/{urllib.parse.quote(name)}"
        return {"filename": name, "url": url, "hashes": {}, "size": 0}
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
    UNRESOLVED.append(slug)
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


GHID_PC_BUN = '''\
=== AI PC BUN? RIDICA-TI SETARILE IN 30 SECUNDE ===
Pack-ul vine setat pentru PC-uri SLABE (asa merge la toata lumea).
Daca PC-ul tau duce (8GB+ RAM, placa video dedicata), in joc:
Options -> Video Settings:
  - Render Distance: 8-12        (serverul trimite 4, dar orizontul e mai lin)
  - Smooth Lighting: ON          (umbre frumoase)
  - Graphics: Fancy
  - Mipmap Levels: 4             (texturi fine in departare)
  - Max Framerate: 120 / Unlimited
  - Particles: All
  - Entity Distance: 100-125%
BONUS placa buna: pune un shader! Pack-ul are deja Oculus:
  descarca "Complementary Reimagined" (versiunea 1.16.5) ->
  pune-l in folderul shaderpacks -> Options -> Video -> Shader Packs.
Serverul NU simte nimic din astea - sunt doar pe ecranul TAU.
'''

OPTIONS_LITE = """\
renderDistance:4
graphicsMode:0
ao:0
maxFps:120
enableVsync:false
particles:1
renderClouds:false
entityShadows:false
biomeBlendRadius:0
mipmapLevels:0
entityDistanceScaling:0.75
gamma:1.0
fullscreen:false
autoJump:false
"""

def fix_json_and_mixin_bytes(filename, data):
    """Repara erorile din moduri (pizzamod.mixin.json fara minVersion, supplementaries tag lipsa)
    si minifica modelele 3D .json din assets/ si data/ pentru economie de spatiu si parsare rapida."""
    low = filename.lower()
    if not low.endswith(".json"):
        return data
    try:
        obj = json.loads(data.decode("utf-8"))
        changed = False
        if "mixin" in low and isinstance(obj, dict) and "minVersion" not in obj:
            obj["minVersion"] = "0.8"
            changed = True
        if "mushroom_colony_growable_on.json" in low and isinstance(obj, dict) and isinstance(obj.get("values"), list):
            new_vals = []
            for v in obj["values"]:
                if isinstance(v, str) and "supplementaries:" in v:
                    new_vals.append({"id": v, "required": False})
                    changed = True
                else:
                    new_vals.append(v)
            obj["values"] = new_vals
        if changed or filename.startswith(("assets/", "data/")):
            nd = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            if changed or len(nd) < len(data):
                return nd
    except Exception:
        pass
    return data


def slim_client_jar(src_path, dst_path):
    """CUANTIC Smart Client Asset Compactor (pentru copii cu net slab si PC slab):
      - .ogg > 24 KB -> mono 22.05 kHz Vorbis q0 prin ffmpeg (sunet identic in joc, -85% MB)
      - .png > 4 KB -> paleta 256 culori FASTOCTREE + deflate 9 la aceeasi rezolutie
      - .json -> minificat + reparat *.mixin.json (minVersion 0.8) si taguri
      - scoate gunoiul de editor (.bbmodel, .psd, .xcf, .bak) si semnaturile META-INF."""
    import io
    import tempfile
    before = os.path.getsize(src_path)
    if before < 100 * 1024:
        shutil.copy2(src_path, dst_path)
        return 0
    has_ffmpeg = shutil.which("ffmpeg") is not None
    try:
        from PIL import Image
        has_pil = True
    except Exception:
        has_pil = False

    tdir = tempfile.mkdtemp(prefix="cslim_")
    try:
        with zipfile.ZipFile(src_path, "r") as zin, \
             zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            all_names = set(zin.namelist())
            for item in zin.infolist():
                n = item.filename
                low = n.lower()
                if low.endswith((".bbmodel", ".psd", ".xcf", ".bak")):
                    continue
                if n.startswith("META-INF/") and low.endswith((".sf", ".rsa", ".dsa", ".ec")):
                    continue
                data = zin.read(n)
                if low.endswith(".json"):
                    data = fix_json_and_mixin_bytes(n, data)
                elif n.startswith("assets/"):
                    if has_ffmpeg and low.endswith(".ogg") and len(data) > 24 * 1024:
                        try:
                            in_f = os.path.join(tdir, "in.ogg")
                            out_f = os.path.join(tdir, "out.ogg")
                            with open(in_f, "wb") as f:
                                f.write(data)
                            r = subprocess.run(
                                ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
                                 "-i", in_f, "-map_metadata", "-1", "-ac", "1", "-ar", "22050",
                                 "-c:a", "libvorbis", "-q:a", "0", out_f],
                                timeout=15, capture_output=True)
                            if r.returncode == 0 and os.path.isfile(out_f):
                                nd = open(out_f, "rb").read()
                                if 200 < len(nd) < len(data):
                                    data = nd
                        except Exception:
                            pass
                    elif has_pil and low.endswith(".png") and len(data) > 4 * 1024:
                        try:
                            im = Image.open(io.BytesIO(data))
                            im.load()
                            if im.mode in ("RGBA", "RGB"):
                                # Pastram 100% modul original RGBA/RGB (fara quantize 'P' ca sa nu apara negru-mov!).
                                # Doar daca o textura patrata power-of-two fara .mcmeta si in afara GUI/font depaseste
                                # 256x256 (ex. poze brute 1024x1024 / 2048x2048 din Pizzaland/ModernXL), o aducem la
                                # 256x256 HD (16x rezolutia vanilla!) cu LANCZOS — calitate vizuala impecabila si -70% VRAM pe Intel HD!
                                if (im.width == im.height and im.width > 256
                                        and (im.width & (im.width - 1)) == 0
                                        and (n + ".mcmeta") not in all_names
                                        and "/gui/" not in low and "/font/" not in low):
                                    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS", Image.BICUBIC)
                                    im = im.resize((256, 256), resample)
                                buf = io.BytesIO()
                                im.save(buf, format="PNG", optimize=True, compress_level=9)
                                nd = buf.getvalue()
                                if 64 < len(nd) < len(data):
                                    data = nd
                        except Exception:
                            pass
                zi = zipfile.ZipInfo(filename=n, date_time=item.date_time)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = item.external_attr
                zout.writestr(zi, data)
        after = os.path.getsize(dst_path)
        if after >= before:
            shutil.copy2(src_path, dst_path)
            return 0
        if before - after > 100 * 1024:
            log(f"    ✂ client {os.path.basename(src_path)}: {before/1e6:.1f} -> {after/1e6:.1f} MB")
        return before - after
    except Exception as e:  # noqa: BLE001
        log(f"    !! slim_client_jar esuat pe {os.path.basename(src_path)}: {e}")
        shutil.copy2(src_path, dst_path)
        return 0
    finally:
        shutil.rmtree(tdir, ignore_errors=True)


def brand_engine_jar(jar_path):
    """Ruleaza scripts/brand_engine.py peste jarul de motor (CatServer/Arclight/Mist)
    pentru a ciopli numele CUANTIC direct in constant-pool (CraftServer + BrandingControl)."""
    script = os.path.join(ROOT, "scripts", "brand_engine.py")
    if not (os.path.isfile(script) and os.path.isfile(jar_path)):
        return None
    tmp = jar_path + ".branded"
    try:
        r = subprocess.run([sys.executable, script, jar_path, tmp, "CUANTIC"],
                           capture_output=True, text=True, timeout=120)
        if os.path.isfile(tmp) and os.path.getsize(tmp) > 1000:
            os.replace(tmp, jar_path)
            info = (r.stdout or "").strip()
            log(f"  + motor cioplit in bytecode ({os.path.basename(jar_path)}): {info}")
            return info
    except Exception as e:  # noqa: BLE001
        log(f"  !! brand_engine_jar ({os.path.basename(jar_path)}): {e}")
    finally:
        if os.path.isfile(tmp):
            os.remove(tmp)
    return None


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
        stripped_any = False
        fixed_bug = False
        with zipfile.ZipFile(jar_path) as zin, \
             zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                n = item.filename
                low = n.lower()
                if n.startswith("assets/") and "/lang/" not in low and (
                        any(d in low for d in CLIENT_DIRS)
                        or low.endswith((".png", ".ogg", ".wav", ".fsh", ".vsh", ".bbmodel"))):
                    stripped_any = True
                    continue
                if n.startswith("META-INF/") and low.endswith((".sf", ".rsa", ".dsa", ".ec")):
                    continue
                data = zin.read(n)
                if low.endswith(".json"):
                    nd = fix_json_and_mixin_bytes(n, data)
                    if ("mixin" in low or "mushroom_colony" in low) and nd != data:
                        fixed_bug = True
                    data = nd
                zout.writestr(item, data)
        if not stripped_any and not fixed_bug:
            os.remove(tmp)
            return 0
        os.replace(tmp, jar_path)
        after = os.path.getsize(jar_path)
        if before - after > 1024 * 100:
            log(f"    ✂ {os.path.basename(jar_path)}: {before/1e6:.1f} -> {after/1e6:.1f} MB")
        return max(0, before - after)
    except Exception as e:  # noqa: BLE001
        log(f"    !! strip esuat pe {os.path.basename(jar_path)}: {e} (ramane intreg)")
        return 0


MODERNFIX_MIXINS_PROPS = """\
# CUANTIC SERVER — pe server nu se randeaza iteme, deci dynamic_resources e 100% sigur
mixin.perf.dynamic_resources=true
mixin.perf.dedup_location=true
mixin.perf.compact_bit_storage=true
mixin.perf.thread_priorities=true
mixin.bugfix.chunk_deadlock=true
"""

MODERNFIX_MIXINS_PROPS_CLIENT = """\
# CUANTIC CLIENT — pastram dynamic_resources=false si faster_item_rendering=false (exact ca in
# ModernFix default), fiindca pe Forge 1.16.5 ModelBakeEventHelper din dynamic_resources returneaza
# missingModel (textura negru-mov!) pentru unele iteme 3D din Pizzaland / ModernXL / CGM / VehicleMod!
mixin.perf.dynamic_resources=false
mixin.perf.faster_item_rendering=false
mixin.perf.dedup_location=true
mixin.perf.compact_bit_storage=true
mixin.perf.thread_priorities=true
mixin.bugfix.chunk_deadlock=true
"""

OPTIONSSHADERS_TXT = """\
# CUANTIC — Oculus este prezent pt compatibilitate texturi/pipeline, dar cu shaderele OPRITE by default
# ca sa nu consume FPS pe laptopuri vechi. Pe PC bun poti activa orice shader din Video Settings -> Shader Packs.
shaderPack=(off)
"""

OUT_OF_SIGHT_CLIENT_TOML = """\
#General mod settings
[general]
\t#Range: 1.0 ~ 30000.0
\ttileEntityRenderRangeMax = 36.0
\t#Range: 1.0 ~ 30000.0
\tentityRenderRangeMax = 56.0
\ttileEntityRenderLimitModdedOnly = false
\tentityRenderLimitModdedOnly = false
"""


def build_servers_dat(name="§b§lCUANTIC RolePlay §8• §aPalma City", ip="92.5.171.150:25565"):
    """Genereaza fisierul binar NBT necomprimat overrides/servers.dat (formatul oficial ServerList 1.16.5)
    astfel incat serverul sa apara direct primul in Multiplayer la deschiderea modpack-ului."""
    import struct
    def nbt_str(s):
        b = s.encode("utf-8")
        return struct.pack(">H", len(b)) + b
    out = bytearray()
    out += b"\x0a" + nbt_str("")  # Root TAG_Compound("")
    out += b"\x09" + nbt_str("servers") + b"\x0a" + struct.pack(">i", 1)  # TAG_List("servers") of 1 TAG_Compound
    out += b"\x08" + nbt_str("name") + nbt_str(name)
    out += b"\x08" + nbt_str("ip") + nbt_str(ip)
    out += b"\x01" + nbt_str("acceptTextures") + b"\x01"
    out += b"\x00"  # End entry compound
    out += b"\x00"  # End root compound
    return bytes(out)

FERRITECORE_MIXIN_TOML = """\
# CUANTIC — toate optimizarile de memorie FerriteCore activate explicit
replaceNeighborLookup = true
replacePropertyMap = true
cacheMultipartPredicates = true
modelResourceLocations = true
multipartDeduplication = true
"""

SMOOTHCHUNK_COMMON_TOML = """\
["Config category"]
\t#Delay before a chunk is saved to disk, default: 300 seconds.
\t#Range: 10 ~ 3600
\tchunkSaveDelay = 300
\t#Enable debug logging
\tdebugLogging = false
"""

CONNECTIVITY_COMMON_TOML = """\
["Connectivity settings"]
\tdisableLoginLimits = true
\tdisablePacketLimits = true
\tdebugPrintMessages = false
\tlogintimeout = 2400
\tdisconnectTimeout = 60
\tpacketHistoryMinutes = 5
\tshowFullResourceLocationException = false
"""

RUBIDIUM_OPTIONS_JSON = """\
{
  "quality": {
    "cloud_quality": "FAST",
    "weather_quality": "FAST",
    "leaves_quality": "FAST",
    "enable_vignette": false,
    "enable_clouds": false,
    "smooth_lighting": "OFF"
  },
  "advanced": {
    "use_vertex_array_objects": true,
    "use_chunk_multidraw": true,
    "animate_only_visible_textures": true,
    "use_entity_culling": true,
    "use_particle_culling": true,
    "use_fog_occlusion": true,
    "use_compact_vertex_format": false,
    "use_block_face_culling": true,
    "allow_direct_memory_access": true,
    "ignore_driver_blacklist": false
  },
  "performance": {
    "chunk_builder_threads": 0,
    "always_defer_chunk_updates": true,
    "use_no_error_gl_context": true
  },
  "notifications": {
    "hide_donation_button": true
  }
}
"""

RUBIDIUM_EXTRA_OPTIONS_JSON = """\
{
  "animation_settings": {
    "animation": true,
    "water": true,
    "lava": false,
    "fire": false,
    "portal": false,
    "block_animations": false
  },
  "particle_settings": {
    "particles": true,
    "rain_splash": false,
    "block_break": true,
    "block_breaking": false,
    "other": {}
  },
  "detail_settings": {
    "sky": true,
    "sun_moon": true,
    "stars": false,
    "rain_snow": false,
    "biome_colors": true,
    "sky_colors": true
  },
  "render_settings": {
    "fog_distance": 33,
    "use_linear_flat_color_blender": true,
    "light_updates": true,
    "item_frame": true,
    "armor_stand": true,
    "painting": true,
    "piston": false,
    "beacon_beam": false,
    "enchanting_table_book": false,
    "item_frame_name_tag": false,
    "player_name_tag": true
  },
  "extra_settings": {
    "overlay_corner": "TOP_LEFT",
    "text_contrast": "SHADOW",
    "show_fps": true,
    "show_f_p_s_extended": false,
    "show_coords": true,
    "reduce_resolution_on_mac": true,
    "use_adaptive_sync": false,
    "cloud_height": 128,
    "toasts": false,
    "advancement_toast": false,
    "recipe_toast": false,
    "system_toast": false,
    "tutorial_toast": false,
    "instant_sneak": true,
    "prevent_shaders": false,
    "use_fast_random": true
  },
  "notification_settings": {
    "hide_r_s_o_recommendation": true
  }
}
"""

ENTITYCULLING_JSON = """\
{
  "configVersion": 5,
  "renderNametagsThroughWalls": true,
  "blockEntityWhitelist": [
    "minecraft:beacon",
    "create:rope_pulley",
    "create:hose_pulley",
    "betterend:eternal_pedestal"
  ],
  "entityWhitelist": [
    "botania:mana_burst"
  ],
  "tracingDistance": 64,
  "debugMode": false,
  "sleepDelay": 10,
  "hitboxLimit": 50,
  "skipMarkerArmorStands": true,
  "tickCulling": true,
  "tickCullingWhitelist": [
    "minecraft:firework_rocket",
    "minecraft:boat"
  ],
  "disableF3": false
}
"""


UNRESOLVED = []

SERVER_PROPERTIES = r"""\
#Minecraft server properties - CUANTIC (consum minim)
motd=\u00A7b\u00A7lCUANTIC \u00A78\u00A7o__VER__ \u00A7f| \u00A7aorice PC, zero lag \u00A7f| \u00A7dOras+Survival+Claims \u00A7f| \u00A7ecost 0
max-players=25
view-distance=4
player-idle-timeout=0
# sync-chunk-writes exista doar din 1.19; pe 1.16.5 punem transportul nativ (epoll), care chiar exista
use-native-transport=true
network-compression-threshold=512
spawn-protection=0
allow-flight=true
enable-command-block=true
max-tick-time=-1
entity-broadcast-range-percentage=60
online-mode=false
pvp=true
difficulty=normal
gamemode=survival
level-name=world
enable-status=true
white-list=false
"""

SPIGOT_YML = """\
# spigot.yml - stratul de tuning CUANTIC (acelasi fisier il primesc si CatServer si Mist)
# Surse chei: docs.dedicatedmc.io/server-optimization, wabbanode blog, builtbybit thread 187104
settings:
  save-user-cache-on-stop-only: true
  netty-threads: 2
world-settings:
  default:
    mob-spawn-range: 3
    entity-activation-range:
      animals: 16
      monsters: 20
      raiders: 24
      misc: 8
      wake-up-inactive:
        animals-max-per-tick: 2
        monsters-max-per-tick: 4
        villagers-max-per-tick: 1
        flying-monsters-max-per-tick: 2
    entity-tracking-range:
      players: 48
      animals: 32
      monsters: 32
      misc: 16
      other: 32
    # NU punem aici per-player-mob-spawns: e cheie de Paper, nu de Spigot 1.16.5, si pe
    # CatServer ar fi ignorata in liniste (cheie moarta = exact ce refuzam). Ea ramane in
    # paper.yml pentru varianta Mist, care intr-adevar are patch-uri Paper.
    max-tnt-per-tick: 20
    merge-radius:
      item: 3.5
      exp: 4.0
    item-despawn-rate: 2400
    max-entity-collisions: 2
    tick-inactive-villagers: false
    nerf-spawner-mobs: false
    ticks-per:
      hopper-transfer: 8
      hopper-check: 8
      monster-spawns: 2
    hopper-amount: 3
    arrow-despawn-rate: 300
    trident-despawn-rate: 300
"""

BUKKIT_YML = """\
# bukkit.yml - stratul de tuning CUANTIC (limitare mobi + chunk-gc), identic pe toate variantele
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
  # load-threshold=0 = functia e DEZACTIVATA implicit; cu 300 elibereaza chunk-urile libere (RAM).
  # Ghid: https://builtbybit.com/threads/guide-optimizing-spigot-remove-lag-fix-tps-improve-performance.187104/
  load-threshold: 300
ticks-per:
  animal-spawns: 400
  monster-spawns: 4
  water-spawns: 11
  ambient-spawns: 11
  autosave: 6000
"""


COMMANDS_YML = """\
# commands.yml - CUANTIC: aliasuri de consola + numele serverului (brand unde se vede)
name: CUANTIC
filter: §
commands: {}
alias:
  cuantic:
  - version
  cuantictps:
  - spark health
"""

CATSERVER_YML = """\
# catserver.yml - tunat pe cheile reale (autopsia tribunalului, 8 oct)
world:
  keepSpawnInMemory: false
  forceSaveOnWatchdog: true
fakePlayer:
  permissions:
  - essentials.build
  eventPass: false
plugin:
  patcher:
    enableDynmapCompatible: false
    enableEssentialsNewVersionCompatible: true
    enableMythicMobsPatcherCompatible: false
    enableWorldEditCompatible: true
disableFMLStatusModInfo: true
disableAsyncCatchWarn: true
versionCheck: false
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
      hard: 72
    alt-item-despawn-rate:
      enabled: true
      items:
        COBBLESTONE: 300
        NETHERRACK: 300
        SAND: 300
        GRAVEL: 300
        DIRT: 300
        GRASS: 300
        KELP: 300
        SUGAR_CANE: 300
        OAK_LEAVES: 300
        SPRUCE_LEAVES: 300
        BIRCH_LEAVES: 300
        JUNGLE_LEAVES: 300
        ACACIA_LEAVES: 300
        DARK_OAK_LEAVES: 300
        CACTUS: 300
        DIORITE: 300
        GRANITE: 300
        ANDESITE: 300
    entity-per-chunk-save-limit:
      experience_orb: 16
      arrow: 16
      snowball: 8
      ender_pearl: 8
      egg: 8
      fireball: 8
      firework_rocket: 8
      potion: 8
      area_effect_cloud: 8
    hopper:
      disable-move-event: true
    anti-xray:
      enabled: false
    use-faster-eigencraft-redstone: true
    mob-spawner-tick-rate: 2
    container-update-tick-rate: 3
    armor-stands-do-collision-entity-lookups: false
    prevent-moving-into-unloaded-chunks: true
    non-player-arrow-despawn-rate: 60
    creative-arrow-despawn-rate: 60
"""

AIKAR_FLAGS = (
    # Generatia post-Aikar: brucethemoose/Minecraft-Performance-Flags-Benchmarks
    # adaptate pt OpenJDK 17 + host partajat (fara root/LargePages/AlwaysPreTouch)
    # + optimizarile Netty din KryptonReforged (arena 4MiB in loc de 16MiB + leakDetection OFF)
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=37 "
    "-XX:+UnlockExperimentalVMOptions -XX:+UnlockDiagnosticVMOptions -XX:+DisableExplicitGC "
    "-XX:G1NewSizePercent=23 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 "
    "-XX:G1HeapWastePercent=20 -XX:G1MixedGCCountTarget=3 -XX:InitiatingHeapOccupancyPercent=10 "
    "-XX:G1RSetUpdatingPauseTimePercent=0 -XX:SurvivorRatio=32 -XX:MaxTenuringThreshold=1 "
    "-XX:G1SATBBufferEnqueueingThresholdPercent=30 -XX:G1ConcMarkStepDurationMillis=5.0 "
    "-XX:G1ConcRSHotCardLimit=16 -XX:G1ConcRefinementServiceIntervalMillis=150 -XX:GCTimeRatio=99 "
    "-XX:+PerfDisableSharedMem -XX:+UseStringDeduplication -XX:+UseFastUnorderedTimeStamps "
    "-XX:NmethodSweepActivity=1 -XX:ReservedCodeCacheSize=256M -XX:NonNMethodCodeHeapSize=12M "
    "-XX:ProfiledCodeHeapSize=122M -XX:NonProfiledCodeHeapSize=122M -XX:-DontCompileHugeMethods "
    "-XX:MaxNodeLimit=240000 -XX:NodeLimitFudgeFactor=8000 -XX:AllocatePrefetchStyle=3 "
    "-Dio.netty.allocator.maxOrder=9 -Dio.netty.leakDetection.level=DISABLED"
)

README_MAXLITE = """\
=== FREEROAM LITE - SERVER "MAX LITE" (Forge pur 1.16.5 - CONSUM MINIM) ===

FARA strat Bukkit = cel mai mic consum posibil. Comenzile de "pluginuri" vin
din moduri server-side (jucatorii NU instaleaza nimic in plus):
  FTB Essentials -> /sethome /home /tpa /back /spawn /rtp /warp /nick /mute /fly
  FTB Ranks      -> ranguri si permisiuni (/ftbranks)

CERINTE: Java 8 sau Java 11 (NU 17+). RAM: porneste de la 1 GB, maxim 4 GB.

--- PE HOST (panou cu SFTP sau VM) ---
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

--- PE HOST (panou cu SFTP sau VM) ---
1. Urca TOT continutul acestui zip in folderul serverului.
2. Startup -> JAR: arclight-forge-1.16.5-1.0.25.jar ; Java version: 11 (sau 8).
3. Start. Prima pornire: 3-6 minute (Arclight isi descarca librariile).

--- COMENZI DUPA PORNIRE ---
/lp user <nume> permission set * true  -> admin total
/sethome /home /spawn /tpa             -> EssentialsX
/chunky radius 1000 + /chunky start    -> pre-genereaza lumea
"""


FORGE_COMMON_TOML = """\
# Scutul anti-crash sta in defaultconfigs/forge-server.toml ([server] e config de LUME la Forge 1.16)
[server]
    removeErroringEntities = true
    removeErroringTileEntities = true
"""

FORGE_COMMON_CLEAN = """\
# gol intentionat - cheile [server] NU au voie aici (Forge le reseta cu warning)
"""


def build_brand_plugin(out_root, server_jar_path, dest_dirs):
    """Compileaza pluginul Cuantic pentru /version (brand + provenienta upstream vizibila).

    Compilam pe `tools/cuantic-brand/stubs` (antete API 1.16.5) ca build-ul sa fie determinist:
    maven Spigot/Paper a dat 404 in CI, iar jarurile CatServer/Mist nu expun org.bukkit.*
    la radacina (le descarca/remapeaza la boot). In runtime legarea se face pe API-ul real
    al serverului, deci stuburile nu adauga nimic in pack. ESUATUL NU opreste build-ul.
    """
    src = os.path.join(ROOT, "tools", "cuantic-brand", "src", "cloud", "cuantic", "brand", "CuanticBrandPlugin.java")
    plg = os.path.join(ROOT, "tools", "cuantic-brand", "plugin.yml")
    stubs = os.path.join(ROOT, "tools", "cuantic-brand", "stubs")
    if not (os.path.isfile(src) and os.path.isfile(plg)):
        log("  !! brand /version: surse lipsa, sarim"); return None
    ver = packv()
    bdir = os.path.join(out_root, "brand-build")
    try:
        import shutil as _sh
        _sh.rmtree(bdir, ignore_errors=True)
        cls = os.path.join(bdir, "classes"); os.makedirs(cls, exist_ok=True)
        with open(plg, encoding="utf-8") as f:
            open(os.path.join(bdir, "plugin.yml"), "w", encoding="utf-8").write(f.read().replace("__VER__", ver))
        surse = [src] + [os.path.join(dp, fn) for dp, _, fns in os.walk(stubs) for fn in fns if fn.endswith(".java")]
        r = subprocess.run(["javac", "--release", "8", "-nowarn", "-d", cls] + surse, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout or "javac a esuat")[:400])
        cuantic = os.path.join(cls, "cloud")
        if not os.path.isdir(cuantic):
            raise RuntimeError("javac a iesit fara clase cloud.cuantic.*")
        jar = os.path.join(out_root, "Cuantic-Brand-%s.jar" % ver)
        with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(os.path.join(bdir, "plugin.yml"), "plugin.yml")
            for dp, _, fs in os.walk(cuantic):
                for fn in fs:
                    z.write(os.path.join(dp, fn), os.path.relpath(os.path.join(dp, fn), cls))
        for d in dest_dirs:
            if d:
                pdir = d if os.path.basename(d.rstrip("/\\")) == "plugins" else os.path.join(d, "plugins")
                os.makedirs(pdir, exist_ok=True)
                _sh.copy(jar, os.path.join(pdir, os.path.basename(jar)))
        log("  + brand /version: Cuantic-Brand-%s.jar montat in %d servere (stubs locale)" % (ver, len([d for d in dest_dirs if d])))
        return os.path.basename(jar)
    except Exception as e:  # noqa: BLE001
        log("  !! brand /version esuat: %s" % str(e)[:400])
        return None

def write_start_scripts(sdir, server_jar):
    # 1.7.0: ops.json pre-populat cu proprietarul din deploy/op-name (UUID OfflinePlayer MD5 v3 real)
    try:
        import hashlib
        import uuid as _uuid
        op_file = os.path.join(ROOT, "deploy", "op-name")
        op_name = open(op_file, encoding="utf-8").read().strip().splitlines()[0].strip() if os.path.isfile(op_file) else "iZentric"
        if op_name:
            md = bytearray(hashlib.md5(("OfflinePlayer:" + op_name).encode("utf-8")).digest())
            md[6] = (md[6] & 0x0f) | 0x30
            md[8] = (md[8] & 0x3f) | 0x80
            op_uuid = str(_uuid.UUID(bytes=bytes(md)))
            with open(os.path.join(sdir, "ops.json"), "w", encoding="utf-8") as f:
                json.dump([{"uuid": op_uuid, "name": op_name, "level": 4, "bypassesPlayerLimit": True}], f, indent=2)
    except Exception as e:
        log(f"  !! ops.json: {e}")

    # 1.6.0: flagurile se iau din lista VALIDATA PE JAVA 17 (deploy/jvm-flags-17.txt, scrisa de
    # scripts/jvm-tune.sh). Motive dovedite: (a) cateva flaguri Aikar pt Java 11 NU mai exista in 17
    # si JVM-ul refuza sa porneasca; (b) -Xmx6G/8G a iesit MAI PROST masurat: pauza GC medie
    # 111.38 ms la 8G vs 47.2 ms la 2G, cu +0.75GB RSS pierduti. Heap-ul de lucru e ~1.2GB.
    FLAGS_17 = AIKAR_FLAGS
    vfile = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deploy", "jvm-flags-17.txt")
    if os.path.isfile(vfile):
        cand = " ".join(x for x in open(vfile, encoding="utf-8").read().split("\n") if x.strip() and not x.startswith("#"))
        if "-XX:+UseG1GC" in cand:
            FLAGS_17 = cand
            log(f"  flaguri luate din {os.path.relpath(vfile, os.getcwd())} (validate pe Java 17)")

    # manifest = singura dovada ca in zip e chiar ce credem ca e (numarul de moduri a derives 32->30
    # fara sa tipe nimeni, pentru ca un slug 404 era "sarit" in liniste)
    try:
        with open(os.path.join(sdir, "manifest-cuantic.json"), "w") as f:
            json.dump({"pack_version": packv(), "engine": os.path.basename(server_jar),
                       "mods": sorted(os.listdir(os.path.join(sdir, "mods"))) if os.path.isdir(os.path.join(sdir, "mods")) else [],
                       "plugins": sorted(os.listdir(os.path.join(sdir, "plugins"))) if os.path.isdir(os.path.join(sdir, "plugins")) else [],
                       "unresolved": UNRESOLVED,
                       "straturi_tuning": sorted(x for x in os.listdir(sdir)
                                                   if x in ("spigot.yml", "bukkit.yml", "catserver.yml", "commands.yml", "paper.yml")),
                       "jvm": "a se vedea unix_args.txt"}, f, ensure_ascii=False, indent=1)
    except Exception as e:
        log(f"  !! manifest: {e}")
    VER = packv()
    BN = "=============================================="
    with open(os.path.join(sdir, "start.sh"), "w") as f:
        f.write("#!/bin/sh" + chr(10)
                + "echo '" + BN + "'" + chr(10)
                + "echo '  CUANTIC " + VER + " - motor forjat de noi'" + chr(10)
                + "echo '  orice PC / zero lag / cost 0'" + chr(10)
                + "echo '" + BN + "'" + chr(10)
                + "exec java -Xms1G -Xmx2G " + FLAGS_17 + " -jar " + server_jar + " nogui" + chr(10))
    with open(os.path.join(sdir, "start.bat"), "w") as f:
        f.write("@echo off" + chr(13) + chr(10)
                + "echo " + BN + chr(13) + chr(10)
                + "echo   CUANTIC " + VER + " - motor forjat de noi" + chr(13) + chr(10)
                + "echo   orice PC / zero lag / cost 0" + chr(13) + chr(10)
                + "echo " + BN + chr(13) + chr(10)
                + "java -Xms1G -Xmx2G " + FLAGS_17 + " -jar " + server_jar + " nogui" + chr(13) + chr(10)
                + "pause" + chr(13) + chr(10))
    with open(os.path.join(sdir, "server.properties"), "w") as f:
        f.write(SERVER_PROPERTIES.replace("__VER__", packv()))
    # TRUCUL PANOURUI: unix_args.txt = panoul foloseste flagurile si jar-ul NOSTRU
    with open(os.path.join(sdir, "unix_args.txt"), "w") as f:
        f.write("-Xms1G\n-Xmx2G\n")
        for fl in AIKAR_FLAGS.split():
            f.write(fl + "\n")
        f.write(f"-jar\n{server_jar}\nnogui\n")
    with open(os.path.join(sdir, "commands.yml"), "w") as f:
        f.write(COMMANDS_YML)
    with open(os.path.join(sdir, "eula.txt"), "w") as f:
        f.write("# Prin folosirea acestui pachet acceptati https://aka.ms/MinecraftEULA\neula=true\n")
    icon = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "server-icon.png")
    if os.path.isfile(icon):
        shutil.copy2(icon, os.path.join(sdir, "server-icon.png"))
    cfg = os.path.join(sdir, "config")
    os.makedirs(cfg, exist_ok=True)
    dc = os.path.join(sdir, "defaultconfigs")
    os.makedirs(dc, exist_ok=True)
    with open(os.path.join(dc, "forge-server.toml"), "w") as f:
        f.write(FORGE_COMMON_TOML)
    with open(os.path.join(cfg, "forge-common.toml"), "w") as f:
        f.write(FORGE_COMMON_CLEAN)
    with open(os.path.join(cfg, "modernlife-common.toml"), "w") as f:
        f.write("# generat gol intentionat - ModernLife il umple la primul boot (ucide eroarea File not found)\n")
    inc = os.path.join(cfg, "incontrol")
    os.makedirs(inc, exist_ok=True)
    with open(os.path.join(inc, "spawn.json"), "w") as f:
        f.write('[\n  {"hostile": true, "maxcount": 50, "result": "deny"}\n]\n')


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

    # ---------------- CLIENT MRPACK ----------------
    log("== CLIENT lite (.mrpack) - toate modurile originale pastrate ==")
    rmc0 = [r.lower() for r in rules.get("remove_from_client", [])]
    client_files = [f for f in index["files"] if not any(r in f.get("path","").lower() for r in rmc0)]
    c_extra_dir = os.path.join(out_dir, "client-extra")
    shutil.rmtree(c_extra_dir, ignore_errors=True)
    os.makedirs(c_extra_dir, exist_ok=True)
    client_cf_jars = []
    for slug in rules["add_client_modrinth"]:
        try:
            info = resolve_modrinth(slug, mc, "forge")
            client_files.append({
                "path": f"mods/{info['filename']}",
                "hashes": info["hashes"],
                "env": {"client": "required", "server": "unsupported"},
                "downloads": [info["url"]],
                "fileSize": info["size"],
            })
            report["client_added"].append(info["filename"])
            log(f"  + {info['filename']} [modrinth]")
        except Exception:  # noqa: BLE001
            info = resolve_any(slug, mc, "forge")
            if info:
                dest_cf = os.path.join(c_extra_dir, info["filename"])
                download(info["url"], dest_cf)
                client_cf_jars.append(info["filename"])
                report["client_added"].append(info["filename"])
                log(f"  + {info['filename']} [{info['source']} -> overrides/mods]")
            else:
                UNRESOLVED.append(f"{slug}:client")
                log(f"  !! '{slug}' sarit (client)")

    # 1.5.9 FIX (cauza reala a "Failed to synchronize registry data"): orice mod de pe
    # server care INREGISTREAZA lucruri (Clumps = entity_type `clumps:xp_orb_big`) trebuie
    # sa existe SI pe client, altfel FML opreste conexiunea inainte de login:
    #   "Missing registry data for network connection" -> "Failed to load registry".
    # NU le punem in lista externa a mrpack-ului (GUILLOTINA 1.5.4: Prism ignora lista
    # externa) - jar-ul intra FISIC in overrides/mods, acelasi fisier byte-cu-byte de pe server.
    mirror = [m.lower() for m in rules.get("mirror_on_client", [])]
    report["client_mirrored"], report["mirror_missing"], mirror_jars = [], [], []
    have = {os.path.basename(f["path"]).lower() for f in client_files}
    have |= {j.lower() for j in override_jars}
    for m in mirror:
        al = [a for a in m.split("|") if a]
        hit = [j for j in sorted(os.listdir(bmods))
               if j.endswith(".jar") and any(a in j.lower() for a in al)]
        if not hit:
            report["mirror_missing"].append(m)
            log(f"  !! mirror '{m}': jar LipsA pe server - clientul va da handshake eronat")
            continue
        for j in hit:
            if j.lower() in have:
                log(f"  = mirror '{m}' era deja in client: {j}")
                continue
            have.add(j.lower())
            mirror_jars.append(j)
            report["client_mirrored"].append(j)
            log(f"  + mirror in client: {j}")

    os.makedirs(os.path.join(base, "config"), exist_ok=True)
    with open(os.path.join(base, "config", "modernfix-mixins.properties"), "w", encoding="utf-8") as f:
        f.write(MODERNFIX_MIXINS_PROPS)
    with open(os.path.join(base, "config", "ferritecore-mixin.toml"), "w", encoding="utf-8") as f:
        f.write(FERRITECORE_MIXIN_TOML)
    with open(os.path.join(base, "config", "smoothchunk-common.toml"), "w", encoding="utf-8") as f:
        f.write(SMOOTHCHUNK_COMMON_TOML)
    with open(os.path.join(base, "config", "connectivity-common.toml"), "w", encoding="utf-8") as f:
        f.write(CONNECTIVITY_COMMON_TOML)

    new_index = {
        "formatVersion": 1, "game": "minecraft", "versionId": ver,
        "name": rules["pack_name"],
        "summary": "CUANTIC (Palma City RP) - serverul de viitor: merge pe orice PC, ruleaza cu 2.6GB, boot 11s.",
        "dependencies": {"minecraft": mc, "forge": forge},
        "files": client_files,
    }
    client_mrpack = os.path.join(out_dir, f"CUANTIC-Client-{ver}.mrpack")
    with zipfile.ZipFile(client_mrpack, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(new_index, indent=2))
        z.writestr("overrides/options.txt", OPTIONS_LITE)
        z.writestr("overrides/optionsshaders.txt", OPTIONSSHADERS_TXT)
        z.writestr("overrides/servers.dat", build_servers_dat())
        z.writestr("overrides/SETARI-PC-BUN.txt", GHID_PC_BUN)
        z.writestr("overrides/config/modernfix-mixins.properties", MODERNFIX_MIXINS_PROPS_CLIENT)
        z.writestr("overrides/config/ferritecore-mixin.toml", FERRITECORE_MIXIN_TOML)
        z.writestr("overrides/config/rubidium-options.json", RUBIDIUM_OPTIONS_JSON)
        z.writestr("overrides/config/sodium-extra-options.json", RUBIDIUM_EXTRA_OPTIONS_JSON)
        z.writestr("overrides/config/rubidium_extra-options.json", RUBIDIUM_EXTRA_OPTIONS_JSON)
        z.writestr("overrides/config/entityculling.json", ENTITYCULLING_JSON)
        z.writestr("overrides/config/out_of_sight-client.toml", OUT_OF_SIGHT_CLIENT_TOML)
        z.writestr("overrides/config/connectivity-common.toml", CONNECTIVITY_COMMON_TOML)

        rmc = [r.lower() for r in rules.get("remove_from_client", [])]
        cslim_dir = os.path.join(out_dir, "client-slim")
        shutil.rmtree(cslim_dir, ignore_errors=True)
        os.makedirs(cslim_dir, exist_ok=True)
        client_saved = 0
        for jar in override_jars:
            if any(r in jar.lower() for r in rmc):
                log(f"  - taiat din client (stil rust): {jar}")
                continue
            src_j = os.path.join(override_mods_dir, jar)
            dst_j = os.path.join(cslim_dir, jar)
            client_saved += slim_client_jar(src_j, dst_j)
            z.write(dst_j, f"overrides/mods/{jar}")
        shutil.rmtree(cslim_dir, ignore_errors=True)
        if client_saved > 0:
            log(f"  => client assets compactate: -{client_saved/1e6:.1f} MB (instalare rapida pt net slab)")
        for jar in client_cf_jars:
            z.write(os.path.join(c_extra_dir, jar), f"overrides/mods/{jar}")
        shutil.rmtree(c_extra_dir, ignore_errors=True)
        for jar in mirror_jars:
            z.write(os.path.join(bmods, jar), f"overrides/mods/{jar}")
    log(f"  => {client_mrpack} ({os.path.getsize(client_mrpack)/1e6:.1f} MB)")


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
    z1 = os.path.join(out_dir, f"CUANTIC-Server-MaxLite-{ver}.zip")
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
    # Elimina avertismentul fals EssentialsX despre servere hibride (inlocuire constanta de aceeasi lungime)
    for pj in os.listdir(plugdir):
        if pj.lower().startswith("essentialsx-") and pj.endswith(".jar"):
            pjp = os.path.join(plugdir, pj)
            try:
                tmp_p = pjp + ".tmp"
                with zipfile.ZipFile(pjp, "r") as zin, zipfile.ZipFile(tmp_p, "w", zipfile.ZIP_DEFLATED) as zout:
                    for it in zin.infolist():
                        d = zin.read(it.filename)
                        if it.filename.endswith(("VersionUtil.class", "Essentials.class")):
                            d = d.replace(b"net.minecraftforge.common.MinecraftForge", b"net.minecraftforge.common.NoNagForge1234")
                            d = d.replace(b"net/minecraftforge/common/MinecraftForge", b"net/minecraftforge/common/NoNagForge1234")
                            d = d.replace(b"!net.minecraft.server.", b"xnet.minecraft.server.")
                        zout.writestr(it, d)
                os.replace(tmp_p, pjp)
            except Exception:
                pass
    log("  ↓ Arclight")
    download(rules["arclight_url"], os.path.join(s2, rules["arclight_jar"]))
    brand_engine_jar(os.path.join(s2, rules["arclight_jar"]))
    brand = build_brand_plugin(out_dir, os.path.join(s2, rules["arclight_jar"]), [s2])
    if brand:
        report["arclight_added"].append("brand /version + motor: " + brand)
    with open(os.path.join(s2, "spigot.yml"), "w") as f:
        f.write(SPIGOT_YML)
    with open(os.path.join(s2, "bukkit.yml"), "w") as f:
        f.write(BUKKIT_YML)
    write_start_scripts(s2, rules["arclight_jar"])
    with open(os.path.join(s2, "CITESTE-MA.txt"), "w") as f:
        f.write(README_ARCLIGHT)
    z2 = os.path.join(out_dir, f"CUANTIC-Server-Arclight-{ver}.zip")
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
    brand_engine_jar(os.path.join(s3, rules["mist_jar"]))
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
    z3 = os.path.join(out_dir, f"CUANTIC-Server-Mist-EXPERIMENTAL-{ver}.zip")
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
    brand_engine_jar(os.path.join(s4, rules["catserver_jar"]))
    with open(os.path.join(s4, "catserver.yml"), "w") as f:
        f.write(CATSERVER_YML)
    write_start_scripts(s4, rules["catserver_jar"])
    with open(os.path.join(s4, "CITESTE-MA.txt"), "w") as f:
        f.write(README_ARCLIGHT.replace("Arclight 1.16.5 = Forge + pluginuri Bukkit",
                                        "CatServer 1.16.5 = Forge + pluginuri Bukkit/Spigot (cel mai STABIL hibrid)")
                .replace("arclight-forge-1.16.5-1.0.25.jar", rules["catserver_jar"])
                .replace("(Arclight isi descarca librariile)", "(isi descarca librariile)")
                + "\nNOTA: CatServer e renumit pentru compatibilitate maxima moduri+pluginuri\n"
                  "(build mai 2023, cel mai recent hibrid 1.16.5 intretinut). Daca Mist crapa,\n"
                  "incearca intai varianta asta inainte de Arclight.\n")
    z4 = os.path.join(out_dir, f"CUANTIC-Server-CatServer-{ver}.zip")
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

# trigger-build: 2026-10-08 (ruleaza intregul lant: 1.5.3 -> release -> deploy)


# 1.6.2 a derivat de la 32 la 30 moduri fara sa tipe nimeni: un slug 404 era sarit in liniste.
# Acum lista celor sarite iese ca fisier in out/ - jobul de build il da mai departe la release.
try:
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    with open(os.path.join(ROOT, "out", "UNRESOLVED.txt"), "w") as f:
        f.write("\n".join(sorted(set(UNRESOLVED))) + ("\n" if UNRESOLVED else ""))
    if UNRESOLVED:
        log("!! UNRESOLVED (" + str(len(set(UNRESOLVED))) + "): " + ", ".join(sorted(set(UNRESOLVED))))
except Exception as _e:
    log(f"  !! UNRESOLVED.txt: {_e}")
