#!/usr/bin/env python3
"""Ephemeral archived-FunCity / patched-FunCity / official-CatServer A/B/C.

18 historical PUBLIC mods, 6 plugins, generated world, 80 mobs, ZERO clients.
Never interpret these measurements as a player count or full RP compatibility.
No custom JAR, runtime seed, world or raw server log leaves the Actions runner.
"""
import json
import os
from pathlib import Path
import shutil
import statistics
import sys

import fc_engine_mods_ab as base
from fc_funcity_compiled_engine_gate import check_packaged
from fc_funcity_runtime_seed import validate_runtime
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

ORDER = 'FXOOXF'
BOOT_JAR = base.BOOT_JAR


def candidate_inputs(root, private, brand='FunCity'):
    raw_private = Path(private)
    root, private = Path(root).resolve(), raw_private.resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if (not temp or root != Path(temp).resolve()/'fc-server-optimizer-ab'
            or private != Path(temp).resolve()/'fc-catserver-private'
            or raw_private.is_symlink()):
        raise ValueError('only a fresh disposable hosted runner candidate')
    if brand not in ('FunCity', 'Cuantic'):
        raise ValueError('unknown candidate brand')
    jar = private/f'{brand}Engine-private-trial.jar'
    seed = private/'runtime-seed'
    if not jar.is_file() or jar.is_symlink() or seed.is_symlink():
        raise ValueError('private source build or runtime seed missing')
    check_packaged(jar, brand)
    folders = validate_runtime(seed, sha(jar))
    return jar, folders


def copy_trial(stage, output, world, arm, archived, official, candidate, seed, folders):
    stage, output, world = map(Path, (stage, output, world))
    temp = os.environ.get('RUNNER_TEMP')
    if (not temp or stage.resolve() != Path(temp).resolve()/'fc-server-optimizer-ab'/'stage'
            or arm not in 'FXO' or output.parent.resolve() != stage.parent.resolve() or output.exists()):
        raise ValueError('unknown arm or non-new runner trial')
    # The existing exact-SHA gate creates identical public mod/plugin/world copies.
    trial = base.copy_arm(stage, output, world, 'O' if arm == 'O' else 'F', archived, official)
    if arm == 'X':
        shutil.copyfile(candidate, trial/BOOT_JAR)
        if sha(trial/BOOT_JAR) != sha(candidate):
            raise ValueError('candidate JAR copy hash mismatch')
        # CatServer needs its own first-boot libraries; only this throwaway arm changes.
        for folder in folders:
            destination = trial/folder
            if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
                raise ValueError('unsafe trial runtime folder')
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(seed/folder, destination, symlinks=False)
    return trial


def main(root, archived, official, private):
    root = Path(root).resolve()
    report = base.check_inputs(root, archived, official)
    candidate, folders = candidate_inputs(root, private)
    seed = root/'seed'
    shutil.copytree(root/'stage', seed, symlinks=False)
    run_one(seed, report, generate=True)
    if not (seed/'lab-world'/'level.dat').is_file():
        raise ValueError('frozen generated world missing')
    shutil.copytree(seed/'lab-world', root/'world-base', symlinks=False)
    samples = {arm: [] for arm in 'FXO'}
    for index, arm in enumerate(ORDER, 1):
        trial = copy_trial(root/'stage', root/f'trial-{index}', root/'world-base',
                           arm, archived, official, candidate, Path(private)/'runtime-seed', folders)
        result = run_one(trial, report)
        if (result['players'] != 0 or result['summons_confirmed'] != 80
                or len(report['server_mods']) != 18 or len(report['plugins']) != 6):
            raise ValueError('synthetic workload drift; no metrics reported')
        samples[arm].append(result)
        print(f'::notice title=FunCity synthetic engine arm {index}::arm={arm} '
              'mods=18 plugins=6 players=0 DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    if any(len(samples[arm]) != 2 or any(row['mean_mspt_from_forge_tps'] is None for row in samples[arm])
           for arm in 'FXO'):
        raise ValueError('two complete trials per engine required')
    names = {'F': 'archived-funcity', 'X': 'source-patched-funcity-0003', 'O': 'official-catserver'}
    hashes = {'F': base.ENGINES['funcity'][3], 'X': sha(candidate),
              'O': base.ENGINES['catserver-official'][3]}
    compact = {names[arm]: {'sha256': hashes[arm],
                            'cpu_s_30s': [row['cpu_s'] for row in samples[arm]],
                            'rss_mib': [row['rss_mib'] for row in samples[arm]],
                            'mean_tick_ms': [row['mean_mspt_from_forge_tps'] for row in samples[arm]],
                            'median_cpu_s_30s': statistics.median(row['cpu_s'] for row in samples[arm])}
               for arm in 'FXO'}
    print('::notice title=Three engines same public workload::' + json.dumps({
        'order': ORDER, 'measurements': compact,
        'limits': '18 public mods/6 plugins/80 mobs/0 players; not 2vCPU-12GB; no real RP capacity winner',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 5:
            raise ValueError('runner-root, old plugins zip, official jar, private build dir required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        # Never echo private file paths or raw server logs.
        print('::error title=FunCity source-engine synthetic AB invalid::' +
              type(exc).__name__ + '; no capacity claim', file=sys.stderr)
        sys.exit(2)
