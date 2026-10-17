export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~
echo "== EXPORT SERVER COMPLET =="
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
tar czf ~/srv-live.tar.gz -C ~/cuantic-live . 2>/dev/null
SZ=$(stat -c %s ~/srv-live.tar.gz 2>/dev/null || echo 0)
echo "tar: $SZ bytes"
RID=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d '{"tag_name":"server-live","name":"Server live (export cloudshell)","draft":false,"prerelease":false}' "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('id') or 'EXISTA')")
if [ "$RID" = "EXISTA" ]; then RID=$(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/server-live | python3 -c "import json,sys;print(json.load(sys.stdin).get('id',''))"); fi
echo "release: $RID"
if [ "$SZ" -gt 1000 ] && [ -n "$RID" ]; then
  J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"srv-live.tar.gz\",\"size\":$SZ,\"content_type\":\"application/gzip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID/assets")
  S3=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null)
  case "$S3" in
    https://*) C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/gzip" --data-binary @~/srv-live.tar.gz "$S3"); echo "PUT: $C" ;;
    *) echo "asset: $(echo $J | head -c 120)";;
  esac
fi
echo "== SI STATUT V36 =="
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT: DESCHIS" || echo "PORT: INCHIS"
sed 's/\x1b\[[0-9;]*m//g' ~/cuantic-live/boot.log 2>/dev/null | grep -oE "Done \([0-9.]*s\)!" | tail -1
