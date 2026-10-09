#!/usr/bin/env bash
# OP — il face pe proprietar operator, fara sa tasteze el ceva in consola serverului.
# 1) afla numele de jucator din live.log  2) trimite "op NUME" in consola prin cmd.in (puntea vie)
# 3) scrie ops.json cu UUID-ul offline (sa supravietuiasca restart-ului)
# 4) verdictul in MESAJUL commitului (logurile runnerului self-hosted nu se vad).
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
V="OP: inca nu stiu"

# ---- 1. numele lui, extras din log (cel mai frecvent jucator care a incercat) ----
N=${NUME_TAU:-}
if [ -z "$N" ]; then
  N=$(grep -haoE '\]: [A-Za-z0-9_]{3,16} (joined the game|lost connection|logged in|logged in with)|Disconnecting [A-Za-z0-9_]{3,16}' "$L" 2>/dev/null \
      | sed -E 's/.*\]: ([A-Za-z0-9_]{3,16}).*/\1/; s/Disconnecting //' \
      | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
fi
case "$N" in Server|minecraft|FML|thread|INFO|WARN|Done|Stopping|Can't|Unknown) N="" ;; esac
V="$V nume=${N:-NICIUNUL-in-log}"

# ---- 2. serverul in picioare? (il pornim DOAR dac nobody altcineva il supravegheaza) ----
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  if pgrep -f 'c\.sh|cuantic-live' >/dev/null 2>&1; then
    echo "java jos, dar supervisorul lui c.sh e viu -> il las pe el sa-l porneasca"; sleep 60
  else
    echo "java: JOS -> il pornesc eu"
    cd "$D" || true
    [ -p in.fifo ] || mkfifo -m 600 in.fifo
    setsid tail -f /dev/null > "$D/in.fifo" &
    setsid "$J" @unix_args.txt < "$D/in.fifo" > "$D/live.log" 2>&1 &
    sleep 90
  fi
fi
if pgrep -f 'java @unix_args' >/dev/null 2>&1; then V="$V java=SUS"; else V="$V java=JOS"; fi
ss -lnt 2>/dev/null | grep -q ':25565' && V="$V port=ASCULTA" || V="$V port=NU"

# ---- 3. consola prin punte ----
CONS=NU
if [ -n "$N" ] && [ -w "$D/cmd.in" ]; then
  printf 'op %s\nlist\n' "$N" > "$D/cmd.in"
  for i in 1 2 3 4 5 6 7 8; do
    sleep 3
    if grep -aqE "$N (is now a server operator|has been made a server operator)|Opped $N|Added $N" "$L" 2>/dev/null; then CONS=DA; break; fi
  done
fi
V="$V consola=$CONS"

# ---- 4. ops.json (UUID offline = algoritmul Java nameUUIDFromBytes) ----
if [ -n "$N" ]; then
  P="$N" D="$D" python3 - <<'PY'
import hashlib, json, os, uuid
name, d = os.environ["P"], os.environ["D"]
b = bytearray(hashlib.md5(("OfflinePlayer:" + name).encode("utf-8")).digest())
b[6] = (b[6] & 0x0F) | 0x30          # versiune 3
b[8] = (b[8] & 0x3F) | 0x80          # variant IETF
u = str(uuid.UUID(bytes=bytes(b)))
p = os.path.join(d, "ops.json")
try:
    cur = json.load(open(p))
    if not isinstance(cur, list):
        cur = []
except Exception:
    cur = []
cur = [x for x in cur if (x.get("name") or "").lower() != name.lower()]
cur.append({"uuid": u, "name": name, "level": 4, "bypassesPlayerLimit": False})
json.dump(cur, open(p, "w"), indent=2)
print("ops.json:", name, u)
PY
  V="$V ops.json=SCRIS"
fi

# ---- 5. verdict in commit ----
cd "$GITHUB_WORKSPACE" 2>/dev/null || cd "$D"
mkdir -p analysis
{ echo "op sh -- $(date -u '+%F %T UTC')"; echo "$V"; echo "live.log final: $(tail -4 "$L" 2>/dev/null | tr '\n' ' ' | cut -c1-300)"; } > analysis/op.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/op.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
echo "$V"
exit 0
