#!/bin/bash
# CLAIE = ureche+mana lui Arena in orice terminal cu net (Cloud Shell, boxa, oriunde).
# Arena scrie comenzi in fisierul cmd.sh din repo; tu le rulezi aici la infinit.
# Roundtrip ~10 sec. Fara porturi deschise, fara agent, fara runner.
R="https://github.com/iZentric/ServerRolePlayLite"
BR="arena/9bbcb24f-serverroleplaylite"
D="${CLAIE_DIR:-$HOME/srpl-claie}"
[ -d "$D/.git" ] || git clone -q "$R" "$D" || { echo "clone esuat"; exit 1; }
cd "$D"
git checkout -q -B "$BR" "origin/$BR" 2>/dev/null || git checkout -q "$BR"
git config user.email claie@arena.local; git config user.name "claie"
# autenticare automata: gh login token, altfel intreba
if command -v gh >/dev/null && gh auth token >/dev/null 2>&1; then
  git remote set-url origin "https://x-access-token:$(gh auth token)@github.com/iZentric/ServerRolePlayLite"
fi
echo "CLAIE PORNITA. Randez comenzi la ~10 sec. Ctrl+C opreste."
while true; do
  git fetch -q origin "$BR" 2>/dev/null
  L=$(git rev-parse origin/"$BR" 2>/dev/null); git update-ref refs/heads/"$BR" "$L" 2>/dev/null
  if [ -f cmd.sh ]; then
    V=$(git log -1 --format=%h "$L" -- cmd.sh 2>/dev/null)
    if [ "$(cat .ver 2>/dev/null)" != "$V" ]; then
      echo ">> rulez $V"
      timeout 600 bash cmd.sh > out.txt 2>&1; RC=$?
      echo "exit=$RC" >> out.txt
      echo "$V" > .ver
      git add -f out.txt .ver && git commit -qm "raspuns $V" && git push -q origin HEAD:"$BR"
    fi
  fi
  sleep 5
done
