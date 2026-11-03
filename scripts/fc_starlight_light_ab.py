#!/usr/bin/env python3
"""Bounded lighting-specific trial: SHA-pinned original Starlight vs 28/6.

B/S/S/B copies of one generated world, each with 24 verified 32x32 toggles
between opaque stone and emissive glowstone. One server at a time, 0 clients.
This is NOT a concurrent-player benchmark or a real city lighting profile.
"""
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import sys
import time
import zipfile

from fc_bench import JvmRun
from fc_chunk_sending_canary import clone_clean_baseline, safe_failure_category
from fc_engine_ab_full_content import proc_sample
from fc_full_rp_engine_boot import main as full_boot, required_graph
from fc_plugin_first_stage import sha
from fc_server_optimizer_ab import BOOT_JAR, check_log
from fc_starlight_official_canary import FILE, SHA256, verify

ORDER = 'BSSB'
TOGGLES = 24
BLOCKS_PER_TOGGLE = 32*32
PHASE = 'PREFLIGHT'


def workload():
    commands = ['gamerule doMobSpawning false', 'gamerule doDaylightCycle false',
                'forceload add 0 0 2 2', 'scoreboard objectives add fcbench dummy',
                'scoreboard players set #writes fcbench 0',
                'fill 0 120 0 31 120 31 minecraft:stone']
    for i in range(TOGGLES):
        block = 'glowstone' if i % 2 == 0 else 'stone'
        commands.extend((
            'execute store result score #last fcbench run fill 0 120 0 31 120 31 minecraft:' + block,
            'scoreboard players operation #writes fcbench += #last fcbench'))
    commands += ['scoreboard players get #writes fcbench',
                 'execute store result score #end fcbench if block 0 120 0 minecraft:stone',
                 'scoreboard players get #end fcbench',
                 'say FCBENCH_LIGHT_COMPLETE']
    return commands


def confirm(text):
    writes = [int(x) for x in re.findall(r'#writes has (\d+) \[fcbench\]', text)]
    end = [int(x) for x in re.findall(r'#end has (\d+) \[fcbench\]', text)]
    if (writes != [TOGGLES*BLOCKS_PER_TOGGLE] or end != [1] or
            text.count('FCBENCH_LIGHT_COMPLETE') != 1):
        raise ValueError('lighting changes not fully confirmed')


def trial(stage, report):
    log = stage/'private-lighting-ab.log'
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
        # Same warm-up/edit on every copied world. Wait for its console queue.
        for command in workload()[:6]:
            j.send(command)
        j.send('say FCBENCH_WARMUP_COMPLETE')
        warmup_start = time.monotonic()
        while time.monotonic() - warmup_start < 80:
            if j.p.poll() is not None:
                raise ValueError('server exited during lighting warm-up')
            if 'FCBENCH_WARMUP_COMPLETE' in log.read_text(encoding='utf-8', errors='replace'):
                break
            time.sleep(0.2)
        else:
            raise ValueError('light warm-up did not complete')
        time.sleep(5)
        before = proc_sample(j.p.pid)
        t0 = time.monotonic()
        for command in workload()[6:]:
            j.send(command)
        while time.monotonic() - t0 < 100:
            if j.p.poll() is not None:
                raise ValueError('server exited during lighting workload')
            text = log.read_text(encoding='utf-8', errors='replace')
            if 'FCBENCH_LIGHT_COMPLETE' in text:
                break
            time.sleep(0.2)
        else:
            raise ValueError('lighting workload did not finish within 100s')
        wall = time.monotonic() - t0
        confirm(text)
        # Allow queued light propagation/disk IO to settle; explicitly avoid
        # misnaming console-ack time as final light propagation latency.
        time.sleep(12)
        after = proc_sample(j.p.pid)
        if j.p.poll() is not None:
            raise ValueError('server exited before observation completed')
        result = {'command_ack_wall_s': round(wall, 2),
                  'cpu_s_plus_12s_settle': round(after[1]-before[1], 2),
                  'rss_mib_after_settle': round(after[0], 2),
                  'actual_changed_blocks': TOGGLES*BLOCKS_PER_TOGGLE}
        if j.stop(70) != 'CLEAN' or j.p.returncode != 0:
            raise ValueError('server did not stop cleanly')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        return result
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(15)
        j.close()


