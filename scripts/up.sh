#!/bin/bash
# CUANTIC — pornire completa pe Cloud Shell, facuta de robot, si TINE serverul cat traieste jobul (~27 min).
D=$HOME/cuantic-live
S=92.5.171.150
T=pateu-de-codru-7
mkdir -p "$D"; cd "$D" || exit 1

if [ ! -f unix_args.txt ]; then
  URL=$(curl -fsS https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/lite | grep -o '"browser_download_url": *"[^"]*Server-CatServer[^"]*"' | head -1 | sed 's/.*"\(http[^"]*\)".*/\1/')
  curl -fsSLo p.zip "$URL"; unzip -qo p.zip; rm -f p.zip
fi
echo "pack: $([ -f unix_args.txt ] && echo DA || echo NU) | marime: $(du -sh "$D" | cut -f1)"
echo eula=true > eula.txt
sed -i 's/^online-mode=.*/online-mode=false/; s/^server-ip=.*/server-ip=/' server.properties
J=$(ls /usr/lib/jvm/java-17*/bin/java 2>/dev/null | head -1)
echo "java: $J"

printf 'serverAddr = "%s"\nserverPort = 443\nauth.method = "token"\nauth.token = "%s"\n\n[[proxies]]\nname = "mc"\ntype = "tcp"\nlocalIP = "127.0.0.1"\nlocalPort = 25565\nremotePort = 25565\n' "$S" "$T" > "$HOME/frpc.toml"
if [ ! -x "$HOME/frpc" ]; then
  VER=$(curl -fsS https://api.github.com/repos/fatedier/frp/releases/latest | grep -oE '"tag_name": *"v[0-9.]+"' | head -1 | grep -oE '[0-9.]+')
  ARCH=$(uname -m); case $ARCH in aarch64) A=arm64;; *) A=amd64;; esac
  cd "$HOME" && curl -fsSLo frp.tgz "https://github.com/fatedier/frp/releases/download/v${VER}/frp_${VER}_linux_${A}.tar.gz" && tar xzf frp.tgz && mv -f frp_${VER}_linux_${A}/frpc "$HOME/frpc"
  cd "$D" || exit 1
fi
echo "frpc: $("$HOME/frpc" --version 2>&1 | head -1)"

tmux kill-server 2>/dev/null
pkill -f unix_args.txt 2>/dev/null
pkill -f 'frpc -c' 2>/dev/null
sleep 3
tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"
i=0
while [ $i -lt 60 ]; do
  sleep 5; i=$((i+1))
  ss -lnt | grep -q ':25565' && break
done
echo "socket 25565 dupa $((i*5))s: $(ss -lnt | grep -q ':25565' && echo DA || echo NU)"
grep -a -m1 'Done (' "$D/live.log"

tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"
sleep 10
tail -2 "$HOME/frpc.log"
for k in 1 2 3; do
  sleep 6
  echo "testextern $k: $(curl -fsS --max-time 12 https://api.mcsrvstat.us/3/$S:25565 | tr -d '\n' | head -c 200)"
done

mkdir -p "$GITHUB_WORKSPACE/analysis"
{ printf '# UP — %s\n\n' "$(date -u '+%F %T UTC')"; echo '```'; echo "adresa: $S:25565"; ss -lnt | grep 25565; tail -3 "$HOME/frpc.log"; echo '```'; } > "$GITHUB_WORKSPACE/analysis/up.md"
cd "$GITHUB_WORKSPACE" || exit 0
git config user.name cuantic-bot
git config user.email bot@arena.local
git add -f analysis/up.md
git commit -q -m "up: $S:25565" || true
git pull --rebase -q origin "$GITHUB_REF_NAME" || true
git push -q origin "$GITHUB_REF_NAME" || true
echo "ADRESA=$S:25565"

END=$(( $(date +%s) + 1500 ))
while [ "$(date +%s)" -lt "$END" ]; do
  pgrep -f unix_args.txt > /dev/null || { tmux kill-session -t mc 2>/dev/null; tmux new -s mc -d "cd $D && $J @unix_args.txt > live.log 2>&1"; echo "$(date +%T) MC repornit"; }
  pgrep -f 'frpc -c' > /dev/null || { tmux kill-session -t frpc 2>/dev/null; tmux new -s frpc -d "exec $HOME/frpc -c $HOME/frpc.toml > $HOME/frpc.log 2>&1"; echo "$(date +%T) frpc repornit"; }
  sleep 20
done
echo "job gata — serverul se opreste odata cu el"
