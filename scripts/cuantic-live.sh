#!/bin/bash
# CUANTIC live v3 — Cloud Shell. Reporneste DOAR cand sesiunea tmux a murit (nu dupa timp).
D=$HOME/cuantic-live
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
[ -x "$J" ] || J=$(command -v java)
cd "$D" || exit 1
echo "JAVA: $J"
[ -f unix_args.txt ] || { echo "pack lipsa"; exit 1; }
echo eula=true > eula.txt
pkill -f 'tmux new -s mc' 2>/dev/null
tmux kill-session -t mc 2>/dev/null
tmux kill-session -t frpc 2>/dev/null
tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"
tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
echo "adresa: 92.5.171.150:25565   (Ctrl+C = opresti supervisorul, nu serverul)"
LAST=-1
while :; do
  NOW=$(wc -l < live.log 2>/dev/null)
  if ss -lnt | grep -q ':25565'; then
    S="SUS — se poate intra"
  else
    S="nu asculta"
    if ! tmux ls 2>/dev/null | grep -q '^mc:'; then
      echo " sesiunea mc a murit -> o pornesc la loc $(date +%T)"
      tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"; LAST=0
    elif [ "$NOW" = "$LAST" ]; then
      echo " log blocat la $NOW linii, ultimele:"; tail -2 live.log
      echo " frpc ultimele:"; tail -1 $HOME/frpc.log 2>/dev/null
    fi
  fi
  tmux ls 2>/dev/null | grep -q '^frpc:' || { echo " frpc jos -> pornit $(date +%T)"; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; }
  echo " $(date +%T) $S | live.log $NOW linii | tmux: $(tmux ls 2>/dev/null | cut -d: -f1 | tr '\n' ' ')"
  LAST=$NOW
  sleep 15
done
