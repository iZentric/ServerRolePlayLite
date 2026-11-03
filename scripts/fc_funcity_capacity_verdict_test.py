#!/usr/bin/env python3
"""Artificial fixtures ONLY: verify gate semantics; never cite as benchmark."""
import copy
import json
import unittest

from fc_funcity_capacity_verdict import InvalidEvidence, unique_keys, verify
from fc_funcity_private_trial import ADDONS


def trial(arm, players, engine, **changes):
    sample = dict(arm=arm, engine_sha256=engine, logged_in_players=players,
                  measured_seconds=1200, warmup_seconds=300, tps=19.8,
                  mspt_p95=23, mspt_p99=38, rss_peak_mib=2600,
                  cpu_total_percent=65, uplink_percent=50, critical_errors=0,
                  auth_ok=True, voice_ok=True, vehicles_ok=True, rp_ok=True,
                  memory_stable=True, gc_stable=True, clean_restart_ok=True,
                  backup_restore_ok=True)
    sample.update(changes)
    return sample


def fixture():
    engines = {"baseline": "a" * 64, "candidate": "b" * 64}
    data = {"schema": 1,
            "environment": dict(java_major=11, ram_limit_mib=3072,
                                mod_jars=34, plugin_jars=13,
                                world_kind="private-rp-copy",
                                clients="real-forge-1.16.5",
                                hardware_kind="isolated-host-equivalent",
                                pack_sha256="c" * 64, world_sha256="d" * 64,
                                scenario_sha256="e" * 64, hardware_sha256="f" * 64),
            "engines": engines, "levels": []}
    for players in (5, 10):
        arms = ("baseline", "candidate", "candidate", "baseline")
        data["levels"].append(dict(players=players,
                                   trials=[trial(arm, players, engines[arm]) for arm in arms]))
    # Two measured baseline trials fail the 10-player rung; candidate passes it.
    for i in (0, 3):
        data["levels"][1]["trials"][i]["mspt_p95"] = 40
        data["levels"][1]["trials"][i]["mspt_p99"] = 42
    return data


def fixture_2cpu_12gb():
    """Synthetic declarations, never measurements from a real player."""
    data = fixture()
    data["schema"] = 2
    env = data["environment"]
    env.update(cpu_logical=2, ram_limit_mib=12288, jvm_xmx_mib=8192)
    for level in data["levels"]:
        for item in level["trials"]:
            item.update(rss_peak_mib=9000, hardware_sha256=env["hardware_sha256"],
                        jvm_xmx_mib=env["jvm_xmx_mib"])
    return data


