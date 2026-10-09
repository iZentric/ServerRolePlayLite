#!/bin/bash
# CUANTIC live — se ruleaza in tabul TAU de Cloud Shell si il lasi deschis.
# Face singur tot ce trebuie, la nesfarsit: serverul MC + tunelul frpc.
J=/usr/lib/jvm/java-17/bin/java
cd ~/cuantic-live
echo "adresa: 92.5.171.150:25565  (Ctrl+C = opresti tot)"
while :; do
  if ! ss -lnt | grep -q ':25565'; then
    tmux kill-session -t mc 2>/dev/null
    tmux new -s mc -d "cd ~/cuantic-live && $J @unix_args.txt > live.log 2>&1"
    echo "MC repornit la $(date +%T) — face ~60-90s sa se incarce"
  fi
  if ! pgrep -f "frpc -c" > /dev/null; then
    tmux kill-session -t frpc 2>/dev/null
    tmux new -s frpc -d "exec ~/frpc -c ~/frpc.toml > frpc.log 2>&1"
    echo "frpc repornit la $(date +%T)"
  fi
  sleep 20
done
