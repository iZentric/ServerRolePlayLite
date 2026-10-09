#!/bin/bash
# CUANTIC live — se ruleaza in tabul TAU de Cloud Shell si il lasi deschis.
# 20:41 fix: reporneste MC DOAR daca procesul a murit (nu daca portul e inca in load).
J=/usr/lib/jvm/java-17/bin/java
cd ~/cuantic-live
echo "adresa: 92.5.171.150:25565  (Ctrl+C = opresti tot)"
while :; do
  if ! pgrep -f unix_args.txt > /dev/null; then
    tmux kill-session -t mc 2>/dev/null
    tmux new -s mc -d "cd ~/cuantic-live && $J @unix_args.txt > live.log 2>&1"
    echo "MC pornit la $(date +%T) — load 60-90s"
  fi
  if ! pgrep -f "frpc -c" > /dev/null; then
    tmux kill-session -t frpc 2>/dev/null
    tmux new -s frpc -d "exec ~/frpc -c ~/frpc.toml > frpc.log 2>&1"
    echo "frpc pornit la $(date +%T)"
  fi
  if ss -lnt | grep -q ':25565'; then
    echo " $(date +%T) SUS — port 25565 asculta, se poate intra"
  else
    echo " $(date +%T) se incarca..."
  fi
  sleep 20
done
