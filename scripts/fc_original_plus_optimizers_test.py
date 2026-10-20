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
    assert set(policy['already_in_declared_list']) <= set(declared)
    assert set(policy['performance_candidates_for_active_game']) - set(declared) == {
        policy['only_new_performance_candidate_by_name']}
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
        new = policy['only_new_performance_candidate_by_name']
        (b/new).write_bytes(b'optimizer fixture')
        ok = assess(original, candidate)
        assert ok['original_jar_count'] == 28 and ok['candidate_jar_count'] == 29
        assert ok['declared_matches_disk_names'] and ok['original_preserved_by_sha']
        assert ok['optimizers_added_by_name'] == [new]
        assert ok['eligible_for_compatibility_testing_only']
        voice = 'voicechat-forge-1.16.5-2.3.23.jar'
        (b/voice).unlink()
        assert assess(original, candidate)['missing_original'] == [voice]
        (b/voice).write_bytes(('fixture:'+voice).encode())
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
    print('PASS: 28 declared names, 3 existing optimizers, 1 optional new; only synthetic SHA preservation')


if __name__ == '__main__':
    main()
