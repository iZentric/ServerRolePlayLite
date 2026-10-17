export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
sudo -n true 2>/dev/null && echo "SUDO: da" || echo "SUDO: nu"
mkdir -p /run/playit 2>/dev/null || sudo mkdir -p /run/playit 2>/dev/null
pkill -f playitd; sleep 1
(setsid nohup ~/playit playitd --socket-path=/run/playit/playitd.sock --secret-path=$HOME/playit-run/playit.toml > /tmp/playitd.log 2>&1 < /dev/null &) 2>/dev/null
(setsid nohup ~/playitd --socket-path=/run/playit/playitd.sock --secret-path=$HOME/playit-run/playit.toml > /tmp/playitd.log 2>&1 < /dev/null &) 2>/dev/null
sleep 6
pgrep -f playitd >/dev/null && echo "playitd: traieste" || echo "playitd: nu a pornit"
tail -6 /tmp/playitd.log 2>/dev/null
if pgrep -f playitd >/dev/null; then
  (setsid nohup ~/playit start > /dev/null 2>&1 < /dev/null &)
  for i in $(seq 1 12); do sleep 3; grep -qE "playit\.gg:[0-9]+|https://playit\.gg/\S*account\S*" /tmp/playitd.log && break; done
  grep -oE "[a-z0-9-]+\.playit\.gg:[0-9]+" /tmp/playitd.log | sort -u | head -3
  grep -oE "https://playit\.gg/[^\" ]+" /tmp/playitd.log | head -2
fi
