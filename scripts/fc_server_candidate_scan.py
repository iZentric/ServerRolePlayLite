#!/usr/bin/env python3
"""Author-file-only Forge 1.16.5 lab preflight: Saturn and Smooth Chunk Save.

28/6 baseline then each candidate separately on fresh disposable generated world.
NEVER bundle unproven optimizers or touch private PC/live server/world.
Boot/save probe is NOT proof of login, player capacity, or save-time gain.
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

CANDIDATES = {
    'saturn': ('saturn-mc1.16.5-0.0.3.jar', 4017215, 670986),
    'smooth': ('smoothchunk1.16.5-2.0.jar', 4453876, 582327),
}
PHASE = 'PREFLIGHT'


def verify(root, label):
    name, file_id, project_id = CANDIDATES[label]
    path = root/name
    if (path.is_symlink() or not path.is_file() or path.resolve() != root/name or
            not 1000 < path.stat().st_size < 100_000):
        raise ValueError('not the expected small hosted author JAR')
    raw = path.read_bytes()
    data = inspect_jar(raw)
    if data['metadata'] != 'mods.toml' or len(data['mod_ids']) != 1 or not data['mod_ids'][0]:
        raise ValueError('Forge 1.16.5 metadata or single mod ID missing')
    if any(dep not in ('minecraft', 'forge') for deps in
           data['required_dependencies'].values() for dep in deps):
        raise ValueError('candidate needs a new mod dependency')
    # File/project IDs are pinned by the workflow's author endpoint; SHA is
    # reported on first retrieval and MUST be pinned before a measured A/B.
    return path, data['mod_ids'][0], sha(path), file_id, project_id


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('fresh hosted runner root required')
    inspected = {label: verify(root, label) for label in CANDIDATES}
    if len({x[1] for x in inspected.values()}) != len(CANDIDATES):
        raise ValueError('candidate mod IDs duplicate one another')
    for label, (_, modid, digest, file_id, _) in inspected.items():
        print('::notice title=Official Forge 1.16.5 candidate metadata::candidate=' + label +
              ' file_id=' + str(file_id) + ' mod_id=' + modid + ' sha256=' + digest +
              ' SHA_NOT_YET_PINNED no_promotion=true', flush=True)
    PHASE = 'BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    stage = root/'stage'
    report = json.loads((stage/'stage-report.json').read_text())
    original = {p.name: sha(p) for p in (stage/'mods').iterdir()}
    if len(original) != 28 or len(report['plugins']) != 6:
        raise ValueError('28/6 baseline drift')
    for label, (source, modid, digest, file_id, _) in inspected.items():
        PHASE = 'CANDIDATE_' + label.upper()
        trial = root/('isolated-' + label)
        clone_clean_baseline(stage, trial)
        dest = trial/'mods'/source.name
        if dest.exists() or dest.is_symlink():
            raise ValueError('candidate already present in historical baseline')
        shutil.copyfile(source, dest)
        actual = {p.name for p in (trial/'mods').iterdir()}
        if (len(actual) != 29 or actual != set(original) | {source.name} or
                sha(dest) != digest or any(sha(trial/'mods'/n) != h for n, h in original.items())):
            raise ValueError('candidate stage changed more than one JAR')
        graph = required_graph({p.name: p.read_bytes() for p in (trial/'mods').iterdir()})
        if modid not in graph[source.name] or len(report['plugins']) != 6 or any(
                sha(trial/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']):
            raise ValueError('candidate graph/plugins drift')
        run_one(trial, report, generate=True)  # fresh world, no clients
        print('::notice title=28 plus one candidate closed boot::candidate=' + label +
              ' file_id=' + str(file_id) + ' mods=29 plugins=6 boot=PASS clean_stop=true '
              'world=GENERATED clients=0 save_load=UNTESTED performance=UNMEASURED '
              'no_jar_log_or_world_uploaded=true', flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six exact hosted inputs required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=New mod candidate scan rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' no raw logs, artifacts, private data or deployment', file=sys.stderr)
        sys.exit(2)
