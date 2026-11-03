#!/usr/bin/env python3
"""Synthetic-only verdict fixtures; these are NOT server measurements."""
import copy
import unittest

from fc_cuantic_synthetic_ab import verdict


def trial(cpu, tick):
    return {'cpu_s': cpu, 'mean_mspt_from_forge_tps': tick,
            'rss_mib': 2300, 'players': 0, 'summons_confirmed': 80}


class CuanticGateTest(unittest.TestCase):
    def setUp(self):
        self.rows = {'O': [trial(2.60, 1.52), trial(2.40, 1.50)],
                     'Q': [trial(2.40, 1.49), trial(2.50, 1.50)]}

    def test_passes_only_both_historical_and_same_job_budgets(self):
        self.assertTrue(verdict(self.rows)['qualified_public_screen'])
        self.rows['Q'][1]['cpu_s'] = 2.64
        self.assertFalse(verdict(self.rows)['historical_ceiling_pass'])

    def test_rejects_even_fast_absolute_candidate_if_official_faster(self):
        rows = copy.deepcopy(self.rows)
        rows['O'] = [trial(2.0, 1.40), trial(2.1, 1.41)]
        result = verdict(rows)
        self.assertTrue(result['historical_ceiling_pass'])
        self.assertFalse(result['same_job_nonregression_pass'])
        self.assertFalse(result['qualified_public_screen'])

    def test_rejects_tick_edge_or_incomplete_or_drifted_trials(self):
        rows = copy.deepcopy(self.rows)
        rows['Q'][1]['mean_mspt_from_forge_tps'] = 1.53
        self.assertFalse(verdict(rows)['qualified_public_screen'])
        rows = copy.deepcopy(self.rows)
        rows['Q'].pop()
        with self.assertRaises(ValueError):
            verdict(rows)
        rows = copy.deepcopy(self.rows)
        rows['Q'][0]['players'] = 1
        with self.assertRaises(ValueError):
            verdict(rows)
        rows = copy.deepcopy(self.rows)
        rows['Q'][0]['cpu_s'] = float('nan')
        with self.assertRaises(ValueError):
            verdict(rows)


if __name__ == '__main__':
    unittest.main()
