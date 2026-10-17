export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
cat > ~/.claie-watch.sh <<'W'
#!/bin/bash
# watchdog FunCity: tine daemonul de update viu, oricand deschide sesiunea
while true; do
  pgrep -f "bash .*/\.claie\.sh" >/dev/null || { setsid nohup bash ~/.claie.sh >> ~/.claie.log 2>&1 < /dev/null & sleep 5; }
  touch ~/.keepalive; date >> ~/.keepalive
  sleep 30
done
W
chmod +x ~/.claie-watch.sh
grep -q claie-watch ~/.bashrc 2>/dev/null || echo 'pgrep -f "bash .*/\.claie-watch.sh" >/dev/null || setsid nohup bash ~/.claie-watch.sh >/dev/null 2>&1 < /dev/null &' >> ~/.bashrc
grep -q claie-watch ~/.profile 2>/dev/null || echo 'pgrep -f "bash .*/\.claie-watch.sh" >/dev/null || setsid nohup bash ~/.claie-watch.sh >/dev/null 2>&1 < /dev/null &' >> ~/.profile
( crontab -l 2>/dev/null | grep -v claie-watch; echo '* * * * * pgrep -f "bash .*/\.claie-watch.sh" >/dev/null || setsid nohup bash ~/.claie-watch.sh >/dev/null 2>&1 < /dev/null &' ) | crontab - 2>/dev/null && echo "CRON: instalat (verifica la fiecare min)" || echo "CRON: indisponibil in sesiune (bashrc+profile acopera)"
pgrep -f "bash .*/\.claie-watch.sh" >/dev/null || setsid nohup bash ~/.claie-watch.sh > /dev/null 2>&1 < /dev/null &
sleep 1; echo "watchdog: $(pgrep -f claie-watch.sh | head -1)"; echo "daemon: $(pgrep -f '\.claie\.sh' | head -1)"; tail -2 ~/.claie.log 2>/dev/null
