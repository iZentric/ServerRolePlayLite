#!/usr/bin/env python3
"""Closed public 18/6 FunCity X+Starlight+Chunk Sending boot, zero clients.

No private world, owner PC, live server, JAR or raw-log upload. This verifies
only that SHA-pinned additive JARs can boot together on the synthetic pack.
"""
import json
import os
from pathlib import Path
import shutil
import sys

from fc_custom_engine_mods_ab import candidate_inputs, copy_trial
from fc_funcity_private_trial import ADDONS, TrialRejected, verified_addons
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one


def overlay(stage, output, paths, seed):
    if len(paths) != 2 or {Path(p).name for p in paths} != set(ADDONS):
        raise TrialRejected('exactly two distinct pinned optimizer JARs required')
    checked = verified_addons(paths, stage, output, seed)
    original = {p.name: sha(p) for p in (stage/'mods').glob('*.jar')}
    if (len(original) != 18 or
            {p.name for p in (output/'mods').iterdir()} != set(original) or
            any(sha(output/'mods'/name) != digest for name, digest in original.items())):
        raise TrialRejected('public baseline mod inventory changed')
    for addon in checked:
        shutil.copyfile(addon, output/'mods'/addon.name)
        if sha(output/'mods'/addon.name) != ADDONS[addon.name][0]:
            raise TrialRejected('optimizer changed during copy')
    if {p.name for p in (output/'mods').iterdir()} != set(original) | set(ADDONS):
        raise TrialRejected('optimizer overlay changed more than two mods')


def main(root, private):
    root = Path(root).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or root != Path(temp).resolve()/'fc-server-optimizer-ab':
        raise TrialRejected('disposable hosted runner only')
    stage = root/'stage'
    report = json.loads((stage/'stage-report.json').read_text())
    if len(report['server_mods']) != 18 or len(report['plugins']) != 6:
        raise TrialRejected('public 18/6 pack drift')
    candidate, folders = candidate_inputs(root, private)
    paths = [root/name for name in ADDONS]
    if any(p.is_symlink() or not p.is_file() for p in paths):
        raise TrialRejected('original release assets missing')
    world = root/'world-base'
    if not (world/'level.dat').is_file():
        raise TrialRejected('generated frozen world missing')
    target = root/'trial-addons'
    if target.exists() or target.is_symlink():
        raise TrialRejected('trial destination must be NEW')
    # Verify both assets before the private X runtime or world is copied.
    verified_addons(paths, stage, target, Path(private)/'runtime-seed')
    trial = copy_trial(stage, target, world, 'X', root/'old-plugins.zip',
                       root/'official.jar', candidate, Path(private)/'runtime-seed', folders)
    overlay(stage, trial, paths, Path(private)/'runtime-seed')
    if any(sha(trial/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']):
        raise TrialRejected('public plugin inventory changed')
    run_one(trial, report, generate=True)
    print('::notice title=FunCity additive hybrid canary::source_patched_X=true '
          'baseline_mods=18 experimental_mods=2 plugins=6 boot=PASS '
          'players=0 clients=0 capacity=UNMEASURED loaded_mods=NOT_VERIFIED '
          'world=GENERATED no_artifact_uploaded=true', flush=True)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise TrialRejected('expected hosted runner root and private source-build workdir')
        main(*sys.argv[1:])
    except (TrialRejected, ValueError, OSError, KeyError) as exc:
        print('::error title=FunCity additive canary rejected::' + type(exc).__name__ +
              ' no private paths, logs, JARs or world published', file=sys.stderr)
        sys.exit(2)
