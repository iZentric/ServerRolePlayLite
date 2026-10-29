#!/usr/bin/env python3
"""Read-only comparison of ONLY two named Prism profiles' mods directories.

Never walks saves, logs, accounts, config, other instances or archives. No copies,
server access or raw paths in output. CI notices contain allowlisted JAR names only.
"""
import argparse
import hashlib
from pathlib import Path
import re
import sys


def is_link(path):
    if path.is_symlink():
        return True
    try:
        return bool(path.lstat().st_file_attributes & 0x400)  # Windows reparse point
    except AttributeError:
        return False


def inventory(profile):
    profile = Path(profile)
    if not profile.is_dir() or is_link(profile):
        raise ValueError('profile missing or linked')
    choices = [profile/folder/'mods' for folder in ('.minecraft', 'minecraft')
               if (profile/folder).exists()]
    if len(choices) != 1:
        raise ValueError('ambiguous or missing Minecraft directory')
    mods = choices[0]
    if (is_link(mods.parent) or not mods.is_dir() or is_link(mods)):
        raise ValueError('mods missing or linked')
    jars = [p for p in mods.iterdir() if p.suffix.lower() == '.jar']
    if len(jars) > 128:
        raise ValueError('unexpected JAR count')
    out = {}
    for jar in jars:
        if (not re.fullmatch(r'[A-Za-z0-9 _().+\-]{1,160}\.jar', jar.name, re.I)
                or not jar.is_file() or is_link(jar) or jar.stat().st_size > 300_000_000):
            raise ValueError('unsafe JAR entry; no inventory published')
        if jar.name.casefold() in (name.casefold() for name in out):
            raise ValueError('ambiguous JAR name')
        digest = hashlib.sha256()
        with jar.open('rb') as stream:
            for block in iter(lambda: stream.read(1 << 20), b''):
                digest.update(block)
        out[jar.name] = digest.hexdigest()
    return out


def compare(original, lowspec):
    a, b = inventory(original), inventory(lowspec)
    common = set(a) & set(b)
    return {'original_count': len(a), 'lowspec_count': len(b),
            'same_bytes': sum(a[name] == b[name] for name in common),
            'changed_sha': sorted(name for name in common if a[name] != b[name]),
            'original_only': sorted(set(a) - set(b)),
            'lowspec_only': sorted(set(b) - set(a))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original', required=True, type=Path)
    p.add_argument('--lowspec', required=True, type=Path)
    args = p.parse_args()
    # When the self-hosted runner cannot see the owner's profile, it must not
    # search elsewhere or pretend the previous FunCity/CUANTIC pack is original.
    if not args.original.is_dir():
        print('::warning title=Freeroam original::PROFILE_NOT_VISIBLE no_other_path_searched=true')
        return 0
    if not args.lowspec.is_dir():
        print('::warning title=Prism LowSpec::PROFILE_NOT_VISIBLE no_other_path_searched=true')
        return 0
    try:
        result = compare(args.original, args.lowspec)
    except (OSError, ValueError):
        # Never print exceptions: Windows may include a full private path.
        print('::error title=Prism read-only inventory::UNSAFE_OR_UNREADABLE; no comparison', file=sys.stderr)
        return 2
    print('::notice title=Freeroam versus LowSpec::original=' + str(result['original_count']) +
          ' lowspec=' + str(result['lowspec_count']) + ' same_sha=' + str(result['same_bytes']) +
          ' changed_sha=' + str(len(result['changed_sha'])) +
          ' original_only=' + str(len(result['original_only'])) +
          ' lowspec_only=' + str(len(result['lowspec_only'])) +
          ' READ_ONLY=true NO_WORLD_OR_ACCOUNTS=true')
    for kind in ('original_only', 'changed_sha', 'lowspec_only'):
        for name in result[kind]:
            # The name was validated against the strict allowlist in inventory().
            print('::notice title=Freeroam comparison ' + kind + '::' + name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
