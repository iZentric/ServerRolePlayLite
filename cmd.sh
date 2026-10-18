export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
cat > start.sh <<'EOF'
#!/bin/bash
cd $HOME/cuantic-live
exec $HOME/j11/bin/java -Xms1G -Xmx5G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1
EOF
chmod +x start.sh
setsid nohup ./start.sh </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(" boot.log && break; done
grep -aE "Done \(|Error" boot.log | tail -2
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
R="python3 /tmp/rcon.py $HOME/cuantic-live/rcon.pass"
$R "list" 2>&1 | head -1
$R "chunky radius 1000" 2>&1 | head -1
$R "chunky start" 2>&1 | head -1
sleep 30
$R "chunky status" 2>&1 | head -2
echo "java rss: $(( $(ps -o rss= -p $(pgrep -f 'java.*FunCity' | head -1) 2>/dev/null || echo 0) / 1024 )) MB"; free -m | awk '/^Mem:/{print "libera: "$7"M"}'
