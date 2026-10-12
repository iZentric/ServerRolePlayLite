#!/usr/bin/env bash
# OP — il face pe proprietar operator, fara sa tasteze el ceva in consola serverului.
# 1) ia numele din deploy/op-name (sau din live.log)
# 2) scrie ops.json cu UUID-ul real OfflinePlayer MD5 v3 din Minecraft 1.16.5
# 3) trimite "op NUME" si "lp user NUME permission set * true" prin in.fifo + cmd.in
# 4) NU omoara niciodata un server care merge (inainte facea pkill java si se batea cu c.sh!).
trap 'bash "$(dirname "$0")/ensure-up.sh" >/dev/null 2>&1 || true' EXIT INT TERM
D=$HOME/cuantic-live
L=$D/live.log
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
V="OP: inca nu stiu"

# ---- 1. numele lui ----
CLEAN=$(sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\r/\n/g' "$L" 2>/dev/null)
for F in "$GITHUB_WORKSPACE/deploy/op-name" deploy/op-name; do
  [ -s "$F" ] && NUME_TAU=$(head -1 "$F" | tr -d ' \r') && break
done
N=${NUME_TAU:-iZentric}
DOVEZI=$(printf '%s\n' "$CLEAN" | grep -aE 'joined the game|lost connection|UUID of player|is now a server operator|players online' | tail -3 | cut -c1-110 | tr '\n' '|')
V="OP: nume=$N"

# ---- 2. ops.json scris direct cu UUID-ul real OfflinePlayer:<N> (MD5 UUID v3 din MC 1.16.5) ----
OPS_OK=NU
if [ -n "$N" ]; then
  mkdir -p "$D"
  python3 - "$D/ops.json" "$N" <<'PYP' && OPS_OK=DA
import hashlib, json, os, sys, uuid

def mc_offline_uuid(name: str) -> str:
    b = bytearray(hashlib.md5(("OfflinePlayer:" + name).encode("utf-8")).digest())
    b[6] = (b[6] & 0x0f) | 0x30
    b[8] = (b[8] & 0x3f) | 0x80
    return str(uuid.UUID(bytes=bytes(b)))

f, nume = sys.argv[1], sys.argv[2]
d = []
if os.path.isfile(f):
    try: d = json.load(open(f, encoding="utf-8"))
    except Exception: d = []
if not isinstance(d, list): d = []
# Scoatem intrarile vechi cu UUID gresit pt acelasi nume si punem UUID-ul real OfflinePlayer
d = [x for x in d if isinstance(x, dict) and str(x.get("name", x.get("Name", ""))).lower() != nume.lower()]
u_exact = mc_offline_uuid(nume)
d.append({"uuid": u_exact, "name": nume, "level": 4, "bypassesPlayerLimit": True})
json.dump(d, open(f, "w", encoding="utf-8"), indent=2)
print("ops.json scris:", u_exact, nume)
PYP
fi
V="$V OPS=$OPS_OK"

# ---- 3. serverul in picioare? ----
if ! pgrep -f 'java @unix_args' >/dev/null 2>&1; then
  if pgrep -f 'c\.sh|cuantic-live' >/dev/null 2>&1; then
    sleep 45
  else
    cd "$D" || true
    [ -p in.fifo ] || mkfifo -m 600 in.fifo
    setsid "$J" @unix_args.txt 3<>"$D/in.fifo" <&3 >> "$D/live.log" 2>&1 < /dev/null &
    sleep 60
  fi
fi
if pgrep -f 'java @unix_args' >/dev/null 2>&1; then V="$V java=SUS"; else V="$V java=JOS"; fi
ss -lnt 2>/dev/null | grep -q ':25565' && V="$V port=ASCULTA" || V="$V port=NU"

# ---- 4. trimite si prin consola (in.fifo + cmd.in), FARA sa omoram serverul daca nu raspunde ----
CONS=NU
if [ -n "$N" ]; then
  [ -p "$D/in.fifo" ] && timeout 4 sh -c "printf 'op %s\nlp user %s permission set * true\nlist\n' '$N' '$N' > '$D/in.fifo'" 2>/dev/null || true
  [ -w "$D/cmd.in" ] && printf 'op %s\nlp user %s permission set * true\nlist\n' "$N" "$N" >> "$D/cmd.in" 2>/dev/null || true
  for i in 1 2 3 4 5; do
    sleep 2
    if grep -aqE "$N (is now a server operator|has been made a server operator)|Opped $N|Added $N|already an operator" "$L" 2>/dev/null; then CONS=DA; break; fi
  done
fi
V="$V consola=$CONS"

# ---- 5. verdict in commit ----
cd "$GITHUB_WORKSPACE" 2>/dev/null || cd "$D"
mkdir -p analysis
{ echo "op sh -- $(date -u '+%F %T UTC')"; echo "$V"; echo "ops.json: $(tr -d '\n' < "$D/ops.json" 2>/dev/null | cut -c1-200)"; echo "DOVEZI: $DOVEZI"; echo "live.log final: $(tail -4 "$L" 2>/dev/null | tr '\n' ' ' | cut -c1-260)"; } > analysis/op.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/op.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
echo "$V"
exit 0
