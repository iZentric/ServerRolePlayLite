export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
pkill -f "java.*FunCity" 2>/dev/null; sleep 4
rm -f /tmp/mcctl; mkfifo -m 600 /tmp/mcctl
setsid nohup bash -c 'cd $HOME/cuantic-live; tail -f /tmp/mcctl | $HOME/j11/bin/java -Xms1G -Xmx5G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=25 -XX:G1MaxNewSizePercent=40 -XX:InitiatingHeapOccupancyPercent=40 -XX:G1HeapRegionSize=8M -XX:MaxGCPauseMillis=30 -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1' </dev/null >/dev/null 2>&1 &
for i in $(seq 1 60); do sleep 3; grep -aqE "Done \(" boot.log && break; done
grep -aE "Done \(" boot.log | tail -1
ss -lnt | grep -q ':25565 ' && echo PORT-OK || echo PORT-NOK
echo "list" > /tmp/mcctl; echo "chunky radius 1000" > /tmp/mcctl; sleep 2; echo "chunky start" > /tmp/mcctl
sleep 25
echo "=== chunky ==="; grep -aE "\[Chunky\]" boot.log | tail -4
echo "=== jucatori ==="; grep -aE "There are" boot.log | tail -1
