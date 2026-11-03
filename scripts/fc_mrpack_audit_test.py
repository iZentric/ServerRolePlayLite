#!/usr/bin/env python3
"""Offline synthetic Modrinth-pack structural fixtures; NO game/client execution."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from fc_client_audit import DEPENDENCIES, ESSENTIAL, GAMEPLAY
from fc_mrpack_audit import audit_pack


class MrpackAuditTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fc-mrpack-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = self.root / 'fixture.mrpack'
        prefixes = set(ESSENTIAL + GAMEPLAY + tuple(DEPENDENCIES))
        prefixes.update(c for children in DEPENDENCIES.values() for c in children)
        self.names = sorted(p + 'test.jar' for p in prefixes)
        self.index = {'formatVersion': 1, 'game': 'minecraft', 'name': 'Test Lite',
                      'versionId': 'fixture', 'dependencies': {'minecraft': '1.16.5', 'forge': '36.2.39'},
                      'files': [{'path': 'mods/' + name,
                                 'hashes': {'sha512': hashlib.sha512(name.encode()).hexdigest(),
                                            'sha1': hashlib.sha1(name.encode()).hexdigest()},
                                 'fileSize': 1234, 'downloads': ['https://example.test/' + name]}
                                for name in self.names]}
        names = ', '.join(self.names)
        self.history = self.root / 'history.txt'
        self.history.write_text('lista: ' + names + '\nlista: ' + names + '\n')

    def build(self, index=None, extras=None):
        with zipfile.ZipFile(self.pack, 'w') as z:
            z.writestr('modrinth.index.json', json.dumps(index or self.index))
            for path, data in (extras or {}).items():
                z.writestr(path, data)
        return self.pack

    def test_matching_pack_reports_metadata_not_fps(self):
        result = audit_pack(self.build(extras={'overrides/config/oculus.properties': 'enableShaders=false'}), self.history)
        self.assertTrue(result['historical_names_match'])
        self.assertEqual(result['client_mod_count'], len(self.names))
        self.assertEqual(result['remote_download_bytes_declared'], len(self.names) * 1234)
        self.assertEqual(result['fps_on_old_laptop'], 'NEMASURAT')

    def test_rejects_missing_clumps_unsafe_and_server_only(self):
        data = copy.deepcopy(self.index)
        data['files'] = [f for f in data['files'] if not f['path'].startswith('mods/Clumps-')]
        with self.assertRaisesRegex(ValueError, 'absent'):
            audit_pack(self.build(data), self.history)
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            audit_pack(self.build(extras={'overrides/../mods/escape.jar': b'dummy'}))
        data = copy.deepcopy(self.index)
        data['files'][0]['env'] = {'client': 'unsupported'}
        with self.assertRaisesRegex(ValueError, 'server-only'):
            audit_pack(self.build(data))

    def test_rejects_unpinned_duplicate_or_added_mod(self):
        data = copy.deepcopy(self.index)
        data['files'][0]['hashes'].pop('sha512')
        with self.assertRaisesRegex(ValueError, 'SHA512'):
            audit_pack(self.build(data))
        data = copy.deepcopy(self.index)
        data['files'][0]['downloads'] = ['http://insecure.test/mod.jar']
        with self.assertRaisesRegex(ValueError, 'secure download'):
            audit_pack(self.build(data))
        with self.assertRaisesRegex(ValueError, 'collides'):
            audit_pack(self.build(extras={'overrides/' + self.index['files'][0]['path']: b'dummy'}))
        data = copy.deepcopy(self.index)
        data['files'].append({'path': 'mods/new-client-only.jar', 'hashes': {'sha512': 'a'*128, 'sha1': 'b'*40},
                              'fileSize': 12, 'downloads': ['https://example.test/new.jar']})
        with self.assertRaisesRegex(ValueError, 'drift'):
            audit_pack(self.build(data), self.history)


if __name__ == '__main__':
    unittest.main(verbosity=2)
