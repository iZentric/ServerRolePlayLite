#!/usr/bin/env python3
"""Tiny synthetic ZIP fixtures only; no Minecraft or licensed binaries."""
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

from fc_funcity_compiled_engine_gate import BRIDGE, IDENTITY, InvalidEngine, check


def fixture(folder, *, inner=True, wrong=False, second=False):
    folder = Path(folder)
    classes = folder / 'classes'
    payload = {name: b'compiled:FunCity:' + name.encode() for name in IDENTITY}
    payload[BRIDGE] = b'compiled:block-place-bridge' * 10
    for name, data in payload.items():
        target = classes / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    data = io.BytesIO()
    with zipfile.ZipFile(data, 'w') as embedded:
        for name, content in payload.items():
            if not (wrong and name == BRIDGE):
                embedded.writestr(name, content)
    jar = folder / 'server.jar'
    with zipfile.ZipFile(jar, 'w') as launcher:
        launcher.writestr('META-INF/MANIFEST.MF', b'Main-Class: catserver.server.CatServerLaunch\n')
        if inner:
            launcher.writestr('data/forge-1.16.5-36.2.39-universal.jar', data.getvalue())
            if second:
                launcher.writestr('data/another-universal.jar', data.getvalue())
        # A false positive in the launcher root must never bypass nested checks.
        for name, content in payload.items():
            launcher.writestr(name, content)
    return jar, classes


class CompiledGateTest(unittest.TestCase):
    def test_nested_classes_match(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(check(*fixture(temp)))

    def test_launcher_root_is_insufficient(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(InvalidEngine):
                check(*fixture(temp, inner=False))

    def test_missing_embedded_bridge_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(InvalidEngine):
                check(*fixture(temp, wrong=True))

    def test_ambiguous_embedded_jars_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(InvalidEngine):
                check(*fixture(temp, second=True))

    def test_brand_only_in_source_not_sufficient(self):
        with tempfile.TemporaryDirectory() as temp:
            jar, classes = fixture(temp)
            (classes / 'catserver/server/CatServer.class').write_bytes(b'CatServer-only')
            with self.assertRaises(InvalidEngine):
                check(jar, classes)


if __name__ == '__main__':
    unittest.main()
