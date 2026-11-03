#!/usr/bin/env python3
"""Fail-closed O/Q/Q/O synthetic screen; not a real-player capacity verdict.

Only the existing public 18-mod/6-plugin/80-mob, zero-client scene is used.
Both CatServer official and Cuantic are built/staged in one disposable job.
"""
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import sys

import fc_engine_mods_ab as base
from fc_custom_engine_mods_ab import candidate_inputs, copy_trial
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

ORDER = 'OQQO'
HISTORICAL_CPU_MEDIAN = 2.515
HISTORICAL_TICK_PAIR = (1.50, 1.52)


def verdict(samples):
    if set(samples) != {'O', 'Q'} or any(len(samples[arm]) != 2 for arm in ('O', 'Q')):
        raise ValueError('two complete trials per engine required')
    for rows in samples.values():
        for row in rows:
            for key in ('cpu_s', 'mean_mspt_from_forge_tps', 'rss_mib'):
                value = row.get(key)
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                    raise ValueError('invalid trial observation')
            if row.get('players') != 0 or row.get('summons_confirmed') != 80:
                raise ValueError('public workload drift')
    cpu = {arm: statistics.median(row['cpu_s'] for row in rows) for arm, rows in samples.items()}
    ticks = {arm: sorted(row['mean_mspt_from_forge_tps'] for row in rows) for arm, rows in samples.items()}
    historical = cpu['Q'] <= HISTORICAL_CPU_MEDIAN and all(
        actual <= ceiling for actual, ceiling in zip(ticks['Q'], HISTORICAL_TICK_PAIR))
    within_job = cpu['Q'] <= cpu['O'] and all(
        actual <= official for actual, official in zip(ticks['Q'], ticks['O']))
    return {'qualified_public_screen': historical and within_job,
            'historical_ceiling_pass': historical,
            'same_job_nonregression_pass': within_job,
            'median_cpu_s_30s': cpu,
            'sorted_mean_tick_ms': ticks}


def main(root, archived, official, private):
    root = Path(root).resolve()
    report = base.check_inputs(root, archived, official)
    jar, folders = candidate_inputs(root, private, 'Cuantic')
    seed = root/'seed'
    shutil.copytree(root/'stage', seed, symlinks=False)
    run_one(seed, report, generate=True)
    if not (seed/'lab-world'/'level.dat').is_file():
        raise ValueError('generated world missing')
    shutil.copytree(seed/'lab-world', root/'world-base', symlinks=False)
    samples = {arm: [] for arm in 'OQ'}
    for index, arm in enumerate(ORDER, 1):
        trial = copy_trial(root/'stage', root/f'cuantic-trial-{index}', root/'world-base',
                           'O' if arm == 'O' else 'X', archived, official, jar,
                           Path(private)/'runtime-seed', folders)
        row = run_one(trial, report)
        if len(report['server_mods']) != 18 or len(report['plugins']) != 6:
            raise ValueError('public content drift')
        samples[arm].append(row)
        print(f'::notice title=Cuantic public arm {index}::arm={arm} '
              'players=0 DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    result = verdict(samples)
    compact = {arm: {'sha256': sha(jar) if arm == 'Q' else base.ENGINES['catserver-official'][3],
                     'cpu_s_30s': [row['cpu_s'] for row in samples[arm]],
                     'mean_tick_ms': [row['mean_mspt_from_forge_tps'] for row in samples[arm]],
                     'rss_mib': [row['rss_mib'] for row in samples[arm]]}
               for arm in 'OQ'}
    print('::notice title=Cuantic vs official, public zero-client screen::' + json.dumps({
        'order': ORDER, 'arms': compact, 'gate': result,
        'limit': '18 public mods/6 plugins/80 mobs/0 clients; NOT private 34/13 or player capacity',
    }, separators=(',', ':')), flush=True)
    if not result['qualified_public_screen']:
        raise ValueError('Cuantic failed requested synthetic CPU/tick ceiling or within-job comparison')
    return result


if __name__ == '__main__':
    try:
        if len(sys.argv) != 5:
            raise ValueError('runner-root, old plugins archive, official jar, private build required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        print('::error title=Cuantic synthetic candidate rejected::' +
              type(exc).__name__ + '; no capacity claim', file=sys.stderr)
        sys.exit(2)
