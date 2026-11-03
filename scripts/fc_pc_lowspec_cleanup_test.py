#!/usr/bin/env python3
"""Synthetic cleanup guard: never touches a real Prism or runner folder."""
import json
from pathlib import Path
import tempfile

from fc_pc_lowspec_cleanup import CONTENT, JARS, NAMES, READMES, ZERO, clean


def fixture(root, name):
    profile = root / name
    mods = profile / '.minecraft' / 'mods'
    mods.mkdir(parents=True)
    (profile/'LAB-READ-ME.txt').write_text(READMES[name], encoding='utf-8')
    (profile/'instance.cfg').write_text('[General]\nname=' + NAMES[name] + '\n', encoding='utf-8')
    (profile/'mmc-pack.json').write_text(json.dumps({'components': [
        {'uid': 'net.minecraft', 'version': '1.16.5'},
        {'uid': 'net.minecraftforge', 'version': '36.2.42'}]}), encoding='utf-8')
    if name == CONTENT:
        for jar in JARS:
            (mods/jar).write_bytes(b'synthetic test jar')
    return profile


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)/'instances'
        root.mkdir()
        zero = fixture(root, ZERO)
        content = fixture(root, CONTENT)
        low = root/'FunCity-Lite-LowSpec-LAB-1.16.5'
        low.mkdir()
        user = root/'FunCity-Actual-Player'
        user.mkdir()
        assert clean(root)[ZERO] == 'eligible'
        assert zero.exists() and content.exists() and low.exists() and user.exists()
        (zero/'.minecraft'/'saves').mkdir()
        assert clean(root, apply=True)[ZERO] == 'preserved_user_files_or_world_present'
        assert zero.exists() and low.exists() and user.exists()
        assert not content.exists()
        (zero/'.minecraft'/'saves').rmdir()
        assert clean(root, apply=True)[ZERO] == 'removed_generated_lab'
        assert not zero.exists() and low.exists() and user.exists()
        fake = fixture(root, CONTENT)
        (fake/'.minecraft'/'mods'/'unexpected.jar').write_bytes(b'keep')
        assert clean(root, apply=True)[CONTENT] == 'preserved_unexpected_mods'
        assert fake.exists()
    print('PASS: exact lab cleanup only; user worlds, added mods and LowSpec profile preserved')


if __name__ == '__main__':
    main()
