#!/usr/bin/env bash
# Read-only live inspection. Does NOT restart java, replace jars, or write to world.
D="$HOME/cuantic-live"
printf '# ENGINE PREFLIGHT — %s UTC\n\n```\n' "$(date -u '+%F %T')"
if [ ! -d "$D" ]; then echo 'STOP: live directory missing'; echo '```'; exit 1; fi
JAR="$D/CatServer-1.16.5-1d8d6313-server.jar"
printf 'java: '; pgrep -af 'java @unix_args.txt' | head -2 || true
printf 'supervisor: '; pgrep -af '^bash .*/c\.sh$' | head -2 || true
printf 'public tunnel: '; pgrep -af '^.*/frpc -c ' | head -2 || true
printf 'port 25565: '; ss -lnt | grep ':25565' || echo CLOSED
printf 'jar: '; sha256sum "$JAR" 2>/dev/null || echo ABSENT
printf 'mods / plugins: '; echo "$(find "$D/mods" -maxdepth 1 -name '*.jar' 2>/dev/null | wc -l) / $(find "$D/plugins" -maxdepth 1 -name '*.jar' 2>/dev/null | wc -l)"
printf 'disk home + temp:\n'; df -h "$D" /tmp | tail -2
printf 'memory:\n'; free -m | head -2
LEVEL=$(sed -n 's/^level-name=//p' "$D/server.properties" | tail -1)
LEVEL=${LEVEL:-world}
for w in "$LEVEL" "${LEVEL}_nether" "${LEVEL}_the_end"; do [ ! -e "$D/$w" ] || du -sh "$D/$w"; done
printf 'log cursor: '; wc -l < "$D/live.log" 2>/dev/null || true
if [ -f "$D/cmd.in" ]; then
  n=$(wc -l < "$D/live.log" 2>/dev/null || echo 0)
  printf 'list\n' >> "$D/cmd.in"
  sleep 6
  printf 'players (console, current): '
  tail -n +$((n+1)) "$D/live.log" | grep -a 'There are .* players online' | tail -1 || echo 'NO RESPONSE — do not restart'
fi
printf '\nNote: inspect before any restart; never infer zero players from an empty reply.\n```\n'
