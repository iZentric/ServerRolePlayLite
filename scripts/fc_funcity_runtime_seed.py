#!/usr/bin/env python3
"""Private CatServer first-boot runtime files for an offline full-pack trial.

Never publish this seed: it may contain Minecraft/third-party binaries. The
build exports it only on a private machine or a disposable Actions runner.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil

FOLDERS = ('libraries', 'foxlaunch-libs', 'foxlaunch-data')
MANIFEST = 'funcity-runtime-seed.json'


class InvalidSeed(ValueError):
    pass


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inventory(root):
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(base)/name
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise InvalidSeed('runtime seed contains a link/special file')
        for name in files:
            path = Path(base)/name
            relative = path.relative_to(root).as_posix()
            if relative != MANIFEST:
                result[relative] = sha(path)
    return result


def export_runtime(boot_work, output, engine):
    """Copy only required private launcher runtime, never world/log/config."""
    boot_work, output = Path(boot_work), Path(output)
    if output.exists() or output.is_symlink() or not output.parent.is_dir():
        raise InvalidSeed('new private runtime seed directory required')
    if not (boot_work/'libraries').is_dir() or not (boot_work/'foxlaunch-data'/'install.dat').is_file():
        raise InvalidSeed('CatServer first-boot libraries/install marker missing')
    for folder in FOLDERS:
        if (boot_work/folder).is_symlink():
            raise InvalidSeed('runtime seed source is linked')
    output.mkdir()
    for folder in FOLDERS:
        if (boot_work/folder).is_dir():
            shutil.copytree(boot_work/folder, output/folder)
    files = inventory(output)
    if not files or not any(name.startswith('libraries/') for name in files):
        raise InvalidSeed('runtime seed is empty')
    (output/MANIFEST).write_text(json.dumps({'schema': 1, 'engine_sha256': sha(engine),
                                             'files': files}, sort_keys=True) + '\n')
    return len(files)


def validate_runtime(output, expected_sha):
    output = Path(output)
    if output.is_symlink() or not output.is_dir():
        raise InvalidSeed('private runtime seed missing')
    try:
        meta = json.loads((output/MANIFEST).read_text())
    except (OSError, ValueError) as exc:
        raise InvalidSeed('private runtime seed manifest missing/invalid') from exc
    if (meta.get('schema') != 1 or meta.get('engine_sha256') != expected_sha
            or not isinstance(meta.get('files'), dict)
            or not (output/'foxlaunch-data'/'install.dat').is_file()
            or not (output/'libraries').is_dir()
            or inventory(output) != meta['files']):
        raise InvalidSeed('private runtime seed hash or engine mismatch')
    return {folder for folder in FOLDERS if (output/folder).is_dir()}
