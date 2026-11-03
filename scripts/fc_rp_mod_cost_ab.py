#!/usr/bin/env python3
"""Disposable 28/6 CatServer optimizer-ablation lab, not an RP/player benchmark.

Exact, SHA-pinned historical archive and official engine; one process at a time.
A/I/R/K/K/R/I/A on the same generated world, 80 vanilla zombies, no clients.
Never touches the owner's PC, profile, saved city or live server. Raw logs stay
in RUNNER_TEMP; no JAR/world/log is uploaded. Two trials are descriptive only.
"""
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import zipfile

from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_full_rp_engine_boot import main as full_boot, required_graph
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import run_one

AI = 'AI-Improvements-1.16.5-0.5.0.jar'
RECIPES = frozenset({'FastSuite-1.16.4-1.1.1.jar',
                     'FastWorkbench-1.16.5-4.6.2.jar',
                     'Placebo-1.16.5-4.7.1.jar'})
KSYXIS = 'Ksyxis-1.4.6.jar'
ARMS = {'A': frozenset(), 'I': frozenset({AI}),
        'R': RECIPES, 'K': frozenset({KSYXIS})}
ORDER = 'AIRKKRIA'  # balanced palindrome: two sequential copies of each arm
PHASE = 'PREFLIGHT'


def validate_arm(stage, baseline, removed, report):
    """Fail closed on inventory, mandatory dependencies, plugins and isolation."""
    mods = stage/'mods'
    expected = set(baseline) - set(removed)
    if not removed <= set(baseline) or {p.name for p in mods.iterdir()} != expected:
        raise ValueError('mod inventory changed outside isolated ablation')
    for name in expected:
        p = mods/name
        if not p.is_file() or p.is_symlink() or sha(p) != baseline[name]:
            raise ValueError('mod SHA mismatch in isolated arm')
    required_graph({name: (mods/name).read_bytes() for name in expected})
    if len(report['plugins']) != 6 or any(
            sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']):
        raise ValueError('plugin inventory changed')
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world'} <= set(
                (stage/'server.properties').read_text().splitlines()):
        raise ValueError('disposable loopback stage settings changed')


def prepare_arm(template, destination, frozen_world, baseline, arm, report):
    if arm not in ARMS or destination.exists():
        raise ValueError('unknown arm or reused stage')
    clone_clean_baseline(template, destination)
    for name in ARMS[arm]:
        (destination/'mods'/name).unlink()
    validate_arm(destination, baseline, ARMS[arm], report)
    shutil.copytree(frozen_world, destination/'lab-world', symlinks=False)
    if not (destination/'lab-world'/'level.dat').is_file():
        raise ValueError('identical generated world missing')
    return destination


def summarize(samples):
    if set(samples) != set(ARMS) or any(len(v) != 2 for v in samples.values()):
        raise ValueError('two valid observations per arm required')
    keys = ('boot_s_wall', 'cpu_s', 'rss_mib', 'mean_mspt_from_forge_tps')
    if any(any(x.get(k) is None for k in keys) or x.get('summons_confirmed') != 80
           for values in samples.values() for x in values):
        raise ValueError('unconfirmed zombie count or tick samples')
    return {a: {k: [x[k] for x in values] for k in keys} for a, values in samples.items()}


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or root != Path(temp).resolve()/'fc-full-rp-catserver-official':
        raise ValueError('only exact hosted isolated root allowed')
    PHASE = 'PINNED_BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    if len(baseline) != 28 or any(not names <= set(baseline) for names in ARMS.values()):
        raise ValueError('28 historical mods or optimizer candidates missing')
    frozen = template/'lab-world'
    if not (frozen/'level.dat').is_file():
        raise ValueError('baseline world not generated')
    samples = {arm: [] for arm in ARMS}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'TRIAL_' + str(index)
        stage = prepare_arm(template, root/('cost-trial-' + str(index)),
                            frozen, baseline, arm, report)
        result = run_one(stage, report)
        samples[arm].append(result)
        print('::notice title=Closed optimizer ablation trial::index=' + str(index) +
              ' arm=' + arm + ' removed=' + str(len(ARMS[arm])) +
              ' six_plugins=true eighty_vanilla_zombies=true clean_stop=true '
              'DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    compact = summarize(samples)
    print('::notice title=RP 28-mod exploratory ablation result::' + json.dumps({
        'order': ORDER,
        'arm_removed': {arm: sorted(mods) for arm, mods in ARMS.items()},
        'measurements': compact,
        'world': 'identical generated world copied before every trial',
        'limitations': '80 vanilla zombies; zero clients, cars, players, NPC, crafting or voice; '
                       'Forge tps means not p95/p99; 2 trials only; no promotion or removal',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('exact runner root, official engine, archive, motor, core, guava required')
        main(*sys.argv[1:])
    except (OSError, ValueError, AssertionError, KeyError, zipfile.BadZipFile) as exc:
        print('::error title=28-mod optimizer ablation rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' no private logs or paths published; no rollout', file=sys.stderr)
        sys.exit(2)
