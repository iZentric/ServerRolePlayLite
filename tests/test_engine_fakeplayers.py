"""Only change the known non-player Curtain injection, and never the released mod."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from engine_fakeplayers import make_catserver_test_mod


class CurtainTestMod(unittest.TestCase):
    def test_minimal_test_only_mixin_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, out = (Path(tmp) / name for name in ("source.jar", "test.jar"))
            config = {"mixins": ["NaturalSpawnerMixin", "rules.command_player.PlayerListMixin",
                                 "rules.command_player.ServerPlayerEntityMixin"]}
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("curtain.mixins.json", json.dumps(config))
                z.writestr("LICENSE", "LGPL-2.1")
            make_catserver_test_mod(source, out)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(json.loads(z.read("curtain.mixins.json"))["mixins"], config["mixins"][1:])
                self.assertEqual(z.read("LICENSE"), b"LGPL-2.1")
            with zipfile.ZipFile(source) as z:
                self.assertIn("NaturalSpawnerMixin", z.read("curtain.mixins.json").decode())

    def test_unknown_upstream_layout_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, out = (Path(tmp) / name for name in ("source.jar", "test.jar"))
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("curtain.mixins.json", json.dumps({"mixins": ["NaturalSpawnerMixin"]}))
            with self.assertRaises(ValueError):
                make_catserver_test_mod(source, out)


if __name__ == "__main__":
    unittest.main()
