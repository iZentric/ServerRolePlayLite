export PATH=$PATH:/usr/bin:/bin:/usr/local/bin
PP=$(ps -o ppid= -p $$ | tr -d ' ')
for p in $(pgrep -f "claie" 2>/dev/null); do [ "$p" != "$PP" ] && kill "$p" 2>/dev/null && echo "dublura oprita: $p"; done
echo "=== STATURI SERVER (dupa v14) ==="
cd ~/cuantic-live
ls mods/ | grep -iE "starlight|ferrite|datafix|chunkload|performant|lithium|modernfix" | tr '\n' ' '; echo
grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1
pgrep -f unix_args >/dev/null && echo "SERVER: VIU" || { nohup ~/j11/bin/java @unix_args.txt nogui > boot.log 2>&1 & echo "SERVER: repornit"; for i in $(seq 1 40); do sleep 5; grep -q "Done (" boot.log && break; done; grep -oE "Done \([0-9.]*s\)!" boot.log | tail -1; }
echo "=== FERRITECORE din github oficial ==="
[ -f mods/ferritecore-4.1.0-forge.jar ] || { F=$(curl -s https://api.github.com/repos/malte0811/FerriteCore/releases | grep -oE '"browser_download_url": *"[^"]*1\.16\.5[^"]*forge[^"]*\.jar"' | cut -d'"' -f4 | head -1); if [ -n "$F" ]; then curl -sL -o "mods/$(basename $F)" "$F" && echo "OK $(basename $F) $(stat -c %s mods/$(basename $F))"; else echo "fara 1.16.5 la malte0811, caut pe curse mai tarziu"; fi; }
cp -f mods/ferritecore*4.1.0-forge.jar ~/pack/final/mods/ 2>/dev/null
echo "=== CLIENT ZIP FINAL + RELEASE ==="
cd ~/pack/final && rm -f ~/FunCity-Client-Lite.zip && zip -qr ~/FunCity-Client-Lite.zip . && echo "zip: $(stat -c %s ~/FunCity-Client-Lite.zip)"
T=$(git -C ~/srpl-claie remote get-url origin | sed 's|.*://x-access-token:\([^@]*\)@.*|\1|')
H="Authorization: token $T"
J=$(curl -s -H "$H" -H "Accept: application/vnd.github+json" https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/tags/client-lite)
RID=$(echo "$J" | grep -oE '"id": *[0-9]+' | head -1 | grep -oE '[0-9]+')
if [ -z "$RID" ]; then J=$(curl -s -X POST -H "$H" -H "Accept: application/vnd.github+json" https://api.github.com/repos/iZentric/ServerRolePlayLite/releases -d '{"tag_name":"client-lite","name":"FunCity CLIENT LITE (orice PC vechi)","body":"Fara radon/rubidium -> bug F3+Shift rezolvat. OptiFine separat. 1.16.5 Forge."}'); RID=$(echo "$J" | grep -oE '"id": *[0-9]+' | head -1 | grep -oE '[0-9]+'); fi
UP=$(curl -s -H "$H" https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID | grep -oE '"upload_url": *"[^"]*"' | cut -d'"' -f4 | sed 's/{?name,label}//')
for a in $(curl -s -H "$H" https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/$RID | grep -oE '"url": *"https://api.github.com/repos/[^"]*/assets/[0-9]+"' | grep -oE 'assets/[0-9]+' | cut -d/ -f2); do curl -s -X DELETE -H "$H" "https://api.github.com/repos/iZentric/ServerRolePlayLite/releases/assets/$a" >/dev/null; done
C=$(curl -s -o /tmp/up.out -w "%{http_code}" -X POST -H "$H" -H "Content-Type: application/zip" --data-binary @~/FunCity-Client-Lite.zip "$UP?name=FunCity-Client-Lite.zip&label=client+zip")
echo "upload HTTP: $C"
grep -oE '"browser_download_url": *"[^"]*"' /tmp/up.out | head -1
