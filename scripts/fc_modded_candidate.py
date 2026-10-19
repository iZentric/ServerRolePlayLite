#!/usr/bin/env python3
"""Unreleased, isolated modded compatibility experiment from a pinned OLD pack.

JARs in this experiment are NOT certified as authored/owned by the user.
No approval to deploy or distribute; no world/credentials/old profiles copied.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

from fc_mod_binary_evidence import inspect_jar
from fc_plugin_first_stage import ARCHIVE_SHA, sha, stage

# Content from the user's historical FunCity pack, not a list of ownership claims.
CONTENT = (
    'Modernxl 1.16.5.jar', 'modernlife-1.16.5-1.15.jar',
    'cfm-7.0.0pre22-1.16.3.jar', 'roadstuff-1.16.5-4.3.0.jar',
    'vehicle-mod-0.45.2-1.16.5 (1).jar', 'cgm-1.2.6-1.16.5.jar',
    'additional-guns-0.7.1-1.16.5.jar',
    'Pizzaland_v68.jar', 'pamhc2foodcore-1.16.3-1.0.2.jar',
    'supplementaries-1.16.5-0.18.4b.jar',
    'emotecraft-for-MC1.16.5-2.2.7-b.build.47-forge.jar',
)
LIBRARIES = (
    'mapperbase-1.16.5-2.4.0.0.jar',  # roads
    'obfuscate-0.6.3-1.16.5.jar',     # guns/vehicles
    'selene-1.16.5-1.9.0.jar',       # Supplementaries
    'player-animation-lib-forge-0.4.0+1.16.5.jar',  # Emotecraft
)
CHOSEN = CONTENT + LIBRARIES


def make(engine, archive, core, guava, output):
    output = Path(output)
    archive = Path(archive)
    if output.exists() or sha(archive) != ARCHIVE_SHA:
        raise ValueError('destination exists or historical ZIP SHA mismatch')
    with zipfile.ZipFile(archive) as source:
        jars = {}
        for entry in source.infolist():
            if '/mods/' in '/' + entry.filename and entry.filename.endswith('.jar'):
                name = entry.filename.rsplit('/', 1)[-1]
                if name in jars or entry.is_dir() or entry.file_size > 300_000_000:
                    raise ValueError('ambiguous/oversized mod source')
                jars[name] = entry
        if len(jars) != 36 or not set(CHOSEN) <= jars.keys():
            raise ValueError('historical mod inventory differs or selected JAR absent')
        if any(entry.filename.startswith('/') or '..' in entry.filename.split('/')
               for entry in jars.values()):
            raise ValueError('unsafe source JAR path')
        # Mandatory relationships only; optional integrations are not forced.
        ids = {}
        records = {}
        for name, entry in jars.items():
            record = inspect_jar(source.read(entry))
            if record['metadata'] == 'mods.toml':
                records[name] = record
                for mod_id in record['mod_ids']:
                    if mod_id in ids and ids[mod_id] != name:
                        raise ValueError('ambiguous mod id: ' + mod_id)
                    ids[mod_id] = name
        chosen = set(CHOSEN)
        for name in CHOSEN:
            if name not in records:
                raise ValueError('missing parsable mods.toml for selected ' + name)
            deps = records[name]['required_dependencies']
            for mod_id in records[name]['mod_ids']:
                for dep in deps.get(mod_id, []):
                    if dep in ('forge', 'minecraft'):
                        continue
                    if dep not in ids or ids[dep] not in chosen:
                        raise ValueError(f'unmet mandatory dependency: {name} needs {dep}')
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.fc-modded-', dir=output.parent) as tmp_dir:
            staged = Path(tmp_dir)/'stage'
            report = stage(engine, archive, core, guava, staged)
            mods = []
            for name in CHOSEN:
                target = staged/'mods'/name
                with source.open(jars[name]) as inp, target.open('xb') as out:
                    shutil.copyfileobj(inp, out, 1 << 20)
                mods.append({'jar': name, 'sha256': sha(target),
                             'mod_ids': records[name]['mod_ids'],
                             'role': 'content' if name in CONTENT else 'hard_dependency'})
            report['scope'] = 'UNRELEASED local modded compatibility experiment; ownership unverified'
            report['server_mods'] = mods
            report['client_mods'] = 'matching set NOT YET installed/tested'
            report['auth'] = 'NOT INSTALLED; loopback only'
            (staged/'stage-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
            staged.rename(output)
            return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('engine', 'archive', 'coreprotect', 'guava21', 'output'):
        p.add_argument('--' + name, required=True, type=Path)
    a = p.parse_args()
    try:
        report = make(a.engine, a.archive, a.coreprotect, a.guava21, a.output)
        print('::notice title=Unreleased modded lab candidate::server_content=' +
              str(len(CONTENT)) + ' dependencies=' + str(len(LIBRARIES)) +
              ' performance_mods=0 ownership=UNVERIFIED; no player or client test')
        print(json.dumps({'server_mod_count': len(report['server_mods']),
                          'plugin_count': len(report['plugins'])}))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
