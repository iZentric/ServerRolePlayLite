export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "== TUNEL =="
pgrep -f "cloudflared tunnel" >/dev/null || { cd ~/cuantic-live && setsid nohup ./cloudflared tunnel --no-autoupdate --url tcp://127.0.0.1:25565 > /tmp/cf.log 2>&1 < /dev/null & sleep 25; }
for i in $(seq 1 10); do grep -q trycloudflare /tmp/cf.log 2>/dev/null && break; sleep 3; done
ADRESA=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1)
echo "ADRESA: $ADRESA"
echo "== MRPACK pt Prism =="
cd ~/freeroam && rm -f Freeroam.mrpack
cd x && zip -qr ../Freeroam.mrpack . && cd ..
SZ=$(stat -c %s Freeroam.mrpack)
echo "marime mrpack: $SZ"
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
RID=$(curl -s https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/freeroam | python3 -c "import json,sys;print(json.load(sys.stdin).get('id',''))")
echo "release id: $RID"
J=$(curl -s -X POST -H "Authorization: token $T" -H "Content-Type: application/json" -d "{\"name\":\"Freeroam-1.0.0.mrpack\",\"size\":$SZ,\"content_type\":\"application/zip\"}" "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID/assets")
S3=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('upload_url',''))" 2>/dev/null)
case "$S3" in
  https://*)
    C=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: application/zip" --data-binary @Freeroam.mrpack "$S3")
    echo "PUT: HTTP $C"
    [ "$C" = 201 ] && echo "LINK: https://github.com/iZentric/ServerRolePlayLite/releases/download/freeroam/Freeroam-1.0.0.mrpack" ;;
  *) echo "eroare: $(echo $J | head -c 150)";;
esac
echo "== SERVER =="
ss -lnt 2>/dev/null | grep -q ":25565 " && echo "PORT 25565: DESCHIS" || echo "PORT: INCHIS"
sed 's/\x1b\[[0-9;]*m//g' ~/cuantic-live/boot.log 2>/dev/null | grep -oE "Done \([0-9.]*s\)!" | tail -1
