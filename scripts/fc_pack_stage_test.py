#!/usr/bin/env python3
"""Fixture tests for read-only A/B pack staging; no Java, PC, or live world."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

from fc_bench import build_stage
from fc_spawner_ab import MOD, compare


class PackStageTest(unittest.TestCase):
    def setUp(self):
        sandbox = Path('/tmp/fc-smoke')
        sandbox.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='pack-ab-test-', dir=sandbox)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.archive = self.root / 'source.zip'
        self.mod = 'mods/SpawnerFix-1.16.2-1.0.0.3.jar'
        with zipfile.ZipFile(self.archive, 'w') as z:
            z.writestr(self.mod, b'client-render-only')
            z.writestr('mods/Clumps-6.0.0.28.jar', b'xp-registries')
            z.writestr('world/level.dat', b'fixture-world')
            z.writestr('bukkit.yml', 'keep-spawn-loaded: true\n')
        self.source_hash = hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def stage(self, name, excluded=()):
        dest = self.root / name
        record = build_stage({'pack_zip': str(self.archive), 'exclude': list(excluded)}, '', str(dest))
        return dest, record

    def test_pair_only_target_differs_and_source_is_unchanged(self):
        a, no_skips = self.stage('baseline')
        b, skipped = self.stage('candidate', [self.mod])
        self.assertEqual(no_skips, {})
        self.assertEqual(skipped, {self.mod: hashlib.sha256(b'client-render-only').hexdigest()})
        self.assertTrue((a / self.mod).is_file())
        self.assertFalse((b / self.mod).exists())
        for path in ('mods/Clumps-6.0.0.28.jar', 'world/level.dat', 'bukkit.yml'):
            self.assertEqual((a / path).read_bytes(), (b / path).read_bytes())
        self.assertEqual(hashlib.sha256(self.archive.read_bytes()).hexdigest(), self.source_hash)

    def test_fail_closed_missing_duplicate_unsafe_and_dirty_stage(self):
        for excluded in (['mods/not-there.jar'], ['../world/level.dat'], [self.mod, self.mod]):
            with self.subTest(excluded=excluded), self.assertRaises(ValueError):
                self.stage('bad-' + str(len(excluded)), excluded)
        with self.assertRaises(ValueError):
            build_stage({'pack_zip': str(self.archive), 'exclude': [self.mod]}, '',
                        str(self.root.parent.parent / 'outside-fc-smoke'))
        dirty = self.root / 'dirty'
        dirty.mkdir()
        (dirty / self.mod).parent.mkdir()
        (dirty / self.mod).write_bytes(b'stale')
        with self.assertRaises(ValueError):
            build_stage({'pack_zip': str(self.archive), 'exclude': [self.mod]}, '', str(dirty))
        self.assertEqual((dirty / self.mod).read_bytes(), b'stale')

    def test_sha_pin_rejected_before_stage_or_java(self):
        engine = self.root / 'engine.jar'
        engine.write_bytes(b'fixture-engine-not-bootable')
        result_dir = self.root / 'must-not-be-created'
        runner = Path(__file__).with_name('fc_spawner_ab.py')
        p = subprocess.run([sys.executable, str(runner), '--pack', str(self.archive),
                            '--pack-sha256', '0' * 64, '--engine', str(engine),
                            '--engine-sha256', hashlib.sha256(engine.read_bytes()).hexdigest(),
                            '--run-dir', str(result_dir)], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('SHA256 mismatch', p.stderr)
        self.assertFalse(result_dir.exists())

    def test_comparison_requires_same_pack_world_and_one_mod_only(self):
        base = dict(status='MASURAT', probate_reusite=3, critice_total=0,
                    pack_sha256_actual=self.source_hash, pack_sha256_asteptat=self.source_hash,
                    world_start_identical_each_trial=True, world_snapshot_sha256='abc',
                    pack_mods=36, pack_plugins=14, overrides={'view-distance': '5'},
                    excluded_mods_test_only={})
        candidate = dict(base, pack_mods=35, excluded_mods_test_only={MOD: 'modhash'})
        self.assertTrue(compare(base, candidate, 'modhash')['structural_pair_valid'])
        for change in ({'pack_mods': 36}, {'world_snapshot_sha256': 'other'},
                       {'pack_sha256_actual': 'other'}, {'critice_total': 1},
                       {'excluded_mods_test_only': {}}, {'pack_mods': None}):
            with self.subTest(change=change):
                self.assertFalse(compare(base, dict(candidate, **change), 'modhash')['structural_pair_valid'])

    def test_fail_closed_ambiguous_or_unsafe_archive(self):
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Duplicate name:', category=UserWarning)
            with zipfile.ZipFile(self.archive, 'a') as z:
                z.writestr(self.mod, b'different-copy')
        with self.assertRaises(ValueError):
            self.stage('ambiguous', [self.mod])
        with zipfile.ZipFile(self.archive, 'w') as z:
            z.writestr('../world/level.dat', b'escape')
            z.writestr(self.mod, b'mod')
        with self.assertRaises(ValueError):
            self.stage('traversal', [self.mod])
        self.assertFalse((self.root / 'world').exists())
        with zipfile.ZipFile(self.archive, 'w') as z:
            link = zipfile.ZipInfo('mods/link.jar')
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            z.writestr(link, '../world/level.dat')
            z.writestr(self.mod, b'mod')
        with self.assertRaises(ValueError):
            self.stage('symlink', [self.mod])


if __name__ == '__main__':
    unittest.main(verbosity=2)
