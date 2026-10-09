#!/usr/bin/env bash
# CUANTIC LIVE v2 pe gazda runner-ului. Fix major: Java 17 (nu 21 — mixin 1.16.5 crapă),
# stdin pe fifo ca sa nu se opreasca la EOF, process detasat (traieste dupa job),
# apoi relay TCP (playit) ca sa ai adresie publica.
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live; cd $DIR || exit 1
say "== CUANTIC LIVE v2 — $(date -u '+%F %T UTC') =="
say "disc: $(df -h / | sed -n 2p) | mem: $(free -m | sed -n '2p;s/ \+/ /g')"

# ---------- Java 17 ----------
J17=""
for c in $HOME/jdk17/bin/java /usr/lib/jvm/java-17-*/bin/java /usr/lib/jvm/java-17-openjdk*/bin/java $HOME/jdk-17*/bin/java; do
  [ -x "$c" ] && J17=$c && break
done
if [ -z "$J17" ]; then
  say "iau Temurin 17 (arm64)..."
  curl -fsSL --retry 2 -o $HOME/jdk17.tgz "https://api.adoptium.net/v3/binary/latest/17/ga/linux/aarch64/jdk/hotspot/normal/eclipse" \
    && mkdir -p $HOME/jdk17 && tar xzf $HOME/jdk17.tgz -C $HOME/jdk17 --strip-components=1 && rm -f $HOME/jdk17.tgz
  J17=$HOME/jdk17/bin/java
fi
[ -x "$J17" ] || { say "FARA JAVA 17 — iesesc"; exit 1; }
say "java17: $($J17 -version 2>&1 | head -1)  [$J17]"

# ---------- oprire eleganta ce era ----------
pkill -f 'unix_args.txt' 2>/dev/null; pkill -f 'cuantic-live' 2>/dev/null; sleep 2
echo "eula=true" > eula.txt

# ---------- stdin fifo + sleep-holder (fara EOF = fara stop automat) ----------
rm -f console.in; mkfifo console.in
setsid nohup sleep 99999 > console.in < /dev/null 2>&1 &

# ---------- start ----------
sed -i "1s/.*/-Xms1G/;2s/.*/-Xmx4G/" unix_args.txt
say "args: $(head -2 unix_args.txt | tr '\n' ' ')"
setsid nohup "$J17" @unix_args.txt < console.in > live.log 2>&1 &
sleep 3
say "procese java: $(pgrep -fc java)"

DONE=""
for i in $(seq 1 70); do
  DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' live.log 2>/dev/null)
  [ -n "$DONE" ] && break
  sleep 3
done
say "boot: ${DONE:-NU in 210s}"
say "ERROR in log: $(grep -c ' ERROR ' live.log)"
say "primele 12 linii:"; head -12 live.log | sed 's/^/  /' >> $LOG
grep -m1 -A6 'Exception\|error' live.log | head -8 | sed 's/^/  ! /' >> $LOG

L=NU; (timeout 4 bash -c "</dev/tcp/127.0.0.1/25565" 2>/dev/null) && L=DA
say "asculta pe 127.0.0.1:25565: $L"
say "ram: $(free -m | sed -n '2p;s/ \+/ /g')"

# ---------- relay public (playit) ----------
ADDR=""
EXT=$(curl -fsS --max-time 20 "https://api.mcsrvstat.us/3/132.145.236.16:25565" 2>/dev/null | tr -d '\n ')
case "$EXT" in *'"online":true'*) ADDR="132.145.236.16:25565"; say "IP-ul intra direct!";; esac
say "probe direct IP: $(echo "$EXT" | grep -oE '"online":[a-z]+')"
if [ -z "$ADDR" ]; then
  say "iau playit (relay gratuit pentru MC Java)..."
  if [ ! -x $HOME/playit ]; then
    PU=$(curl -fsS --max-time 20 https://api.github.com/repos/digitalnet/playit-clients/releases/latest | grep -o '"browser_download_url": *"[^"]*linux-aarch64[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
    say "asset: ${PU:-NICIUNUL}"
    if [ -n "$PU" ]; then
      curl -fsSL --retry 2 -o $HOME/playit.tgz "$PU" && tar xzf $HOME/playit.tgz -C $HOME 2>/dev/null
      find $HOME -maxdepth 2 -name 'playit*' -type f -not -name '*.tgz' -not -name 'playit.tgz' -exec mv -f {} $HOME/playit \; 2>/dev/null
      chmod +x $HOME/playit 2>/dev/null
    fi
  fi
  if [ -x $HOME/playit ]; then
    rm -rf $HOME/.config/playit 2>/dev/null
    setsid nohup $HOME/playit --url localhost:25565 < /dev/null > $DIR/playit.log 2>&1 &
    sleep 22
    say "playit.log:"; tail -20 $DIR/playit.log | sed 's/^/  /' >> $LOG
    A=$(grep -oE 'playit\.gg:[0-9]+' $DIR/playit.log | head -1)
    [ -z "$A" ] && A=$(grep -oE '[a-z0-9-]+\.tunnel\.playit\.gg' $DIR/playit.log | head -1)
    CLAIM=$(grep -oE 'https://playit\.gg/[a-zA-Z0-9/_-]*' $DIR/playit.log | head -1)
    [ -n "$A" ] && ADDR="$A"
    say "adresa relay: ${A:-NIMIC} | claim: ${CLAIM:-—}"
  else
    say "playit indisponibil"
  fi
fi

say "==> ${DONE:+SERVER PORNIT ($DONE)}"
say "==> ADRESA DE JOC: ${ADDR:-NU AM REUSAT (serverul merge local, fara intrare publica)}"
echo "Adresa de joc: ${ADDR:-NIMIC}" > $DIR/ADRESA
[ -n "$CLAIM" ] && echo "Claim: $CLAIM" >> $DIR/ADRESA
say "GATA"; exit 0
