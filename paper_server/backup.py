#!/usr/bin/env python3
"""Create a dated archive of generated Paper world, plugin and server data."""
from __future__ import annotations

import argparse
import datetime as dt
import tarfile
from pathlib import Path

INCLUDE_FILES = (
    "server.properties", "bukkit.yml", "spigot.yml", "commands.yml", "permissions.yml",
    "ops.json", "whitelist.json", "banned-ips.json", "banned-players.json", "usercache.json",
    "eula.txt", "config", "plugins",
)
EXCLUDE_NAMES = {"logs", "cache", "libraries", "versions", "paper.jar"}


def create_backup(runtime: Path, destination: Path | None = None) -> Path:
    runtime = runtime.resolve()
    if not runtime.is_dir():
        raise FileNotFoundError(f"Runtime directory does not exist: {runtime}")
    output_dir = destination.resolve() if destination else runtime.parent / "backups"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    archive = output_dir / f"paper-backup-{timestamp}.tar.gz"
    members: list[Path] = []
    for name in INCLUDE_FILES:
        path = runtime / name
        if path.exists():
            members.append(path)
    # Include all conventional world folders (world, world_nether, world_the_end and custom worlds).
    for path in runtime.iterdir():
        if path.is_dir() and path.name not in EXCLUDE_NAMES and (
            (path / "level.dat").exists() or path.name.startswith("world_")
        ):
            members.append(path)
    if not members:
        raise ValueError("No generated server data found to back up")
    with tarfile.open(archive, "w:gz") as bundle:
        for path in dict.fromkeys(members):
            bundle.add(path, arcname=path.relative_to(runtime), filter=_filter)
    return archive


def _filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(info.name).parts
    if any(part in EXCLUDE_NAMES or ".before-low-spec-" in part for part in parts):
        return None
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path(__file__).resolve().parent / "runtime")
    parser.add_argument("--destination", type=Path, help="optional private backup directory")
    args = parser.parse_args()
    try:
        archive = create_backup(args.runtime, args.destination)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Backup created: {archive}")
    print("Keep this archive private: plugin configs may contain private service credentials.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
