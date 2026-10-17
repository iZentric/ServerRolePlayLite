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
echo "== MONTAJ SERVER v34 =="+
cd ~/cuantic-live
echo "== MONTARE RETETA VALIDATA (v6) =="
if [ ! -d mods ] || [ -z "$(ls mods/*.jar 2>/dev/null)" ]; then mv -f mods-pre-fr mods 2>/dev/null; fi
[ -d mods ] && echo "mods: $(ls mods/*.jar 2>/dev/null | wc -l) jar-uri" || echo "FARA mods folder"
pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
for i in $(seq 1 60); do sleep 5; grep -qE "Done \(|LoadingFailed|FATAL" boot.log && break; done
sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
if grep -q "Done (" boot.clean; then
  grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1; echo "STATUT: VIU"
else
  echo "FML cere liburi lipsa - elimin exact modurile problematice si retrag un singur restart:"
  BAD=$(grep -oE "Mod [^ ]+§e[a-zA-Z0-9_-]+§r requires" boot.clean | sed 's/.*§e//;s/§r.*//' | sort -u)
  for m in $BAD; do rm -fv mods/*"${m}"* 2>/dev/null; done
  [ -z "$BAD" ] && echo "(nimic de eliminat - alte erori:)" && grep -aE "FATAL|Exception" boot.clean | head -4 | cut -c1-140
  pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 4
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do sleep 5; grep -qE "Done \(|FATAL" boot.log && break; done
  sed 's/\x1b\[[0-9;]*m//g' boot.log > boot.clean
  grep -oE "Done \([0-9.]*s\)!" boot.clean | tail -1
fi
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 12); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
