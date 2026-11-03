#!/usr/bin/env python3
"""Synthetic 28-for-28 dependency-safe replacement, no game or downloads."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fc_saturn_replacement_ab as ab
from fc_full28_memory_choice import FERRITE
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab_test import fake_jar
from fc_server_candidate_scan import CANDIDATES


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unsafe Saturn substitution accepted')


def main():
    with TemporaryDirectory() as d:
        root = Path(d)
        base = root/'stage'
        (base/'mods').mkdir(parents=True)
        (base/'plugins').mkdir()
        (base/'lab-world').mkdir()
        (base/'lab-world'/'level.dat').write_bytes(b'generated')
        (base/'eula.txt').write_text('true')
        os.mkfifo(base/'.fcbench-in')
        (base/'server.properties').write_text('\n'.join((
            'server-ip=127.0.0.1','online-mode=true','white-list=true',
            'view-distance=5','level-name=lab-world')))
        names = [FERRITE, 'obfuscate.jar', 'vehicle.jar'] + [f'content-{i}.jar' for i in range(25)]
        for i, n in enumerate(names):
            mid = 'obfuscate' if n == 'obfuscate.jar' else 'vehicle' if n == 'vehicle.jar' else f'mod{i}'
            (base/'mods'/n).write_bytes(fake_jar(mid, 'obfuscate' if n == 'vehicle.jar' else None))
        baseline = {p.name: sha(p) for p in (base/'mods').iterdir()}
        report = {'plugins': []}
        for i in range(6):
            p = base/'plugins'/f'p{i}.jar'
            p.write_bytes(bytes([i]))
            report['plugins'].append({'jar': p.name, 'sha256': sha(p)})
        saturn = root/CANDIDATES['saturn'][0]
        saturn.write_bytes(fake_jar('saturn'))
        expected = CANDIDATES['saturn'][:3] + (sha(saturn),)
        with patch.dict(ab.CANDIDATES, {'saturn': expected}):
            b = ab.prepare(base, root/'base', base/'lab-world', baseline, report, 'B', saturn)
            s = ab.prepare(base, root/'swap', base/'lab-world', baseline, report, 'S', saturn)
            assert len(list((b/'mods').iterdir())) == len(list((s/'mods').iterdir())) == 28
            assert not (s/'mods'/FERRITE).exists() and (s/'mods'/saturn.name).exists()
            assert (base/'mods'/FERRITE).exists() and not (s/'.fcbench-in').exists()
            reject(lambda: ab.prepare(base, root/'swap', base/'lab-world', baseline, report, 'S', saturn))
            with patch.dict(ab.CANDIDATES, {'saturn': expected[:3] + ('0'*64,)}):
                reject(lambda: ab.prepare(base, root/'invalid', base/'lab-world', baseline,
                                          report, 'S', saturn))
    data = {a: [{'heap_after_explicit_gc_mib': 320, 'boot_s_wall': 25,
                 'cpu_s_30s': 1, 'rss_mib': 1600, 'mean_tick_ms': 0.3}]*2 for a in ('B','S')}
    assert len(ab.summarize(data)) == 2
    reject(lambda: ab.summarize({'B': data['B'], 'S': data['S'][:1]}))
    print('PASS: pinned 28-for-28 memory substitution, same RP/dependencies, no stacking')


if __name__ == '__main__':
    main()
