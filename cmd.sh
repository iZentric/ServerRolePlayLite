export PATH=$PATH:/usr/bin:/bin
cd ~ && mkdir -p mcserver && cd mcserver
echo "descarc paper..."
B=$(curl -s https://api.papermc.io/v2/projects/paper/versions/1.21.4 | grep -o '"build":[0-9]*' | tail -1 | cut -d: -f2)
curl -sL -o server.jar "https://api.papermc.io/v2/projects/paper/versions/1.21.4/builds/$B/downloads/paper-1.21.4-$B.jar"
ls -lh server.jar && echo eula=true > eula.txt
echo "pornesc serverul in background..."
nohup java -Xms2G -Xmx4G -jar server.jar nogui > server.log 2>&1 &
echo "astept 60 sec sa generalizeze lumea..."
for i in $(seq 1 12); do sleep 5; grep -q 'Done (' server.log && break; done
tail -4 server.log
