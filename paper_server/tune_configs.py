#!/usr/bin/env python3
"""Tune only Paper-generated low-spec settings; never create missing YAML keys."""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
from pathlib import Path

SERVER_PROPERTIES = {
    "view-distance": "8",
    "simulation-distance": "4",
}
BUKKIT_LIMITS = {
    "spawn-limits.monsters": "35",
    "spawn-limits.animals": "6",
    "spawn-limits.water-animals": "3",
    "spawn-limits.water-ambient": "4",
    "spawn-limits.water-underground-creature": "3",
    "spawn-limits.axolotls": "2",
    "spawn-limits.ambient": "1",
}
PAPER_LIMITS = {
    "entities.spawning.spawn-limits.monster": "35",
    "entities.spawning.spawn-limits.creature": "6",
    "entities.spawning.spawn-limits.water_creature": "3",
    "entities.spawning.spawn-limits.water_ambient": "4",
    "entities.spawning.spawn-limits.underground_water_creature": "3",
    "entities.spawning.spawn-limits.axolotls": "2",
    "entities.spawning.spawn-limits.ambient": "1",
}
PAPER_DESPAWN_PATHS = tuple(
    f"entities.spawning.despawn-ranges.{category}.{bound}"
    for category in (
        "monster", "creature", "ambient", "axolotls", "underground_water_creature",
        "water_creature", "water_ambient", "misc",
    )
    for bound in ("hard", "soft")
)


def _replace_properties(text: str, values: dict[str, str], required: bool = True) -> tuple[str, list[str]]:
    lines = text.splitlines(keepends=True)
    found: dict[str, int] = {}
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if not stripped or stripped.startswith(("#", "!")) or "=" not in stripped and ":" not in stripped:
            continue
        key, sep, _value = re.split(r"([=:])", stripped, maxsplit=1)
        key = key.strip()
        if key in values:
            found[key] = found.get(key, 0) + 1
            newline = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
            indent = line[: len(line) - len(stripped)]
            lines[index] = f"{indent}{key}{sep}{values[key]}{newline}"
    duplicates = [key for key, count in found.items() if count != 1]
    missing = sorted(set(values) - set(found))
    if duplicates:
        raise ValueError(f"duplicate server.properties key(s): {', '.join(duplicates)}")
    if required and missing:
        raise ValueError(f"required generated property key(s) missing: {', '.join(missing)}")
    return "".join(lines), missing


def _replace_yaml_paths(text: str, values: dict[str, str], *, required: bool = True) -> tuple[str, list[str]]:
    """Update plain scalar keys by indentation path while preserving comments/formatting."""
    lines = text.splitlines(keepends=True)
    stack: list[tuple[int, str]] = []
    found: dict[str, int] = {}
    for index, line in enumerate(lines):
        match = re.match(r"^( *)([A-Za-z0-9_-]+):(?:[ \t]*(.*?))?(\r?\n)?$", line)
        if not match:
            continue
        indent = len(match.group(1))
        key = match.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([item[1] for item in stack] + [key])
        if path in values:
            found[path] = found.get(path, 0) + 1
            prefix = f"{match.group(1)}{key}:"
            rest = match.group(3) or ""
            newline = match.group(4) or ""
            comment = ""
            comment_match = re.search(r"\s+#.*$", rest)
            if comment_match:
                comment = comment_match.group(0)
            lines[index] = f"{prefix} {values[path]}{comment}{newline}"
        if not (match.group(3) or "").strip().startswith(("#", "'", '"')):
            stack.append((indent, key))
    duplicates = [key for key, count in found.items() if count != 1]
    missing = sorted(set(values) - set(found))
    if duplicates:
        raise ValueError(f"duplicate generated YAML key path(s): {', '.join(duplicates)}")
    if required and missing:
        raise ValueError(f"required generated YAML key path(s) missing: {', '.join(missing)}")
    return "".join(lines), missing


def _require_eula_accepted(runtime: Path) -> None:
    eula = runtime / "eula.txt"
    if not eula.is_file() or not re.search(r"(?m)^eula\s*=\s*true\s*$", eula.read_text(encoding="utf-8")):
        raise ValueError("runtime/eula.txt must exist with eula=true after the server owner has read and accepted the Minecraft EULA")


def tune(runtime: Path) -> list[str]:
    _require_eula_accepted(runtime)
    targets = {
        runtime / "server.properties": (SERVER_PROPERTIES, "properties", True),
        runtime / "bukkit.yml": (BUKKIT_LIMITS, "yaml", True),
        runtime / "spigot.yml": ({"world-settings.default.mob-spawn-range": "3"}, "yaml", True),
        runtime / "config" / "paper-world-defaults.yml": (PAPER_LIMITS, "yaml", True),
    }
    # Despawn keys are edited only where the generated defaults actually contain them.
    paper_defaults = runtime / "config" / "paper-world-defaults.yml"
    original_paper = paper_defaults.read_text(encoding="utf-8") if paper_defaults.is_file() else ""
    available_despawn = {}
    if original_paper:
        for path in PAPER_DESPAWN_PATHS:
            updated, missing = _replace_yaml_paths(original_paper, {path: "48" if path.endswith(".hard") else "24"}, required=False)
            if not missing:
                available_despawn[path] = "48" if path.endswith(".hard") else "24"
    if available_despawn:
        targets[paper_defaults] = ({**PAPER_LIMITS, **available_despawn, "entities.spawning.per-player-mob-spawns": "true"}, "yaml", True)
    else:
        targets[paper_defaults] = ({**PAPER_LIMITS, "entities.spawning.per-player-mob-spawns": "true"}, "yaml", True)

    prepared: dict[Path, str] = {}
    for path, (values, kind, required) in targets.items():
        if not path.is_file():
            raise FileNotFoundError(f"Missing Paper-generated config: {path}. Boot the server once and stop it cleanly first.")
        source = path.read_text(encoding="utf-8")
        if kind == "properties":
            output, _missing = _replace_properties(source, values, required=required)
        else:
            output, _missing = _replace_yaml_paths(source, values, required=required)
        prepared[path] = output

    changed = [path for path, content in prepared.items() if path.read_text(encoding="utf-8") != content]
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for path in changed:
        backup = path.with_name(f"{path.name}.before-low-spec-{stamp}.bak")
        shutil.copy2(path, backup)
    for path in changed:
        path.write_text(prepared[path], encoding="utf-8", newline="")
    return [str(path.relative_to(runtime)) for path in changed]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=Path(__file__).resolve().parent / "runtime")
    args = parser.parse_args(argv)
    try:
        changed = tune(args.runtime.resolve())
    except (OSError, ValueError) as error:
        print(f"Config tune aborted without writing changes: {error}", file=sys.stderr)
        return 1
    print("Updated generated Paper keys (backups made before any change):")
    for path in changed:
        print(f"  {path}")
    if not changed:
        print("  no changes needed; generated defaults already match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
