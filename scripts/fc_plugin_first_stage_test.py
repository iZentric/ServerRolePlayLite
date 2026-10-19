#!/usr/bin/env python3
"""Small fake-JAR fixtures; no engine launch, PC, player data or live files."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

from fc_plugin_audit import EXPECTED
from fc_plugin_first_stage import SELECTED, stage


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jar_with_metadata(name):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as jar:
        jar.writestr('plugin.yml', f'name: {name}\nmain: example.Plugin\nversion: 1\n')
    return buf.getvalue()


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        engine, archive, core, output = [root / n for n in ('motor.jar', 'old.zip', 'CoreProtect.jar', 'stage')]
        engine.write_bytes(b'FAKE pinned engine')
        core.write_bytes(jar_with_metadata('CoreProtect'))
        with zipfile.ZipFile(archive, 'w') as source:
            for index, name in enumerate(sorted(EXPECTED)):
                source.writestr('old/plugins/' + name, jar_with_metadata('P' + str(index)))
            source.writestr('old/world/level.dat', b'private world fixture')
            source.writestr('old/plugins/AuthMe/accounts.db', b'private accounts fixture')
        pins = tuple(map(digest, (engine, archive, core)))
        try:
            stage(engine, archive, core, output, ('0' * 64, pins[1], pins[2]))
        except ValueError as exc:
            assert 'SHA256 mismatch' in str(exc)
        else:
            raise AssertionError('unverified engine accepted')
        assert not output.exists()
        report = stage(engine, archive, core, output, pins)
        assert report['server_mods'] == [] and len(report['plugins']) == 6
        assert len({p['declared_name'] for p in report['plugins']}) == 6
        assert set(SELECTED) <= {p.name for p in (output/'plugins').iterdir()}
        assert not list((output/'mods').iterdir())
        assert 'online-mode=true' in (output/'server.properties').read_text()
        assert 'white-list=true' in (output/'server.properties').read_text()
        assert 'server-ip=127.0.0.1' in (output/'server.properties').read_text()
        assert not (output/'world').exists() and not (output/'plugins/AuthMe').exists()
        assert b'private world fixture' not in (output/'stage-report.json').read_bytes()
        try:
            stage(engine, archive, core, output, pins)
        except ValueError as exc:
            assert 'destination must be new' in str(exc)
        else:
            raise AssertionError('existing stage overwritten')
        stored = json.loads((output/'stage-report.json').read_text())
        assert stored == report
    print('PASS: closed zero-mod 6-plugin stage, SHA gating and privacy fixtures (NO boot)')


if __name__ == '__main__':
    main()
