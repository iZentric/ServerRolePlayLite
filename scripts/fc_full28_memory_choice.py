#!/usr/bin/env python3
"""Closed CatServer 28/6 memory ablation for FerriteCore and ModernFix.

Same generated world + 80 vanilla zombies; CPU/RSS, Forge mean tick, and used
heap after one explicit GC. Only historical SHA-checked files, no PC/clients.
B/F/M/M/F/B = baseline, without FerriteCore, without ModernFix.
Results are NOT jvm player capacity or real-world memory proofs.
"""
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time
import zipfile

from fc_bench import JvmRun
from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_engine_ab_full_content import proc_sample
from fc_full_rp_engine_boot import main as full_boot
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import validate_arm
from fc_server_optimizer_ab import BOOT_JAR, OVERALL, check_log

FERRITE = 'ferritecore-2.1.1-forge.jar'
MODERN = 'modernfix-forge-5.18.0+mc1.16.5.jar'
ARMS = {'B': frozenset(), 'F': frozenset({FERRITE}),
        'M': frozenset({MODERN})}
ORDER = 'BFMMFB'
PHASE = 'PREFLIGHT'


def parse_heap(text):
    # Java 17 Temurin G1 `jcmd GC.heap_info`. Do not publish process output.
    match = re.search(r'garbage-first heap\s+total\s+\d+K, used\s+(\d+)K', text)
    if not match:
        raise ValueError('explicit-GC heap measurement not parsable')
    return round(int(match.group(1))/1024, 2)


def used_heap_after_gc(pid):
    for command in ('GC.run', 'GC.heap_info'):
        result = subprocess.run(['jcmd', str(pid), command], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=45, check=False)
        if result.returncode != 0:
            raise ValueError('explicit-GC heap measurement unavailable')
        if command == 'GC.heap_info':
            return parse_heap(result.stdout)
    raise ValueError('explicit-GC heap measurement unavailable')


def measure(stage, report):
    log = stage/'private-memory-measurement.log'
    (stage/'eula.txt').write_text('eula=true\n')
    j = JvmRun(str(stage), BOOT_JAR,
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
                '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    try:
        j.start()
        if not j.wait_done(420):
            raise ValueError('server did not reach Done')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        for cmd in ('gamerule doDaylightCycle false', 'time set night',
                    'forceload add 0 0 3 3'):
            j.send(cmd)
        for _ in range(80):
            j.send('execute in minecraft:overworld run summon minecraft:zombie 0 65 0')
        time.sleep(12)
        text = log.read_text(encoding='utf-8', errors='replace')
        if text.count('Summoned new Zombie') < 80:
            raise ValueError('zombie workload unconfirmed')
        start = proc_sample(j.p.pid)
        samples = []
        for _ in range(6):
            j.send('forge tps')
            time.sleep(5)
            if j.p.poll() is not None:
                raise ValueError('server exited during observation')
            samples.append(proc_sample(j.p.pid))
        text = log.read_text(encoding='utf-8', errors='replace')
        mspt = [float(x) for x in OVERALL.findall(text)]
        if len(mspt) < 4:
            raise ValueError('Forge tick samples absent')
        # CPU/RSS window ENDS before explicit full GC; heap-after-GC is separate.
        result = {'cpu_s_30s': round(samples[-1][1] - start[1], 2),
                  'rss_mib': round(statistics.median(x[0] for x in samples), 2),
                  'mean_tick_ms': round(statistics.median(mspt[-6:]), 2),
                  'boot_s_wall': j.done_wall_s}
        result['heap_after_explicit_gc_mib'] = used_heap_after_gc(j.p.pid)
        if j.stop(70) != 'CLEAN' or j.p.returncode != 0:
            raise ValueError('server did not stop cleanly')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        return result
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(15)
        j.close()


def summarize(data):
    if set(data) != set(ARMS) or any(len(v) != 2 for v in data.values()):
        raise ValueError('two valid trials per arm required')
    keys = ('boot_s_wall', 'cpu_s_30s', 'rss_mib', 'mean_tick_ms',
            'heap_after_explicit_gc_mib')
    if any(any(x.get(k) is None for k in keys) for v in data.values() for x in v):
        raise ValueError('memory or tick sample missing')
    return {arm: {k: [x[k] for x in v] for k in keys} for arm, v in data.items()}


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('hosted isolated temp only')
    PHASE = 'BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    world = template/'lab-world'
    if len(baseline) != 28 or not {FERRITE, MODERN} <= set(baseline) or not (
            world/'level.dat').is_file():
        raise ValueError('28 baseline or frozen world missing')
    data = {arm: [] for arm in ARMS}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'TRIAL_' + str(index)
        stage = root/('memory-trial-' + str(index))
        clone_clean_baseline(template, stage)
        for name in ARMS[arm]:
            (stage/'mods'/name).unlink()
        validate_arm(stage, baseline, ARMS[arm], report)
        shutil.copytree(world, stage/'lab-world', symlinks=False)
        if not (stage/'lab-world'/'level.dat').is_file():
            raise ValueError('frozen world lost')
        data[arm].append(measure(stage, report))
        print('::notice title=Full 28 memory ablation trial::index=' + str(index) +
              ' arm=' + arm + ' mods=' + str(28-len(ARMS[arm])) +
              ' plugins=6 zombies=80 explicit_gc=true clean_stop=true '
              'VALUES_WITHHELD', flush=True)
    compact = summarize(data)
    print('::notice title=Full 28 memory mod ablation::' + json.dumps({
        'order': ORDER, 'removed': {arm: sorted(names) for arm, names in ARMS.items()},
        'observations': compact,
        'limitations': 'same generated world; 80 vanilla zombies, 6 historical plugins, '
                       'zero players/drivers/voice, not 34/13 or production heap; two '
                       'samples do not certify max players or justify removal',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six hosted SHA-pinned inputs required')
        main(*sys.argv[1:])
    except (OSError, ValueError, KeyError, AssertionError, zipfile.BadZipFile,
            subprocess.TimeoutExpired) as exc:
        print('::error title=Full 28 memory ablation rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' private logs/paths not published; no rollout', file=sys.stderr)
        sys.exit(2)
