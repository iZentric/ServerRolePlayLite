export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
cat > ~/serveo-loop.sh <<'L'
#!/bin/bash
export PATH=$PATH:/usr/bin:/bin
while true; do
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ExitOnForwardFailure=yes -R 0:localhost:25565 serveo.net > /tmp/serveo.log 2>&1
  P=$(grep -oE "Forwarding TCP port: [0-9]+" /tmp/serveo.log | grep -oE "[0-9]+" | head -1)
  [ -n "$P" ] && echo "serveo.net:$P" > ~/addr.txt
  echo "$(date) dropped, recon in 8s" >> /tmp/serveo.log
  sleep 8
done
L
chmod +x ~/serveo-loop.sh
pkill -f serveo-loop 2>/dev/null; pkill -f "serveo.net" 2>/dev/null; sleep 2
rm -f ~/addr.txt
setsid nohup ~/serveo-loop.sh > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 15); do sleep 3; [ -s ~/addr.txt ] && break; P=$(grep -oE "Forwarding TCP port: [0-9]+" /tmp/serveo.log 2>/dev/null | grep -oE "[0-9]+" | head -1); [ -n "$P" ] && { echo "serveo.net:$P" > ~/addr.txt; break; }; done
echo "ADRESA: $(cat ~/addr.txt 2>/dev/null || echo NEMERS)"
grep -iE "Forwarding|failed|error" /tmp/serveo.log | head -3
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "MC local: DESCHIS" || echo "MC: INCHIS"
