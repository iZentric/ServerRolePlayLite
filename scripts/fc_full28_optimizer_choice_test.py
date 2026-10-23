#!/usr/bin/env python3
"""No downloaded JAR, PC or game launch: SHA, exact 28-for-28 swap, graph."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fc_full28_optimizer_choice as choice
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab_test import fake_jar
from fc_server_optimizer_ab import PERFORMANT, ROADRUNNER


def reject(fn):
    try:
        fn()
    except (ValueError, AssertionError):
        return
    raise AssertionError('invalid optimization candidate accepted')


def main():
    with TemporaryDirectory() as d:
        root = Path(d)
        template = root/'stage'
        (template/'mods').mkdir(parents=True)
        (template/'plugins').mkdir()
        (template/'lab-world').mkdir()
        (template/'lab-world'/'level.dat').write_bytes(b'world')
        (template/'eula.txt').write_text('true')
        os.mkfifo(template/'.fcbench-in')
        (template/'server.properties').write_text('\n'.join((
            'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world')))
        names = [ROADRUNNER, 'obfuscate.jar', 'vehicle.jar'] + [f'mod-{i}.jar' for i in range(25)]
        for i, name in enumerate(names):
            modid, dependency = ('obfuscate', None) if name == 'obfuscate.jar' else (
                ('vehicle', 'obfuscate') if name == 'vehicle.jar' else ('rr' if i == 0 else f'mod{i}', None))
            (template/'mods'/name).write_bytes(fake_jar(modid, dependency))
        baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
        assert len(baseline) == 28
        report = {'plugins': []}
        for i in range(6):
            p = template/'plugins'/f'p{i}.jar'
            p.write_bytes(bytes([i]))
            report['plugins'].append({'jar': p.name, 'sha256': sha(p)})
        perf = root/PERFORMANT
        perf.write_bytes(fake_jar('performant'))
        with patch.object(choice, 'PERFORMANT_SHA', sha(perf)):
            assert choice.check_performant(root, perf) == perf
            reject(lambda: choice.check_performant(root, template/'mods'/ROADRUNNER))
            r = choice.prepare(template, root/'arm-R', template/'lab-world',
                               baseline, report, 'R', perf)
            p = choice.prepare(template, root/'arm-P', template/'lab-world',
                               baseline, report, 'P', perf)
            assert len(list((p/'mods').iterdir())) == len(list((r/'mods').iterdir())) == 28
            assert (r/'mods'/ROADRUNNER).is_file() and not (p/'mods'/ROADRUNNER).exists()
            assert (p/'mods'/PERFORMANT).is_file() and not (r/'mods'/PERFORMANT).exists()
            assert (template/'mods'/ROADRUNNER).is_file()  # source unchanged
            assert not (p/'.fcbench-in').exists() and (p/'lab-world'/'level.dat').is_file()
            reject(lambda: choice.prepare(template, root/'arm-P', template/'lab-world',
                                          baseline, report, 'P', perf))
            with patch.object(choice, 'PERFORMANT_SHA', '0'*64):
                reject(lambda: choice.check_performant(root, perf))
        bad = {'R': [{'summons_confirmed': 80}], 'P': []}
        reject(lambda: choice.summarize(bad))
    print('PASS: exact pinned author mod, 28-for-28 swap, graph, world, six plugins, safety')


if __name__ == '__main__':
    main()
