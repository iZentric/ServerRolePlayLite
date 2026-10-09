#!/bin/bash
# CUANTIC live — Cloud Shell. Gaseste Java 17 (o si descarca daca lipseste), porneste MC + frpc, le tine sus.
D=$HOME/cuantic-live
cd "$D" || { echo "nu exista $D"; exit 1; }

JAVA_OK=0
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
[ -x "$J" ] || J=$(command -v java)
if [ -x "$J" ] && "$J" -version 2>&1 | head -1 | grep -qE '"(17|18|19|20|21)'; then JAVA_OK=1; fi
if [ "$JAVA_OK" = 0 ]; then
  if [ -x "$HOME/.local/jdk17/bin/java" ]; then J="$HOME/.local/jdk17/bin/java"; JAVA_OK=1; fi
fi
if [ "$JAVA_OK" = 0 ]; then
  echo "Java 17 absentata — o descarc (Temurin, ~180 MB)..."
  A=$(uname -m); case $A in aarch64) T=aarch64;; *) T=x64;; esac
  U="https://api.adoptium.net/v3/binary/latest/17/ga/linux/${T}/jdk/hotspot/normal/eclipse"
  mkdir -p "$HOME/.local" && cd "$HOME/.local" || exit 1
  curl -fsSLo jdk.tgz "$U" && tar xzf jdk.tgz
  N=$(ls -d jdk-17* 2>/dev/null | head -1)
  [ -n "$N" ] && mv -f "$N" jdk17 2>/dev/null
  rm -f jdk.tgz
  cd "$D" || exit 1
  J="$HOME/.local/jdk17/bin/java"
fi
echo "JAVA=$J"
"$J" -version 2>&1 | head -1

if [ ! -f unix_args.txt ]; then
  echo "pack absentat — il descarc..."
  URL=$(curl -fsS https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSLo p.zip "$URL"; unzip -qo p.zip; rm -f p.zip
fi
echo eula=true > eula.txt
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/' server.properties

echo "adresa: 92.5.171.150:25565   (Ctrl+C = opresti tot)"
while :; do
  if ! pgrep -f unix_args.txt > /dev/null; then
    tmux kill-session -t mc 2>/dev/null
    tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"
    echo "MC pornit la $(date +%T) cu $J — load 60-90s"
  fi
  if ! pgrep -f 'frpc -c' > /dev/null; then
    tmux kill-session -t frpc 2>/dev/null
    tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
    echo "frpc pornit la $(date +%T)"
  fi
  if ss -lnt | grep -q ':25565'; then
    echo " $(date +%T) SUS — 25565 asculta, se poate intra"
  else
    echo " $(date +%T) se incarca | java $(pgrep -fc unix_args.txt) proc | live.log: $(wc -l < live.log) linii"
  fi
  sleep 20
done
