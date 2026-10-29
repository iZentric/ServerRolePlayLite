#!/usr/bin/env python3
"""Fail-closed static gate: FunCity 3 GiB capacity arm is ONLY a proposed config.

No network, server launch, installed client, world, PC or host access. The 4-chunk
profile must not accidentally change binding, auth, mods, entity tracking or RP.
"""
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'functity-config/server.properties'
CANDIDATE = ROOT / 'functity/capacity/3g-view4/server.properties'
VIEW_ONLY = ROOT / 'functity/capacity/3g-view4-only/server.properties'


def parse(path):
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' not in line:
            raise AssertionError('invalid property line')
        key, value = line.split('=', 1)
        if key in values:
            raise AssertionError('duplicate property: ' + key)
        values[key] = value
    return values


def test_profile():
    base, candidate, view_only = parse(BASE), parse(CANDIDATE), parse(VIEW_ONLY)
    assert base.keys() == candidate.keys() == view_only.keys(), 'profile changed property set'
    assert base['view-distance'] == '5' and candidate['view-distance'] == view_only['view-distance'] == '4'
    assert base['max-tick-time'] == view_only['max-tick-time'] == '-1'
    assert candidate['max-tick-time'] == '60000'
    assert {k for k in base if base[k] != view_only[k]} == {'view-distance'}
    assert {k for k in base if base[k] != candidate[k]} == {'view-distance', 'max-tick-time'}
    for arm in (candidate, view_only):
        assert arm['server-ip'] == '127.0.0.1'  # No exposure as a side effect.
        assert arm['online-mode'] == base['online-mode']
        assert arm['entity-broadcast-range-percentage'] == base['entity-broadcast-range-percentage']
        assert arm['max-players'] == base['max-players']  # Not a capacity result.
        assert 'simulation-distance' not in arm  # Minecraft/Forge 1.16.5.
    assert (2 * 5 + 1) ** 2 == 121 and (2 * 4 + 1) ** 2 == 81
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp) / 'bad.properties'
        fixture.write_text('view-distance=4\nview-distance=5\n', encoding='utf-8')
        try:
            parse(fixture)
        except AssertionError as exc:
            assert str(exc).startswith('duplicate property:')
        else:
            raise AssertionError('duplicate view-distance accepted')
    print('PASS: isolated view 5->4-only arm (watchdog unchanged) and view4+watchdog safety arm; '
          '121->81 nominal chunk window; NO live write, no player-count claim')


if __name__ == '__main__':
    test_profile()
