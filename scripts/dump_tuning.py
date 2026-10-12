#!/usr/bin/env python3
"""Scrie straturile de tuning CUANTIC ca fisiere de sine statatoare (site/tuning/).
Le foloseste scripts/tune-live.sh pe box-ul live, ca sa nu existe doua surse de adevar:
continutul vine din scripts/build_lite.py, singurul loc unde se genereaza si zip-ul."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_lite as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(ROOT, "site", "tuning")
os.makedirs(out, exist_ok=True)
fis = {"spigot.yml": B.SPIGOT_YML, "bukkit.yml": B.BUKKIT_YML,
       "catserver.yml": B.CATSERVER_YML, "commands.yml": B.COMMANDS_YML}
for n, t in fis.items():
    with open(os.path.join(out, n), "w", encoding="utf-8") as f:
        f.write(t)
with open(os.path.join(out, "server.properties.keys"), "w", encoding="utf-8") as f:
    f.write("\n".join(l for l in B.SERVER_PROPERTIES.split("\n")
                      if "=" in l and not l.startswith("#")))
print("tuning scris in", out, "->", ", ".join(sorted(fis)))
