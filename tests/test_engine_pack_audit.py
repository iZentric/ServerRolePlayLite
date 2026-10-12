"""A release audit must reject a changed ZIP, duplicates and missing components."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import engine_pack_audit as audit


class AuditTests(unittest.TestCase):
    def make_zip(self, root, *, mod_count=36, duplicate=False):
        pack = root / 'pack.zip'
        with zipfile.ZipFile(pack, 'w') as z:
            for i in range(mod_count):
                z.writestr(f'mods/mod-{i}.jar', b'mod')
            for i in range(14):
                z.writestr(f'plugins/plugin-{i}.jar', b'plugin')
            z.writestr('server.properties', 'max-players=25\nrcon.password=secret\n')
            if duplicate:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    z.writestr('mods/mod-0.jar', b'evil')
        return pack

    def test_inventory_and_redaction(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            pack = self.make_zip(root)
            with patch.object(audit, 'EXPECTED_PACK_SHA', hashlib.sha256(pack.read_bytes()).hexdigest()):
                audit.main(pack, root / 'out.md')
            report = (root / 'out.md').read_text()
            self.assertIn('36 moduri / 14 pluginuri', report)
            self.assertIn('`max-players` | `25`', report)
            self.assertNotIn('rcon.password', report)
            self.assertNotIn('secret', report)

    def test_wrong_hash_and_missing_mod_and_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            pack = self.make_zip(root, mod_count=35)
            with self.assertRaisesRegex(ValueError, 'SHA changed'):
                audit.audit(pack)
            with patch.object(audit, 'EXPECTED_PACK_SHA', hashlib.sha256(pack.read_bytes()).hexdigest()):
                with self.assertRaisesRegex(ValueError, 'expected 36'):
                    audit.audit(pack)
            pack = self.make_zip(root, duplicate=True)
            with patch.object(audit, 'EXPECTED_PACK_SHA', hashlib.sha256(pack.read_bytes()).hexdigest()):
                with self.assertRaisesRegex(ValueError, 'duplicate ZIP'):
                    audit.audit(pack)


if __name__ == '__main__':
    unittest.main()
