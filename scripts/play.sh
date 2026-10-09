#!/usr/bin/env bash
# PLAY — serverul pe Cloud Shell, legat pe 127.0.0.1 + bore; adresa in git in ~2 min; jobul il tine 55 min.
LOG=/tmp/play.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
HOLD=${HOLD:-55}
say "== PLAY — $(date -u '+%F %T UTC') (tin ${HOLD} min) =="
mkdir -p $DIR && cd $DIR || exit 1
JAR=$(ls CatServer-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip
fi

# experiment: ce bind-uri sunt posibile pe gazda asta?
python3 - <<'PY' >> $LOG 2>&1
import socket
for host, fam in (("0.0.0.0", socket.AF_INET), ("127.0.0.1", socket.AF_INET), ("::", socket.AF_INET6)):
    s = socket.socket(fam, socket.SOCK_STREAM)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); s.bind((host, 25566)); print("  bind", host, ":25566 = OK")
    except Exception as e:
        print("  bind", host, ":25566 = ESUC", e)
    s.close()
PY

pkill -f 'unix_args.txt' 2>/dev/null; pkill -f 'bore local' 2>/dev/null; sleep 2
echo 'eula=true' > eula.txt
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=127.0.0.1/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
sed -i "1s/.*/-Xms512M/;2s/.*/-Xmx2G/" unix_args.txt

# stdin: fifo cu scriitor in bucla (nu tail pe /dev/null)
[ -e cin ] && [ ! -p cin ] && rm -f cin
[ -p cin ] || mkfifo cin
setsid bash -c 'exec 8>"'"$DIR"'/cin; while :; do sleep 3600; done' &
setsid bash -c "cd $DIR && exec ${J17:-java} @unix_args.txt < $DIR/cin > live.log 2>&1" &

# astept socketul, nu doar "Done"
LISTEN=NU
for i in $(seq 1 70); do
  sleep 3
  ss -lnt 2>/dev/null | grep -q ':25565' && { LISTEN=DA; break; }
  grep -q 'Done (' $DIR/live.log 2>/dev/null && say "  (Done gasit la it $i, ascult $LISTEN)"
done
say "socket 25565: $LISTEN | boot: $(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null)"
[ "$LISTEN" = "NU" ] && { say "primele 15 din live.log:"; head -15 $DIR/live.log | sed 's/^/  /' >> $LOG; }
python3 - <<'PY' >> $LOG 2>&1
import socket
try:
    s = socket.create_connection(("127.0.0.1", 25565), timeout=6)
    s.sendall(b"\x00"); d = s.recv(64); print("  MC raspunde pe loopback:", d[:16])
except Exception as e:
    print("  loopback 25565:", e)
PY

[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/b.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/b.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/b.tgz $HOME/bore-v0.6.0-*; }
: > $DIR/bore.log
setsid bash -c "$HOME/bore local 25565 --to bore.pub --port 25565 >> $DIR/bore.log 2>&1" &
ADDR=""
for i in $(seq 1 10); do
  sleep 4
  ADDR=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log | tail -1 | sed 's/listening at //')
  [ -n "$ADDR" ] && break
  if [ $i -eq 5 ]; then pkill -f 'bore local' 2>/dev/null; : > $DIR/bore.log; setsid bash -c "$HOME/bore local 25565 --to bore.pub >> $DIR/bore.log 2>&1" & fi
done
say "adresa: ${ADDR:-NU}"
R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${ADDR:-bore.pub:1}" 2>/dev/null)
say "probe dinafara: $(echo "$R" | grep -oE '\"online\":(true|false)') $(echo "$R" | grep -oE '\"motd\":.{0,70}')"

# raport ACUM, ca sa apuci sa intri
mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# JOCI ACUM — %s\n\n- **`%s`**\n- server: %s | socket: %s | probe dinafara: %s\n- jobul tine procesele %s min\n\n' "$(date -u '+%F %T UTC')" "${ADDR:-NU}" "$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null)" "$LISTEN" "$(echo "$R" | grep -oE '\"online\":(true|false)')" "$HOLD"
  echo '```'; cat $LOG; echo '```'; } > analysis/play.md
git add -f analysis/play.md; git commit -q -m "play: ${ADDR:-nu}" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true

# ---------- mentinere ----------
N=0
while [ $N -lt $((HOLD - 2)) ]; do
  sleep 60; N=$((N+1))
  pgrep -f 'unix_args.txt' >/dev/null || { say "[$N] server cazut, repornesc"; setsid bash -c "cd $DIR && exec ${J17:-java} @unix_args.txt < $DIR/cin > live.log 2>&1" & }
  pgrep -f 'bore local' >/dev/null || { say "[$N] bore cazut, repornesc"; : > $DIR/bore.log; setsid bash -c "$HOME/bore local 25565 --to bore.pub >> $DIR/bore.log 2>&1" & }
  [ $((N % 15)) -eq 0 ] && say "[$N min] sus=$(pgrep -fc 'unix_args.txt') rss=$(ps -o rss= -C java 2>/dev/null|awk '{s+=$1}END{print int(s/1024)}')MB"
done
say "GATA PLAY"; exit 0
