#!/usr/bin/env python3
"""Read-only, offline audit of a FunCity .mrpack. No download, installation or release.

Usage: python3 scripts/fc_mrpack_audit.py PACK.mrpack --historical diag/pc-client.txt
A passing structural audit is NOT a Forge login, an FPS test or a guarantee
that the remote downloads still work. It never accesses diag/pc-probe.txt/out/.
"""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import zipfile

from fc_client_audit import DEPENDENCIES, ESSENTIAL, GAMEPLAY, INVENTORY

SHA512 = re.compile(r'[a-fA-F0-9]{128}\Z')
SHA1 = re.compile(r'[a-fA-F0-9]{40}\Z')


def safe_path(path):
    if (not isinstance(path, str) or not path or path.startswith('/') or
            '\\' in path or ':' in path or any(part in ('', '.', '..') for part in path.split('/'))):
        raise ValueError(f'unsafe pack path: {path!r}')
    return path


def audit_pack(archive, historical=None):
    with zipfile.ZipFile(archive) as z:
        infos = z.infolist()
        seen_zip = set()
        for info in infos:
            name = info.filename.rstrip('/')
            safe_path(name)
            if name.casefold() in seen_zip:
                raise ValueError(f'duplicate archive entry: {name}')
            seen_zip.add(name.casefold())
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError(f'symlink archive entry: {name}')
        entries = [i for i in infos if i.filename == 'modrinth.index.json' and not i.is_dir()]
        if len(entries) != 1 or entries[0].file_size > 2_000_000:
            raise ValueError('exactly one reasonably sized modrinth.index.json required')
        idx = json.loads(z.read(entries[0]))
        if idx.get('formatVersion') != 1 or idx.get('game') != 'minecraft':
            raise ValueError('expected Modrinth Minecraft pack format v1')
        deps = idx.get('dependencies') or {}
        if deps.get('minecraft') != '1.16.5' or not isinstance(deps.get('forge'), str) or not deps['forge']:
            raise ValueError('Minecraft 1.16.5 / Forge dependency not pinned')
        paths = set()
        mods = {}
        remote_bytes = 0
        missing_sizes = 0
        files = idx.get('files')
        if not isinstance(files, list):
            raise ValueError('manifest files must be a list')
        for f in files:
            if not isinstance(f, dict):
                raise ValueError('manifest file entry must be an object')
            path = safe_path(f.get('path'))
            key = path.casefold()
            if key in paths:
                raise ValueError(f'duplicate manifest path: {path}')
            paths.add(key)
            env = f.get('env') or {}
            if env.get('client') == 'unsupported':
                if path.startswith('mods/'):
                    raise ValueError(f'server-only mod must not be in Lite client pack: {path}')
                continue
            hashes = f.get('hashes') or {}
            if not (isinstance(hashes.get('sha512'), str) and SHA512.fullmatch(hashes['sha512']) and
                    isinstance(hashes.get('sha1'), str) and SHA1.fullmatch(hashes['sha1'])):
                raise ValueError(f'missing/invalid SHA512+SHA1 pin: {path}')
            urls = f.get('downloads') or []
            if not isinstance(urls, list) or not urls or not all(
                    isinstance(u, str) and urlsplit(u).scheme == 'https' and urlsplit(u).hostname
                    for u in urls):
                raise ValueError(f'missing secure download URL: {path}')
            size = f.get('fileSize')
            if size is None:
                missing_sizes += 1
            elif type(size) is not int or size <= 0:
                raise ValueError(f'invalid fileSize: {path}')
            else:
                remote_bytes += size
            if path.startswith('mods/') and path.lower().endswith('.jar'):
                mods[path.split('/')[-1].casefold()] = path.split('/')[-1]
        override_bytes = 0
        for info in infos:
            name = info.filename
            if info.is_dir() or not name.startswith(('overrides/', 'client-overrides/')):
                continue
            rel = name.split('/', 1)[1]
            if rel.casefold() in paths:
                raise ValueError(f'override collides with remote file: {rel}')
            paths.add(rel.casefold())
            override_bytes += info.file_size
            if rel.startswith('mods/') and rel.lower().endswith('.jar'):
                mods[rel.split('/')[-1].casefold()] = rel.split('/')[-1]
        jar_paths = sorted(p for p in paths if p.startswith('mods/') and p.endswith('.jar'))
        if len(jar_paths) != len(mods):
            raise ValueError('two client JARs have the same filename under different paths')
        names = sorted(mods.values(), key=str.casefold)
        for parent, children in DEPENDENCIES.items():
            if any(n.casefold().startswith(parent.casefold()) for n in names):
                for child in children:
                    if sum(n.casefold().startswith(child.casefold()) for n in names) != 1:
                        raise ValueError(f'client dependency missing/duplicated: {parent} -> {child}')
        required = ESSENTIAL + GAMEPLAY
        missing_required = [p for p in required if sum(n.casefold().startswith(p.casefold()) for n in names) != 1]
        if missing_required:
            raise ValueError(f'historical RP/compatibility mods absent or duplicated: {missing_required}')
        if historical:
            history = INVENTORY.findall(Path(historical).read_text(encoding='utf-8'))
            if len(history) != 2 or history[0] != history[1]:
                raise ValueError('two matching historical inventories required')
            previous = {n.casefold() for n in history[0].split(', ')}
            if set(mods) != previous:
                raise ValueError(f'client mod drift without A/B: missing={sorted(previous - set(mods))}, new={sorted(set(mods) - previous)}')
        return {'scope': 'archive structure only; no remote download/login/FPS measured',
                'name': idx.get('name'), 'version': idx.get('versionId'),
                'minecraft': deps['minecraft'], 'forge': deps.get('forge'),
                'archive_bytes': Path(archive).stat().st_size,
                'remote_download_bytes_declared': remote_bytes,
                'remote_files_without_declared_size': missing_sizes,
                'override_bytes_uncompressed': override_bytes,
                'client_mod_count': len(mods),
                'client_mod_names': names,
                'historical_names_match': bool(historical),
                'installation_time': 'NEMASURAT', 'forge_login': 'NEMASURAT',
                'fps_on_old_laptop': 'NEMASURAT'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('pack', type=Path)
    p.add_argument('--historical', type=Path, help='optional exact filename baseline; blocks unknown client changes')
    a = p.parse_args()
    try:
        report = audit_pack(a.pack, a.historical)
    except (OSError, KeyError, TypeError, json.JSONDecodeError, zipfile.BadZipFile, ValueError) as e:
        print(f'RESPINS: {e}', file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
