#!/usr/bin/env python3
"""Author's archived 1.16.5 Forge RC2 Starlight; closed 28/6 hybrid canary.

Not a benchmark of lighting, player capacity or real FunCity saved world. No
live PC, client, player, public binding, JAR redistribution or raw log upload.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_full_rp_engine_boot import main as full_boot, required_graph
from fc_mod_binary_evidence import inspect_jar
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

FILE = 'starlight-forge-1.0.0-RC2-1.16.5.jar'
RELEASE = '1.0.0-RC2'
ASSET_ID = 35665567
# SHA from official hosted release retrieval 39768089449 (GH asset API lacked digest).
SHA256 = '02c7b7bba187d8a066ce0bbb1f60c1d17961cb4cc2a61a9d0138232a9e1eebf0'
PHASE = 'PREFLIGHT'


def verify(root, expected_sha=SHA256):
    path = root/FILE
    if (path.is_symlink() or not path.is_file() or path.resolve() != root/FILE
            or path.stat().st_size != 97563):
        raise ValueError('not official Starlight release asset size/path')
    data = inspect_jar(path.read_bytes())
    if (data['metadata'] != 'mods.toml' or data['mod_ids'] != ['starlight'] or
            any(dep not in ('minecraft', 'forge') for deps in
                data['required_dependencies'].values() for dep in deps)):
        raise ValueError('unexpected Forge metadata/mod id/dependency')
    digest = sha(path)
    if digest != expected_sha:
        raise ValueError('official release bytes changed')
    return path, digest


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('hosted new runner root only')
    path, digest = verify(root)
    print('::notice title=Starlight original 1.16.5 Forge RC2::release=' + RELEASE +
          ' asset_id=' + str(ASSET_ID) + ' sha256=' + digest +
          ' SHA_PINNED=true no_rollout=true', flush=True)
    PHASE = 'BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    original = {p.name: sha(p) for p in (template/'mods').iterdir()}
    if len(original) != 28 or len(report['plugins']) != 6:
        raise ValueError('28/6 inventory drift')
    PHASE = 'CANDIDATE'
    stage = root/'starlight-canary'
    clone_clean_baseline(template, stage)
    if (stage/'mods'/FILE).exists():
        raise ValueError('candidate already in baseline')
    shutil.copyfile(path, stage/'mods'/FILE)
    if (set(p.name for p in (stage/'mods').iterdir()) != set(original) | {FILE} or
            any(sha(stage/'mods'/n) != h for n, h in original.items()) or
            sha(stage/'mods'/FILE) != digest or
            len(report['plugins']) != 6 or
            any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('more than one JAR changed or plugin drift')
    graph = required_graph({p.name: p.read_bytes() for p in (stage/'mods').iterdir()})
    if graph[FILE] != ['starlight']:
        raise ValueError('metadata graph changed')
    run_one(stage, report, generate=True)
    print('::notice title=Starlight Forge 1.16.5 closed hybrid canary::baseline=28/6 '
          'candidate=29/6 boot=PASS clean_stop=true no_players=true '
          'lighting_workload=UNTESTED saved_world=UNTESTED no_rollout=true', flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six hosted inputs required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=Original Starlight canary rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) + ' no raw logs/JAR/world uploaded',
              file=sys.stderr)
        sys.exit(2)
