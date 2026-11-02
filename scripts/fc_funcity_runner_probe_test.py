#!/usr/bin/env python3
"""Self-hosted resource probe must never check out code or inspect RP files."""
from pathlib import Path
import unittest

WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/funcity-private-lab-resources.yml'


class ProbeSafetyTest(unittest.TestCase):
    def test_dedicated_runner_only_and_no_private_data(self):
        text = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('runs-on: [self-hosted, Linux, funcity-capacity-lab]', text)
        self.assertIn('permissions: {}', text)
        job = text.split('  private-resource-probe:', 1)[1]
        for unsafe in ('actions/checkout', 'curl ', 'wget ', 'gh ', 'ssh ', 'sftp ',
                       'server.jar', 'mods/', 'plugins/', 'world/', 'secrets.', 'upload-artifact'):
            with self.subTest(unsafe=unsafe):
                self.assertNotIn(unsafe, job)
        self.assertIn('NO_PRIVATE_FILES_READ=true', job)
        self.assertIn('NO_SERVER_START=true', job)


if __name__ == '__main__':
    unittest.main()
