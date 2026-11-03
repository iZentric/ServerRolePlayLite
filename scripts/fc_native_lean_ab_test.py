#!/usr/bin/env python3
"""Synthetic 28->22 selection/graph/unchanged source; never boots a server."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_native_lean_ab import prepare, read_decision, summarize
from fc_plugin_first_stage import sha
from fc_rp_mod_cost_ab_test import fake_jar


def denied(fn):
    try:
        fn()
    except (ValueError, KeyError):
        return
    raise AssertionError('unsafe lean selection or metric accepted')


def main():
    chosen, removed = read_decision('agent/FUNCITY-SERVER-LEAN-22.json')
    assert len(chosen) == 22 and len(removed) == 6
    assert 'Placebo-1.16.5-4.7.1.jar' in removed
    assert 'vehicle-mod-0.45.2-1.16.5 (1).jar' in chosen
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        decision = json.loads(Path('agent/FUNCITY-SERVER-LEAN-22.json').read_text())
        decision['keep'].remove('vehicle-mod-0.45.2-1.16.5 (1).jar')
        corrupt = tmp/'corrupt.json'
        corrupt.write_text(json.dumps(decision))
        denied(lambda: read_decision(corrupt))
        base = tmp/'stage'
        (base/'mods').mkdir(parents=True)
        (base/'plugins').mkdir()
        (base/'lab-world').mkdir()
        (base/'lab-world'/'level.dat').write_bytes(b'generated world')
        (base/'eula.txt').write_text('true')
        os.mkfifo(base/'.fcbench-in')
        (base/'server.properties').write_text('\n'.join((
            'server-ip=127.0.0.1', 'online-mode=true', 'white-list=true',
            'view-distance=5', 'level-name=lab-world')))
        baseline = {}
        for index, name in enumerate(sorted(chosen | removed)):
            dep = ('placebo' if name.startswith(('FastSuite-', 'FastWorkbench-')) else
                   'obfuscate' if name.startswith('vehicle-mod-') else None)
            mod_id = ('placebo' if name.startswith('Placebo-') else
                      'obfuscate' if name.startswith('obfuscate-') else
                      'mod' + str(index))
            p = base/'mods'/name
            p.write_bytes(fake_jar(mod_id, dep))
            baseline[name] = sha(p)
        report = {'plugins': []}
        for index in range(6):
            p = base/'plugins'/('plugin' + str(index) + '.jar')
            p.write_bytes(bytes([index]))
            report['plugins'].append({'jar': p.name, 'sha256': sha(p)})
        lean = prepare(base, tmp/'lean', base/'lab-world', baseline, report, chosen)
        assert {p.name for p in (lean/'mods').iterdir()} == chosen
        assert (lean/'lab-world'/'level.dat').read_bytes() == b'generated world'
        assert not (lean/'.fcbench-in').exists()
        assert (base/'mods'/'FastSuite-1.16.4-1.1.1.jar').exists()
        denied(lambda: prepare(base, tmp/'lean', base/'lab-world', baseline, report, chosen))
        # Placebo cannot be removed alone while recipes depend on it.
        without_placebo = (chosen | removed) - {'Placebo-1.16.5-4.7.1.jar'}
        denied(lambda: prepare(base, tmp/'unsafe', base/'lab-world', baseline,
                               report, without_placebo))
    sample = {'boot_s_wall': 35, 'cpu_s': 2, 'rss_mib': 1900,
              'mean_mspt_from_forge_tps': 0.5, 'summons_confirmed': 80}
    assert len(summarize({'F': [sample, sample], 'L': [sample, sample]})) == 2
    denied(lambda: summarize({'F': [sample, sample], 'L': [sample]}))
    denied(lambda: summarize({'F': [sample, sample], 'L': [sample, dict(sample, summons_confirmed=0)]}))
    print('PASS: exact 22 choice, RP anchor, graph, isolated source, six plugins, metric gates')


if __name__ == '__main__':
    main()