class VerdictTest(unittest.TestCase):
    def test_artificial_positive(self):
        self.assertEqual(verify(fixture()), (5, 10))

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(InvalidEvidence):
            json.loads('{"schema":1,"schema":1}', object_pairs_hook=unique_keys)

    def reject(self, transform):
        data = copy.deepcopy(fixture())
        transform(data)
        with self.assertRaises(InvalidEvidence):
            verify(data)

    def test_no_real_client(self):
        self.reject(lambda d: d["environment"].update(clients="fake-player"))

    def test_incomplete_pack(self):
        self.reject(lambda d: d["environment"].update(mod_jars=18))

    def test_unverified_world(self):
        self.reject(lambda d: d["environment"].update(world_sha256="not-a-hash"))

    def test_wrong_trial_order(self):
        self.reject(lambda d: d["levels"][0]["trials"].sort(key=lambda t: t["arm"]))

    def test_one_baseline_pass_does_not_certify_rung(self):
        self.reject(lambda d: d["levels"][1]["trials"][3].update(mspt_p95=25))

    def test_same_highest_capacity(self):
        self.reject(lambda d: [d["levels"][1]["trials"][i].update(mspt_p95=25) for i in (0, 3)])

    def test_candidate_incompatible_at_higher_level(self):
        self.reject(lambda d: d["levels"][1]["trials"][2].update(voice_ok=False))

    def test_candidate_must_pass_lower_level(self):
        self.reject(lambda d: d["levels"][0]["trials"][1].update(mspt_p99=49))

    def test_candidate_oom_risk(self):
        self.reject(lambda d: d["levels"][1]["trials"][1].update(rss_peak_mib=3000))

    def test_hardware_mismatch(self):
        self.reject(lambda d: d["environment"].update(ram_limit_mib=12288))

    def test_2cpu_12gb_additive_pack_schema_preserves_all_original_mods(self):
        data = fixture_2cpu_12gb()
        data['schema'] = 3
        additions = [sha for sha, size in ADDONS.values()]
        data['addons'] = {'baseline': [], 'candidate': additions}
        for level in data['levels']:
            for item in level['trials']:
                item['addon_sha256'] = data['addons'][item['arm']]
                item['addons_loaded_ok'] = True
        self.assertEqual(verify(data), (5, 10))
        data['engines']['candidate'] = data['engines']['baseline']
        for level in data['levels']:
            for item in level['trials']:
                item['engine_sha256'] = data['engines'][item['arm']]
        self.assertEqual(verify(data), (5, 10))  # Same engine, different addon pack.
        for mutate in (
            lambda d: d['addons']['candidate'].append('0' * 64),
            lambda d: d['levels'][1]['trials'][1].update(addon_sha256=[]),
            lambda d: d['levels'][1]['trials'][1].update(addons_loaded_ok=False),
            lambda d: d['environment'].update(mod_jars=32),
        ):
            with self.subTest(mutate=mutate):
                altered = copy.deepcopy(data)
                mutate(altered)
                with self.assertRaises(InvalidEvidence):
                    verify(altered)

    def test_new_2cpu_12gb_target_accepts_complete_synthetic_fixture(self):
        self.assertEqual(verify(fixture_2cpu_12gb()), (5, 10))

    def test_new_target_accepts_decimal_12gb_as_actual_mib(self):
        data = fixture_2cpu_12gb()
        data["environment"]["ram_limit_mib"] = 11444
        self.assertEqual(verify(data), (5, 10))

    def test_new_target_requires_5_10_15_20_rungs_in_order(self):
        data = fixture_2cpu_12gb()
        for level, players in zip(data["levels"], (10, 20)):
            level["players"] = players
            for item in level["trials"]:
                item["logged_in_players"] = players
        with self.assertRaises(InvalidEvidence):
            verify(data)

    def test_new_target_rejects_wrong_cpu_or_memory(self):
        for change in ({"cpu_logical": 1}, {"ram_limit_mib": 3072},
                       {"ram_limit_mib": 13000}):
            with self.subTest(change=change):
                data = fixture_2cpu_12gb()
                data["environment"].update(change)
                with self.assertRaises(InvalidEvidence):
                    verify(data)

    def test_new_target_requires_two_gib_os_headroom(self):
        data = fixture_2cpu_12gb()
        data["levels"][1]["trials"][1]["rss_peak_mib"] = 10241
        with self.assertRaises(InvalidEvidence):
            verify(data)

    def test_new_target_rejects_oversized_or_mixed_heap(self):
        for value in (12288, 0):
            with self.subTest(value=value):
                data = fixture_2cpu_12gb()
                data["environment"]["jvm_xmx_mib"] = value
                with self.assertRaises(InvalidEvidence):
                    verify(data)
        data = fixture_2cpu_12gb()
        data["levels"][1]["trials"][1]["jvm_xmx_mib"] = 4096
        with self.assertRaises(InvalidEvidence):
            verify(data)

    def test_new_target_rejects_mixed_or_missing_hardware_identity(self):
        for value in (None, "a" * 64):
            with self.subTest(value=value):
                data = fixture_2cpu_12gb()
                data["levels"][1]["trials"][1]["hardware_sha256"] = value
                with self.assertRaises(InvalidEvidence):
                    verify(data)

    def test_nonfinite_fails_closed(self):
        self.reject(lambda d: d["levels"][0]["trials"][0].update(mspt_p95=float("nan")))

    def test_no_measurement_at_candidate_rung(self):
        self.reject(lambda d: d["levels"][1]["trials"].pop())

    def test_missing_compatibility_field(self):
        self.reject(lambda d: d["levels"][1]["trials"][1].pop("auth_ok"))

    def test_simulated_baseline_not_accepted(self):
        self.reject(lambda d: d["environment"].update(world_kind="generated"))

    def test_invalid_engine_identity(self):
        self.reject(lambda d: d["levels"][1]["trials"][1].update(engine_sha256="a" * 64))


if __name__ == "__main__":
    unittest.main()
