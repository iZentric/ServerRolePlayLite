export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "server: $(pgrep -f unix_args >/dev/null && echo VIU || echo MORT)"
pgrep -f "cloudflared tunnel" >/dev/null || { nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 & }
for i in $(seq 1 25); do sleep 3; grep -qE "trycloudflare.com:[0-9]+" /tmp/cf.log && break; done
echo "=== ADRESA PUBLICA ==="
grep -oE "[a-z0-9-]+\.trycloudflare\.com:[0-9]+" /tmp/cf.log | head -1 || tail -6 /tmp/cf.log
