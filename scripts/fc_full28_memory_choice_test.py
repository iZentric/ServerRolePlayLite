#!/usr/bin/env python3
"""Synthetic no-JVM guards for independent FerriteCore/ModernFix arms and heap."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_chunk_sending_canary import clone_clean_baseline
from fc_full28_memory_choice import ARMS, FERRITE, MODERN, parse_heap, summarize
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import validate_arm
from fc_rp_mod_cost_ab_test import fake_jar


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('bad memory experiment accepted')


def main():
    assert parse_heap('123:\ngarbage-first heap   total 524288K, used 262144K [0x...]') == 256
    reject(lambda: parse_heap('no G1 memory information'))
    assert set(ARMS) == {'B','F','M'} and ARMS['F'] == {FERRITE} and ARMS['M'] == {MODERN}
    with TemporaryDirectory() as t:
        root = Path(t)
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
        names = [FERRITE, MODERN] + [f'content-{i}.jar' for i in range(26)]
        for index, n in enumerate(names):
            (base/'mods'/n).write_bytes(fake_jar('mod' + str(index)))
        baseline = {n: sha(base/'mods'/n) for n in names}
        report = {'plugins': []}
        for i in range(6):
            p = base/'plugins'/f'plugin{i}.jar'
            p.write_bytes(bytes([i]))
            report['plugins'].append({'jar': p.name, 'sha256': sha(p)})
        for arm in ARMS:
            stage = root/arm
            clone_clean_baseline(base, stage)
            for name in ARMS[arm]:
                (stage/'mods'/name).unlink()
            validate_arm(stage, baseline, ARMS[arm], report)
            assert len(list((stage/'mods').iterdir())) == 28-len(ARMS[arm])
            assert not (stage/'.fcbench-in').exists() and (base/'mods'/FERRITE).exists()
        (root/'M'/'mods'/'content-0.jar').write_bytes(b'corrupt')
        reject(lambda: validate_arm(root/'M', baseline, ARMS['M'], report))
    row = {'boot_s_wall': 32, 'cpu_s_30s': 1.5, 'rss_mib': 1900,
           'mean_tick_ms': 0.5, 'heap_after_explicit_gc_mib': 750}
    assert len(summarize({k:[row,row] for k in ARMS})) == 3
    reject(lambda: summarize({'B':[row,row], 'F':[row], 'M':[row,row]}))
    print('PASS: same mod graph/6 plugins, independently removed MF/FC, G1 post-GC parser, complete report')


if __name__ == '__main__':
    main()
