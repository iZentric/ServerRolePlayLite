#!/usr/bin/env python3
"""Make a new, isolated Lite beta candidate from an exact, verified 25-mod mrpack.

Two SCOS client mods are removed and pinned RP voice is referenced remotely.
Source remains untouched; destination must not exist. This does NOT download mods, install,
launch Forge, benchmark FPS or authorize a release. Fail closed on any drift.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import zipfile

from fc_client_audit import INVENTORY
from fc_mrpack_audit import audit_pack, safe_path

MAX_ENTRIES = 4096
MAX_UNCOMPRESSED = 1_000_000_000
EXPECTED_REMOVALS = {'out_of_sight-1.16.4-1.0.1.jar',
                     'entitycollisionfpsfix-1.16-1.0.1.jar'}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def selection(decisions, historical, voice_metadata):
    text = Path(decisions).read_text(encoding='utf-8')
    block = text.split('## Client —', 1)[1].split('## Server —', 1)[0]
    rows = re.findall(r'^\| (C\d\d) \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS) \|', block, re.M)
    if len(rows) != 26 or len({id for id, _, _ in rows}) != 26:
        raise ValueError('expected 26 unique decisions (25 old + voice)')
    names = {n.casefold() for _, n, _ in rows}
    meta = json.loads(Path(voice_metadata).read_text(encoding='utf-8'))
    voice = meta['filename'].casefold()
    if (voice != 'voicechat-forge-1.16.5-2.3.23.jar' or
            meta['version_id'] != 'NSBUNV8T' or
            meta['download'] != ('https://cdn.modrinth.com/data/9eGKb6K1/'
                                 'versions/NSBUNV8T/voicechat-forge-1.16.5-2.3.23.jar') or
            not re.fullmatch('[a-f0-9]{128}', meta['sha512']) or
            not re.fullmatch('[a-f0-9]{40}', meta['sha1']) or
            type(meta['size']) is not int or meta['size'] <= 0):
        raise ValueError('unverified or changed Forge voice file metadata')
    inventories = INVENTORY.findall(Path(historical).read_text(encoding='utf-8'))
    if len(inventories) != 2 or inventories[0] != inventories[1] or names - {voice} != {
            n.casefold() for n in inventories[0].split(', ')} or len(names) != 26:
        raise ValueError('decisions must match the two historical 25-mod inventories')
    removed = {n.casefold() for _, n, state in rows if state == 'SCOS'}
    if removed != EXPECTED_REMOVALS or sum(n.casefold() == voice and state == 'PĂSTRAT'
                                           for _, n, state in rows) != 1:
        raise ValueError('unexpected Lite removals/voice choice')
    return names - removed, removed, meta


def mod_name(path):
    if path.startswith('mods/') and path.casefold().endswith('.jar'):
        return path.split('/')[-1].casefold()
    for root in ('overrides/', 'client-overrides/'):
        if path.startswith(root + 'mods/') and path.casefold().endswith('.jar'):
            return path.split('/')[-1].casefold()
    return None


def repack(source, expected_sha256, destination, decisions, historical,
           voice_metadata=Path('agent/voicechat-1.16.5-2.3.23.json'),
           without_pizzaland=False):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError('destination must be new and distinct from the source')
    if not re.fullmatch('[a-fA-F0-9]{64}', expected_sha256):
        raise ValueError('pin the source with a 64-character SHA256')
    if sha256_file(source) != expected_sha256.lower():
        raise ValueError('source SHA256 mismatch; no output written')
    keep, remove, voice = selection(decisions, historical, voice_metadata)
    keep, remove = set(keep), set(remove)
    if without_pizzaland:
        optional = 'pizzaland_v68.jar'
        if optional not in keep:
            raise ValueError('Pizzaland missing from baseline selection')
        keep.remove(optional)
        remove.add(optional)
    target_count = 23 if without_pizzaland else 24
    baseline = audit_pack(source, historical)
    if len(baseline['client_mod_names']) != 25:
        raise ValueError('source is not the historical 25-mod baseline')
    with zipfile.ZipFile(source) as src:
        infos = src.infolist()
        if len(infos) > MAX_ENTRIES or sum(i.file_size for i in infos) > MAX_UNCOMPRESSED:
            raise ValueError('archive size/entry safety limit exceeded')
        idx = json.loads(src.read('modrinth.index.json'))
        retained = []
        manifest_removed = []
        for f in idx['files']:
            name = mod_name(f['path'])
            if name in remove:
                manifest_removed.append(name)
            else:
                retained.append(f)
        override_removed = [mod_name(i.filename) for i in infos
                            if mod_name(i.filename) in remove and not i.is_dir()]
        if sorted(manifest_removed + override_removed) != sorted(remove):
            raise ValueError('expected each removed client JAR exactly once in source')
        changed = copy.deepcopy(idx)
        changed['files'] = retained + [{
            'path': 'mods/' + voice['filename'],
            'hashes': {'sha1': voice['sha1'], 'sha512': voice['sha512']},
            'downloads': [voice['download']], 'fileSize': voice['size'],
            'env': {'client': 'required', 'server': 'required'},
        }]
        changed['versionId'] = str(idx['versionId']) + ('-lite-no-pizzaland-lab' if without_pizzaland else '-lite-beta')
        changed['name'] = str(idx['name']) + (' Lite No Pizzaland Lab' if without_pizzaland else ' Lite Beta')
        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(prefix='.fc-lite-', suffix='.mrpack',
                                             dir=destination.parent, delete=False) as f:
                tmp = Path(f.name)
            with zipfile.ZipFile(tmp, 'w', allowZip64=True) as out:
                for info in infos:
                    safe_path(info.filename.rstrip('/'))
                    if mod_name(info.filename) in remove:
                        continue
                    if info.filename == 'modrinth.index.json':
                        out.writestr(info, json.dumps(changed, ensure_ascii=False,
                                                     separators=(',', ':')).encode('utf-8'))
                    elif info.is_dir():
                        out.writestr(info, b'')
                    else:
                        with src.open(info) as inp, out.open(info, 'w') as dest:
                            shutil.copyfileobj(inp, dest, 1024 * 1024)
            report = audit_pack(tmp, without_pizzaland_lab=without_pizzaland)
            actual = {n.casefold() for n in report['client_mod_names']}
            if actual != keep or report['client_mod_count'] != target_count:
                raise ValueError('output does not match the chosen client mods')
            if set(manifest_removed + override_removed) != remove:
                raise ValueError('unaccounted removal')
            digest = sha256_file(tmp)
            tmp.rename(destination)
            return {'scope': 'structural candidate only; NO launcher import/login/FPS',
                    'source_sha256': expected_sha256.lower(), 'output_sha256': digest,
                    'output_bytes': destination.stat().st_size,
                    'client_mod_count': target_count, 'removed': sorted(remove),
                    'added_remote': voice['filename'],
                    'remote_download_bytes_declared': report['remote_download_bytes_declared']}
        finally:
            if tmp is not None and tmp.exists():
                tmp.unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--source-sha256', required=True)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--decisions', type=Path, default=Path('agent/DECIZII.md'))
    p.add_argument('--historical', type=Path, default=Path('diag/pc-client.txt'))
    p.add_argument('--without-pizzaland', action='store_true',
                   help='isolated 23-mod comparison only; never touches Prism or a world')
    p.add_argument('--voice-metadata', type=Path,
                   default=Path('agent/voicechat-1.16.5-2.3.23.json'))
    a = p.parse_args()
    try:
        print(json.dumps(repack(a.source, a.source_sha256, a.output,
                                a.decisions, a.historical, a.voice_metadata,
                                without_pizzaland=a.without_pizzaland),
                              ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, IndexError, TypeError, zipfile.BadZipFile,
            json.JSONDecodeError) as exc:
        print(f'RESPINS: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
