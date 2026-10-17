export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "=== ADAUG MODURI LIPSA (server) ==="
for s in starlight limited-chunkloading datafixerslayer; do
  if ls mods/ 2>/dev/null | grep -qi "${s//-/.}"; then echo "$s: deja"; continue; fi
  python3 - "$s" <<'PY'
import json,sys,urllib.request,urllib.parse,hashlib,os
slug=sys.argv[1]
try:
    q=urllib.parse.urlencode({"game_versions":'["1.16.5"]',"loaders":'["forge"]'})
    v=json.load(urllib.request.urlopen(f"https://api.modrinth.com/v2/project/{slug}/version?{q}",timeout=30))
    f=v[0]["files"][0]; name=f["filename"]; dst="mods/"+name
    data=urllib.request.urlopen(f["url"],timeout=180).read()
    if f["hashes"].get("sha512") and hashlib.sha512(data).hexdigest()!=f["hashes"]["sha512"]:
        print(slug,"HASH ROSIT - REFUZ"); raise SystemExit
    open(dst,"wb").write(data); print("ADAUGAT:",name)
except Exception as e: print(slug,"esuat:",type(e).__name__,str(e)[:70])
PY
done
NEWJ=$(ls -t mods/*.jar | head -3 | grep -cE "starlight|limited|datafix")
if [ "$NEWJ" -gt 0 ]; then
  echo "=== RESTART + MASURATOARE ==="
  grep -c "Can't keep up" boot.log > /tmp/ku.vechi
  pkill -f unix_args; sleep 3
  nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
  for i in $(seq 1 60); do sleep 5; grep -q "Done (" boot.log && break; done
  grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 | sed 's/^/PORNIRE: /'
  ps -o rss= -p $(pgrep -f unix_args|head -1) 2>/dev/null | awk '{printf "RAM: %.0fM\n",$1/1024}'
fi
echo "=== CLIENT -> RELEASE ==="
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
cp -f mods/ferritecore*.jar ~/pack/final/mods/ 2>/dev/null
cd ~/pack/final && rm -f ~/FunCity-Client-Lite.zip && zip -qr ~/FunCity-Client-Lite.zip .
J=$(curl -s -H "Authorization: token $T" https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/client-lite)
RID=$(echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
echo "RID=$RID"
if [ -n "$RID" ]; then
  UP="https://uploads.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID/assets"
  C=$(curl -s -o /tmp/up.out -w "%{http_code}" -X POST -H "Authorization: token $T" -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$UP?name=FunCity-Client-Lite.zip")
  echo "upload: HTTP $C ($(stat -c %s ~/FunCity-Client-Lite.zip) bytes)"
fi
echo "=== GATA ==="
