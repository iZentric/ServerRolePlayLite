#!/usr/bin/env bash
# CUANTIC LIVE v5 — supervisor detasat (NU moare la finalul job-ului) + bore.pub cu sintaxa corecta.
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
say "== CUANTIC LIVE v5 — $(date -u '+%F %T UTC') =="

cat > $HOME/cuantic-supervise.sh <<EOS
#!/usr/bin/env bash
DIR=$DIR
J17=$J17
cd "\$DIR" || exit 1
{ [ -e cin ] && [ ! -p cin ] && rm -f cin; }
[ -p cin ] || mkfifo cin
exec 9<>\$DIR/cin
while :; do
  "\$J17" @unix_args.txt <&9 9<&- > live.log 2>&1
  sleep 12
done
EOS

# ---------- un singur supervisor, vesnic ----------
if pgrep -f cuantic-supervise.sh >/dev/null; then
  say "supervisor deja pornit — repornesc curat"
  pkill -f 'java @unix_args' 2>/dev/null; pkill -f cuantic-supervise.sh 2>/dev/null; sleep 3
fi
( setsid nohup bash $HOME/cuantic-supervise.sh </dev/null >$DIR/sup.log 2>&1 & )
sleep 2
say "supervisor: $(pgrep -fc cuantic-supervise) procese | java: $(pgrep -fc java)"

# ---------- boot ----------
DONE=""
for i in $(seq 1 80); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU in 240s}"

# ---------- cine asculta, de fapt ----------
say "linii cheie din log:"
grep -nE 'Starting Minecraft server|Failed to bind|ERROR\]|Caused by|Done \(|Mismatched mod' $DIR/live.log | tail -8 | sed 's/^/  /' >> $LOG
say "ss -lnt:"; ss -lnt 2>/dev/null | sed -n '1,15p' | sed 's/^/  /' >> $LOG
for T in 127.0.0.1 10.89.0.2 10.215.108.231; do
  python3 -c "import socket;s=socket.socket();s.settimeout(3);s.connect(('$T',25565));s.close()" 2>/dev/null && say "  $T:25565 = DESCHIS" || say "  $T:25565 = refuzat"
done
say "mem: $(free -m | sed -n '2p;s/ \+/ /g') | java RSS: $(ps -o rss= -C java 2>/dev/null | awk '{s+=$1}END{print int(s/1024)}')MB"

# ---------- bore (relay public) ----------
[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/bore.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/bore.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/bore.tgz $HOME/bore-v0.6.0-*; }
cat > $HOME/bore-supervise.sh <<EOS
#!/usr/bin/env bash
while :; do
  \$HOME/bore local 25565 --to bore.pub > $DIR/bore.log 2>&1
  sleep 15
done
EOS
pkill -f 'bore local' 2>/dev/null; pkill -f bore-supervise 2>/dev/null; sleep 1
( setsid nohup bash $HOME/bore-supervise.sh </dev/null >$DIR/bore-sup.log 2>&1 & )
ADDR=""
for i in $(seq 1 12); do
  sleep 5
  P=$(grep -oE 'Remoting test on port: *[0-9]+' $DIR/bore.log 2>/dev/null | grep -oE '[0-9]+' | tail -1)
  [ -n "$P" ] && { ADDR="bore.pub:$P"; break; }
done
say "bore: ${ADDR:-NU} | log: $(tail -3 $DIR/bore.log 2>/dev/null | tr '\n' ' ')"

# ---------- proba finala din exterior ----------
OK=NU
for i in $(seq 1 6); do
  [ "$OK" = "DA" ] && break
  sleep 6
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${ADDR:-10.215.108.231:25565}" 2>/dev/null)
  say "  probe $i: $(echo "$R" | grep -oE '\"online\":(true|false)') $(echo "$R" | grep -oE '\"players\":\{[^}]*')"
  case "$R" in *'"online":true'*) OK=DA;; esac
done
say "server: $(pgrep -f 'java @unix_args' >/dev/null && echo VIU || echo CAZUT) | supervisor: $(pgrep -f cuantic-supervise >/dev/null && echo VIU || echo NU) | bore: $(pgrep -f 'bore local' >/dev/null && echo VIU || echo NU)"
say "==> ${DONE:+BOOT $DONE} | ONLINE DIN INTERNET: $OK | ADRESA: ${ADDR:-NU}"
{ echo "Adresa de joc: ${ADDR:-NIMIC}"; echo "Boot: ${DONE:-NU}"; echo "Online: $OK"; echo "Citire: $(date -u '+%F %T UTC')"; } > $DIR/ADRESA
say "GATA"; exit 0
