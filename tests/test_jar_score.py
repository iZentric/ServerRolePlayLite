#!/usr/bin/env python3
"""Scorul pe bară: cite dovezi, nu cite promisiuni."""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

import jar_score  # noqa: E402


class ScorecardTest(unittest.TestCase):
    def setUp(self):
        self.rows = jar_score.scorecard()

    def test_own_engine_is_first_and_pinned(self):
        first = self.rows[0]
        self.assertTrue(first["pin"])
        self.assertIn("CUANTIC", first["name"])

    def test_scores_are_gate_multiples_and_sorted_by_evidence(self):
        for row in self.rows:
            self.assertEqual(row["score"] % 25, 0)
            self.assertLessEqual(row["score"], row["max"])
            self.assertEqual(sum(row["gates"].values()) * 25, row["score"])
        rest = [r["score"] for r in self.rows[1:]]
        self.assertEqual(rest, sorted(rest, reverse=True))

    def test_unmeasured_candidate_cannot_inherit_a_number(self):
        with patch.object(jar_score, "family_smokes", return_value={}), \
             patch.object(jar_score, "ladder_rows", return_value=[
                 {"name": "Mohist 1.16.5", "sha_verified": False, "smoke_passed": False,
                  "plugins": None, "reason": "fără URL", "status": "ESUAT · fără URL",
                  "boot_s": None, "sha": "", "licence": "x", "verdict": "NEAVĂGAT"}]), \
             patch.object(jar_score, "same_run_pairs", return_value=[]):
            rows = jar_score.scorecard()
        mohist = [r for r in rows if r["name"].startswith("Mohist")][0]
        self.assertEqual(mohist["score"], 0)
        self.assertFalse(mohist["measured"])
        self.assertIsNone(mohist["perf"])

    def test_a_lost_candidate_is_not_painted_as_a_win(self):
        for row in self.rows:
            if row["perf"] and "RESPINS" in row["perf"]["verdict"]:
                self.assertFalse(row["perf"]["worse"])
                self.assertTrue(row["perf"]["inside_noise"] or row["perf"]["better"])

    def test_delta_is_signed_from_each_arms_own_side(self):
        perf = {r["name"]: r["perf"] for r in self.rows}
        ours = [k for k in perf if k.startswith("CUANTIC (")][0]
        ref = [k for k in perf if k.startswith("CatServer oficial")][0]
        self.assertEqual(perf[ours]["delta"], -perf[ref]["delta"])
        self.assertEqual(perf[ours]["verdict"], "NEDECIS · sub zgomot")
        self.assertFalse(perf[ours]["worse"], "egalitate sub zgomot nu se coloreaza in rosu")

    def test_panel_refuses_marketing_words_and_never_claims_a_winner(self):
        html = jar_score.panel()
        for banned in ("câștigător", "cel mai rapid motor este", "10× demonstrat", "zero lag"):
            self.assertNotIn(banned, html)
        self.assertIn("NEDECIS", html)
        self.assertIn('data-score="100"', html)

    def test_every_row_carries_all_four_gate_chips(self):
        html = jar_score.panel()
        self.assertEqual(html.count('class="js-gates">'), len(self.rows))
        self.assertEqual(html.count('js-gate '), len(self.rows) * 4)

    def test_empty_bar_for_a_row_without_evidence(self):
        import re
        html = jar_score.panel()
        fills = []
        for block in html.split('<li class="js-row')[1:]:
            head = block.split(">")[0]
            width = int(re.search(r"width:(\d+)%", block).group(1))
            fills.append(('data-measured="true"' in head, width))
        self.assertTrue(all(w > 0 for measured, w in fills if measured))
        self.assertTrue(all(w == 0 for measured, w in fills if not measured))
        self.assertIn(False, [m for m, _ in fills])

    def test_within_noise_rows_do_not_pretend_a_direction(self):
        for row in self.rows:
            if row["perf"] and row["perf"]["inside_noise"]:
                self.assertGreaterEqual(abs(row["perf"]["delta"]), 0)
                self.assertFalse(row["perf"]["worse"])
                block = jar_score._bar(row)
                self.assertIn("js-delta flat", block)
                self.assertNotIn("js-delta up", block)
                self.assertNotIn("js-delta down", block)


class SiteIntegrationTest(unittest.TestCase):
    def test_site_renders_the_score_bars(self):
        index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="scor"', index)
        self.assertIn("Bari de dovezi", index)


if __name__ == "__main__":
    unittest.main()
