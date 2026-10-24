#!/usr/bin/env python3
"""Artificial private trial fixtures only; no real Minecraft files or host access."""
import hashlib
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess

from fc_funcity_compiled_engine_gate_test import fixture
from fc_funcity_private_trial import (MARKER, TrialRejected, isolated_java_command,
                                       namespace_supported, prepare, preflight, properties, trial)


def unused_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def synthetic_lab(root):
    root = Path(root)
    source = root / 'offline-source-copy'
    source.mkdir()
    (source / '.funcity-isolated-copy').write_text(MARKER)
    (source / 'eula.txt').write_text('eula=true\n')
    (source / 'server.properties').write_text('level-name=rp\nonline-mode=false\nserver-ip=0.0.0.0\n'
                                               'enable-rcon=true\nserver-port=25565\n')
    (source / 'rp').mkdir()
    (source / 'rp' / 'level.dat').write_bytes(b'SYNTHETIC WORLD')
    (source / 'server.jar').write_bytes(b'original rollback engine')
    for folder, count in (('mods', 34), ('plugins', 13)):
        (source / folder).mkdir()
        for i in range(count):
            (source / folder / f'{i:02d}.jar').write_bytes(b'fixture')
    binary_dir = root / 'binary'
    binary_dir.mkdir()
    jar, _classes = fixture(binary_dir)
    digest = hashlib.sha256(jar.read_bytes()).hexdigest()
    return source, root / 'new-trial', jar, digest


def fake_java(root, *, fatal=False, version='11.0.29'):
    path = Path(root) / 'fake-java'
    msg = '[Server thread/ERROR] failed' if fatal else 'Done (2s)! For help, type "help"'
    path.write_text('#!/usr/bin/env python3\nimport sys\n'
                    'if "-version" in sys.argv:\n'
                    '  print("openjdk version \\"' + version + '\\"", file=sys.stderr); sys.exit(0)\n'
                    'print(' + repr(msg) + ', flush=True)\n'
                    'input()\n')
    path.chmod(0o755)
    return path


class PrivateTrialTest(unittest.TestCase):
    def test_shield_preserves_world_and_auth(self):
        world, safe = properties('level-name=City\nonline-mode=false\n'
                                 'server-ip=0.0.0.0\nenable-rcon=true\n', 25595)
        self.assertEqual(world, 'City')
        self.assertIn('online-mode=false\n', safe)
        for line in ('server-ip=127.0.0.1', 'white-list=true', 'enable-rcon=false',
                     'enable-query=false', 'server-port=25595'):
            self.assertEqual(safe.splitlines().count(line), 1)
        self.assertNotIn('server-ip=0.0.0.0', safe)
        with self.assertRaises(TrialRejected):
            properties('online-mode=false\nlevel-name=../other\n', 25595)
        with self.assertRaises(TrialRejected):
            properties('online-mode=false\nonline-mode=false\n', 25595)

    def test_prepare_only_new_copy_with_rollback(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            before = (source / 'server.jar').read_bytes()
            prepared = prepare(source, output, jar, digest, unused_port())
            self.assertEqual(prepared, output)
            self.assertEqual((source / 'server.jar').read_bytes(), before)
            self.assertEqual((output / 'server-before-funcity-trial.jar').read_bytes(), before)
            self.assertEqual(hashlib.sha256((output / 'server.jar').read_bytes()).hexdigest(), digest)
            self.assertNotEqual((source / 'server.properties').read_bytes(),
                                (output / 'server.properties').read_bytes())
            self.assertEqual((source / 'rp' / 'level.dat').read_bytes(),
                             (output / 'rp' / 'level.dat').read_bytes())
            self.assertFalse((output / '.funcity-isolated-copy').exists())

    def test_refuse_missing_marker_or_wrong_sha_or_live_target(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            port = unused_port()
            (source / '.funcity-isolated-copy').unlink()
            with self.assertRaises(TrialRejected):
                preflight(source, output, jar, digest, port)
            (source / '.funcity-isolated-copy').write_text(MARKER)
            with self.assertRaises(TrialRejected):
                preflight(source, output, jar, '0' * 64, port)
            with self.assertRaises(TrialRejected):
                preflight(source, source / 'nested-output', jar, digest, port)
            (source / 'plugins' / '00.jar').unlink()
            with self.assertRaises(TrialRejected):
                preflight(source, output, jar, digest, port)

    def test_refuse_links_or_taken_port(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                with self.assertRaises(TrialRejected):
                    preflight(source, output, jar, digest, sock.getsockname()[1])
            (source / 'mods' / 'linked.jar').symlink_to(source / 'mods' / '00.jar')
            with self.assertRaises(TrialRejected):
                preflight(source, output, jar, digest, unused_port())

    def test_boot_requires_kernel_network_isolation(self):
        cmd = isolated_java_command('/opt/java11/bin/java')
        self.assertEqual(cmd[:6], ['unshare', '--user', '--map-root-user', '--net', '--', 'sh'])
        self.assertIn('ip link set lo up && exec "$@"', cmd)
        self.assertIn('server.jar', cmd)

    def test_isolation_failure_aborts_before_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            with patch('fc_funcity_private_trial.shutil.which', return_value='/usr/bin/tool'), \
                 patch('fc_funcity_private_trial.subprocess.run',
                       side_effect=[CompletedProcess([], 0, stdout=b'', stderr=b'openjdk version "11.0.29"'),
                                    CompletedProcess([], 1)]) as run:
                with self.assertRaises(TrialRejected):
                    trial(Path(temp)/'fake-java', source, output, jar, digest, unused_port())
            self.assertEqual(run.call_count, 2)
            self.assertFalse(output.exists())

    def test_two_boots_and_failure_stop(self):
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            with patch('fc_funcity_private_trial.namespace_supported'), \
                 patch('fc_funcity_private_trial.boot_once', return_value=True) as boots:
                self.assertTrue(trial(fake_java(temp), source, output, jar, digest,
                                      unused_port(), timeout=5))
            self.assertEqual(boots.call_count, 2)
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            with patch('fc_funcity_private_trial.namespace_supported'), \
                 patch('fc_funcity_private_trial.boot_once', side_effect=[False, True]) as boots:
                with self.assertRaises(TrialRejected):
                    trial(fake_java(temp, fatal=True), source, output, jar, digest,
                          unused_port(), timeout=5)
            self.assertEqual(boots.call_count, 1)
        with tempfile.TemporaryDirectory() as temp:
            source, output, jar, digest = synthetic_lab(temp)
            with self.assertRaises(TrialRejected):
                trial(fake_java(temp, version='17.0.1'), source, output, jar, digest,
                      unused_port(), timeout=5)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
