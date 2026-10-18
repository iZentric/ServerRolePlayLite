export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
mkdir -p /tmp/gunoi && mv "mods/SeleneChat-0.2.0-all.jar" /tmp/gunoi/ 2>/dev/null && echo "SeleneChat: scos (era fisier mort, fara mods.toml)"
echo "mods acum: $(ls mods/*.jar | wc -l)"
pgrep -f "java.*-jar" | while read p; do kill $p; done; sleep 5
setsid nohup bash -c 'cd ~/cuantic-live && ~/j11/bin/java -Xms2G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1' </dev/null >/dev/null 2>&1 &
for i in $(seq 1 40); do sleep 3; grep -aqE "Done \(" boot.log && break; done
grep -aE "Done \(|ERROR.*(mod|Selene)" boot.log | head -4
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: inchis"
grep -aci "warning" boot.log | awk '{print "linii warning: "$1}'
