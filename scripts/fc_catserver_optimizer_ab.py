#!/usr/bin/env python3
"""Same-VM official CatServer 1.16.5: RoadRunner vs Performant server-only."""
import json
import os
from pathlib import Path
import shutil
import sys

from fc_engine_family_lab import BOOT_JAR, ENGINES, source_engine
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import guard, make_arm, run_one

PERFORMANT_SHA = '7451c817430b509eb88dcd23933973110ed659a06f3cfdb1933ceb33bdfab656'
ORDER = 'RPPR'


def main(root):
    root = Path(root).resolve()
    stage = root/'stage'
    perf = root/'performant-1.16.2-5-4.1m.jar'
    official = root/'official.jar'
    if official.is_symlink() or not official.is_file() or sha(official) != ENGINES['catserver-official'][3]:
        raise ValueError('official CatServer binary unavailable/mismatch')
    if perf.is_symlink() or not perf.is_file() or sha(perf) != PERFORMANT_SHA:
        raise ValueError('official Performant file SHA mismatch')
    report = guard(root, stage, str(perf))  # before changing the SHA-pinned template engine
    replacement = source_engine('catserver-official', official)
    (stage/BOOT_JAR).write_bytes(replacement)
    if sha(stage/BOOT_JAR) != ENGINES['catserver-official'][3]:
        raise ValueError('engine swap mismatch')
    seed = make_arm(stage, root/'seed', None, 'R', perf)
    run_one(seed, report, generate=True)
    if not (seed/'lab-world'/'level.dat').is_file():
        raise ValueError('generated world missing')
    shutil.copytree(seed/'lab-world', root/'world-base', symlinks=False)
    samples = {'R': [], 'P': []}
    for index, arm in enumerate(ORDER, 1):
        trial = make_arm(stage, root/f'trial-{index}', root/'world-base', arm, perf)
        if sha(trial/BOOT_JAR) != ENGINES['catserver-official'][3]:
            raise ValueError('engine mismatch between optimization trials')
        samples[arm].append(run_one(trial, report))
        print(f'::notice title=CatServer official optimizer trial {index}::arm={arm} '
              'mods=18 plugins=6 mobs=80 stop=clean VALUES_WITHHELD', flush=True)
    if any(len(samples[arm]) != 2 for arm in samples):
        raise ValueError('require two valid runs per optimizer')
    compact = {arm: {metric: [x[metric] for x in samples[arm]] for metric in
                     ('rss_mib', 'cpu_s', 'mean_mspt_from_forge_tps')} for arm in samples}
    print('::notice title=CatServer official R vs P A/B::' + json.dumps({
        'order': ORDER, 'engine_sha': ENGINES['catserver-official'][3], 'measurements': compact,
        'limits': 'generated world, 80 mobs, no players/real RP NPCs; no live MSPT/FPS/compatibility claim',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('expect hosted runner root')
        main(sys.argv[1])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        print('::error title=CatServer optimizer A/B invalid::' + str(exc), file=sys.stderr)
        sys.exit(2)
