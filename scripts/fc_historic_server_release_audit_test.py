#!/usr/bin/env python3
"""Fixture-only tests; never download, extract, or execute historic server files."""
import hashlib
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
import warnings
import zipfile

from fc_historic_server_release_audit import audit


class HistoricServerZipAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'fixture.zip'

    def create(self, entries):
        with warnings.catch_warnings(), zipfile.ZipFile(self.path, 'w') as z:
            warnings.simplefilter('ignore', UserWarning)
            for name, value in entries:
                z.writestr(name, value)
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_counts_only_and_no_extraction(self):
        expected = self.create([
            ('FunCity/mods/a.jar', b'fixture'), ('FunCity/plugins/b.jar', b'fixture'),
            ('FunCity/engine.jar', b'fixture'), ('FunCity/world/level.dat', b'private fixture'),
            ('FunCity/ops.json', b'private fixture'), ('FunCity/server.properties', b'private fixture'),
            ('FunCity/java/bin/java.exe', b'fixture'), ('FunCity/start.bat', b'fixture'),
            ('FunCity/libraries/forge.jar', b'fixture'),
            ('FunCity/mods/archive/extra.jar', b'fixture'),
            ('FunCity/server-bundle.zip', b'fixture archive')])
        result = audit(self.path, expected)
        self.assertEqual((result['mod_jars'], result['plugin_jars'], result['other_jars']), (1, 1, 3))
        self.assertEqual((result['mod_jars_in_deeper_folders'], result['library_jars']), (1, 1))
        self.assertEqual((result['nested_archives'], result['nested_archive_bytes']), (1, 15))
        self.assertEqual((result['world_entries'], result['sensitive_entries']), (1, 3))
        self.assertEqual((result['scripts'], result['java_runtime_entries']), (2, 1))
        self.assertFalse((Path(self.tmp.name) / 'FunCity').exists())

    def test_detect_unsafe_paths_duplicates_and_links(self):
        link = zipfile.ZipInfo('FunCity/mods/link.jar')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        expected = self.create([('../world/level.dat', b'secret'), ('C:/bad.jar', b'bad'),
                                ('FunCity//mods/bad.jar', b'bad'),
                                ('FunCity/mods/a.jar', b'fixture'),
                                ('funcity/MODS/A.jar', b'alias'), (link, b'../x')])
        result = audit(self.path, expected)
        self.assertEqual(result['unsafe_paths'], 3)
        self.assertEqual(result['duplicate_paths'], 1)
        self.assertEqual(result['symlinks'], 1)

    def test_public_target_matches_outer_and_nested_without_inner_extraction(self):
        target = Path(__file__).resolve().parents[1] / 'agent/FUNCITY-SERVER-TARGET-28.json'
        names = json.loads(target.read_text(encoding='utf-8'))['mods']
        inner_buffer = io.BytesIO()
        with zipfile.ZipFile(inner_buffer, 'w') as inner:
            inner.writestr('old-backup/mods/' + names[1], b'fixture nested JAR')
            inner.writestr('old-backup/plugins/private.jar', b'fixture plugin')
        expected = self.create([('server/mods/' + names[0], b'fixture outer JAR'),
                                ('server/data/snapshot.zip', inner_buffer.getvalue())])
        result = audit(self.path, expected, target)
        self.assertEqual((result['target_outer_matches'], result['target_nested_matches'],
                          result['target_combined_matches'], result['target_missing_count']),
                         (1, 1, 2, 26))
        self.assertEqual((result['nested_zip_inspected'], result['nested_mod_jars'],
                          result['nested_plugin_jars']), (1, 1, 1))
        self.assertFalse((Path(self.tmp.name) / 'server').exists())

    def test_sha_required_and_symlink_refused(self):
        expected = self.create([('mods/a.jar', b'fixture')])
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            audit(self.path, '0' * 64)
        self.assertEqual(audit(self.path, expected)['mod_jars'], 1)
        link = Path(self.tmp.name) / 'link.zip'
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, 'regular file'):
            audit(link, expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
