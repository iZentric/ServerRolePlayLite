#!/usr/bin/env python3
"""Synthetic client/server logs; check that only safe aggregate evidence escapes."""
import subprocess
import tempfile
import zipfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix='fc-join-probe-') as tmp:
    root = Path(tmp)
    client = root / 'Prism' / 'instances' / 'FunCity RP Lite'
    game = client / '.minecraft' / 'logs'
    game.mkdir(parents=True)
    clientmods = client / '.minecraft' / 'mods'
    clientmods.mkdir()
    with zipfile.ZipFile(clientmods / 'examplemod.jar', 'w') as jar:
        jar.writestr('META-INF/mods.toml', '[[mods]]\nmodId="examplemod"\n')
    server = root / 'FunCityLocal' / 'server'
    servermods = server / 'mods'
    servermods.mkdir(parents=True)
    with zipfile.ZipFile(servermods / 'clumps.jar', 'w') as jar:
        jar.writestr('META-INF/mods.toml', '[[mods]]\nmodId="clumps"\n')
    log = server / 'logs'
    log.mkdir(parents=True)
    game.joinpath('latest.log').write_text(
        'Connecting to 127.0.0.1:25565 secret-account\n'
        'Incomplete mod data: registry missing clumps SECRET_TOKEN\n', encoding='utf-8')
    game.joinpath('debug.log').write_text(
        'Missing registry entry clumps:xp_orb_big PRIVATE_VALUE\n'
        'client network channel examplemod:main rejected server version SECRET_ACCOUNT\n', encoding='utf-8')
    log.joinpath('latest.log').write_text(
        'secret-player lost connection due to registry mismatch\n', encoding='utf-8')
    script = str(Path(__file__).with_name('fc_join_failure_probe.ps1'))
    result = subprocess.run(['pwsh', '-NoProfile', '-File', script, '-Profile', str(client),
                             '-Server', str(server), '-Synthetic'], capture_output=True, text=True, timeout=10)
    if result.returncode or 'CLIENT_INCOMPLETE_HINTS=1' not in result.stdout or 'REJECT_CLIENT_ONLY_MOD_IDS=examplemod' not in result.stdout:
        # Script output is fixed-form, synthetic and contains no raw log values.
        print('::error title=Private join synthetic fixture::' + result.stdout.strip().replace('\n', ' ')[-650:])
        raise AssertionError('Synthetic Forge join classification failed')
    assert 'ALLOWLIST_MOD_IDS=clumps' in result.stdout, result.stdout
    assert 'DEBUG_ALLOWED_IDS_IN_ERROR_CONTEXT=clumps' in result.stdout, result.stdout
    assert 'REJECT_CLIENT_ONLY_MOD_IDS=examplemod' in result.stdout, result.stdout
    for secret in ('secret-account', 'secret-player', 'SECRET_TOKEN', 'PRIVATE_VALUE', 'SECRET_CHANNEL', 'SECRET_ACCOUNT', '127.0.0.1', tmp):
        assert secret not in result.stdout + result.stderr
    print('PASS: latest client/server join symptoms are aggregate-only, raw logs never leave PC')
