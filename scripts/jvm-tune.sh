#!/usr/bin/env bash
# JVM-TUNE — a treia brate a experimentului: RAM-ul mare a iesit MAI PROST la pauze GC
# (probe: -Xmx8G => 111.38 ms media unei pauze vs 47.2 ms la 2G, RSS +0.75GB).
# Deci castigul real nu e "toata memoria", ci setul complet de flaguri GC, VALIDAT pe Java 17
# (kit-ul din build e validat pe Java 11 — cateva flaguri nu mai exista in 17, le elimina singur scriptul).
# keepalive: orice iesire (si eroare, si Ctrl-C) reporneste ce am oprit noi
# PAUZAT la cererea „serverul sa fie mereu pornit": joburile astea opresc java minute intregi
# (ram-test/jvm-tune cautaplafone, brand/no-login repornesc). Scoate randurile urmatoare ca sa le
# rulezi din nou:
case "${CUANTIC_FORTEAZA:-}" in ""|0) echo "PAUZAT deliberate (nu pun serverul jos pentru un test neesential). CUANTIC_FORTEAZA=1 forteaza." >&2; exit 0;; esac
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
BIN=$(dirname "$J")
STRIP="s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g; s/\r/\n/g"
HEAP=${HEAP_TINTA:-2G}
V="JVMTUNE: heap=$HEAP"
cd "$D" || { echo "JVMTUNE: lipsa $D" > /tmp/tuneverdict; exit 0; }

# ---- 1. candidatul: setul forjat in build (AIKAR_FLAGS din build_lite.py) ----
python3 - > /tmp/flags.txt <<'PY'
import re, os
p = os.path.join(os.environ.get("GITHUB_WORKSPACE", "."), "scripts", "build_lite.py")
s = open(p, encoding="utf-8", errors="replace").read()
m = re.search(r"AIKAR_FLAGS = \((.*?)\n\)", s, re.S)
blob = eval("(" + m.group(1) + ")")
print(blob)
PY
FLAGI=$(cat /tmp/flags.txt)

# ---- 2. curatare automata: Java 17 refuza flaguri postate in 11 -> le scoatem pe rand ----
ARUNCAT=""
# succesul se judeca la codul de iesire (-version scrie intotdeauna pe stderr, deci stderr-ul
# nu e dovada esecului - doar cand java refuza argv-urile dam de "Unrecognized VM option")
for i in $(seq 1 40); do
  if "$J" $FLAGI -version >/dev/null 2>/tmp/jvm.err; then break; fi
  ERR=$(cat /tmp/jvm.err 2>/dev/null)
  BAD=$(printf '%s' "$ERR" | grep -aoE "Unrecognized VM option '[^']+'" | head -1 | sed "s/.*'\([^']*\)'.*/\1/" | cut -d= -f1)
  [ -z "$BAD" ] && BAD=$(printf '%s' "$ERR" | grep -aoE "Cannot specify VM option '[^']+'" | head -1 | sed "s/.*'\([^']*\)'.*/\1/" | cut -d= -f1)
  [ -z "$BAD" ] && BAD=$(printf '%s' "$ERR" | grep -aoE "VM option '[^']+' is experimental" | head -1 | sed "s/.*'\([^']*\)'.*/\1/" | cut -d= -f1)
  if [ -z "$BAD" ]; then echo "eroare negasita de curator:"; printf '%s\n' "$ERR" | head -4; FLAGI=""; break; fi
  ARUNCAT="$ARUNCAT $BAD"
  FLAGI=$(printf '%s\n' "$FLAGI" | tr ' ' '\n' | grep -v -x -- "-XX:[+-]*${BAD}" | grep -v -x -- "-XX:${BAD}=.*" | tr '\n' ' ')
done
V="$V aruncat=$(echo $ARUNCAT | wc -w)"

if [ -z "$FLAGI" ]; then
  echo "JVMTUNE: candidat respins de Java 17, ramane ce a fost" > /tmp/tuneverdict
  cp /tmp/tuneverdict /tmp/tuneout.txt
  cd "$GITHUB_WORKSPACE" 2>/dev/null || true
  { echo "# esec candidat — $(date -u '+%F %T UTC')"; cat /tmp/jvm.err 2>/dev/null; } > analysis/JVM-TUNE.md
  git config user.name "cuantic-bot"; git commit -q -am "jvm-tune: candidat respins" 2>/dev/null || true
  git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" 2>/dev/null || true
  git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" 2>/dev/null || true
  exit 0
fi
mkdir -p "$GITHUB_WORKSPACE/deploy" 2>/dev/null
printf '%s\n' $FLAGI > "$GITHUB_WORKSPACE/deploy/jvm-flags-17.txt" 2>/dev/null || true
{ echo "## flaguri acceptate de Java 17 ($(printf '%s\n' $FLAGI | wc -l))"; printf '%s\n' $FLAGI | sed 's/^/  /'
  echo "## aruncate (nu mai exista in 17):$ARUNCAT"; } > /tmp/flagreport.txt

