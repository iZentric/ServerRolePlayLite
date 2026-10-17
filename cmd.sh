export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
grep -oE "Forwarding TCP connections from [A-Za-z0-9.]+:[0-9]+" /tmp/serveo.log | tail -1 | awk '{print $5}' > ~/addr.txt
echo "ADRESA: $(cat ~/addr.txt)"
sed -i 's|grep -oE "Forwarding TCP port: \[0-9\]+" .serveo.log . grep -oE "\[0-9\]+"|grep -oE "Forwarding TCP connections from [A-Za-z0-9.]+:[0-9]+" /tmp/serveo.log|' ~/serveo-loop.sh 2>/dev/null
cat > ~/serveo-loop.sh <<'L'
#!/bin/bash
export PATH=$PATH:/usr/bin:/bin
while true; do
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 0:localhost:25565 serveo.net > /tmp/serveo.log 2>&1
  A=$(grep -oE "Forwarding TCP connections from [A-Za-z0-9.]+:[0-9]+" /tmp/serveo.log | awk '{print $5}' | tail -1)
  [ -n "$A" ] && echo "$A" > ~/addr.txt
  echo "$(date) dropped, recon 8s" >> /tmp/serveo.log
  sleep 8
done
L
chmod +x ~/serveo-loop.sh
pgrep -f serveo-loop.sh >/dev/null || { pkill -f "ssh.*serveo"; sleep 2; setsid nohup ~/serveo-loop.sh > /dev/null 2>&1 < /dev/null & }
cd ~/cuantic-live
curl -fsSL -o server-icon.png https://github.com/iZentric/ServerRolePlayLite/releases/download/funcity/server-icon.png && echo "favicon: $(stat -c %s server-icon.png) B" || echo "favicon: n-a mers"
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "MC: VIU" || echo "MC: mort"
