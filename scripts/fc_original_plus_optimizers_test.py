#!/usr/bin/env python3
"""Fixture-only tests; no Windows profile or Minecraft is read or changed."""
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_original_plus_optimizers import assess


def main():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        original = root/'Freeroam 1.0.0'
        candidate = root/'FunCity RP Lite'
        a, b = original/'.minecraft'/'mods', candidate/'.minecraft'/'mods'
        a.mkdir(parents=True)
        b.mkdir(parents=True)
        original_jars = {'rp.jar': b'RP content', 'Clumps.jar': b'XP registry', 'voice.jar': b'voice'}
        for name, data in original_jars.items():
            (a/name).write_bytes(data)
            (b/name).write_bytes(data)
        (b/'rubidium-mc1.16.5-0.2.13.jar').write_bytes(b'optimizer placeholder')
        ok = assess(original, candidate)
        assert ok['original_preserved_by_sha'] and ok['eligible_for_compatibility_testing_only']
        assert ok['compatible_optimizers_added_by_name'] == ['rubidium-mc1.16.5-0.2.13.jar']
        (b/'Clumps.jar').unlink()
        missing = assess(original, candidate)
        assert missing['missing_original'] == ['Clumps.jar']
        assert not missing['eligible_for_compatibility_testing_only']
        (b/'Clumps.jar').write_bytes(b'XP registry')
        (b/'rp.jar').write_bytes(b'changed without permission')
        assert assess(original, candidate)['changed_original'] == ['rp.jar']
        (b/'rp.jar').write_bytes(b'RP content')
        (b/'unexpected.jar').write_bytes(b'not in optimizer allowlist')
        assert assess(original, candidate)['unexpected_additions'] == ['unexpected.jar']
        (b/'unexpected.jar').unlink()
        assert assess(original, candidate)['eligible_for_compatibility_testing_only']
        for name in original_jars:
            (a/name).unlink()
        assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
    print('PASS: preserve every original JAR SHA; reject missing/changed/unknown/empty; fixture only')


if __name__ == '__main__':
    main()
