#!/usr/bin/env python3
"""Synthetic metadata/path guard only. Does not download, boot or touch PC."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

from fc_chunk_sending_canary import CANDIDATE, safe_failure_category, validate_candidate


def denied(root, candidate):
    try:
        validate_candidate(root, candidate)
    except ValueError:
        return
    raise AssertionError('invalid hosted candidate accepted')


def main():
    assert safe_failure_category(ValueError('server did not reach Done; exit=0')) == 'BOOT_NOT_DONE'
    assert safe_failure_category(ValueError('fatal server/plugin marker')) == 'RUNTIME_FATAL'
    assert safe_failure_category(OSError('private-host-path-do-not-print')) == 'PRECHECK_OR_RUNTIME'
    with TemporaryDirectory() as tmp:
        temp = Path(tmp)
        root = temp/'fc-full-rp-catserver-official'
        root.mkdir()
        jar = root/CANDIDATE
        with ZipFile(jar, 'w') as zipfile:
            zipfile.writestr('META-INF/mods.toml',
                             '[[mods]]\nmodId="chunksending"\n[[dependencies.chunksending]]\n'
                             'modId="forge"\nmandatory=true\n')
            zipfile.writestr('padding', b'0'*2000)
        with patch.dict(os.environ, {'RUNNER_TEMP': tmp}):
            assert len(validate_candidate(root, jar)) == 64
            denied(temp, jar)
            denied(root, root/'another.jar')
            with TemporaryDirectory() as elsewhere:
                denied(root, Path(elsewhere)/CANDIDATE)
            jar.unlink()
            with ZipFile(jar, 'w') as zipfile:
                zipfile.writestr('META-INF/mods.toml', '[[mods]]\nmodId="bad"\n')
                zipfile.writestr('padding', b'0'*2000)
            denied(root, jar)
            jar.unlink()
            (root/'data.jar').write_bytes(b'untrusted')
            jar.symlink_to(root/'data.jar')
            denied(root, jar)
    print('PASS: synthetic pinned path, Forge mod ID, no symlink or arbitrary PC candidate')


if __name__ == '__main__':
    main()
