#!/usr/bin/env python3
"""Verify actual compiled FunCity classes inside a CatServer launcher.

The server launcher is a thin jar. Forge/Bukkit classes live in the embedded
`data/*-universal.jar`; checking for those classes at the outer root is wrong.
Never uploads or prints a JAR or its private log; only a verified SHA is used
by the caller. The binary is reobfuscated during packaging, so this checks
presence and identity, not equality of bytecode. It does not prove runtime or
multiplayer compatibility.
"""
import io
from pathlib import Path
import sys
import zipfile

IDENTITY = (
    'catserver/server/CatServer.class',
    'org/bukkit/craftbukkit/v1_16_R3/CraftServer.class',
)
BRIDGE = 'catserver/server/CatServerEventHandler.class'


class InvalidEngine(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidEngine(message)


def check_packaged(jar_path, brand='FunCity'):
    """Presence/branding gate for a local launcher; not a source provenance proof."""
    require(brand in ('FunCity', 'Cuantic'), 'unknown engine identity')
    with zipfile.ZipFile(jar_path) as outer:
        require(b'catserver.server.CatServerLaunch' in outer.read('META-INF/MANIFEST.MF'),
                'launcher manifest missing')
        entries = [name for name in outer.namelist()
                   if name.startswith('data/') and name.endswith('-universal.jar')]
        require(len(entries) == 1, 'one embedded Forge universal jar required')
        with zipfile.ZipFile(io.BytesIO(outer.read(entries[0]))) as universal:
            names = set(universal.namelist())
            for relative in IDENTITY:
                require(relative in names and brand.encode('ascii') in universal.read(relative),
                        'packaged identity missing: ' + relative)
            # ForgeGradle reobfuscates references, so byte-for-byte equality with
            # build/classes is *not* required. Both classes must be present.
            require(BRIDGE in names and len(universal.read(BRIDGE)) > 100,
                    'missing/empty packaged event bridge')
    return True


def check(jar_path, classes_root, brand='FunCity'):
    require(brand in ('FunCity', 'Cuantic'), 'unknown engine identity')
    for relative in IDENTITY:
        path = Path(classes_root) / relative
        require(path.is_file(), 'missing compiled class: ' + relative)
        data = path.read_bytes()
        require(brand.encode('ascii') in data, 'compiled identity missing: ' + relative)
    bridge_file = Path(classes_root) / BRIDGE
    require(bridge_file.is_file(), 'missing compiled event bridge')
    require(len(bridge_file.read_bytes()) > 100, 'empty compiled event bridge')
    return check_packaged(jar_path, brand)


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        sys.exit(2)
    try:
        check(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else 'FunCity')
    except (InvalidEngine, FileNotFoundError, KeyError, zipfile.BadZipFile, OSError) as exc:
        print('COMPILED_FUNCTITY_GATE_FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(2)
    print('COMPILED_FUNCTITY_GATE_PASS: identity and Forge/Bukkit bridge match embedded universal jar')
