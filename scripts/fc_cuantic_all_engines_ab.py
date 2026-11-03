#!/usr/bin/env python3
"""Five pinned engines, one hosted runner, one public world, zero players.

F archived FunCity, C archived CatServer, O official CatServer, X source FunCity,
Q source Cuantic. Nothing is published until all ten trials succeed; no private
RP data, real clients, host deployment or player-capacity inference.
"""
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import sys

import fc_engine_mods_ab as base
from fc_custom_engine_mods_ab import copy_trial
from fc_funcity_compiled_engine_gate import check_packaged
from fc_funcity_runtime_seed import validate_runtime
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

ORDER = 'FCOXQQXOCF'
NAMES = {'F': 'funcity-archived', 'C': 'catserver-old',
         'O': 'catserver-official', 'X': 'funcity-source', 'Q': 'cuantic-source'}


def validate(rows, mods, plugins):
    if (set(rows) != set(NAMES) or mods != 18 or plugins != 6 or
            any(len(rows[arm]) != 2 for arm in NAMES)):
        raise ValueError('incomplete five-engine identical-content trial')
    for arm in NAMES:
        for row in rows[arm]:
            if row.get('players') != 0 or row.get('summons_confirmed') != 80:
                raise ValueError('synthetic workload drift')
            for key in ('cpu_s', 'rss_mib', 'mean_mspt_from_forge_tps'):
                value = row.get(key)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                    raise ValueError('invalid observation')
    return {NAMES[arm]: {
        'cpu_s_30s': [row['cpu_s'] for row in rows[arm]],
        'median_cpu_s_30s': statistics.median(row['cpu_s'] for row in rows[arm]),
        'mean_tick_ms': [row['mean_mspt_from_forge_tps'] for row in rows[arm]],
        'rss_mib': [row['rss_mib'] for row in rows[arm]],
    } for arm in NAMES}


def notice_rows(results):
    if set(results) != set(NAMES.values()):
        raise ValueError('all five completed engines required before reporting')
    return [f'::notice title={arm}::' + json.dumps(results[name], separators=(',', ':'))
            for arm, name in NAMES.items()]


def source_candidate(root, private, brand, folder):
    raw = Path(private)
    private = raw.resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if (brand, folder) not in (('FunCity', 'fc-catserver-private'),
                              ('Cuantic', 'fc-catserver-cuantic-private')):
        raise ValueError('unapproved source identity')
    if (not temp or root != Path(temp).resolve()/'fc-server-optimizer-ab' or
            raw.is_symlink() or private != Path(temp).resolve()/folder):
        raise ValueError('candidate must remain in disposable hosted temp')
    jar, seed = private/f'{brand}Engine-private-trial.jar', private/'runtime-seed'
    if not jar.is_file() or jar.is_symlink() or seed.is_symlink():
        raise ValueError('missing built candidate/seed')
    check_packaged(jar, brand)
    folders = validate_runtime(seed, sha(jar))
    return jar, seed, folders


def main(root, archived, official, x_private, q_private):
    root = Path(root).resolve()
    report = base.check_inputs(root, archived, official)
    x = source_candidate(root, x_private, 'FunCity', 'fc-catserver-private')
    q = source_candidate(root, q_private, 'Cuantic', 'fc-catserver-cuantic-private')
    seed = root/'seed'
    shutil.copytree(root/'stage', seed, symlinks=False)
    run_one(seed, report, generate=True)
    if not (seed/'lab-world'/'level.dat').is_file():
        raise ValueError('generated frozen world missing')
    shutil.copytree(seed/'lab-world', root/'world-base', symlinks=False)
    rows = {arm: [] for arm in NAMES}
    for index, arm in enumerate(ORDER, 1):
        output = root/f'all-trial-{index}'
        if arm in 'FCO':
            trial = base.copy_arm(root/'stage', output, root/'world-base', arm, archived, official)
        else:
            jar, runtime, folders = x if arm == 'X' else q
            trial = copy_trial(root/'stage', output, root/'world-base',
                               'X', archived, official, jar, runtime, folders)
        rows[arm].append(run_one(trial, report))
    results = validate(rows, len(report['server_mods']), len(report['plugins']))
    for arm, name in NAMES.items():
        results[name]['sha256'] = (sha(x[0]) if arm == 'X' else sha(q[0]) if arm == 'Q'
                                   else base.ENGINES[base.ARMS[arm]][3])
    for line in notice_rows(results):
        print(line, flush=True)
    print(f'::notice title=Five public engines complete::order={ORDER} '
          'mods=18 plugins=6 mobs=80 clients=0 no_capacity_claim=true', flush=True)
    return results


if __name__ == '__main__':
    try:
        if len(sys.argv) != 6:
            raise ValueError('runner root, archive, official, FunCity source dir, Cuantic source dir required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        print('::error title=Five-engine public comparison invalid::' +
              type(exc).__name__ + '; no partial ranking or capacity claim', file=sys.stderr)
        sys.exit(2)
