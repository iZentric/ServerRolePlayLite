#!/usr/bin/env python3
"""Bounded three-pair idle/synthetic comparison of 15-mod FunCity vs old CatServer.

Same GitHub-hosted VM, Java 11, frozen disposable world, same plugins/options,
A/B/B/A/A/B. No public port, account, real world, live JAR or gameplay claim.
Do NOT interpret idle+zombies as an RP capacity or hybrid API test.
"""
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import sys
import time

from fc_bench import JvmRun
from fc_engine_family_lab import BOOT_JAR, ENGINES, source_engine, validate_stage
from fc_plugin_first_stage import sha


def proc_sample(pid):
    """RSS MiB and cumulative CPU seconds for this exact JVM PID, not all Java."""
    stat = Path(f'/proc/{pid}/stat').read_text().rsplit(') ', 1)[1].split()
    ticks = int(stat[11]) + int(stat[12])
    rss = next(int(line.split()[1]) / 1024 for line in
               Path(f'/proc/{pid}/status').read_text().splitlines() if line.startswith('VmRSS:'))
    return round(rss, 2), ticks / os.sysconf('SC_CLK_TCK')


def check_env(root, stage):
    temp = os.environ.get('RUNNER_TEMP')
    root = Path(root).resolve()
    if (not temp or not root.is_relative_to(Path(temp).resolve()) or
            root.name != 'fc-engine-ab' or stage != root/'stage'):
        raise ValueError('only new runner-temp stage and output allowed')
    validate_stage(stage)
    if (root/'world-base').exists() or (root/'trial-1').exists():
        raise ValueError('old AB work exists; no reuse')
    return root


def boot(stage, report, seed_world=False):
    log = stage/'bench-private.log'  # never uploaded or printed
    (stage/'eula.txt').write_text('eula=true\n')
    j = JvmRun(str(stage), BOOT_JAR,
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'), '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    try:
        j.start()
        if not j.wait_done(420):
            raise ValueError('candidate did not reach Done')
        text = log.read_text(encoding='utf-8', errors='replace')
        names = [p['declared_name'] for p in report['plugins']]
        if any(not re.search(r'Enabling ' + re.escape(name) + r' (?:v|\d)', text) for name in names):
            raise ValueError('not all six plugins enabled')
        if any(token in text for token in ('Exception in server tick loop',
                                           'Could not load plugin', 'Error occurred while enabling')):
            raise ValueError('critical plugin/tick error')
        if seed_world:
            # Create a disposable common source world once. Never read/copy user's world.
            time.sleep(5)
            return None
        j.send('forceload add 0 0 3 3')
        for _ in range(40):
            j.send('execute in minecraft:overworld run summon minecraft:zombie 0 65 0')
        time.sleep(8)
        text = log.read_text(encoding='utf-8', errors='replace')
        # The workload is invalid unless server acknowledges every requested summon.
        if text.count('Summoned new Zombie') < 40:
            raise ValueError('synthetic workload not confirmed; no metrics published')
        start = proc_sample(j.p.pid)
        samples = []
        for _ in range(6):
            time.sleep(5)
            if j.p.poll() is not None:
                raise ValueError('JVM exited in observation window')
            samples.append(proc_sample(j.p.pid))
        if j.stop(70) != 'CLEAN':
            raise ValueError('server did not stop cleanly')
        return {'rss_mib': round(statistics.median(x[0] for x in samples), 2),
                'cpu_s_30s': round(samples[-1][1] - start[1], 2),
                'window_s': 30, 'summons_confirmed': True, 'mods': 15, 'plugins': 6}
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(12)
        j.close()


def main(root, catserver_source):
    root = Path(root).resolve()
    stage = root/'stage'
    root = check_env(root, stage)
    report = json.loads((stage/'stage-report.json').read_text())
    cat = source_engine('catserver-old', catserver_source)
    if not cat:
        raise ValueError('pinned CatServer unavailable')
    seed = root/'seed'
    shutil.copytree(stage, seed, symlinks=False)
    props = seed/'server.properties'
    with props.open('a') as output:
        output.write('level-seed=2073\n')
    boot(seed, report, seed_world=True)
    world = seed/'lab-world'
    if not (world/'level.dat').is_file() or world.is_symlink():
        raise ValueError('disposable seed world missing')
    # Keep only a frozen GENERATED world; no old player data, logs or accounts.
    shutil.copytree(world, root/'world-base', symlinks=False)
    samples = {'A': [], 'B': []}
    for index, arm in enumerate('ABBAAB', 1):
        trial = root/f'trial-{index}'
        shutil.copytree(stage, trial, symlinks=False)
        shutil.copytree(root/'world-base', trial/'lab-world', symlinks=False)
        with (trial/'server.properties').open('a') as output:
            output.write('level-seed=2073\n')
        if arm == 'B':
            (trial/BOOT_JAR).write_bytes(cat)
            if sha(trial/BOOT_JAR) != ENGINES['catserver-old'][3]:
                raise ValueError('CatServer trial SHA drift')
        elif sha(trial/BOOT_JAR) != ENGINES['funcity'][3]:
            raise ValueError('FunCity trial SHA drift')
        result = boot(trial, report)
        samples[arm].append(result)
        print(f'::notice title=AB trial {index}::arm={arm} workload_confirmed=true '
              'clean_stop=true values=WITHHELD_UNTIL_ALL_VALID', flush=True)
    if any(len(samples[x]) != 3 for x in ('A', 'B')):
        raise ValueError('need exactly 3 valid runs per arm')
    summary = {arm: {key: round(statistics.median(r[key] for r in samples[arm]), 2)
                     for key in ('rss_mib', 'cpu_s_30s')}
               for arm in ('A', 'B')}
    # This is NOT MSPT, FPS or a test of modded-client/hybrid-gameplay integration.
    print('::notice title=Exploratory same-VM 15-mod A/B::' +
          ' A_FunCity_rss_mib=' + str([r['rss_mib'] for r in samples['A']]) +
          ' B_CatServer_rss_mib=' + str([r['rss_mib'] for r in samples['B']]) +
          ' A_cpu_s_30s=' + str([r['cpu_s_30s'] for r in samples['A']]) +
          ' B_cpu_s_30s=' + str([r['cpu_s_30s'] for r in samples['B']]) +
          ' median=' + json.dumps(summary, separators=(',', ':')) +
          ' SAME_JAVA=11 SAME_VM=true WORLD=GENERATED 40_ZOMBIES_EACH=true '
          'MSPT=NOT_MEASURED CLIENT_JOIN=NOT_TESTED NO_PERFORMANCE_WINNER_CLAIM', flush=True)
    return summary


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError('expected new runner-temp root and SHA-pinned old pack')
        main(sys.argv[1], sys.argv[2])
    except (ValueError, OSError, KeyError) as exc:
        print('::error title=AB invalid; no benchmark verdict::' + str(exc), file=sys.stderr)
        sys.exit(2)
