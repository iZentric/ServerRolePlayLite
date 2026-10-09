#!/usr/bin/env bash
# LIVE6 — raspuns final: traieste serverul dupa job? e acessibil? apoi curata tot ce NU e proiectul nostru.
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
say "== LIVE6 — $(date -u '+%F %T UTC') =="
say "uptime: $(uptime | sed 's/^ *//')"
say "heartbeat v1 (daca e viu, detasamentul functioneaza): $(tail -1 $HOME/cuantic-live/heartbeat.txt 2>/dev/null || echo 'fara fisier') | acum: $(date -u +%FT%TZ)"
say "procese: java=$(pgrep -fc 'java @unix_args' 2>/dev/null || echo 0) supervisor=$(pgrep -fc cuantic-supervise 2>/dev/null || echo 0) bore=$(pgrep -fc 'bore local' 2>/dev/null || echo 0) watchdog=$(pgrep -fc cuantic-watchdog 2>/dev/null || echo 0)"
say "port 25565:"; (ss -lnt 2>/dev/null | grep 25565 || echo "  NIMIC ASCULTAT") | sed 's/^/  /' >> $LOG
say "log live: $(grep -cE 'Starting Minecraft server on' $DIR/live.log 2>/dev/null) bind-uri | ultimul rand: $(tail -1 $DIR/live.log 2>/dev/null | cut -c1-120)"
say "jurnal eschere (de ce pica): $(grep -hE 'Stopping|SIGTERM|SIGINT|Done \(|Failed to bind|Exception' $DIR/live.log $DIR/sup.log 2>/dev/null | tail -5 | tr '\n' ' ' | cut -c1-400)"
for T in 127.0.0.1; do python3 -c "import socket;s=socket.socket();s.settimeout(3);s.connect(('$T',25565));s.close()" 2>/dev/null && say "  $T:25565 = DESCHIS" || say "  $T:25565 = REFUZAT"; done
B=$(grep -ohE 'listening at bore\.pub:[0-9]+' $DIR/bore.log 2>/dev/null | tail -1 | grep -oE '[0-9]+$')
say "bore: ${B:+bore.pub:$B}"
R=""
[ -n "$B" ] && R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/bore.pub:$B" 2>/dev/null)
say "probe publica: $(echo "$R" | grep -oE '\"online\":(true|false)' || echo n/a)"

VIU=NU
case "$R" in *'"online":true'*) VIU=DA;; esac
if [ "$VIU" = "DA" ]; then
  echo "Adresa de joc: bore.pub:$B" > $DIR/ADRESA
  say "==> serverul e JUCABIL pe bore.pub:$B (ramane asa, nu sterg)"
else
  say "==> Cloud Shell nu poate fi server de jocuri (fara intrare). Opresc si sterg tot ce am incercat aici."
  pkill -f cuantic-supervise 2>/dev/null; pkill -f 'bore local' 2>/dev/null; pkill -f bore-supervise 2>/dev/null
  pkill -f cuantic-watchdog 2>/dev/null; pkill -f cuantic-live 2>/dev/null; pkill -f 'java @unix_args' 2>/dev/null
  pkill -f heartbeat 2>/dev/null; rm -f $HOME/heartbeat.sh
  sleep 2
  rm -rf $HOME/cuantic $HOME/srv $HOME/srv.zip $HOME/pack.zip $HOME/bore.tgz $HOME/jdk17.tgz $HOME/.config/playit $HOME/playit $HOME/playit.tgz $HOME/.playit 2>/dev/null
  du -sh $DIR 2>/dev/null | sed 's/^/  what ramane: /' >> $LOG
  rm -rf $HOME/cuantic-live $HOME/cuantic-supervise.sh $HOME/bore-supervise.sh $HOME/cuantic-watchdog.sh $HOME/bore $HOME/ADRESA 2>/dev/null
  say "  curat: $(ls -d $HOME/* 2>/dev/null | grep -viE 'actions-runner|_work|\.oci|\.ssh|jdk-21|\.cache|\.local|\.config|\.git|profile|\.bash' | tr '\n' ' ')"
  say "  libere: $(df -h / | sed -n 2p)"
fi
say "GATA"; exit 0
