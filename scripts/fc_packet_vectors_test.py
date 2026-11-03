#!/usr/bin/env python3
"""Public deterministic packet corpus; no private world or player payload."""
from pathlib import Path
import tempfile
import unittest
import zlib

from fc_packet_vectors import write_vectors


class PacketVectorsTest(unittest.TestCase):
    def test_reproducible_compressible_and_incompressible_payloads(self):
        with tempfile.TemporaryDirectory() as temp:
            first, second = Path(temp)/'a', Path(temp)/'b'
            vectors = write_vectors(first)
            self.assertEqual(vectors, write_vectors(second))
            self.assertEqual(len(vectors), 6)
            for name, loops in vectors:
                data = (first/name).read_bytes()
                self.assertEqual(data, (second/name).read_bytes())
                self.assertIn(len(data), (1024, 32768, 262144))
                self.assertGreater(loops, 0)
                if 'mixed' in name:
                    self.assertLess(len(zlib.compress(data)), len(data) * .75)
                else:
                    self.assertGreater(len(zlib.compress(data)), len(data) * .95)
            with self.assertRaises(FileExistsError):
                write_vectors(first)


if __name__ == '__main__':
    unittest.main()
