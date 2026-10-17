export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== V21B RULA CURAT ==="
echo "=== SERVER ==="
cd ~/cuantic-live
pgrep -f unix_args >/dev/null && echo "server: VIU" || { echo "repornesc"; nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 & }
for i in $(seq 1 40); do sleep 5; grep -q "Done (" boot.log && break; done
grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1
grep -cE "Can't keep up" boot.log | sed 's/^/keepup-uri la 6: /'
echo "=== RELEASE via S3 (doi pasi) ==="
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
Z=~/FunCity-Client-Lite.zip
SZ=$(stat -c %s $Z)
J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"FunCity-Client-Lite.zip\",\"size\":$SZ,\"content_type\":\"application/zip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets")
S3=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null)
echo "asset inregistrat: ${S3:+OK}"
C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/zip" --data-binary @$Z "$S3")
echo "PUT S3: HTTP $C"
[ "$C" = 200 ] && echo "LINK: https://github.com/iZentric/ServerRolePlayLite/releases/download/client-lite/FunCity-Client-Lite.zip"
