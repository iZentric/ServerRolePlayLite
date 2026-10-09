#!/usr/bin/env bash
# CUANTIC LIVE v3. Fixuri: stdin printr-o teava vesnica (fara EOF = serverul NU se mai opreste),
# probe externe in timp ce serverul asculta, si clarificare retea (IP public pe NIC vs NAT).
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live; cd $DIR || exit 1
J17=$(ls /usr/lib/jvm/java-17-*/bin/java $HOME/jdk17/bin/java 2>/dev/null | head -1)
say "== CUANTIC LIVE v3 — $(date -u '+%F %T UTC') =="
say "java17: ${J17:-NIMIC}"

# ---------- RETEA: e IP-ul public chiar pe NIC? ----------
say "--- interfete:"
ip -4 -o addr show 2>/dev/null | sed 's/^/  /' >> $LOG
EGRESS=$(curl -fsS --max-time 12 https://ifconfig.me 2>/dev/null)
NICPUB=$(ip -4 -o addr show 2>/dev/null | awk '$4 !~ /^(10\.|127\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)/ {print $4}' | cut -d/ -f1 | head -1)
say "egress (asa ne vad internetul): ${EGRESS:-?} | IP public pe NIC: ${NICPUB:-NICIUNUL (deci NAT/cloud-shell)}"
[ -n "$EGRESS" ] && { case "$EGRESS" in 10.*|192.168.*) MODE=NAT;; *) MODE=PUBLIC-POSIBILE;; esac; }
say "mod retea estimat: ${MODE:-NISTI}"

# ---------- opre ce era ----------
pkill -f 'unix_args.txt' 2>/dev/null; sleep 2
echo "eula=true" > eula.txt

# ---------- pornire: fifo tinut deschis read-write (niciodata EOF = serverul traieste) ----------
mkfifo cin 2>/dev/null || true
setsid nohup bash -c 'exec 9<> '"$DIR"'/cin; while :; do sleep 600; done' < /dev/null > /dev/null 2>&1 &
sleep 1
setsid nohup "$J17" @unix_args.txt < "$DIR/cin" > live.log 2>&1 &
sleep 3
say "java pornit, procese: $(pgrep -fc java)"

DONE=""
for i in $(seq 1 70); do
  DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3
done
say "boot: ${DONE:-NU in 210s} | ERROR: $(grep -c ' ERROR ' live.log)"

# ---------- asculta? ----------
L=NU
python3 - <<EOF >> $LOG 2>&1 && L=DA
import socket
s=socket.socket(); s.settimeout(4)
s.connect(("127.0.0.1",25565)); s.close()
print("  connect local pe 25565: OK")
EOF
say "asculta local 25565: $L"
say "bind:"; (ss -lntp 2>/dev/null | grep 25565 || netstat -lnt 2>/dev/null | grep 25565) | sed 's/^/  /' >> $LOG

# ---------- probe din exterior, cu serverul SUS ----------
say "tin serverul 45s la dispozitia probei..."
for i in $(seq 1 15); do
  [ -n "$V" ] && break
  sleep 3
  A=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/$EGRESS:25565" 2>/dev/null)
  B=$(curl -fsS --max-time 20 "https://api.mcstatus.io/v2/status/java/$EGRESS:25565" 2>/dev/null)
  C=""; [ -n "$NICPUB" ] && [ "$NICPUB" != "$EGRESS" ] && C=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/$NICPUB:25565" 2>/dev/null)
  case "$A$B$C" in *'"online":true'*|*'"online": true'*) V=DA;; esac
  say "  incercare $i: mcsrvstat=$(echo "$A" | grep -oE '\"online\":[a-z]+') mcstatus=$(echo "$B" | grep -oE '\"online\":[a-z]+')$( [ -n "$C" ] && echo " nicip=$(echo "$C" | grep -oE '\"online\":[a-z]+')" )"
done
if [ "$V" = "DA" ]; then
  say "==> REZULTAT: serverul e ACCESIBIL din internet pe ${EGRESS}:25565"
  ADDR="$EGRESS:25565"
else
  say "==> REZULTAT: portul NU e deschis din exterior (gazda = Cloud Shell/VM cu retea doar de iesire sau securitate nepermisiva)."
  ADDR="NU"
fi

# ---------- relay (doar daca n-avem intrare directa) ----------
if [ "$ADDR" = "NU" ]; then
  PURL=https://github.com/playit-cloud/playit-agent/releases/download/v1.0.10/playit-cli-linux-aarch64
  [ -x $HOME/playit ] || { curl -fsSL --retry 2 -o $HOME/playit "$PURL" && chmod +x $HOME/playit; }
  if [ -x $HOME/playit ]; then
    setsid nohup $HOME/playit < /dev/null > $DIR/playit.log 2>&1 &
    sleep 25; say "playit (iesire bruta):"; tail -25 $DIR/playit.log | sed 's/^/  /' >> $LOG
    CL=$(grep -oE 'https://playit\.gg/[A-Za-z0-9/_.-]*claim[A-Za-z0-9/_.-]*' $DIR/playit.log | head -1)
    PT=$(grep -oE 'playit\.gg:[0-9]+' $DIR/playit.log | tail -1)
    [ -n "$CL" ] && say "link de claim (deschide-l, apoi relayul e al tau): $CL"
    [ -n "$PT" ] && ADDR="$PT" && say "relay: $ADDR"
  fi
fi

say "server in viata acum: $(pgrep -f unix_args.txt >/dev/null && echo DA || echo NU)"
say "==> ADRESA: ${ADDR:-NU}"
echo "Adresa de joc: $ADDR" > $DIR/ADRESA
[ -n "$CL" ] && echo "Claim playit: $CL" >> $DIR/ADRESA
say "GATA"; exit 0
