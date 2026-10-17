export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
pkill -f "cloudflared" 2>/dev/null; sleep 1
rm -f cloudflared
curl -sL --retry 3 -o cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
SZ=$(stat -c %s cloudflared 2>/dev/null || echo 0)
echo "cloudflared bytes: $SZ"
if [ "$SZ" -gt 30000000 ]; then
  chmod +x cloudflared
  nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 &
  for i in $(seq 1 25); do sleep 3; grep -qE "trycloudflare.com:[0-9]+" /tmp/cf.log && break; done
  echo "=== ADRESATA ==="
  grep -oE "[a-z0-9-]+\.trycloudflare\.com:[0-9]+" /tmp/cf.log | head -1
else
  curl -sI https://github.com 2>/dev/null | head -1 || echo github inaccesibil
fi
echo "server: $(pgrep -f unix_args >/dev/null && echo VIU || echo MORT)"
