#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CUANTIC ENGINE — ciopleste numele motorului direct in jarul de server (inclusiv in
jarurile interne `data/*universal*.jar` din CatServer), pastrand 100% intacte sirul de
versiune si licenta upstream-ului.

Ce schimba in bytecode (constant-pool structurat, DOAR literali String tag=8):
  1. `CraftServer.class` / `CatServer.class` / `Arclight` / `Mist`:
     literalul `"CatServer"` / `"Arclight"` / `"Mist"` -> `"CUANTIC"`
     => `Bukkit.getName()` intoarce nativ `"CUANTIC"`, iar la pornire serverul scrie:
        `This server is running CUANTIC version 1.16.5-1d8d6313 (MC: 1.16.5) ...`
  2. `net/minecraftforge/fml/BrandingControl.class`:
     literalul `"forge"` din `getServerBranding()` -> `"CUANTIC"`
     => pachetul `minecraft:brand` trimis nativ la login afiseaza pe ecranul F3 din joc
        `"CUANTIC" server`, iar Server Ping / Query raporteaza `"CUANTIC 1.16.5"`.

Nicio cale de clasa (`CONSTANT_Class` tag=7) si nicio semnatura (`CONSTANT_NameAndType`
tag=12) nu este atinsa.

Rulare:  python3 scripts/brand_engine.py IN.jar OUT.jar [NUME_NOU]
"""
import io
import json
import struct
import sys
import zipfile

TAG_UTF8 = 1
TAG_CLASS = 7
TAG_STRING = 8
TAG_NAME_AND_TYPE = 12
NUME_MOTOARE = {"CatServer", "Arclight", "Mist", "Mohist", "Kibotec"}


def patch_class(data: bytes, targets: set, new_name: str):
    """Inlocuieste doar intrarile CONSTANT_Utf8 din `targets` care sunt referite de
    CONSTANT_String (tag=8) si NU sunt referite de CONSTANT_Class (tag=7) sau
    CONSTANT_NameAndType (tag=12). Lungimea u2 se actualizeaza curat (fara spatii)."""
    if len(data) < 10 or data[0:4] != b"\xca\xfe\xba\xbe":
        return data, []
    count = struct.unpack(">H", data[8:10])[0]
    pos, i = 10, 1
    entries = {}          # idx -> (tag, raw_payload)
    str_refs = set()      # utf8 indices referenced by CONSTANT_String (tag=8)
    unsafe_refs = set()   # utf8 indices referenced by Class / NameAndType / etc.

    while i < count and pos < len(data):
        tag = data[pos]
        pos += 1
        if tag == TAG_UTF8:
            if pos + 2 > len(data):
                return data, []
            ln = struct.unpack(">H", data[pos:pos + 2])[0]
            raw = data[pos + 2:pos + 2 + ln]
            entries[i] = (tag, raw)
            pos += 2 + ln
        elif tag == TAG_STRING:
            idx = struct.unpack(">H", data[pos:pos + 2])[0]
            str_refs.add(idx)
            entries[i] = (tag, data[pos:pos + 2])
            pos += 2
        elif tag in (TAG_CLASS, 16, 19, 20):
            idx = struct.unpack(">H", data[pos:pos + 2])[0]
            unsafe_refs.add(idx)
            entries[i] = (tag, data[pos:pos + 2])
            pos += 2
        elif tag == TAG_NAME_AND_TYPE:
            i1, i2 = struct.unpack(">HH", data[pos:pos + 4])
            unsafe_refs.add(i1)
            unsafe_refs.add(i2)
            entries[i] = (tag, data[pos:pos + 4])
            pos += 4
        elif tag == 15:
            entries[i] = (tag, data[pos:pos + 3])
            pos += 3
        elif tag in (5, 6):
            entries[i] = (tag, data[pos:pos + 8])
            pos += 8
            i += 1
        else:
            entries[i] = (tag, data[pos:pos + 4])
            pos += 4
        i += 1

    hits = []
    rep_bytes = new_name.encode("utf-8")
    for idx in (str_refs - unsafe_refs):
        ent = entries.get(idx)
        if not ent or ent[0] != TAG_UTF8:
            continue
        txt = ent[1].decode("utf-8", "replace")
        if txt in targets:
            entries[idx] = (TAG_UTF8, rep_bytes)
            hits.append(txt)

    if not hits:
        return data, []

    out = bytearray(data[:10])
    i = 1
    while i < count:
        tag, payload = entries[i]
        out.append(tag)
        if tag == TAG_UTF8:
            out += struct.pack(">H", len(payload)) + payload
        else:
            out += payload
        if tag in (5, 6):
            i += 2
        else:
            i += 1
    out += data[pos:]
    return bytes(out), hits


def patch_jar_bytes(jar_bytes: bytes, new_name: str, note: str, is_root: bool = False):
    """Parcurge un jar (si orice jar intern `data/*.jar`) si ciopleste clasele tinta."""
    buf_in = io.BytesIO(jar_bytes)
    buf_out = io.BytesIO()
    n_cls = n_hit = 0
    pe_craft = False
    pe_brand = False
    cu_noi = []

    with zipfile.ZipFile(buf_in, "r") as zin, \
         zipfile.ZipFile(buf_out, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            fn = it.filename
            low = fn.lower()
            # Scoatem eventuale semnaturi ca jarul modificat sa nu fie respins de SecurityManager
            if fn.startswith("META-INF/") and low.endswith((".sf", ".rsa", ".dsa", ".ec")):
                continue
            data = zin.read(fn)
            if fn.endswith(".class"):
                n_cls += 1
                targets = set(NUME_MOTOARE)
                if fn.endswith("BrandingControl.class"):
                    targets.add("forge")
                new_data, hits = patch_class(data, targets, new_name)
                if hits:
                    data = new_data
                    n_hit += 1
                    if fn.endswith("CraftServer.class"):
                        pe_craft = True
                    if fn.endswith("BrandingControl.class"):
                        pe_brand = True
                    cu_noi.append(f"{fn.split('/')[-1]}:{','.join(hits)}")
            elif fn.endswith(".jar") and (fn.startswith("data/") or "universal" in low or "server" in low):
                sub_bytes, sub_stats = patch_jar_bytes(data, new_name, note, is_root=False)
                if sub_stats["clase_cioplite"] > 0:
                    data = sub_bytes
                    n_cls += sub_stats["clase_scanate"]
                    n_hit += sub_stats["clase_cioplite"]
                    pe_craft = pe_craft or sub_stats["pe_craftserver"]
                    pe_brand = pe_brand or sub_stats["pe_f3_brand"]
                    cu_noi.extend(sub_stats["primele"])
            zout.writestr(it, data)
        if is_root:
            zout.writestr("CUANTIC-ENGINE.txt", note)

    return buf_out.getvalue(), {
        "clase_scanate": n_cls,
        "clase_cioplite": n_hit,
        "nume": new_name,
        "pe_craftserver": pe_craft,
        "pe_f3_brand": pe_brand,
        "primele": cu_noi[:10],
    }


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, dst = argv[1], argv[2]
    new_name = (argv[3] if len(argv) > 3 else "CUANTIC").strip()
    note = (
        "CUANTIC Engine - jar de motor patch-uit la nivel de bytecode (constant-pool)\n"
        "============================================================================\n"
        f'Numele motorului in CraftServer.getName() si F3 (BrandingControl) = "{new_name}".\n'
        "Codul, licentele si sirul de versiune ale upstream-ului au ramas identice:\n"
        f'  /version = "This server is running {new_name} version <sirul upstream: build, MC, API>"\n'
        "Upstream: Luohuayu/CatServer (1.16.5, build 23.05.26-1, LGPL-3.0) / IzzelAliz/Arclight / Mist.\n"
        "Build: scripts/build_lite.py -> scripts/brand_engine.py.\n"
    )
    raw = open(src, "rb").read()
    patched, stats = patch_jar_bytes(raw, new_name, note, is_root=True)
    open(dst, "wb").write(patched)
    print(json.dumps(stats, ensure_ascii=False))
    return 0 if stats["clase_cioplite"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
