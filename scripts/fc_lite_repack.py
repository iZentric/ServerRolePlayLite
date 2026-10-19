#!/usr/bin/env python3
"""Make a new, isolated Lite beta candidate from an exact, verified 25-mod mrpack.

Only the two SCOS client mods from agent/DECIZII.md are removed. Source remains
untouched; destination must not exist. This does NOT download mods, install,
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


def selection(decisions, historical):
    text = Path(decisions).read_text(encoding='utf-8')
    block = text.split('## Client —', 1)[1].split('## Server —', 1)[0]
    rows = re.findall(r'^\| (C\d\d) \| `([^`]+\.jar)` \| (PĂSTRAT|SCOS) \|', block, re.M)
    if len(rows) != 25 or len({id for id, _, _ in rows}) != 25:
        raise ValueError('expected 25 unique decisions in client section')
    names = {n.casefold() for _, n, _ in rows}
    inventories = INVENTORY.findall(Path(historical).read_text(encoding='utf-8'))
    if len(inventories) != 2 or inventories[0] != inventories[1] or names != {
            n.casefold() for n in inventories[0].split(', ')} or len(names) != 25:
        raise ValueError('decisions must match the two historical 25-mod inventories')
    removed = {n.casefold() for _, n, state in rows if state == 'SCOS'}
    if removed != EXPECTED_REMOVALS:
        raise ValueError('unexpected Lite removals; review code and decision together')
    return names - removed, removed


def mod_name(path):
    if path.startswith('mods/') and path.casefold().endswith('.jar'):
        return path.split('/')[-1].casefold()
    for root in ('overrides/', 'client-overrides/'):
        if path.startswith(root + 'mods/') and path.casefold().endswith('.jar'):
            return path.split('/')[-1].casefold()
    return None


def repack(source, expected_sha256, destination, decisions, historical):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve() or destination.exists():
        raise ValueError('destination must be new and distinct from the source')
    if not re.fullmatch('[a-fA-F0-9]{64}', expected_sha256):
        raise ValueError('pin the source with a 64-character SHA256')
    if sha256_file(source) != expected_sha256.lower():
        raise ValueError('source SHA256 mismatch; no output written')
    keep, remove = selection(decisions, historical)
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
        changed['files'] = retained
        changed['versionId'] = str(idx['versionId']) + '-lite-beta'
        changed['name'] = str(idx['name']) + ' Lite Beta'
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
            report = audit_pack(tmp)
            actual = {n.casefold() for n in report['client_mod_names']}
            if actual != keep or report['client_mod_count'] != 23:
                raise ValueError('output does not match the 23 chosen client mods')
            if set(manifest_removed + override_removed) != remove:
                raise ValueError('unaccounted removal')
            digest = sha256_file(tmp)
            tmp.rename(destination)
            return {'scope': 'structural candidate only; NO launcher import/login/FPS',
                    'source_sha256': expected_sha256.lower(), 'output_sha256': digest,
                    'output_bytes': destination.stat().st_size,
                    'client_mod_count': 23, 'removed': sorted(remove),
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
    a = p.parse_args()
    try:
        print(json.dumps(repack(a.source, a.source_sha256, a.output,
                                a.decisions, a.historical), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, IndexError, TypeError, zipfile.BadZipFile,
            json.JSONDecodeError) as exc:
        print(f'RESPINS: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
