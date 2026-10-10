#!/usr/bin/env bash
# OP — il face pe proprietar operator, fara sa tasteze el ceva in consola serverului.
# 1) afla numele de jucator din live.log  2) trimite "op NUME" in consola prin cmd.in (puntea vie)
# 3) scrie ops.json cu UUID-ul offline (sa supravietuiasca restart-ului)
# 4) verdictul in MESAJUL commitului (logurile runnerului self-hosted nu se vad).
# keepalive: orice iesire (si eroare, si Ctrl-C) reporneste ce am oprit noi
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
V="OP: inca nu stiu"

# ---- 1. numele lui, extras din log (ANSI curatat; mai intai UUID-ul vanilie, apoi join/lost) ----
CLEAN=$(sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\r/\n/g' "$L" 2>/dev/null)
# numele: deploy/op-name (conventiarepozitoriului); deploy/op.txt ramane doar butonul de declansare
for F in "$GITHUB_WORKSPACE/deploy/op-name" deploy/op-name; do
  [ -s "$F" ] && NUME_TAU=$(head -1 "$F" | tr -d ' \r') && break
done
N=${NUME_TAU:-}
if [ -z "$N" ]; then
  N=$(printf '%s\n' "$CLEAN" | grep -aoE 'UUID of player [A-Za-z0-9_]{3,16}' | tail -1 | awk '{print $4}')
fi
if [ -z "$N" ]; then
  N=$(printf '%s\n' "$CLEAN" | grep -aoE '[A-Za-z0-9_]{3,16} (joined the game|lost connection)' \
     | awk '{print $1}' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
fi
case "$N" in Server|minecraft|FML|thread|INFO|WARN|Done|Stopping|Unknown|Disconnecting) N="" ;; esac
DOVEZI=$(printf '%s\n' "$CLEAN" | grep -aE 'joined the game|lost connection|UUID of player|is now a server operator|players online' | tail -3 | cut -c1-110 | tr '\n' '|')
V="OP: nume=${N:-NICIUNUL-in-log}"

# ---- 2. serverul in picioare? (il pornim DOAR dac nobody altcineva il supravegheaza) ----
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  if pgrep -f 'c\.sh|cuantic-live' >/dev/null 2>&1; then
    echo "java jos, dar supervisorul lui c.sh e viu -> il las pe el sa-l porneasca"; sleep 60
  else
    echo "java: JOS -> il pornesc eu"
    cd "$D" || true
    [ -p in.fifo ] || mkfifo -m 600 in.fifo
    setsid tail -f /dev/null > "$D/in.fifo" &
    setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 > "$D/live.log" 2>&1 &
    sleep 90
  fi
fi
if pgrep -f 'java @unix_args' >/dev/null 2>&1; then V="$V java=SUS"; else V="$V java=JOS"; fi
ss -lnt 2>/dev/null | grep -q ':25565' && V="$V port=ASCULTA" || V="$V port=NU"

# ---- 3. consola prin punte ----
CONS=NU
# --- ops.json direct (fara consola, nu depinde de punte): singura cale care functioneaza si
#     cand serverul are consola moarta. Serverul il citeste la pornire; /reload il reciteste.
if [ -n "$N" ]; then
  echo "ops.json direct pentru $N"   # marcaj pentru verificare
  python3 - "$D/ops.json" "$N" <<'PYP'
import json, sys, os, uuid
f, nume = sys.argv[1], sys.argv[2]
d = []
if os.path.isfile(f):
    try: d = json.load(open(f, encoding="utf-8"))
    except Exception: d = []
if not isinstance(d, list): d = []
if not any(str(x.get("Name", "")).lower() == nume.lower() for x in d if isinstance(x, dict)):
    d.append({"uuid": str(uuid.uuid5(uuid.NAMESPACE_DNS, "Player_" + nume)), "name": nume,
              "Level": 4, "bypassesPlayerLimit": False})
json.dump(d, open(f, "w", encoding="utf-8"), indent=2)
print("ops.json scris:", [x.get("name") for x in d])
PYP
  echo "ops.json direct" # marcaj
fi

if [ -n "$N" ] && [ -w "$D/cmd.in" ]; then
  printf 'op %s\nlist\n' "$N" > "$D/cmd.in"
  for i in 1 2 3 4 5 6 7 8; do
    sleep 3
    if grep -aqE "$N (is now a server operator|has been made a server operator)|Opped $N|Added $N" "$L" 2>/dev/null; then CONS=DA; break; fi
  done
fi
V="$V consola=$CONS"

# ---- 3.5 consola moarta? atunci restart controlat: SIGTERM = oprire gracioasa (salveaza lumea),
#      serverul citeste ops.json la pornire => OP-ul devine live.
if [ "$CONS" != DA ] && [ -n "$N" ]; then
  RAMAS=$(cat "$D/cmd.in" 2>/dev/null | tr '\n' ' ' | cut -c1-60)
  V="$V cmd.in_neconsumat=[${RAMAS:-gol}]"
  echo "> op $N" >> "$D/op-live.sql" 2>/dev/null
  pkill -TERM -f 'java @unix_args' 2>/dev/null; sleep 22
  pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 8; }
  cd "$D" || true
  [ -p in.fifo ] || mkfifo -m 600 in.fifo
  setsid tail -f /dev/null > "$D/in.fifo" &
  setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 > "$D/live.log" 2>&1 &
  for i in $(seq 1 40); do
    sleep 5
    sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$D/live.log" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)|For voicechat binding' && break
  done
  V="$V restart=PORNIT"
fi

# ---- 5. verdict in commit ----
cd "$GITHUB_WORKSPACE" 2>/dev/null || cd "$D"
mkdir -p analysis
{ echo "op sh -- $(date -u '+%F %T UTC')"; echo "$V"; echo "DOVEZI: $DOVEZI"; echo "live.log final: $(tail -4 "$L" 2>/dev/null | tr '\n' ' ' | cut -c1-260)"; } > analysis/op.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/op.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
echo "$V"
exit 0
