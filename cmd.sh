export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== PROCES =="; pgrep -fa "j11/bin/java" | head -2 | cut -c1-100
echo "== PORT =="; ss -lnt 2>/dev/null | grep 25565 || echo "PORT 25565 INCHIS"
echo "== BOOT LOG (curat, ultimele) =="
sed 's/\x1b\[[0-9;]*m//g' boot.log 2>/dev/null | grep -vE "^$" | tail -6 | cut -c1-140
[ -f logs/latest.log ] && { echo "== LATEST.LOG =="; sed 's/\x1b\[[0-9;]*m//g' logs/latest.log | tail -4 | cut -c1-140; }
echo "== ZIP =="; ls -l ~/FunCity-Client-Lite.zip 2>/dev/null | awk '{print $5" bytes"}'
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
echo "== TOKEN: ${T:+gasit}${T:-NUSI} ==" | head -c 20; echo
SZ=$(stat -c %s ~/FunCity-Client-Lite.zip 2>/dev/null || echo 0)
if [ -n "$T" ] && [ "$SZ" -gt 1000000 ]; then
  J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"FunCity-Client-Lite.zip\",\"size\":$SZ,\"content_type\":\"application/zip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets")
  S3=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('upload_url') or ('ERR:'+str(d.get('message'))))" 2>/dev/null)
  echo "asset: $S3" | head -c 120; echo
  case "$S3" in https://*) C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$S3"); echo "PUT S3: HTTP $C";; esac
fi
