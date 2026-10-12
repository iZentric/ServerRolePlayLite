#!/bin/bash
# JAVA — pune Java noastra la punct, repara packul, face test real de boot, scrie ~/c.sh.
D=$HOME/cuantic-live
V=""
mkdir -p "$D"

if [ ! -x "$HOME/.local/jdk17/bin/java" ]; then
  A=$(uname -m); case $A in aarch64) T=aarch64;; *) T=x64;; esac
  mkdir -p "$HOME/.local"; cd "$HOME/.local" || exit 1
  echo "descarc Temurin 17 ($T)..."
  curl -fsSLo jdk.tgz "https://api.adoptium.net/v3/binary/latest/17/ga/linux/${T}/jdk/hotspot/normal/eclipse"
  tar xzf jdk.tgz
  N=$(ls -d jdk-17* 2>/dev/null | head -1)
  if [ -n "$N" ]; then rm -rf jdk17; mv -f "$N" jdk17; fi
  rm -f jdk.tgz
  cd "$D" || exit 1
fi
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
JV=$("$J" -version 2>&1 | head -1 | tr -d '"')
V="java=${JV:-NIMIC}"

JAR=$(ls "$D"/CatServer-*.jar 2>/dev/null | head -1)
if [ ! -s "$JAR" ]; then
  echo "jar lipsa/corupt - il reassamblu din release..."
  cd "$D" || exit 1
  URL=$(curl -fsS https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSLo p.zip "$URL"
  S=$(sha256sum p.zip | cut -d' ' -f1)
  if [ "$S" = "b97230e1073a8d1568205ab6fec92981b3903d947a101026deb5f9e75de0b278" ]; then V="$V sha=OK"; else V="$V sha=DIFFERIT"; fi
  unzip -qo p.zip; rm -f p.zip
  JAR=$(ls "$D"/CatServer-*.jar 2>/dev/null | head -1)
fi
V="$V jar=$(basename "${JAR:-NICIUNUL}"):$(stat -c%s "${JAR:-/dev/null}" 2>/dev/null)"
[ -f "$D/unix_args.txt" ] || V="$V unix_args=LIPSA"
echo eula=true > "$D/eula.txt"
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/' "$D/server.properties"
rm -rf "$D/logs" "$D/Crash-Reports" "$HOME/frp.tgz" 2>/dev/null
V="$V home_uses=$(df -h /home | tail -1 | tr -s ' ' | cut -d' ' -f5)"

cd "$D" || exit 1
setsid "$J" @unix_args.txt < /dev/null > boot.log 2>&1 &
PG=$!
ok=NU
for i in $(seq 1 36); do sleep 5; grep -aq 'Done (' boot.log && { ok=DA; break; }; done
bd=NU; ss -lnt | grep -q ':25565' && bd=DA
kill -TERM -"$PG" 2>/dev/null
sleep 6
V="$V boot=$ok bind=$bd"
LAST=$(grep -a -m1 'Done (' boot.log | cut -c1-40 | tr -d '\n')
V="$V [$LAST]"
tail -3 boot.log > /tmp/boot-tail.txt

cat > "$HOME/c.sh" <<'EOF'
#!/bin/bash
# CUANTIC live v4 - porneste MC + frpc si le tine sus.
D=$HOME/cuantic-live
J=$HOME/.local/jdk17/bin/java
[ -x "$J" ] || J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
cd "$D" || { echo "nu exista $D"; exit 1; }
echo "JAVA: $J -> $("$J" -version 2>&1 | head -1)"
echo "JAR : $(ls "$D"/CatServer-*.jar 2>/dev/null | head -1)"
echo eula=true > eula.txt
tmux kill-session -t mc 2>/dev/null
tmux kill-session -t frpc 2>/dev/null
tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"
tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
echo "adresa: 92.5.171.150:25565   (Ctrl+C = opresti doar supervisorul)"
LAST=-1
while :; do
  NOW=$(wc -l < live.log 2>/dev/null)
  if ss -lnt | grep -q ':25565'; then
    S="SUS - se poate intra"
  else
    S="nu asculta"
    if ! tmux ls 2>/dev/null | grep -q '^mc:'; then
      echo " sesiune mc murita -> repornesc $(date +%T)"
      tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"; LAST=0
    elif [ "$NOW" = "$LAST" ]; then
      echo " log blocat la $NOW linii:"; tail -2 live.log
    fi
  fi
  tmux ls 2>/dev/null | grep -q '^frpc:' || { echo " frpc jos -> pornit $(date +%T)"; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; }
  echo " $(date +%T) $S | live.log $NOW linii | tmux: $(tmux ls 2>/dev/null | cut -d: -f1 | tr '\n' ' ')"
  LAST=$NOW
  sleep 15
done
EOF

cd "$GITHUB_WORKSPACE" || exit 0
git config user.name java-bot
git config user.email bot@arena.local
git add -A 2>/dev/null
git commit -q --allow-empty -m "VERDICT: $V"
git pull --rebase -q origin "$GITHUB_REF_NAME" || true
git push -q origin "$GITHUB_REF_NAME" || true
echo "tail boot.log:"; cat /tmp/boot-tail.txt
echo "VERDICT: $V"
echo "c.sh: scris la $HOME/c.sh"
