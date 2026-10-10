#!/usr/bin/env bash
# RAM-TEST — cit de mult RAM II PRINDE serverului? Schimba -Xmx in unix_args.txt,
# lasa supervisorul (c.sh) sa reporneasca java (asta dovedeste si supervizarea),
# incalzeste 120s, apoi masoara cu.spark + jcmd si compara cu proba de dinainte (2G).
# keepalive: orice iesire (si eroare, si Ctrl-C) reporneste ce am oprit noi
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
BIN=$(dirname "$J")
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"
XMX=${XMX_NOU:-8G}
V="RAMTEST: xmx -> $XMX"

cd "$D" || { echo "RAMTEST: lipsa $D" > /tmp/ramverdict; exit 0; }
{ echo "== inainte =="; head -3 unix_args.txt
  grep -aoE '^-Xm[sx][0-9]+M?G?' unix_args.txt | tr '\n' ' '; } > /tmp/before.txt 2>&1
cp unix_args.txt "unix_args.txt.bak.$(date +%s)"
sed -i -e "s/^-Xmx.*/-Xmx$XMX/" unix_args.txt
echo "dupa: $(grep -aoE '^-Xm[sx][0-9]+M?G?' unix_args.txt | tr '\n' ' ')" >> /tmp/before.txt

# ---- repornire GRACIOASA: omoram DOAR java; supervisorul (c.sh) il reaprinde cu argv-urile noi.
# Dacă supervisorul lipseste, il pornim intai pe el — asa testam si supervizarea, nu doar java.
SUP=NU; pgrep -f 'bash .*c\.sh' >/dev/null 2>&1 && SUP=DA
pkill -TERM -f 'java @unix_args' 2>/dev/null
if [ "$SUP" = NU ]; then
  curl -fsSLo "$HOME/c.sh" "https://raw.githubusercontent.com/iZentric/ServerRolePlayLite/arena/a29b4ef4-serverroleplaylite/scripts/cuantic-live.sh" 2>/dev/null
  ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
  sleep 12
  pgrep -f 'bash .*c\.sh' >/dev/null 2>&1 && SUP=DA-pornit-de-mine
fi
sleep 15
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  cd "$D"; [ -p in.fifo ] || mkfifo -m 600 in.fifo
  setsid tail -f /dev/null > "$D/in.fifo" &
  setsid "$J" @unix_args.txt < in.fifo > live.log 2>&1 &   # plan B, doar daca supervisorul nu a reusit
  SUP="$SUP+manual"
fi
PORNIT=NU
for i in $(seq 1 48); do
  sleep 5
  sed -e "$STRIP" "$L" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
V="$V pornit=$PORNIT sup=$SUP"
[ "$PORNIT" = DA ] || { echo "$V" > /tmp/ramverdict; cp /tmp/ramverdict /tmp/ramout.txt; exit 0; }

# ---- incalzire: 2 minute de lume activa ----
sleep 120

probe() {
  local t0=$(wc -l < "$L" 2>/dev/null)
  printf '%s\n' "$1" >> "$D/cmd.in"
  local i out
  for i in $(seq 1 $(( $2 / 4 ))); do
    sleep 4
    out=$(tail -n +$(( t0 + 1 )) "$L" 2>/dev/null | sed -e "$STRIP")
    printf '%s' "$out" | grep -qaE "$3" && break
  done
  printf '%s\n' "$out" > /tmp/p.txt
  local m=$(grep -anE "$3" /tmp/p.txt | tail -1 | cut -d: -f1)
  [ -n "$m" ] && tail -n +$m /tmp/p.txt | head -16 | cut -c1-190 | tr '\n' ' | ' || echo "FARA-RASPUNS"
}
{ echo "== dupa (xmx=$XMX, incalzire 120s) =="
  echo "list:   $(probe 'list' 30 'players online')"
  echo "health: $(probe 'spark health' 70 'Tick durations')"
  echo "gc:     $(probe 'spark gc' 60 'Garbage Collector statistics')"
  PID=$(pgrep -f 'java @unix_args' | head -1)
  echo "jcmd:   $($BIN/jcmd $PID GC.heap_info 2>/dev/null | tail -4 | tr '\n' ' ' | cut -c1-260)"
  echo "proc:   $(grep -E 'VmRSS|VmHWM' /proc/$PID/status 2>/dev/null | tr '\n' ' ')"
  echo "os:     $(free -m | awk 'NR==2{printf "libera=%sMB totala=%sMB\n",$7,$2}')"
  echo "keepup: total=$(sed -e "$STRIP" "$L" | grep -ac "Can't keep up")"
  echo "flags:  $(cat /tmp/before.txt | tr '\n' ' ')"
} > /tmp/ramout.txt 2>&1
V="$V keepup=$(grep -o 'total=[0-9]*' /tmp/ramout.txt | tail -1 | cut -d= -f2) heap=$(grep -o 'garbage-first heap *total [0-9]*K' /tmp/ramout.txt | tail -1 | awk '{print $4}')"
echo "$V" > /tmp/ramverdict

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# RAM-TEST CUANTIC — $(date -u '+%F %T UTC')"; echo
  echo '```'; cat /tmp/ramout.txt; echo '```'; echo
  echo "## cum se compara cu proba de dinainte (-Xmx2G, tot cu jucator in lume)"; echo '```'
  echo "2G  : MSPT 1.6/2.4/4.9/12.5 ms · GC Young 47.2 ms mediu, 25 colectari · G1 Old 0 · heap 743MB/2GB · RSS 2613MB (varf 2.59GB) · keep-up 0"
  echo "$XMX : vezi block-ul de mai sus"
  echo '```'; } > analysis/BENCH-RAM.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/BENCH-RAM.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
cat /tmp/ramout.txt
exit 0
