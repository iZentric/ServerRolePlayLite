export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
cd ~ && rm -rf pack FunCity-Client-Lite.zip && mkdir -p pack && cd pack
curl -sL --retry 2 -o c.mrpack "https://github.com/iZentric/ServerRolePlayLite/releases/download/lite/CUANTIC-Client-1.7.7.mrpack"
echo "mrpack bytes: $(stat -c %s c.mrpack 2>/dev/null)"
unzip -qo c.mrpack 2>/dev/null
mkdir -p final/mods
[ -d overrides/mods ] && cp -n overrides/mods/*.jar final/mods/ 2>/dev/null
[ -d mods ] && cp -n mods/*.jar final/mods/ 2>/dev/null
cd final/mods
echo "=== SCOT (cauza bug F3+Shift / incompat) ==="
ls | grep -iE "radon|rubidium|sodium|oculus|optifine" | tee /dev/stderr | xargs -r rm -f
cd ~/pack/final
python3 - <<'PY'
import json, urllib.request, urllib.parse, hashlib, os
for slug in ["ferritecore","modelfix"]:
    try:
        q=urllib.parse.urlencode({"game_versions":'["1.16.5"]',"loaders":'["forge"]'})
        v=json.load(urllib.request.urlopen(f"https://api.modrinth.com/v2/project/{slug}/version?{q}",timeout=30))
        f=v[0]["files"][0]; name=f["filename"]
        if not name.endswith(".jar"): name+=".jar"
        data=urllib.request.urlopen(f["url"],timeout=120).read()
        if f["hashes"].get("sha512") and hashlib.sha512(data).hexdigest()!=f["hashes"]["sha512"]:
            print("HASH ROSIT:",name); continue
        open(os.path.join("mods",name),"wb").write(data)
        print("ADAUGAT:",name)
    except Exception as e: print("esuat",slug,type(e).__name__,str(e)[:60])
PY
cat > CUM-IL-PUN.txt <<'TXT'
FunCity CLIENT LITE - 1.16.5 Forge
1. Instaleari Forge 36.2.42 (installer oficial, o data).
2. Tot continutul folderului mods il puneti in .minecraft/mods
3. OptiFine T (pentru 1.16.5) se instaleaza SEPARAT de pe optifine.net -
   licenta OptiFine nu permite sa-l impachetam noi.
4. In launcher, JVM args:  -Xms1G -Xmx2G  (PC cu 4GB) / -Xmx3G (8GB)
Gata. F3 = coordonate, fara bug la Shift (radon/rubidium au fost scoase).
TXT
cd ~/pack/final && zip -qr ~/FunCity-Client-Lite.zip . && cd ~
echo "zip: $(stat -c %s ~/FunCity-Client-Lite.zip 2>/dev/null) bytes, mods: $(ls ~/pack/final/mods | wc -l)"
J=$(curl -s -X POST https://api.github.com/repos/iZentric/ServerRolePlayLite/releases -H "Authorization: token $T" -H "Accept: application/vnd.github+json" -d '{"tag_name":"client-lite","name":"FunCity CLIENT LITE (merge pe orice PC vechi)","body":"Fara radon/rubidium = bug F3+Shift rezolvat. OptiFine separat. Vezi CUM-IL-PUN.txt."}')
U=$(echo "$J" | grep -o '"upload_url":"[^"]*"' | cut -d'"' -f4 | sed 's/{?name,label}//')
curl -s -X POST "$U?name=FunCity-Client-Lite.zip&label=client" -H "Authorization: token $T" -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip | grep -oE '"browser_download_url": *"[^"]*"' | head -1
