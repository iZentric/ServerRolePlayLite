#!/usr/bin/env python3
"""Keep four user-requested Prism profiles visible; archive others reversibly.

Never delete an instance, world or screenshot. Backup is a SAME-VOLUME rename
outside `instances` under PrismLauncher/Arena-Archived-Instances/<run-id>.
Minecraft and Prism Launcher MUST be closed; workflow checks before calling.
"""
import argparse
from pathlib import Path
import os
import re
import sys

from fc_pc_lowspec_cleanup import is_link

LITE = 'FunCity-Lite-LowSpec-LAB-1.16.5'
FAB = 'Fabulously Optimized'


def keep_names(names):
    if len(names) != 8 or len(set(names)) != 8:
        raise ValueError('Prism inventory changed since read-only inspection; no move')
    matches = (
        [n for n in names if n == LITE],
        [n for n in names if re.search('egk', n, re.I)],
        [n for n in names if re.search(r'v[ _-]?rp', n, re.I)],
        [n for n in names if n.casefold() == FAB.casefold()],
    )
    if any(len(group) != 1 for group in matches):
        raise ValueError('cannot uniquely identify Lite, EGK, V RP and Fabulously Optimized')
    result = {group[0] for group in matches}
    if len(result) != 4:
        raise ValueError('keep-list overlap')
    return result


def archive_profiles(instances, run_id, apply=False):
    instances = Path(instances)
    if (not instances.is_dir() or is_link(instances) or is_link(instances.parent) or
            not re.fullmatch(r'[0-9]{8,20}', str(run_id))):
        raise ValueError('unexpected instances root or run id')
    profiles = [p for p in instances.iterdir() if p.is_dir()]
    if len(profiles) != 8 or any(is_link(p) for p in profiles):
        raise ValueError('Prism inventory/reparse drift; no move')
    names = [p.name for p in profiles]
    keep = keep_names(names)
    archived = [p for p in profiles if p.name not in keep]
    if len(archived) != 4:
        raise ValueError('expected exactly four other profiles, no move')
    # Never move a profile through a junction/symlink to some other user's data.
    for profile in archived:
        count = 0
        for base, dirs, files in os.walk(profile, followlinks=False):
            for entry in dirs + files:
                count += 1
                if count > 30000 or is_link(Path(base)/entry):
                    raise ValueError('unexpected link or oversized profile; no move')
    archive_parent = instances.parent/'Arena-Archived-Instances'
    dest = archive_parent/str(run_id)
    if dest.exists() or (archive_parent.exists() and is_link(archive_parent)):
        raise ValueError('backup destination exists or is linked; no move')
    if not apply:
        return {'status':'eligible', 'keep':len(keep), 'to_archive':len(archived),
                'archive_relative':'Arena-Archived-Instances/'+str(run_id)}
    archive_parent.mkdir(exist_ok=True)
    dest.mkdir(exist_ok=False)
    readme = dest/'RESTORE.txt'
    readme.write_text('These four profiles were moved from PrismLauncher/instances, not deleted. '
                      'To restore, close Prism and move a folder from this directory back to '
                      'PrismLauncher/instances only if that name does not already exist.\n', encoding='utf-8')
    moved = 0
    for profile in archived:
        profile.rename(dest/profile.name)  # same parent drive: no copy/delete of worlds
        moved += 1
    if {p.name for p in instances.iterdir() if p.is_dir()} != keep:
        raise ValueError('post-move Prism inventory changed; backups still present')
    return {'status':'archived', 'keep':len(keep), 'archived':moved,
            'archive_relative':'Arena-Archived-Instances/'+str(run_id)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instances', required=True, type=Path)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = archive_profiles(args.instances, args.run_id, args.apply)
    except (OSError, ValueError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    print('Prism archive:', result['status'], 'active_kept=', result['keep'],
          'archived=', result.get('archived', result.get('to_archive', 0)),
          'backup=', result['archive_relative'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
