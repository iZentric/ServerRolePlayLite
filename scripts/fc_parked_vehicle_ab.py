#!/usr/bin/env python3
"""Closed, vehicle-entity-specific 28/6 vs 27/6 RoadRunner ablation.

Sixteen stationary smart_car entities in a generated flat test patch, no driver,
network, PC, server, private city, or actual vehicle traffic. Four sequential
trials R/N/N/R on a frozen world. This is NOT a real-player benchmark.
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
from fc_chunk_sending_canary import safe_failure_category
from fc_engine_ab_full_content import proc_sample
from fc_full_rp_engine_boot import main as full_boot
from fc_rp_mod_cost_ab import prepare_arm
from fc_server_optimizer_ab import check_log, OVERALL, ROADRUNNER
from fc_plugin_first_stage import sha

ORDER = 'RNNR'
VEHICLES = 16
PHASE = 'PREFLIGHT'


def vehicle_commands():
    """Fixed platform/positions. Source: MrCrayfish 1.16.X ModEntities SMART_CAR."""
    commands = ['gamerule doMobSpawning false', 'gamerule doDaylightCycle false',
                'time set day', 'forceload add 0 0 3 3',
                'fill 0 68 0 12 68 12 minecraft:stone',
                'fill 0 69 0 12 80 12 minecraft:air',
                'scoreboard objectives add fcbench dummy']
    commands += ['summon vehicle:smart_car ' + str(x) + ' 69 ' + str(z)
                 for x in (1, 4, 7, 10) for z in (1, 4, 7, 10)]
    commands += ['execute store result score #cars fcbench if entity @e[type=vehicle:smart_car]',
                 'scoreboard players get #cars fcbench']
    return commands


def confirmed_vehicle_count(text, snapshots=1):
    """Scoreboard RESULT of an entity selector, not a summon-success guess."""
    matches = re.findall(r'#cars has (\d+) \[fcbench\]', text)
    if len(matches) != snapshots or any(int(n) != VEHICLES for n in matches):
        raise ValueError('stationary modded vehicle entity count unconfirmed')
    return VEHICLES


def run_vehicle(stage, report):
    log = stage/'private-parked-vehicles.log'  # never print or upload
    (stage/'eula.txt').write_text('eula=true\n')
    j = JvmRun(str(stage), 'FunCity-1.16.5-b1.0827.jar',
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
                '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    try:
        j.start()
        if not j.wait_done(420):
            raise ValueError('server did not reach Done')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        for line in vehicle_commands():
            j.send(line)
        time.sleep(16)
        text = log.read_text(encoding='utf-8', errors='replace')
        confirmed_vehicle_count(text)
        if j.p.poll() is not None:
            raise ValueError('server exited before vehicle measurement')
        start = proc_sample(j.p.pid)
        samples = []
        for _ in range(6):
            j.send('forge tps')
            time.sleep(5)
            if j.p.poll() is not None:
                raise ValueError('server exited during vehicle measurement')
            samples.append(proc_sample(j.p.pid))
        j.send('execute store result score #cars fcbench if entity @e[type=vehicle:smart_car]')
        j.send('scoreboard players get #cars fcbench')
        time.sleep(2)
        text = log.read_text(encoding='utf-8', errors='replace')
        confirmed_vehicle_count(text, snapshots=2)  # unchanged before AND after observation
        values = [float(x) for x in OVERALL.findall(text)]
        if len(values) < 4:
            raise ValueError('Forge tick samples absent')
        result = {'cpu_s_30s': round(samples[-1][1] - start[1], 2),
                  'rss_mib': round(statistics.median(x[0] for x in samples), 2),
                  'mean_tick_ms': round(statistics.median(values[-6:]), 2),
                  'boot_s_wall': j.done_wall_s, 'parked_cars_confirmed': VEHICLES}
        if j.stop(70) != 'CLEAN' or j.p.returncode != 0:
            raise ValueError('server did not stop cleanly')
        check_log(log.read_text(encoding='utf-8', errors='replace'), report)
        return result
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(15)
        j.close()


def main(root, engine, archive, motor, core, guava):
    global PHASE
    root = Path(root).resolve()
    if (not os.environ.get('RUNNER_TEMP') or
            root != Path(os.environ['RUNNER_TEMP']).resolve()/'fc-full-rp-catserver-official'):
        raise ValueError('new exact hosted runner root required')
    PHASE = 'PINNED_BASELINE'
    full_boot(root, 'catserver-official', engine, archive, motor, core, guava)
    template = root/'stage'
    report = json.loads((template/'stage-report.json').read_text())
    baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
    if len(baseline) != 28 or ROADRUNNER not in baseline:
        raise ValueError('historic 28-mod target changed')
    frozen = template/'lab-world'
    if not (frozen/'level.dat').is_file():
        raise ValueError('frozen generated world missing')
    samples = {'R': [], 'N': []}
    for index, arm in enumerate(ORDER, 1):
        PHASE = 'VEHICLE_TRIAL_' + str(index)
        stage = root/('parked-vehicle-' + str(index))
        # Re-use the strict manifest/dep/plugin guard; N only removes RoadRunner.
        prepare_arm(template, stage, frozen, baseline, 'A', report)
        if arm == 'N':
            (stage/'mods'/ROADRUNNER).unlink()
            from fc_full_rp_engine_boot import required_graph
            required_graph({p.name: p.read_bytes() for p in (stage/'mods').iterdir()})
        if ({p.name for p in (stage/'mods').iterdir()} !=
                set(baseline) - ({ROADRUNNER} if arm == 'N' else set())):
            raise ValueError('vehicle arm inventory drift')
        result = run_vehicle(stage, report)
        samples[arm].append(result)
        print('::notice title=Vehicle-entity ablation trial::index=' + str(index) +
              ' arm=' + arm + ' 16_stationary_modded_smart_cars_confirmed=true '
              'clients=0 plugins=6 clean_stop=true DATA_WITHHELD_UNTIL_ALL_VALID', flush=True)
    if any(len(v) != 2 for v in samples.values()):
        raise ValueError('two samples per arm required')
    keys = ('cpu_s_30s', 'rss_mib', 'mean_tick_ms', 'boot_s_wall')
    compact = {arm: {key: [x[key] for x in values] for key in keys}
               for arm, values in samples.items()}
    print('::notice title=Stationary vehicle RoadRunner lab result::' + json.dumps({
        'order': ORDER, 'cars': VEHICLES,
        'arms': {'R': '28 mods with RoadRunner', 'N': '27 mods without RoadRunner'},
        'measurements': compact,
        'limits': '16 parked smart_car entities, generated platform/world; zero drivers, movement, '
                  'clients, network traffic, voice, city or 13-plugin stack; Forge mean != p95/p99; '
                  'two trials do not justify install/removal',
    }, separators=(',', ':')), flush=True)
    return compact


if __name__ == '__main__':
    try:
        if len(sys.argv) != 7:
            raise ValueError('exact runner root, official engine, archive, motor, core, guava required')
        main(*sys.argv[1:])
    except (OSError, ValueError, AssertionError, KeyError, zipfile.BadZipFile) as exc:
        print('::error title=Parked vehicle comparison rejected::PHASE=' + PHASE +
              ' CATEGORY=' + safe_failure_category(exc) +
              ' no private logs, paths or player data published; no rollout', file=sys.stderr)
        sys.exit(2)
