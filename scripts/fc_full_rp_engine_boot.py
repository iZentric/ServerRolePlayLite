#!/usr/bin/env python3
"""Closed boot test of 28 client-aligned RP server mods (historical 29 minus Clumps) with 6 plugins.

Never touches PC, live server, worlds, accounts or any client profile. Historical
selection, not proof of live inventory, player login or real RP gameplay.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_engine_family_lab import BOOT_JAR, ENGINES, source_engine
from fc_mod_binary_evidence import inspect_jar
from fc_plugin_first_stage import ENGINE_SHA, GUAVA21_SHA, sha, stage as plugin_stage
from fc_server_lite_candidate import HISTORICAL_SHA256, decisions, stage as select_server
from fc_server_optimizer_ab import run_one


def required_graph(jars):
    """Metadata-only test; Forge optional/dynamic dependencies need boot too."""
    mod_ids = {}
    parsed = {}
    for name, raw in jars.items():
        meta = inspect_jar(raw)
        if meta['metadata'] != 'mods.toml' or not meta['mod_ids']:
            raise ValueError('unparseable metadata: ' + name)
        parsed[name] = meta
        for mod_id in meta['mod_ids']:
            if mod_id in mod_ids:
                raise ValueError('duplicate mod id in selection: ' + mod_id)
            mod_ids[mod_id] = name
    for name, meta in parsed.items():
        for deps in meta['required_dependencies'].values():
            for dependency in deps:
                if dependency not in ('minecraft', 'forge') and dependency not in mod_ids:
                    raise ValueError('missing mandatory mod for ' + name + ': ' + dependency)
    return {k: sorted(v['mod_ids']) for k, v in parsed.items()}


def boot_once_or_installer_then_once(stage, report):
    """Permit only a clean installer bootstrap with an explicit marker, then one boot."""
    try:
        return run_one(stage, report, generate=True)
    except ValueError as exc:
        if 'server did not reach Done;' not in str(exc) or 'exit=0' not in str(exc):
            raise
        log = stage/'private-benchmark.log'
        text = log.read_text(encoding='utf-8', errors='replace')
        if not any(marker in text.lower() for marker in ('successfully installed',
                        'server installed', 'install complete', 'installation finished')):
            raise
        if (stage/'lab-world'/'level.dat').exists():
            raise ValueError('installer left a world; no retry on possibly dirty state')
        log.rename(stage/'private-installer.log')  # no logs outside runner
        return run_one(stage, report, generate=True)


def main(root, engine, source, archive, motor, core, guava):
    root = Path(root).resolve()
    tmp = os.environ.get('RUNNER_TEMP')
    if (not tmp or root != Path(tmp).resolve()/('fc-full-rp-' + engine)
            or engine not in ENGINES or (root/'stage').exists()
            or (root/'selected-mods.zip').exists()):
        raise ValueError('new GitHub-hosted temp stage required')
    if (Path(archive).resolve() != root/'historic.zip' or
            Path(motor).resolve() != root/'motor.jar' or
            Path(core).resolve() != root/'CoreProtect.jar' or
            Path(guava).resolve() != root/'guava-21.0.jar' or
            Path(source).resolve() != root/('engine.jar' if engine == 'catserver-official' else
                                           'alternative.zip' if engine in ('arclight', 'mist') else
                                           'historic.zip' if engine == 'catserver-old' else 'motor.jar')):
        raise ValueError('source outside the expected hosted temp directory')
    if sha(archive) != HISTORICAL_SHA256:
        raise ValueError('historical ZIP SHA mismatch')
    decision_file = Path('agent/DECIZII.md')
    client_source = Path('diag/pc-client.txt')
    voice = Path('agent/voicechat-1.16.5-2.3.23.json')
    names, kept, excluded = decisions(decision_file, decision_file, client_source, voice)
    result = select_server(archive, HISTORICAL_SHA256, root/'selected-mods.zip',
                           decision_file, client_source, voice)
    if len(kept) != 29 or result['server_mod_count'] != 29 or len(excluded) != 7:
        raise ValueError('decision inventory drift')
    report = plugin_stage(motor, archive, core, guava, root/'stage')
    stage = root/'stage'
    jar_hashes = dict(result['kept_sha256'])
    # Owner removed Clumps on BOTH sides after a private backup/login trial.
    # The 29-mod historical manifest still includes it; do not reintroduce it.
    if jar_hashes.pop('Clumps-6.0.0.28.jar', None) is None:
        raise ValueError('historical Clumps entry missing; selection drift')
    client_aligned = kept - {'clumps-6.0.0.28.jar'}
    with zipfile.ZipFile(root/'selected-mods.zip') as z:
        if len(z.infolist()) != 29 or z.testzip() is not None:
            raise ValueError('invalid selected archive')
        jars = {name: z.read('mods/' + name) for name in jar_hashes}
        graph = required_graph(jars)
        if set(n.casefold() for n in jars) != client_aligned or len(jars) != 28:
            raise ValueError('wrong mod selection')
        for name, raw in jars.items():
            path = stage/'mods'/name
            path.write_bytes(raw)
            if sha(path) != jar_hashes[name]:
                raise ValueError('mod SHA mismatch: ' + name)
    replacement = source_engine(engine, source)
    if replacement is not None:
        (stage/BOOT_JAR).write_bytes(replacement)
    if sha(stage/BOOT_JAR) != ENGINES[engine][3] or sha(stage/'runtime/guava-21.0.jar') != GUAVA21_SHA:
        raise ValueError('motor or Guava SHA mismatch')
    if ({p.name for p in (stage/'mods').iterdir()} != set(jars) or
            len(report['plugins']) != 6 or
            any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']) or
            (stage/'lab-world').exists() or (stage/'eula.txt').exists()):
        raise ValueError('stage diff/inventory/world mismatch')
    props = set((stage/'server.properties').read_text().splitlines())
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true'} <= props:
        raise ValueError('not closed to public')
    boot_once_or_installer_then_once(stage, report)
    print(f'::notice title=28 client-aligned RP server mods boot::{engine} boot=PASS '
          'metadata=28 clumps=ABSENT mandatory_deps=PASS plugins=6 stopped_cleanly=true '
          'NO client, login, voice transport, vehicle drive or live world tested', flush=True)
    return graph


if __name__ == '__main__':
    try:
        if len(sys.argv) != 8:
            raise ValueError('expected runner root, engine, exact source, archive, motor, core, guava')
        main(*sys.argv[1:])
    except (OSError, ValueError, AssertionError, KeyError, zipfile.BadZipFile) as exc:
        print('::error title=28-mod engine boot rejected::' + str(exc), file=sys.stderr)
        sys.exit(2)
