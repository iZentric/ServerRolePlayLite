#!/usr/bin/env bash
# HOLD — server CUANTIC + relay pe Cloud Shell, tinut in viatza cat traieste jobul,
# apoi jobul isi da singur dispatch => serverul nu se mai opreste.
LOG=/tmp/hold.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
MIN_MAX=${MIN_MAX:-320}
say "== HOLD — $(date -u '+%F %T UTC') (job de pana la ${MIN_MAX} min) =="
mkdir -p $DIR && cd $DIR || exit 1

# ---------- pack ----------
JAR=$(ls CatServer-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  say "iaduc pack: $URL"
  curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip
fi
say "jar: $(ls CatServer-*.jar 2>/dev/null | head -1) | mods: $(ls mods 2>/dev/null | wc -l) | plugini: $(ls plugins 2>/dev/null | wc -l) | java17: ${J17:-NIMIC}"
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo 'eula=true' > eula.txt

# ---------- server (stdin vesnic = nu se mai opreste singur) ----------
pkill -f 'java @unix_args' 2>/dev/null; pkill -f 'bore local' 2>/dev/null; sleep 2
setsid bash -c "cd $DIR && exec tail -f /dev/null | ${J17:-java} @unix_args.txt >> live.log 2>&1" &
say "server pornit"
DONE=""
for i in $(seq 1 90); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU in 270s}"

# ---------- relay ----------
[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/bore.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/bore.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/bore.tgz $HOME/bore-v0.6.0-*; }
start_bore(){
  if [ -n "$PIN" ]; then setsid bash -c "$HOME/bore local 25565 --to bore.pub --port 25565 >> $DIR/bore.log 2>&1";
  else setsid bash -c "$HOME/bore local 25565 --to bore.pub >> $DIR/bore.log 2>&1"; fi
}
: > $DIR/bore.log; PIN=1; start_bore &
ADDR=""
for i in $(seq 1 12); do
  sleep 4
  ADDR=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log | tail -1 | sed 's/listening at //')
  [ -n "$ADDR" ] && break
  if [ $i -eq 6 ]; then say "port fixat refuzat, iau random"; PIN=; pkill -f 'bore local' 2>/dev/null; : > $DIR/bore.log; start_bore &
  fi
done
say "adresa: ${ADDR:-NU}"
[ -z "$ADDR" ] && PIN=
sleep 3
EXT=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${ADDR:-1.2.3.4:25565}" 2>/dev/null)
say "probe dinafaras: $(echo "$EXT" | grep -oE '\"online\":(true|false)') | $(echo "$EXT" | grep -oE '\"motd\":\[[^]]*' | head -c 90)"

# ---------- adresa in git, acum ----------
rep(){
  mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
  { printf '# CUANTIC pe Cloud Shell — %s\n' "$(date -u '+%F %T UTC')"
    echo
    echo "- **JOCI PE: \`${ADDR:-se pune}\`** (Minecraft Java 1.16.5, cracked)"
    echo "- boot: ${DONE:-?} | relay: $([ -n "$ADDR" ] && echo VIU || echo CAZUT) | server: $(pgrep -f 'java @unix_args' >/dev/null && echo VIU || echo CAZUT)"
    echo "- mentinere: joburi inlantuite, adresa se actualizeaza aici daca se schimba portul"
    echo; echo '```'; cat $LOG; echo '```'; } > analysis/hold.md
  git add -f analysis/hold.md; git commit -q -m "hold: ${ADDR:-?}" || true
  git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
}
rep

# ---------- mentinere + re-armare ----------
N=0
while [ $N -lt $MIN_MAX ]; do
  sleep 60; N=$((N+1))
  if ! pgrep -f 'java @unix_args' >/dev/null; then
    say "[$N] java cazut, repornesc"; : > $DIR/live.log
    setsid bash -c "cd $DIR && exec tail -f /dev/null | ${J17:-java} @unix_args.txt >> live.log 2>&1" &
    for i in $(seq 1 40); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
    say "[$N] boot: ${DONE:-NU}"; rep
  fi
  if ! pgrep -f 'bore local' >/dev/null; then
    say "[$N] bore cazut, repornesc"; : > $DIR/bore.log; start_bore &
    sleep 12
    A2=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log | tail -1 | sed 's/listening at //')
    [ -n "$A2" ] && { ADDR="$A2"; say "[$N] adresa nouas: $ADDR"; rep; }
  fi
  [ $((N % 20)) -eq 0 ] && say "[$N] sus: java=$(pgrep -fc 'java @unix_args') bore=$(pgrep -fc 'bore local') rss=$(ps -o rss= -C java 2>/dev/null | awk '{s+=$1}END{print int(s/1024)}')MB errs=$(grep -cE '/ERROR\]' $DIR/live.log 2>/dev/null)"
done
say "re-armez jobul urmator ca serverul sa nu cada"
curl -fsS -X POST -H "Authorization: Bearer ${GITHUB_TOKEN}" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/${GITHUB_REPOSITORY}/actions/workflows/hold.yml/dispatch" -d "{\"ref\":\"$GITHUB_REF_NAME\"}" >> $LOG 2>&1
rep; say "GATA HOLD"; exit 0
