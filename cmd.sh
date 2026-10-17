export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
echo "== SERVEO (zero cont) =="
pkill -f "serveo" 2>/dev/null; sleep 1
setsid nohup ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 25565:localhost:25565 serveo.net > /tmp/serveo.log 2>&1 < /dev/null &
for i in $(seq 1 10); do sleep 3; grep -qE "Forwarding TCP|remoted port forwarding|Failed" /tmp/serveo.log && break; done
head -6 /tmp/serveo.log
PORT=$(grep -oE "Forwarding TCP port: [0-9]+" /tmp/serveo.log | grep -oE "[0-9]+" | head -1)
if [ -n "$PORT" ]; then
  echo "SERVEO OK: serveo.net:$PORT"
  ss -lnt 2>/dev/null | grep -q ":25565 " && echo "MC local: DESCHIS"
else
  echo "serveo mort - PLAYITD standalone:"
  mkdir -p ~/playit-run && cd ~/playit-run
  cat > playit.toml <<'T'
[autotunnels.mc]
dst = "localhost:25565"
kind = "tcp"
[autotunnels.mc.port]
port = 25565
T
  pkill -f playitd 2>/dev/null; sleep 1
  setsid nohup ~/playit version >/dev/null 2>&1
  ~/playit version 2>&1 | head -1
  setsid nohup ~/playit start --socket-path=./playit.sock --secret-path=./playit.toml > /tmp/playitd.log 2>&1 < /dev/null &
  [ ! -s /tmp/playitd.log ] && setsid nohup ~/playit start > /tmp/playitd.log 2>&1 < /dev/null &
  for i in $(seq 1 20); do sleep 3; grep -qE "playit\.gg:[0-9]+|https://playit\.gg[^ ]*account[^ ]*" /tmp/playitd.log && break; done
  head -20 /tmp/playitd.log
  grep -oE "[A-Za-z0-9._-]+\.playit\.gg:[0-9]+" /tmp/playitd.log | sort -u | head -3
  grep -oE "https://playit\.gg[^\" ]*" /tmp/playitd.log | head -2
fi
echo "== MC =="
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT INCHIS"
