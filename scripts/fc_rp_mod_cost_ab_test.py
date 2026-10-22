#!/usr/bin/env python3
"""Synthetic only: dependencies, frozen world, exclusion isolation, report gating."""
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab import AI, ARMS, KSYXIS, RECIPES, prepare_arm, summarize


def fake_jar(mod_id, dependency=None):
    with io.BytesIO() as stream:
        with ZipFile(stream, 'w') as z:
            toml = '[[mods]]\nmodId="' + mod_id + '"\nversion="1"\n'
            if dependency:
                toml += '[[dependencies.' + mod_id + ']]\nmodId="' + dependency + (
                    '"\nmandatory=true\nversionRange="[1,)"\nordering="NONE"\nside="BOTH"\n')
            z.writestr('META-INF/mods.toml', toml)
        return stream.getvalue()


def reject(fn):
    try:
        fn()
    except (ValueError, AssertionError):
        return
    raise AssertionError('unsafe or incomplete comparison passed')


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        base = root/'baseline'
        (base/'mods').mkdir(parents=True)
        (base/'plugins').mkdir()
        (base/'server.properties').write_text('\n'.join((
            'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world')))
        (base/'eula.txt').write_text('true')
        (base/'private-benchmark.log').write_text('do not copy')
        os.mkfifo(base/'.fcbench-in')
        world = base/'lab-world'
        world.mkdir()
        (world/'level.dat').write_bytes(b'frozen')
        mods = {AI: fake_jar('aiimprovements'), KSYXIS: fake_jar('ksyxis'),
                'FastSuite-1.16.4-1.1.1.jar': fake_jar('fastsuite', 'placebo'),
                'FastWorkbench-1.16.5-4.6.2.jar': fake_jar('fastworkbench', 'placebo'),
                'Placebo-1.16.5-4.7.1.jar': fake_jar('placebo'),
                'vehicle.jar': fake_jar('vehicle')}
        assert RECIPES <= set(mods)
        for name, raw in mods.items():
            (base/'mods'/name).write_bytes(raw)
        baseline = {name: sha(base/'mods'/name) for name in mods}
        report = {'plugins': []}
        # Synthetic graph has no plugins; test graph in isolation then strict six-plugin gate.
        for index in range(6):
            p = base/'plugins'/('plugin' + str(index) + '.jar')
            p.write_bytes(b'plugin' + bytes([index]))
            report['plugins'].append({'jar': p.name, 'sha256': sha(p)})
        for arm, removed in ARMS.items():
            trial = prepare_arm(base, root/('arm-' + arm), world, baseline, arm, report)
            assert {p.name for p in (trial/'mods').iterdir()} == set(mods) - set(removed)
            assert (trial/'lab-world'/'level.dat').read_bytes() == b'frozen'
            assert not (trial/'.fcbench-in').exists()
            assert not (trial/'private-benchmark.log').exists()
            assert (base/'mods'/AI).is_file()  # never edit the source
        (root/'arm-R'/'mods'/'vehicle.jar').write_bytes(b'corrupt')
        reject(lambda: prepare_arm(base, root/'arm-R', world, baseline, 'R', report))
        bad = dict(baseline)
        bad.pop('Placebo-1.16.5-4.7.1.jar')
        reject(lambda: prepare_arm(base, root/'bad', world, bad, 'A', report))
        reject(lambda: prepare_arm(base, root/'bad2', world, baseline, '?', report))
        reject(lambda: summarize({'A': [{}], 'I': [], 'R': [], 'K': []}))
        sample = dict(boot_s_wall=30, cpu_s=2, rss_mib=2100,
                      mean_mspt_from_forge_tps=1.5, summons_confirmed=80)
        good = {arm: [sample, sample] for arm in ARMS}
        assert len(summarize(good)) == 4
        good['A'][0] = dict(sample, summons_confirmed=0)
        reject(lambda: summarize(good))
    print('PASS: four dependency-safe arms, FIFO/world isolation, exact inventory, six plugins, report guards')


if __name__ == '__main__':
    main()
