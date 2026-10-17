export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== SERVICIU =="
if ! ss -lnt 2>/dev/null | grep -q ":25565 "; then
  echo "repornesc serverul..."
  pkill -9 -f "j11/bin/java" 2>/dev/null; sleep 5
  rm -f world/session.lock world/DIM-1/session.lock world/DIM1/session.lock
  setsid nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 < /dev/null &
  for i in $(seq 1 50); do sleep 5; grep -q "Done (" boot.log && break; done
fi
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -oE "Done \([0-9.]*s\)!" | tail -1
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || { echo "PORT INCAPATINAT - ultimele erori:"; sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -nE "ERROR|Caused by|Exception:" | head -5 | cut -c1-160; }
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null &
for i in $(seq 1 15); do sleep 3; grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; done
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
echo "== CLIENT: curat asset + S3 upload =="
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
for a in $(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets | grep -oE '"id": [0-9]+' | grep -oE '[0-9]+'); do curl -s -X DELETE -H "Authorization: token $T" "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/assets/$a" >/dev/null && echo "am sters asset fantoma $a"; done
SZ=$(stat -c %s ~/FunCity-Client-Lite.zip 2>/dev/null || echo 0)
J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"FunCity-Client-Lite.zip\",\"size\":$SZ,\"content_type\":\"application/zip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets")
S3=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null)
case "$S3" in
  https://*)
    C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$S3")
    echo "PUT: HTTP $C"
    if [ "$C" = 201 ] || [ "$C" = 200 ]; then echo "LINK: https://github.com/iZentric/ServerRolePlayLite/releases/download/client-lite/FunCity-Client-Lite.zip"; fi ;;
  *) echo "eroare asset: $(echo $J | head -c 150)";;
esac
