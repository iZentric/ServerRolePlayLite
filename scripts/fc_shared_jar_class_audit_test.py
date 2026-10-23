#!/usr/bin/env python3
"""Synthetic JAR bytecode comparator: distinguishes code vs resource-only differences."""
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path


def jar(folder, name, bytecode, resource):
    with zipfile.ZipFile(folder / name, 'w') as out:
        out.writestr('net/example/Example.class', bytecode)
        out.writestr('assets/example/lang/en_us.json', resource)


with tempfile.TemporaryDirectory(prefix='fc-class-audit-') as temp:
    root = Path(temp)
    client, server = root / 'client', root / 'server'
    client.mkdir()
    server.mkdir()
    jar(client, 'same.jar', b'code1', b'resource1')
    jar(server, 'same.jar', b'code1', b'resource1')
    jar(client, 'resource.jar', b'code2', b'resource1')
    jar(server, 'resource.jar', b'code2', b'resource2')
    jar(client, 'code.jar', b'client-code', b'other')
    jar(server, 'code.jar', b'server-code', b'other')
    manifest = root / 'selection.json'
    manifest.write_text(json.dumps({'retained_in_future_target': ['same.jar', 'resource.jar', 'code.jar']}))
    script = Path(__file__).with_name('fc_shared_jar_class_audit.ps1')
    result = subprocess.run(['pwsh', '-File', str(script), '-ClientMods', str(client),
                             '-ServerMods', str(server), '-Manifest', str(manifest),
                             '-SyntheticDiagnostics'], capture_output=True, text=True, timeout=25)
    if result.returncode or 'WHOLE_JAR_SHA_DIFF=2 CLASS_DIFF=1 SAME_CLASSES_OTHER_BYTES_DIFF=1' not in result.stdout or \
       'class-different approved names::code.jar' not in result.stdout:
        for line in result.stdout.splitlines():
            if line.startswith('::'):
                print(line.replace(temp,'<fixture>'))
        raise AssertionError('Synthetic class fingerprint comparison failed')
    assert temp not in result.stdout + result.stderr, 'Private path leaked'
    print('PASS: fixture separates class changes from resource-only JAR changes')
