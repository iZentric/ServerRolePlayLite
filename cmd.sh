export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== CURATENIE ==="
pkill -f "server.jar" 2>/dev/null; pkill -f cloudflared 2>/dev/null; sleep 1
rm -rf ~/mcserver ~/c.sh ~/.claie_token 2>/dev/null; echo "curat (claie ramane)"
echo "=== SERVER ULTRA-LITE ==="
mkdir -p ~/mcserver && cd ~/mcserver
ARCH=$(uname -m); [ "$ARCH" = "aarch64" ] && P=arm64 || P=amd64
B=$(curl -s https://api.papermc.io/v2/projects/paper/versions/1.21.4 | grep -o '"build":[0-9]*' | tail -1 | cut -d: -f2)
curl -sL -o server.jar "https://api.papermc.io/v2/projects/paper/versions/1.21.4/builds/$B/downloads/paper-1.21.4-$B.jar"
ls -lh server.jar | awk '{print "jar:",$5}'
echo "eula=true" > eula.txt
printf 'view-distance=6\nsimulation-distance=4\nspawn-protection=0\nmax-players=20\nmotd=UltraLite\n' > server.properties
nohup java -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=4M -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=20 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Xms2G -Xmx4G -jar server.jar nogui > server.log 2>&1 &
for i in $(seq 1 24); do sleep 5; grep -q "Done (" server.log && break; done
grep -oE "Done \([0-9.]*s\)! For help" server.log || tail -3 server.log
echo "=== TUNEL PUBLIC (fara cont) ==="
curl -sL -o cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-$P" && chmod +x cloudflared
nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > cf.log 2>&1 &
for i in $(seq 1 10); do sleep 3; grep -q "trycloudflare" cf.log && break; done
grep -oE "[a-z0-9-]+\.trycloudflare\.com:[0-9]+" cf.log | head -1
echo "=== GATA ==="
