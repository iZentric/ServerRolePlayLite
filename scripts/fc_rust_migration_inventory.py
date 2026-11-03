#!/usr/bin/env python3
"""Offline, read-only inventory for a *private inactive copy* of the RP pack.

Output includes filenames and hashes: it is PRIVATE, must be created outside Git.
This does not classify a mod, prove a license, port an API or measure capacity.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

MARKER = 'FUNCITY_INACTIVE_ISOLATED_COPY_V1'
REPO = Path(__file__).resolve().parents[1]
EXPECTED = {'mods': 34, 'plugins': 13}


class InventoryError(ValueError):
    pass


def outside_repo(path):
    return path != REPO and REPO not in path.parents


def read_copy(root):
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir() or not outside_repo(root.resolve()):
        raise InventoryError('private inactive copy outside the repository required')
    marker = root/'.funcity-isolated-copy'
    if marker.is_symlink() or not marker.is_file() or marker.read_text(encoding='utf-8').strip() != MARKER:
        raise InventoryError('inactive-copy marker missing or invalid')
    items = []
    for folder, expected in EXPECTED.items():
        directory = root/folder
        if directory.is_symlink() or not directory.is_dir():
            raise InventoryError('inventory directory missing or symlinked')
        files = sorted(directory.iterdir(), key=lambda p: p.name)
        if len(files) != expected or any(p.is_symlink() or not p.is_file() or p.suffix.lower() != '.jar'
                                         for p in files):
            raise InventoryError('exact 34 mod JARs and 13 plugin JARs required; no symlinks')
        for path in files:
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
            items.append({
                'file': f'{folder}/{path.name}', 'sha256': digest.hexdigest(),
                'behavior': 'UNVERIFIED', 'source_and_license': 'UNVERIFIED',
                'client_protocol_and_registry': 'UNVERIFIED',
                'world_save_and_nbt': 'UNVERIFIED', 'dependencies': 'UNVERIFIED',
                'rust_equivalent_tested': False,
            })
    return {'schema': 1, 'privacy': 'PRIVATE_OFFLINE_DO_NOT_COMMIT',
            'engine_compatibility': 'NOT_VERIFIED', 'player_capacity': 'NOT_MEASURED',
            'items': items}


def save_private(report, output):
    output = Path(output).absolute()
    if not outside_repo(output.resolve()) or output.exists():
        raise InventoryError('new private output path outside repository required')
    if not output.parent.is_dir():
        raise InventoryError('private output parent missing')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(output, flags, 0o600), 'w', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def main(argv):
    if len(argv) != 3:
        print('usage: fc_rust_migration_inventory.py PRIVATE_INACTIVE_COPY NEW_PRIVATE_REPORT_JSON', file=sys.stderr)
        return 2
    try:
        report = read_copy(argv[1])
        save_private(report, argv[2])
    except (InventoryError, OSError, UnicodeError) as exc:
        print('LOCAL_AUDIT_REFUSED: ' + type(exc).__name__ + ' (details remain local)', file=sys.stderr)
        return 2
    print('PRIVATE_INVENTORY_WRITTEN: 34 mods / 13 plugins; all conversion statuses UNVERIFIED; no capacity result')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
