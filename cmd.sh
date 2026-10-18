export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== descarc CoreProtect pt 1.16.5 =="
URL=$(curl -sf "https://api.github.com/repos/Zrips/CoreProtect/releases/tags/21.2" 2>/dev/null | grep browser_download_url | grep -oE 'https[^"]+\.jar' | head -1)
[ -z "$URL" ] && URL=$(curl -sf "https://api.github.com/repos/Zrips/CoreProtect/releases" 2>/dev/null | grep browser_download_url | grep -oE 'https[^"]+\.jar' | head -1)
echo "url: $URL"
curl -sfLo plugins/CoreProtect.jar "$URL" && echo "jar: $(stat -c%s plugins/CoreProtect.jar)B" || { echo "ESUAT-DESCARCARE"; exit 1; }
echo "== restart server (aprobat) =="
pgrep -f "java.*-jar" | while read p; do kill $p; done; sleep 5
setsid nohup bash -c 'cd ~/cuantic-live && ~/j11/bin/java -Xms2G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1' </dev/null >/dev/null 2>&1 &
for i in $(seq 1 40); do sleep 3; grep -aqE "Done \(" boot.log && break; done
echo "== boot =="; grep -aE "Done \(|CoreProtect" boot.log | head -4
grep -aiE "CoreProtect.*(enabled|version)|Loading.*CoreProtect" boot.log | head -3
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: inchis"
sleep 8
[ -f plugins/CoreProtect/database.db ] && echo "CP DB: CREATAT (baza de loguri functionala)" || echo "CP DB: inca nu (se face la prima interactiune)"
ls plugins/ | head -8
