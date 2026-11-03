#!/usr/bin/env python3
"""Synthetic overlay fixture: S+C adds no replacements to the public pack."""
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from fc_funcity_addon_canary import overlay
from fc_funcity_private_trial import ADDONS, TrialRejected


class AddonCanaryTest(unittest.TestCase):
    def test_exact_two_pins_preserve_existing_mods_plugins_and_world(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)/'fc-server-optimizer-ab'
            stage = root/'stage'
            (stage/'mods').mkdir(parents=True)
            (stage/'plugins').mkdir()
            (stage/'lab-world').mkdir()
            (stage/'lab-world'/'level.dat').write_bytes(b'WORLD')
            (stage/'plugins'/'RP.jar').write_bytes(b'PLUGIN')
            for i in range(18):
                (stage/'mods'/f'{i}.jar').write_bytes(b'RP'+str(i).encode())
            names = list(ADDONS)
            paths = [root/name for name in names]
            for i, path in enumerate(paths):
                path.write_bytes(b'OPT'+str(i).encode())
            pins = {p.name: (hashlib.sha256(p.read_bytes()).hexdigest(), len(p.read_bytes()))
                    for p in paths}
            with patch.dict(ADDONS, pins, clear=True):
                candidate = root/'candidate'
                shutil.copytree(stage, candidate)
                overlay(stage, candidate, paths, root/'runtime-seed')
                self.assertEqual(len(list((candidate/'mods').glob('*.jar'))), 20)
                self.assertEqual(len(list((stage/'mods').glob('*.jar'))), 18)
                for name in names:
                    self.assertEqual((candidate/'mods'/name).read_bytes(), (root/name).read_bytes())
                self.assertEqual((candidate/'plugins'/'RP.jar').read_bytes(), b'PLUGIN')
                self.assertEqual((candidate/'lab-world'/'level.dat').read_bytes(), b'WORLD')
                with self.assertRaises(TrialRejected):
                    overlay(stage, root/'another', paths[:1], root/'runtime-seed')
                paths[0].write_bytes(b'CHANGED')
                with self.assertRaises(TrialRejected):
                    overlay(stage, root/'another', paths, root/'runtime-seed')


if __name__ == '__main__':
    unittest.main()
