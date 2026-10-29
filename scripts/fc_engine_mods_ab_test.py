#!/usr/bin/env python3
"""Synthetic Java-engine swap only; no download, server or PC."""
from pathlib import Path
import tempfile
from unittest.mock import patch

import fc_engine_mods_ab as ab
from fc_engine_family_lab import ENGINES


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unsafe trial accepted')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        stage = root/'stage'
        world = root/'world-base'
        (stage/'mods').mkdir(parents=True)
        (stage/'plugins').mkdir()
        (stage/'mods'/'keep-rp.jar').write_bytes(b'RP unchanged')
        (stage/'plugins'/'keep-plugin.jar').write_bytes(b'PLUGIN unchanged')
        (stage/ab.BOOT_JAR).write_bytes(b'FunCity candidate')
        world.mkdir()
        (world/'level.dat').write_bytes(b'generated-world')
        hashes = {b'FunCity candidate': ENGINES['funcity'][3],
                  b'CatServer old': ENGINES['catserver-old'][3],
                  b'CatServer official': ENGINES['catserver-official'][3]}

        def fake_engine(name, source):
            return {'catserver-old': b'CatServer old',
                    'catserver-official': b'CatServer official'}[name]

        def fake_sha(path):
            return hashes[Path(path).read_bytes()]

        with patch.object(ab, 'source_engine', side_effect=fake_engine), patch.object(ab, 'sha', side_effect=fake_sha):
            for label, binary in [('F', b'FunCity candidate'), ('C', b'CatServer old'),
                                  ('O', b'CatServer official')]:
                result = ab.copy_arm(stage, root/('trial-'+label), world, label, 'old.zip', 'official.jar')
                assert (result/ab.BOOT_JAR).read_bytes() == binary
                assert (result/'mods'/'keep-rp.jar').read_bytes() == b'RP unchanged'
                assert (result/'plugins'/'keep-plugin.jar').read_bytes() == b'PLUGIN unchanged'
                assert (result/'lab-world'/'level.dat').read_bytes() == b'generated-world'
            reject(lambda: ab.copy_arm(stage, root/'bad-arm', world, 'X', '', ''))
        assert ab.ORDER == 'FCOOCF'
        print('PASS: exact engine swap, unchanged RP/plugins/world, unknown engine refused')


if __name__ == '__main__':
    main()
