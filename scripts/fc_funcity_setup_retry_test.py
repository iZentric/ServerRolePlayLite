#!/usr/bin/env python3
"""Artificial Gradle messages; no URLs or private logs in fixtures."""
import unittest
from fc_funcity_setup_retry import retryable


class RetryTest(unittest.TestCase):
    def test_network_timeouts_and_503(self):
        self.assertTrue(retryable('Could not resolve all files for :forge:compileClasspath.\nRead timed out'))
        self.assertTrue(retryable('Could not get resource\nReceived status code 503'))
        self.assertTrue(retryable('UnknownHostException'))

    def test_network_phrase_alone_gets_one_bounded_retry(self):
        self.assertTrue(retryable('Could not resolve all files for configuration'))

    def test_missing_or_forbidden_does_not_retry(self):
        self.assertFalse(retryable('Could not get resource: received status code 404'))
        self.assertFalse(retryable('Could not resolve all files; HTTP 403'))
        self.assertFalse(retryable('Plugin foo was not found'))

    def test_compiler_and_memory_fail_closed(self):
        self.assertFalse(retryable('Could not resolve all files\nerror: cannot find symbol'))
        self.assertFalse(retryable('OutOfMemoryError'))
        self.assertFalse(retryable('no space left on device'))
        self.assertFalse(retryable('Gradle build daemon disappeared unexpectedly'))

    def test_empty_log(self):
        self.assertFalse(retryable(''))


if __name__ == '__main__':
    unittest.main()
