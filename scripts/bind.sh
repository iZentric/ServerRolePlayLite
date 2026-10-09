#!/usr/bin/env bash
# BIND — test curat: pornim MC cu stdin tinut de INSASI scriptul (fifo, exec 9<>) si vedem
# daca socketul 25565 apare. Fara bore, fara mentinere.
LOG=/tmp/bind.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
say "== BIND test — $(date -u '+%F %T UTC') =="
cd $DIR 2>/dev/null || { say "nu exista $DIR"; exit 0; }
say "jar: $(ls CatServer-*.jar 2>/dev/null | head -1)"
[ -f CatServer-1.16.5-1d8d6313-server.jar ] || say "LIPSESTE packul"
echo 'eula=true' > eula.txt
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
pkill -f 'unix_args.txt' 2>/dev/null; sleep 2

rm -f cin; mkfifo cin
exec 9<>$DIR/cin
"$J17" @unix_args.txt <&9 > $DIR/bind.log 2>&1 &
JP=$!
say "java pid $JP"
for i in $(seq 1 60); do
  sleep 3
  if ss -lnt 2>/dev/null | grep -q ':25565'; then say "SOCKET 25565: APARUT la it $i"; break; fi
  kill -0 $JP 2>/dev/null || { say "java a murit la it $i"; break; }
  [ $i -eq 30 ] && say "  la 90s: inca $(kill -0 $JP 2>/dev/null && echo viu || echo mort), log $(wc -l < $DIR/bind.log) linii"
done
say "log lines: $(wc -l < $DIR/bind.log 2>/dev/null) | Done: $(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/bind.log)"
say "ss:"; ss -lnt 2>/dev/null | sed -n '1,8p' | sed 's/^/  /' >> $LOG
python3 - <<'PY' >> $LOG 2>&1
import socket
for h in ("127.0.0.1", "10.215.108.231"):
    try:
        s = socket.create_connection((h, 25565), timeout=5)
        s.sendall(bytes.fromhex("00090003fe") + b"\x00\x00")
        print(" ", h, ": raspuns", s.recv(32)[:12])
    except Exception as e:
        print(" ", h, ":", e)
PY
say "ultimele 10 din bind.log:"; tail -10 $DIR/bind.log | cut -c1-140 | sed 's/^/  /' >> $LOG
kill $JP 2>/dev/null
mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# BIND test — %s\n\n' "$(date -u '+%F %T UTC')"; echo '```'; cat $LOG; echo '```'; } > analysis/bind.md
git add -f analysis/bind.md; git commit -q -m "bind test" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
