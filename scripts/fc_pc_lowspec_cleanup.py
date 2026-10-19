#!/usr/bin/env python3
"""Remove ONLY two obsolete, untouched FunCity lab Prism profiles.

Dry-run by default. Never removes the LowSpec profile, a world, logs, accounts,
old user profiles, or a directory with unexpected files. Close Minecraft first.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

ZERO = 'FunCity-Lite-PluginFirst-LAB-1.16.5'
CONTENT = 'FunCity-Lite-Content-LAB-1.16.5'
FORGE = '36.2.42'
JARS = {
    'Modernxl 1.16.5.jar', 'modernlife-1.16.5-1.15.jar',
    'cfm-7.0.0pre22-1.16.3.jar', 'roadstuff-1.16.5-4.3.0.jar',
    'vehicle-mod-0.45.2-1.16.5 (1).jar', 'cgm-1.2.6-1.16.5.jar',
    'additional-guns-0.7.1-1.16.5.jar', 'mapperbase-1.16.5-2.4.0.0.jar',
    'obfuscate-0.6.3-1.16.5.jar',
}
READMES = {
    ZERO: 'LAB baseline ONLY: Minecraft 1.16.5 + Forge 36.2.42; 0 client mods. No own content mods identified, no login/voice/RP or performance validated. Do not replace an existing profile.',
    CONTENT: 'Private modded compatibility experiment from existing FunCity pack. Ownership/distribution unverified. Not a final RP pack: no authentication, player join, voice or FPS test. Never replace old Prism profiles.',
}
NAMES = {
    ZERO: 'FunCity Lite PluginFirst LAB 1.16.5',
    CONTENT: 'FunCity Lite Content LAB 1.16.5',
}


def is_link(path):
    if path.is_symlink():
        return True
    try:
        return bool(path.lstat().st_file_attributes & 0x400)  # Windows reparse point
    except AttributeError:
        return False


def safe_profile(root, name):
    p = root / name
    if not p.exists():
        return False, 'absent'
    if not p.is_dir() or is_link(root) or is_link(p):
        return False, 'symlink_or_not_directory'
    allowed_root = {'instance.cfg', 'mmc-pack.json', 'LAB-READ-ME.txt', '.minecraft'}
    if {x.name for x in p.iterdir()} != allowed_root:
        return False, 'unexpected_profile_files'
    mc, mods = p / '.minecraft', p / '.minecraft' / 'mods'
    if (not mc.is_dir() or is_link(mc) or {x.name for x in mc.iterdir()} != {'mods'} or
            not mods.is_dir() or is_link(mods)):
        return False, 'user_files_or_world_present'
    expected = set() if name == ZERO else JARS
    files = list(mods.iterdir())
    if {x.name for x in files} != expected or any(not x.is_file() or is_link(x) for x in files):
        return False, 'unexpected_mods'
    try:
        if (p / 'LAB-READ-ME.txt').read_text(encoding='utf-8') != READMES[name]:
            return False, 'lab_marker_changed'
        config = (p / 'instance.cfg').read_text(encoding='utf-8')
        if f'name={NAMES[name]}' not in config.splitlines():
            return False, 'instance_name_changed'
        pack = json.loads((p / 'mmc-pack.json').read_text(encoding='utf-8'))
        components = {c['uid']: c['version'] for c in pack['components']}
        if components != {'net.minecraft': '1.16.5', 'net.minecraftforge': FORGE}:
            return False, 'game_version_changed'
    except (ValueError, KeyError, OSError, UnicodeError):
        return False, 'cannot_verify_lab_files'
    return True, 'generated_lab_only'


def clean(root, apply=False):
    root = Path(root)
    if not root.is_dir() or is_link(root):
        raise ValueError('instances root missing or symlinked')
    results = {}
    for name in (ZERO, CONTENT):
        safe, reason = safe_profile(root, name)
        if safe and apply:
            shutil.rmtree(root / name)
            results[name] = 'removed_generated_lab'
        else:
            results[name] = 'eligible' if safe else 'preserved_' + reason
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--instances', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='only after Minecraft is closed')
    args = parser.parse_args()
    try:
        results = clean(args.instances, args.apply)
    except (ValueError, OSError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    for name, result in results.items():
        print(name + ': ' + result)
    print('LowSpec profile: PRESERVED; no old user profile touched')
    return 0


if __name__ == '__main__':
    sys.exit(main())
