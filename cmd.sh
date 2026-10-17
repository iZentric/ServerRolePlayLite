export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "=== 1. opresc java bolnav ==="
pkill -f "unix_args" 2>/dev/null; sleep 2; pgrep -f java >/dev/null && pkill -9 -f java; echo "oprit"
echo "=== 2. Java 11 ==="
if [ ! -x ~/j11/bin/java ]; then
  curl -sL "https://api.adoptium.net/v3/binary/latest/11/ga/linux/aarch64/jre/hotspot/normal/eclipse" -o /tmp/j11.tgz
  mkdir -p ~/j11 && tar xzf /tmp/j11.tgz -C ~/j11 --strip-components=1 && rm -f /tmp/j11.tgz
fi
~/j11/bin/java -version 2>&1 | head -1
echo "=== 3. pornesc serverul (lumea existenta, neatinsa) ==="
mv boot.log boot.log.old 2>/dev/null
nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
for i in $(seq 1 40); do sleep 5; grep -q "Done (" boot.log && break; done
grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 || tail -4 boot.log
echo "=== 4. tunel nou ==="
[ -x ./cloudflared ] || curl -sL -o cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64" && chmod +x ./cloudflared
pkill -f cloudflared 2>/dev/null; sleep 1
nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 &
for i in $(seq 1 12); do sleep 3; grep -q "trycloudflare" /tmp/cf.log && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
echo "=== memorie/fișier ==="; grep -c "" boot.log; free -m | head -2
