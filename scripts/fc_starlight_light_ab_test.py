#!/usr/bin/env python3
"""Synthetic closed inventory and exact 24*1024 block-change gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fc_starlight_light_ab as ab
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab_test import fake_jar


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unverified light workload accepted')


def main():
    commands = ab.workload()
    assert len(commands) == 6 + ab.TOGGLES*2 + 4
    assert sum('execute store result score #last' in x for x in commands) == 24
    assert sum('minecraft:glowstone' in x for x in commands) == 12
    assert sum('minecraft:stone' in x for x in commands) == 14  # warmup + 12 toggles + final persisted-block check
    confirmed = '#writes has 24576 [fcbench]\n#end has 1 [fcbench]\nFCBENCH_LIGHT_COMPLETE'
    ab.confirm(confirmed)
    reject(lambda: ab.confirm(confirmed.replace('24576','24575')))
    reject(lambda: ab.confirm(confirmed.replace('#end has 1','#end has 0')))
    with TemporaryDirectory() as d:
        root = Path(d)
        template = root/'stage'
        (template/'mods').mkdir(parents=True)
        (template/'plugins').mkdir()
        (template/'lab-world').mkdir()
        (template/'lab-world'/'level.dat').write_bytes(b'generated')
        (template/'server.properties').write_text('\n'.join((
            'server-ip=127.0.0.1','online-mode=true','white-list=true',
            'view-distance=5','level-name=lab-world')))
        for i in range(28):
            (template/'mods'/f'mod{i}.jar').write_bytes(fake_jar(f'mod{i}'))
        baseline = {p.name: sha(p) for p in (template/'mods').iterdir()}
        report = {'plugins': []}
        for i in range(6):
            f = template/'plugins'/f'plugin{i}.jar'
            f.write_bytes(bytes([i]))
            report['plugins'].append({'jar': f.name, 'sha256': sha(f)})
        candidate = root/ab.FILE
        candidate.write_bytes(fake_jar('starlight'))
        with patch.object(ab, 'SHA256', sha(candidate)):
            b = ab.prepare(template, root/'trial-B', template/'lab-world',
                           baseline, report, candidate)
            s = ab.prepare(template, root/'trial-S', template/'lab-world',
                           baseline, report, candidate)
            assert len(list((b/'mods').iterdir())) == 28
            assert len(list((s/'mods').iterdir())) == 29
            assert (template/'mods'/next(iter(baseline))).is_file()
            reject(lambda: ab.prepare(template, root/'trial-S', template/'lab-world',
                                      baseline, report, candidate))
    good = {'command_ack_wall_s': 10, 'cpu_s_plus_12s_settle': 3,
            'rss_mib_after_settle': 1900, 'actual_changed_blocks': 24576}
    ab.summarize({'B':[good,good], 'S':[good,good]})
    reject(lambda: ab.summarize({'B':[good,good], 'S':[good]}))
    print('PASS: SHA-pinned closed 28/29 inventory, equal light writes and 2+2 samples')


if __name__ == '__main__':
    main()
