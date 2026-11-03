#!/usr/bin/env python3
"""Synthetic safety checks for the read-only Freeroam installation preflight."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from fc_freeroam_target_preflight import DECLARED, EXPECTED_EXCLUSIONS, SELECTION, check, main


def main_test():
    names = json.loads(DECLARED.read_text(encoding='utf-8'))['jar_names']
    selection = json.loads(SELECTION.read_text(encoding='utf-8'))
    assert len(names) == 28 and len(EXPECTED_EXCLUSIONS) == 6
    assert set(selection['removed_from_future_target']) == EXPECTED_EXCLUSIONS
    assert set(selection['retained_in_future_target']) == set(names) - EXPECTED_EXCLUSIONS
    with TemporaryDirectory() as temp:
        profile = Path(temp)/'Freeroam 1.0.0'
        mods = profile/'.minecraft'/'mods'
        mods.mkdir(parents=True)
        for name in names:
            (mods/name).write_bytes(('fixture:'+name).encode())
        before = {name: (mods/name).read_bytes() for name in names}
        ok = check(profile)
        assert ok == {'pass': True, 'original_jar_count': 28,
                      'declared_missing_count': 0, 'unexpected_jar_count': 0,
                      'approved_exclusions_present_count': 6,
                      'remaining_target_count_if_inventory_matches': 22,
                      'installation_performed': False}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert main(['--profile', str(profile)]) == 0
        assert 'INSTALLATION=false' in out.getvalue()
        assert str(profile) not in out.getvalue() and all(name not in out.getvalue() for name in names)
        assert {name: (mods/name).read_bytes() for name in names} == before
        # An extra original JAR is a blocker, not something to delete to force 28.
        extra = mods/'extra-original.jar'
        extra.write_bytes(b'fixture')
        assert check(profile)['unexpected_jar_count'] == 1
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            assert main(['--profile', str(profile)]) == 1
        assert 'unexpected=1' in out.getvalue() and 'extra-original.jar' not in out.getvalue()
        assert extra.read_bytes() == b'fixture'
        extra.unlink()
        kept = mods/'voicechat-forge-1.16.5-2.3.23.jar'
        kept.unlink()
        assert check(profile)['declared_missing_count'] == 1
        assert not check(profile)['pass']
        kept.write_bytes(before[kept.name])
        wrong = Path(temp)/'FunCity LowSpec'
        try:
            check(wrong)
            raise AssertionError('unexpected acceptance of wrong Prism instance')
        except ValueError:
            pass
        # The existing inventory library must also reject links and unsafe files.
        (mods/'extra-link.jar').symlink_to(mods/names[0])
        try:
            check(profile)
            raise AssertionError('unexpected acceptance of symlink')
        except ValueError:
            pass
        (mods/'extra-link.jar').unlink()
        assert {name: (mods/name).read_bytes() for name in names} == before
    print('PASS: Freeroam-only inventory 28/22; extra/missing/link fail closed; no fixture mutated')


if __name__ == '__main__':
    main_test()
