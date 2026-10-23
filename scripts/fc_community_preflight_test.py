#!/usr/bin/env python3
"""Synthetic-only tests: no real server, backup or player capacity measured."""
from collections import namedtuple
from pathlib import Path
import json
import sys
import tempfile

from fc_community_preflight import MIB, RESERVE_BYTES, report

Usage = namedtuple('Usage', 'total used free')


def main():
    with tempfile.TemporaryDirectory(prefix='fc-preflight-fixture-') as tmp:
        base = Path(tmp)
        root, backup = base / 'server', base / 'backup'
        root.mkdir()
        backup.mkdir()
        world = root / 'world'
        world.mkdir()
        (world / 'level.dat').write_bytes(b'world')
        (root / 'plugins' / 'CoreProtect').mkdir(parents=True)
        (root / 'plugins' / 'CoreProtect' / 'database.db').write_bytes(b'log')
        (root / 'server.properties').write_text('online-mode=false\nmax-players=200\n'
                                                 'rcon.password=NEVER_PRINT\n')
        free = lambda _: Usage(1024*MIB, 0, 10*MIB)
        blocked = report(root, backup, free)
        assert blocked['data_bytes_total'] == 8 and blocked['free_space_gate'] == 'BLOCKED'
        assert blocked['project_policy_minimum_free_bytes'] == RESERVE_BYTES + 16
        assert blocked['identity_review_required'] is True
        assert 'NEVER_PRINT' not in json.dumps(blocked)
        assert blocked['capacity_player_count'] is None and not blocked['restore_tested']
        eligible = report(root, backup, lambda _: Usage(1024*MIB, 0, 1024*MIB))
        assert eligible['free_space_gate'] == 'ELIGIBLE_FOR_TEST_ONLY'
        (world / 'level.dat').unlink()
        assert report(root, backup, lambda _: Usage(1024*MIB, 0, 1024*MIB))['free_space_gate'] == 'NO_WORLD_TO_BACK_UP'
        (world / 'level.dat').write_bytes(b'world')
        (world / 'link').symlink_to(base / 'server.properties')
        try:
            report(root, backup, free)
        except ValueError:
            pass
        else:
            raise AssertionError('symlink within world was not rejected')
    print('PASS: storage gate, symlink rejection, no secret output, no capacity claim; synthetic only')


if __name__ == '__main__':
    sys.exit(main())
