#!/usr/bin/env python3
"""Synthetic Forge metadata differences without publishing raw archive bytes."""
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path

repo=Path(__file__).resolve().parent.parent
names=json.loads((repo/'agent/FUNCITY-RP-LITE-SELECTIE.json').read_text())['retained_in_future_target']
with tempfile.TemporaryDirectory(prefix='fc-metadata-') as temp:
    client=Path(temp)/'client'; server=Path(temp)/'server'
    client.mkdir(); server.mkdir()
    for index,name in enumerate(names):
        for folder in (client,server):
            with zipfile.ZipFile(folder/name,'w') as jar:
                jar.writestr('META-INF/mods.toml', 'secret config AAA' if (index==0 and folder==server) else 'normal')
                jar.writestr('META-INF/MANIFEST.MF','private BBB' if (index==1 and folder==server) else 'normal')
    script=repo/'scripts/fc_forge_metadata_parity.ps1'
    p=subprocess.run(['pwsh','-NoProfile','-File',str(script),'-ClientMods',str(client),
                      '-ServerMods',str(server),'-Manifest',str(repo/'agent/FUNCITY-RP-LITE-SELECTIE.json')],
                     capture_output=True,text=True,timeout=15)
    assert p.returncode==0, p.returncode
    assert 'MODS_TOML_DIFFERENT=1' in p.stdout and 'MANIFEST_DIFFERENT=1' in p.stdout
    for private in ('secret config','private BBB',temp):
        assert private not in p.stdout+p.stderr
    print('PASS: metadata parity isolates mods.toml/manifest differences without printing private bytes')
