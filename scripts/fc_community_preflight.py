#!/usr/bin/env python3
"""Read-only capacity/backup preflight for a disposable or authorized server copy.

Reports only aggregate bytes and allowlisted public settings. Does not back up,
restore, launch Minecraft, contact a host or establish player capacity.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

MIB = 1024 * 1024
RESERVE_BYTES = 512 * MIB  # conservative project policy, NOT measured backup size
DATA = ('world', 'world_nether', 'world_the_end', 'plugins/CoreProtect')
CONFIG_FLAGS = {'max-players', 'online-mode', 'spawn-protection',
                'view-distance', 'network-compression-threshold'}


def tree_size(directory):
    if directory.is_symlink():
        raise ValueError('symlink in data root; source cannot be safely sized')
    if not directory.exists():
        return 0
    if not directory.is_dir():
        raise ValueError('expected data directory')
    total = 0
    for base, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs:
            if (Path(base) / name).is_symlink():
                raise ValueError('symlink in world/plugin data; inspect before staging')
        for name in files:
            file = Path(base) / name
            if file.is_symlink():
                raise ValueError('symlink in world/plugin data; inspect before staging')
            total += file.stat().st_size
    return total


def public_properties(root):
    path = root / 'server.properties'
    if not path.is_file() or path.is_symlink():
        return {}
    values = {}
    for line in path.read_text(errors='replace').splitlines():
        if '=' not in line or line.lstrip().startswith('#'):
            continue
        key, value = map(str.strip, line.split('=', 1))
        if key in CONFIG_FLAGS and (value in ('true', 'false') or
                                    value.lstrip('-').isdigit()):
            values[key] = value
    return values


def report(server_root, backup_root, disk_usage=shutil.disk_usage):
    root, backup = Path(server_root), Path(backup_root)
    if not root.is_dir() or not backup.is_dir() or root.is_symlink() or backup.is_symlink():
        raise ValueError('both roots must be existing, non-symlink directories')
    if (root / 'plugins').is_symlink():
        raise ValueError('symlink in plugin directory; inspect before staging')
    sizes = {key: tree_size(root / key) for key in DATA}
    source = sum(sizes.values())
    free = disk_usage(backup).free
    # A second full copy + headroom, intentionally conservative. If different volumes
    # are used, the backup volume alone must satisfy the condition.
    minimum = 2 * source + RESERVE_BYTES
    props = public_properties(root)
    world_exists = (root / 'world/level.dat').is_file() and not (root / 'world/level.dat').is_symlink()
    gate = ('NO_WORLD_TO_BACK_UP' if not world_exists else
            'BLOCKED' if free < minimum else 'ELIGIBLE_FOR_TEST_ONLY')
    return {
        'scope': 'read-only preflight; NOT a backup, restore, runtime config or player-capacity test',
        'data_bytes_by_group': sizes,
        'data_bytes_total': source,
        'backup_volume_free_bytes': free,
        'project_policy_minimum_free_bytes': minimum,
        'free_space_gate': gate,
        'same_device_as_server': root.stat().st_dev == backup.stat().st_dev,
        'allowlisted_config_values_not_confirmed_loaded': props,
        'identity_review_required': props.get('online-mode') == 'false',
        'capacity_player_count': None,
        'restore_tested': False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--server-root', type=Path, required=True)
    p.add_argument('--backup-root', type=Path, required=True)
    args = p.parse_args()
    try:
        result = report(args.server_root, args.backup_root)
    except (OSError, ValueError) as exc:
        print('BLOCAT:', exc, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['free_space_gate'] == 'ELIGIBLE_FOR_TEST_ONLY' else 2


if __name__ == '__main__':
    sys.exit(main())
