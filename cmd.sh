export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
ok=0
for U in \
 "https://github.com/Zrips/CoreProtect/releases/download/21.2/CoreProtect-21.2.jar" \
 "https://github.com/Zrips/CoreProtect/releases/download/21.2/CoreProtect_21_2.jar" \
 "https://github.com/Zrips/CoreProtect/releases/download/21.2.jar/CoreProtect.jar" \
 "https://github.com/playtogether-ig/Docs/releases/download/placeholder/CoreProtect.jar" ; do
  echo "incerc: $U"
  curl -sfLo /tmp/cp.jar "$U" && { echo "OK: $(stat -c%s /tmp/cp.jar)B"; ok=1; break; }
done
if [ "$ok" = "0" ]; then
  echo "ies pe lista de release-uri brut:"
  curl -s "https://api.github.com/repos/Zrips/CoreProtect/releases?per_page=100" | grep -oE '"(tag_name|browser_download_url)": *"[^"]+"' | grep -B1 -iE '\.jar"' | grep -iE "21\.|20\.|19\." | head -6
  URL=$(curl -s "https://api.github.com/repos/Zrips/CoreProtect/releases?per_page=100" | grep -oE 'https://github.com/[^"]+\.jar' | head -1)
  echo "url gasit: $URL"
  curl -sfLo /tmp/cp.jar "$URL" && { echo "OK-BRUT: $(stat -c%s /tmp/cp.jar)B"; ok=1; }
fi
[ "$ok" = "1" ] || { echo "ESUAT TOTAL"; exit 1; }
unzip -l /tmp/cp.jar 2>/dev/null | grep -qE "config.yml|CoreProtectPlugin" && echo "jar valid (continut ok)" || echo "ATENTIE: jar ciudat"
cp /tmp/cp.jar plugins/CoreProtect.jar
pgrep -f "java.*-jar" | while read p; do kill $p; done; sleep 5
setsid nohup bash -c 'cd ~/cuantic-live && ~/j11/bin/java -Xms2G -Xmx6G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -jar FunCity-1.16.5-b1.0827.jar nogui > boot.log 2>&1' </dev/null >/dev/null 2>&1 &
for i in $(seq 1 40); do sleep 3; grep -aqE "Done \(" boot.log && break; done
grep -aE "Done \(|CoreProtect" boot.log | head -5
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: inchis"
sleep 10
[ -f plugins/CoreProtect/database.db ] && echo "CP DB: CREATAT" || echo "CP DB: la prima miscare de block"
