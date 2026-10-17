#!/bin/bash
# CLAIE v4: lock unic, fara ucideri, push cu retry (nu mai ia foc terminalul)
T=$(cat ~/.claie_token 2>/dev/null)
R="https://x-access-token:${T:-none}@github.com/iZentric/ServerRolePlayLite"
BR="arena/9bbcb24f-serverroleplaylite"
D="$HOME/srpl-claie"
LK="$HOME/.claie.lock"
if [ -d "$LK" ]; then P=$(cat "$LK/pid" 2>/dev/null); if [ -n "$P" ] && kill -0 "$P" 2>/dev/null; then echo "CLAIE exista deja (pid $P) - ies"; exit 0; fi; fi
mkdir -p "$LK"; echo $$ > "$LK/pid"; trap 'rm -rf "$LK"' EXIT
[ -d "$D/.git" ] || git clone -q "$R" "$D" || { echo "clone esuat (ruleaza login)"; exit 1; }
cd "$D" || exit 1
git config user.email claie@arena.local && git config user.name claie
git fetch -q origin "$BR" && git checkout -q -B "$BR" "origin/$BR" 2>/dev/null
echo "=== CLAIE VIE v4: ascult comenzile. Nu inchide fereastra. ==="
while true; do
  git fetch -q origin "$BR" 2>/dev/null
  L2=$(git rev-parse "origin/$BR" 2>/dev/null) || { sleep 10; continue; }
  git merge -q --no-edit -X ours "$L2" 2>/dev/null || git merge --abort 2>/dev/null
  if [ -f cmd.sh ]; then
    V=$(git log -1 --format=%h "$L2" -- cmd.sh 2>/dev/null)
    if [ "$(cat .ver 2>/dev/null)" != "$V" ]; then
      echo ">> rulez $V"
      date > out.txt
      timeout 900 bash cmd.sh >> out.txt 2>&1
      echo "exit=$?" >> out.txt
      echo "$V" > .ver
      git add -f out.txt .ver && git commit -qm "raspuns $V"
      for a in 1 2 3 4 5; do
        git push -q origin HEAD:"$BR" && break
        git pull -q --no-rebase -X ours origin "$BR" 2>/dev/null; sleep 3
      done
      echo ">> raspuns impins"
    fi
  fi
  sleep 5
done
