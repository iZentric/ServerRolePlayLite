#!/usr/bin/env python3
"""Synthetic in-place client restore, without real Prism data."""
import io
import json
from pathlib import Path
import tempfile
import zipfile

from fc_pc_lowspec_full_content import ARCHIVE_RUN, EXTRA, PROFILE, restore, sha


def fake_jar(name):
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as out:
        out.writestr('META-INF/mods.toml', '[[mods]]\nmodId="fixture"\n')
        out.writestr('content.bin', bytes(range(256)) * 30, compress_type=zipfile.ZIP_STORED)
    return data.getvalue()


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/'PrismLauncher'/'instances'
        root.mkdir(parents=True)
        old = root.parent/'Arena-Archived-Instances'/ARCHIVE_RUN/'FunCity'
        source = old/'.minecraft'/'mods'
        source.mkdir(parents=True)
        (old/'mmc-pack.json').write_text(json.dumps({'components': [
            {'uid':'net.minecraft','version':'1.16.5'},
            {'uid':'net.minecraftforge','version':'36.2.42'}]}), encoding='utf-8')
        (old/'.minecraft'/'saves').mkdir()
        (old/'.minecraft'/'saves'/'my-world').write_bytes(b'preserve world')
        for name in EXTRA:
            (source/name).write_bytes(fake_jar(name))
        current = root/PROFILE
        mods = current/'.minecraft'/'mods'
        mods.mkdir(parents=True)
        existing = {}
        for n in range(15):
            name = 'lazydfu-0.1.3.jar' if n == 14 else f'old-{n}.jar'
            (mods/name).write_bytes(b'original selected JAR')
            existing[name] = sha(mods/name)
        manifest = {'minecraft':'1.16.5','forge':'36.2.42','release':'BLOCKED',
                    'client_optimizers':list(range(4)), 'visual_compatibility':['oculus'],
                    'client_startup_optimizer':['lazydfu-0.1.3.jar'],
                    'content_and_libraries':list(range(9)), 'jar_sha256':existing}
        report = current/'LAB-MANIFEST.json'
        report.write_text(json.dumps(manifest), encoding='utf-8')
        (root/'EGK').mkdir()
        assert restore(root)[0] == 'eligible_for_in_place_restore'
        assert len(list(mods.iterdir())) == 15
        assert restore(root, apply=True) == ('restored_in_place', 21)
        assert restore(root, apply=True) == ('already_verified', 21)
        assert (old/'.minecraft'/'saves'/'my-world').read_bytes() == b'preserve world'
        assert (root/'EGK').exists() and len(list(root.iterdir())) == 2
        (mods/'unapproved.jar').write_bytes(b'user data')
        try:
            restore(root, apply=True)
        except ValueError as exc:
            assert 'unknown user mods' in str(exc)
        else:
            raise AssertionError('modified user profile accepted')
    print('PASS: six original RP JARs restored into existing LowSpec; backups and worlds intact')


if __name__ == '__main__':
    main()
