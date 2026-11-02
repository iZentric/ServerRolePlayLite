#!/usr/bin/env python3
"""Synthetic JFR fixtures: rank only server-thread CPU samples, fail closed."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from fc_funcity_jfr_hotspots import ProfileRejected, main, summarize


def sample(thread, class_name, method='tick'):
    return {'type': 'jdk.ExecutionSample', 'values': {
        'sampledThread': {'javaName': thread},
        'stackTrace': {'frames': [{'method': {
            'type': {'name': class_name}, 'name': method}}]}}}


class HotspotTest(unittest.TestCase):
    def test_ranks_only_server_thread_and_preserves_class_identity(self):
        recording = {'recording': {'events': (
            [sample('Server thread', 'rp.Vehicle', 'drive') for _ in range(80)] +
            [sample('Server thread', 'net.minecraft.Server', 'tick') for _ in range(40)] +
            [sample('Server thread', 'rp.Vehicle', 'login') for _ in range(5)] +
            [sample('Netty Worker', 'rp.Vehicle', 'drive') for _ in range(200)] +
            [sample('Server thread', 'rp.Vehicle', 'drive') | {'type': 'jdk.GCHeapSummary'}])}}
        total, ranking = summarize(recording)
        self.assertEqual(total, 125)
        self.assertEqual(ranking[:3], [
            ('rp.Vehicle.drive', 80), ('net.minecraft.Server.tick', 40),
            ('rp.Vehicle.login', 5)])

    def test_cli_reads_only_private_json_and_prints_aggregates(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / 'profile.json'
            export.write_text(json.dumps({'recording': {'events': [
                sample('Server thread', 'rp.Vehicle') for _ in range(120)]}}))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                main(export)
            self.assertIn('100.0%    120  rp.Vehicle.tick', out.getvalue())
            self.assertIn('no real-player capacity', out.getvalue())
            with self.assertRaises(ProfileRejected):
                main(Path(__file__))

    def test_rejects_missing_or_insufficient_evidence(self):
        for data in ({}, {'recording': {'events': []}},
                     {'recording': {'events': [sample('Server thread', 'rp.Vehicle')] * 99}},
                     {'recording': {'events': [sample('Netty Worker', 'rp.Vehicle')] * 200}},
                     {'recording': {'events': [sample('Server thread', '', '')] * 150}}):
            with self.subTest(data=str(data)[:30]), self.assertRaises(ProfileRejected):
                summarize(data)


if __name__ == '__main__':
    unittest.main()
