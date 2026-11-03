#!/usr/bin/env python3
"""Same-VM Java 11 engine A/B/C under identical 18-mod server optimizer stack.

Closed GitHub runner; no live/PC access. CPU/RSS/tick of 80 synthetic mobs
cannot certify RP, client login, motor scalability, or world compatibility.
"""
import json
from pathlib import Path
import shutil
import sys

from fc_engine_family_lab import BOOT_JAR, ENGINES, source_engine
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import guard, run_one

ARMS = {'F': 'funcity', 'C': 'catserver-old', 'O': 'catserver-official'}
ORDER = 'FCOOCF'


def check_inputs(root, archived, official):
    root = Path(root).resolve()
    stage = root/'stage'
    report = guard(root, stage, '-')
    if (Path(archived).resolve() != root/'old-plugins.zip' or
            Path(official).resolve() != root/'official.jar'):
        raise ValueError('engine sources must be under the exact runner-temp root')
    if sha(archived) != ENGINES['catserver-old'][1] or sha(official) != ENGINES['catserver-official'][3]:
        raise ValueError('engine archive/official SHA pin mismatch')
    if source_engine('catserver-old', archived) is None or source_engine('catserver-official', official) is None:
        raise ValueError('missing alternate engine')
    return report


def copy_arm(stage, output, frozen_world, arm, archived, official):
    if arm not in ARMS:
        raise ValueError('unknown motor')
    shutil.copytree(stage, output, symlinks=False)
    shutil.copytree(frozen_world, output/'lab-world', symlinks=False)
    if sha(output/BOOT_JAR) != ENGINES['funcity'][3]:
        raise ValueError('template engine drift')
    if arm != 'F':
        data = source_engine(ARMS[arm], archived if arm == 'C' else official)
        (output/BOOT_JAR).write_bytes(data)
    if sha(output/BOOT_JAR) != ENGINES[ARMS[arm]][3]:
        raise ValueError('engine SHA mismatch after swap')
    return output


def main(root, archived, official):
    root = Path(root).resolve()
    report = check_inputs(root, archived, official)
    seed = root/'seed'
    shutil.copytree(root/'stage', seed, symlinks=False)
    run_one(seed, report, generate=True)
    if not (seed/'lab-world'/'level.dat').is_file():
        raise ValueError('frozen generated world missing')
    shutil.copytree(seed/'lab-world', root/'world-base', symlinks=False)
    samples = {arm: [] for arm in ARMS}
    for index, arm in enumerate(ORDER, 1):
        stage = copy_arm(root/'stage', root/f'trial-{index}', root/'world-base',
                         arm, archived, official)
        result = run_one(stage, report)
        samples[arm].append(result)
        print(f'::notice title=Engine 18-mod trial {index}::motor={ARMS[arm]} '
              'mods=18 plugins=6 mobs=80 stop=clean DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    if any(len(samples[arm]) != 2 for arm in ARMS):
        raise ValueError('at least two successful trials per engine needed')
    compact = {ARMS[arm]: {
        'sha256': ENGINES[ARMS[arm]][3],
        'cpu_s_30s': [x['cpu_s'] for x in samples[arm]],
        'rss_mib': [x['rss_mib'] for x in samples[arm]],
        'mean_tick_ms': [x['mean_mspt_from_forge_tps'] for x in samples[arm]],
    } for arm in ARMS}
    print('::notice title=Same Java same runner 18-mod engine A/B/C::' + json.dumps({
        'order': ORDER, 'measurements': compact,
        'limits': 'generated world; no clients, players or RP NPC/vehicles; no production winner',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 4:
            raise ValueError('expected runner-root, old pack zip, exact official CatServer jar')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        print('::error title=Engine 18-mod AB invalid::' + str(exc), file=sys.stderr)
        sys.exit(2)
