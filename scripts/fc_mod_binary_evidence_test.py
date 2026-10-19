#!/usr/bin/env python3
"""Tiny synthetic read-only fixture; not a Forge boot or mod performance test."""
import io
from pathlib import Path
import tempfile
import zipfile
from fc_mod_binary_evidence import FOCUS, inspect_archive, inspect_jar, scan_required_dependents


def main():
    toml = b'''license="MIT"\n[[mods]]\nmodId="example"\ndisplayName="Example"\n[[dependencies.example]]\nmodId="forge"\nmandatory=true\n'''
    jar_stream = io.BytesIO()
    with zipfile.ZipFile(jar_stream, 'w') as jar:
        jar.writestr('META-INF/mods.toml', toml)
        jar.writestr('example/Foo.class', b'x')
        jar.writestr('assets/example/icon.png', b'x')
    result = inspect_jar(jar_stream.getvalue())
    assert result['mod_ids'] == ['example']
    assert result['declared_dependencies'] == {'example': ['forge']}
    assert result['required_dependencies'] == {'example': ['forge']}
    assert result['classes'] == result['asset_files'] == 1
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'server.zip'
        with zipfile.ZipFile(path, 'w') as source:
            for name in FOCUS:
                source.writestr('root/mods/' + name, jar_stream.getvalue())
        assert len(inspect_archive(path)) == len(FOCUS)
        scan = scan_required_dependents(path, 'forge')
        assert scan['embedded_jars_inspected'] == len(FOCUS)
        assert len(scan['mandatory_dependents']) == len(FOCUS)
        assert not scan['metadata_not_parsed']
        with zipfile.ZipFile(path, 'a') as source:
            source.writestr('other/mods/' + FOCUS[0], jar_stream.getvalue())
        try:
            inspect_archive(path)
        except ValueError as exc:
            assert 'ambiguous' in str(exc)
        else:
            raise AssertionError('duplicate source accepted')
    print('PASS: bounded JAR metadata parsing and ambiguous source refusal (synthetic)')


if __name__ == '__main__':
    main()
