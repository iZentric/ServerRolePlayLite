#!/usr/bin/env bash
# VERIF — probeaza din internet daca un client MC poate intra prin bore. Tine procesele ~4 min.
LOG=/tmp/verif.txt; : > $LOG
say(){ echo "$*" | tee -a $LOG; }
DIR=$HOME/cuantic-live
J17=$(ls /usr/lib/jvm/java-17-*/bin/java 2>/dev/null | head -1)
say "== VERIF — $(date -u '+%F %T UTC') =="
mkdir -p $DIR && cd $DIR || exit 1

JAR=$(ls CatServer-*.jar 2>/dev/null | head -1)
if [ -z "$JAR" ]; then
  URL=$(curl -fsS --max-time 30 https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  say "iaduc pack: $URL"
  curl -fsSL --retry 2 -o p.zip "$URL" && unzip -qo p.zip && rm -f p.zip
fi
say "jar: $(ls CatServer-*.jar 2>/dev/null | head -1) | java17: ${J17:-NIMIC}"
grep -q '^server-ip=' server.properties || echo 'server-ip=' >> server.properties
sed -i 's/^server-ip=.*/server-ip=/; s/^server-port=.*/server-port=25565/; s/^online-mode=.*/online-mode=false/' server.properties
echo 'eula=true' > eula.txt

pkill -f 'java @unix_args' 2>/dev/null; pkill -f 'bore local' 2>/dev/null; sleep 2
setsid bash -c "cd $DIR && exec tail -f /dev/null | ${J17:-java} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false @unix_args.txt > live.log 2>&1" &
DONE=""
for i in $(seq 1 80); do DONE=$(grep -m1 -oE 'Done \([0-9.]+s\)' $DIR/live.log 2>/dev/null); [ -n "$DONE" ] && break; sleep 3; done
say "boot: ${DONE:-NU in 240s}"
python3 - <<'PY' >> $LOG 2>&1
import socket
for host in ("127.0.0.1", "::1", "0.0.0.0"):
    try:
        fam = socket.AF_INET6 if host == "::1" else socket.AF_INET
        s = socket.socket(fam, socket.SOCK_STREAM); s.settimeout(5)
        s.connect((host, 25565)); print("  ", host, "25565: DESCHIS"); s.close()
    except Exception as e:
        print("  ", host, "25565: REFUZAT", e)
PY
ss -lnt 2>/dev/null | grep -E '25565|State' | sed 's/^/  ss: /' >> $LOG

[ -x $HOME/bore ] || { curl -fsSL --retry 2 -o $HOME/b.tgz https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-aarch64-unknown-linux-musl.tar.gz && tar xzf $HOME/b.tgz -C $HOME && mv -f $HOME/bore-v0.6.0-aarch64-unknown-linux-musl/bore $HOME/bore && chmod +x $HOME/bore && rm -rf $HOME/b.tgz $HOME/bore-v0.6.0-*; }
: > $DIR/bore.log
setsid bash -c "$HOME/bore local 25565 --to bore.pub --port 25565 > $DIR/bore.log 2>&1" &
ADDR=""
for i in $(seq 1 10); do
  sleep 4
  ADDR=$(grep -oE 'listening at bore\.pub:[0-9]+' $DIR/bore.log 2>/dev/null | tail -1 | sed 's/listening at //')
  [ -n "$ADDR" ] && break
  if [ $i -eq 5 ]; then
    say "  port 25565 fixat nu a mers, iau random"
    pkill -f 'bore local' 2>/dev/null; : > $DIR/bore.log; sleep 1
    setsid bash -c "$HOME/bore local 25565 --to bore.pub > $DIR/bore.log 2>&1" &
  fi
done
say "adresa: ${ADDR:-NU}"

for i in 1 2 3; do
  sleep 12
  R=$(curl -fsS --max-time 25 "https://api.mcsrvstat.us/3/${ADDR:-bore.pub:1}" 2>/dev/null)
  say "  proba dinafara $i: online=$(echo "$R" | grep -oE '\"online\":(true|false)') $(echo "$R" | grep -oE '\"message\":\"[^\"]+\"' | head -1)"
  case "$R" in *'"online":true'*) break;; esac
done
say "MC ping din interiorul relayului:"
BPORT=$(echo "$ADDR" | grep -oE '[0-9]+$')
MOTD=$(BPORT=$BPORT python3 - <<'PY' 2>&1 | tail -1
import socket, struct, json, time, os
port = int(os.environ.get("BPORT") or 0)
if not port: raise SystemExit("nu am portul relayului")
def v(n):
    o = b''
    while True:
        b = n & 0x7F; n >>= 7
        if n: o += bytes([b | 0x80])
        else: return o + bytes([b])
def st(t): return v(len(t.encode())) + t.encode()
try:
    sk = socket.create_connection(("bore.pub", port), timeout=25)
    body = v(0x00) + v(754) + st("bore.pub") + struct.pack(">H", port) + v(1)
    sk.sendall(v(len(body)) + body); sk.sendall(v(2) + b"\x00\x00")
    buf = b""; end = time.time() + 25
    out = "fara raspuns"
    while time.time() < end:
        try:
            sk.settimeout(max(0.5, end - time.time())); c = sk.recv(4096)
        except Exception: break
        if not c: break
        buf += c
        i = buf.find(b'{')
        if i >= 0:
            try:
                j = json.loads(buf[i:].decode('utf-8', 'ignore'))
                out = "%s | playeri %s/%s | desc: %s" % (j.get("version", {}).get("name", "?"),
                    j.get("players", {}).get("online", 0), j.get("players", {}).get("max", 0),
                    str(j.get("description", ""))[:70])
                break
            except Exception: pass
    print(out); sk.close()
except Exception as e:
    print("ESUC: %r" % (e,))
PY
)
say "  $MOTD"

mkdir -p "$GITHUB_WORKSPACE/analysis"; cd "$GITHUB_WORKSPACE"
{ printf '# VERIF — %s\n\n- adresa: `%s`\n- boot: %s\n- MC ping prin relay: %s\n\n' "$(date -u '+%F %T UTC')" "${ADDR:-NU}" "${DONE:-NU}" "$MOTD"
  echo '```'; cat $LOG; echo '```'; } > analysis/verif.md
git add -f analysis/verif.md; git commit -q -m "verif: ${ADDR:-nu}" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true; git push -q origin "$GITHUB_REF_NAME" || true
say "tin procesele 4 min ca sa probez si eu dinafara"
sleep 240
say "GATA"; exit 0
