export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
cat > ~/serveo-loop.sh <<'L'
#!/bin/bash
export PATH=$PATH:/usr/bin:/bin
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
while true; do
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=25 -o ExitOnForwardFailure=yes -R 0:localhost:25565 serveo.net > /tmp/serveo.log 2>&1 &
  SPID=$!
  A=""
  for t in $(seq 1 25); do sleep 2; A=$(grep -oE "Forwarding TCP connections from [A-Za-z0-9.]+:[0-9]+" /tmp/serveo.log | awk '{print $5}' | tail -1); [ -n "$A" ] && break; done
  if [ -n "$A" ] && [ "$A" != "$(cat ~/addr-last.txt 2>/dev/null)" ]; then
    echo "$A" > ~/addr-last.txt
    ( cd ~/srpl-claie && git fetch -q origin arena/9bbcb24f-serverroleplaylite && git reset -q --hard origin/arena/9bbcb24f-serverroleplaylite && mkdir -p diag && echo -n "$A" > diag/addr.txt && git add -f diag/addr.txt && git commit -qm "addr $A" && git push -q "https://x-access-token:${T}@github.com/iZentric/ServerRolePlayLite" HEAD:arena/9bbcb24f-serverroleplaylite )
  fi
  wait $SPID
  sleep 8
done
L
chmod +x ~/serveo-loop.sh
pkill -f serveo-loop 2>/dev/null; pkill -f "ssh.*serveo" 2>/dev/null; sleep 3
rm -f ~/addr-last.txt
setsid nohup ~/serveo-loop.sh > /dev/null 2>&1 < /dev/null &
for i in $(seq 1 20); do sleep 4; [ -n "$(cat ~/addr-last.txt 2>/dev/null)" ] && break; done
echo "ADRESA: $(cat ~/addr-last.txt 2>/dev/null || echo NEMERS)"
