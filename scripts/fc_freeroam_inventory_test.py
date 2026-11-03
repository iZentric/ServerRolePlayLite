#!/usr/bin/env python3
"""Synthetic, isolated regression tests; never reads a real Prism profile."""
from pathlib import Path
import tempfile

from fc_freeroam_inventory import compare, inventory


def rejected(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError('unsafe Prism inventory accepted')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        old, low = root/'Freeroam 1.0.0', root/'LowSpec'
        original = old/'.minecraft'/'mods'
        selected = low/'minecraft'/'mods'
        original.mkdir(parents=True)
        selected.mkdir(parents=True)
        (original/'rp.jar').write_bytes(b'original content')
        (original/'same.jar').write_bytes(b'same')
        (original/'changed.jar').write_bytes(b'old')
        (selected/'rp.jar').write_bytes(b'original content')
        (selected/'same.jar').write_bytes(b'same')
        (selected/'changed.jar').write_bytes(b'new')
        (selected/'added.jar').write_bytes(b'new extra')
        (old/'.minecraft'/'saves').mkdir()
        (old/'.minecraft'/'saves'/'private-world').write_bytes(b'not read')
        got = compare(old, low)
        assert got == {'original_count': 3, 'lowspec_count': 4,
                       'same_bytes': 2, 'changed_sha': ['changed.jar'],
                       'original_only': [], 'lowspec_only': ['added.jar']}
        (selected/'rp.jar').unlink()
        assert compare(old, low)['original_only'] == ['rp.jar']
        rejected(lambda: inventory(root/'missing'))
        (original/'linked.jar').symlink_to(root/'private.txt')
        rejected(lambda: inventory(old))
        (original/'linked.jar').unlink()
        (original/'another-mods.txt').write_text('untouched')
        assert len(inventory(old)) == 3
        (old/'minecraft'/'mods').mkdir(parents=True)
        rejected(lambda: inventory(old))  # never guess between two locations
    print('PASS: read-only inventory, byte equality, missing/changed JARs, symlink and ambiguity guards')


if __name__ == '__main__':
    main()
