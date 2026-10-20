#!/usr/bin/env python3
"""Fixture-only: no real JAR, Prism profile or Minecraft session is touched."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_original_plus_optimizers import DECLARED, POLICY, SELECTION, assess

EXPECTED_EXCLUSIONS = {
    'CTM-MC1.16.1-1.1.2.6.jar',
    'DynamicSurroundings-1.16.5-4.0.5.0.jar',
    'InGameAccountSwitcher-Forge-1.16-8.0.1.jar',
    'lightfallclient-1.0.0.jar',
    'TRansliterationLib-1.0.4.jar',
    'notenoughanimations-1.2.4.jar',
}
LIBRARY = 'TRansliterationLib-1.0.4.jar'
ANIMATIONS = 'notenoughanimations-1.2.4.jar'


def main():
    declared = json.loads(DECLARED.read_text(encoding='utf-8'))['jar_names']
    policy = json.loads(POLICY.read_text(encoding='utf-8'))
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    assert len(declared) == len(set(declared)) == 28
    assert len({name.casefold() for name in declared}) == 28
    assert all(name.endswith('.jar') for name in declared)
    assert set(policy['performance_candidates_for_active_game']) == set(policy['already_in_declared_list'])
    assert not policy['approved_additions']
    assert set(policy['approved_exclusions_from_future_lite']) == EXPECTED_EXCLUSIONS
    assert set(selection['removed_from_future_target']) == EXPECTED_EXCLUSIONS
    assert len(selection['retained_in_future_target']) == 22
    assert set(selection['retained_in_future_target']) == set(declared) - EXPECTED_EXCLUSIONS
    assert {LIBRARY, ANIMATIONS}.isdisjoint(selection['retained_in_future_target'])
    assert {LIBRARY, ANIMATIONS} <= set(selection['removed_from_future_target'])
    assert 'voicechat-forge-1.16.5-2.3.23.jar' in selection['retained_in_future_target']
    assert not selection['ready_for_release']
    assert selection['requested_prism_destination'] == 'Freeroam 1.0.0'
    assert selection['installation_performed'] is False
    assert policy['installation_state'].startswith('BLOCKED_')
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
            # Synthetic bytes: no actual mod SHA, compatibility or user inventory asserted.
            (a/name).write_bytes(('fixture:'+name).encode())
            if name not in EXPECTED_EXCLUSIONS:
                (b/name).write_bytes(('fixture:'+name).encode())
        ok = assess(original, candidate)
        assert ok['original_jar_count'] == 28 and ok['candidate_jar_count'] == 22
        assert ok['declared_matches_disk_names'] and ok['retained_original_sha_unchanged']
        assert ok['exactly_six_approved_exclusions'] and ok['eligible_for_compatibility_testing_only']
        assert not ok['ready_for_release'] and not ok['unapproved_missing_original']
        assert ok['missing_original'] == sorted(EXPECTED_EXCLUSIONS)
        for new in policy['deferred_not_installed']:
            (b/new).write_bytes(b'not approved for addition')
            assert assess(original, candidate)['unexpected_additions'] == [new]
            assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
            (b/new).unlink()
        for kept in ('voicechat-forge-1.16.5-2.3.23.jar', 'mapperbase-1.16.5-2.4.0.0.jar'):
            (b/kept).unlink()
            result = assess(original, candidate)
            assert result['unapproved_missing_original'] == [kept]
            assert not result['eligible_for_compatibility_testing_only']
            (b/kept).write_bytes(('fixture:'+kept).encode())
        voice = 'voicechat-forge-1.16.5-2.3.23.jar'
        (b/voice).write_bytes(b'changed without permission')
        assert assess(original, candidate)['changed_original'] == [voice]
        assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
        (b/voice).write_bytes(('fixture:'+voice).encode())
        (b/'unexpected.jar').write_bytes(b'unknown fixture')
        assert assess(original, candidate)['unexpected_additions'] == ['unexpected.jar']
        (b/'unexpected.jar').unlink()
        (a/'extra-original.jar').write_bytes(b'fixture')
        (b/'extra-original.jar').write_bytes(b'fixture')
        mismatch = assess(original, candidate)
        assert mismatch['unlisted_original'] == ['extra-original.jar']
        assert mismatch['retained_original_sha_unchanged'] and not mismatch['eligible_for_compatibility_testing_only']
        (a/'extra-original.jar').unlink()
        (b/'extra-original.jar').unlink()
        for removed in EXPECTED_EXCLUSIONS:
            (b/removed).write_bytes(('fixture:'+removed).encode())
            assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
            (b/removed).unlink()
        (a/voice).unlink()
        assert assess(original, candidate)['declared_missing_in_original'] == [voice]
        for name in declared:
            (a/name).unlink(missing_ok=True)
        assert not assess(original, candidate)['eligible_for_compatibility_testing_only']
    print('PASS: 28 declared / 22 target, six authorized exclusions incl. dependency pair (synthetic)')


if __name__ == '__main__':
    main()
