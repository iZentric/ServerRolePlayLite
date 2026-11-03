#!/usr/bin/env python3
"""Tiny synthetic JAR fixtures only; no private world/mod/plugin data."""
import json
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from fc_rust_migration_inventory import InventoryError, MARKER, REPO, main, read_copy, save_private


class PrivateInventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'inactive'
        self.root.mkdir()
        (self.root/'.funcity-isolated-copy').write_text(MARKER + '\n')
        for folder, count in (('mods', 34), ('plugins', 13)):
            directory = self.root/folder
            directory.mkdir()
            for index in range(count):
                with zipfile.ZipFile(directory/f'test-{index:02}.jar', 'w') as jar:
                    if folder == 'mods':
                        jar.writestr('META-INF/mods.toml',
                                    '[[mods]]\nmodId="test%d"\n' % index +
                                    ('[[dependencies.test0]]\nmodId="library"\nmandatory=true\n'
                                     if index == 0 else ''))
                    else:
                        jar.writestr('plugin.yml', f'name: Test{index}\nmain: test.Main\n')

    def test_private_manifest_is_not_a_port_or_player_benchmark(self):
        report = read_copy(self.root)
        self.assertEqual(len(report['items']), 47)
        self.assertEqual(report['player_capacity'], 'NOT_MEASURED')
        self.assertEqual(report['engine_compatibility'], 'NOT_VERIFIED')
        self.assertTrue(all(not x['rust_equivalent_tested'] for x in report['items']))
        self.assertEqual(report['items'][0]['declared_metadata']['mod_ids'], ['test0'])
        self.assertEqual(report['items'][0]['declared_metadata']['required_mod_ids'], ['library'])
        self.assertEqual(report['items'][34]['declared_metadata']['plugin_name'], 'Test0')
        output = Path(self.tmp.name)/'private-manifest.json'
        save_private(report, output)
        self.assertEqual(os.stat(output).st_mode & 0o777, 0o600)
        self.assertEqual(json.loads(output.read_text()), report)
        with self.assertRaises(InventoryError):
            save_private(report, output)
        with self.assertRaises(InventoryError):
            save_private(report, REPO/'DO_NOT_WRITE_IN_GIT.json')

    def test_descriptor_errors_are_never_claimed_as_compatibility(self):
        first = self.root/'mods'/'test-00.jar'
        with zipfile.ZipFile(first, 'w') as jar:
            jar.writestr('META-INF/mods.toml', 'not-valid-toml')
        report = read_copy(self.root)
        self.assertEqual(report['items'][0]['declared_metadata']['status'], 'UNPARSED')
        self.assertEqual(report['items'][0]['declared_metadata']['mod_ids'], [])
        self.assertFalse(report['items'][0]['rust_equivalent_tested'])
        with zipfile.ZipFile(first, 'w') as jar:
            jar.writestr('META-INF/mods.toml', 'x' * 200001)
        with self.assertRaises(InventoryError):
            read_copy(self.root)
        first.write_bytes(b'not a real JAR')
        with self.assertRaises(InventoryError):
            read_copy(self.root)

    def test_refuse_live_or_incomplete_or_symlink(self):
        (self.root/'.funcity-isolated-copy').unlink()
        output = Path(self.tmp.name)/'must-not-exist.json'
        self.assertEqual(main(['script', str(self.root), str(output)]), 2)
        self.assertFalse(output.exists())
        with self.assertRaises(InventoryError):
            read_copy(self.root)
        (self.root/'.funcity-isolated-copy').write_text(MARKER)
        (self.root/'mods'/'test-00.jar').unlink()
        with self.assertRaises(InventoryError):
            read_copy(self.root)
        (self.root/'mods'/'test-00.jar').symlink_to(self.root/'mods'/'test-01.jar')
        with self.assertRaises(InventoryError):
            read_copy(self.root)
        (self.root/'mods'/'test-00.jar').unlink()
        (self.root/'mods'/'test-00.jar').write_bytes(b'restored fake jar')
        (self.root/'plugins').rename(self.root/'plugins-real')
        (self.root/'plugins').symlink_to(self.root/'plugins-real')
        with self.assertRaises(InventoryError):
            read_copy(self.root)


if __name__ == '__main__':
    unittest.main()
