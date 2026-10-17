export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== CAUZA CRASH =="
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -nE "ERROR|Caused by|FATAL|Exception:" | head -6 | cut -c1-170
echo "== CURATARE LOCK + PORNIRE CORECTA =="
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 6
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock 2>/dev/null
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
sleep 2
echo "pid: $(pgrep -f 'j11/bin/java' | head -1)"
for i in $(seq 1 50); do sleep 5; grep -q "Done (" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -E "Done \(|ERROR" | tail -3 | cut -c1-150
ss -lnt 2>/dev/null | grep -q 25565 && echo "PORT 25565: DESCHIS" || echo "PORT: INCĂ ÎNCHIS"
pgrep -f cloudflared >/dev/null || { cd ~/cuantic-live && setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null & for i in $(seq 1 15); do sleep 3; grep -q trycloudflare /tmp/cf.log && break; done; }
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
