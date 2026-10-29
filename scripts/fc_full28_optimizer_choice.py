#!/usr/bin/env python3
"""Official CatServer 28/6 RoadRunner-vs-Performant closed, interleaved comparison.

Uses ONLY SHA-pinned hosted historical sources and author's exact Performant
Forge JAR. Same generated world, 80 vanilla zombies; ZERO real players/vehicles,
client, private RP world, or production changes. Not a capacity benchmark.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_catserver_optimizer_ab import PERFORMANT_SHA
from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_full_rp_engine_boot import main as full_boot, required_graph
from fc_mod_binary_evidence import inspect_jar
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import validate_arm
from fc_server_optimizer_ab import PERFORMANT, ROADRUNNER, run_one

ORDER = 'RPPR'
PHASE = 'PREFLIGHT'


def check_performant(root, path):
    root, path = Path(root).resolve(), Path(path)
    if (path.is_symlink() or not path.is_file() or path.resolve() != root/PERFORMANT or
            sha(path) != PERFORMANT_SHA):
        raise ValueError('exact author Performant SHA/path missing')
    evidence = inspect_jar(path.read_bytes())
    if evidence['metadata'] != 'mods.toml' or 'performant' not in evidence['mod_ids']:
        raise ValueError('exact author Forge mod ID missing')
    return path


def prepare(template, destination, world, baseline, report, arm, performant):
    if destination.exists() or arm not in 'RP' or len(arm) != 1 or ROADRUNNER not in baseline:
        raise ValueError('unsafe trial or missing RoadRunner')
    clone_clean_baseline(template, destination)
    if arm == 'P':
        (destination/'mods'/ROADRUNNER).unlink()
        shutil.copyfile(performant, destination/'mods'/PERFORMANT)
    actual = {p.name for p in (destination/'mods').iterdir()}
    expected = set(baseline) if arm == 'R' else set(baseline) - {ROADRUNNER} | {PERFORMANT}
    if actual != expected or len(actual) != 28 or any(
            not (destination/'mods'/n).is_file() or (destination/'mods'/n).is_symlink() or
            sha(destination/'mods'/n) != h for n, h in baseline.items() if n != ROADRUNNER or arm == 'R'):
        raise ValueError('not exactly one optimizer changed')
    if arm == 'P' and sha(destination/'mods'/PERFORMANT) != PERFORMANT_SHA:
        raise ValueError('Performant staged bytes changed')
    # Validate mandatory dependency closure and plugin checks regardless of arm.
    required_graph({p.name: p.read_bytes() for p in (destination/'mods').iterdir()})
    if arm == 'R':
        validate_arm(destination, baseline, frozenset(), report)
    elif (len(report['plugins']) != 6 or any(
            sha(destination/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('plugin inventory changed')
    props = set((destination/'server.properties').read_text().splitlines())
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world'} <= props:
        raise ValueError('trial is not closed to public')
    shutil.copytree(world, destination/'lab-world', symlinks=False)
    if not (destination/'lab-world'/'level.dat').is_file():
        raise ValueError('identical frozen world missing')
    return destination


def summarize(samples):
    if set(samples) != {'R', 'P'} or any(len(v) != 2 for v in samples.values()):
        raise ValueError('two completed trials required per optimizer')
    fields = ('boot_s_wall', 'cpu_s', 'rss_mib', 'mean_mspt_from_forge_tps')
    if any(x.get('summons_confirmed') != 80 or any(x.get(k) is None for k in fields)
           for values in samples.values() for x in values):
        raise ValueError('zombie workload or Forge tick missing')
    return {arm: {key: [x[key] for x in values] for key in fields}
            for arm, values in samples.items()}


def main(root, engine, archive, motor, core, guava, performant):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('hosted temporary root only')
    performant = check_performant(root, performant)
    PHASE = 'BASELINE_28'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    world = template/'lab-world'
    if len(baseline) != 28 or ROADRUNNER not in baseline or not (world/'level.dat').is_file():
        raise ValueError('28-mod fixed world/optimizer missing')
    samples = {'R': [], 'P': []}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'TRIAL_' + str(index)
        stage = prepare(template, root/('opt-full28-trial-' + str(index)),
                        world, baseline, report, arm, performant)
        result = run_one(stage, report)
        samples[arm].append(result)
        print('::notice title=Full RP optimizer trial::index=' + str(index) +
              ' arm=' + arm + ' mods=28 plugins=6 mobs=80 clean_stop=true '
              'DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    compact = summarize(samples)
    print('::notice title=Full 28 RP RoadRunner vs Performant::' + json.dumps({
        'order': ORDER, 'full_historical_mods': 28, 'plugins': 6,
        'measurements': compact,
        'limitations': 'generated world, 80 vanilla zombies, zero players/mafia NPC/drivers/voice; '
                       'NOT live 34/13, not tick p95/p99, no max players claim or deployment',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 8:
            raise ValueError('seven hosted pinned inputs required')
        main(*sys.argv[1:])
    except (OSError, ValueError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=Full 28 optimizer comparison rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) + ' no private data or rollout', file=sys.stderr)
        sys.exit(2)
