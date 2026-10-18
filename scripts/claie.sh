#!/bin/bash
# CLAIE v2: comenzi de la Arena prin repo. Fara gh, doar curl+git+token.
T=$(cat ~/.claie_token)
R="https://x-access-token:$T@github.com/iZentric/ServerRolePlayLite"
BR="arena/9bbcb24f-serverroleplaylite"
D="$HOME/srpl-claie"
[ -d "$D/.git" ] || git clone -q "$R" "$D" 2>/dev/null || { echo "clone esuat (sterge $D si reia login)"; exit 1; }
cd "$D"
git config user.email claie@arena.local && git config user.name claie
git checkout -q -B "$BR" "origin/$BR" 2>/dev/null
echo "=== CLAIE VIE: comenzile vin singure, eu le execut. Nu inchide fereastra. ==="
while true; do
  git fetch -q origin "$BR" 2>/dev/null
  L=$(git rev-parse "origin/$BR" 2>/dev/null) || { sleep 10; continue; }
  git reset -q --hard "$L" 2>/dev/null
  if [ -f cmd.sh ]; then
    V=$(git log -1 --format=%h "$L" -- cmd.sh 2>/dev/null)
    if [ "$(cat .ver 2>/dev/null)" != "$V" ]; then
      echo ">> rulez $V"; date > out.txt
      timeout 900 bash cmd.sh >> out.txt 2>&1; RC=$?
      echo "exit=$RC" >> out.txt
      echo "$V" > .ver
      git add -f out.txt .ver && git commit -qm "raspuns $V" && git push -q origin HEAD:"$BR"
    fi
  fi
  sleep 5
done
