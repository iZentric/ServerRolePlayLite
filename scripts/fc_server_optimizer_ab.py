#!/usr/bin/env python3
"""GitHub-hosted, disposable A/B of server tick optimizers with 15 RP mods.

Uses only a NEW GitHub runner temp directory, a generated world, local-only
online-mode + whitelist, six already-tested historical plugins, Java 11.
Not the owner PC/live server/world, and never publishes logs or binary artifacts.
No player simulation: comparisons are exploratory, not an RP capacity or FPS test.
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
from fc_engine_ab_full_content import proc_sample
from fc_mod_binary_evidence import inspect_jar
from fc_modded_candidate import CHOSEN, PERFORMANCE
from fc_plugin_first_stage import ENGINE_SHA, GUAVA21_SHA, sha

ROADRUNNER = 'RoadRunner-mc1.16.5-1.5.2.jar'
PERFORMANT = 'performant-1.16.2-5-4.1m.jar'
BOOT_JAR = 'FunCity-1.16.5-b1.0827.jar'
FATAL = ('Exception in server tick loop', 'Could not load plugin',
         'Error occurred while enabling', 'Failed to start', 'Mixin apply failed')
OVERALL = re.compile(r'Overall[^\n]*?Mean tick time:\s*([0-9]+(?:\.[0-9]+)?)\s*ms', re.I)


def guard(root, template, performant):
    root = Path(root).resolve()
    template = Path(template).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or root != Path(temp).resolve()/'fc-server-optimizer-ab' or template != root/'stage':
        raise ValueError('refuse non-hosted or owner PC/server paths')
    if any((root/x).exists() for x in ('seed', 'world-base', 'trial-1')):
        raise ValueError('refuse stale world/trials')
    report = json.loads((template/'stage-report.json').read_text())
    mods = report['server_mods']
    expected = set(CHOSEN + PERFORMANCE)
    if (report['scope'] != 'UNRELEASED local modded compatibility experiment; ownership unverified' or
            report['server_optimizers'] != list(PERFORMANCE) or
            len(mods) != len(expected) or {m['jar'] for m in mods} != expected or
            {p.name for p in (template/'mods').iterdir()} != expected or
            any(sha(template/'mods'/m['jar']) != m['sha256'] for m in mods) or
            sha(template/BOOT_JAR) != ENGINE_SHA or
            sha(template/'runtime/guava-21.0.jar') != GUAVA21_SHA or
            len(report['plugins']) != 6 or
            any(sha(template/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('template inventory/sha mismatch')
    props = set((template/'server.properties').read_text().splitlines())
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world'} <= props:
        raise ValueError('loopback, whitelist or properties mismatch')
    if (template/'lab-world').exists() or (template/'eula.txt').exists():
        raise ValueError('template is not clean')
    if performant != '-':
        jar = Path(performant).resolve()
        if jar != root/PERFORMANT or jar.is_symlink() or not jar.is_file() or not (100_000 < jar.stat().st_size < 1_000_000):
            raise ValueError('invalid exact Performant source path/size')
        evidence = inspect_jar(jar.read_bytes())
        if evidence['metadata'] != 'mods.toml' or 'performant' not in evidence['mod_ids']:
            raise ValueError('download is not the expected Performant Forge JAR')
        print('::notice title=Performant original artifact verified::' +
              f'fileId=4562378 sha256={sha(jar)} mod_id=performant (NOT redistributed)', flush=True)
    return report


def make_arm(template, destination, world, arm, performant):
    """Identical baseline files, except exactly ONE server-side optimizer JAR."""
    shutil.copytree(template, destination, symlinks=False)
    mods = destination/'mods'
    rr = mods/ROADRUNNER
    if arm == 'P':
        rr.unlink()
        shutil.copyfile(performant, mods/PERFORMANT)
        assert 'performant' in inspect_jar((mods/PERFORMANT).read_bytes())['mod_ids']
        expected = set(CHOSEN + PERFORMANCE) - {ROADRUNNER} | {PERFORMANT}
    elif arm == 'N':
        rr.unlink()  # availability fallback; cannot be named a Performant comparison
        expected = set(CHOSEN + PERFORMANCE) - {ROADRUNNER}
    elif arm == 'R':
        expected = set(CHOSEN + PERFORMANCE)
    else:
        raise ValueError('unknown optimization arm')
    if {p.name for p in mods.iterdir()} != expected:
        raise ValueError('optimizer overlap or inventory drift')
    if world:
        shutil.copytree(world, destination/'lab-world', symlinks=False)
    if (destination/'lab-world').is_symlink():
        raise ValueError('symlink world forbidden')
    return destination


def check_log(text, report):
    if any(token in text for token in FATAL):
        raise ValueError('fatal server/plugin marker; no numbers published')
    if any(not re.search(r'Enabling ' + re.escape(p['declared_name']) + r' (?:v|\d)', text)
           for p in report['plugins']):
        raise ValueError('a staged plugin was not enabled')


def run_one(stage, report, generate=False):
    log = stage/'private-benchmark.log'  # NOT uploaded or printed
    (stage/'eula.txt').write_text('eula=true\n')  # disposable isolated runner
    j = JvmRun(str(stage), BOOT_JAR,
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
                '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    try:
        j.start()
        if not j.wait_done(420):
            raise ValueError('server did not reach Done; no A/B verdict; exit=' + str(j.p.poll()))
        text = log.read_text(encoding='utf-8', errors='replace')
        check_log(text, report)
        if generate:
            time.sleep(5)
            result = None
        else:
            j.send('gamerule doDaylightCycle false')
            j.send('time set night')
            j.send('forceload add 0 0 3 3')
            for _ in range(80):
                j.send('execute in minecraft:overworld run summon minecraft:zombie 0 65 0')
            # Give the server time to finish all commands and enter a repeatable idle tick phase.
            time.sleep(12)
            text = log.read_text(encoding='utf-8', errors='replace')
            if text.count('Summoned new Zombie') < 80:
                raise ValueError('zombie workload unconfirmed; no numbers published')
            samples = []
            t0 = time.monotonic()
            start = proc_sample(j.p.pid)
            for _ in range(6):
                j.send('forge tps')
                time.sleep(5)
                if j.p.poll() is not None:
                    raise ValueError('JVM exited during observation')
                samples.append(proc_sample(j.p.pid))
            text = log.read_text(encoding='utf-8', errors='replace')
            mspt = [float(m) for m in OVERALL.findall(text)]
            # Forge command may be unavailable on this hybrid; CPU/RSS still valid.
            result = {'rss_mib': round(statistics.median(v[0] for v in samples), 2),
                      'boot_s_wall': j.done_wall_s,
                      'cpu_s': round(samples[-1][1] - start[1], 2),
                      'window_s': round(time.monotonic() - t0, 2),
                      'mean_mspt_from_forge_tps': round(statistics.median(mspt[-6:]), 2) if len(mspt) >= 4 else None,
                      'mspt_samples': len(mspt), 'summons_confirmed': 80,
                      'client_fps': None, 'players': 0}
        if j.stop(70) != 'CLEAN' or j.p.returncode != 0:
            raise ValueError('server did not stop cleanly; no numbers published')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        return result
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(15)
        j.close()


def main(root, performant):
    root = Path(root).resolve()
    stage = root/'stage'
    report = guard(root, stage, performant)
    other = 'P' if performant != '-' else 'N'
    seed = make_arm(stage, root/'seed', None, 'R', performant)
    run_one(seed, report, generate=True)
    world = seed/'lab-world'
    if not (world/'level.dat').is_file():
        raise ValueError('generated world missing; no numbers published')
    shutil.copytree(world, root/'world-base', symlinks=False)
    samples = {'R': [], other: []}
    for idx, arm in enumerate('R' + other + other + 'R', 1):
        trial = make_arm(stage, root/f'trial-{idx}', root/'world-base', arm, performant)
        measurement = run_one(trial, report)
        samples[arm].append(measurement)
        print(f'::notice title=Bounded AB arm {idx}::arm={arm} 80_mobs=true '
              '6_plugins=true 15_RP_mods=true stopped_cleanly=true DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    if any(len(samples[arm]) != 2 for arm in ('R', other)):
        raise ValueError('need two valid trials each; no numbers published')
    # Avoid spurious winner from tiny differences and coarse forge tps windows.
    compact = {arm: {'rss_mib': [x['rss_mib'] for x in samples[arm]],
                     'cpu_s_30s': [x['cpu_s'] for x in samples[arm]],
                     'mspt_ms': [x['mean_mspt_from_forge_tps'] for x in samples[arm]]}
               for arm in ('R', other)}
    print('::notice title=Hosted optimizer A/B result::' + json.dumps({
        'arm_R': 'RoadRunner 1.5.2',
        'arm_other': 'Performant 4.1m' if other == 'P' else 'NO OPTIMIZER (Performant unavailable)',
        'observations': compact,
        'caveat': 'Generated idle world, 80 zombies, no players; not live FunCity MSPT/FPS or RP compatibility',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError('expected runner-temp root and original Performant path or -')
        main(sys.argv[1], sys.argv[2])
    except (ValueError, OSError, KeyError, AssertionError) as exc:
        # No raw private logs or server files leave the runner.
        print('::error title=Hosted optimizer A/B invalid::' + str(exc), file=sys.stderr)
        sys.exit(2)
