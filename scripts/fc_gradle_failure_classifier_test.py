#!/usr/bin/env python3
"""Synthetic compiler diagnostics only. No raw CI logs or server files."""
import unittest
from fc_gradle_failure_classifier import classify, details


class ClassifierTest(unittest.TestCase):
    def test_wrapper_url_is_not_cause_of_javac_failure(self):
        text = 'gradle-7.3.3-bin.zip\n> Task :forge:compileJava FAILED\n'
        task, *_ = details(text)
        self.assertEqual(task, ':forge:compileJava')
        self.assertEqual(classify(text, task), 'COMPILER_FAILURE_UNCLASSIFIED')

    def test_missing_symbol_has_compiler_category(self):
        text = '> Task :forge:compileJava FAILED\nerror: cannot find symbol\n  symbol: class MissingType\n'
        self.assertEqual(classify(text, details(text)[0]), 'SOURCE_COMPILE')
        self.assertEqual(details(text)[-1], 'MissingType')

    def test_real_wrapper_failure_retains_label(self):
        self.assertEqual(classify('gradle-7.3.3-bin.zip', 'UNKNOWN'), 'GRADLE_DISTRIBUTION')


if __name__ == '__main__':
    unittest.main()
