#!/usr/bin/env bash
# UP — serverul CUANTIC pe Cloud Shell, lasat in tmux (supravietuieste jobului),
# + relay bore, + proba dinafara. Raportul (adresa) e impins in git in ~3 min.
LOG=/tmp/up.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
say "== UP — $(date -u '+%F %T UTC') =="
mkdir -p $DIR

# pack (daca lipseste)
JAR=$(ls $DIR/CatServer-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSL --retry 2 -o $DIR/p.zip "$URL" && (cd $DIR && unzip -qo p.zip && rm -f p.zip)
  JAR=$(ls $DIR/CatServer-*.jar 2>/dev/null | head -1)
fi
say "jar: ${JAR:-LIPSESTE} | java17: ${J17:-LIPSESTE}"
cd $DIR
echo 'eula=true' > eula.txt
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/; s/^player-idle-timeout=.*/player-idle-timeout=0/' server.properties

# curat ce a mai ramas din incercarile precedente
tmux kill-server 2>/dev/null
pkill -f 'unix_args.txt' 2>/dev/null; pkill -f 'bore local' 2>/dev/null; sleep 3

# serverul intr-un tmux detachat (stdin = pty, deci fara EOF = fara "Stopping server")
if command -v tmux >/dev/null; then
  tmux new-session -d -s mc "cd $DIR && $J17 @unix_args.txt > live.log 2>&1"
  say "mod: tmux"
else
  setsid script -qfc "cd $DIR && $J17 @unix_args.txt" /dev/null > $DIR/live.log 2>&1 &
  say "mod: script(1) (fara tmux)"
fi

SOCKET=NU
for i in $(seq 1 90); do
  sleep 3
  ss -lnt 2>/dev/null | grep -q ':25565' && { SOCKET=DA; say "socket aparut la it $i"; break; }
done
DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null)
say "boot: ${DONE:-NU} | socket 25565: $SOCKET"
if [ "$SOCKET" != "DA" ]; then
  say "--- de ce nu leaga:"
  grep -nE 'Failed to bind|Stopping server|Address already|ERROR' $DIR/live.log | tail -6 | sed 's/^/  /' >> $LOG
  say "--- ultimele 8 linii:"; tail -8 $DIR/live.log | cut -c1-150 | sed 's/^/  /' >> $LOG
fi
python3 - <<'PY' >> $LOG 2>&1
import socket
for h in ("127.0.0.1",):
    try:
        s = socket.create_connection((h, 25565), timeout=6); print("  handshake local: OK"); s.close()
    except Exception as e:
        print("  handshake local:", e)
PY

# ---------- relay ----------
[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/b.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/b.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/b.tgz $HOME/bore-v0.6.0-*; }
: > $DIR/bore.log
if command -v tmux >/dev/null; then
  tmux new-session -d -s bore "$HOME/bore local 25565 --to bore.pub --port 25565 2>&1 | tee -a $DIR/bore.log; $HOME/bore local 25565 --to bore.pub 2>&1 | tee -a $DIR/bore.log"
else
  setsid bash -c "$HOME/bore local 25565 --to bore.pub --port 25565 >> $DIR/bore.log 2>&1 || $HOME/bore local 25565 --to bore.pub >> $DIR/bore.log 2>&1" &
fi
ADDR=""
for i in $(seq 1 12); do
  sleep 4
  ADDR=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log 2>/dev/null | tail -1 | sed 's/listening at //')
  [ -n "$ADDR" ] && break
done
say "adresa: ${ADDR:-NU}"

# ---------- proba dinafara ----------
RES="n/a"
for i in 1 2 3; do
  sleep 10
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${ADDR:-bore.pub:1}" 2>/dev/null)
  RES=$(echo "$R" | grep -oE '"online":(true|false)')
  say "  proba $i: $RES $(echo "$R" | grep -oE '\"motd\":.{0,60}')"
  case "$R" in *'"online":true'*) break;; esac
done
say "==> ${ADDR:-NU} | socket $SOCKET | $RES"
echo "${ADDR:-NU}" > $DIR/ADRESA

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# SERVER SUS — %s\n\n- **adresa: `%s`**\n- boot: %s | socket: %s | dinafara: %s\n- procesele sunt in tmux (`tmux ls`), deci traieshte dupa job cat tine sesiunea Cloud Shell\n\n' "$(date -u '+%F %T UTC')" "${ADDR:-NU}" "${DONE:-NU}" "$SOCKET" "$RES"
  echo '```'; cat $LOG; echo '```'; } > analysis/up.md
git add -f analysis/up.md; git commit -q -m "up: ${ADDR:-nu}" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "GATA"; exit 0
