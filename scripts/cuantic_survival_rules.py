#!/usr/bin/env python3
"""Read-only InControl survival rule review. Never claims a static check proves gameplay.

For the 1.16.5 InControl author's docs, a deny rule that activates ABOVE a
mob count uses `mincount`; `maxcount` tests the opposite condition. This tool
flags an obvious inversion, but runtime Forge client tests are still required.
"""
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

AUTHOR_DOCS = "https://mcjty.eu/docs/mods/control-mods/control-mods-16"


def review(data):
    if not isinstance(data, list):
        return ["BLOCK: spawn.json must be a JSON array"]
    findings = []
    for index, rule in enumerate(data, 1):
        if not isinstance(rule, dict):
            findings.append(f"BLOCK: rule {index} is not an object")
            continue
        if rule.get("result") != "deny":
            continue
        conditions = set(rule) - {"result", "continue", "comment", "__comment"}
        if not conditions:
            findings.append(f"BLOCK: rule {index} denies every natural spawn")
        elif rule.get("hostile") is True and "maxcount" in rule and "mincount" not in rule:
            findings.append(f"BLOCK: rule {index} uses maxcount + deny for hostile mobs; likely inverted cap. Author's 1.16+ example uses mincount + deny above limit")
        elif rule.get("hostile") is True and not any(x in rule for x in ("maxcount", "mincount", "dimension", "biome", "mob", "area", "time", "mintime", "maxtime", "maxheight", "minheight", "phase", "seesky", "random")):
            findings.append(f"BLOCK: rule {index} denies hostile spawns without a limiting condition")
    if not findings:
        findings.append("NEVALIDAT: static rules did not show the known inversion; natural mob spawns, survival and memory still need client-side staging tests")
    return findings


def review_pack(path):
    """Small fail-closed archive preflight for a *new* CatServer pack, not gameplay proof."""
    findings = []
    required = {
        "server.properties": ("spawn-monsters=true", "gamemode=survival"),
        "bukkit.yml": ("allow-end: true",),
        "spigot.yml": ("nerf-spawner-mobs: false", "zombie-aggressive-towards-villager: true",
                       "hopper-transfer: 8", "hopper-check: 1", "hopper-amount: 1"),
    }
    with ZipFile(path) as archive:
        for name, keys in required.items():
            if archive.namelist().count(name) != 1:
                findings.append(f"BLOCK: missing or duplicate {name}")
                continue
            lines = [line.strip() for line in archive.read(name).decode("utf-8").splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
            for key in keys:
                separator = "=" if name.endswith(".properties") else ":"
                setting = key.split(separator, 1)[0]
                if len([line for line in lines if line.split(separator, 1)[0] == setting]) != 1 or key not in lines:
                    findings.append(f"BLOCK: {name} does not uniquely preserve {key}")
            if name == "server.properties":
                difficulty = [line for line in lines if line.startswith("difficulty=")]
                if len(difficulty) != 1 or difficulty[0] not in ("difficulty=easy", "difficulty=normal", "difficulty=hard"):
                    findings.append("BLOCK: server.properties difficulty must be explicitly non-peaceful")
    return findings


def load(path):
    if str(path).endswith(".zip"):
        with ZipFile(path) as archive:
            if archive.namelist().count("config/incontrol/spawn.json") != 1:
                raise ValueError("missing or duplicate spawn.json in pack")
            return json.loads(archive.read("config/incontrol/spawn.json"))
    text = Path(path).read_text(encoding="utf-8")
    if str(path).endswith(".md"):
        # CHK is a dated read-only snapshot of a live file, not the live file.
        match = re.search(r"\[OK\] config/incontrol/spawn\.json[^\n]*?:\s*(\[[^\n]+\])", text)
        if not match:
            raise ValueError("no InControl spawn.json snapshot in report")
        text = match.group(1)
    return json.loads(text)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: cuantic_survival_rules.py <config/incontrol/spawn.json | pack.zip | analysis/chk.md>")
    try:
        findings = review(load(sys.argv[1]))
        if sys.argv[1].endswith(".zip"):
            findings.extend(review_pack(sys.argv[1]))
        for finding in findings:
            print(finding)
        print("InControl 1.16+ author documentation:", AUTHOR_DOCS)
        sys.exit(2 if any(f.startswith("BLOCK") for f in findings) else 0)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"NEMASURAT: could not read rules: {exc}", file=sys.stderr)
        sys.exit(2)
