#!/bin/bash
# CUANTIC live v5 — serverul + puntea de comenzi.
# In aceeasi masina cu serverul: java isi tine stdin deschis printr-un fifo (fara EOF = fara "Stopping server" fantoma)
# si citeste comenzi de consola din ~/cuantic-live/cmd.in (scrise din orice container, inclusiv de agent).
D=$HOME/cuantic-live
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
cd "$D" || { echo "nu exista $D"; exit 1; }
echo eula=true > eula.txt
: > cmd.in
mkfifo -m 600 in.fifo 2>/dev/null
exec 3<>in.fifo
echo "JAVA: $J -> $("$J" -version 2>&1 | head -1)"
[ -s "$(ls CatServer-*.jar 2>/dev/null | head -1)" ] || echo "!! jar absent - ruleaza jobul JAVA inainte"
tmux kill-session -t frpc 2>/dev/null
tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
"$J" @unix_args.txt < in.fifo > live.log 2>&1 &
MC=$!
echo "MC pornit (pid $MC). Adresa: 92.5.171.150:25565. Ctrl+C = opresti DOAR supervisorul."
LAST=-1
while :; do
  # puntea: orice linie din cmd.in merge in consola serverului
  if [ -s cmd.in ]; then
    while IFS= read -r L; do
      [ -n "$L" ] || continue
      case "$L" in
        restart) echo "[$(date +%T)] restart cerut"; kill -TERM $MC 2>/dev/null; sleep 8
                 "$J" @unix_args.txt < in.fifo > live.log 2>&1 & MC=$!; echo "[$(date +%T)] MC pid $MC" ;;
        stop)    echo "[$(date +%T)] stop cerut"; printf 'stop\n' >&3; sleep 6 ;;
        *)       printf '%s\n' "$L" >&3; echo "[$(date +%T)] trimis: $L" ;;
      esac
    done < cmd.in
    : > cmd.in
  fi
  NOW=$(wc -l < live.log 2>/dev/null)
  if kill -0 $MC 2>/dev/null; then ALIVE=DA; else ALIVE=NU; fi
  if ss -lnt | grep -q ':25565'; then S="SUS"; else S="nu asculta"; fi
  echo " $(date +%T) mc=$ALIVE port=$S log=$NOW"
  if [ "$ALIVE" = NU ]; then
    echo " mc mort -> repornesc"; "$J" @unix_args.txt < in.fifo > live.log 2>&1 & MC=$!; LAST=0
  elif [ "$NOW" = "$LAST" ]; then
    echo " log blocat:"; tail -2 live.log; tail -1 "$HOME/frpc.log" 2>/dev/null
  fi
  tmux ls 2>/dev/null | grep -q '^frpc:' || { echo " frpc jos -> pornit"; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; }
  LAST=$NOW
  sleep 15
done
