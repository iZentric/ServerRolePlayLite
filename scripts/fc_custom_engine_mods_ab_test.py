#!/usr/bin/env python3
"""Synthetic fixture only: exact custom-engine/runtime swap, no server/player."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fc_custom_engine_mods_ab import copy_trial, candidate_inputs, ORDER


class CustomSwapTest(unittest.TestCase):
    def test_only_custom_arm_gets_private_seed_and_other_arms_stay_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'fc-server-optimizer-ab'
            root.mkdir()
            stage = root/'stage'
            (stage/'mods').mkdir(parents=True)
            (stage/'plugins').mkdir()
            (stage/'libraries').mkdir()
            (stage/'mods'/'keep.jar').write_bytes(b'18 public test mods')
            (stage/'plugins'/'keep.jar').write_bytes(b'6 public test plugins')
            (stage/'libraries'/'old.jar').write_bytes(b'old engine library')
            (stage/'FunCity-1.16.5-b1.0827.jar').write_bytes(b'old engine')
            world = root/'world'
            world.mkdir()
            (world/'level.dat').write_bytes(b'generated world')
            private = Path(tmp)/'fc-catserver-private'
            private.mkdir()
            (private/'FunCityEngine-private-trial.jar').write_bytes(b'custom source engine')
            seed = private/'runtime-seed'
            (seed/'libraries').mkdir(parents=True)
            (seed/'libraries'/'new.jar').write_bytes(b'new engine library')
            with patch.dict(os.environ, {'RUNNER_TEMP': tmp}), \
                 patch('fc_custom_engine_mods_ab.check_packaged'), \
                 patch('fc_custom_engine_mods_ab.validate_runtime', return_value={'libraries'}), \
                 patch('fc_custom_engine_mods_ab.base.copy_arm') as base_copy:
                def copy_base(source, output, world_root, arm, *_):
                    import shutil
                    shutil.copytree(source, output)
                    shutil.copytree(world_root, output/'lab-world')
                    if arm == 'O':
                        (output/'FunCity-1.16.5-b1.0827.jar').write_bytes(b'official engine')
                    return output
                base_copy.side_effect = copy_base
                jar, folders = candidate_inputs(root, private)
                for arm in ORDER:
                    copy_trial(stage, root/('trial-'+arm+str(len(list(root.glob('trial-'+arm+'*'))))),
                               world, arm, 'archived.zip', 'official.jar', jar, seed, folders)
            custom = next(root.glob('trial-X*'))
            self.assertEqual((custom/'FunCity-1.16.5-b1.0827.jar').read_bytes(), b'custom source engine')
            self.assertEqual((custom/'libraries'/'new.jar').read_bytes(), b'new engine library')
            self.assertFalse((custom/'libraries'/'old.jar').exists())
            for output in root.glob('trial-*'):
                self.assertEqual((output/'mods'/'keep.jar').read_bytes(), b'18 public test mods')
                self.assertEqual((output/'plugins'/'keep.jar').read_bytes(), b'6 public test plugins')
                self.assertEqual((output/'lab-world'/'level.dat').read_bytes(), b'generated world')
                if not output.name.startswith('trial-X'):
                    self.assertEqual((output/'libraries'/'old.jar').read_bytes(), b'old engine library')
            with self.assertRaises(ValueError):
                candidate_inputs(root, root/'outside')


if __name__ == '__main__':
    unittest.main()
