#!/usr/bin/env python3
"""Artificial process tests only; no Minecraft binary or real boot."""
from pathlib import Path
import tempfile
import unittest

from fc_funcity_java11_smoke import PROPERTIES, inspect, smoke


class SmokeTest(unittest.TestCase):
    def test_private_boot_flags(self):
        self.assertEqual(inspect('[Server thread/INFO] Done (2.1s)! For help, type "help"'), (True, False))
        self.assertEqual(inspect('[main/ERROR] failed\nDone (2s)! For help, type "help"'), (True, True))
        self.assertEqual(inspect('Starting Minecraft server'), (False, False))

    def test_loopback_and_no_rcon(self):
        self.assertIn('server-ip=127.0.0.1\n', PROPERTIES)
        self.assertIn('enable-rcon=false\n', PROPERTIES)
        self.assertIn('white-list=true\n', PROPERTIES)
        self.assertNotIn('server-ip=0.0.0.0', PROPERTIES)

    def fake(self, text):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jar = root / 'synthetic.jar'
            jar.write_bytes(b'NOT A MINECRAFT JAR')
            fake_java = root / 'fake-java'
            fake_java.write_text('#!/usr/bin/env python3\n'
                                 'print(' + repr(text) + ', flush=True)\n'
                                 'input()\n')
            fake_java.chmod(0o755)
            return smoke(fake_java, jar, deadline_seconds=5)

    def test_clean_stop_fake_process(self):
        self.assertTrue(self.fake('Done (2s)! For help, type "help"'))

    def test_fatal_fake_process(self):
        self.assertFalse(self.fake('[main/FATAL] crash'))

    def test_done_then_exit_without_stop_is_not_clean_shutdown(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jar = root / 'synthetic.jar'
            jar.write_bytes(b'NOT A MINECRAFT JAR')
            fake_java = root / 'fake-java'
            fake_java.write_text('#!/usr/bin/env python3\n'
                                 'print("Done (2s)! For help, type \\"help\\"", flush=True)\n')
            fake_java.chmod(0o755)
            self.assertFalse(smoke(fake_java, jar, deadline_seconds=5))


if __name__ == '__main__':
    unittest.main()
