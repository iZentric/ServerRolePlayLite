#!/usr/bin/env python3
"""Stage a CLOSED, isolated FunCity b1.0827 plugin-only server from pinned inputs.

No world, credentials, players, release or PC changes. This is NOT a public server:
plugin authentication, voice and complete RP gameplay are still unresolved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from fc_plugin_audit import EXPECTED, scan
from fc_plugin_first_gate import POLICY, validate

ENGINE_SHA = 'd6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd'
ARCHIVE_SHA = 'fe1e261097d92f26c6653239a7161613e6be54b8e9f82c79739c101ce8aa8a15'
COREPROTECT_SHA = '04f31b609d1e3e1c53e99aaa06ca10ea6bdf5172c94bf5af8ccf108b0bc4b977'
SELECTED = ('EssentialsX-2.19.7.jar', 'EssentialsXChat-2.19.7.jar',
            'EssentialsXSpawn-2.19.7.jar', 'LuckPerms-Bukkit-5.5.71.jar',
            'Vault.jar')
PROPERTIES = '''# Closed, throwaway laboratory: no plugin account login or public network
motd=FunCity plugin-first LAB - NOT PUBLIC
server-ip=127.0.0.1
server-port=25565
online-mode=true
white-list=true
max-players=8
view-distance=5
spawn-protection=0
network-compression-threshold=256
level-name=lab-world
'''


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as inp:
        for block in iter(lambda: inp.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def stage(engine, archive, coreprotect, output, pins=(ENGINE_SHA, ARCHIVE_SHA, COREPROTECT_SHA)):
    engine, archive, coreprotect, output = map(Path, (engine, archive, coreprotect, output))
    if output.exists() or any(output.resolve() == p.resolve() for p in (engine, archive, coreprotect)):
        raise ValueError('destination must be new, isolated and distinct from sources')
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    validate(policy)
    if policy['client_jar_selection'] or policy['server_jar_selection']:
        raise ValueError('this plugin-only stage does not allow mod JAR approvals yet')
    for path, expected in zip((engine, archive, coreprotect), pins):
        if not path.is_file() or sha(path) != expected:
            raise ValueError(f'SHA256 mismatch: {path.name}; no stage written')
    audit = scan(archive)  # exact 14 historical JAR names, unique plugin.yml identities
    by_file = {row['jar']: row for row in audit['plugins']}
    assert set(SELECTED) <= EXPECTED
    selected_names = {by_file[n]['declared_name'].casefold() for n in SELECTED}
    selected_names.add('coreprotect')
    for filename in SELECTED:
        required = by_file[filename]['depend']
        if required is None or any(n.casefold() not in selected_names for n in required):
            raise ValueError('unmet or unparseable hard plugin dependency: ' + filename)
    with zipfile.ZipFile(coreprotect) as jar:
        metas = [i for i in jar.infolist() if i.filename == 'plugin.yml' and not i.is_dir()]
        if len(metas) != 1 or metas[0].file_size > 256_000:
            raise ValueError('CoreProtect plugin.yml missing or oversized')
        if not any(line.strip().casefold() == 'name: coreprotect'
                   for line in jar.read(metas[0]).decode('utf-8-sig').splitlines()):
            raise ValueError('pinned plugin is not named CoreProtect')
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='.fc-plugins-only-', dir=output.parent))
    try:
        (tmp / 'mods').mkdir()  # deliberate zero; Forge support remains in the engine
        (tmp / 'plugins').mkdir()
        shutil.copyfile(engine, tmp / 'FunCity-1.16.5-b1.0827.jar')
        with zipfile.ZipFile(archive) as source:
            items = {i.filename.rsplit('/', 1)[-1]: i for i in source.infolist()
                     if '/plugins/' in '/' + i.filename and i.filename.endswith('.jar')}
            if len(items) != 14 or set(items) != EXPECTED:
                raise ValueError('historical plugin archive changed')
            for name in SELECTED:
                with source.open(items[name]) as src, (tmp / 'plugins' / name).open('wb') as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
        shutil.copyfile(coreprotect, tmp / 'plugins' / 'CoreProtect.jar')
        (tmp / 'server.properties').write_text(PROPERTIES, encoding='ascii')
        report = {
            'scope': 'closed isolated stage, NOT public or booted',
            'engine': {'name': 'FunCity b1.0827 hybrid', 'sha256': pins[0]},
            'server_mods': [], 'client_mods': [],
            'plugins': [
                {'jar': p.name, 'sha256': sha(p)} for p in sorted((tmp / 'plugins').glob('*.jar'))
            ],
            'auth': 'NOT INSTALLED: closed to public; online-mode true + whitelist true',
            'voice': 'unresolved', 'rp_jobs_mafias_vehicles': 'NOT IMPLEMENTED',
            'boot_login_backup_restore': 'NOT TESTED',
            'no_world_or_player_data_copied': True,
        }
        if len(report['plugins']) != 6 or list((tmp / 'mods').iterdir()):
            raise ValueError('mod/plugin stage inventory drift')
        (tmp / 'stage-report.json').write_text(json.dumps(report, indent=2) + '\n')
        tmp.rename(output)
        return report
    finally:
        if tmp.exists():
            shutil.rmtree(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--coreprotect', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(stage(args.engine, args.archive, args.coreprotect, args.output), indent=2))
    except (ValueError, AssertionError, OSError, zipfile.BadZipFile, KeyError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
