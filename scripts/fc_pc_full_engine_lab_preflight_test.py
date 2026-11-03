#!/usr/bin/env python3
"""Read-only static guard for the Windows owner-PC resource probe."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name('fc_pc_full_engine_lab_preflight.ps1')


class ResourceProbeTest(unittest.TestCase):
    def test_reports_bounded_resource_flags_without_private_values(self):
        text = SOURCE.read_text(encoding='utf-8')
        for required in ('NumberOfLogicalProcessors', 'TotalPhysicalMemory',
                         'FreePhysicalMemory', 'PC_LOGICAL_CPU_AT_LEAST_2=',
                         'PC_RAM_12GB_RANGE=', 'PC_FREE_RAM_FOR_8G_JVM=',
                         'TARGET_HOST_SPECS_NOT_VERIFIED=true'):
            self.assertIn(required, text)
        self.assertNotIn('Write-Output $root', text)
        self.assertNotIn('Write-Output $manifest', text)


if __name__ == '__main__':
    unittest.main()
