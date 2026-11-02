#!/usr/bin/env python3
"""Synthetic Linux limits: no real host/world/clients are tested."""
import unittest
from fc_funcity_lab_resources import LabRejected, verify_limits


class LabResourceTest(unittest.TestCase):
    def test_two_cpu_and_twelve_gib_with_room_for_eight_gib_jvm(self):
        self.assertTrue(verify_limits(affinity=4, cpu_max='200000 100000',
                                      ram_limit_mib=12288, available_mib=11000))
        self.assertTrue(verify_limits(affinity=2, cpu_max='max 100000',
                                      ram_limit_mib=11444, available_mib=10300))

    def test_reject_wrong_cpu_or_ram_or_free_memory(self):
        examples = [(4, 'max 100000', 12288, 11000),
                    (1, '200000 100000', 12288, 11000),
                    (4, '150000 100000', 12288, 11000),
                    (2, 'max 100000', 3072, 3000),
                    (2, 'max 100000', 12288, 9000),
                    (2, 'max 100000', 16384, 14000),
                    (2, 'nonsense', 12288, 11000)]
        for args in examples:
            with self.subTest(args=args), self.assertRaises(LabRejected):
                verify_limits(*args)


if __name__ == '__main__':
    unittest.main()
