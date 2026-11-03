#!/usr/bin/env python3
"""Bounded hosted boot of UNAPPROVED modded candidate; not player compatibility."""
import json
import os
from pathlib import Path
import re
import sys
import time

from fc_bench import JvmRun
from fc_modded_candidate import CHOSEN, PERFORMANCE
from fc_plugin_first_stage import ENGINE_SHA, GUAVA21_SHA, sha


def run(stage):
    stage = Path(stage).resolve()
    temp = os.environ.get('RUNNER_TEMP')
    if not temp or not stage.is_relative_to(Path(temp).resolve()) or stage.name != 'stage':
        raise ValueError('only isolated hosted runner temp stage allowed')
    report = json.loads((stage/'stage-report.json').read_text())
    entries = report['server_mods']
    expected = set(CHOSEN + tuple(report['server_optimizers']))
    if report['server_optimizers'] not in ([], list(PERFORMANCE)):
        raise ValueError('unknown performance selection')
    if (report['scope'] != 'UNRELEASED local modded compatibility experiment; ownership unverified' or
            {m['jar'] for m in entries} != expected or len(entries) != len(expected) or
            {p.name for p in (stage/'mods').iterdir()} != expected or
            any(sha(stage/'mods'/m['jar']) != m['sha256'] for m in entries) or
            sha(stage/'FunCity-1.16.5-b1.0827.jar') != ENGINE_SHA or
            sha(stage/'runtime/guava-21.0.jar') != GUAVA21_SHA or
            len(report['plugins']) != 6 or
            any(sha(stage/'plugins'/p['jar']) != p['sha256'] for p in report['plugins'])):
        raise ValueError('unverified modded lab inventory')
    props = (stage/'server.properties').read_text().splitlines()
    if not {'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true'} <= set(props):
        raise ValueError('lab must stay loopback only')
    if (stage/'eula.txt').exists() or (stage/'lab-world').exists():
        raise ValueError('refuse existing world/server')
    (stage/'eula.txt').write_text('eula=true\n')  # disposable hosted runner only
    log = stage/'modded-boot.log'
    j = JvmRun(str(stage), 'FunCity-1.16.5-b1.0827.jar',
               ['-Xbootclasspath/a:' + str(stage/'runtime/guava-21.0.jar'),
                '-Xms512M', '-Xmx3G'], str(log))
    j.port = 25565
    try:
        j.start()
        ready = j.wait_done(480)
        if ready:
            time.sleep(5)
        text = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
        if not ready:
            clues = [line for line in text.splitlines() if any(
                marker in line.lower() for marker in ('error', 'exception', 'missing', 'failed'))]
            sample = re.sub(r'[^a-zA-Z0-9 ._+:/()=-]', '_', ' | '.join(clues[-8:]))[-1200:]
            print('::error title=Modded lab boot failure::' + sample)
            raise ValueError('modded lab did not reach Done; exit=' + str(j.p.poll()))
        missing = [p['declared_name'] for p in report['plugins'] if not re.search(
            r'Enabling ' + re.escape(p['declared_name']) + r' (?:v|\d)', text)]
        critical = [line for line in text.splitlines() if any(
            marker in line for marker in ('Could not load plugin', 'Error occurred while enabling',
                                           'Exception in server tick loop', 'Failed to start'))]
        stopped = j.stop(70)
        if missing or critical or stopped != 'CLEAN':
            raise ValueError(f'missing plugins={missing}, critical_lines={len(critical)}, stop={stopped}')
        print('::notice title=FunCity MODDED closed boot::Done=true server_mods=' +
              str(len(expected)) + ' active_plugins=' +
              ','.join(p['declared_name'] for p in report['plugins']) +
              ' performance_mods=' + str(len(report['server_optimizers'])) +
              ' ownership=UNVERIFIED '
              'NO client join, RP, auth, voice or performance claim')
    finally:
        if getattr(j, 'p', None) is not None and j.p.poll() is None:
            j.stop(15)
        j.close()


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('expected fresh hosted stage')
        run(sys.argv[1])
    except (ValueError, KeyError, OSError) as exc:
        print('RESPINS:', exc, file=sys.stderr)
        sys.exit(2)
