#!/usr/bin/env python3
"""Synthetic selected-mod graph checks; no server or PC access."""
import io
import zipfile

from fc_full_rp_engine_boot import required_graph


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
    print('PASS: valid dependencies, missing prerequisite, duplicate mod ID and fake JAR blocked')


if __name__ == '__main__':
    main()
