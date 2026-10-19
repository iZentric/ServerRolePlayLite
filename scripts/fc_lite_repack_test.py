#!/usr/bin/env python3
"""Synthetic, offline pack transformer tests; no Windows, Forge or network."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from fc_client_audit import INVENTORY
from fc_lite_repack import repack
from fc_mrpack_audit import audit_pack

REPO = Path(__file__).resolve().parents[1]


class LeanRepackTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fc-lean-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'base.mrpack'
        self.output = self.root / 'candidate.mrpack'
        self.decisions = REPO / 'agent/DECIZII.md'
        self.history = REPO / 'diag/pc-client.txt'
        names = INVENTORY.findall(self.history.read_text())[0].split(', ')
        self.assertEqual(len(names), 25)
        self.names = names
        self.index = {'formatVersion': 1, 'game': 'minecraft', 'name': 'FunCity',
                      'versionId': 'test',
                      'dependencies': {'minecraft': '1.16.5', 'forge': '36.2.39'},
                      'files': [{'path': 'mods/' + name,
                                 'hashes': {'sha1': hashlib.sha1(name.encode()).hexdigest(),
                                            'sha512': hashlib.sha512(name.encode()).hexdigest()},
                                 'downloads': ['https://example.invalid/' + name],
                                 'fileSize': 100}
                                for name in names if not name.startswith('out_of_sight-')]}
        self.build()

    def build(self, extra=None):
        with zipfile.ZipFile(self.source, 'w') as z:
            z.writestr('modrinth.index.json', json.dumps(self.index))
            z.writestr('overrides/mods/out_of_sight-1.16.4-1.0.1.jar', b'fixture JAR')
            z.writestr('client-overrides/options.txt', 'renderDistance:5\n')
            for name, contents in (extra or {}).items():
                z.writestr(name, contents)
        return hashlib.sha256(self.source.read_bytes()).hexdigest()

    def run_pack(self, sha=None):
        return repack(self.source, sha or self.build(), self.output,
                      self.decisions, self.history)

    def test_exact_2_mod_reduction_preserves_other_files_and_source(self):
        pin = hashlib.sha256(self.source.read_bytes()).hexdigest()
        report = repack(self.source, pin, self.output, self.decisions, self.history)
        self.assertEqual(report['removed'], ['entitycollisionfpsfix-1.16-1.0.1.jar',
                                             'out_of_sight-1.16.4-1.0.1.jar'])
        self.assertEqual(report['client_mod_count'], 24)
        self.assertEqual(report['added_remote'], 'voicechat-forge-1.16.5-2.3.23.jar')
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), pin)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(z.read('client-overrides/options.txt'), b'renderDistance:5\n')
            self.assertNotIn('overrides/mods/out_of_sight-1.16.4-1.0.1.jar', z.namelist())
            manifest = json.loads(z.read('modrinth.index.json'))
            self.assertNotIn('entitycollisionfpsfix', json.dumps(manifest))
            voice=[f for f in manifest['files'] if f['path'].startswith('mods/voicechat-')]
            self.assertEqual(len(voice), 1)
            self.assertEqual(voice[0]['fileSize'], 7839781)
            self.assertEqual(voice[0]['env']['client'], 'required')
        self.assertEqual(audit_pack(self.output)['client_mod_count'], 24)

    def test_unpinned_voice_metadata_is_rejected(self):
        fake = self.root / 'fake-voice.json'
        data = json.loads((REPO / 'agent/voicechat-1.16.5-2.3.23.json').read_text())
        data['download'] = 'https://bad.invalid/unverified.jar'
        fake.write_text(json.dumps(data))
        pin = hashlib.sha256(self.source.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'unverified'):
            repack(self.source, pin, self.output, self.decisions, self.history, fake)
        self.assertFalse(self.output.exists())

    def test_wrong_pin_or_existing_destination_never_overwrites(self):
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            repack(self.source, '0'*64, self.output, self.decisions, self.history)
        self.assertFalse(self.output.exists())
        self.output.write_bytes(b'keep me')
        with self.assertRaisesRegex(ValueError, 'destination must be new'):
            repack(self.source, hashlib.sha256(self.source.read_bytes()).hexdigest(),
                   self.output, self.decisions, self.history)
        self.assertEqual(self.output.read_bytes(), b'keep me')

    def test_wrong_baseline_or_extra_mod_fails_closed(self):
        self.index['files'] = [x for x in self.index['files']
                               if not x['path'].endswith('Clumps-6.0.0.28.jar')]
        pin = self.build()
        with self.assertRaises(ValueError):
            repack(self.source, pin, self.output, self.decisions, self.history)
        self.assertFalse(self.output.exists())
        self.index['files'].append({'path': 'mods/Clumps-6.0.0.28.jar',
                                    'hashes': {'sha1':'a'*40,'sha512':'a'*128},
                                    'downloads': ['https://example.invalid/clumps'],
                                    'fileSize': 100})
        self.index['files'].append({'path': 'mods/unwanted.jar',
                                    'hashes': {'sha1':'a'*40,'sha512':'a'*128},
                                    'downloads': ['https://example.invalid/x'],
                                    'fileSize': 100})
        pin = self.build()
        with self.assertRaisesRegex(ValueError, 'drift'):
            repack(self.source, pin, self.output, self.decisions, self.history)

    def test_missing_target_and_unsafe_override_fail_without_output(self):
        self.index['files'] = [x for x in self.index['files']
                               if not x['path'].startswith('mods/entitycollisionfpsfix-')]
        pin = self.build()
        with self.assertRaises(ValueError):
            repack(self.source, pin, self.output, self.decisions, self.history)
        self.assertFalse(self.output.exists())
        self.index['files'].append({'path':'mods/entitycollisionfpsfix-1.16-1.0.1.jar',
                                    'hashes': {'sha1':'a'*40,'sha512':'a'*128},
                                    'downloads':['https://example.invalid/collision'], 'fileSize':100})
        pin = self.build({'overrides/../unwanted.txt': 'unsafe'})
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            repack(self.source, pin, self.output, self.decisions, self.history)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
