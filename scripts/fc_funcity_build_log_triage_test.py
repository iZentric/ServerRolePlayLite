#!/usr/bin/env python3
import unittest
from fc_funcity_build_log_triage import triage


class TriageTest(unittest.TestCase):
    def test_compiler_error_not_distracted_by_wrapper_download(self):
        task, categories, symbols = triage(
            'Downloading https://example.org/gradle-7.3.3-bin.zip\n'
            '> Task :forge:compileJava FAILED\n'
            '/tmp/forge/Example.java:12: error: cannot find symbol\n'
            '  symbol: class LevelChunk\n')
        self.assertEqual((task, categories, symbols),
                         (':forge:compileJava', 'MISSING_SYMBOL', 'LevelChunk'))

    def test_no_raw_secret_or_path(self):
        result = triage('password=PRIVATE\n/home/user/foo\n'
                        '> Task :forge:compileJava FAILED\n'
                        'symbol: variable accessToken\n')
        self.assertEqual(result, (':forge:compileJava', 'UNKNOWN_FAILURE', 'NONE'))
        self.assertNotIn('PRIVATE', str(result))

    def test_dependency_graph(self):
        self.assertEqual(triage('> Task :forge:compileJava FAILED\n'
                                'uses this output of task without declaring an explicit dependency'),
                         (':forge:compileJava', 'GRADLE_TASK_DEPENDENCY', 'NONE'))

    def test_oom(self):
        self.assertEqual(triage('> Task :forge:compileJava FAILED\nJava heap space'),
                         (':forge:compileJava', 'RESOURCE_EXHAUSTED', 'NONE'))


if __name__ == '__main__':
    unittest.main()
