#!/usr/bin/env bash
# GC-DUEL — masoara collectorii de gunoi pe serverul LIVE, pe aceeasi masina, si lasa cifrele
# in analysis/GC-DUEL.md. NU alege el nimic si NU lasa nimic schimbat: restabileste
# unix_args.txt din backupul facut la inceput, chiar daca o axa crapa.
D=$HOME/cuantic-live
cd "$D" 2>/dev/null || { echo "DUEL: lipsa $D" > /tmp/gcduel.txt; exit 0; }
BK="$D/unix_args.txt.duel.bak"
cp unix_args.txt "$BK"
AXE=${DUEL_AXE:-A B C}
pune() { python3 - "$1" <<'PY'
import sys, re
gc = sys.argv[1].split()
p = "unix_args.txt"
linii = [l.strip() for l in open(p, encoding="utf-8", errors="replace") if l.strip()]
cap = [l for l in linii if re.match(r"^-Xm[sx]", l)]
jar = [l for l in linii if l in ("-jar", "nogui") or l.endswith(".jar")]
retele = [l for l in linii if l.startswith("-XX") and not re.search(r"Use(G1GC|ShenandoahGC|ZGC|ParallelGC)|MaxGCPauseMillis|G1[A-Za-z]+|Shenandoah[A-Za-z]+|ZGenerational", l)]
open(p, "w", encoding="utf-8").write("\n".join(cap + retele + gc + jar) + "\n")
print("args:", " ".join(cap + gc), "| -jar", jar[-2] if len(jar) > 1 else "?")
PY
}
oproeste() { pkill -TERM -f 'java @unix_args' 2>/dev/null; sleep 20
  pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }; }
asteapta() { for i in $(seq 1 36); do sleep 5
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && return 0
done; return 1; }
probeaza() { local nume=$1 S=$(date +%s)
  while [ $(( $(date +%s) - S )) -lt 150 ]; do sleep 10; done
  local L=$(sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log)
  local GC=$(printf '%s' "$L" | grep -aoE 'Pause (Young|Remark|Cleanup)[^,]*, [0-9]+M->[0-9]+M\([0-9]+M\) [0-9.]+ms' | grep -aoE '[0-9.]+ms$' | tail -60 | sed 's/ms//' | awk '{s+=$1;n++;if($1>m)m=$1}END{printf "%.1f/%.1f/%d", n?s/n:0, m, n}')
  local PID=$(pgrep -f 'java @unix_args' | head -1)
  local RSS=$([ -n "$PID" ] && awk '/VmRSS/{print int($2/1024)}' /proc/$PID/status 2>/dev/null || echo 0)
  local HI=$(printf '%s' "$L" | grep -caE "Allocation Pause|Pause Initial Mark|.concurrent")
  local CK=$(printf '%s' "$L" | grep -cai "can't keep up")
  echo "$nume gc-medie-max-nr=${GC:-0/0/0} rss=${RSS}MB ancore=${HI} keepup=${CK}" >> /tmp/gcduel.raw; }
: > /tmp/gcduel.raw
for a in $AXE; do
  case $a in
    A) GC="-XX:+UseG1GC -XX:MaxGCPauseMillis=37";;
    B) GC="-XX:+UseG1GC -XX:MaxGCPauseMillis=20";;
    C) GC="-XX:+UnlockExperimentalVMOptions -XX:+UseShenandoahGC";;
    D) GC="-XX:+UnlockExperimentalVMOptions -XX:+UseZGC";;
    *) GC="";;
  esac
  echo "== AXA $a ($GC)" >> /tmp/gcduel.raw
  cp "$BK" unix_args.txt
  pune "$GC"
  oproeste
  ( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
  if asteapta; then probeaza "axa-$a"; else echo "axa-$a NU-A-POURNIT" >> /tmp/gcduel.raw; fi
done
cp "$BK" unix_args.txt
( setsid bash "$HOME/c.sh" >> "$D/sup.log" 2>&1 < /dev/null & )
for i in $(seq 1 30); do sleep 5
  sed -e "s/$(printf '\033')\[[0-9;]*[a-zA-Z]//g" live.log 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && break; done
V="# GC-DUEL CUANTIC — $(date -u '+%Y-%m-%d %H:%M:%S') UTC (150 s pe axa, server live, aceeasi masina, args restaurat din backup)"
{ echo "$V"; echo; sed 's/^/- /' /tmp/gcduel.raw; echo; echo "Stare finala: $(grep -aoE '^-XX:[+]?Use[A-Za-z]+GC' unix_args.txt | head -1) / $(grep -c . unix_args.txt) linii args"; } > /tmp/gcduel.txt
cat /tmp/gcduel.txt
