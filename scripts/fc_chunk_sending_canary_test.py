#!/usr/bin/env python3
"""Synthetic metadata/path guard only. Does not download, boot or touch PC."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import fc_chunk_sending_canary as canary
from fc_chunk_sending_canary import CANDIDATE, clone_clean_baseline, safe_failure_category, validate_candidate
from fc_plugin_first_stage import sha


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
        template = temp/'baseline'
        template.mkdir()
        (template/'mods').mkdir()
        (template/'mods'/'source.jar').write_bytes(b'source')
        (template/'lab-world').mkdir()
        (template/'lab-world'/'level.dat').write_bytes(b'world')
        (template/'eula.txt').write_text('eula=true')
        (template/'private-benchmark.log').write_text('private')
        os.mkfifo(template/'.fcbench-in')
        trial = temp/'trial'
        clone_clean_baseline(template, trial)
        assert (trial/'mods'/'source.jar').read_bytes() == b'source'
        assert not any((trial/name).exists() for name in
                       ('lab-world', 'eula.txt', 'private-benchmark.log', '.fcbench-in'))
        jar = root/CANDIDATE
        with ZipFile(jar, 'w') as zipfile:
            zipfile.writestr('META-INF/mods.toml',
                             '[[mods]]\nmodId="chunksending"\n[[dependencies.chunksending]]\n'
                             'modId="forge"\nmandatory=true\n')
            zipfile.writestr('padding', b'0'*2000)
        with patch.dict(os.environ, {'RUNNER_TEMP': tmp}), patch.object(canary, 'CANDIDATE_SHA256', sha(jar)):
            assert len(validate_candidate(root, jar)) == 64
            with patch.object(canary, 'CANDIDATE_SHA256', '0'*64):
                denied(root, jar)
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
