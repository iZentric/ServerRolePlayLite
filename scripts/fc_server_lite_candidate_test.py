#!/usr/bin/env python3
"""Synthetic server-mod candidate tests. Never accesses the PC, live server or worlds."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from fc_server_lite_candidate import decisions, stage

ROOT = Path(__file__).resolve().parents[1]


class ServerLiteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fc-server-lite-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'historical.zip'
        self.dest = self.root / 'candidate.zip'
        self.decisions = ROOT / 'agent/DECIZII.md'
        self.client = ROOT / 'diag/pc-client.txt'
        self.voice = ROOT / 'agent/voicechat-1.16.5-2.3.23.json'
        names, keep, removed = decisions(self.decisions, self.decisions, self.client, self.voice)
        self.assertEqual((len(names), len(keep), len(removed)), (36, 29, 7))
        self.names = names
        self.keep = keep
        self.removed = removed
        self.make_source()

    def make_source(self, missing=None):
        with zipfile.ZipFile(self.source, 'w') as z:
            for key, name in self.names.items():
                if key != missing:
                    z.writestr('Old server/mods/' + name, ('fixture:' + name).encode())
            z.writestr('Old server/world/level.dat', b'private-world-fixture')
            z.writestr('Old server/plugins/AuthMe/accounts.db', b'private-accounts-fixture')
            z.writestr('Old server/config/secret.txt', b'private-config-fixture')
        return hashlib.sha256(self.source.read_bytes()).hexdigest()

    def run_stage(self, sha=None):
        return stage(self.source, sha or hashlib.sha256(self.source.read_bytes()).hexdigest(),
                     self.dest, self.decisions, self.client, self.voice)

    def test_exact_29_mods_only_and_untouched_source(self):
        pin = hashlib.sha256(self.source.read_bytes()).hexdigest()
        result = self.run_stage(pin)
        self.assertEqual((result['server_mod_count'], result['shared_client_server_names'],
                          result['server_only'], result['client_only']), (29, 20, 9, 4))
        self.assertEqual(result['source_sha256'], pin)
        self.assertEqual(result['candidate_sha256'], hashlib.sha256(self.dest.read_bytes()).hexdigest())
        self.assertEqual(set(result['removed']), {self.names[n] for n in self.removed})
        with zipfile.ZipFile(self.dest) as z:
            self.assertEqual(set(z.namelist()), {'mods/' + self.names[n] for n in self.keep})
            self.assertEqual(z.testzip(), None)
            for name, jar_sha in result['kept_sha256'].items():
                self.assertEqual(hashlib.sha256(z.read('mods/' + name)).hexdigest(), jar_sha)
            self.assertNotIn(b'private-world-fixture', self.dest.read_bytes())
            self.assertNotIn(b'private-accounts-fixture', self.dest.read_bytes())
            self.assertNotIn(b'private-config-fixture', self.dest.read_bytes())
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), pin)

    def test_isolated_no_pizzaland_comparison(self):
        pin = hashlib.sha256(self.source.read_bytes()).hexdigest()
        result = stage(self.source, pin, self.dest, self.decisions, self.client,
                       self.voice, without_pizzaland=True)
        self.assertEqual((result['server_mod_count'], result['shared_client_server_names'],
                          result['server_only'], result['client_only']), (28, 19, 9, 4))
        self.assertIn('Pizzaland_v68.jar', result['removed'])
        with zipfile.ZipFile(self.dest) as z:
            self.assertNotIn('mods/Pizzaland_v68.jar', z.namelist())
            self.assertEqual(len(z.namelist()), 28)
            self.assertEqual(z.testzip(), None)
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), pin)

    def test_wrong_pin_missing_and_duplicate_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            self.run_stage('0' * 64)
        self.assertFalse(self.dest.exists())
        self.make_source(missing=next(iter(self.keep)))
        with self.assertRaisesRegex(ValueError, 'inventory'):
            self.run_stage()
        self.assertFalse(self.dest.exists())
        self.make_source()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(self.source, 'a') as z:
                z.writestr('Old server/mods/' + self.names[next(iter(self.keep))], b'duplicate')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            self.run_stage()
        self.assertFalse(self.dest.exists())

    def test_existing_destination_kept_and_no_config_copied(self):
        self.dest.write_bytes(b'existing-file')
        with self.assertRaisesRegex(ValueError, 'destination must be new'):
            self.run_stage()
        self.assertEqual(self.dest.read_bytes(), b'existing-file')

    def test_side_parity_and_decision_drift_rejected(self):
        text = self.decisions.read_text()
        mutated = self.root / 'decisions.md'
        mutated.write_text(text.replace('| S36 | `voicechat-forge-1.16.5-2.3.23.jar` | PĂSTRAT |',
                                        '| S36 | `voicechat-forge-1.16.5-2.3.23.jar` | SCOS |'))
        with self.assertRaisesRegex(ValueError, 'expected 29'):
            stage(self.source, hashlib.sha256(self.source.read_bytes()).hexdigest(),
                  self.dest, mutated, self.client, self.voice)
        mutated.write_text(text.replace('| S03 | `FastFurnace-1.16.5-4.5.0.jar` | SCOS |',
                                        '| S03 | `FastFurnace-1.16.5-4.5.0.jar` | PĂSTRAT |')
                           .replace('| S36 | `voicechat-forge-1.16.5-2.3.23.jar` | PĂSTRAT |',
                                    '| S36 | `voicechat-forge-1.16.5-2.3.23.jar` | SCOS |'))
        with self.assertRaisesRegex(ValueError, 'selection mismatch|voice'):
            stage(self.source, hashlib.sha256(self.source.read_bytes()).hexdigest(),
                  self.dest, mutated, self.client, self.voice)
        self.assertFalse(self.dest.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
