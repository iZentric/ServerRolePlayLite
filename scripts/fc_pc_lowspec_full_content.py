#!/usr/bin/env python3
"""Restore all old FunCity RP content to the ONE existing Lite Prism profile.

Uses archived 25-mod FunCity profile read-only; no new Prism instance or release.
Six JARs match the six restored on the isolated 15-mod server. Preserve accounts,
worlds, options and the user's other profiles; Minecraft must be closed.
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
ARCHIVE_RUN = '39332296211'
CONTENT = (
    'Pizzaland_v68.jar', 'pamhc2foodcore-1.16.3-1.0.2.jar',
    'supplementaries-1.16.5-0.18.4b.jar',
    'emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar',
)
DEPENDENCIES = ('selene-1.16.5-1.9.0.jar',
                'player-animation-lib-forge-0.4.0+1.16.5.jar')
EXTRA = CONTENT + DEPENDENCIES


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def restore(root, apply=False):
    root = Path(root)
    profile = root/PROFILE
    mods = profile/'.minecraft'/'mods'
    report = profile/'LAB-MANIFEST.json'
    if any(not p.is_dir() or is_link(p) for p in (root, profile, profile/'.minecraft', mods)):
        raise ValueError('LowSpec profile missing or linked')
    if not report.is_file() or is_link(report):
        raise ValueError('LowSpec manifest missing or linked')
    manifest = json.loads(report.read_text(encoding='utf-8'))
    existing = manifest.get('jar_sha256')
    if (manifest.get('minecraft') != '1.16.5' or manifest.get('forge') != '36.2.42' or
            manifest.get('release') != 'BLOCKED' or not isinstance(existing, dict) or
            len(manifest.get('client_optimizers', [])) != 4 or
            len(manifest.get('visual_compatibility', [])) != 1 or
            manifest.get('client_startup_optimizer') != ['lazydfu-0.1.3.jar'] or
            len(manifest.get('content_and_libraries', [])) not in (9, 15)):
        raise ValueError('LowSpec inventory/metadata drift')
    names = {p.name for p in mods.iterdir()}
    if names != set(existing) | ({name for name in EXTRA if (mods/name).exists()}):
        raise ValueError('unknown user mods; no changes')
    if any(not (mods/name).is_file() or is_link(mods/name) or sha(mods/name) != digest
           for name, digest in existing.items()):
        raise ValueError('existing LowSpec SHA mismatch; no changes')
    archive_batch = root.parent/'Arena-Archived-Instances'/ARCHIVE_RUN
    archive = archive_batch/'FunCity'
    if (not archive_batch.is_dir() or is_link(archive_batch) or
            not (archive_batch/'RESTORE.txt').is_file() or
            not archive.is_dir() or is_link(archive)):
        raise ValueError('original FunCity backup/restore marker missing or linked')
    pack = archive/'mmc-pack.json'
    if not pack.is_file() or is_link(pack):
        raise ValueError('original pack metadata missing')
    components = {c['uid']: c['version'] for c in json.loads(pack.read_text(encoding='utf-8'))['components']}
    if components.get('net.minecraft') != '1.16.5' or components.get('net.minecraftforge') != '36.2.42':
        raise ValueError('archived FunCity is not matching Forge 36.2.42')
    sources = {}
    for rel in ('.minecraft/mods', 'minecraft/mods'):
        parent = archive/rel
        if not parent.is_dir() or is_link(parent):
            continue
        if all((parent/name).is_file() and not is_link(parent/name) for name in EXTRA):
            sources = {name: parent/name for name in EXTRA}
            break
    if len(sources) != 6:
        raise ValueError('original FunCity missing six RP content/dependency JARs')
    source_hashes = {}
    for name, src in sources.items():
        if src.stat().st_size < 1024 or src.stat().st_size > 200_000_000:
            raise ValueError('invalid source JAR size: ' + name)
        with zipfile.ZipFile(src) as jar:
            if jar.testzip() is not None or 'META-INF/mods.toml' not in jar.namelist():
                raise ValueError('invalid source mod metadata/CRC: ' + name)
        source_hashes[name] = sha(src)
        if (mods/name).exists() and (is_link(mods/name) or sha(mods/name) != source_hashes[name]):
            raise ValueError('existing extra JAR differs from original: ' + name)
    if len(existing) == 21 and all(existing.get(n) == h for n, h in source_hashes.items()):
        return 'already_verified', len(existing)
    if len(existing) != 15 or len(manifest['content_and_libraries']) != 9:
        raise ValueError('cannot safely reconcile partial manifest')
    if not apply:
        return 'eligible_for_in_place_restore', 21
    created = []
    manifest_tmp = report.with_name('LAB-MANIFEST.json.new-content')
    if manifest_tmp.exists():
        raise ValueError('unresolved prior manifest update')
    try:
        for name, src in sources.items():
            dst = mods/name
            if not dst.exists():
                with src.open('rb') as inp, dst.open('xb') as out:
                    shutil.copyfileobj(inp, out, 1 << 20)
                created.append(dst)
            if sha(dst) != source_hashes[name]:
                raise ValueError('copied JAR SHA mismatch: ' + name)
        manifest['jar_sha256'].update(source_hashes)
        manifest['content_and_libraries'].extend(EXTRA)
        manifest['restored_original_content'] = list(EXTRA)
        with manifest_tmp.open('x', encoding='utf-8') as out:
            json.dump(manifest, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(manifest_tmp, report)
        return 'restored_in_place', len(manifest['jar_sha256'])
    except Exception:
        if manifest_tmp.exists():
            manifest_tmp.unlink()
        for dst in created:
            dst.unlink()  # only files this call created
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instances', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        status, count = restore(args.instances, args.apply)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    print('LowSpec content:', status, 'client_jar_count=', count,
          'original backup preserved; no other profile modified')
    return 0


if __name__ == '__main__':
    sys.exit(main())
