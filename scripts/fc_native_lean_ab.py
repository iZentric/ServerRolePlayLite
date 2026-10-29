#!/usr/bin/env python3
"""Closed comparison of full 28 versus a SPECIFIED lean 22 on official CatServer.

Same generated world, 80 vanilla zombies, six historical plugins. Zero clients,
zero drivers, no production changes. Results alone do NOT justify rollout.
"""
import json
import os
from pathlib import Path
import sys
import zipfile

from fc_chunk_sending_canary import safe_failure_category
from fc_full_rp_engine_boot import main as full_boot
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import validate_arm
from fc_chunk_sending_canary import clone_clean_baseline
from fc_server_optimizer_ab import run_one
import shutil

ORDER = 'FLLF'  # two each, balanced against time drift
PHASE = 'PREFLIGHT'


def read_decision(path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    original = json.loads(Path('agent/FUNCITY-SERVER-TARGET-28.json').read_text(encoding='utf-8'))
    expected_removed = {
        'AI-Improvements-1.16.5-0.5.0.jar',
        'FastSuite-1.16.4-1.1.1.jar',
        'FastWorkbench-1.16.5-4.6.2.jar',
        'Placebo-1.16.5-4.7.1.jar',
        'getittogetherdrops-1.16.5-v1.2.jar',
        'lazydfu-0.1.3.jar',
    }
    selected = set(d['keep'])
    if (d['status'] != 'ISOLATED_PROPOSED_LEAN_22_NOT_LIVE_OR_CLIENT_VALIDATED' or
            len(original['mods']) != 28 or len(set(original['mods'])) != 28 or
            len(d['keep']) != 22 or len(selected) != 22 or
            set(d['exclude_on_disposable_lab_copy_only']) != expected_removed or
            len(d['exclude_on_disposable_lab_copy_only']) != 6 or
            selected != set(original['mods']) - expected_removed or
            not {'vehicle-mod-0.45.2-1.16.5 (1).jar',
                 'voicechat-forge-1.16.5-2.3.23.jar',
                 'RoadRunner-mc1.16.5-1.5.2.jar',
                 'modernfix-forge-5.18.0+mc1.16.5.jar',
                 'ferritecore-2.1.1-forge.jar',
                 'Ksyxis-1.4.6.jar'} <= selected):
        raise ValueError('lean selection drifts from chosen 28/RP/dependencies')
    return selected, expected_removed


def prepare(template, destination, world, baseline, report, selected):
    if destination.exists() or not selected <= set(baseline):
        raise ValueError('reused or inconsistent stage')
    removed = set(baseline) - selected
    clone_clean_baseline(template, destination)  # no baseline FIFO/log/world/eula
    for name in removed:
        (destination/'mods'/name).unlink()
    validate_arm(destination, baseline, removed, report)  # SHA/deps/6 plugins/loopback
    shutil.copytree(world, destination/'lab-world', symlinks=False)
    if not (destination/'lab-world'/'level.dat').is_file():
        raise ValueError('frozen world missing')
    return destination


def summarize(results):
    if set(results) != {'F', 'L'} or any(len(v) != 2 for v in results.values()):
        raise ValueError('need both repetitions per arm')
    metrics = ('boot_s_wall', 'cpu_s', 'rss_mib', 'mean_mspt_from_forge_tps')
    if any(x.get('summons_confirmed') != 80 or any(x.get(m) is None for m in metrics)
           for values in results.values() for x in values):
        raise ValueError('workload or Forge tick metric unconfirmed')
    return {arm: {metric: [x[metric] for x in values] for metric in metrics}
            for arm, values in results.items()}


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or root != Path(temp).resolve()/'fc-full-rp-catserver-official':
        raise ValueError('not an isolated hosted runner')
    selected, removed = read_decision('agent/FUNCITY-SERVER-LEAN-22.json')
    PHASE = 'PINNED_BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    if set(baseline) != selected | removed or len(baseline) != 28 or not (
            template/'lab-world'/'level.dat').is_file():
        raise ValueError('baseline target/world/inventory drift')
    world = template/'lab-world'
    results = {'F': [], 'L': []}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'TRIAL_' + str(index)
        stage = prepare(template, root/('lean-trial-' + str(index)), world, baseline,
                        report, set(baseline) if arm == 'F' else selected)
        result = run_one(stage, report)
        results[arm].append(result)
        print('::notice title=Lean RP closed trial::index=' + str(index) +
              ' arm=' + arm + ' mods=' + ('28' if arm == 'F' else '22') +
              ' six_plugins=true eighty_zombies=true clean_stop=true '
              'DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    compact = summarize(results)
    print('::notice title=Native-first 28 vs 22 isolated result::' + json.dumps({
        'order': ORDER, 'removed_in_lean_copy': sorted(removed), 'measurements': compact,
        'limits': 'generated world; 80 zombies; no client login, mafias, crafting, '
                  'driving, RP voice, actual world or 13-plugin stack; two repeats; '
                  'Forge mean is not p95/p99; do not deploy on these numbers',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six pinned-hosted inputs required')
        main(*sys.argv[1:])
    except (OSError, ValueError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=Native-first lean test rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' no raw logs/private paths published; no deployment', file=sys.stderr)
        sys.exit(2)
