#!/usr/bin/env python3
"""Ce are voie iaspectorul de arhive sa intoarca in repo."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import rp_archive_inspect as R  # noqa: E402

KEEP = [
    "srv/server.properties", "srv/spigot.yml", "srv/catserver.yml",
    "srv/logs/latest.log", "srv/plugins/Essentials/config.yml",
    "srv/config/paper-world-defaults.yml", "srv/bukkit.yml",
]
DROP = [
    "srv/world/region/r.0.0.mca", "srv/world_nether/region/r.1.1.mca", "srv/level.dat",
    "srv/session.lock", "srv/usercache.json", "srv/ops.json", "srv/whitelist.json",
    "srv/permissions.yml", "srv/playerdata/PlayerOne.dat", "srv/mods/Fake.jar",
    "srv/plugins/Essentials.jar", "srv/plugins/Essentials/playerdata/x.yml",
    "srv/secrets.yml", "srv/plugins/DiscordBot/token.txt", "srv/backup.zip",
    "srv/plugins/Vault/config.yml",             # nu, ramane la ce nu e credential
    "minecity/plugins/LuckPerms/config.yml",   # plugin de permisiuni: poate avea MySQL
]


class KeepTest(unittest.TestCase):
    def test_config_text_is_kept(self):
        for rel in KEEP:
            got = R.keep_body(rel, "srv")
            self.assertTrue(got, f"trebuia pastrat: {rel}")
            if rel.startswith("srv/"):
                self.assertEqual(got, rel[len("srv/"):], "wrapperul trebuie taiat cand e numele arhivei")

    def test_no_player_data_no_binaries_no_secrets(self):
        for rel in DROP:
            self.assertFalse(R.keep_body(rel, "srv"), f"NU trebuia sa iasa din arhiva: {rel}")

    def test_wrapper_nu_taia_cand_e_dir_real(self):
        # "plugins" NU e chihlimbara arhivei: forma integrala ramane, ca sa nu se ciocneasca
        # de fisiere omonime din arhive cuibate (bug-ul care a scurmat Chat.txt de 41 MB)
        self.assertEqual(R.keep_body("plugins/ChatManager/Logs/Chat.txt", "server-2024"),
                         "plugins/ChatManager/Logs/Chat.txt")
        self.assertEqual(R.keep_body("server-2024/plugins/ChatManager/Logs/Chat.txt", "server-2024"),
                         "plugins/ChatManager/Logs/Chat.txt")


class CollectTest(unittest.TestCase):
    def test_logs_are_tailed_not_copied_whole(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "x"
            (root / "srv" / "logs").mkdir(parents=True)
            big = root / "srv" / "logs" / "latest.log"
            big.write_text("A" * 900_000, encoding="utf-8")
            (root / "srv" / "server.properties").write_text("view-distance=10\n", encoding="utf-8")
            out = Path(tmp) / "out"
            res = R.collect(root, out, wrapper="srv")
            log = out / "config" / "logs__latest.log"
            self.assertTrue(log.is_file(), "coada de log trebuie sa iasa")
            self.assertLessEqual(log.stat().st_size, R.LOG_TAIL_BYTES + 1)
            self.assertEqual({k["file"] for k in res["kept"]},
                             {"server.properties", "logs/latest.log"})

    def test_empty_archive_does_not_crash(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "x"
            root.mkdir()
            res = R.collect(root, Path(tmp) / "out")
        self.assertEqual(res["kept"], [])


if __name__ == "__main__":
    unittest.main()


class ScrubTest(unittest.TestCase):
    def test_junk_names_are_blocked(self):
        self.assertFalse(R.keep("New Text Document.txt"))

    def test_scrub_redacts_keys_and_long_tokens(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "config.yml"
            f.write_text("minetrax:\n  api-key: WHC1NmZYq6s0L0L0a1l3sr3KYk3qp0Jz\nbot-token: 'abc.DEF.123'\n"
                         "view-distance: 10\n# 229933NIX2GZ0EKY1YTRJ\n", encoding="utf-8")
            R.scrub(f)
            t = f.read_text(encoding="utf-8")
            self.assertNotIn("WHC1NmZYq6s0L0L0a1l3sr3KYk3qp0Jz", t)
            self.assertNotIn("229933NIX2GZ0EKY1YTRJ", t)
            self.assertIn("view-distance: 10", t)


class NestedFilterTest(unittest.TestCase):
    def test_lobby_and_velocity_are_excluded(self):
        self.assertFalse(R.nested_allowed("lobby.tar"))
        self.assertFalse(R.nested_allowed("velocity.tar"))
        self.assertFalse(R.nested_allowed("Lobby-SNAPSHOT.tar.gz"))
        self.assertTrue(R.nested_allowed("roleplay.tar"))
        self.assertTrue(R.nested_allowed("archive-2024-09-11T124205Z.tar.gz"))


class VarintTest(unittest.TestCase):
    def test_varint_semnat(self):
        import importlib, sys
        sys.path.insert(0, "scripts")
        import mc_run_check as M
        importlib.reload(M)
        self.assertEqual(M._varint(-1), b"\xff")
        self.assertEqual(M._varint(0), b"\x00")
        self.assertEqual(M._varint(127), b"\x7f")
        self.assertEqual(M._varint(300), b"\xac\x02")
