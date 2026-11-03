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

    def test_netty_samples_are_separate_from_server_tick(self):
        events = ([sample('Server thread', 'rp.Vehicle') for _ in range(120)] +
                  [sample('Netty Server IO #1', 'java.util.zip.Deflater', 'deflate') for _ in range(130)] +
                  [sample('Netty Epoll Server IO #2', 'java.util.zip.Deflater', 'deflate') for _ in range(20)])
        recording = {'recording': {'events': events}}
        self.assertEqual(summarize(recording, thread='netty'),
                         (150, [('java.util.zip.Deflater.deflate', 150)]))
        self.assertEqual(summarize(recording)[0], 120)

    def test_cli_reads_only_private_json_and_prints_aggregates(self):
        with tempfile.TemporaryDirectory() as tmp:
            export = Path(tmp) / 'profile.json'
            export.write_text(json.dumps({'recording': {'events':
                [sample('Server thread', 'rp.Vehicle') for _ in range(120)] +
                [sample('Netty Server IO #1', 'java.util.zip.Deflater') for _ in range(120)]}}))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                main(export)
            self.assertIn('100.0%    120  rp.Vehicle.tick', out.getvalue())
            self.assertIn('netty execution samples: 120', out.getvalue())
            self.assertIn('java.util.zip.Deflater.tick', out.getvalue())
            self.assertIn('no real-player capacity', out.getvalue())
            with self.assertRaises(ProfileRejected):
                main(Path(__file__))

    def test_short_java_fixture_does_not_lower_private_cli_gate(self):
        recording = {'recording': {'events': [sample('Server thread', 'JfrFixture')]}}
        self.assertEqual(summarize(recording, minimum=1), (1, [('JfrFixture.tick', 1)]))
        with self.assertRaises(ProfileRejected):
            summarize(recording)
        with self.assertRaises(ProfileRejected):
            summarize(recording, minimum=0)

    def test_rejects_missing_or_insufficient_evidence(self):
        for data in ({}, {'recording': {'events': []}},
                     {'recording': {'events': [sample('Server thread', 'rp.Vehicle')] * 99}},
                     {'recording': {'events': [sample('Netty Worker', 'rp.Vehicle')] * 200}},
                     {'recording': {'events': [sample('Server thread', '', '')] * 150}}):
            with self.subTest(data=str(data)[:30]), self.assertRaises(ProfileRejected):
                summarize(data)


if __name__ == '__main__':
    unittest.main()
