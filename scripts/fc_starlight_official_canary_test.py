#!/usr/bin/env python3
"""No server/download: reject wrong author size, Forge identity and hash drift."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from fc_rp_mod_cost_ab_test import fake_jar
from fc_plugin_first_stage import sha
from fc_starlight_official_canary import FILE, verify


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError('unsafe file accepted')


def main():
    with TemporaryDirectory() as d:
        root = Path(d)
        jar = root/FILE
        data = fake_jar('starlight')
        jar.write_bytes(data)
        with ZipFile(jar, 'a') as z:
            z.writestr('p', b'0'*(97563-len(data)-78))
        assert jar.stat().st_size == 97563
        reject(lambda: verify(root))  # synthetic bytes must not match pinned author SHA
        path, digest = verify(root, sha(jar))
        assert path == jar and len(digest) == 64
        reject(lambda: verify(root, '0'*64))
        wrong = fake_jar('wrongmod')
        jar.write_bytes(wrong)
        with ZipFile(jar, 'a') as z:
            z.writestr('p', b'0'*(97563-len(wrong)-78))
        reject(lambda: verify(root))
        jar.unlink()
        jar.symlink_to(root/'missing.jar')
        reject(lambda: verify(root))
    print('PASS: original Forge release path/asset size/mod ID/dependencies/hash guard')


if __name__ == '__main__':
    main()
