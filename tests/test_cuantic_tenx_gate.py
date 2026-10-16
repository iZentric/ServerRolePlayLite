"""Do not advertise 10x from empty fake players, a changed pack or a good boot."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cuantic_tenx_gate import evaluate


def row(players, jar, run_id):
    return dict(pack_sha256='pack', host_id='same-host', jdk='17', world_id='seed-and-fixture',
                settings_sha256='config', workload_id='survival-rp-vehicles', duration_s=600,
                jar_sha256=jar, players=players, confirmed_forge_clients=players,
                run_id=run_id, server_log_sha256='a' * 64, client_log_sha256='b' * 64,
                vehicles_ok=True, survival_ok=True, plugins_ok=True, tps=19.9, p95_ms=42)


def arms(baseline_players=1, candidate_players=10):
    return {'baseline': [row(baseline_players, 'old', f'baseline-{i}') for i in range(3)],
            'candidate': [row(candidate_players, 'new', f'candidate-{i}') for i in range(3)]}


class ClaimGate(unittest.TestCase):
    def test_no_data_and_prior_zero_players_cannot_win(self):
        self.assertEqual(evaluate({})['verdict'], 'NEMASURAT')
        self.assertEqual(evaluate(arms(0, 25))['verdict'], 'NEMASURAT')

    def test_repeated_capacity_only_not_resource_ratio(self):
        data = arms()
        result = evaluate(data)
        self.assertEqual(result['verdict'], '10X_PRELIMINAR')
        self.assertNotIn('cpu_ratio', result)
        self.assertIn('not proof', result['limits'])
        self.assertEqual(evaluate(arms(1, 9))['verdict'], 'SUB_TINTA')

    def test_refuses_different_conditions_fake_claims_and_regressions(self):
        good = arms()
        for changes in ({'pack_sha256': 'new-pack'}, {'confirmed_forge_clients': 0},
                        {'vehicles_ok': False}, {'p95_ms': 51}, {'tps': 19.4},
                        {'jar_sha256': 'old'}, {'server_log_sha256': 'bad'},
                        {'run_id': 'baseline-0'}):
            case = deepcopy(good)
            case['candidate'][1].update(changes)
            self.assertEqual(evaluate(case)['verdict'], 'NEMASURAT', changes)
        identical = deepcopy(good)
        for trial in identical['candidate']:
            trial['jar_sha256'] = 'old'
        self.assertEqual(evaluate(identical)['verdict'], 'NEMASURAT')


if __name__ == '__main__':
    unittest.main()
