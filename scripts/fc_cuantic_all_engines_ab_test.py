#!/usr/bin/env python3
"""Public synthetic fixtures; numbers are NOT benchmark results."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fc_cuantic_all_engines_ab import NAMES, ORDER, source_candidate, validate


class FiveEngineTest(unittest.TestCase):
    def test_order_is_palindrome_and_each_engine_is_twice(self):
        self.assertEqual(ORDER, ORDER[::-1])
        self.assertEqual(len(ORDER), 10)
        self.assertEqual({arm: ORDER.count(arm) for arm in NAMES}, {arm: 2 for arm in NAMES})

    def test_complete_public_same_job_only(self):
        rows = {arm: [dict(cpu_s=2 + index/10, rss_mib=2300,
                           mean_mspt_from_forge_tps=.8, players=0,
                           summons_confirmed=80) for index in (0, 1)] for arm in NAMES}
        results = validate(rows, 18, 6)
        self.assertEqual(len(results), 5)
        self.assertEqual(results['cuantic-source']['median_cpu_s_30s'], 2.05)
        rows['Q'][0]['players'] = 1
        with self.assertRaises(ValueError):
            validate(rows, 18, 6)
        rows['Q'][0]['players'] = 0
        rows['Q'].pop()
        with self.assertRaises(ValueError):
            validate(rows, 18, 6)
        rows['Q'].append(dict(rows['O'][0]))
        with self.assertRaises(ValueError):
            validate(rows, 34, 13)
        rows['Q'][1]['cpu_s'] = float('nan')
        with self.assertRaises(ValueError):
            validate(rows, 18, 6)

    def test_rejects_wrong_candidate_location_or_brand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/'fc-server-optimizer-ab'
            root.mkdir()
            qdir = Path(tmp)/'fc-catserver-cuantic-private'
            qdir.mkdir()
            (qdir/'CuanticEngine-private-trial.jar').write_bytes(b'public fixture')
            (qdir/'runtime-seed').mkdir()
            with patch.dict(os.environ, {'RUNNER_TEMP': tmp}), \
                 patch('fc_cuantic_all_engines_ab.check_packaged') as check, \
                 patch('fc_cuantic_all_engines_ab.validate_runtime', return_value={'libraries'}):
                jar, _, folders = source_candidate(root, qdir, 'Cuantic', 'fc-catserver-cuantic-private')
                self.assertEqual(jar.name, 'CuanticEngine-private-trial.jar')
                self.assertEqual(folders, {'libraries'})
                check.assert_called_once_with(jar, 'Cuantic')
                with self.assertRaises(ValueError):
                    source_candidate(root, qdir, 'FunCity', 'fc-catserver-cuantic-private')
                with self.assertRaises(ValueError):
                    source_candidate(root, root, 'Cuantic', 'fc-catserver-cuantic-private')


if __name__ == '__main__':
    unittest.main()
