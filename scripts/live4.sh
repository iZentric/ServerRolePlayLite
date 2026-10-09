#!/usr/bin/env bash
# CUANTIC LIVE v4 — server + relay bore.pub (gazda noastra are iesire, nu si intrare: NIC = 10.x).
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live; cd $DIR || exit 1
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
say "== CUANTIC LIVE v4 — $(date -u '+%F %T UTC') =="

# ---------- porturi forate ----------
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo "eula=true" > eula.txt
say "server.properties: $(grep -E '^(server-ip|server-port|online-mode|max-players|view-distance)=' server.properties | tr '\n' ' ')"

# ---------- stop + start server ----------
pkill -f 'unix_args.txt' 2>/dev/null; sleep 2
{ [ -e cin ] && [ ! -p cin ] && rm -f cin; } ; mkfifo cin 2>/dev/null || true
setsid nohup bash -c 'exec 9<> '"$DIR"'/cin; while :; do sleep 600; done' </dev/null >/dev/null 2>&1 &
sleep 1
setsid nohup "$J17" @unix_args.txt < "$DIR/cin" > live.log 2>&1 &
say "java: $($J17 -version 2>&1 | head -1) | heap: $(head -2 unix_args.txt | tr '\n' ' ')"

DONE=""
for i in $(seq 1 70); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU in 210s} | ERROR: $(grep -c ' ERROR ' live.log)"
say "binding in log:"; grep -iE 'binding|bind|listen|Could not bind' live.log | tail -4 | sed 's/^/  /' >> $LOG
say "porturi deschise:"; ss -lntp 2>/dev/null | sed -n '1,12p' | sed 's/^/  /' >> $LOG

# ---------- ascultam local, cu rabdare ----------
L=NU
for i in $(seq 1 10); do
  python3 -c "import socket,sys;s=socket.socket();s.settimeout(3);s.connect(('127.0.0.1',25565));s.close()" 2>/dev/null && { L=DA; break; }
  sleep 3
done
say "asculta local 25565: $L"

# ---------- watchdog (server + relay traiesc si dupa job) ----------
cat > $HOME/cuantic-watchdog.sh <<'EOS'
#!/usr/bin/env bash
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
while :; do
  pgrep -f 'unix_args.txt' >/dev/null || {
    cd $DIR 2>/dev/null && setsid nohup "$J17" @unix_args.txt < $DIR/cin > $DIR/live.log 2>&1 &
  }
  pgrep -f "$HOME/bore " >/dev/null || {
    [ -x $HOME/bore ] && cd $DIR && setsid nohup $HOME/bore public 25565 > $DIR/bore.log 2>&1 &
  }
  sleep 25
done
EOS
pgrep -f cuantic-watchdog >/dev/null || { setsid nohup bash $HOME/cuantic-watchdog.sh </dev/null >/dev/null 2>&1 & say "watchdog pornit"; }

# ---------- relay bore.pub ----------
ADDR=""
[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/bore.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/bore.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore 2>/dev/null; chmod +x $HOME/bore; rm -f $HOME/bore.tgz; }
say "bore: $(ls -l $HOME/bore 2>/dev/null | awk '{print $5" bytes"}')"
if [ -x $HOME/bore ]; then
  pkill -f "$HOME/bore " 2>/dev/null; sleep 1
  cd $DIR && setsid nohup $HOME/bore public 25565 > $DIR/bore.log 2>&1 &
  for i in $(seq 1 8); do
    sleep 4
    A=$(grep -oE 'Remoting [a-z ]*on port: *[0-9]+' $DIR/bore.log | grep -oE '[0-9]+$' | head -1)
    [ -n "$A" ] && { ADDR="bore.pub:$A"; break; }
  done
  say "bore.log:"; tail -8 $DIR/bore.log | sed 's/^/  /' >> $LOG
fi
say "adresa relay: ${ADDR:-NIMIC}"

# ---------- probe publica ----------
for i in $(seq 1 6); do
  [ "$OK" = "DA" ] && break
  sleep 5
  R=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/${ADDR:-132.145.236.16:25565}" 2>/dev/null)
  M=$(echo "$R" | grep -oE '"online":(true|false)')
  P=$(echo "$R" | grep -oE '"players":\{"online":[0-9]+')
  say "  probe $i (${ADDR:-direct}): $M ${P}"
  case "$R" in *'"online":true'*) OK=DA;; esac
done
say "server in viata: $(pgrep -f unix_args.txt >/dev/null && echo DA || echo NU) | bore in viata: $(pgrep -f "$HOME/bore " >/dev/null && echo DA || echo NU)"
say "==> ${DONE:+SERVER PORNIT $DONE} | ADRESA DE JOC: ${ADDR:-NU}"
{ echo "Adresa de joc: ${ADDR:-NIMIC}"; echo "Server: ${DONE:-NU}"; } > $DIR/ADRESA
say "GATA"; exit 0
