#!/usr/bin/env bash
# BRAND — pune numele CUANTIC curat in lista de servere.
# Cauza reala a "Â§rÂ§bÂ§lCUANTIC": server.properties are §-uri scrise cu UTF-8, iar Java citeste
# fisierul ca Latin-1. Corect = secvente ASCII \u00A7 (build_lite.py e reparat la fel, raw string).
D=$HOME/cuantic-live
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
V="BRAND: inca nu"
cd "$D" 2>/dev/null || { echo "BRAND: lipsa $D" > /tmp/brandverdict; exit 0; }

MOTD='\u00A7b\u00A7lCUANTIC \u00A78\u00A7ov2 \u00A7f| \u00A7aRuleaza din viitor: orice PC, zero lag \u00A7f| \u00A7dOras+Survival+Claims'
cp server.properties "server.properties.bak.$(date +%s)" 2>/dev/null
grep -v '^motd=' server.properties > /tmp/sp.new || true
printf 'motd=%s\n' "$MOTD" >> /tmp/sp.new
mv /tmp/sp.new server.properties
V="BRAND: motd=$(grep -c 'u00A7' server.properties) secvente-ASCII"

# ---- restart ca sa fie citit server.properties ----
pkill -TERM -f 'java @unix_args' 2>/dev/null; sleep 20
pgrep -f 'java @unix_args' >/dev/null 2>&1 && { pkill -KILL -f 'java @unix_args'; sleep 6; }
[ -p in.fifo ] || mkfifo -m 600 in.fifo
setsid tail -f /dev/null > "$D/in.fifo" &
setsid "$J" @unix_args.txt < "$D/in.fifo" > "$D/live.log" 2>&1 &
PORNIT=NU
for i in $(seq 1 45); do
  sleep 5
  sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$D/live.log" 2>/dev/null | grep -qaE 'Done \([0-9.]+s\)' && { PORNIT=DA; break; }
done
V="$V restart=$PORNIT"
sleep 8
R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/92.5.171.150:25565" 2>/dev/null)
CLEAN=$(printf '%s' "$R" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin); print(' | '.join(d.get('motd',{}).get('clean',[]))[:120])
except Exception as e:
    print('citire esuata:', str(e)[:60])
" 2>/dev/null)
echo "$R" | grep -q '"online":true' && V="$V online=DA" || V="$V online=NU"
V="$V text='$CLEAN'"
echo "$V" > /tmp/brandverdict

mkdir -p "$GITHUB_WORKSPACE/analysis" 2>/dev/null && cd "$GITHUB_WORKSPACE"
{ echo "brand -- $(date -u '+%F %T UTC')"; echo "$V"; echo "online din exterior: $(printf '%s' "$R" | head -c 200)"; } > analysis/brand.md
git config user.name "cuantic-bot"; git config user.email "bot@cuantic.local"
git add -f analysis/brand.md >/dev/null 2>&1
git commit -q -m "$(echo "$V" | tr -d '"' | head -c 180)" || true
git pull --rebase -q origin "${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || true
git push -q origin "HEAD:${GITHUB_REF_NAME:-arena/a29b4ef4-serverroleplaylite}" || echo "push: nimic"
exit 0
