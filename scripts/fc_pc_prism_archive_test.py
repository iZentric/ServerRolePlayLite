#!/usr/bin/env python3
"""Synthetic eight-profile inventory with a protected world and screenshot."""
from pathlib import Path
import tempfile

from fc_pc_prism_archive import FAB, LITE, archive_profiles


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/'PrismLauncher'/'instances'
        root.mkdir(parents=True)
        names = (LITE, 'EGK RP', 'V RP', FAB, 'FunCity', 'FunCity-1.0.0 (3)',
                 'Historical client', 'Legacy gameplay')
        for name in names:
            (root/name).mkdir()
        world = root/'Historical client'/'.minecraft'/'saves'/'important-world'
        world.mkdir(parents=True)
        (world/'level.dat').write_bytes(b'preserve private test world')
        screenshot = root/'FunCity'/'.minecraft'/'screenshots'
        screenshot.mkdir(parents=True)
        (screenshot/'test.png').write_bytes(b'preserve screenshot')
        assert archive_profiles(root, '39331442750')['status'] == 'eligible'
        assert len(list(root.iterdir())) == 8
        status = archive_profiles(root, '39331442750', apply=True)
        assert status['status'] == 'archived' and status['archived'] == 4
        assert {p.name for p in root.iterdir()} == {LITE, 'EGK RP', 'V RP', FAB}
        backup = root.parent/'Arena-Archived-Instances'/'39331442750'
        assert (backup/'Historical client'/'.minecraft'/'saves'/'important-world'/'level.dat').read_bytes() == b'preserve private test world'
        assert (backup/'FunCity'/'.minecraft'/'screenshots'/'test.png').read_bytes() == b'preserve screenshot'
        assert (backup/'RESTORE.txt').exists()
        try:
            archive_profiles(root, '39331442751', apply=True)
        except ValueError as exc:
            assert 'inventory' in str(exc)
        else:
            raise AssertionError('unexpected second cleanup allowed')
    print('PASS: four requested Prism profiles kept; other four archived with worlds/screenshots intact')


if __name__ == '__main__':
    main()
