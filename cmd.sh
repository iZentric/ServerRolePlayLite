export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/srpl-claie && git fetch -q origin arena/9bbcb24f-serverroleplaylite && git reset -q --hard origin/arena/9bbcb24f-serverroleplaylite
cd /tmp && cat ~/srpl-claie/diag/cp_part0.txt ~/srpl-claie/diag/cp_part1.txt ~/srpl-claie/diag/cp_part2.txt ~/srpl-claie/diag/cp_part3.txt > cp.b64
wc -c cp.b64; tr -d '\n\r ' < cp.b64 | base64 -d > cp.jar; S=$(stat -c%s cp.jar); echo "jar: $S B (trebuie 815372)"
unzip -l cp.jar >/dev/null 2>&1 && grep -qa config.yml <(unzip -p cp.jar META-INF/MANIFEST.MF 2>/dev/null; unzip -l cp.jar) && echo "JAR VALID"
cp cp.jar ~/cuantic-live/plugins/CoreProtect.jar
cd ~/cuantic-live
pgrep -f "java.*-jar" | while read p; do kill $p; done; sleep 5
setsid nohup bash -c 'cd ~/cuantic-live && ~/j11/bin/java -Xms2G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1' </dev/null >/dev/null 2>&1 &
for i in $(seq 1 40); do sleep 3; grep -aqE "Done \(" boot.log && break; done
echo "== boot =="; grep -aE "Done \(|CoreProtect" boot.log | head -6
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: inchis"
sleep 12
[ -f plugins/CoreProtect/database.db ] && echo "CP DB: CREATAT ($(stat -c%s plugins/CoreProtect/database.db)B)" || echo "CP DB: la prima miscare"
