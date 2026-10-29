#!/usr/bin/env python3
"""Extract only the SHA-pinned FunCity engine from a verified release tarball."""
import hashlib
from pathlib import Path
import shutil
import sys
import tarfile

ARCHIVE_SHA = 'f2cb921efbf751fa24534a9a02b57197db46294ca7b71d9711b04996bf6d1784'
ENGINE_SHA = 'd6ffa35c1ea9032a4a95f7f1e34b734aa7f53b0358dda6b9e6592326640a15dd'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def extract(archive, dest):
    archive, dest = Path(archive), Path(dest)
    if dest.exists() or sha(archive) != ARCHIVE_SHA:
        raise ValueError('existing destination or unverified release tarball')
    with tarfile.open(archive, 'r:gz') as source:
        matches = [m for m in source.getmembers() if m.isfile() and
                   Path(m.name).name in ('FunCity-b1.0827.jar', 'FunCity-1.16.5-b1.0827.jar')]
        if len(matches) != 1 or matches[0].size > 350_000_000:
            raise ValueError('ambiguous/oversized FunCity engine')
        with source.extractfile(matches[0]) as inp, dest.open('xb') as out:
            shutil.copyfileobj(inp, out, 1 << 20)
    if sha(dest) != ENGINE_SHA:
        dest.unlink()  # only file newly created by this function
        raise ValueError('engine SHA mismatch')


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError('expected verified tarball and NEW output file')
        extract(sys.argv[1], sys.argv[2])
        print('::notice title=PC isolated FunCity engine::SHA256 verified; no existing engine changed')
    except (ValueError, OSError, tarfile.TarError) as exc:
        print('RESPINS: ' + str(exc), file=sys.stderr)
        sys.exit(2)
