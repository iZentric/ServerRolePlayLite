#!/usr/bin/env python3
"""Synthetic path/optimizer isolation checks; never boot, download or touch PC."""
import os
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

from fc_modded_candidate import CHOSEN, PERFORMANCE
from fc_server_optimizer_ab import (PERFORMANT, ROADRUNNER, check_log,
                                    guard, make_arm)


def denied(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError('unsafe input was accepted')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        lab = root/'fc-server-optimizer-ab'
        stage = lab/'stage'
        (stage/'mods').mkdir(parents=True)
        for name in CHOSEN + PERFORMANCE:
            (stage/'mods'/name).write_bytes(name.encode())
        original = {p.name: p.read_bytes() for p in (stage/'mods').iterdir()}
        performant = lab/PERFORMANT
        with zipfile.ZipFile(performant, 'w') as z:
            z.writestr('META-INF/mods.toml', '[[mods]]\nmodId="performant"\nversion="4.1m"\n')
        with patch.dict(os.environ, {'RUNNER_TEMP': str(root)}):
            denied(lambda: guard(root, stage, '-'))
            denied(lambda: guard(lab, lab/'not-a-stage', '-'))
        world = lab/'world-base'
        world.mkdir()
        (world/'level.dat').write_bytes(b'synthetic-level-not-private')
        arms = {}
        for name in 'RPN':
            arm = make_arm(stage, lab/f'arm-{name}', world, name, performant)
            jars = {p.name: p.read_bytes() for p in (arm/'mods').iterdir()}
            assert {p.name for p in (arm/'lab-world').iterdir()} == {'level.dat'}
            assert all(jars[p] == content for p, content in original.items() if p != ROADRUNNER)
            arms[name] = jars
        assert ROADRUNNER in arms['R'] and PERFORMANT not in arms['R']
        assert ROADRUNNER not in arms['P'] and PERFORMANT in arms['P']
        assert ROADRUNNER not in arms['N'] and PERFORMANT not in arms['N']
        assert all(len(arms[a]) == len(CHOSEN) + 2 + (a != 'N') for a in 'RPN')
        denied(lambda: make_arm(stage, lab/'bad', world, 'X', performant))
        report = {'plugins': [{'declared_name': 'CoreProtect'}, {'declared_name': 'Vault'}]}
        check_log('Enabling CoreProtect v21.2\nEnabling Vault v1.7', report)
        denied(lambda: check_log('Enabling Vault v1.7', report))
        denied(lambda: check_log('Enabling CoreProtect v21.2\nEnabling Vault v1.7\n'
                                 'Exception in server tick loop', report))
        print('PASS: no PC path, exact optimizer swap, unchanged RP files, isolated world, fatal guard')


if __name__ == '__main__':
    main()
