#!/usr/bin/env python3
"""Fixture-only test for safe Forge metadata comparison; no user JARs."""
import subprocess
import tempfile
import zipfile
from pathlib import Path


def jar(folder, name, mod_id):
    with zipfile.ZipFile(folder / name, 'w') as out:
        out.writestr('META-INF/mods.toml', (
            'modLoader="javafml"\nloaderVersion="[36,)"\n'
            '[[mods]]\nmodId="%s"\nversion="1.0"\n'
            '[[dependencies.%s]]\nmodId="forge"\nmandatory=true\n'
        ) % (mod_id, mod_id))


with tempfile.TemporaryDirectory(prefix='fc-forge-fixture-') as temp:
    client = Path(temp) / 'client'
    server = Path(temp) / 'server'
    client.mkdir()
    server.mkdir()
    jar(client, 'shared.jar', 'rpcontent')
    jar(client, 'client.jar', 'visualonly')
    jar(server, 'shared.jar', 'rpcontent')
    jar(server, 'server.jar', 'requiredcandidate')
    jar(server, 'Clumps-6.0.0.28.jar', 'clumps')
    result = subprocess.run(['pwsh', '-File', str(Path(__file__).with_name('fc_forge_modid_audit.ps1')),
                             '-ClientMods', str(client), '-ServerMods', str(server), '-SyntheticDiagnostics'],
                            capture_output=True, text=True)
    if result.returncode or 'COMMON_IDS=1 SERVER_ONLY_IDS=2 CLIENT_ONLY_IDS=1' not in result.stdout or \
       'CLUMPS_SERVER_JAR=Clumps-6.0.0.28.jar CLUMPS_CLIENT_PRESENT=False' not in result.stdout:
        for line in result.stdout.splitlines():
            if line.startswith('::'):
                print(line.replace(str(temp), '<synthetic>'))
        if result.stderr:
            diagnostic = result.stderr.replace(str(temp), '<synthetic>').replace('\n', ' ')[:800]
            print('::error title=Forge synthetic stderr::' + diagnostic)
        raise AssertionError('audit fixture failed or wrong counts')
    assert 'requiredcandidate' in result.stdout and 'visualonly' in result.stdout
    assert '::forge' not in result.stdout.lower() and ',forge' not in result.stdout.lower(), 'dependency mistakenly parsed as a mod ID'
    assert str(temp) not in result.stdout + result.stderr, 'private fixture path leaked'
    print('PASS: Forge JAR IDs, not dependency IDs or paths; source files unchanged')
