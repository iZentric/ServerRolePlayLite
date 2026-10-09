#!/usr/bin/env bash
# CUANTIC LIVE pe gazda runner-ului (Cloud Shell / VM Oracle, 11GB).
# Punem jarul 1.5.8 auditat in ~/, pornim DETASAT (sa traiasca dupa job),
# testam intrarea din exterior si, daca portul e blocat, ridicam un tunnel TCP.
LOG=/tmp/live.txt
: > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
IP=$(curl -fsS --max-time 10 https://ifconfig.me 2>/dev/null || echo 132.145.236.16)
say "== CUANTIC LIVE — $(date -u '+%F %T UTC') =="
say "gazda: $(uname -m) | java: $(java -version 2>&1 | head -1) | ip public (egress): $IP"
say "memorie: $(free -m | sed -n 2p)"
say "disc: $(df -h / | sed -n 2p)"

# ---------- 1. pack ----------
mkdir -p $DIR && cd $DIR
URL=$(curl -fsS --max-time 20 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite 2>/dev/null | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
if [ -z "$URL" ]; then URL=$(curl -fsS --max-time 20 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite 2>/dev/null | grep -o '"browser_download_url": *"[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/'); fi
say "asset pack: ${URL:-NICIUNUL}"
if [ -n "$URL" ] && { [ ! -f .last-url ] || [ "$(cat .last-url)" != "$URL" ]; }; then
  say "descarc pack..."
  curl -fsSL --retry 2 -o pack.zip "$URL" && unzip -qo pack.zip && echo "$URL" > .last-url && say "pack descarcat ($(du -sh . | cut -f1))"
fi
JAR=$(ls *.jar 2>/dev/null | grep -viE 'unix|paperclip' | head -1)
[ -z "$JAR" ] && JAR=$(ls *.jar 2>/dev/null | head -1)
say "jar: ${JAR:-NIMIC}"
ls -la | head -20 | sed 's/^/  /' >> $LOG

# ---------- 2. server.properties (cracked + limitari) ----------
touch server.properties
setp(){ k=$1 v=$2; if grep -q "^$k=" server.properties; then sed -i "s|^$k=.*|$k=$v|" server.properties; else echo "$k=$v" >> server.properties; fi; }
setp online-mode false
setp server-port 25565
setp server-ip 0.0.0.0
setp motd CUANTIC_RP_Live
setp max-players 40
setp view-distance 6
setp simulation-distance 5
setp player-idle-timeout 0
setp sync-chunk-writes false
setp allow-flight true
setp hardcore false
say "server.properties: $(grep -c . server.properties) linii, online-mode=$(grep '^online-mode' server.properties)"

# ---------- 3. heap in unix_args (gasda are 11GB, nu 1GB) ----------
if [ -f unix_args.txt ]; then
  head -2 unix_args.txt | sed 's/^/  inainte: /' >> $LOG
  sed -i "1s/.*/-Xms1G/;2s/.*/-Xmx4G/" unix_args.txt
  say "args: $(head -2 unix_args.txt | tr '\n' ' ')"
else
  ARGS="-Xms1G -Xmx4G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1"
  say "fara unix_args, folosesc args simpli"
fi

# ---------- 4. pornire detasata ----------
pkill -f 'cuantic-live/unix_args' 2>/dev/null; pkill -f 'Xmx4G.*'"$DIR" 2>/dev/null
sleep 2
cd $DIR
if [ -f unix_args.txt ]; then
  setsid nohup java -Xms1G -Xmx4G @unix_args.txt < /dev/null > live.log 2>&1 &
else
  setsid nohup java $ARGS nogui < /dev/null > live.log 2>&1 &
fi
PID=$!
say "pid $PID (detasat prin setsid)"
echo $PID > $DIR/live.pid

# inima care supravietuiese si ne arata ca masina e vie intre joburi
pgrep -f 'heartbeat.sh' >/dev/null || { printf '#!/usr/bin/env bash\nwhile :; do date -u "+%%FT%%TZ" >> %s/heartbeat.txt; sleep 300; done\n' "$DIR" > $HOME/heartbeat.sh; setsid nohup bash $HOME/heartbeat.sh </dev/null >/dev/null 2>&1 & say "heartbeat pornit"; }

# ---------- 5. boot ----------
DONE=""
for i in $(seq 1 60); do
  DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' live.log 2>/dev/null)
  [ -n "$DONE" ] && break
  sleep 3
done
say "boot: ${DONE:-NU ÎN 180s}"
ERRN=$(grep -c ERROR live.log 2>/dev/null)
say "linii ERROR: $ERRN"
tail -6 live.log | sed 's/^/  /' >> $LOG

# ---------- 6. asculta local? ----------
LISTEN=NU
(timeout 4 bash -c "</dev/tcp/127.0.0.1/25565" 2>/dev/null) && LISTEN=DA
say "port 25565 pe 127.0.0.1: $LISTEN"

EXT=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$IP:25565" 2>/dev/null | tr -d '\n ')
say "probe exterior $IP:25565 -> $EXT"

ADDR=""
case "$EXT" in *'"online":true'*) ADDR="$IP:25565"; say "DIRECT FUNCTIONEAZA";; esac

# ---------- 7. tunnel daca IP-ul public nu intra ----------
if [ -z "$ADDR" ]; then
  say "IP-ul public nu accepta 25565 (Cloud Shell = doar iesire) -> tunnel TCP"
  pkill -f 'ssh.localhost.run' 2>/dev/null; sleep 1
  for P in 22 443; do
    setsid nohup ssh -p $P -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes \
      -R 80:localhost:25565 nokey@ssh.localhost.run < /dev/null > $DIR/tunnel.log 2>&1 &
    sleep 12
    TL=$(grep -oE '[a-z0-9-]+\.([a-z0-9-]+\.)?localhost\.run:[0-9]+' $DIR/tunnel.log | head -1)
    [ -z "$TL" ] && TL=$(grep -oE 'tcp://[^ ]+' $DIR/tunnel.log | head -1 | sed 's|tcp://||')
    if [ -n "$TL" ]; then
      say "tunnel pe port $P: $TL"
      say "tunnel.log: $(tail -4 $DIR/tunnel.log | tr '\n' ' ')"
      T2=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/$TL" 2>/dev/null | tr -d '\n ')
      say "probe tunnel -> $T2"
      case "$T2" in *'"online":true'*) ADDR=$TL;; *) ADDR=$TL;; esac
      break
    else
      say "tunnel esuat pe $P: $(tail -2 $DIR/tunnel.log | tr '\n' ' ')"
    fi
  done
fi

[ -z "$ADDR" ] && ADDR=$(sed -n 's/^Adresa de joc: //p' $DIR/ADRESA 2>/dev/null)
say "==> ADRESA DE JOC: ${ADDR:-NU AM REUSAT}"
echo "Adresa de joc: ${ADDR:-NIMIC}" > $DIR/ADRESA
echo "$ADDR" > /tmp/live-addr.txt
say "ramasi pe loc: $(pgrep -fc 'java') java, uptime $(uptime | sed 's/^ *//')"
say "GATA"
exit 0
