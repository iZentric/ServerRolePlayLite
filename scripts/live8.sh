#!/usr/bin/env bash
# LIVE8 — doar diagnostic, 60 sec: de ce nu ramane portul ascultat + de ce n-are bore port.
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
say "== LIVE8 diagnostic — $(date -u '+%F %T UTC') =="
say "java: $(ps -o pid,etime,rss,args -C java 2>/dev/null | tail -3 | tr '\n' '|')"
say "--- erorile:"; grep -nE '/ERROR\]|Failed to bind|Caused by|Exception|Done \(' $DIR/live.log 2>/dev/null | tail -20 | sed 's/^/  /' >> $LOG
say "--- live.log ultimul rand:"; tail -3 $DIR/live.log 2>/dev/null | sed 's/^/  /' >> $LOG
say "--- bore.log:"; tail -15 $DIR/bore.log 2>/dev/null | sed 's/^/  /' >> $LOG
say "--- porturi:"; ss -lnt 2>/dev/null | sed -n '1,12p' | sed 's/^/  /' >> $LOG
say "--- test bind 25565:"
python3 - <<'PY' 2>&1 | sed 's/^/  /' >> $LOG
import socket
s=socket.socket()
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0",25565)); s.listen(1)
    print("bind 0.0.0.0:25565 = POSIBIL (deci lipseste doar procesul care asculta)")
    c=socket.create_connection(("127.0.0.1",25565),timeout=3); print("  connect pe el = OK"); c.close()
except Exception as e:
    print("bind esuat:", e)
s.close()
PY
say "--- memorie: $(free -m | sed -n 2p) | disc: $(df -h / | sed -n 2p)"
say "--- cine a omorat java: din log, ultimele 6 linii inainte de stop:"
grep -nE 'Stopping|SIGTERM|SIGINT|Oom|OutOfMemory|Server thread/ERROR' $DIR/live.log 2>/dev/null | tail -8 | sed 's/^/  /' >> $LOG
mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
F=analysis/live.md
printf '# LIVE8 diagnostic — %s\n```\n' "$(date -u '+%F %T UTC')" > $F
cat $LOG >> $F
printf '```\n' >> $F
git add -f analysis/live.md; git commit -q -m "live8: diagnostic" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
