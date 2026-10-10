#!/usr/bin/env bash
# Construieste pluginul Cuantic pentru /version FARA maven: ne legam direct de jarul serverului
# (CatServer contine clasele org.bukkit.*), deci API-ul cu care compilam e exact cel de runtime.
set -e
cd "$(dirname "$0")/../.."
V=$(python3 -c "import json;print(json.load(open('pack-rules.json'))['pack_version'])")
OUT=tools/cuantic-brand/out
mkdir -p "$OUT/build/classes"
CS="$OUT/catserver.jar"
if [ ! -s "$CS" ]; then
  URL=$(curl -fsS --max-time 40 "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite" \
        | python3 -c "import sys,json;print(next((a['browser_download_url'] for a in json.load(sys.stdin).get('assets',[]) if 'Server-CatServer' in a['name']),''))")
  [ -n "$URL" ] || { echo "build: nu gasesc zip-ul de server pe release"; exit 1; }
  curl -fsSLo "$OUT/p.zip" --max-time 400 "$URL"
  JAR=$(unzip -Z1 "$OUT/p.zip" | grep -m1 -E '\.jar$')
  unzip -qo "$OUT/p.zip" "$JAR" -d "$OUT" && mv "$OUT/$JAR" "$CS" && rm -f "$OUT/p.zip"
fi
sed "s/__VER__/$V/" tools/cuantic-brand/plugin.yml > "$OUT/build/plugin.yml"
javac --release 8 -nowarn -cp "$CS" -d "$OUT/build/classes" tools/cuantic-brand/src/cloud/cuantic/brand/CuanticBrandPlugin.java
( cd "$OUT/build" && jar cf "../Cuantic-Brand-$V.jar" plugin.yml classes )
cp "$OUT/Cuantic-Brand-$V.jar" "$OUT/Cuantic-Brand.jar"
unzip -l "$OUT/Cuantic-Brand-$V.jar" | tail -4
echo "build: Cuantic-Brand-$V.jar OK (compilat impotriva $(du -h "$CS" | cut -f1) de jar server)"