def prepare(template, dest, world, baseline, report, candidate):
    if dest.exists() or candidate.is_symlink() or sha(candidate) != SHA256:
        raise ValueError('dirty destination or unpinned Starlight')
    clone_clean_baseline(template, dest)
    if candidate.name in baseline:
        raise ValueError('lighting mod already in baseline')
    if candidate is not None and dest.name.endswith('-S'):
        shutil.copyfile(candidate, dest/'mods'/candidate.name)
    expected = set(baseline) | ({FILE} if dest.name.endswith('-S') else set())
    if ({p.name for p in (dest/'mods').iterdir()} != expected or
            any(sha(dest/'mods'/n) != h for n, h in baseline.items()) or
            len(report['plugins']) != 6 or
            any(sha(dest/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('light arm JAR/plugin drift')
    required_graph({p.name: p.read_bytes() for p in (dest/'mods').iterdir()})
    props = set((dest/'server.properties').read_text().splitlines())
    if not {'server-ip=127.0.0.1', 'white-list=true', 'online-mode=true',
            'level-name=lab-world', 'view-distance=5'} <= props:
        raise ValueError('trial not loopback/whitelisted')
    shutil.copytree(world, dest/'lab-world', symlinks=False)
    if not (dest/'lab-world'/'level.dat').is_file():
        raise ValueError('frozen generated world missing')
    return dest


def summarize(data):
    if set(data) != {'B','S'} or any(len(v) != 2 for v in data.values()):
        raise ValueError('need two valid samples per arm')
    keys = ('command_ack_wall_s', 'cpu_s_plus_12s_settle',
            'rss_mib_after_settle', 'actual_changed_blocks')
    if any(any(x.get(k) is None for k in keys) or
           x['actual_changed_blocks'] != TOGGLES*BLOCKS_PER_TOGGLE
           for v in data.values() for x in v):
        raise ValueError('lighting result incomplete')
    return {arm: {k: [x[k] for x in v] for k in keys}
            for arm, v in data.items()}


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('only a new hosted runner root')
    candidate, digest = verify(root)
    if digest != SHA256:
        raise ValueError('untrusted Starlight')
    PHASE = 'BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    world = template/'lab-world'
    if len(baseline) != 28 or not (world/'level.dat').is_file():
        raise ValueError('not 28/6 frozen generated baseline')
    data = {'B': [], 'S': []}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'LIGHT_TRIAL_' + str(index)
        stage = prepare(template, root/('light-trial-' + str(index) + '-' + arm),
                        world, baseline, report, candidate)
        data[arm].append(trial(stage, report))
        print('::notice title=Lighting candidate trial::index=' + str(index) +
              ' arm=' + arm + ' confirmed_changed_blocks=' + str(TOGGLES*BLOCKS_PER_TOGGLE) +
              ' clean_stop=true values_withheld_until_all_pass', flush=True)
    result = summarize(data)
    print('::notice title=Original Starlight 1.16.5 lighting-specific A/B::' + json.dumps({
        'order': ORDER, 'arms': {'B': 'baseline 28', 'S': '29 with original Starlight RC2'},
        'source_sha256': SHA256, 'measurements': result,
        'limits': 'generated world/6 plugins/zero clients; command ack is NOT p95 tick or finished '
                  'light propagation; no simultaneous player limit/real city/34 mod 13 plugin proof',
    }, separators=(',', ':')), flush=True)
    return result


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('six pinned hosted inputs required')
        main(*sys.argv[1:])
    except (ValueError, OSError, KeyError, AssertionError, zipfile.BadZipFile) as exc:
        print('::error title=Starlight lighting A/B invalid::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) + ' no private logs/JAR/world published',
              file=sys.stderr)
        sys.exit(2)
