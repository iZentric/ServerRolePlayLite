#!/usr/bin/env python3
"""Only synthetic Prism files; never touches the user's PC."""
import io
import json
from pathlib import Path
import tempfile
import zipfile

from fc_pc_lowspec_lazy import JAR, PROFILE, add_lazy, sha


def fake_jar():
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as zipout:
        zipout.writestr('META-INF/MANIFEST.MF', 'Manifest-Version: 1.0\n')
        zipout.writestr('META-INF/mods.toml', '[[mods]]\nmodId="lazydfu"\n')
        zipout.writestr('data.bin', b'valid test fixture' * 100)
    return data.getvalue()


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)/'instances'
        root.mkdir()
        source = root/'FunCity Old'
        source_mods = source/'.minecraft'/'mods'
        source_mods.mkdir(parents=True)
        (source/'mmc-pack.json').write_text(json.dumps({'components': [
            {'uid':'net.minecraft','version':'1.16.5'},
            {'uid':'net.minecraftforge','version':'36.2.42'}]}), encoding='utf-8')
        (source_mods/JAR).write_bytes(fake_jar())
        profile = root/PROFILE
        mods = profile/'.minecraft'/'mods'
        mods.mkdir(parents=True)
        pinned = {}
        for i in range(14):
            name = f'fixture-{i}.jar'
            (mods/name).write_bytes(b'not a real mod')
            pinned[name] = sha(mods/name)
        manifest = {'minecraft':'1.16.5', 'forge':'36.2.42', 'release':'BLOCKED',
                    'content_and_libraries':list(range(9)), 'client_optimizers':list(range(4)),
                    'visual_compatibility':['Oculus'], 'jar_sha256': pinned}
        report = profile/'LAB-MANIFEST.json'
        report.write_text(json.dumps(manifest), encoding='utf-8')
        other = root/'EGK'
        other.mkdir()
        assert add_lazy(root)[0] == 'eligible_for_in_place_addition'
        assert not (mods/JAR).exists()
        assert add_lazy(root, apply=True)[0] == 'added_in_place'
        assert add_lazy(root, apply=True)[0] == 'already_verified'
        updated = json.loads(report.read_text())
        assert updated['jar_sha256'][JAR] == sha(mods/JAR)
        assert (source_mods/JAR).exists() and other.exists()
        (mods/'unexpected.jar').write_bytes(b'keep')
        try:
            add_lazy(root, apply=True)
        except ValueError as exc:
            assert 'unexpected mod files' in str(exc)
        else:
            raise AssertionError('accepted modified user profile')
    print('PASS: LazyDFU added only to existing LowSpec; idempotent; unknown user files refused')


if __name__ == '__main__':
    main()
