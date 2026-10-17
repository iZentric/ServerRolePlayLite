export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "== ERORI FML (lista completa) =="
sed 's/\x1b\[[0-9;]*m//g' boot.log | grep -A24 "LoadingFailedException" | head -26 | cut -c1-170
echo "== MODS =="
ls -la mods/ 2>/dev/null | awk '{print $5, $9}' | tail -20
echo "== RETIARE CLIENT (nume nou) =="
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
SZ=$(stat -c %s ~/FunCity-Client-Lite.zip)
J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"FunCity-RP-Client-1.16.5.zip\",\"size\":$SZ,\"content_type\":\"application/zip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets")
S3=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null)
case "$S3" in
  https://*)
    C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$S3")
    echo "PUT: HTTP $C"
    [ "$C" = 201 ] && echo "LINK: https://github.com/iZentric/ServerRolePlayLite/releases/download/client-lite/FunCity-RP-Client-1.16.5.zip"
    ;;
  *) echo "eroare: $(echo $J | head -c 200)";;
esac
