#!/usr/bin/env python3
"""Read-only metadata audit of an exact historical server ZIP; never installs plugins.

Only JAR names and plugin.yml metadata are reported. Does not parse plugin configs,
player records, world files or claim runtime equivalence of plugins.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import zipfile

EXPECTED = frozenset({
    'Chunky-1.2.217.jar', 'Cuantic-Brand-1.7.7.jar', 'EssentialsX-2.19.7.jar',
    'EssentialsXAntiBuild-2.19.7.jar', 'EssentialsXChat-2.19.7.jar',
    'EssentialsXProtect-2.19.7.jar', 'EssentialsXSpawn-2.19.7.jar',
    'LuckPerms-Bukkit-5.5.71.jar', 'ProtocolLib.jar', 'SkinsRestorer.jar',
    'Vault.jar', 'claimchunk-0.0.22.jar', 'worldedit-bukkit-7.2.5-dist.jar',
    'worldguard-bukkit-7.0.5-dist.jar',
})
NAME = re.compile(r'^[a-zA-Z0-9_.-]{1,80}$')
JAR_MAX = 25_000_000
META_MAX = 256_000


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def field(text, key):
    """Conservative plugin.yml top-level field reader: unknown syntax is not guessed."""
    matches = re.findall(r'^' + re.escape(key) + r':[ \t]*(.*?)[ \t]*$', text, re.M)
    if len(matches) != 1:
        return None
    return matches[0].split(' #', 1)[0].strip().strip('"\'')


def deps(text, key):
    value = field(text, key)
    if value is None:
        return None if re.search('^' + re.escape(key) + r':', text, re.M) else []
    if value.startswith('[') and value.endswith(']'):
        items = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
    elif not value:
        match = re.search(r'^' + re.escape(key) + r':[ \t]*\n((?:[ \t]+.*\n?)*)', text, re.M)
        items = re.findall(r'^  - ([^\s#]+)', match.group(1), re.M) if match else []
        if match and re.search(r'^\s+\S', match.group(1), re.M) and not items:
            return None
    else:
        return None
    return sorted(set(items), key=str.casefold) if all(NAME.fullmatch(x) for x in items) else None


def declared_commands(text):
    match = re.search(r'^commands:[ \t]*\n((?:[ \t]+.*\n?)*)', text, re.M)
    if not match:
        return []
    names = re.findall(r'^  ([a-zA-Z0-9_.-]+):', match.group(1), re.M)
    return sorted(set(names), key=str.casefold) if all(NAME.fullmatch(x) for x in names) else []


def scan(archive):
    with zipfile.ZipFile(archive) as z:
        entries = [i for i in z.infolist() if not i.is_dir() and
                   re.fullmatch(r'(?:[^/]+/)*plugins/[^/]+\.jar', i.filename, re.I)]
        if len(entries) != len(EXPECTED) or {i.filename.rsplit('/', 1)[-1] for i in entries} != EXPECTED:
            raise ValueError('historical 14-plugin inventory mismatch or duplicate')
        if any(i.file_size > JAR_MAX for i in entries):
            raise ValueError('plugin exceeds read-only audit size cap')
        result = []
        for i in sorted(entries, key=lambda i: i.filename.lower()):
            with zipfile.ZipFile(io.BytesIO(z.read(i))) as jar:
                metas = [m for m in jar.infolist() if m.filename == 'plugin.yml' and not m.is_dir()]
                if len(metas) != 1 or metas[0].file_size > META_MAX:
                    raise ValueError('plugin.yml missing, duplicated or too large: ' + i.filename.rsplit('/', 1)[-1])
                meta = jar.read(metas[0]).decode('utf-8-sig', 'replace')
            name = field(meta, 'name')
            if not name or not NAME.fullmatch(name):
                raise ValueError('missing/unparseable plugin name in ' + i.filename.rsplit('/', 1)[-1])
            result.append({'jar': i.filename.rsplit('/', 1)[-1], 'declared_name': name,
                           'depend': deps(meta, 'depend'), 'softdepend': deps(meta, 'softdepend'),
                           'commands': declared_commands(meta)})
    names = [x['declared_name'].casefold() for x in result]
    if len(names) != len(set(names)):
        raise ValueError('duplicate plugin.yml names')
    command_owners = {}
    for item in result:
        for command in item['commands']:
            command_owners.setdefault(command.casefold(), []).append(item['declared_name'])
    return {'scope': 'historical archive plugin.yml declarations ONLY; no live/loaded config or gameplay',
            'plugins': result,
            'shared_declared_commands': {k: v for k, v in command_owners.items() if len(v) > 1},
            'coreprotect_in_historical_archive': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('--sha256', required=True)
    a = p.parse_args()
    try:
        if not re.fullmatch('[a-f0-9]{64}', a.sha256) or sha256(a.archive) != a.sha256:
            raise ValueError('archive SHA256 differs from pin')
        print(json.dumps(scan(a.archive), indent=2, ensure_ascii=False))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
