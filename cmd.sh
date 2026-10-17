export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
echo "=== DE CE 422 ==="; head -c 300 /tmp/up.out 2>/dev/null; echo
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
AID=$(curl -s -H "Authorization: token $T" "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets" | python3 -c "import json,sys;a=json.load(sys.stdin);print(a[0]['id'] if a else '')" 2>/dev/null)
[ -n "$AID" ] && { echo "sterg asset vechi $AID"; curl -s -X DELETE -H "Authorization: token $T" "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/assets/$AID" > /dev/null; }
C=$(curl -s -o /tmp/up2.out -w "%{http_code}" -X POST -H "Authorization: token $T" -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/415883660/assets?name=FunCity-Client-Lite.zip")
echo "re-upload: HTTP $C"; grep -oE '"browser_download_url": *"[^"]*"' /tmp/up2.out 2>/dev/null | head -1
echo "=== CAPACITATE: view-distance ==="
cd ~/cuantic-live
sed -i 's/^view-distance=.*/view-distance=6/; s/^simulation-distance=.*/simulation-distance=4/' server.properties
grep -E "^view-distance" server.properties || echo "view-distance=6" >> server.properties
grep -q "view-distance=6" server.properties && { pkill -f unix_args; sleep 3; nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
  for i in $(seq 1 60); do sleep 5; grep -q "Done (" boot.log && break; done
  grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1; }
pgrep -f unix_args >/dev/null && echo "server: VIU" || echo "server: JOS(!)"
grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf.log | head -1
