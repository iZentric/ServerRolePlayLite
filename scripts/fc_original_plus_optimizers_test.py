#!/usr/bin/env python3
"""Fixture-only tests: neither Prism nor a real Minecraft JAR is read."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_original_plus_optimizers import DECLARED, POLICY, assess


def main():
    declared = json.loads(DECLARED.read_text(encoding='utf-8'))['jar_names']
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    assert len(declared) == len(set(declared)) == 28
    assert len({name.casefold() for name in declared}) == 28
    assert all(name.endswith('.jar') for name in declared)
    assert 'voicechat-forge-1.16.5-2.3.23.jar' in declared
    assert 'InGameAccountSwitcher-Forge-1.16-8.0.1.jar' in declared
    assert set(policy['performance_candidates_for_active_game']) == set(policy['already_in_declared_list'])
    assert not policy['approved_additions']
    assert set(policy['deferred_not_installed']) == {
        'entityculling-forge-mc1.16.5-1.5.2.jar', 'embeddium-0.3.18+mc1.16.5.jar'}
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        original = root/'Freeroam 1.0.0'
        candidate = root/'FunCity RP Lite'
        a, b = original/'.minecraft'/'mods', candidate/'.minecraft'/'mods'
        a.mkdir(parents=True)
        b.mkdir(parents=True)
        for name in declared:
            # Synthetic bytes only; this does not verify any actual JAR SHA.
            (a/name).write_bytes(('fixture:'+name).encode())
            (b/name).write_bytes(('fixture:'+name).encode())
        ok = assess(original, candidate)
        assert ok['original_jar_count'] == ok['candidate_jar_count'] == 28
        assert ok['declared_matches_disk_names'] and ok['original_preserved_by_sha']
        assert ok['optimizers_added_by_name'] == []
        assert ok['eligible_for_compatibility_testing_only']
        for new in policy['deferred_not_installed']:
            (b/new).write_bytes(b'not approved for addition')
            assert assess(original, candidate)['unexpected_additions'] == [new]
            (b/new).unlink()
        voice = 'voicechat-forge-1.16.5-2.3.23.jar'
        (b/voice).unlink()
        assert assess(original, candidate)['missing_original'] == [voice]
        (b/voice).write_bytes(b'changed without permission')
        assert assess(original, candidate)['changed_original'] == [voice]
        (b/voice).write_bytes(('fixture:'+voice).encode())
        (b/'unexpected.jar').write_bytes(b'unknown fixture')
        assert assess(original, candidate)['unexpected_additions'] == ['unexpected.jar']
        (b/'unexpected.jar').unlink()
        (a/'extra-original.jar').write_bytes(b'fixture')
        (b/'extra-original.jar').write_bytes(b'fixture')
        mismatch = assess(original, candidate)
        assert mismatch['unlisted_original'] == ['extra-original.jar']
        assert mismatch['original_preserved_by_sha'] and not mismatch['eligible_for_compatibility_testing_only']
        (a/'extra-original.jar').unlink()
        (b/'extra-original.jar').unlink()
        (a/voice).unlink()
        assert assess(original, candidate)['declared_missing_in_original'] == [voice]
        for name in declared:
            (a/name).unlink(missing_ok=True)
        assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
    print('PASS: 28 declared names, 0 additions approved; reject new mods, removals or SHA changes (synthetic)')


if __name__ == '__main__':
    main()
