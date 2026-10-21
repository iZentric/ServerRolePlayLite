#!/usr/bin/env python3
"""Synthetic client/server logs; check that only safe aggregate evidence escapes."""
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix='fc-join-probe-') as tmp:
    root = Path(tmp)
    client = root / 'Prism' / 'instances' / 'FunCity RP Lite'
    game = client / '.minecraft' / 'logs'
    game.mkdir(parents=True)
    server = root / 'FunCityLocal' / 'server'
    log = server / 'logs'
    log.mkdir(parents=True)
    game.joinpath('latest.log').write_text(
        'Connecting to 127.0.0.1:25565 secret-account\n'
        'Incomplete mod data: registry missing clumps SECRET_TOKEN\n', encoding='utf-8')
    log.joinpath('latest.log').write_text(
        'secret-player lost connection due to registry mismatch\n', encoding='utf-8')
    script = str(Path(__file__).with_name('fc_join_failure_probe.ps1'))
    result = subprocess.run(['pwsh', '-NoProfile', '-File', script, '-Profile', str(client),
                             '-Server', str(server)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.returncode
    assert 'CLIENT_INCOMPLETE_HINTS=1' in result.stdout, result.stdout
    assert 'ALLOWLIST_MOD_IDS=clumps' in result.stdout, result.stdout
    for secret in ('secret-account', 'secret-player', 'SECRET_TOKEN', '127.0.0.1', tmp):
        assert secret not in result.stdout + result.stderr
    print('PASS: latest client/server join symptoms are aggregate-only, raw logs never leave PC')
