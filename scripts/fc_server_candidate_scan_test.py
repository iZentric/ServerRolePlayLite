#!/usr/bin/env python3
"""No downloaded mods or server: exact hosted paths, metadata, dependency gate."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile

import fc_server_candidate_scan as scan
from fc_plugin_first_stage import sha
from fc_server_candidate_scan import CANDIDATES, verify


def create(path, modid, dep=None):
    with ZipFile(path, 'w') as z:
        text = '[[mods]]\nmodId="' + modid + '"\nversion="1"\n'
        if dep:
            text += ('[[dependencies.' + modid + ']]\nmodId="' + dep + '"\n'
                     'mandatory=true\nversionRange="[1,)"\n')
        z.writestr('META-INF/mods.toml', text)
        z.writestr('padding', b'0'*2400)


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unsafe candidate accepted')


def main():
    with TemporaryDirectory() as d:
        root = Path(d)
        with patch.dict(os.environ, {'RUNNER_TEMP': d}):
            for label, (name, file_id, project_id, _) in CANDIDATES.items():
                path = root/name
                create(path, label)
                with patch.dict(scan.CANDIDATES, {label: (name, file_id, project_id, sha(path))}):
                    result = verify(root, label)
                    assert result[0] == path and result[1] == label and result[3] == file_id
                    with patch.dict(scan.CANDIDATES, {label: (name, file_id, project_id, '0'*64)}):
                        reject(lambda: verify(root, label))
                    path.unlink()
                    create(path, label, 'unapprovedclientmod')
                    reject(lambda: verify(root, label))
                    path.unlink()
                    path.symlink_to(root/'arbitrary.jar')
                    reject(lambda: verify(root, label))
                    path.unlink()
                    create(path, label)
    print('PASS: two distinct exact author artifacts, Forge mod IDs, no new client dependency or symlink')


if __name__ == '__main__':
    main()
