export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
ARCH=$(uname -m)
URL=$(curl -s https://api.github.com/repos/playit-cloud/playit-agent/releases/latest | grep -oE '"https://[^"]+linux[^"]*"' | tr -d '"' | grep -iE "${ARCH/x86_64/amd64}|${ARCH/aarch64/arm64}" | head -1)
[ -z "$URL" ] && URL=$(curl -s https://api.github.com/repos/playit-cloud/playit-agent/releases/latest | grep -oE '"browser_download_url": *"[^"]+"' | sed 's/.*"\(http[^"]*\)".*/\1/' | grep -iE "linux" | grep -iE "arm64|aarch64" | head -1)
echo "URL: $URL"
if [ -n "$URL" ]; then
  curl -fsL -o playit "$URL" && chmod +x playit
fi
SZ=$(stat -c %s playit 2>/dev/null || echo 0)
echo "binar: $SZ B"
if [ "$SZ" -gt 2000000 ]; then
  mkdir -p ~/.playit
  cat > ~/.playit/config.toml <<'T'
[autotunnels.mc]
dst = "localhost:25565"
kind = "tcp"
[autotunnels.mc.port]
port = 25565
T
  pkill -f "./playit" 2>/dev/null; sleep 2
  setsid nohup ~/playit > /tmp/playit.log 2>&1 < /dev/null &
  for i in $(seq 1 30); do sleep 3; grep -qE "playit\.gg:[0-9]+" /tmp/playit.log && break; done
  grep -oE "[A-Za-z0-9._-]+\.playit\.gg:[0-9]+" /tmp/playit.log | sort -u
  echo "playit: $(pgrep -f 'playit$|/playit ' | head -1)"
fi
echo "== MC inca viu? =="
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT INCHIS"
