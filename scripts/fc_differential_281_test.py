#!/usr/bin/env python3
"""Fail closed if the 281-case contract matrix is padded or silently reduced."""
from collections import Counter
from pathlib import Path
import tempfile
import unittest

from fc_differential_281 import SIZES, SPECIAL, cases, write_manifest


class DifferentialMatrixTest(unittest.TestCase):
    def test_unique_domain_cases_and_protocol_boundaries(self):
        rows = cases()
        self.assertEqual(len(rows), 261)
        self.assertEqual(len(SIZES), 64)
        self.assertEqual(len(set(row[1:] for row in rows)), 261)
        self.assertEqual([r[0] for r in rows], [f'PKT-{i:03d}' for i in range(261)])
        self.assertEqual(Counter(row[2] for row in rows[:256]),
                         {'zeros': 64, 'repeat': 64, 'random': 64, 'mixed': 64})
        self.assertEqual(Counter(row[3] for row in rows[:256]),
                         {'heap': 128, 'direct': 128})
        self.assertEqual({r[1] for r in rows if r[4] == 256}, set(SIZES) | {2097152})
        self.assertTrue({127, 128, 129, 255, 256, 257, 511, 512, 513,
                         8191, 8192, 8193, 16383, 16384, 16385}.issubset(SIZES))
        self.assertEqual(tuple(r[1:] for r in rows[256:]), SPECIAL)

    def test_manifest_is_public_deterministic_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a.tsv', Path(tmp) / 'b.tsv'
            write_manifest(a)
            write_manifest(b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(len(a.read_text().splitlines()), 261)
            with self.assertRaises(FileExistsError):
                write_manifest(a)


if __name__ == '__main__':
    unittest.main()
