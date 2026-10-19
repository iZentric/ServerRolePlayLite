#!/usr/bin/env python3
"""Synthetic plugin archive fixtures; no real plugin binaries or Minecraft boot."""
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import zipfile

from fc_plugin_audit import EXPECTED, deps, scan, sha256


def archive(path, missing=False, duplicate_name=False, shared_command=False):
    with zipfile.ZipFile(path, 'w') as server:
        for index, filename in enumerate(sorted(EXPECTED)):
            name = 'Example' + str(index if not duplicate_name or index != 1 else 0)
            commands = 'commands:\n  test: {}\n' if shared_command and index < 2 else ''
            meta = (f'name: {name}\nmain: org.example.Plugin\n'
                    'depend: [Vault]\nsoftdepend:\n  - WorldEdit\n' + commands)
            jar = io.BytesIO()
            with zipfile.ZipFile(jar, 'w') as z:
                if not missing or index != 0:
                    z.writestr('plugin.yml', meta)
            server.writestr('server/plugins/' + filename, jar.getvalue())


def rejects(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('expected fail closed')


def main():
    assert deps('depend: [Vault, WorldEdit]\n', 'depend') == ['Vault', 'WorldEdit']
    assert deps('softdepend:\n  - Vault\n  - WorldEdit\n', 'softdepend') == ['Vault', 'WorldEdit']
    assert deps('depend: {Vault: true}\n', 'depend') is None
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / 'server.zip'
        archive(path)
        digest = sha256(path)
        assert len(scan(path)['plugins']) == 14
        assert not scan(path)['shared_declared_commands']
        assert digest == hashlib.sha256(path.read_bytes()).hexdigest()
        archive(path, shared_command=True)
        assert scan(path)['shared_declared_commands'] == {'test': ['Example0', 'Example1']}
        archive(path, duplicate_name=True)
        rejects(lambda: scan(path))
        archive(path, missing=True)
        rejects(lambda: scan(path))
    print('PASS: inventory, metadata, declared commands, missing/duplicate fail-closed; synthetic only')


if __name__ == '__main__':
    sys.exit(main())
