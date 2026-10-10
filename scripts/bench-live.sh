#!/usr/bin/env bash
# BENCH-LIVE — repune puntea live (cmd.in -> consola serverului) si masoara serverul CUANTIC
# CU UN JUCATOR REAL IN LUME. Fara punte agentul doar pregateste config; cu punte vede si comanda.
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"

# ---- 1. supervisorul (puntea), fara sa omor serverul care merge deja ----
if ! pgrep -f 'bash .*c\.sh' >/dev/null 2>&1; then
  curl -fsSLo "$HOME/c.sh" "https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-live.sh" 2>/dev/null
  ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
  sleep 6
fi
SUP=NU; pgrep -f 'bash .*c\.sh' >/dev/null 2>&1 && SUP=DA
PID=$(pgrep -f 'java @unix_args' | head -1)
[ -n "$PID" ] && MC=SUS || MC=JOS

# ---- 2. proba de punte: comanda in consola, raspunsul citit din live.log ----
probe() { # $1=comanda  $2=cuvant de cautat in raspuns  $3=secunde de asteptat
  local t0=$(wc -l < "$L" 2>/dev/null)
  printf '%s\n' "$1" >> "$D/cmd.in"
  local i out=""
  for i in $(seq 1 $(( $3 / 3 ))); do
    sleep 3
    out=$(tail -n +$(( t0 + 1 )) "$L" 2>/dev/null | sed -e "$STRIP")
    printf '%s' "$out" | grep -qaE "$2" && break
  done
  # lucram cu o copie curat-A ANSI, ca sa prinDEM si liniile urmatoare (spark pune cifrele pe randurile de dupa titlu)
  printf '%s\n' "$out" > /tmp/probe.txt
  local m=$(grep -anE "$2" /tmp/probe.txt 2>/dev/null | tail -1 | cut -d: -f1)
  if [ -n "$m" ]; then
    tail -n +$m /tmp/probe.txt | head -14 | cut -c1-190 | tr '\n' ' | '
  else
    echo "FARA-RASPUNS"
  fi
}
echo "== PUNTE ==" > /tmp/bench.txt
echo "list: $(probe 'list' 'players online|online:' 30)" >> /tmp/bench.txt
echo "health: $(probe 'spark health' 'Tick|MSPT|TPS|timp' 60)" >> /tmp/bench.txt
echo "gc: $(probe 'spark gc' 'GC|pause|heap|Allocat' 60)" >> /tmp/bench.txt
echo "mem: $(probe 'spark memory' 'Heap|Memory|Allocated|used' 50)" >> /tmp/bench.txt
echo "chat: $(probe 'say agent: puntea de comanda functioneaza (test)' 'agent: puntea' 20)" >> /tmp/bench.txt

# ---- 3. statistici de OS, esantionate 60s ----
{ echo "== OS =="; free -m | awk 'NR==2{printf "ram_libera=%sMB total=%sMB\n",$7,$2}'
  df -h "$D" 2>/dev/null | tail -1 | awk '{printf "disc=%s din %s (%s)\n",$5,$2,$1}'
  echo "load: $(cat /proc/loadavg)  cpu=$(nproc) fire"
  echo "jstat_gcutil (60s, 6 esantioane):"
  if [ -n "$PID" ]; then
    "$(dirname "$J")/jstat" -gcutil "$PID" 10000 6 2>/dev/null | tail -7 | sed 's/^/  /'
    ps -o pid,pcpu,rss,etime -p "$PID" --no-headers 2>/dev/null | awk '{printf "  java cpu=%s%% rss=%dMB live=%s\n",$2,$3/1024,$4}'
  fi
} >> /tmp/bench.txt 2>&1

# ---- 4. ce zice logul despre tick-uri ----
{ echo "== LOG =="
  sed -e "$STRIP" "$L" 2>/dev/null > /tmp/clean.log
  echo "Done: $(grep -aoE 'Done \([0-9.]+s\)' /tmp/clean.log | tail -1)"
  echo "Can't keep up: total=$(grep -ac "Can't keep up" /tmp/clean.log) in_ultimele_4000=$(tail -4000 /tmp/clean.log | grep -ac "Can't keep up")"
  echo "chunk/incarcare (linii complete):"
  grep -aiE 'took [0-9.]+ ?(ms|s)' /tmp/clean.log | tail -5 | sed 's/^/  /' | cut -c1-180
  if [ -n "$PID" ]; then
    echo "jcmd/GC:"; "$(dirname "$J")/jcmd" "$PID" GC.heap_info 2>/dev/null | tail -6 | sed 's/^/  /' || echo "  jcmd indisponibil"
    echo "jstat:"; "$(dirname "$J")/jstat" -gcutil "$PID" 5000 6 2>&1 | tail -7 | sed 's/^/  /'
    echo "din /proc: $(grep -E 'VmRSS|VmHWM' /proc/$PID/status 2>/dev/null | tr '\n' ' ')"
  fi
  T0=$(date +%s%N); ( exec 3<>/dev/tcp/92.5.171.150/25565 ) 2>/dev/null; T1=$(date +%s%N)
  echo "latenta TCP pana la propriul port public: $(( (T1-T0)/1000000 ))ms"
  echo "erori CRITICE in sesiune: $(grep -aciE 'crash|out of memory|StackOverflow|Exception in server tick loop' /tmp/clean.log)"
  echo "frpc: $(tail -1 "$HOME/frpc.log" 2>/dev/null | cut -c1-90)"
} >> /tmp/bench.txt 2>&1

# ---- 5. verdict in commit ----
V="BENCH: punte=$SUP mc=$MC keeup=$(grep -ao 'total=[0-9]*' /tmp/bench.txt | head -1 | tr -d ' ')"
mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# BENCH live CUANTIC — $(date -u '+%F %T UTC')"; echo; echo '```'; cat /tmp/bench.txt; echo '```'; } > analysis/BENCH-LIVE.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/BENCH-LIVE.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
cat /tmp/bench.txt
exit 0
