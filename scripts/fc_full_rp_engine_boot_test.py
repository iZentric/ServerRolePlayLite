#!/usr/bin/env python3
"""Synthetic selected-mod graph checks; no server or PC access."""
import io
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

from fc_full_rp_engine_boot import boot_once_or_installer_then_once, required_graph


def jar(mod_id, deps=()):
    with io.BytesIO() as stream:
        with zipfile.ZipFile(stream, 'w') as z:
            toml = f'[[mods]]\nmodId="{mod_id}"\nversion="1"\n'
            if deps:
                toml += f'[[dependencies.{mod_id}]]\nmodId="{deps[0]}"\nmandatory=true\nversionRange="[1,)"\nordering="NONE"\nside="BOTH"\n'
            z.writestr('META-INF/mods.toml', toml)
        return stream.getvalue()


def reject(jars):
    try:
        required_graph(jars)
    except (ValueError, zipfile.BadZipFile):
        return
    raise AssertionError('invalid mod selection accepted')


def main():
    content = {'vehicle.jar': jar('vehicle', ('obfuscate',)),
               'obfuscate.jar': jar('obfuscate')}
    assert required_graph(content) == {'vehicle.jar': ['vehicle'], 'obfuscate.jar': ['obfuscate']}
    reject({'vehicle.jar': jar('vehicle', ('obfuscate',))})
    reject({'vehicle.jar': jar('vehicle'), 'duplicate.jar': jar('vehicle')})
    reject({'vehicle.jar': b'NOT A JAR'})
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        log = stage/'private-benchmark.log'
        log.write_text('Successfully installed server files\n')
        with patch('fc_full_rp_engine_boot.run_one', side_effect=[
                ValueError('server did not reach Done; no A/B verdict; exit=0'), None]) as f:
            boot_once_or_installer_then_once(stage, {'plugins': []})
            assert f.call_count == 2 and (stage/'private-installer.log').exists()
        log.write_text('Normal exit, no installer evidence')
        with patch('fc_full_rp_engine_boot.run_one', side_effect=ValueError(
                'server did not reach Done; no A/B verdict; exit=0')) as f:
            try:
                boot_once_or_installer_then_once(stage, {})
            except ValueError:
                pass
            else:
                raise AssertionError('unknown clean exit retried')
            assert f.call_count == 1
    print('PASS: required graph; bootstrap only retried on explicit installer evidence')


if __name__ == '__main__':
    main()