# ---- 3. aplica (cu backup) ----
cp unix_args.txt "unix_args.txt.bak.$(date +%s)"
# PAZA: unix_args.txt trebuie sa pastreze coada `-jar <server.jar> nogui`, altfel java nu are
# main-class si moare instant ( supervisorul o reporneste la nesfarsit).
TAIL=$(awk '/^-jar$/{f=1} f' unix_args.txt)
{ echo "-Xms1G"; echo "-Xmx$HEAP"; printf '%s\n' $FLAGI; [ -n "$TAIL" ] && printf '%s\n' "$TAIL"; } > unix_args.txt
bash "$HOME/cuantic-args.sh" "$D" 2>/dev/null || true
V="$V scris=DA"

# ---- 4. repornire prin supervisor ----
SUP=NU; pgrep -f 'bash .*c\.sh' >/dev/null 2>&1 && SUP=DA
pkill -TERM -f 'java @unix_args' 2>/dev/null
if [ "$SUP" = NU ]; then
  ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & ); sleep 12
  pgrep -f 'bash .*c\.sh' >/dev/null 2>&1 && SUP=DA-pornit-de-mine
fi
sleep 15
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  [ -p in.fifo ] || mkfifo -m 600 in.fifo
  setsid tail -f /dev/null > "$D/in.fifo" &
  setsid "$J" @unix_args.txt 3<>in.fifo <&3 > live.log 2>&1 &
  SUP="$SUP+manual"
fi
PORNIT=NU
for i in $(seq 1 48); do
  sleep 5
  sed -e "$STRIP" "$L" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
V="$V pornit=$PORNIT sup=$SUP"
[ "$PORNIT" = DA ] || { echo "$V" > /tmp/tuneverdict; cp /tmp/tuneverdict /tmp/tuneout.txt; exit 0; }
sleep 120   # incalzire

probe() {
  local t0=$(wc -l < "$L" 2>/dev/null); printf '%s\n' "$1" >> "$D/cmd.in"
  local i out
  for i in $(seq 1 $(( $2 / 4 ))); do
    sleep 4; out=$(tail -n +$(( t0 + 1 )) "$L" 2>/dev/null | sed -e "$STRIP")
    printf '%s' "$out" | grep -qaE "$3" && break
  done
  printf '%s\n' "$out" > /tmp/p2.txt
  local m=$(grep -anE "$3" /tmp/p2.txt | tail -1 | cut -d: -f1)
  [ -n "$m" ] && tail -n +$m /tmp/p2.txt | head -16 | cut -c1-190 | tr '\n' ' | ' || echo "FARA-RASPUNS"
}
{ echo "== brata C: heap $HEAP + set complet de flaguri GC (Java 17 validat) =="
  echo "list:   $(probe 'list' 30 'players online')"
  echo "health: $(probe 'spark health' 70 'Tick durations')"
  echo "gc:     $(probe 'spark gc' 60 'Garbage Collector statistics')"
  PID=$(pgrep -f 'java @unix_args' | head -1)
  echo "jcmd:   $($BIN/jcmd $PID GC.heap_info 2>/dev/null | tail -3 | tr '\n' ' ' | cut -c1-240)"
  echo "proc:   $(grep -E 'VmRSS|VmHWM' /proc/$PID/status 2>/dev/null | tr '\n' ' ')"
  echo "os:     $(free -m | awk 'NR==2{printf "libera=%sMB",$7}')"
  echo "keepup: total=$(sed -e "$STRIP" "$L" | grep -ac "Can't keep up")"
  echo; cat /tmp/flagreport.txt
  echo "## brate anterior, aceeasi masina, acelasi jucator"
  echo "  A) -Xmx2G, 3 flaguri              : MSPT 1.6/2.4/4.9/12.5 ms · GC 47.2 ms mediu/25 · Old 0 · heap 743MB/2G · RSS 2613MB · keep-up 0"
  echo "  B) -Xmx8G, 3 flaguri (toata RAM-ul): MSPT 1.2/1.6/9.1/29.5 · GC 111.38 ms mediu/8 · Old 0 · heap 1.2G/8G · RSS 3366MB · keep-up 0"
} > /tmp/tuneout.txt 2>&1
RSS=$(grep -o 'VmHWM:\s*[0-9]*' /tmp/tuneout.txt | grep -o '[0-9]*' | head -1)
NF=$(printf "%s\n" $FLAGI | grep -c . )
V="$V flaguri=$NF keepup=$(grep -o 'total=[0-9]*' /tmp/tuneout.txt | tail -1 | cut -d= -f2) hwm=${RSS}KB"
echo "$V" > /tmp/tuneverdict

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "# JVM-TUNE CUANTIC — $(date -u '+%F %T UTC')"; echo; echo '```'; cat /tmp/tuneout.txt; echo '```'; } > analysis/JVM-TUNE.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/JVM-TUNE.md deploy/jvm-flags-17.txt >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
cat /tmp/tuneout.txt
exit 0
