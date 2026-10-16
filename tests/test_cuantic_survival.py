"""Static screens do not substitute for a real Forge client and mob spawning."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
import warnings
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cuantic_survival_candidate import create_candidate, digest, OLD_RULES, PROFILES, SPAWN
from cuantic_survival_rules import load, review, review_pack
from build_lite import BUKKIT_YML, SERVER_PROPERTIES, SPIGOT_YML, write_start_scripts


class SurvivalRules(unittest.TestCase):
    def test_release_snapshot_is_blocked_but_new_build_keeps_vanilla_spawning(self):
        self.assertEqual(load(ROOT / "analysis/chk.md"), OLD_RULES)
        self.assertTrue(review(load(ROOT / "analysis/chk.md"))[0].startswith("BLOCK:"))
        # Exercise the actual builder routine, not a grep of its source. A fresh
        # server is staging only until Forge client and RAM tests are performed.
        with tempfile.TemporaryDirectory() as folder:
            write_start_scripts(folder, 'CatServer-1.16.5-1d8d6313-server.jar')
            spawn = Path(folder) / SPAWN
            self.assertEqual(load(spawn), [])
            self.assertTrue(review(load(spawn))[0].startswith("NEVALIDAT:"))
            properties = (Path(folder) / 'server.properties').read_text()
            self.assertIn('gamemode=survival\n', properties)
            self.assertIn('spawn-monsters=true\n', properties)
            for name in ('start.sh', 'start.bat'):
                banner = (Path(folder) / name).read_text()
                self.assertIn('CatServer upstream', banner)
                self.assertNotIn('zero lag', banner)
                self.assertNotIn('motor forjat de noi', banner)

    def test_builder_does_not_silently_disable_end_spawner_ai_or_redstone(self):
        # Same constants that are written to bukkit.yml/spigot.yml in the ZIP.
        self.assertIn('allow-end: true\n', BUKKIT_YML)
        self.assertIn('nerf-spawner-mobs: false\n', SPIGOT_YML)
        self.assertIn('zombie-aggressive-towards-villager: true\n', SPIGOT_YML)
        self.assertIn('hopper-transfer: 8\n', SPIGOT_YML)
        self.assertIn('hopper-check: 1\n', SPIGOT_YML)
        self.assertIn('hopper-amount: 1\n', SPIGOT_YML)

    def test_archive_gate_rejects_hidden_survival_losses_and_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'built.zip'

            def make_pack(properties=SERVER_PROPERTIES, bukkit=BUKKIT_YML, spigot=SPIGOT_YML):
                with ZipFile(path, 'w') as archive:
                    archive.writestr(SPAWN, '[]')
                    archive.writestr('server.properties', properties)
                    archive.writestr('bukkit.yml', bukkit)
                    archive.writestr('spigot.yml', spigot)
                return review_pack(path)

            self.assertEqual(make_pack(), [])
            self.assertTrue(any('allow-end' in x for x in make_pack(bukkit=BUKKIT_YML.replace('allow-end: true', 'allow-end: false'))))
            self.assertTrue(any('nerf-spawner-mobs' in x for x in make_pack(spigot=SPIGOT_YML.replace('nerf-spawner-mobs: false', 'nerf-spawner-mobs: true'))))
            self.assertTrue(any('difficulty' in x for x in make_pack(properties=SERVER_PROPERTIES.replace('difficulty=normal', 'difficulty=peaceful'))))
            self.assertTrue(any('spawn-monsters' in x for x in make_pack(properties=SERVER_PROPERTIES + '\nspawn-monsters=false\n')))

    def test_candidate_profiles_not_certified_and_malformed_denies_blocked(self):
        for profile in PROFILES.values():
            self.assertTrue(review(profile)[0].startswith("NEVALIDAT:"))
        self.assertTrue(review([{"result": "deny"}])[0].startswith("BLOCK:"))
        self.assertTrue(review([{"hostile": True, "result": "deny"}])[0].startswith("BLOCK:"))
        self.assertTrue(review({"result": "deny"})[0].startswith("BLOCK:"))
        self.assertTrue(review([{"hostile": True, "maxcount": 50, "result": "deny"}])[0].startswith("BLOCK:"))

    def test_candidate_only_changes_spawn_json_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            base, result = Path(folder) / 'base.zip', Path(folder) / 'staging.zip'
            with ZipFile(base, 'w') as archive:
                archive.writestr('engine.jar', b'upstream original')
                archive.writestr('mods/vehicle.jar', b'keep mod')
                archive.writestr('plugins/claims.jar', b'keep plugin')
                archive.writestr(SPAWN, json.dumps(OLD_RULES))
            self.assertEqual(load(base), OLD_RULES)
            for profile in PROFILES:
                candidate = result.with_name(profile + '.zip')
                report = create_candidate(base, candidate, profile, expected_sha=digest(base))
                self.assertEqual(report['verdict'], 'STAGING_ONLY_NOT_A_GAMEPLAY_OR_MEMORY_PASS')
                self.assertEqual(load(candidate), PROFILES[profile])
                with ZipFile(base) as old, ZipFile(candidate) as new:
                    self.assertEqual(old.namelist(), new.namelist())
                    for name in old.namelist():
                        if name == SPAWN:
                            self.assertEqual(json.loads(new.read(name)), PROFILES[profile])
                        else:
                            self.assertEqual(old.read(name), new.read(name))
                with self.assertRaisesRegex(ValueError, 'new, separate'):
                    create_candidate(base, candidate, profile, expected_sha=digest(base))
            with self.assertRaisesRegex(ValueError, 'new, separate'):
                create_candidate(base, base, 'vanilla', expected_sha=digest(base))
            with self.assertRaisesRegex(ValueError, 'pinned'):
                create_candidate(base, result, 'vanilla', expected_sha='wrong')
            self.assertFalse(result.exists())

    def test_release_workflow_cannot_auto_publish_inverted_cap(self):
        workflow = (ROOT / '.github/workflows/build-lite.yml').read_text()
        self.assertNotIn('  push:', workflow)
        self.assertIn('default: false', workflow)
        self.assertIn('if: ${{ inputs.publish_staging == true }}', workflow)
        self.assertNotIn('gh release delete lite', workflow)
        self.assertIn('gh release create "cuantic-staging-', workflow)
        self.assertLess(workflow.index('cuantic_survival_rules.py "$pack"'),
                        workflow.index('gh release create "cuantic-staging-'))

    def test_unknown_rule_and_duplicate_members_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            base, result = Path(folder) / 'base.zip', Path(folder) / 'staging.zip'
            with ZipFile(base, 'w') as archive:
                archive.writestr(SPAWN, '[]')
            with self.assertRaisesRegex(ValueError, 'differs'):
                create_candidate(base, result, 'vanilla', expected_sha=digest(base))
            self.assertFalse(result.exists())
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                with ZipFile(base, 'w') as archive:
                    archive.writestr(SPAWN, json.dumps(OLD_RULES))
                    archive.writestr(SPAWN, json.dumps(OLD_RULES))
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                create_candidate(base, result, 'vanilla', expected_sha=digest(base))
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                load(base)
            self.assertFalse(result.exists())


if __name__ == '__main__':
    unittest.main()
