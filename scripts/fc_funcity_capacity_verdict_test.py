#!/usr/bin/env python3
"""Artificial fixtures ONLY: verify gate semantics; never cite as benchmark."""
import copy
import json
import unittest

from fc_funcity_capacity_verdict import InvalidEvidence, unique_keys, verify


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
