#!/usr/bin/env python3
"""Closed 28/6 Saturn-vs-FerriteCore substitution, NOT Saturn stacked on top.

ModernFix and RP content identical, frozen generated world, 80 vanilla mobs.
Two interleaved B/S/S/B observations, heap after explicit GC; no real clients,
vehicle driving, world save p99 or capacity claims. No live/PC writes.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import zipfile

from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_full28_memory_choice import FERRITE, measure
from fc_full_rp_engine_boot import main as full_boot, required_graph
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import validate_arm
from fc_server_candidate_scan import CANDIDATES, verify

ORDER = 'BSSB'
PHASE = 'PREFLIGHT'


def prepare(template, output, world, baseline, report, arm, saturn):
    if arm not in ('B', 'S') or output.exists() or FERRITE not in baseline:
        raise ValueError('unsafe Saturn experiment arm')
    clone_clean_baseline(template, output)
    if arm == 'S':
        (output/'mods'/FERRITE).unlink()
        shutil.copyfile(saturn, output/'mods'/saturn.name)
    files = {p.name for p in (output/'mods').iterdir()}
    wanted = set(baseline) if arm == 'B' else set(baseline) - {FERRITE} | {saturn.name}
    if files != wanted or len(files) != 28 or any(
            sha(output/'mods'/name) != digest for name, digest in baseline.items()
            if arm == 'B' or name != FERRITE):
        raise ValueError('Saturn trial changed more than a single substitution')
    if arm == 'S' and sha(output/'mods'/saturn.name) != CANDIDATES['saturn'][3]:
        raise ValueError('Saturn bytes changed')
    required_graph({p.name: p.read_bytes() for p in (output/'mods').iterdir()})
    if arm == 'B':
        validate_arm(output, baseline, frozenset(), report)
    elif len(report['plugins']) != 6 or any(
            sha(output/'plugins'/p['jar']) != p['sha256'] for p in report['plugins']):
        raise ValueError('plugin inventory drift')
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world'} <= set(
                (output/'server.properties').read_text().splitlines()):
        raise ValueError('not a closed loopback trial')
    shutil.copytree(world, output/'lab-world', symlinks=False)
    if not (output/'lab-world'/'level.dat').is_file():
        raise ValueError('frozen world missing')
    return output


def summarize(data):
    if set(data) != {'B', 'S'} or any(len(v) != 2 for v in data.values()):
        raise ValueError('two valid samples per arm required')
    fields = ('boot_s_wall', 'cpu_s_30s', 'rss_mib', 'mean_tick_ms',
              'heap_after_explicit_gc_mib')
    if any(any(x.get(k) is None for k in fields) for v in data.values() for x in v):
        raise ValueError('memory/CPU/tick evidence incomplete')
    return {arm: {key: [x[key] for x in v] for key in fields}
            for arm, v in data.items()}


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('only fresh hosted runner root')
    saturn, modid, digest, file_id, _ = verify(root, 'saturn')
    if modid != 'saturn' or digest != CANDIDATES['saturn'][3]:
        raise ValueError('not the pinned author Saturn 1.16.5 artifact')
    PHASE = 'BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    world = template/'lab-world'
    if (len(baseline) != 28 or FERRITE not in baseline or
            saturn.name in baseline or not (world/'level.dat').is_file()):
        raise ValueError('historic 28 or frozen world drift')
    data = {'B': [], 'S': []}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'TRIAL_' + str(index)
        stage = prepare(template, root/('saturn-trial-' + str(index)), world,
                        baseline, report, arm, saturn)
        data[arm].append(measure(stage, report))
        print('::notice title=Memory optimizer replacement trial::index=' + str(index) +
              ' arm=' + arm + ' mods=28 plugins=6 zombies=80 stopped_cleanly=true '
              'VALUES_WITHHELD_UNTIL_COMPLETE', flush=True)
    result = summarize(data)
    print('::notice title=FerriteCore vs Saturn 1.16.5 memory evidence::' + json.dumps({
        'order': ORDER,
        'B': '28 mods with FerriteCore and ModernFix',
        'S': '28 mods with pinned Saturn instead of FerriteCore; same ModernFix',
        'saturn_file_id': file_id, 'measurements': result,
        'limits': '80 vanilla zombies, generated world, 6 plugins, no clients/voice/vehicles '
                  'or 34/13; post-GC heap not max-player result; no live rollout',
    }, separators=(',', ':')), flush=True)
    return result


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six hosted SHA-pinned inputs required')
        main(*sys.argv[1:])
    except (OSError, ValueError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=Saturn substitution rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' no raw logs/world/JARs published; no rollout', file=sys.stderr)
        sys.exit(2)
