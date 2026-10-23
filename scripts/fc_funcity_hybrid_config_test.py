#!/usr/bin/env python3
"""No server launch: validate reversible, safety-first CatServer config arm.

Do not copy these files to an existing world: defaultconfigs applies to newly
created world configs, and Forge can load world/serverconfig/forge-server.toml.
"""
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'functity-config'
ARM = ROOT / 'functity/capacity/3g-view4'

FILES = {
    'bukkit.yml': [('warn-on-overload: false', 'warn-on-overload: true')],
    'config/connectivity-common.toml': [
        ('disableLoginLimits = true', 'disableLoginLimits = false'),
        ('disablePacketLimits = true', 'disablePacketLimits = false'),
    ],
    'defaultconfigs/forge-server.toml': [
        ('removeErroringEntities = true', 'removeErroringEntities = false'),
        ('removeErroringTileEntities = true', 'removeErroringTileEntities = false'),
    ],
}
SOURCE = {
    'bukkit.yml': 'bukkit.yml',
    'config/connectivity-common.toml': 'connectivity-common.toml',
    'defaultconfigs/forge-server.toml': 'forge-server.toml',
}


def expected_candidate(source, replacements):
    for original, safer in replacements:
        if source.count(original) != 1 or source.count(safer) != 0:
            raise AssertionError('missing/duplicate baseline safety setting')
        source = source.replace(original, safer)
    return source


def test_config():
    for dest, changes in FILES.items():
        source = (BASE / SOURCE[dest]).read_text(encoding='utf-8')
        proposed = (ARM / dest).read_text(encoding='utf-8')
        assert proposed == expected_candidate(source, changes), 'config arm changed more than approved: ' + dest
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'fixture.toml'
        path.write_text('removeErroringEntities = true\nremoveErroringEntities = true\n')
        try:
            expected_candidate(path.read_text(), FILES['defaultconfigs/forge-server.toml'][:1])
        except AssertionError:
            pass
        else:
            raise AssertionError('duplicate dangerous setting accepted')
    print('PASS: candidate-only Forge entity deletion OFF; Connectivity limits ON; '
          'overload warning ON; no auth/bind/pack/world changes or live write')


if __name__ == '__main__':
    test_config()
