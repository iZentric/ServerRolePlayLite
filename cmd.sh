export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
cd ~/cuantic-live
echo "=== INAINTE ==="
pgrep -f unix_args >/dev/null && RSS1=$(ps -o rss= -p $(pgrep -f unix_args|head -1) 2>/dev/null | awk '{printf "%.0fM",$1/1024}') && echo "RAM server acum: $RSS1"; grep -c "Can't keep up" boot.log 2>/dev/null | sed 's/^/keepup-uri vechi: /'
echo "=== CE MODURI DE PERF MAI SUNT ==="
ls mods/ 2>/dev/null | grep -ciE "starlight|ferrite|performant|datafix|chunkload" | sed 's/^/există deja: /'
echo "=== DESCARC DE PE MODRINTH (fisa + hash) ==="
python3 - <<'PY'
import json, urllib.request, urllib.parse, hashlib, os
mods = {"starlight":"starlight","ferritecore":"ferritecore","datafixerslayer":"datafixerslayer","limited-chunkloading":"limited-chunkloading"}
os.makedirs("mods", exist_ok=True)
for slug in mods.values():
    try:
        q=urllib.parse.urlencode({"game_versions":'["1.16.5"]',"loaders":'["forge"]'})
        v=json.load(urllib.request.urlopen(f"https://api.modrinth.com/v2/project/{slug}/version?{q}",timeout=30))
        f=v[0]["files"][0]; name=f["filename"]
        if not name.endswith(".jar"): name+= ".jar"
        dst=os.path.join("mods",name)
        if os.path.exists(dst): print("deja:",name); continue
        data=urllib.request.urlopen(f["url"],timeout=120).read()
        got=hashlib.sha512(data).hexdigest(); want=f["hashes"].get("sha512","")
        if want and got!=want: print("HASH ROSIT, sar:",name); continue
        open(dst,"wb").write(data)
        print("OK",name,len(data)//1024,"KB",v[0].get("version_number",""))
    except Exception as e: print("esuat",slug,":",type(e).__name__,str(e)[:80])
PY
echo "=== RESTART CU PACHET NOU ==="
pkill -f "unix_args"; sleep 3
nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
for i in $(seq 1 48); do sleep 5; grep -q "Done (" boot.log && break; done
if grep -q "Done (" boot.log; then
  grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 | sed 's/^/PORNIRE: /'
  RSS2=$(ps -o rss= -p $(pgrep -f unix_args|head -1) 2>/dev/null | awk '{printf "%.0fM",$1/1024}')
  echo "RAM dupa: $RSS2 (inainte: $RSS1)"
else
  echo "CRAPAT - SCOT MODURILE NOI SI REVIN"
  ls -t mods/*.jar | head -4 | xargs -r rm -f
  nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 &
  for i in $(seq 1 48); do sleep 5; grep -q "Done (" boot.log && break; done
  grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1 | sed 's/^/PORNIRE (curat): /'
fi
