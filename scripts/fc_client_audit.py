#!/usr/bin/env python3
"""Read-only audit of historical client evidence, not a Forge/FPS benchmark.

Never opens diag/pc-probe.txt, out/, installed clients, or the live server.
"""
import argparse
import json
import re
from pathlib import Path


INVENTORY = re.compile(r"^lista: (.+)$", re.MULTILINE)
FAILED = re.compile(r"^\[([^]]+)\].*Failed to load registry, closing connection", re.MULTILINE)
JOINED = re.compile(r"joined the game|logged in with entity id", re.IGNORECASE)
ESSENTIAL = (
    "Clumps-", "lazydfu-", "oculus-", "rubidium-", "modernfix-", "ferritecore-"
)
GAMEPLAY = (
    "cgm-", "cfm-", "vehicle-mod-", "modernlife-", "Modernxl ",
    "Pizzaland_", "roadstuff-", "additional-guns-", "supplementaries-"
)
# Dependencies verified against the mod authors' release pages; filename audit only.
DEPENDENCIES = {
    "additional-guns-": ("cgm-", "obfuscate-"),
    "cgm-": ("obfuscate-",),
    "vehicle-mod-": ("obfuscate-",),
    "roadstuff-": ("mapperbase-",),
    "supplementaries-": ("selene-",),
    "emotecraft-": ("player-animation-lib-forge-",),
    "oculus-": ("rubidium-",),
}


def audit(inventory_text, handshake_text, properties_text):
    profiles = [[s.strip() for s in line.split(", ")]
                for line in INVENTORY.findall(inventory_text)]
    if len(profiles) != 2 or not profiles[0] or profiles[0] != profiles[1]:
        raise ValueError("two nonempty identical client inventories required")
    jars = profiles[0]
    if len(jars) != len(set(jars)):
        raise ValueError("duplicate JAR filename in client inventory")
    required = ESSENTIAL + GAMEPLAY
    if any(sum(jar.startswith(name) for jar in jars) != 1 for name in required):
        raise ValueError("expected compatibility/gameplay JAR missing or duplicated")
    for parent, children in DEPENDENCIES.items():
        if any(jar.startswith(parent) for jar in jars):
            for child in children:
                if sum(jar.startswith(child) for jar in jars) != 1:
                    raise ValueError(f"dependency {parent} -> {child} missing or duplicated")
    properties = dict(line.split("=", 1) for line in properties_text.splitlines()
                      if line and not line.startswith("#") and "=" in line)
    failures = sorted(set(FAILED.findall(handshake_text)))
    if not failures or "clumps:xp_orb_big" not in handshake_text:
        raise ValueError("expected historical Clumps registry failure absent")
    return {
        "scope": "historical logs and repository config only; not installed/live pack",
        "profiles": len(profiles),
        "unique_jars_per_profile": len(jars),
        "compatibility_and_optimizers_named": len(ESSENTIAL),
        "gameplay_jars_named": len(GAMEPLAY),
        "dependency_edges_checked": sum(len(children) for parent, children in DEPENDENCIES.items()
                                        if any(jar.startswith(parent) for jar in jars)),
        "culling_and_collision_jars": [jar for jar in jars if jar.startswith(
            ("entityculling-", "out_of_sight-", "entitycollisionfpsfix-"))],
        "clumps_registry_failure_timestamps": failures,
        "explicit_join_in_excerpt": bool(JOINED.search(handshake_text)),
        "repo_view_chunks": int(properties["view-distance"]),
        "repo_entity_broadcast_percent": int(properties["entity-broadcast-range-percentage"]),
        "fps_samples": "not collected here",
    }


def self_test():
    prefixes = set(ESSENTIAL + GAMEPLAY + tuple(DEPENDENCIES))
    prefixes.update(child for children in DEPENDENCIES.values() for child in children)
    fixture = "lista: " + ", ".join(name + "test.jar" for name in sorted(prefixes))
    log = "[18Oct2026 16:00:51.807] Failed to load registry, closing connection\nclumps:xp_orb_big"
    props = "view-distance=5\nentity-broadcast-range-percentage=80"
    good = audit(fixture + "\n" + fixture, log, props)
    assert good["unique_jars_per_profile"] == len(prefixes)
    assert good["dependency_edges_checked"] == 8
    assert good["clumps_registry_failure_timestamps"] == ["18Oct2026 16:00:51.807"]
    assert good["explicit_join_in_excerpt"] is False
    assert audit(fixture + "\n" + fixture, log + "\njoined the game", props)["explicit_join_in_excerpt"]
    duplicate = fixture + ", " + ESSENTIAL[0] + "test.jar"
    no_mapper = fixture.replace(", mapperbase-test.jar", "")
    for broken in (fixture, fixture + "\n" + duplicate, duplicate + "\n" + duplicate,
                   no_mapper + "\n" + no_mapper):
        try:
            audit(broken, log, props)
        except ValueError:
            pass
        else:
            raise AssertionError("incomplete or mismatched profile accepted")
    print("client-audit fixture PASS (matching profiles, failures, join marker, duplicate/dependency rejection)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    else:
        print(json.dumps(audit(Path("diag/pc-client.txt").read_text(),
                               Path("diag/fix.txt").read_text(),
                               Path("functity-config/server.properties").read_text()),
                         ensure_ascii=False, indent=2))
