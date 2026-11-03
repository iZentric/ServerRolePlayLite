#!/usr/bin/env python3
"""Add LazyDFU ONLY to the one existing LowSpec lab from a local FunCity source.

No new Prism profile, remote download, old-profile edits or server-mod change.
Fail closed on unknown files, hash drift, symlinks or conflicting source JARs.
Minecraft must be closed; the Windows workflow checks running Java first.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_pc_lowspec_cleanup import is_link

PROFILE = 'FunCity-Lite-LowSpec-LAB-1.16.5'
JAR = 'lazydfu-0.1.3.jar'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def assert_regular(path):
    if not path.is_file() or is_link(path):
        raise ValueError('not a regular, non-linked file')


def lazy_source(root):
    found = {}
    for profile in root.iterdir():
        if not profile.is_dir() or is_link(profile) or 'FunCity' not in profile.name or 'LAB' in profile.name:
            continue
        pack = profile/'mmc-pack.json'
        if not pack.is_file() or is_link(pack):
            continue
        try:
            components = {c['uid']: c['version'] for c in json.loads(pack.read_text(encoding='utf-8'))['components']}
        except (KeyError, ValueError, UnicodeError):
            continue
        if components.get('net.minecraft') != '1.16.5' or components.get('net.minecraftforge') != '36.2.42':
            continue
        for name in ('.minecraft', 'minecraft'):
            mc = profile/name
            mods = mc/'mods'
            src = mods/JAR
            if not src.is_file() or any(is_link(p) for p in (mc, mods, src)):
                continue
            if src.stat().st_size > 20_000_000 or src.stat().st_size < 1000:
                raise ValueError('LazyDFU source JAR size is unexpected')
            digest = sha(src)
            found[digest] = src
    if len(found) != 1:
        raise ValueError('expected one unique local LazyDFU binary (no source or conflicting SHA)')
    digest, source = next(iter(found.items()))
    try:
        with zipfile.ZipFile(source) as jar:
            if jar.testzip() is not None or not {'META-INF/MANIFEST.MF', 'META-INF/mods.toml'} & set(jar.namelist()):
                raise ValueError('LazyDFU is not a readable Forge JAR')
    except zipfile.BadZipFile as exc:
        raise ValueError('LazyDFU source JAR invalid') from exc
    return source, digest


def add_lazy(root, apply=False):
    root = Path(root)
    profile = root/PROFILE
    mc, mods = profile/'.minecraft', profile/'.minecraft'/'mods'
    report = profile/'LAB-MANIFEST.json'
    if (not root.is_dir() or is_link(root) or not profile.is_dir() or is_link(profile) or
            not mc.is_dir() or is_link(mc) or not mods.is_dir() or is_link(mods)):
        raise ValueError('not the expected non-linked LowSpec profile')
    assert_regular(report)
    manifest = json.loads(report.read_text(encoding='utf-8'))
    if (manifest.get('minecraft') != '1.16.5' or manifest.get('forge') != '36.2.42' or
            manifest.get('release') != 'BLOCKED' or
            len(manifest.get('content_and_libraries', [])) != 9 or
            len(manifest.get('client_optimizers', [])) != 4 or
            len(manifest.get('visual_compatibility', [])) != 1):
        raise ValueError('LowSpec manifest differs from generated lab')
    pinned = manifest['jar_sha256']
    if not isinstance(pinned, dict) or len(pinned) not in (14, 15):
        raise ValueError('LowSpec JAR inventory drift')
    if {p.name for p in mods.iterdir()} != set(pinned) | ({JAR} if (mods/JAR).exists() else set()):
        raise ValueError('unexpected mod files in LowSpec profile; no changes')
    if any(not (mods/name).is_file() or is_link(mods/name) or sha(mods/name) != expected
           for name, expected in pinned.items()):
        raise ValueError('LowSpec JAR SHA mismatch; no changes')
    src, digest = lazy_source(root)
    dest = mods/JAR
    if dest.exists() and (is_link(dest) or sha(dest) != digest):
        raise ValueError('existing LazyDFU differs from local original')
    if pinned.get(JAR) == digest:
        return 'already_verified', digest
    if JAR in pinned:
        raise ValueError('recorded LazyDFU SHA differs from original')
    if not apply:
        return 'eligible_for_in_place_addition', digest
    created = False
    manifest_tmp = report.with_name('LAB-MANIFEST.json.new-lazydfu')
    if manifest_tmp.exists():
        raise ValueError('unresolved previous manifest update')
    try:
        if not dest.exists():
            with src.open('rb') as inp, dest.open('xb') as out:
                shutil.copyfileobj(inp, out, 1 << 20)
            created = True
        if sha(dest) != digest:
            raise ValueError('copied LazyDFU hash mismatch')
        manifest['jar_sha256'][JAR] = digest
        manifest['client_startup_optimizer'] = [JAR]
        with manifest_tmp.open('x', encoding='utf-8') as out:
            json.dump(manifest, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(manifest_tmp, report)
        return 'added_in_place', digest
    except Exception:
        if manifest_tmp.exists():
            manifest_tmp.unlink()
        if created and dest.exists():
            dest.unlink()  # only the file we just created
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--instances', type=Path, required=True)
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    try:
        status, digest = add_lazy(a.instances, a.apply)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    print(f'LowSpec LazyDFU: {status}; sha256={digest}; other profiles untouched')
    return 0


if __name__ == '__main__':
    sys.exit(main())
