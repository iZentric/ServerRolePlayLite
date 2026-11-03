#!/bin/bash
# CLAIE v3: comenzi de la Arena prin repo. Nu moara la dedup.
T=$(cat ~/.claie_token 2>/dev/null)
R="https://x-access-token:${T:-none}@github.com/iZentric/ServerRolePlayLite"
BR="arena/9bbcb24f-serverroleplaylite"
D="$HOME/srpl-claie"
[ -d "$D/.git" ] || git clone -q "$R" "$D" 2>/dev/null || { echo "clone esuat (ruleaza login)"; exit 1; }
cd "$D"
git config user.email claie@arena.local && git config user.name claie
git checkout -q -B "$BR" "origin/$BR" 2>/dev/null
# dedup: omoram doar ALTII (nu parintele bunicul-pierdut)
SELF=$$
for p in $(pgrep -f "bash.*claie" 2>/dev/null); do
  [ "$p" = "$SELF" ] && continue
  tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | grep -q "claie.sh" && { [ "$(ps -o tpgid= -p $p)" = "$(ps -o tpgid= -p $$)" ] && continue; kill "$p" 2>/dev/null; }
done
echo "=== CLAIE VIE: comenzile vin singure, eu le execut. Nu inchide fereastra. ==="
while true; do
  git fetch -q origin "$BR" 2>/dev/null
  L=$(git rev-parse "origin/$BR" 2>/dev/null) || { sleep 10; continue; }
  git reset -q --hard "$L" 2>/dev/null
  if [ -f cmd.sh ]; then
    V=$(git log -1 --format=%h "$L" -- cmd.sh 2>/dev/null)
    if [ "$(cat .ver 2>/dev/null)" != "$V" ]; then
      echo ">> rulez $V"
      ( trap '' TERM HUP INT; date > out.txt; timeout 900 bash cmd.sh >> out.txt 2>&1; echo "exit=$?" >> out.txt; echo "$V" > .ver
        git add -f out.txt .ver && git commit -qm "raspuns $V" && git push -q origin HEAD:"$BR" ) &
      WP=$!
      disown
    fi
  fi
  sleep 5
done
