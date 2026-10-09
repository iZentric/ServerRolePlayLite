#!/usr/bin/env bash
# LIVE7 — serverul RAMANE SUS in job (~2h), cu relay bore.pub = IP functional pentru Minecraft.
# Oprire: pun fisier deploy/STOP-LIVE.txt in repo (jobul se uita dupa el la fiecare pull).
LOG=/tmp/live.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
WS=$GITHUB_WORKSPACE; DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
say "== LIVE7 — $(date -u '+%F %T UTC') =="
mkdir -p $DIR && cd $DIR || exit 1

[ -f $WS/deploy/STOP-LIVE.txt ] && { say "STOP-LIVE exista, nu pornesc"; exit 0; }

# ---------- pack ----------
JAR=$(ls CatServer-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  URL=$(curl -fsS --max-time 25 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  say "iaduc pack: $URL"
  curl -fsSL --retry 2 -o pack.zip "$URL" && unzip -qo pack.zip && rm -f pack.zip
  JAR=$(ls CatServer-*.jar 2>/dev/null | head -1)
fi
say "jar: ${JAR:-NIMIC} | heap: $(head -2 unix_args.txt 2>/dev/null | tr '\n' ' ') | mods: $(ls mods 2>/dev/null | wc -l) | plugini: $(ls plugins 2>/dev/null | wc -l)"
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo "eula=true" > eula.txt

# ---------- stop ce a mai ramas din rularile trecute ----------
pkill -f cuantic-supervise 2>/dev/null; pkill -f bore-supervise 2>/dev/null
pkill -f 'java @unix_args' 2>/dev/null; pkill -f 'bore local' 2>/dev/null; sleep 3

# ---------- server (stdin = fifo tinut deschis de un writer vesnic) ----------
[ -e cin ] && [ ! -p cin ] && rm -f cin
[ -p cin ] || mkfifo cin
setsid nohup tail -f /dev/null > $DIR/cin &
sleep 1
setsid nohup "$J17" @unix_args.txt < $DIR/cin > $DIR/live.log 2>&1 &
sleep 4
say "java: $(pgrep -fc 'java @unix_args') proces | mem: $(free -m | sed -n '2p;s/ \+/ /g')"

DONE=""
for i in $(seq 1 80); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU in 240s} | ERROR: $(grep -cE '/ERROR\]' $DIR/live.log 2>/dev/null)"
python3 -c "
import socket
try:
    s=socket.create_connection(('127.0.0.1',25565),timeout=6); print('  port local 25565: DESCHIS'); s.close()
except Exception as e:
    print('  port local 25565: REFUZAT', e)
" 2>&1 | tee -a $LOG

# ---------- relay ----------
[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/bore.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/bore.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/bore.tgz $HOME/bore-v0.6.0-*; }
setsid nohup $HOME/bore local 25565 --to bore.pub > $DIR/bore.log 2>&1 &
ADDR=""
for i in $(seq 1 15); do
  sleep 4
  PORT=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log 2>/dev/null | tail -1 | grep -oE '[0-9]+$')
  [ -n "$PORT" ] && { ADDR="bore.pub:$PORT"; break; }
done
say "relay: ${ADDR:-NU}"

# ---------- MC ping cap-coada, prin relay ----------
MOTD="n/a"
if [ -n "$PORT" ]; then
  MOTD=$(python3 - "$PORT" <<'PY' 2>&1 | tail -1
import socket,struct,json,sys,time
port=int(sys.argv[1])
def v(n):
    o=b''
    while True:
        b=n&0x7F; n>>=7
        if n: o+=bytes([b|0x80])
        else: return o+bytes([b])
def st(t): return v(len(t.encode()))+t.encode()
body=v(0x00)+v(754)+st("bore.pub")+struct.pack(">H",port)+v(1)
try:
    sk=socket.create_connection(("bore.pub",port),timeout=25)
    sk.sendall(v(len(body))+body)
    sk.sendall(v(2)+b"\x00\x00")
    buf=b""; end=time.time()+25
    while time.time()<end:
        try: sk.settimeout(max(0.5,end-time.time())); c=sk.recv(4096)
        except Exception: break
        if not c: break
        buf+=c
        i=buf.find(b'{')
        if i>=0:
            try:
                j=json.loads(buf[i:].decode('utf-8','ignore'))
                print("%s | playeri %s/%s | MOTD %s" % (j.get("version",{}).get("name","?"),
                      j.get("players",{}).get("online",0), j.get("players",{}).get("max",0),
                      str(j.get("description",""))[:60]))
                break
            except Exception: pass
    sk.close()
except Exception as e:
    print("ESUC: %r" % (e,))
PY
)
  say "MC ping prin relay: $MOTD"
fi

mkdir -p $WS/analysis
cd $WS
{ echo "# CUANTIC LIVE — $(date -u '+%F %T UTC') (jobul tine serverul ~2h)"; echo
  echo "- **ADRESA DE JOC: \`${ADDR:-NU}\`** — Java 1.16.5, cracked, CUANTIC 1.5.8"; echo
  echo "- boot: ${DONE:-NU} | MC ping din exterior: ${MOTD}"; echo
  echo '```'; cat $LOG; echo '```'; } > analysis/live.md
git add -f analysis/live.md && git commit -q -m "live: adresa ${ADDR:-nu}" ; git pull --rebase -q origin "$GITHUB_REF_NAME" ; git push -q origin "$GITHUB_REF_NAME"
say "raport impins"

# ---------- mentinere ~2h ----------
N=0
while [ $N -lt 115 ]; do
  sleep 60; N=$((N+1))
  pgrep -f 'java @unix_args' >/dev/null || { say "[$N min] java cazut, repornesc"; setsid nohup "$J17" @unix_args.txt < $DIR/cin > $DIR/live.log 2>&1 & }
  pgrep -f 'bore local' >/dev/null || { say "[$N min] bore cazut, repornesc"; setsid nohup $HOME/bore local 25565 --to bore.pub > $DIR/bore.log 2>&1 & }
  if [ $((N % 10)) -eq 0 ]; then
    git pull -q --rebase origin "$GITHUB_REF_NAME" 2>/dev/null
    [ -f $WS/deploy/STOP-LIVE.txt ] && { say "[$N min] STOP-LIVE gasit -> ma opresc"; break; }
    say "[$N min] sus | java=$(pgrep -fc 'java @unix_args') RSS=$(ps -o rss= -C java 2>/dev/null | awk '{s+=$1}END{print int(s/1024)}')MB keepup=$(grep -c 'keep up' $DIR/live.log 2>/dev/null) errors=$(grep -cE '/ERROR\]' $DIR/live.log 2>/dev/null)"
  fi
done
say "GATA dupa ${N} min"
exit 0
