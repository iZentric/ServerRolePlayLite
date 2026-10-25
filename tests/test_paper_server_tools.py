import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, file_name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "paper_server" / file_name)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


paper_download = load_module("paper_download", "download_paper.py")
paper_tune = load_module("paper_tune", "tune_configs.py")
paper_backup = load_module("paper_backup", "backup.py")


class FillDownloadTests(unittest.TestCase):
    def test_selects_highest_stable_not_latest_unstable(self):
        builds = [
            {"id": 135, "channel": "EXPERIMENTAL"},
            {"id": 134, "channel": "STABLE"},
            {"id": 133, "channel": "STABLE"},
        ]
        self.assertEqual([134, 133], [item["id"] for item in paper_download.stable_builds(builds)])

    def test_get_build_uses_fill_metadata_and_exact_server_file(self):
        sha = "a" * 64
        payload = [{
            "id": 134,
            "channel": "STABLE",
            "downloads": {"server:default": {
                "name": "paper-26.2-134.jar",
                "checksums": {"sha256": sha},
                "url": f"https://fill-data.papermc.io/v1/objects/{sha}/paper-26.2-134.jar",
            }},
        }]
        with mock.patch.object(paper_download, "fetch_json", return_value=payload):
            self.assertEqual({
                "version": "26.2", "build": 134, "name": "paper-26.2-134.jar",
                "sha256": sha, "url": payload[0]["downloads"]["server:default"]["url"],
            }, paper_download.get_build("26.2"))

    def test_rejects_untrusted_download_host(self):
        payload = [{
            "id": 1, "channel": "STABLE", "downloads": {"server:default": {
                "name": "paper.jar", "checksums": {"sha256": "a" * 64},
                "url": "https://example.invalid/paper.jar",
            }},
        }]
        with mock.patch.object(paper_download, "fetch_json", return_value=payload):
            with self.assertRaises(ValueError):
                paper_download.get_build("26.2")


class PaperConfigTunerTests(unittest.TestCase):
    def test_updates_only_existing_generated_paths_and_makes_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Path(temp)
            (runtime / "config").mkdir()
            (runtime / "eula.txt").write_text("eula=true\n", encoding="utf-8")
            (runtime / "server.properties").write_text(
                "view-distance=10\nsimulation-distance=10\n", encoding="utf-8"
            )
            (runtime / "bukkit.yml").write_text(
                "spawn-limits:\n  monsters: 70\n  animals: 10\n  water-animals: 5\n"
                "  water-ambient: 20\n  water-underground-creature: 5\n  axolotls: 5\n  ambient: 15\n",
                encoding="utf-8",
            )
            (runtime / "spigot.yml").write_text(
                "world-settings:\n  default:\n    mob-spawn-range: 8\n", encoding="utf-8"
            )
            (runtime / "config" / "paper-world-defaults.yml").write_text(
                "entities:\n  spawning:\n    per-player-mob-spawns: true\n    spawn-limits:\n"
                "      monster: -1\n      creature: -1\n      water_creature: -1\n"
                "      water_ambient: -1\n      underground_water_creature: -1\n"
                "      axolotls: -1\n      ambient: -1\n    despawn-ranges:\n"
                "      monster:\n        hard: 128\n        soft: 32\n",
                encoding="utf-8",
            )
            changed = paper_tune.tune(runtime)
            self.assertEqual(4, len(changed))
            self.assertIn("simulation-distance=4", (runtime / "server.properties").read_text())
            self.assertIn("mob-spawn-range: 3", (runtime / "spigot.yml").read_text())
            paper = (runtime / "config" / "paper-world-defaults.yml").read_text()
            self.assertIn("hard: 48", paper)
            self.assertIn("soft: 24", paper)
            self.assertEqual(4, len(list(runtime.rglob("*.before-low-spec-*.bak"))))

    def test_missing_generated_key_aborts_before_any_file_is_written(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Path(temp)
            (runtime / "config").mkdir()
            (runtime / "eula.txt").write_text("eula=true\n", encoding="utf-8")
            originals = {
                "server.properties": "view-distance=10\nsimulation-distance=10\n",
                "bukkit.yml": "spawn-limits:\n  monsters: 70\n",
                "spigot.yml": "world-settings:\n  default:\n    mob-spawn-range: 8\n",
                "config/paper-world-defaults.yml": "entities:\n  spawning:\n    per-player-mob-spawns: true\n",
            }
            for name, text in originals.items():
                path = runtime / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError):
                paper_tune.tune(runtime)
            self.assertEqual([], list(runtime.rglob("*.before-low-spec-*.bak")))
            for name, text in originals.items():
                self.assertEqual(text, (runtime / name).read_text(encoding="utf-8"))

    def test_yaml_update_preserves_unrelated_lines_and_comments(self):
        source = "root:\n  target: 8 # keep note\n  other: yes\n"
        changed, missing = paper_tune._replace_yaml_paths(source, {"root.target": "3"})
        self.assertEqual([], missing)
        self.assertIn("target: 3 # keep note", changed)
        self.assertIn("other: yes", changed)


class BackupTests(unittest.TestCase):
    def test_archive_contains_server_data_but_not_jar_or_logs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = root / "runtime"
            (runtime / "world").mkdir(parents=True)
            (runtime / "world" / "level.dat").write_text("level", encoding="utf-8")
            (runtime / "plugins" / "TestPlugin").mkdir(parents=True)
            (runtime / "plugins" / "TestPlugin" / "config.yml").write_text("setting: true", encoding="utf-8")
            (runtime / "logs").mkdir()
            (runtime / "logs" / "latest.log").write_text("log", encoding="utf-8")
            (runtime / "paper.jar").write_bytes(b"jar")
            (runtime / "server.properties").write_text("motd=test", encoding="utf-8")
            archive = paper_backup.create_backup(runtime, root / "backup")
            with tarfile.open(archive, "r:gz") as bundle:
                names = set(bundle.getnames())
            self.assertIn("world/level.dat", names)
            self.assertIn("plugins/TestPlugin/config.yml", names)
            self.assertIn("server.properties", names)
            self.assertFalse(any("latest.log" in name or "paper.jar" in name for name in names))


if __name__ == "__main__":
    unittest.main()
