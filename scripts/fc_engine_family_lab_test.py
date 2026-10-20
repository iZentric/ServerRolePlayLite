#!/usr/bin/env python3
"""Synthetic SHA/path preflight. Does not fetch or run any engine."""
import hashlib
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

import fc_engine_family_lab as lab


def rejected(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unsafe/unverified engine was accepted')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        data = b'synthetic-binary-not-a-real-engine'
        digest = hashlib.sha256(data).hexdigest()
        jar = root/'source.jar'
        jar.write_bytes(data)
        with patch.dict(lab.ENGINES, {'catserver-official': ('jar', None, None, digest)}):
            assert lab.source_engine('catserver-official', jar) == data
            jar.write_bytes(data + b' tampered')
            rejected(lambda: lab.source_engine('catserver-official', jar))
        archive = root/'source.zip'
        member = 'candidate.jar'
        with zipfile.ZipFile(archive, 'w') as output:
            output.writestr(member, data)
        with patch.dict(lab.ENGINES, {'mist': ('zip', lab.sha(archive), member, digest)}):
            assert lab.source_engine('mist', archive) == data
        with patch.dict(lab.ENGINES, {'mist': ('zip', lab.sha(archive), 'not-there.jar', digest)}):
            rejected(lambda: lab.source_engine('mist', archive))
        with patch.dict(lab.ENGINES, {'mist': ('zip', '0'*64, member, digest)}):
            rejected(lambda: lab.source_engine('mist', archive))
        with patch.dict(lab.ENGINES, {'mist': ('zip', lab.sha(archive), member, '0'*64)}):
            rejected(lambda: lab.source_engine('mist', archive))
        with patch.dict('os.environ', {'RUNNER_TEMP': str(root)}):
            rejected(lambda: lab.validate_stage(root/'an-old-server'))
        assert len(lab.ENGINES) == 5
        print('PASS: 5 known engines only; archive/JAR SHA, missing source and stage guards')


if __name__ == '__main__':
    main()
